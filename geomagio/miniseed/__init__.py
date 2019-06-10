"""IO Module for MiniSEED Format
"""
from __future__ import absolute_import

from .sncl import decode_sncl, encode_sncl


__all__ = [
    'decode_sncl',
    'encode_sncl'
]
