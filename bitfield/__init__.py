"""
django-bitfield
~~~~~~~~~~~~~~~
"""

try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('bitfield').version
except Exception, e:
    VERSION = 'unknown'

from django import forms
from django.db.models import signals
from django.db.models.sql.expressions import SQLEvaluator
from django.db.models.fields import Field, BigIntegerField
from django.db.models.fields.subclassing import Creator, LegacyConnection

class Bit(object):
    """
    Represents a single Bit.
    """
    def __init__(self, number, is_set=True):
        self.number = number
        self.is_set = bool(is_set)
        self.mask = 2**int(number)
        if not self.is_set:
            self.mask = ~self.mask

    def __repr__(self):
        return '<%s: number=%d, is_set=%s>' % (self.__class__.__name__, self.number, self.is_set)

    # def __str__(self):
    #     if self.is_set:
    #         return 'Yes'
    #     return 'No'

    def __int__(self):
        return self.mask

    def __nonzero__(self):
        return self.is_set

    def __eq__(self, value):
        if isinstance(value, Bit):
            return value.number == self.number and value.is_set == self.is_set
        elif isinstance(value, bool):
            return value == self.is_set
        elif isinstance(value, int):
            return value == self.mask
        return value == self.is_set

    def __ne__(self, value):
        return not self == value

    def __coerce__(self, value):
        return (self.is_set, bool(value))

    def __invert__(self):
        return self.__class__(self.number, not self.is_set)

    def __and__(self, value):
        if isinstance(value, Bit):
            value = value.mask
        return value & self.mask

    def __rand__(self, value):
        if isinstance(value, Bit):
            value = value.mask
        return self.mask & value

    def __or__(self, value):
        if isinstance(value, Bit):
            value = value.mask
        return value | self.mask

    def __ror__(self, value):
        if isinstance(value, Bit):
            value = value.mask
        return self.mask | value

    def __lshift__(self, value):
        if isinstance(value, Bit):
            value = value.mask
        return value << self.mask

    def __rlshift__(self, value):
        if isinstance(value, Bit):
            value = value.mask
        return self.mask << value

    def __rshift__(self, value):
        if isinstance(value, Bit):
            value = value.mask
        return value >> self.mask

    def __rrshift__(self, value):
        if isinstance(value, Bit):
            value = value.mask
        return self.mask >> value

    def __xor__(self, value):
        if isinstance(value, Bit):
            value = value.mask
        return value ^ self.mask

    def __rxor__(self, value):
        if isinstance(value, Bit):
            value = value.mask
        return self.mask ^ value

    def __sentry__(self):
        return repr(self)

    def prepare(self, evaluator, query, allow_joins):
        return self

    def evaluate(self, evaluator, qn, connection):
        return self.mask, []

class BitHandler(object):
    """
    Represents an array of bits, each as a ``Bit`` object.
    """
    def __init__(self, value, keys):
        # TODO: change to bitarray?
        if value:
            self._value = int(value)
        else:
            self._value = 0
        self._keys = keys

    def __eq__(self, other):
        if not isinstance(other, BitHandler):
            return False
        return self._value == other._value

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, ', '.join('%s=%s' % (k, self.get_bit(n).is_set) for n, k in enumerate(self._keys)),)

    def __str__(self):
        return str(self._value)

    def __int__(self):
        return self._value

    def __nonzero__(self):
        return bool(self._value)

    def __and__(self, value):
        return BitHandler(self._value & int(value), self._keys)

    def __or__(self, value):
        return BitHandler(self._value | int(value), self._keys)

    def __add__(self, value):
        return BitHandler(self._value + int(value), self._keys)

    def __sub__(self, value):
        return BitHandler(self._value - int(value), self._keys)

    def __lshift__(self, value):
        return BitHandler(self._value << int(value), self._keys)

    def __rshift__(self, value):
        return BitHandler(self._value >> int(value), self._keys)

    def __xor__(self, value):
        return BitHandler(self._value ^ int(value), self._keys)

    def __contains__(self, key):
        bit_number = self._keys.index(key)
        return bool(self.get_bit(bit_number))

    def __getattr__(self, key):
        if key.startswith('_'):
            return object.__getattribute__(self, key)
        if key not in self._keys:
            raise AttributeError('%s is not a valid flag' % key)
        return self.get_bit(self._keys.index(key))

    def __setattr__(self, key, value):
        if key.startswith('_'):
            return object.__setattr__(self, key, value)
        if key not in self._keys:
            raise AttributeError('%s is not a valid flag' % key)
        self.set_bit(self._keys.index(key), value)

    def __iter__(self):
        return self.iteritems()

    def __sentry__(self):
        return repr(self)

    def _get_mask(self):
        return self._value
    mask = property(_get_mask)

    def prepare(self, evaluator, query, allow_joins):
        return self

    def evaluate(self, evaluator, qn, connection):
        return self.mask, []

    def get_bit(self, bit_number):
        mask = 2**int(bit_number)
        return Bit(bit_number, self._value & mask != 0)

    def set_bit(self, bit_number, true_or_false):
        mask = 2**int(bit_number)
        if true_or_false:
            self._value |= mask
        else:
            self._value &= (~mask)
        return Bit(bit_number, self._value & mask != 0)

    def keys(self):
        return self._keys

    def iterkeys(self):
        return iter(self._keys)

    def items(self):
        return list(self.iteritems())

    def iteritems(self):
        for k in self._keys:
            yield (k, getattr(self, k).is_set)

class BitFormField(forms.IntegerField):
    def __init__(self, *args, **kwargs):
        super(BitFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = int(value)
        return super(BitFormField, self).clean(value)

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

class BitQueryLookupWrapper(object):
    def __init__(self, alias, column, bit):
        self.table_alias = alias
        self.column = column
        self.bit = bit

    def as_sql(self, qn, connection=None):
        """
        Create the proper SQL fragment. This inserts something like
        "(T0.flags & value) != 0".

        This will be called by Where.as_sql()
        """
        if self.bit:
            return ("(%s.%s | %d)" % (qn(self.table_alias), qn(self.column), self.bit.mask),
                    [])
        return ("(%s.%s & %d)" % (qn(self.table_alias), qn(self.column), self.bit.mask),
                [])

class BitQuerySaveWrapper(BitQueryLookupWrapper):
    def as_sql(self, qn, connection):
        """
        Create the proper SQL fragment. This inserts something like
        "(T0.flags & value) != 0".

        This will be called by Where.as_sql()
        """
        engine = connection.settings_dict['ENGINE'].rsplit('.', -1)[-1]
        if engine.startswith('postgres'):
            XOR_OPERATOR = '#'
        elif engine.startswith('sqlite'):
            raise NotImplementedError
        else:
            XOR_OPERATOR = '^'

        if self.bit:
            return ("%s.%s | %d" % (qn(self.table_alias), qn(self.column), self.bit.mask),
                    [])
        return ("%s.%s %s %d" % (qn(self.table_alias), qn(self.column), XOR_OPERATOR, self.bit.mask),
                [])

class BitFieldMeta(LegacyConnection):
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
        return Field.formfield(self, form_class, **kwargs)

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
            return BitQueryLookupWrapper(self.model._meta.db_table, self.name, value)
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

