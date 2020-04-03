import datetime
import enum
from typing import Any, Dict, List, Optional, Union

from obspy import UTCDateTime
from pydantic import BaseModel, root_validator, validator

from .Element import ELEMENTS, ELEMENT_INDEX

DEFAULT_ELEMENTS = ["X", "Y", "Z", "F"]
REQUEST_LIMIT = 345600
VALID_ELEMENTS = [e.id for e in ELEMENTS]

VALID_OBSERVATORIES = [
    "BDT",
    "BOU",
    "BRT",
    "BRW",
    "BSL",
    "CMO",
    "CMT",
    "DED",
    "DHT",
    "FDT",
    "FRD",
    "FRN",
    "GUA",
    "HON",
    "NEW",
    "SHU",
    "SIT",
    "SJG",
    "SJT",
    "TST",
    "TUC",
    "USGS",
]


class DataType(str, enum.Enum):
    VARIATION = "variation"
    ADJUSTED = "adjusted"
    QUASI_DEFINITIVE = "quasi-definitive"
    DEFINITIVE = "definitive"


class OutputFormat(str, enum.Enum):
    IAGA2002 = "iaga2002"
    JSON = "json"


class SamplingPeriod(float, enum.Enum):
    TEN_HERTZ = 0.1
    SECOND = 1.0
    MINUTE = 60.0
    HOUR = 3600.0
    DAY = 86400.0


class DataApiQuery(BaseModel):
    id: str
    starttime: datetime.datetime = None
    endtime: datetime.datetime = None
    elements: List[str] = DEFAULT_ELEMENTS
    sampling_period: SamplingPeriod = SamplingPeriod.MINUTE
    data_type: Union[DataType, str] = DataType.VARIATION
    format: OutputFormat = OutputFormat.IAGA2002

    @validator("data_type")
    def validate_data_type(
        cls, data_type: Union[DataType, str]
    ) -> Union[DataType, str]:
        if data_type not in DataType and len(data_type) != 2:
            raise ValueError(
                f"Bad data type value '{data_type}'."
                f" Valid values are: {', '.join(list(DataType))}"
            )
        return data_type

    @validator("elements", pre=True, always=True)
    def validate_elements(cls, elements: List[str]) -> List[str]:
        if not elements:
            return DEFAULT_ELEMENTS
        if len(elements) == 1 and "," in elements[0]:
            elements = [e.strip() for e in elements[0].split(",")]
        for element in elements:
            if element not in VALID_ELEMENTS and len(element) != 3:
                raise ValueError(
                    f"Bad element '{element}'."
                    f" Valid values are: {', '.join(VALID_ELEMENTS)}."
                )
        return elements

    @validator("id")
    def validate_id(cls, id: str) -> str:
        if id not in VALID_OBSERVATORIES:
            raise ValueError(
                f"Bad observatory id '{id}'."
                f" Valid values are: {', '.join(VALID_OBSERVATORIES)}."
            )
        return id

    @validator("starttime", pre=True, always=True)
    def validate_starttime(
        cls, starttime: Union[datetime.datetime, datetime.date]
    ) -> datetime.datetime:
        if not starttime:
            # default to start of current day
            now = datetime.datetime.now(tz=datetime.timezone.utc)
            return datetime.datetime(
                year=now.year,
                month=now.month,
                day=now.day,
                tzinfo=datetime.timezone.utc,
            )
        elif isinstance(starttime, datetime.date):
            return datetime.datetime(
                year=starttime.year,
                month=starttime.month,
                day=starttime.day,
                tzinfo=datetime.timezone.utc,
            )
        return starttime

    @validator("endtime", always=True, pre=True)
    def validate_endtime(
        cls, endtime: Union[datetime.datetime, datetime.date], *, values: Dict, **kwargs
    ) -> datetime.datetime:
        """Default endtime is based on starttime.

        This method needs to be after validate_starttime.
        """
        if not endtime:
            # endtime defaults to 1 day after startime
            starttime = values.get("starttime")
            endtime = starttime + datetime.timedelta(seconds=86400 - 0.001)
        elif isinstance(endtime, datetime.date):
            return datetime.datetime(
                year=endtime.year,
                month=endtime.month,
                day=endtime.day,
                tzinfo=datetime.timezone.utc,
            )
        return endtime

    @root_validator
    def validate_combinations(cls, values):
        starttime, endtime, elements, format, sampling_period = (
            values.get("starttime"),
            values.get("endtime"),
            values.get("elements"),
            values.get("format"),
            values.get("sampling_period"),
        )
        if len(elements) > 4 and format == "iaga2002":
            raise ValueError("No more than four elements allowed for iaga2002 format.")
        if starttime > endtime:
            raise ValueError("Starttime must be before endtime.")
        # check data volume
        samples = int(
            len(elements) * (endtime - starttime).total_seconds() / sampling_period
        )
        if samples > REQUEST_LIMIT:
            raise ValueError(f"Request exceeds limit ({samples} > {REQUEST_LIMIT})")
        # otherwise okay
        return values
