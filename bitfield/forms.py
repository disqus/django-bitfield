from django.forms import CheckboxSelectMultiple, IntegerField, ValidationError
from django.utils.encoding import force_unicode

from bitfield.types import BitHandler
from bitfield.widgets import BitFieldCheckboxSelectMultiple


class BitFormField(IntegerField):
    def __init__(self, choices=(), widget=BitFieldCheckboxSelectMultiple, *args, **kwargs):
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
