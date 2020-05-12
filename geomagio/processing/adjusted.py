import sys

from ..algorithm import AdjustedAlgorithm
from ..edge import EdgeFactory
from ..TimeseriesFactory import TimeseriesFactory
from .run import run_as_update, run_concurrent
from .observatory import legacy_deltaf, legacy_sqdist_minute, legacy_xyz


def algorithm_adjusted(
    observatory: str,
    input_factory: TimeseriesFactory,
    output_factory: TimeseriesFactory,
    statefile: str,
    realtime_interval: int = 600,
    **kwargs,
):
    print(f"Adjusted {observatory}", file=sys.stderr)
    run_as_update(
        observatories=[observatory],
        input_channels=["H", "E", "Z", "F"],
        input_factory=input_factory,
        algorithm=AdjustedAlgorithm(statefile=statefile),
        output_channels=["X", "Y", "Z", "F"],
        output_factory=output_factory,
        realtime_interval=realtime_interval,
        **kwargs,
    )


def legacy_adjusted(
    host: str,
    observatory: str,
    interval: str,
    statefile: str,
    realtime_interval: int = 600,
    **kwargs,
):
    algorithm_adjusted(
        observatory=observatory,
        input_factory=EdgeFactory(host=host, interval=interval, type="variation"),
        output_factory=EdgeFactory(host=host, interval=interval, type="adjusted"),
        statefile=statefile,
        realtime_interval=realtime_interval,
        **kwargs,
    )


def adjusted_1hz(host: str, observatory: str, adjusted_statefile: str):
    legacy_adjusted(
        host=host,
        observatory=observatory,
        interval="second",
        statefile=adjusted_statefile,
    )
    run_concurrent(
        [
            lambda: legacy_deltaf(
                host=host,
                observatory=observatory,
                interval="second",
                data_type="adjusted",
                informat="geo",
            ),
            lambda: legacy_xyz(
                host=host,
                observatory=observatory,
                interval="second",
                data_type="adjusted",
                informat="geo",
                outformat="mag",
                output_channels=["H", "D"],
            ),
        ]
    )


def adjusted_1minute(
    host: str, observatory: str, adjusted_statefile: str, sqdist_statefile: str
):
    legacy_adjusted(
        host=host,
        observatory=observatory,
        interval="minute",
        statefile=adjusted_statefile,
    )
    run_concurrent(
        [
            lambda: legacy_deltaf(
                host=host,
                observatory=observatory,
                interval="minute",
                data_type="adjusted",
                informat="geo",
            ),
            lambda: legacy_xyz(
                host=host,
                observatory=observatory,
                interval="minute",
                data_type="adjusted",
                informat="geo",
                outformat="mag",
                output_channels=["H", "D"],
            ),
            # also sqdist for 1 minute
            lambda: legacy_sqdist_minute(
                host=host,
                observatory=observatory,
                data_type="adjusted",
                statefile=sqdist_statefile,
            ),
        ]
    )
