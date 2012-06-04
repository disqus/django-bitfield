from django.db.models import signals
from django.db.models.sql.expressions import SQLEvaluator
from django.db.models.fields import Field, BigIntegerField
from django.db.models.fields.subclassing import Creator
try:
    from django.db.models.fields.subclassing import SubfieldBase
except ImportError:
    # django 1.2
    from django.db.models.fields.subclassing import LegacyConnection as SubfieldBase

from .forms import BitFormField
from .query import BitQueryLookupWrapper
from .types import BitHandler, Bit


class BitFieldFlags(object):
    def __init__(self, flags):
        self._flags = flags

    def __repr__(self):
        return repr(self._flags)

    def __iter__(self):
        for flag in self._flags:
            yield flag

    def __getattr__(self, key):
        if key not in self._flags:
            raise AttributeError
        return Bit(self._flags.index(key))

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


class BitFieldCreator(Creator):
    """
    Descriptor for BitFields.  Checks to make sure that all flags of the
    instance match the class.  This is to handle the case when caching
    an older version of the instance and a newer version of the class is
    available (usually during deploys).
    """
    def __get__(self, obj, type=None):
        if obj is None:
            return BitFieldFlags(self.field.flags)
        retval = obj.__dict__[self.field.name]
        if self.field.__class__ is BitField:
            # Update flags from class in case they've changed.
            retval._keys = self.field.flags
        return retval


class BitFieldMeta(SubfieldBase):
    """
    Modified SubFieldBase to use our contribute_to_class method (instead of
    monkey-patching make_contrib).  This uses our BitFieldCreator descriptor
    in place of the default.

    NOTE: If we find ourselves needing custom descriptors for fields, we could
    make this generic.
    """
    def __new__(cls, name, bases, attrs):
        def contribute_to_class(self, cls, name):
            BigIntegerField.contribute_to_class(self, cls, name)
            setattr(cls, self.name, BitFieldCreator(self))

        new_class = super(BitFieldMeta, cls).__new__(cls, name, bases, attrs)
        new_class.contribute_to_class = contribute_to_class
        return new_class


class BitField(BigIntegerField):
    __metaclass__ = BitFieldMeta

    def __init__(self, flags, *args, **kwargs):
        BigIntegerField.__init__(self, *args, **kwargs)
        self.flags = flags

    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.BigIntegerField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

    def formfield(self, form_class=BitFormField, **kwargs):
        choices = [(f, f) for f in self.flags]
        return Field.formfield(self, form_class, choices=choices, **kwargs)

    def pre_save(self, instance, add):
        value = getattr(instance, self.attname)
        return value

    def get_prep_value(self, value):
        if isinstance(value, (BitHandler, Bit)):
            value = value.mask
        return int(value)

    # def get_db_prep_save(self, value, connection):
    #     if isinstance(value, Bit):
    #         return BitQuerySaveWrapper(self.model._meta.db_table, self.name, value)
    #     return super(BitField, self).get_db_prep_save(value, connection=connection)

    def get_db_prep_lookup(self, lookup_type, value, connection, prepared=False):
        if isinstance(value, SQLEvaluator) and isinstance(value.expression, Bit):
            value = value.expression
        if isinstance(value, (BitHandler, Bit)):
            return BitQueryLookupWrapper(self.model._meta.db_table, self.db_column or self.name, value)
        return BigIntegerField.get_db_prep_lookup(self, lookup_type=lookup_type, value=value,
                                                        connection=connection, prepared=prepared)

    def get_prep_lookup(self, lookup_type, value):
        if isinstance(value, SQLEvaluator) and isinstance(value.expression, Bit):
            value = value.expression
        if isinstance(value, Bit):
            if lookup_type in ('exact',):
                return value
            raise TypeError('Lookup type %r not supported with `Bit` type.' % lookup_type)
        return BigIntegerField.get_prep_lookup(self, lookup_type, value)

    def to_python(self, value):
        if isinstance(value, Bit):
            value = value.mask
        if not isinstance(value, BitHandler):
            # Regression for #1425: fix bad data that was created resulting
            # in negative values for flags.  Compute the value that would
            # have been visible ot the application to preserve compatibility.
            if isinstance(value, (int, long)) and value < 0:
                new_value = 0
                for bit_number, _ in enumerate(self.flags):
                    new_value |= (value & (2**bit_number))
                value = new_value

            value = BitHandler(value, self.flags)
        else:
            # Ensure flags are consistent for unpickling
            value._keys = self.flags
        return value


class CompositeBitField(object):
    def __init__(self, fields):
        self.fields = fields

    def contribute_to_class(self, cls, name):
        self.name = name
        self.model = cls
        cls._meta.add_virtual_field(self)

        signals.class_prepared.connect(self.validate_fields, sender=cls)

        setattr(cls, name, self)

    def validate_fields(self, sender, **kwargs):
        cls = sender
        model_fields = dict([
            (f.name, f) for f in cls._meta.fields if f.name in self.fields])
        all_flags = sum([model_fields[f].flags for f in self.fields], ())
        if len(all_flags) != len(set(all_flags)):
            raise ValueError('BitField flags must be unique.')

    def __get__(self, instance, instance_type=None):
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
        fields = [getattr(instance, f) for f in self.fields]
        return CompositeBitFieldWrapper(fields)

    def __set__(self, *args, **kwargs):
        raise NotImplementedError('CompositeBitField cannot be set.')

