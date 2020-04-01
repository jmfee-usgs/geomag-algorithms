import collections
from typing import Dict, List, Optional

from .Absolute import Absolute
from .Measurement import Measurement
from .MeasurementType import MeasurementType
from .Ordinate import Ordinate
from .Calculation import calculate


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
        ordinates: Optional[List[Ordinate]] = None,
        pier_correction: float = 0,
    ):
        self.absolutes = absolutes or []
        self.measurements = measurements or []
        self.metadata = metadata or []
        self.ordinates = ordinates or []

    def absolutes_index(self) -> Dict[str, Absolute]:
        """Generate index of absolutes keyed by element.
        """
        return {a.element: a for a in self.absolutes}

    # FIXME: Move method into calculation module. Make a method in this module that updates absolutes
    def update_absolutes(self):
        self.absolutes = calculate(self)

    def measurement_index(self) -> Dict[MeasurementType, List[Measurement]]:
        """Generate index of measurements keyed by MeasurementType.

        Any missing MeasurementType returns an empty list.
        There may be multiple measurements of each MeasurementType.
        """
        index = collections.defaultdict(list)
        for m in self.measurements:
            index[m.measurement_type].append(m)
        return index

    def ordinate_index(self) -> Dict[MeasurementType, List[Ordinate]]:
        """Generate index of ordinates keyed by MeasurementType.

        Any missing MeasurementType returns an empty list.
        There may be multiple ordinates of each MeasurementType.
        """
        index = collections.defaultdict(list)
        for o in self.ordinates:
            index[o.measurement_type].append(o)
        return index
