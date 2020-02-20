import numpy
from obspy.core import UTCDateTime


# declination
FIRST_MARK_UP = "FirstMarkUp"
FIRST_MARK_DOWN = "FirstMarkDown"
WEST_DOWN = "WestDown"
EAST_DOWN = "EastDown"
WEST_UP = "WestUp"
EAST_UP = "EastUp"
SECOND_MARK_UP = "SecondMarkUp"
SECOND_MARK_DOWN = "SecondMarkDown"
# inclination
SOUTH_DOWN = "SouthDown"
NORTH_UP = "NorthUp"
SOUTH_UP = "SouthUp"
NORTH_DOWN = "NorthDown"


class Absolute(object):
    def __init__(
        self,
        element,
        absolute=None,
        baseline=None,
        starttime=None,
        endtime=None,
        shift=0,
        valid=True,
    ):
        self.element = element
        self.absolute = absolute
        self.baseline = baseline
        self.starttime = starttime
        self.endtime = endtime
        self.shift = shift
        self.valid = valid


class Measurement(object):
    def __init__(self, measurement_type, angle, time=None, residuals=None):
        self.measurement_type = measurement_type
        self.angle = angle
        self.time = time
        self.residuals = residuals or []


class Reading(object):
    def __init__(self, absolutes=None, measurements=None, metadata=None):
        self.absolutes = absolutes or []
        self.measurements = measurements or []
        self.metadata = metadata or []

    def absolutes_index(self):
        return {a.element: a for a in self.absolutes}

    def measurement_index(self):
        return {m.measurement_type: m for m in self.measurements}


def from_dms(degrees=0, minutes=0, seconds=0):
    return degrees + (minutes / 60.0) + (seconds / 3600.0)


def to_dms(degrees):
    minutes = (degrees - int(degrees)) * 60
    seconds = (minutes - int(minutes)) * 60
    return {"degrees": int(degrees), "minutes": int(minutes), "seconds": seconds}

