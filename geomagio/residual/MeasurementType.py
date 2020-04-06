import enum

<<<<<<< HEAD
# FIXME: add another measurement type that is a scaling measurement type
=======

>>>>>>> master
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

    # meridian
    # meridian is the average of declination measurements
    # but recorded because calculated and used during inclination measurements.
    MERIDIAN = "Meridian"

    # inclination
    SOUTH_DOWN = "SouthDown"
    NORTH_UP = "NorthUp"
    SOUTH_UP = "SouthUp"
    NORTH_DOWN = "NorthDown"
<<<<<<< HEAD

    # scaling
    NORTH_DOWN_SCALE = "NorthDownScale"
=======
>>>>>>> master
