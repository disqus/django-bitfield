from itertools import chain
from django import forms
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

from bitfield.types import BitHandler

__all__ = [
    'BitFieldWidgetMixin',
    'BitFieldCheckboxSelect'
]

class BitFieldWidgetMixin(object):

    def __init__(self, attrs={}, *args, **kwargs):

        attrs['class'] = "class" in attrs and self.add_to_css_class(
            attrs['class'], 'bitfield') or "bitfield"

        super(BitFieldWidgetMixin, self).__init__(attrs, *args, **kwargs)

    def add_to_css_class(self, classes, new_class):
        new_classes = classes
        try:
            classes_test = u" " + unicode(classes) + u" "
            new_class_test = u" " + unicode(new_class) + u" "
            if new_class_test not in classes_test:
                new_classes += u" " + unicode(new_class)
        except TypeError:
            pass
        return new_classes

class BitFieldCheckboxSelectMultiple(BitFieldWidgetMixin, forms.CheckboxSelectMultiple):

    def _has_changed(self, initial, data):
        #this doesn't work right
        #return False
        if initial is None:
            initial = []
        if data is None:
            data = []

        initial_set = set([force_unicode(key) for key, value in initial.items() if value])
        data_set = set([force_unicode(value) for value in data])
        return data_set != initial_set

    def render(self, name, value, attrs=None, choices=()):
        if type(value) is int:
            value = BitHandler(value, self.flags)
        if type(value) is BitHandler:
            value = [k for k, v in value if v]
        if value is None: value = []

        choices = enumerate(choices)
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = ['<ul class="bitfield_ul">']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = force_unicode(option_label)
            output.append(u'<li><label%s>%s %s</label></li>' % (label_for, rendered_cb, option_label))
        output.append('</ul>')
        return mark_safe('\n'.join(output))

class BitFieldButton(BitFieldWidgetMixin, forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if type(value) is int:
            value = BitHandler(value, self.flags)
        if type(value) is BitHandler:
            value = [k for k, v in value if v]
        if value is None: value = []

        choices = enumerate(choices)
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = ['<div id="%s_buttons">' % attrs['id']]
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):

            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''
            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = force_unicode(option_label)
            output.append(u'%s<label%s>%s</label>' % (rendered_cb, label_for, option_label))
        output.append('</div>')
        return mark_safe('\n'.join(output))

