# residual module

from obspy import UTCDateTime
from .measurement import *
from .WebAbsolutesFactory import WebAbsolutesFactory


def example_api():
    reading = Reading(
        metadata={"pier_correction": 1.23},
        measurements=[
            Measurement(
                NORTH_DOWN,
                from_dms(12, 15, 28),
                UTCDateTime("2018-01-01T17:01:02"),
                [-1, -2],
            )
        ],
    )
    return [reading]


def example_webabsolutes():
    factory = WebAbsolutesFactory()
    readings = factory.get_readings(
        "BOU", UTCDateTime("2016-01-01"), UTCDateTime("2016-02-01"), True
    )
    return readings
