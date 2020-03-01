import collections
import enum
from typing import Dict, List, Optional, Mapping

import numpy
from obspy.core import UTCDateTime


class MeasurementType(str, enum.Enum):
    """Measurement types used during absolutes."""

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
    """Computed absolute and baseline measurement.

    Attributes
    ----------
    element: the absolute and baseline component.
    absolute: absolute measurement.
    baseline: baseline measurement.
    starttime: time of first measurement used.
    endtime: time of last measurement used.
    shift: used to correct polarity.
    valid: whether values are considered valid.
    """

    def __init__(
        self,
        element: str,
        absolute: Optional[float] = None,
        baseline: Optional[float] = None,
        starttime: Optional[UTCDateTime] = None,
        endtime: Optional[UTCDateTime] = None,
        shift: float = 0,
        valid: bool = True,
    ):
        self.element = element
        self.absolute = absolute
        self.baseline = baseline
        self.starttime = starttime
        self.endtime = endtime
        self.shift = shift
        self.valid = valid


class Measurement(object):
    """One angle and time measurement with optional residual.

    Attributes
    ----------
    measurement_type: type of measurement.
    angle: measured angle, decimal degrees.
    residual: residual at time of measurement.
    time: when measurement was taken.
    """

    def __init__(
        self,
        measurement_type: MeasurementType,
        angle: float = 0,
        residual: float = 0,
        time: Optional[UTCDateTime] = None,
    ):
        self.measurement_type = measurement_type
        self.angle = angle
        self.residual = residual
        self.time = time


class Reading(object):
    """A collection of absolute measurements.

    Attributes
    ----------
    absolutes: absolutes computed from measurements.
    azimuth: azimuth angle to mark used for measurements, decimal degrees.
    hemisphere: 1 for northern hemisphere, -1 for southern hemisphere
    measurements: raw measurements used to compute absolutes.
    metadata: metadata used during absolute calculations.
    pier_correction: pier correction value, nT.
    """

    def __init__(
        self,
        absolutes: Optional[List[Absolute]] = None,
        azimuth: float = 0,
        hemisphere: float = 1,  # maybe hemisphere should be calculated from latitude
        measurements: Optional[List[Measurement]] = None,
        metadata: Optional[Dict] = None,
        pier_correction: float = 0,
    ):
        self.absolutes = absolutes or []
        self.measurements = measurements or []
        self.metadata = metadata or []

    def absolutes_index(self) -> Mapping[str, Absolute]:
        """Generate index of absolutes keyed by element.
        """
        return {a.element: a for a in self.absolutes}

    def measurement_index(self) -> Dict[MeasurementType, List[Measurement]]:
        """Generate index of measurements keyed by MeasurementType.

        Any missing MeasurementType returns an empty list.
        There may be multiple measurements of each MeasurementType.
        """
        index = collections.defaultdict(list)
        for m in self.measurements:
            index[m.measurement_type].append(m)
        return index


def from_dms(degrees: float = 0, minutes: float = 0, seconds: float = 0) -> float:
    """Convert degrees, minutes, seconds to decimal degrees"""
    return degrees + (minutes / 60.0) + (seconds / 3600.0)


def to_dms(degrees: float) -> List[float]:
    """Convert decimal degrees to degrees, minutes, seconds"""
    minutes = (degrees - int(degrees)) * 60
    seconds = (minutes - int(minutes)) * 60
    return [int(degrees), int(minutes), seconds]
