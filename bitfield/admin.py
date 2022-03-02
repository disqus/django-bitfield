import django
import six

from django.core.exceptions import ValidationError
if django.VERSION < (2, 0):
    from django.utils.translation import ugettext_lazy as _
else:
    # Aliased since Django 2.0 https://github.com/django/django/blob/2.0/django/utils/translation/__init__.py#L80-L81
    from django.utils.translation import gettext_lazy as _
from django.contrib.admin import FieldListFilter
from django.contrib.admin.options import IncorrectLookupParameters

from bitfield import Bit, BitHandler


class BitFieldListFilter(FieldListFilter):
    """
    BitField list filter.
    """

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = field_path
        self.lookup_val = int(request.GET.get(self.lookup_kwarg, 0))
        self.flags = field.flags
        self.labels = field.labels
        super(BitFieldListFilter, self).__init__(
            field, request, params, model, model_admin, field_path)

    def queryset(self, request, queryset):
        filter_kwargs = dict(
            (p, BitHandler(v, ()))
            for p, v in six.iteritems(self.used_parameters)
        )
        if not filter_kwargs:
            return queryset
        try:
            return queryset.filter(**filter_kwargs)
        except ValidationError as e:
            raise IncorrectLookupParameters(e)

    def expected_parameters(self):
        return [self.lookup_kwarg]

    def choices(self, cl):
        yield {
            'selected': self.lookup_val == 0,
            'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
            'display': _('All'),
        }
        for number, flag in enumerate(self.flags):
            bit_mask = Bit(number).mask
            yield {
                'selected': self.lookup_val == bit_mask,
                'query_string': cl.get_query_string({self.lookup_kwarg: bit_mask}),
                'display': self.labels[number],
            }
