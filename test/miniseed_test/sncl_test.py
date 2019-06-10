"""Tests for the miniseed.sncl module."""

from nose.tools import assert_equals

from geomagio.miniseed import sncl

TESTS = [
    [
        {
            'network': 'NT',
            'station': 'TEST',
            'channel': 'BEU',
            'location': 'R0'
        },
        {
            'network': 'NT',
            'observatory': 'TEST',
            'element': 'U_Volt',
            'data_type': 'variation',
            'data_interval': 'tenhertz'
        }
    ],

    [
        {
            'network': 'NT',
            'station': 'TEST',
            'channel': 'LFH',
            'location': 'RD'
        },
        {
            'network': 'NT',
            'observatory': 'TEST',
            'element': 'H_Dist',
            'data_type': 'variation',
            'data_interval': 'second'
        }
    ],

    [
        {
            'network': 'NT',
            'station': 'TEST',
            'channel': 'UFZ',
            'location': 'A0'
        },
        {
            'network': 'NT',
            'observatory': 'TEST',
            'element': 'Z',
            'data_type': 'adjusted',
            'data_interval': 'minute'
        }
    ]
]


def test_decode_sncl():
    """miniseed_test.sncl_test.test_decode_sncl()
    """
    for test in TESTS:
        actual = sncl.decode_sncl(**test[0])
        assert_equals(actual, test[1])


def test_encode_sncl():
    """miniseed_test.sncl_test.test_encode_sncl()
    """
    for test in TESTS:
        actual = sncl.encode_sncl(**test[1])
        assert_equals(actual, test[0])
