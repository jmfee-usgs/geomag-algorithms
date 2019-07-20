

from geomagio.algorithm import Algorithm
from obspy.core import Stream, UTCDateTime


class AlgorithmController(object):
    def __init__(self, components,
            algorithm=None, max_delay=0, left_pad=0, right_pad=0):
        self.components = components
        self.algorithm = algorithm or Algorithm()
        self.max_delay = 0
        self.left_pad = 0
        self.right_pad = 0
        self.input = Stream()
        self.listeners = []

    def on_data(self, trace):
        self.input += trace
        self.input.merge()
        output = process(
                self.input,
                self.components,
                lambda d: self.process(d),
                self.max_delay,
                self.left_pad,
                self.right_pad)
        if len(output) > 0:
            self.notify_listeners(output)

    def notify_listeners(self, data):
        for listener in self.listeners:
            listener.on_data(data)

    def process(self, stream):
        return self.algorithm.process(stream)


def get_overlap(stream, components):
    # get range for requested components
    ranges = []
    missing = False
    for component in components:
        traces = stream.select(**component)
        if not traces:
            ranges.append(None)
            missing = True
        elif len(traces) > 1:
            raise "expected only one trace per component"
        else:
            trace = traces[0]
            ranges.append((trace.stats.starttime, trace.stats.endtime))
    # find overlapping area.
    overlap = False
    if not missing:
        overlap = (
            max(r[0] for r in ranges),
            min(r[1] for r in ranges))
    return overlap


def process(input, components, callback, max_delay=0, left_pad=0, right_pad=0):
    output = Stream()
    overlap = get_overlap(input, components)
    if overlap and (overlap[1] - overlap[0]) > (left_pad + right_pad):
        #  process overlapping area
        data = input.slice(
                starttime=overlap[0],
                endtime=overlap[1],
                nearest_sample=False)
        output = callback(data)
        # remove input data that is no longer needed
        trim_time = max(
            # don't trim before starttime
            overlap[0],
            # don't trim data that is still needed
            overlap[1] - left_pad)
        # TODO: this currently leaves one extra sample
        input.trim(starttime=trim_time, nearest_sample=False)
    elif max_delay > 0:
        #  remove data before max delay.
        cutoff = UTCDateTime() - left_pad - max_delay
        input.trim(starttime=cutoff, nearest_sample=False)
    return output
