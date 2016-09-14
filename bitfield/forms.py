from __future__ import absolute_import

from django.forms import CheckboxSelectMultiple, IntegerField, ValidationError

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text

from bitfield.types import BitHandler


class BitFieldCheckboxSelectMultiple(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if isinstance(value, BitHandler):
            value = [k for k, v in value if v]
        elif isinstance(value, int):
            real_value = []
            div = 2
            for (k, v) in self.choices:
                if value % div != 0:
                    real_value.append(k)
                    value -= (value % div)
                div *= 2
            value = real_value
        return super(BitFieldCheckboxSelectMultiple, self).render(
            name, value, attrs=attrs)

    def _has_changed(self, initial, data):
        if initial is None:
            initial = []
        if data is None:
            data = []
        if initial != data:
            return True
        initial_set = set([force_text(value) for value in initial])
        data_set = set([force_text(value) for value in data])
        return data_set != initial_set


class BitFormField(IntegerField):
    def __init__(self, choices=(), widget=BitFieldCheckboxSelectMultiple, *args, **kwargs):

        if isinstance(kwargs['initial'], int):
            iv = kwargs['initial']
            l = []
            for i in range(0, 63):
                if (1 << i) & iv > 0:
                    l += [choices[i][0]]
            kwargs['initial'] = l
        self.widget = widget
        super(BitFormField, self).__init__(widget=widget, *args, **kwargs)
        self.choices = self.widget.choices = choices

    def clean(self, value):
        if not value:
            return 0
        return int(self.to_python(value))

    def to_python(self, value):
        # Assume an iterable which contains an item per flag that's enabled
        result = BitHandler(0, [k for k, v in self.choices])
        for k in value:
            try:
                setattr(result, str(k), True)
            except AttributeError:
                raise ValidationError('Unknown choice: %r' % (k,))
        return result
