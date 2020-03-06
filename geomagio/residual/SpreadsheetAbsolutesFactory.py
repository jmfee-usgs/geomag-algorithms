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


def _parse_float(sheet, cell, name) -> float:
    try:
        value = sheet[cell].value
        return value and float(value) or None
    except ValueError as e:
        raise ValueError(f"Unable to parse {name} at {cell}") from e


def _parse_int(sheet, cell, name) -> int:
    try:
        value = sheet[cell].value
        return value and int(value) or None
    except ValueError as e:
        raise ValueError(f"Unable to parse {name} at {cell}") from e


def _parse_time(sheet, cell, name, base_date) -> UTCDateTime:
    try:
        value = sheet[cell].value
        print(f"{base_date}{value}", value)
        return value and UTCDateTime(f"{base_date}{value}") or None
    except Exception as e:
        raise ValueError(f"Unable to parse {name} at {cell}") from e


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
            observatory_directory = os.path.join(
                self.base_directory, observatory, f"{year}", observatory
            )
            for (dirpath, dirnames, filenames) in os.walk(observatory_directory):
                for filename in filenames:
                    if start_filename < filename < end_filename:
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
        measurements = None
        if include_measurements:
            measurements, errors = self._parse_measurements(measurement_sheet, metadata)
            metadata["errors"].extend(errors)
        absolutes = self._parse_absolutes(summary_sheet, metadata)
        reading = Reading(
            absolutes=absolutes,
            azimuth=metadata["mark_azimuth"],
            hemisphere=metadata["hemisphere"],
            measurements=measurements,
            metadata=metadata,
            pier_correction=metadata["pier_correction"],
        )
        return reading

    def _parse_absolutes(self, sheet, metadata) -> List[Absolute]:
        """Parse absolutes from a summary sheet.
        """
        base_date = f"{metadata['year']}{metadata['date']}T"
        absolutes = [
            Absolute(
                element="D",
                absolute=Angle.from_dms(
                    degrees=int(sheet["C12"].value), minutes=float(sheet["D12"].value)
                ),
                baseline=Angle.from_dms(minutes=float(sheet["F12"].value)),
                endtime=UTCDateTime(f"{base_date}{sheet['B12'].value}"),
                starttime=UTCDateTime(f"{base_date}{sheet['B12'].value}"),
            ),
            Absolute(
                element="H",
                absolute=float(sheet["C17"].value),
                baseline=float(sheet["F17"].value),
                endtime=UTCDateTime(f"{base_date}{sheet['B17'].value}"),
                starttime=UTCDateTime(f"{base_date}{sheet['B17'].value}"),
            ),
            Absolute(
                element="Z",
                absolute=float(sheet["C22"].value),
                baseline=float(sheet["F22"].value),
                endtime=UTCDateTime(f"{base_date}{sheet['B22'].value}"),
                starttime=UTCDateTime(f"{base_date}{sheet['B22'].value}"),
            ),
        ]
        return absolutes

    def _parse_measurements(
        self, sheet, metadata
    ) -> (List[Measurement], List[ValueError]):
        """Parse measurements from a measurement sheet.
        """
        base_date = f"{metadata['year']}{metadata['date']}T"
        errors = []
        measurements = []

        for m in SPREADSHEET_MEASUREMENTS:
            measurement_type = m["type"]
            angle = None
            residual = None
            time = None
            try:
                if "angle" in m:
                    angle = _parse_float(sheet, m["angle"], f"{measurement_type} angle")
                if "residual" in m:
                    residual = _parse_float(
                        sheet, m["residual"], f"{measurement_type} residual"
                    )
                if "time" in m:
                    time = _parse_time(
                        sheet, m["time"], f"{measurement_type} time", base_date
                    )
            except ValueError as e:
                errors.append(str(e))
                continue
            measurements.append(
                Measurement(
                    measurement_type=measurement_type,
                    angle=angle,
                    residual=residual,
                    time=time,
                )
            )
        return measurements, errors

    def _parse_metadata(
        self, constants_sheet, measurement_sheet, summary_sheet
    ) -> Dict:
        """Parse metadata from various sheets.
        """
        errors = []
        hemisphere = None
        mark_azimuth = None
        pier_correction = None
        temperature = None
        try:
            azimuth_number = _parse_int(measurement_sheet, "F8", "azimuth number")
            mark_azimuth = _parse_float(
                constants_sheet, f"F{azimuth_number + 5}", "mark azimuth"
            )
        except ValueError as e:
            errors.append(str(e))
        try:
            hemisphere = _parse_int(measurement_sheet, "J8", "hemisphere")
        except ValueError as e:
            errors.append(str(e))
        try:
            pier_correction = _parse_float(constants_sheet, "H6", "pier_correction")
        except ValueError as e:
            errors.append(str(e))
        try:
            temperature = _parse_float(constants_sheet, "J58", "temperature")
        except ValueError as e:
            errors.append(str(e))
        return {
            "date": f"{measurement_sheet['C8'].value:04}",
            "di_scale": measurement_sheet["K8"].value,
            "errors": errors,
            "hemisphere": hemisphere,
            "instrument": summary_sheet["B4"].value,
            "mark_azimuth": mark_azimuth,
            "observer": measurement_sheet["E8"].value,
            "pier_correction": pier_correction,
            "pier_name": summary_sheet["B5"].value,
            "station": measurement_sheet["A8"].value,
            "temperature": temperature,
            "year": measurement_sheet["B8"].value,
        }
