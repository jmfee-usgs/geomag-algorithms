#! /usr/bin/env python

from os import path
import sys
# ensure geomag is on the path before importing
try:
    import geomagio  # noqa (tells linter to ignore this line.)
except ImportError:
    script_dir = path.dirname(path.abspath(__file__))
    sys.path.append(path.normpath(path.join(script_dir, '..')))

import numpy
from obspy.core import Stats, Stream, Trace, UTCDateTime
from geomagio.streaming import AlgorithmController, SeedLinkInput


class AddAlgorithm(object):
    def __init__(self, out_channel):
        self.out_channel = out_channel

    def process(self, stream):
        stats = Stats(stream[0].stats)
        stats.channel = self.out_channel
        # sum all arrays
        data = numpy.zeros(stats.npts)
        for trace in stream:
            data += trace.data
        return Stream(Trace(data, stats))


class MultiplyAlgorithm(object):
    def __init__(self, multiplier):
        self.multiplier = multiplier

    def process(self, stream):
        for trace in stream:
            trace.data = trace.data * self.multiplier
        return stream


class PrintListener(object):
    def on_data(self, data):
        print(data)
        print(data[0].data)

if __name__ == '__main__':
    # wire everything up
    seedlink = SeedLinkInput('cwbpub.cr.usgs.gov:18000', autoconnect=False)
    # compute U component
    u_volt = AlgorithmController(
        [{'channel': 'U_Volt'}],
        MultiplyAlgorithm(100.0)
    )
    seedlink.listeners.append(u_volt)
    u_bin = AlgorithmController(
        [{'channel': 'U_Bin'}],
        MultiplyAlgorithm(500.0)
    )
    seedlink.listeners.append(u_bin)
    u = AlgorithmController(
        [{'channel': 'U_Bin'}, {'channel': 'U_Volt'}],
        AddAlgorithm('U')
    )
    u_bin.listeners.append(u)
    u_volt.listeners.append(u)

    # set up debug listener
    out = PrintListener()
    u.listeners.append(out)

    # simulate data
    bin = Trace(
            numpy.array([10, 20,30, 40, 50], dtype=numpy.float64),
            Stats(header={
                'network': 'NT',
                'station': 'LLO',
                'channel': 'BYU',
                'location': 'R0',
                'starttime': UTCDateTime('2019-01-01T00:02:00Z'),
                'delta': 60,
                'npts': 5
            })
    )
    volt = Trace(
            numpy.array([1, 2, 3, 4, 5], dtype=numpy.float64),
            Stats(header={
                'network': 'NT',
                'station': 'LLO',
                'channel': 'BEU',
                'location': 'R0',
                'starttime': UTCDateTime('2019-01-01T00:02:00Z'),
                'delta': 60,
                'npts': 5
            })
    )
    seedlink.on_data(bin)
    seedlink.on_data(volt)
