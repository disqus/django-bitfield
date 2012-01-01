"""
django-bitfield
~~~~~~~~~~~~~~~
"""

try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('bitfield').version
except Exception, e:
    VERSION = 'unknown'

from .models import Bit, BitHandler, CompositeBitField, BitField