import os
from typing import Optional

from ..algorithm import Algorithm, FilterAlgorithm
from ..edge import EdgeFactory, MiniSeedFactory
from ..Controller import Controller, get_realtime_interval
from ..TimeseriesFactory import TimeseriesFactory
from .factory import get_edge_factory, get_miniseed_factory


def obsrio_minute(
    observatory: str,
    input_factory: Optional[TimeseriesFactory] = None,
    output_factory: Optional[TimeseriesFactory] = None,
    realtime_interval: int = 600,
):
    """Filter 1Hz legacy H,E,Z,F to 1 minute legacy.

    Should be called after obsrio_second() and obsrio_tenhertz(),
    which populate 1Hz legacy H,E,Z,F.
    """
    starttime, endtime = get_realtime_interval(realtime_interval)
    controller = Controller(
        algorithm=FilterAlgorithm(input_sample_period=1, output_sample_period=60),
        inputFactory=input_factory or get_edge_factory(data_type="variation"),
        inputInterval="second",
        outputFactory=output_factory or get_edge_factory(data_type="variation"),
        outputInterval="minute",
    )
    for channel in ["H", "E", "Z", "F"]:
        controller.run_as_update(
            observatory=(observatory,),
            output_observatory=(observatory,),
            starttime=starttime,
            endtime=endtime,
            input_channels=(channel,),
            output_channels=(channel,),
            realtime=realtime_interval,
            update_limit=10,
        )


def obsrio_second(
    observatory: str,
    input_factory: Optional[TimeseriesFactory] = None,
    output_factory: Optional[TimeseriesFactory] = None,
    realtime_interval: int = 600,
):
    """Copy 1Hz miniseed F to 1Hz legacy F.
    """
    starttime, endtime = get_realtime_interval(realtime_interval)
    controller = Controller(
        algorithm=Algorithm(),
        inputFactory=input_factory or get_miniseed_factory(data_type="variation"),
        inputInterval="second",
        outputFactory=output_factory or get_edge_factory(data_type="variation"),
        outputInterval="second",
    )
    controller.run_as_update(
        observatory=(observatory,),
        output_observatory=(observatory,),
        starttime=starttime,
        endtime=endtime,
        input_channels=("F",),
        output_channels=("F",),
        realtime=realtime_interval,
        update_limit=10,
    )


def obsrio_temperatures(
    observatory: str,
    input_factory: Optional[TimeseriesFactory] = None,
    output_factory: Optional[TimeseriesFactory] = None,
    realtime_interval: int = 600,
):
    """Filter temperatures 1Hz miniseed (LK1-4) to 1 minute legacy (UK1-4).
    """
    starttime, endtime = get_realtime_interval(realtime_interval)
    controller = Controller(
        algorithm=FilterAlgorithm(input_sample_period=1, output_sample_period=60),
        inputFactory=input_factory or get_miniseed_factory(data_type="variation"),
        inputInterval="second",
        outputFactory=output_factory or get_edge_factory(data_type="variation"),
        outputInterval="minute",
    )
    renames = {"LK1": "UK1", "LK2": "UK2", "LK3": "UK3", "LK4": "UK4"}
    for input_channel in renames.keys():
        output_channel = renames[input_channel]
        controller.run_as_update(
            observatory=(observatory,),
            output_observatory=(observatory,),
            starttime=starttime,
            endtime=endtime,
            input_channels=(input_channel,),
            output_channels=(output_channel,),
            realtime=realtime_interval,
            rename_output_channel=((input_channel, output_channel),),
            update_limit=10,
        )


def obsrio_tenhertz(
    observatory: str,
    input_factory: Optional[TimeseriesFactory] = None,
    output_factory: Optional[TimeseriesFactory] = None,
    realtime_interval: int = 600,
):
    """Filter 10Hz miniseed U,V,W to 1Hz legacy H,E,Z.
    """
    starttime, endtime = get_realtime_interval(realtime_interval)
    # filter 10Hz U,V,W to H,E,Z
    controller = Controller(
        algorithm=FilterAlgorithm(input_sample_period=0.1, output_sample_period=1),
        inputFactory=input_factory or get_miniseed_factory(data_type="variation"),
        inputInterval="tenhertz",
        outputFactory=output_factory or get_edge_factory(data_type="variation"),
        outputInterval="second",
    )
    renames = {"U": "H", "V": "E", "W": "Z"}
    for input_channel in renames.keys():
        output_channel = renames[input_channel]
        controller.run_as_update(
            observatory=(observatory,),
            output_observatory=(observatory,),
            starttime=starttime,
            endtime=endtime,
            input_channels=(input_channel,),
            output_channels=(output_channel,),
            realtime=realtime_interval,
            rename_output_channel=((input_channel, output_channel),),
            update_limit=10,
        )
