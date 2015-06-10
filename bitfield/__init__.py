"""
django-bitfield
~~~~~~~~~~~~~~~
"""
from __future__ import absolute_import

from bitfield.models import Bit, BitHandler, CompositeBitField, BitField  # NOQA


try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('bitfield').version
except Exception:
    VERSION = 'unknown'
