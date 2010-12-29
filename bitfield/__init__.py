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
from django.db.models.fields import Field, BigIntegerField
from django.db.models.fields.subclassing import Creator, LegacyConnection

class Bit(object):
    """
    Represents a single Bit.
    """
    def __init__(self, number, is_set=True):
        self.number = number
        self.is_set = is_set
    
    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.number)
    
    def __str__(self):
        if self.is_set:
            return 'Yes'
        return 'No'
    
    def __int__(self):
        return int(self.is_set)
    
    def __nonzero__(self):
        return self.is_set
        
    def __eq__(self, value):
        if isinstance(value, Bit):
            return value.number == self.number and value.is_set == self.is_set
        return bool(value) == self.is_set

    def __ne__(self, value):
        if isinstance(value, Bit):
            return value != self
        return bool(value) != self.is_set

    def __coerce__(self, value):
        return (self.is_set, bool(value))

    def __invert__(self):
        return Bit(self.number, bool(not self.is_set))

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
            raise AttributeError
        return self.get_bit(self._keys.index(key))
    
    def __setattr__(self, key, value):
        if key.startswith('_'):
            return object.__setattr__(self, key, value)
        if key not in self._keys:
            raise AttributeError
        self.set_bit(self._keys.index(key), value)
    
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

class BitFormField(forms.IntegerField):
    def __init__(self, *args, **kwargs):
        super(BitFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = int(value)
        return super(BitFormField, self).clean(value)

class BitFieldFlags(object):
    def __init__(self, flags):
        self._flags = flags
    
    def __iter__(self):
        for flag in self._flags:
            yield flag
    
    def __getattr__(self, key):
        if key not in self._flags:
            raise AttributeError
        return Bit(self._flags.index(key))

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
            super(self.__class__, self).contribute_to_class(cls, name)
            setattr(cls, self.name, BitFieldCreator(self))

        new_class = super(BitFieldMeta, cls).__new__(cls, name, bases, attrs)
        new_class.contribute_to_class = contribute_to_class
        return new_class

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
        mask = 2**self.bit.number
        if self.bit:
            return ("(%s.%s | %d)" % (qn(self.table_alias), qn(self.column), mask),
                    [])
        return ("(%s.%s & ~%d)" % (qn(self.table_alias), qn(self.column), mask),
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
        
        mask = 2**self.bit.number
        if self.bit:
            return ("%s.%s | %d" % (qn(self.table_alias), qn(self.column), mask),
                    [])
        return ("%s.%s %s %d" % (qn(self.table_alias), qn(self.column), XOR_OPERATOR, mask),
                [])

class BitField(BigIntegerField):
    __metaclass__ = BitFieldMeta

    def __init__(self, flags, *args, **kwargs):
        super(BitField, self).__init__(*args, **kwargs)
        self.flags = flags

    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.BigIntegerField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

    def formfield(self, form_class=BitFormField, **kwargs):
        return Field.formfield(self, form_class, **kwargs)

    def get_prep_value(self, value):
        return int(value)

    def get_db_prep_save(self, value, connection):
        if isinstance(value, Bit):
            return BitQuerySaveWrapper(self.model._meta.db_table, self.name, value)
        return super(BitField, self).get_db_prep_save(value, connection=connection)

    def get_db_prep_lookup(self, lookup_type, value, connection, prepared=False):
        if isinstance(value, Bit):
            return BitQueryLookupWrapper(self.model._meta.db_table, self.name, value)
        return super(BitField, self).get_db_prep_lookup(lookup_type=lookup_type, value=value,
                                                        connection=connection, prepared=prepared)

    def get_prep_lookup(self, lookup_type, value):
        if isinstance(value, Bit):
            if lookup_type in ('exact',):
                return value
            raise TypeError('Lookup type %r not supported with `Bit` type.' % lookup_type)
        return super(BitField, self).get_prep_lookup(lookup_type, value)

    def to_python(self, value):
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