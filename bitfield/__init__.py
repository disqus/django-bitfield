"""
django-bitfield
~~~~~~~~~~~~~~~
"""

try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('bitfield').version
except Exception as e:
    VERSION = 'unknown'

from bitfield.models import Bit, BitHandler, CompositeBitField, BitField  # noqa
