import enum


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
