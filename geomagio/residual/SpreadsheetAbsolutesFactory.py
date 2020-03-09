import os
from typing import Dict, IO, List, Mapping, Optional, Union

from obspy.core import UTCDateTime
import openpyxl

from .Absolute import Absolute
from .Measurement import Measurement
from .MeasurementType import MeasurementType as mt
from .Reading import Reading
from . import Angle


SPREADSHEET_MEASUREMENTS = [
    # first mark
    {"type": mt.FIRST_MARK_UP, "angle": "A13"},
    {"type": mt.FIRST_MARK_UP, "angle": "B13"},
    {"type": mt.FIRST_MARK_DOWN, "angle": "C13"},
    {"type": mt.FIRST_MARK_DOWN, "angle": "D13"},
    # declination
    {"type": mt.WEST_DOWN, "angle": "C19", "residual": "E19", "time": "B19"},
    {"type": mt.WEST_DOWN, "angle": "C20", "residual": "E20", "time": "B20"},
    {"type": mt.EAST_DOWN, "angle": "C21", "residual": "E21", "time": "B21"},
    {"type": mt.EAST_DOWN, "angle": "C22", "residual": "E22", "time": "B22"},
    {"type": mt.WEST_UP, "angle": "C23", "residual": "E23", "time": "B23"},
    {"type": mt.WEST_UP, "angle": "C24", "residual": "E24", "time": "B24"},
    {"type": mt.EAST_UP, "angle": "C25", "residual": "E25", "time": "B25"},
    {"type": mt.EAST_UP, "angle": "C26", "residual": "E26", "time": "B26"},
    # second mark
    {"type": mt.SECOND_MARK_UP, "angle": "A31"},
    {"type": mt.SECOND_MARK_UP, "angle": "B31"},
    {"type": mt.SECOND_MARK_DOWN, "angle": "C31"},
    {"type": mt.SECOND_MARK_DOWN, "angle": "D31"},
    # meridian
    {"type": mt.MERIDIAN, "angle": "C37"},
    # inclination
    {"type": mt.SOUTH_DOWN, "angle": "D37", "residual": "E37", "time": "B37"},
    {"type": mt.SOUTH_DOWN, "angle": "D38", "residual": "E38", "time": "B38"},
    {"type": mt.NORTH_UP, "angle": "D39", "residual": "E39", "time": "B39"},
    {"type": mt.NORTH_UP, "angle": "D40", "residual": "E40", "time": "B40"},
    {"type": mt.SOUTH_UP, "angle": "D41", "residual": "E41", "time": "B41"},
    {"type": mt.SOUTH_UP, "angle": "D42", "residual": "E42", "time": "B42"},
    {"type": mt.NORTH_DOWN, "angle": "D43", "residual": "E43", "time": "B43"},
    {"type": mt.NORTH_DOWN, "angle": "D44", "residual": "E44", "time": "B44"},
    {"type": mt.NORTH_DOWN, "angle": "D45", "residual": "E45", "time": "B45"},
]


def parse_relative_time(base_date: str, time: str) -> UTCDateTime:
    """Parse a relative date.

    Arguments
    ---------
    base_date: date when time occurs (YYYYMMDD)
    time: time on base_date (HHMMSS)
        left padded with zeros to 6 characters
    """
    try:
        return UTCDateTime(f"{base_date}T{time:06}")
    except Exception as e:
        print(f"error parsing relative date '{base_date}T{time:06}': {e}")
        return None


