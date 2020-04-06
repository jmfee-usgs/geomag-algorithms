from typing import Optional
<<<<<<< HEAD
from obspy import UTCDateTime


class Absolute(object):
=======

from obspy import UTCDateTime
from pydantic import BaseModel

from .. import pydantic_utcdatetime


class Absolute(BaseModel):
>>>>>>> master
    """Computed absolute and baseline measurement.

    Attributes
    ----------
    element: the absolute and baseline component.
    absolute: absolute measurement.
        nT or ?radians?
    baseline: baseline measurement.
        nT or ?radians?
    starttime: time of first measurement used.
    endtime: time of last measurement used.
    shift: used to correct polarity.
    valid: whether values are considered valid.
    """

<<<<<<< HEAD
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
=======
    element: str
    absolute: Optional[float] = None
    baseline: Optional[float] = None
    starttime: Optional[UTCDateTime] = None
    endtime: Optional[UTCDateTime] = None
    shift: float = 0
    valid: bool = True
>>>>>>> master

    def is_valid(self) -> bool:
        return (
            self.valid
            and self.absolute is not None
            and self.baseline is not None
            and self.element is not None
            and self.endtime is not None
            and self.starttime is not None
        )
