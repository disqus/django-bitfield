import django
from django.apps import AppConfig


django.setup()


class BitFieldAppConfig(AppConfig):
    name = 'bitfield'
    verbose_name = "Bit Field"
