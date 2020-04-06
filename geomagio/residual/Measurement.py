from typing import Optional

from obspy.core import UTCDateTime
<<<<<<< HEAD
from .MeasurementType import MeasurementType


class Measurement(object):
=======
from pydantic import BaseModel

from .. import pydantic_utcdatetime
from .MeasurementType import MeasurementType


class Measurement(BaseModel):
>>>>>>> master
    """One angle and time measurement with optional residual.

    Attributes
    ----------
    measurement_type: type of measurement.
    angle: measured angle, decimal degrees.
    residual: residual at time of measurement.
    time: when measurement was taken.
<<<<<<< HEAD
    ordinate: variometer data from time of measurement
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
=======
    """

    measurement_type: MeasurementType
    angle: float = 0
    residual: float = 0
    time: Optional[UTCDateTime] = None
>>>>>>> master
