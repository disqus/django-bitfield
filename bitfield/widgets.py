from django.forms import CheckboxSelectMultiple, IntegerField, ValidationError
from django.utils.encoding import force_unicode

from bitfield.types import BitHandler


class BitFieldCheckboxSelectMultiple(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if isinstance(value, BitHandler):
            value = [k for k, v in value if v]
        return super(BitFieldCheckboxSelectMultiple, self).render(
          name, value, attrs=attrs, choices=enumerate(choices))

    def _has_changed(self, initial, data):
        if initial is None:
            initial = []
        if data is None:
            data = []
        if initial != data:
            return True
        initial_set = set([force_unicode(value) for value in initial])
        data_set = set([force_unicode(value) for value in data])
        return data_set != initial_set
