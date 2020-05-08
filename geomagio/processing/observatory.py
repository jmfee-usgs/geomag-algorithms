import os
import sys

import numpy

from ..TimeseriesFactory import TimeseriesFactory
from ..algorithm import (
    Algorithm,
    DeltaFAlgorithm,
    FilterAlgorithm,
    SqDistAlgorithm,
    XYZAlgorithm,
)
from ..edge import EdgeFactory, MiniSeedFactory
from .run import run, run_as_update, run_concurrent


def algorithm_deltaf(
    observatory: str,
    input_factory: TimeseriesFactory,
    output_factory: TimeseriesFactory,
    informat: str = "geo",
    realtime_interval: int = 600,
    **kwargs,
):
    print(f"DeltaF {observatory} from {informat}", file=sys.stderr)
    run_as_update(
        observatories=[observatory],
        # read
        input_factory=input_factory,
        # deltaf algorithm
        algorithm=DeltaFAlgorithm(informat=informat),
        # write
        output_factory=output_factory,
        # realtime and update
        realtime_interval=realtime_interval,
        update_limit=10,
        **kwargs,
    )


def algorithm_sqdist_minute(
    observatory: str,
    input_factory: TimeseriesFactory,
    output_factory: TimeseriesFactory,
    statefile: str,
    **kwargs,
):
    print(f"SQDist {observatory}", file=sys.stderr)
    run(
        observatories=[observatory],
        input_channels=["X", "Y", "Z", "F"],
        input_factory=input_factory,
        algorithm=SqDistAlgorithm(
            alpha=2.3148e-5,
            gamma=3.3333e-2,
            m=1440,
            mag=True,
            smooth=180,
            statefile=statefile,
        ),
        output_channels=["MDT", "MSQ", "MSV"],
        output_factorry=output_factory,
        realtime_interval=1800,
        rename_output_channels={"H_Dist": "MDT", "H_SQ": "MSQ", "H_SV": "MSV"},
        **kwargs,
    )


def algorithm_xyz(
    observatory: str,
    input_factory: TimeseriesFactory,
    output_factory: TimeseriesFactory,
    informat: str,
    outformat: str,
    realtime_interval: int = 600,
    **kwargs,
):
    print(f"XYZ {observatory} from {informat} to {outformat}", file=sys.stderr)
    run_as_update(
        observatories=[observatory],
        # read
        input_factory=input_factory,
        # deltaf algorithm
        algorithm=XYZAlgorithm(informat=informat, outformat=outformat),
        # write
        output_factory=output_factory,
        # realtime and update
        realtime_interval=realtime_interval,
        update_limit=10,
        **kwargs,
    )


def legacy_deltaf(
    host: str, observatory: str, interval: str, data_type: str, informat: str, **kwargs
):
    factory = EdgeFactory(host=host, interval=interval, type=data_type)
    algorithm_deltaf(
        observatory=observatory,
        input_factory=factory,
        output_factory=factory,
        informat=informat,
        realtime_interval=(interval == "second" and 600 or 3600),
        **kwargs,
    )


def legacy_sqdist_minute(
    host: str, observatory: str, data_type: str, statefile: str, **kwargs,
):
    factory = EdgeFactory(host=host, interval="minute", type=data_type)
    algorithm_sqdist_minute(
        observatory=observatory,
        input_factory=factory,
        output_factory=factory,
        statefile=statefile,
        **kwargs,
    )


def legacy_xyz(
    data_type: str,
    host: str,
    informat: str,
    interval: str,
    observatory: str,
    outformat: str,
    **kwargs,
):
    factory = EdgeFactory(host=host, interval=interval, type=data_type)
    algorithm_xyz(
        informat=informat,
        input_factory=factory,
        observatory=observatory,
        output_factory=factory,
        realtime_interval=(interval == "second" and 600 or 3600),
        **kwargs,
    )
