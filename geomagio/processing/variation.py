from .run import run_concurrent
from .observatory import legacy_deltaf, legacy_sqdist_minute, legacy_xyz


def variation_1hz(host: str, observatory: str):
    run_concurrent(
        [
            lambda: legacy_deltaf(
                host=host,
                observatory=observatory,
                interval="second",
                data_type="variation",
                informat="obs",
            ),
            lambda: legacy_xyz(
                host=host,
                observatory=observatory,
                interval="second",
                data_type="variation",
                informat="obs",
                outformat="geo",
                output_channels=["X", "Y"],
            ),
            lambda: legacy_xyz(
                host=host,
                observatory=observatory,
                interval="second",
                data_type="variation",
                informat="obs",
                outformat="obsd",
                output_channels=["D"],
            ),
        ]
    )


def variation_1minute(host: str, observatory: str, sqdist_statefile: str):
    run_concurrent(
        [
            lambda: legacy_deltaf(
                host=host,
                observatory=observatory,
                interval="minute",
                data_type="variation",
                informat="obs",
            ),
            lambda: legacy_xyz(
                host=host,
                observatory=observatory,
                interval="minute",
                data_type="variation",
                informat="obs",
                outformat="geo",
                output_channels=["X", "Y"],
            ),
            lambda: legacy_xyz(
                host=host,
                observatory=observatory,
                interval="minute",
                data_type="variation",
                informat="obs",
                outformat="obsd",
                output_channels=["D"],
            ),
            # also sqdist for 1 minute
            lambda: legacy_sqdist_minute(
                host=host,
                observatory=observatory,
                data_type="variation",
                statefile=sqdist_statefile,
            ),
        ]
    )
