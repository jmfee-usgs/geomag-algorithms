"""IO Module for MiniSEED Format
"""
from __future__ import absolute_import

from .sncl import decode_sncl, decode_stream, encode_sncl, encode_stream


__all__ = [
    'decode_sncl',
    'decode_stream',
    'encode_sncl',
    'encode_stream'
]
