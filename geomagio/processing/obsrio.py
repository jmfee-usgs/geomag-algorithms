import os
import sys
import threading
from typing import List

from ..algorithm import Algorithm, FilterAlgorithm
from ..edge import EdgeFactory, MiniSeedFactory
from ..TimeseriesFactory import TimeseriesFactory
from .run import run_as_update, run_concurrent


"""

HEZF
    hezf to xy 1Hz legacy
    hezf to xy 1 minute legacy
        hezf to sqdist 1 minute legacy
        -> SQDist
    -> D
    -> G
    -> XYZF adjusted
        -> H,D adjusted
        -> G adjusted



HEZF -> XY
HEZF -> D
HEZF -> G

HEZF -> XYZF adjusted

XYZF adjusted ->
"""


def copy(
    observatory: str,
    channel: str,
    input_factory: TimeseriesFactory,
    output_factory: TimeseriesFactory,
    **kwargs,
):
    # miniseed 1Hz to legacy 1Hz
    print(f"Copy {channel}", file=sys.stderr)
    run_as_update(
        observatories=[observatory],
        # read 1Hz variation
        input_channels=[channel],
        input_factory=input_factory,
        # identity algorithm
        algorithm=Algorithm(),
        # write 1Hz variation
        output_channels=[channel],
        output_factory=output_factory,
        # realtime and update
        update_limit=10,
        **kwargs,
    )


def filter_10hz_to_1hz(
    observatory: str,
    channel: str,
    input_factory: TimeseriesFactory,
    output_factory: TimeseriesFactory,
    **kwargs,
):
    print(f"Filter {channel} 10Hz to 1Hz", file=sys.stderr)
    run_as_update(
        observatories=[observatory],
        # read 1Hz variation
        input_channels=[channel],
        input_factory=input_factory,
        # identity algorithm
        algorithm=FilterAlgorithm(input_sample_period=0.1, output_sample_period=1),
        # write 1Hz variation
        output_channels=[channel],
        output_factory=output_factory,
        # realtime and update
        realtime_interval=600,
        update_limit=10,
        **kwargs,
    )


def filter_1hz_to_1minute(
    observatory: str,
    channel: str,
    input_factory: TimeseriesFactory,
    output_factory: TimeseriesFactory,
    **kwargs,
):
    print(f"Filter {channel} 1Hz to 1 minute", file=sys.stderr)
    run_as_update(
        observatories=[observatory],
        # read 1Hz variation
        input_channels=[channel],
        input_factory=input_factory,
        # identity algorithm
        algorithm=FilterAlgorithm(input_sample_period=1, output_sample_period=60),
        # write 1Hz variation
        output_channels=[channel],
        output_factory=output_factory,
        # realtime and update
        realtime_interval=600,
        update_limit=10,
        **kwargs,
    )


def obsrio_raw(host: str, observatory: str, channel: str):
    """Process one obsrio raw channel.

    - Populate legacy 1hz
        For U/V/W: filter miniseed 10hz to legacy 1hz
        For other channels: copy miniseed 1hz to legacy 1hz.
    - Filter legacy 1hz to legacy 1 minute
    """
    renames = {"U": "H", "V": "E", "W": "Z"}
    # create 1Hz
    if channel in renames:
        filter_10hz_to_1hz(
            observatory=observatory,
            channel=channel,
            input_factory=MiniSeedFactory(
                host=host,
                interval="tenhertz",
                type="variation",
                convert_channels=["U", "V", "W"],
            ),
            output_factory=EdgeFactory(host=host, interval="second", type="variation"),
            output_channels=[renames[channel]],
            rename_output_channels={channel: renames[channel]},
        )
        channel = renames[channel]
    else:
        copy(
            observatory=observatory,
            channel=channel,
            input_factory=MiniSeedFactory(
                host=host, interval="second", type="variation"
            ),
            output_factory=EdgeFactory(host=host, interval="second", type="variation"),
        )
    # filter 1 minute
    filter_1hz_to_1minute(
        observatory=observatory,
        channel=channel,
        input_factory=EdgeFactory(host=host, interval="second", type="variation"),
        output_factory=EdgeFactory(host=host, interval="minute", type="variation"),
    )


def obsrio_temperature(host: str, observatory: str, channel: str):
    """Process one obsrio temperature channel.

    - Filter miniseed 1hz to legacy 1 minute
    """
    renames = {"LK1": "UK1", "LK2": "UK2", "LK3": "UK3", "LK4": "UK4"}
    if not channel in renames:
        raise ValueError(f"Expected one of {renames.keys()}")
    filter_1hz_to_1minute(
        observatory=observatory,
        channel=channel,
        input_factory=MiniSeedFactory(host=host, interval="second", type="variation"),
        output_factory=EdgeFactory(host=host, interval="minute", type="variation"),
        output_channels=[renames[channel]],
        rename_output_channels={channel: renames[channel]},
    )


def process(host: str, observatory: str):
    """Process ObsRIO outputs

    raw
    U 10Hz -> H 1Hz -> H 1 minute
    V 10Hz -> E 1Hz -> E 1 minute
    W 10Hz -> Z 1Hz -> Z 1 minute
    F 1Hz -> F 1Hz -> F 1 minute

    temperatures
    LK1 1Hz -> UK1 1 minute
    LK2 1Hz -> UK2 1 minute
    LK3 1Hz -> UK3 1 minute
    LK4 1Hz -> UK4 1 minute
    """
    run_concurrent(
        [
            lambda: obsrio_raw(host, observatory, "U"),
            lambda: obsrio_raw(host, observatory, "V"),
            lambda: obsrio_raw(host, observatory, "W"),
            lambda: obsrio_raw(host, observatory, "F"),
            lambda: obsrio_temperature(host, observatory, "LK1"),
            lambda: obsrio_temperature(host, observatory, "LK2"),
            lambda: obsrio_temperature(host, observatory, "LK3"),
            lambda: obsrio_temperature(host, observatory, "LK4"),
        ]
    )
