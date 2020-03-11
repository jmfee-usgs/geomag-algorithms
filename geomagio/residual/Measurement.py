from typing import Optional

from obspy.core import UTCDateTime
from pydantic import BaseModel

from .. import pydantic_utcdatetime
from .MeasurementType import MeasurementType
from .Ordinate import Ordinate


class Measurement(BaseModel):
    """One angle and time measurement with optional residual.

    Attributes
    ----------
    measurement_type: type of measurement.
    angle: measured angle, decimal degrees.
    residual: residual at time of measurement.
    time: when measurement was taken.
    ordinate: variometer data from time of measurement
    """

    measurement_type: MeasurementType
    angle: float = 0
    residual: float = 0
    time: Optional[UTCDateTime] = None
    ordinate: Ordinate = None
