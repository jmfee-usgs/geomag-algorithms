from typing import Optional

from obspy.core import UTCDateTime
from .MeasurementType import MeasurementType
from .Ordinate import Ordinate


class Measurement(object):
    """One angle and time measurement with optional residual.

    Attributes
    ----------
    measurement_type: type of measurement.
    angle: measured angle, decimal degrees.
    residual: residual at time of measurement.
    time: when measurement was taken.
    ordinate: variometer data from time of measurement
    """

    def __init__(
        self,
        measurement_type: MeasurementType,
        angle: float = 0,
        residual: float = 0,
        time: Optional[UTCDateTime] = None,
        ordinate: Optional[Ordinate] = None,
    ):
        self.measurement_type = measurement_type
        self.angle = angle
        self.residual = residual
        self.time = time
        self.ordinate = ordinate
