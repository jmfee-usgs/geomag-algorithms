"""Tests for the IMFV283 Parser class."""

from nose.tools import assert_equals, assert_not_equals
from obspy import UTCDateTime
from geomagio.metadata import get_observatory


TEST_OBSERVATORIES = {
    'TEST': [
        {
            'starttime': '2017-01-01',
            'endtime': None,

            'foo': 'bar'
        },
        {
            'starttime': '2016-01-01',
            'endtime': '2016-12-01',

            'foo': 'baz'
        }
    ]
}


def test_get_observatory_unknown():
    """metadata_test.observatory_test.test_get_observatory_unknown()

    Expect get_observatory to return None,
    when code is not defined.
    """
    obs = get_observatory('OTHER', observatories=TEST_OBSERVATORIES)
    assert_equals(obs, None)


def test_get_observatory_latest():
    """metadata_test.observatory_test.test_get_observatory_latest()

    Expect get_observatory to return latest epoch,
    when time not specified (and latest epoch doen't have endtime...)
    """
    obs = get_observatory('TEST', observatories=TEST_OBSERVATORIES)
    assert_equals(obs['foo'], 'bar')


def test_get_observatory_older():
    """metadata_test.observatory_test.test_get_observatory_older()

    Expect get_observatory to return specific epoch,
    when time is specified
    """
    obs = get_observatory('TEST', time=UTCDateTime('2016-06-01'),
            observatories=TEST_OBSERVATORIES)
    assert_equals(obs['foo'], 'baz')


def test_get_observatory_gap():
    """metadata_test.observatory_test.test_get_observatory_gap()

    Expect get_observatory to return None,
    if specified time is in a metadata gap
    """
    obs = get_observatory('TEST', time=UTCDateTime('2016-12-02'),
            observatories=TEST_OBSERVATORIES)
    assert_equals(obs, None)


def test_get_observatory_bou():
    """metadata_test.observatory_test.test_get_observatory_gap()

    Expect get_observatory to return None,
    if specified time is in a metadata gap
    """
    obs = get_observatory('BOU')
    assert_not_equals(obs, None)
