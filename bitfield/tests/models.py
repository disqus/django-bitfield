from django.db import models

from bitfield import BitField

class BitFieldTestModel(models.Model):
    flags = BitField(flags=(
        'FLAG_0',
        'FLAG_1',
        'FLAG_2',
        'FLAG_3',
    ), default=3)
