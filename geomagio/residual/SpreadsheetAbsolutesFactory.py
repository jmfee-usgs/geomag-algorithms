from typing import Dict, IO, List, Mapping, Optional, Union

from obspy.core import UTCDateTime
import openpyxl

from .measurement import Absolute, Measurement, MeasurementType, Reading, from_dms


class SpreadsheetAbsolutesFactory(object):
    """Read absolutes from residual spreadsheets.
    """

    def __init__(self):
        pass

    def get_readings(
        self,
        observatory: str,
        starttime: UTCDateTime,
        endtime: UTCDateTime,
        include_measurements: bool = False,
    ) -> List[Reading]:
        pass

    def parse_spreadsheet(self, path: str) -> Reading:
        workbook = openpyxl.load_workbook(path, data_only=True)
        constants_sheet = workbook["constants"]
        measurement_sheet = workbook["measurement"]
        summary_sheet = workbook["Summary"]
        metadata = self._parse_metadata(
            constants_sheet, measurement_sheet, summary_sheet
        )
        measurements = self._parse_measurements(measurement_sheet, metadata)
        absolutes = self._parse_absolutes(summary_sheet)
        reading = Reading(
            absolutes=absolutes,
            azimuth=metadata["mark_azimuth"],
            hemisphere=metadata["hemisphere"],
            measurements=measurements,
            metadata=metadata,
            pier_correction=metadata["pier_correction"],
        )
        return reading

    def _parse_absolutes(self, sheet) -> List[Absolute]:
        base_date = f"{sheet['H4'].value}{sheet['G4'].value}T"
        absolutes = [
            Absolute(
                element="D",
                absolute=from_dms(
                    degrees=int(sheet["C12"].value), minutes=float(sheet["D12"].value)
                ),
                baseline=from_dms(minutes=float(sheet["F12"].value)),
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

    def _parse_measurements(self, sheet, metadata) -> List[Measurement]:
        base_date = f"{metadata['year']}{metadata['date']}T"
        measurements = []
        # first mark
        first_mark = [
            {"type": MeasurementType.FIRST_MARK_UP, "cell": "A13"},
            {"type": MeasurementType.FIRST_MARK_UP, "cell": "B13"},
            {"type": MeasurementType.FIRST_MARK_DOWN, "cell": "C13"},
            {"type": MeasurementType.FIRST_MARK_DOWN, "cell": "D13"},
        ]
        for m in first_mark:
            measurements.append(
                Measurement(measurement_type=m["type"], angle=sheet[m["cell"]].value)
            )
        # declination
        declination = [
            {"type": MeasurementType.WEST_DOWN, "row": 19},
            {"type": MeasurementType.WEST_DOWN, "row": 20},
            {"type": MeasurementType.EAST_DOWN, "row": 21},
            {"type": MeasurementType.EAST_DOWN, "row": 22},
            {"type": MeasurementType.WEST_UP, "row": 23},
            {"type": MeasurementType.WEST_UP, "row": 24},
            {"type": MeasurementType.EAST_UP, "row": 25},
            {"type": MeasurementType.EAST_UP, "row": 26},
        ]
        for d in declination:
            row = d["row"]
            measurements.append(
                Measurement(
                    measurement_type=d["type"],
                    angle=sheet[f"C{row}"].value,
                    residual=sheet[f"E{row}"].value,
                    time=UTCDateTime(f"{base_date}{sheet[f'B{row}'].value}"),
                )
            )
        # second mark
        second_mark = [
            {"type": MeasurementType.SECOND_MARK_UP, "cell": "A31"},
            {"type": MeasurementType.SECOND_MARK_UP, "cell": "B31"},
            {"type": MeasurementType.SECOND_MARK_DOWN, "cell": "C31"},
            {"type": MeasurementType.SECOND_MARK_DOWN, "cell": "D31"},
        ]
        for m in second_mark:
            measurements.append(
                Measurement(measurement_type=m["type"], angle=sheet[m["cell"]].value)
            )
        # inclination
        inclination = [
            {"type": MeasurementType.SOUTH_DOWN, "row": 37},
            {"type": MeasurementType.SOUTH_DOWN, "row": 38},
            {"type": MeasurementType.NORTH_UP, "row": 39},
            {"type": MeasurementType.NORTH_UP, "row": 40},
            {"type": MeasurementType.SOUTH_UP, "row": 41},
            {"type": MeasurementType.SOUTH_UP, "row": 42},
            {"type": MeasurementType.NORTH_DOWN, "row": 43},
            {"type": MeasurementType.NORTH_DOWN, "row": 44},
            {"type": MeasurementType.NORTH_DOWN, "row": 45},
        ]
        for i in inclination:
            row = i["row"]
            measurements.append(
                Measurement(
                    measurement_type=i["type"],
                    angle=sheet[f"D{row}"].value,
                    residual=sheet[f"E{row}"].value,
                    time=UTCDateTime(f"{base_date}{sheet[f'B{row}'].value}"),
                )
            )
        return measurements

    def _parse_metadata(
        self, constants_sheet, measurement_sheet, summary_sheet
    ) -> Dict:
        azimuth_number = int(measurement_sheet["F8"].value)
        return {
            "date": measurement_sheet["C8"].value,
            "di_scale": measurement_sheet["K8"].value,
            "hemisphere": int(measurement_sheet["J8"].value),
            "instrument": summary_sheet["B4"].value,
            "mark_azimuth": float(constants_sheet[f"F{azimuth_number + 5}"].value),
            "observer": measurement_sheet["E8"].value,
            "pier_correction": float(constants_sheet["H6"].value),
            "pier_name": summary_sheet["B5"].value,
            "station": measurement_sheet["A8"].value,
            "temperature": float(measurement_sheet["J58"].value),
            "year": measurement_sheet["B8"].value,
        }
