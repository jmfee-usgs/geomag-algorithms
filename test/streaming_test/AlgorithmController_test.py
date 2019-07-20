
import numpy
from obspy.core import Stats, Trace, UTCDateTime
from nose.tools import assert_equals

from geomagio.streaming import AlgorithmController


class TestListener(object):
    def __init__(self):
        self.data = []

    def on_data(self, data):
        self.data.append(data)


def test_algorithm_controller():
    """streaming_test.AlgorithmController_test.test_algorithm_controller()
    """
    client = AlgorithmController(
            [
                {'network': 'NT', 'station': 'LLO', 'channel': 'BEU'},
                {'network': 'NT', 'station': 'LLO', 'channel': 'BYU'}
            ])

    listener = TestListener()
    client.listeners.append(listener)

    # add data for one component
    trace = Trace(
            numpy.array([1, 2, 3, 4, 5]),
            Stats(header={
                'network': 'NT', 'station': 'LLO', 'channel': 'BEU',
                'starttime': UTCDateTime('2019-01-01T00:01:00Z'),
                'delta': 60,
                'npts': 5
            })
    )
    client.on_data(trace)
    # no data "processed" yet
    assert_equals(len(listener.data), 0)

    # add overlapping data for other component
    trace = Trace(
            numpy.array([2, 3, 4, 5, 6]),
            Stats(header={
                'network': 'NT', 'station': 'LLO', 'channel': 'BYU',
                'starttime': UTCDateTime('2019-01-01T00:02:00Z'),
                'delta': 60,
                'npts': 5
            })
    )
    client.on_data(trace)
    # overlapping data processed
    assert_equals(len(listener.data), 1)
    output = listener.data[0]
    assert_equals(
            output[0].stats.starttime,
            UTCDateTime('2019-01-01T00:02:00Z'))
    assert_equals(len(output[0].data), 4)
    # client input trimmed
    # TODO: currently leaves one extra sample
    # assert_equals(
    #       client.input[0].stats.starttime,
    #       UTCDateTime('2019-01-01T00:06:00Z'))
