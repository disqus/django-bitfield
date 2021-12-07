from __future__ import absolute_import

from django.forms import CheckboxSelectMultiple, IntegerField, ValidationError

from django.utils.encoding import force_str

from bitfield.types import BitHandler


class BitFieldCheckboxSelectMultiple(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=(), renderer=None):
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

    def has_changed(self, initial, data):
        if initial is None:
            initial = []
        if data is None:
            data = []
        if initial != data:
            return True
        initial_set = set([force_str(value) for value in initial])
        data_set = set([force_str(value) for value in data])
        return data_set != initial_set


class BitFormField(IntegerField):
    def __init__(self, choices=(), widget=BitFieldCheckboxSelectMultiple, *args, **kwargs):

        if isinstance(kwargs['initial'], int):
            iv = kwargs['initial']
            iv_list = []
            for i in range(0, min(len(choices), 63)):
                if (1 << i) & iv > 0:
                    iv_list += [choices[i][0]]
            kwargs['initial'] = iv_list
        self.widget = widget
        super(BitFormField, self).__init__(widget=widget, *args, **kwargs)
        self.choices = self.widget.choices = choices

    def clean(self, value):
        if not value:
            return 0

        # Assume an iterable which contains an item per flag that's enabled
        result = BitHandler(0, [k for k, v in self.choices])
        for k in value:
            try:
                setattr(result, str(k), True)
            except AttributeError:
                raise ValidationError('Unknown choice: %r' % (k,))
        return int(result)
