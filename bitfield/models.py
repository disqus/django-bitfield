from __future__ import absolute_import

import six

from django.db.models import signals
from django.db.models.fields import Field, BigIntegerField

from bitfield.forms import BitFormField
from bitfield.query import BitQueryLookupWrapper
from bitfield.types import BitHandler, Bit

# Count binary capacity. Truncate "0b" prefix from binary form.
# Twice faster than bin(i)[2:] or math.floor(math.log(i))
MAX_FLAG_COUNT = int(len(bin(BigIntegerField.MAX_BIGINT)) - 2)


class BitFieldFlags(object):
    def __init__(self, flags):
        if len(flags) > MAX_FLAG_COUNT:
            raise ValueError('Too many flags')
        self._flags = flags

    def __repr__(self):
        return repr(self._flags)

    def __iter__(self):
        for flag in self._flags:
            yield flag

    def __getattr__(self, key):
        if key == '_flags':
            # Since __getattr__ is for fallback, reaching here from Python
            # means that there's no '_flags' attribute in this object,
            # which may be caused by intermediate state while copying etc.
            raise AttributeError(
                "'%s' object has no attribute '%s'" % (self.__class__.__name__, key)
            )
        try:
            flags = self._flags
        except AttributeError:
            raise AttributeError(
                "'%s' object has no attribute '%s'" % (self.__class__.__name__, key)
            )
        try:
            flag = flags.index(key)
        except ValueError:
            raise AttributeError("flag {} is not registered".format(key))
        return Bit(flag)

    def iteritems(self):
        for flag in self._flags:
            yield flag, Bit(self._flags.index(flag))

    def iterkeys(self):
        for flag in self._flags:
            yield flag

    def itervalues(self):
        for flag in self._flags:
            yield Bit(self._flags.index(flag))

    def items(self):
        return list(self.iteritems())

    def keys(self):
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())


class BitFieldCreator(object):
    """
    A placeholder class that provides a way to set the attribute on the model.
    Descriptor for BitFields.  Checks to make sure that all flags of the
    instance match the class.  This is to handle the case when caching
    an older version of the instance and a newer version of the class is
    available (usually during deploys).
    """
    def __init__(self, field):
        self.field = field

    def __set__(self, obj, value):
        obj.__dict__[self.field.name] = self.field.to_python(value)

    def __get__(self, obj, type=None):
        if obj is None:
            return BitFieldFlags(self.field.flags)
        retval = obj.__dict__[self.field.name]
        if self.field.__class__ is BitField:
            # Update flags from class in case they've changed.
            retval._keys = self.field.flags
        return retval


class BitField(BigIntegerField):

    def contribute_to_class(self, cls, name, **kwargs):
        super(BitField, self).contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, BitFieldCreator(self))

    def __init__(self, flags, default=None, *args, **kwargs):
        if isinstance(flags, dict):
            # Get only integer keys in correct range
            valid_keys = (k for k in flags.keys() if isinstance(k, int) and (0 <= k < MAX_FLAG_COUNT))
            if not valid_keys:
                raise ValueError('Wrong keys or empty dictionary')
            # Fill list with values from dict or with empty values
            flags = [flags.get(i, '') for i in range(max(valid_keys) + 1)]

        if len(flags) > MAX_FLAG_COUNT:
            raise ValueError('Too many flags')

        self._arg_flags = flags
        flags = list(flags)
        labels = []
        for num, flag in enumerate(flags):
            if isinstance(flag, (tuple, list)):
                flags[num] = flag[0]
                labels.append(flag[1])
            else:
                labels.append(flag)

        if isinstance(default, (list, tuple, set, frozenset)):
            new_value = 0
            for flag in default:
                new_value |= Bit(flags.index(flag))
            default = new_value

        BigIntegerField.__init__(self, default=default, *args, **kwargs)
        self.flags = flags
        self.labels = labels

    def formfield(self, form_class=BitFormField, **kwargs):
        choices = [(k, self.labels[self.flags.index(k)]) for k in self.flags]
        return Field.formfield(self, form_class, choices=choices, **kwargs)

    def get_prep_value(self, value):
        if value is None:
            return None
        if isinstance(value, (BitHandler, Bit)):
            value = value.mask
        return int(value)

    # def get_db_prep_save(self, value, connection):
    #     if isinstance(value, Bit):
    #         return BitQuerySaveWrapper(self.model._meta.db_table, self.name, value)
    #     return super(BitField, self).get_db_prep_save(value, connection=connection)

    def to_python(self, value):
        if isinstance(value, Bit):
            value = value.mask
        if not isinstance(value, BitHandler):
            # Regression for #1425: fix bad data that was created resulting
            # in negative values for flags.  Compute the value that would
            # have been visible ot the application to preserve compatibility.
            if isinstance(value, six.integer_types) and value < 0:
                new_value = 0
                for bit_number, _ in enumerate(self.flags):
                    new_value |= (value & (2 ** bit_number))
                value = new_value

            value = BitHandler(value, self.flags, self.labels)
        else:
            # Ensure flags are consistent for unpickling
            value._keys = self.flags
        return value

    def deconstruct(self):
        name, path, args, kwargs = super(BitField, self).deconstruct()
        args.insert(0, self._arg_flags)
        return name, path, args, kwargs


BitField.register_lookup(BitQueryLookupWrapper)


class CompositeBitFieldWrapper(object):
    def __init__(self, fields):
        self.fields = fields

    def __getattr__(self, attr):
        if attr == 'fields':
            return super(CompositeBitFieldWrapper, self).__getattr__(attr)

        for field in self.fields:
            if hasattr(field, attr):
                return getattr(field, attr)
        raise AttributeError('%s is not a valid flag' % attr)

    def __hasattr__(self, attr):
        if attr == 'fields':
            return super(CompositeBitFieldWrapper, self).__hasattr__(attr)

        for field in self.fields:
            if hasattr(field, attr):
                return True
        return False

    def __setattr__(self, attr, value):
        if attr == 'fields':
            super(CompositeBitFieldWrapper, self).__setattr__(attr, value)
            return

        for field in self.fields:
            if hasattr(field, attr):
                setattr(field, attr, value)
                return
        raise AttributeError('%s is not a valid flag' % attr)


class CompositeBitField(object):
    is_relation = False
    many_to_many = False
    concrete = False

    def __init__(self, fields):
        self.fields = fields

    def contribute_to_class(self, cls, name):
        self.name = name
        self.model = cls
        cls._meta.private_fields.append(self)

        signals.class_prepared.connect(self.validate_fields, sender=cls)

        setattr(cls, name, self)

    def validate_fields(self, sender, **kwargs):
        cls = sender
        model_fields = dict([
            (f.name, f) for f in cls._meta.fields if f.name in self.fields])
        all_flags = sum([model_fields[f].flags for f in self.fields], [])
        if len(all_flags) != len(set(all_flags)):
            raise ValueError('BitField flags must be unique.')

    def __get__(self, instance, instance_type=None):
        fields = [getattr(instance, f) for f in self.fields]
        return CompositeBitFieldWrapper(fields)

    def __set__(self, *args, **kwargs):
        raise NotImplementedError('CompositeBitField cannot be set.')
