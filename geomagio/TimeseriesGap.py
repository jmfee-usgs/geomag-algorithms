"""Timeseries gap"""


class TimeseriesGap(object):
    """Represent a gap in a timeseries.

    Parameters
    ----------
    start : obspy.core.UTCDateTime
        time of first missing sample.
    end : obspy.core.UTCDateTime
        time of last missing sample in gap.
        may be the same as start.
    next_start : obspy.core.UTCDateTime
        expected time of next sample.
    """
    def __init__(self, start, end, next_start):
        self.start = start
        self.end = end
        self.next_start = next_start

    def __repr__(self):
        """String representation of gap for debugging output.

        Returns
        -------
        representation : string
        """
        return '[' + str(self.start) + ' => ' + str(self.end) + ']'
