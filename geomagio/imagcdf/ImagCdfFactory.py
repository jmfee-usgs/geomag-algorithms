import json
import sys
from typing import List, Optional, Tuple

import cdflib
import numpy
from obspy import Stream, Trace, UTCDateTime

from ..TimeseriesFactory import TimeseriesFactory
from ..TimeseriesUtility import get_delta_from_interval


PUBLICATION_LEVEL_DATA_TYPE = {
    "1": "variation",
    "2": "adjusted",
    "3": "quasi-definitive",
    "4": "definitive",
}
DATA_TYPE_PUBLICATION_LEVEL = {
    PUBLICATION_LEVEL_DATA_TYPE[k]: k for k in PUBLICATION_LEVEL_DATA_TYPE.keys()
}


class ImagCdfFactory(TimeseriesFactory):
    def __init__(self, **kwargs):
        TimeseriesFactory.__init__(self, **kwargs)

    def parse_file(
        self,
        path: str,
        observatory: Optional[str] = None,
        type: Optional[str] = None,
        interval: Optional[str] = None,
        channels: Optional[List[str]] = None,
    ) -> Stream:
        print(
            f"parse_file({path}, {observatory}, {type}, {interval}, {channels}",
            file=sys.stderr,
        )
        # open file
        cdf = cdflib.cdfread.CDF(path=path)
        # read metadata
        globalatts = cdf.globalattsget()
        info = cdf.cdf_info()
        delta = get_delta_from_interval(interval)
        # attributes
        metadata = {
            "agency_name": globalatts["Institution"],
            "cdf_globalatts": globalatts,
            "cdf_leapseconds_updated": info["LeapSecondUpdated"],
            "conditions_of_use": globalatts["TermsOfUse"],
            "data_interval": interval,
            "data_type": PUBLICATION_LEVEL_DATA_TYPE[globalatts["PublicationLevel"]],
            "elevation": globalatts["Elevation"],
            "geodetic_latitude": globalatts["Latitude"][0],
            "geodetic_longitude": globalatts["Longitude"][0],
            "sensor_orientation": globalatts["ElementsRecorded"],
            "station": globalatts["IagaCode"],
            "station_name": globalatts["ObservatoryName"],
        }
        # read elements
        epoch = cdflib.cdfepoch()
        stream = Stream()
        variables = info["zVariables"]
        for var in variables:
            print(f"parse variable {var}", file=sys.stderr)
            var_atts = cdf.varattsget(var)
            if "DEPEND_0" not in var_atts:
                # no times, no timeseries
                continue
            channel = var_atts["LABLAXIS"]
            if channels and channel not in channels:
                continue
            time_var = var_atts["DEPEND_0"]
            if not time_var in variables:
                print(f"Missing var {time_var} when parsing {var}", file=sys.stderr)
                continue
            var_times = cdf.varget(var_atts["DEPEND_0"])
            var_data = cdf.varget(var)
            print("getting times")
            for (start, end) in _get_time_ranges(var_times, delta):
                print(f"processing times {start}, {end}")
                starttime = epoch.to_datetime(var_times[start])[0]
                trace = Trace()
                trace.stats.update(metadata)
                trace.stats.channel = channel
                trace.stats.delta = delta
                trace.stats.starttime = UTCDateTime(starttime)
                trace.data = numpy.array(var_data[start:end])
                if var_atts["UNITS"] == "Degrees of arc":
                    # convert degrees to radians
                    trace.data = numpy.radians(trace.data)
                stream += trace
        return stream

    def write_path(
        self, path: str, timeseries: Stream, channels: List[str], force=True
    ):
        trace = timeseries[0]
        delta = trace.stats.delta
        # write global attrs
        globalattrs = dict(
            "cdf_globalatts" in trace.stats and trace.stats.cdf_globalatts or {}
        )
        globalattrs.update(
            {
                # 4.1 fixed attrs
                "FormatDescription": "INTERMAGNET CDF Format",
                "FormatVersion": "1.2",
                "Title": "Geomagnetic time series data",
                # 4.2 data
                "IagaCode": trace.stats.station,
                "ElementsRecorded": trace.stats.sensor_orientation or None,
                "PublicationLevel": DATA_TYPE_PUBLICATION_LEVEL[trace.stats.data_type],
                "PublicationDate": _get_tt2000([UTCDateTime()]),
                # 4.3 observatory
                "ObservatoryName": trace.stats.station_name or None,
                "Latitude": trace.stats.geodetic_latitude,
                "Longitude": trace.stats.geodetic_longitude,
                "Elevation": trace.stats.elevation,
                "Institution": trace.stats.agency_name,
                "VectorSensOrient": trace.stats.sensor_orientation,
                # 4.4 standards and quality
                # "StandardLevel": "",
                # "StandardName": None,
                # "StandardVersion": None,
                # "PartialStandDesc": None,
                # 4.5 publication
                "Source": "agency" in trace.stats and trace.stats.agency or "USGS",
                "TermsOfUse": trace.stats.conditions_of_use,
                # "UniqueIdentifier": None,
                # "ParentIdentifiers": [],
                # "ReferenceLinks": [],
                # Extensions
                "Comments": "comments" in trace.stats and trace.stats.comments or None,
                "DataType": trace.stats.data_type,
                "Interval": trace.stats.data_interval,
            }
        )
        cdf = cdflib.cdfwrite.CDF(
            path=path, cdf_spec={"checksum": True, "compressed": True}, delete=force
        )
        cdf.write_globalattrs(
            {
                k: {0: globalattrs[k]}
                for k in globalattrs.keys()
                if globalattrs[k] is not None
            }
        )
        # write times
        starttime = trace.stats.starttime
        cdf.write_var(
            var_spec={
                "Variable": f"DataTimes",
                "Data_Type": cdf.CDF_TIME_TT2000,
                "Dim_Sizes": [],
                "Num_Elements": 1,
                "Rec_Vary": True,
            },
            var_attrs={},
            var_data=_get_tt2000(
                [starttime + i * delta for i in range(len(trace.data))]
            ),
        )
        # write channels
        for channel in channels:
            trace = timeseries.select(channel=channel)[0]
            data = trace.data
            name = f"Geomagnetic Field Element {channel}"
            units = "nT"
            if channel == "D":
                data = numpy.degrees(data)
                units = "Degrees of arc"
            elif channel.startswith("T"):
                name = f"Temperature {channel[1:]}"
                units = "Celsius"
            cdf.write_var(
                var_spec={
                    "Variable": f"GeomagneticField{channel}",
                    "Data_Type": cdf.CDF_DOUBLE,
                    "Dim_Sizes": [],
                    "Num_Elements": 1,
                    "Rec_Vary": True,
                },
                var_attrs={
                    "DEPEND_0": "DataTimes",
                    "FIELDNAM": name,
                    "UNITS": units,
                    "FILLVAL": numpy.nan,
                    "VALIDMIN": -99999.99,
                    "VALIDMAX": 99999.99,
                    "DISPLAY_TYPE": "time_series",
                    "LABLAXIS": channel,
                },
                var_data=data,
            )


