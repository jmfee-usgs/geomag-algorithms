from obspy.core import UTCDateTime


class Flag(object):
    """
    Object for holding a flag object. A flag can be either a spike, gap, disturbance, or offset within the data
    """

    def __init__(
        self,
        starttime: UTCDateTime = None,
        endtime: UTCDateTime = None,
        observatory: str = None,
        channel: str = None,
        type: str = None,
        comment: str = None,
    ):
        self.starttime = starttime
        self.endtime = endtime
        self.observatory = observatory
        self.type = type
        self.channel = channel
        self.comment = comment