class SpreadsheetAbsolutesFactory(object):
    """Read absolutes from residual spreadsheets.

    Attributes
    ----------
    base_directory: directory where spreadsheets exist.
        Assumed structure is base/OBS/YEAR/OBS/*.xlsm
        Where each xlsm file is named OBS-YEARJULHHMM.xlsm
    """

    def __init__(self, base_directory="/Volumes/geomag/pub/observatories"):
        self.base_directory = base_directory

    def get_readings(
        self,
        observatory: str,
        starttime: UTCDateTime,
        endtime: UTCDateTime,
        include_measurements: bool = True,
    ) -> List[Reading]:
        """Read spreadsheet files between starttime/endtime.
        """
        readings = []
        start_filename = f"{observatory}-{starttime.datetime:%Y%j%H%M}.xlsm"
        end_filename = f"{observatory}-{endtime.datetime:%Y%j%H%M}.xlsm"
        for year in range(starttime.year, endtime.year + 1):
            # start in observatory year directory to scan fewer files
            observatory_directory = os.path.join(
                self.base_directory, observatory, f"{year}", observatory
            )
            for (dirpath, dirnames, filenames) in os.walk(observatory_directory):
                for filename in filenames:
                    if start_filename <= filename < end_filename:
                        readings.append(
                            self.parse_spreadsheet(os.path.join(dirpath, filename))
                        )
        return readings

    def parse_spreadsheet(self, path: str, include_measurements=True) -> Reading:
        """Parse a residual spreadsheet file.

        Be sure to check Reading metadata for errors.
        """
        workbook = openpyxl.load_workbook(path, data_only=True)
        constants_sheet = workbook["constants"]
        measurement_sheet = workbook["measurement"]
        summary_sheet = workbook["Summary"]
        metadata = self._parse_metadata(
            constants_sheet, measurement_sheet, summary_sheet
        )
        absolutes = self._parse_absolutes(summary_sheet, metadata["date"])
        measurements = (
            include_measurements
            and self._parse_measurements(measurement_sheet, metadata["date"])
            or None
        )
        return Reading(
            absolutes=absolutes,
            azimuth=metadata["mark_azimuth"],
            hemisphere=metadata["hemisphere"],
            measurements=measurements,
            metadata=metadata,
            pier_correction=metadata["pier_correction"],
        )

    def _parse_absolutes(
        self, sheet: openpyxl.worksheet, base_date: str
    ) -> List[Absolute]:
        """Parse absolutes from a summary sheet.
        """
        absolutes = [
            Absolute(
                element="D",
                absolute=Angle.from_dms(
                    degrees=sheet["C12"].value, minutes=sheet["D12"].value
                ),
                baseline=Angle.from_dms(minutes=sheet["F12"].value),
                endtime=parse_relative_time(base_date, sheet["B12"].value),
                starttime=parse_relative_time(base_date, sheet["B12"].value),
            ),
            Absolute(
                element="H",
                absolute=sheet["C17"].value,
                baseline=sheet["F17"].value,
                endtime=parse_relative_time(base_date, sheet["B17"].value),
                starttime=parse_relative_time(base_date, sheet["B17"].value),
            ),
            Absolute(
                element="Z",
                absolute=sheet["C22"].value,
                baseline=sheet["F22"].value,
                endtime=parse_relative_time(base_date, sheet["B22"].value),
                starttime=parse_relative_time(base_date, sheet["B22"].value),
            ),
        ]
        return absolutes

    def _parse_measurements(
        self, sheet: openpyxl.worksheet, base_date: str
    ) -> List[Measurement]:
        """Parse measurements from a measurement sheet.
        """
        measurements = []
        for m in SPREADSHEET_MEASUREMENTS:
            measurement_type = m["type"]
            angle = "angle" in m and sheet[m["angle"]].value or None
            residual = "residual" in m and sheet[m["residual"]].value or None
            time = (
                "time" in m
                and parse_relative_time(base_date, sheet[m["time"]].value)
                or None
            )
            measurements.append(
                Measurement(
                    measurement_type=measurement_type,
                    angle=angle,
                    residual=residual,
                    time=time,
                )
            )
        return measurements

    def _parse_metadata(
        self,
        constants_sheet: openpyxl.worksheet,
        measurement_sheet: openpyxl.worksheet,
        summary_sheet: openpyxl.worksheet,
    ) -> Dict:
        """Parse metadata from various sheets.
        """
        errors = []
        mark_azimuth = None
        try:
            azimuth_number = measurement_sheet["F8"].value
            mark_azimuth = Angle.from_dms(
                minutes=constants_sheet[f"F{azimuth_number + 5}"].value
            )
        except:
            errors.append("Unable to read mark azimuth")
        year = measurement_sheet["B8"].value
        return {
            # pad in case month starts with zero (which is trimmed)
            "date": f"{year}{measurement_sheet['C8'].value:04}",
            "di_scale": measurement_sheet["K8"].value,
            "errors": errors,
            "hemisphere": measurement_sheet["J8"].value,
            "instrument": f"{summary_sheet['B4'].value}",
            "mark_azimuth": mark_azimuth,
            "observer": measurement_sheet["E8"].value,
            "pier_correction": constants_sheet["H6"].value,
            "pier_name": summary_sheet["B5"].value,
            "station": measurement_sheet["A8"].value,
            "temperature": constants_sheet["J58"].value,
            "year": year,
        }