def _get_time_ranges(
    times: numpy.array, expected_delta: float
) -> List[Tuple[int, int]]:
    """Find uniformly spaced time ranges.

    The array of times is not required to be uniform, and may skip over gaps.
    This method checks for gaps, and determines continuous ranges.

    Parameters
    ----------
    times: array of CDF_TIME_* values.
    expected_delta: expected time between samples.

    Returns
    -------
    list of ranges that can be used to select uniform times.
    each range is (first index, last index + 1)
    """
    ranges: List[Tuple[int, int]] = []
    epoch = cdflib.cdfepoch()
    # quick check to verify uniform times
    npts = len(times)
    starttime, endtime = epoch.to_datetime([times[0], times[npts - 1]])
    delta = (endtime - starttime).total_seconds() / (npts - 1)
    if delta == expected_delta:
        # uniform times, one range
        ranges.append((0, npts))
    else:
        # slower scan list to find gaps
        print(times)
        times = epoch.to_datetime(times)
        print(expected_delta, times, (times[1] - times[0]).total_seconds())
        start_index = None
        for i in range(npts - 1):
            if start_index is None:
                start_index = i
            if (times[i + 1] - times[i]).total_seconds() != expected_delta:
                ranges.append((start_index, i + 1))
                start_index = None
        # close range at end
        if start_index is not None:
            ranges.append((start_index, npts))
    return ranges


def _get_tt2000(times: List[UTCDateTime]) -> List[int]:
    """Convert a list of UTCDateTime objects to CDF TT2000 times.
    """
    return cdflib.cdfepoch().compute_tt2000(
        [
            (d.year, d.month, d.day, d.hour, d.minute, d.second, d.microsecond / 1000)
            for d in [t.datetime for t in times]
        ]
    )
