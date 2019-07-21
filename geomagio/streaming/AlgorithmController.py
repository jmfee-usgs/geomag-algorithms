from geomagio.algorithm import Algorithm
from obspy.core import Stream, UTCDateTime


class AlgorithmController(object):
    """Streaming controller for algorithm.

    Parameters
    ----------
    components: list
        each list item should contain kwargs to select channels distinctly.
    algorithm: geomagio.algorithm.Algorithm
        algorithm for processing
    max_delay: float
        when greater than 0, number of seconds to wait before trimming,
        otherwise, ignored.
    left_pad: int
        number of samples requried preceding a data point for processing.
    right_pad: int
        number of samples required following a data point for processing.
    """
    def __init__(self, components,
            algorithm=None, max_delay=0, left_pad=0, right_pad=0):
        self.components = components
        self.algorithm = algorithm or Algorithm()
        self.max_delay = 0
        self.left_pad = 0
        self.right_pad = 0
        self.input = Stream()
        self.listeners = []

    def on_data(self, stream):
        """Receive data.

        Calls _process to check whether data is ready to be processed.
        Notifies listeners if output is generated.

        Parameters
        ----------
        stream: obspy.core.Trace|obspy.core.Stream
            data to be added to input
        """
        if not isinstance(stream, Stream):
            stream = Stream(stream)
        for component in self.components:
            self.input += stream.select(**component).copy()
        self.input.merge()
        output = self._process()
        if len(output) > 0:
            self.notify_listeners(output)

    def notify_listeners(self, data):
        """Call all listeners with provided data.

        Parameters
        ----------
        data: obspy.core.Stream
            data produced during processing
        """
        for listener in self.listeners:
            listener.on_data(data)

    def _process(self):
        """Incrementally process from input data stream.

        Returns
        -------
        obspy.core.Stream
            result from processing, empty if no data processed.
        """
        output = Stream()
        if len(self.input) == 0:
            # no data to process
            return output
        # assume uniform delta for now
        delta = self.input[0].stats.delta
        overlap = get_overlap(self.input, self.components)
        if overlap:
            if (overlap[1] - overlap[0]) \
                    < (self.left_pad + self.right_pad) * delta:
                # need more data for algorithm
                return output
            # process overlapping area
            data = self.input.slice(
                    starttime=overlap[0],
                    endtime=overlap[1],
                    nearest_sample=False)
            output = self.algorithm.process(data)
            # TODO: should this verify output was produced?
            # remove input data that is no longer needed
            trim_time = max(
                # don't trim before starttime
                overlap[0],
                # don't trim data that is still needed
                overlap[1] - (self.left_pad * delta) + delta)
            self.input.trim(starttime=trim_time, nearest_sample=False)
        elif self.max_delay > 0:
            #  remove data before max delay.
            cutoff = UTCDateTime() - (self.left_pad * delta) - self.max_delay
            self.input.trim(starttime=cutoff, nearest_sample=False)
        return output


def get_overlap(stream, components):
    """Check for overlaps between requested components.

    Parameters
    ----------
    stream: obspy.core.Stream
        stream with data.
    components: list
        list of kwargs objects to select desired components.

    Returns
    -------
    list
        overlapping time period as (starttime, endtime) UTCDateTime tuple,
        or False if there is not overlap between requested components.
    """
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
