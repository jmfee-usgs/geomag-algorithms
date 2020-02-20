import json
import urllib
from obspy.core import UTCDateTime
from .measurement import Absolute, Measurement, Reading


class WebAbsolutesFactory(object):
    """Read absolutes from web absolutes service.
    """

    def __init__(self, url="https://geomag.usgs.gov/baselines/observation.json.php"):
        self.url = url

    def get_readings(self, observatory, starttime, endtime, include_measurements=False):
        args = urllib.parse.urlencode(
            {
                "observatory": observatory,
                "starttime": starttime.isoformat(),
                "endtime": endtime.isoformat(),
                "includemeasurements": include_measurements and "true" or "false",
            }
        )
        with urllib.request.urlopen(f"{self.url}?{args}") as data:
            return self.parse_response(data, include_measurements)

    def parse_response(self, jsonstr, include_measurements=False):
        readings = []
        response = json.load(jsonstr)
        for data in response["data"]:
            metadata = self._parse_metadata(data)
            readings.extend(
                [
                    self._parse_reading(metadata, r, include_measurements)
                    for r in data["readings"]
                ]
            )
        return readings

    def _parse_absolute(self, element, data):
        return Absolute(
            element,
            data["absolute"],
            data["baseline"],
            data["start"] and UTCDateTime(data["start"]) or None,
            data["end"] and UTCDateTime(data["end"]) or None,
            "shift" in data and data["shift"] or 0,
            data["valid"],
        )

    def _parse_measurement(self, data):
        return Measurement(
            data["type"],
            data["angle"],
            data["time"] and UTCDateTime(data["time"]) or None,
        )

    def _parse_metadata(self, data):
        return {
            "time": data["time"],
            "reviewed": data["reviewed"],
            "electronics": data["electronics"]["serial"],
            "theodolite": data["theodolite"]["serial"],
            "mark_name": data["mark"]["name"],
            "mark_azimuth": data["mark"]["azimuth"],
            "pier_name": data["pier"]["name"],
            "pier_correction": data["pier"]["correction"],
            "observer": data["observer"],
            "reviewer": data["reviewer"],
        }

    def _parse_reading(self, metadata, data, include_measurements):
        absolutes = [
            self._parse_absolute(element, data[element])
            for element in ["D", "H", "Z"]
            if element in data
        ]
        measurements = (
            (include_measurements and "measurements" in data)
            and [self._parse_measurement(m) for m in data["measurements"]]
            or []
        )
        return Reading(absolutes, measurements, metadata)

