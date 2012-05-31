from django import forms
from bitfield.tests.models import BitFieldTestModel, CompositeBitFieldTestModel

class BitFieldTestModelForm(forms.ModelForm):
    
    class Meta:
        model = BitFieldTestModel
