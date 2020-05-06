"""Controller class for geomag algorithms"""
import sys
from typing import Dict, List

from obspy.core import Stream, UTCDateTime

from geomagio import TimeseriesFactory, TimeseriesUtility, Util
from geomagio.algorithm import Algorithm, AlgorithmException


def _get_input_timeseries(
    algorithm: Algorithm,
    input_channels: List[str],
    input_factory: TimeseriesFactory,
    input_interval: str,
    input_type: str,
    observatories: List[str],
    starttime: UTCDateTime,
    endtime: UTCDateTime,
) -> Stream:
    timeseries = Stream()
    for observatory in observatories:
        input_start, input_end = algorithm.get_input_interval(
            start=starttime,
            end=endtime,
            observatory=observatory,
            channels=input_channels,
        )
        if input_start is not None and input_end is not None:
            timeseries += input_factory.get_timeseries(
                observatory=observatory,
                channels=input_channels,
                interval=input_interval,
                type=input_type,
                starttime=input_start,
                endtime=input_end,
            )
    return timeseries


def _rename_channels(timeseries: Stream, renames: Dict[str, str]) -> Stream:
    for key in renames:
        from_name, to_name = key, renames[key]
        for t in timeseries.select(channel=from_name):
            t.stats.channel = to_name
    return timeseries


def _get_output_timeseries(
    observatories: List[str],
    output_channels: List[str],
    output_factory: TimeseriesFactory,
    output_interval: str,
    output_type: str,
    starttime,
    endtime,
) -> Stream:
    timeseries = Stream()
    for observatory in observatories:
        timeseries += output_factory.get_timeseries(
            observatory=observatory,
            channels=output_channels,
            interval=output_interval,
            type=output_type,
            starttime=starttime,
            endtime=endtime,
        )
    return timeseries


def run(
    algorithm: Algorithm,
    input_factory: TimeseriesFactory,
    observatories: List[str],
    output_factory: TimeseriesFactory,
    starttime: UTCDateTime,
    endtime: UTCDateTime,
    input_channels: List[str] = None,
    input_interval: str = "second",
    input_timeseries: Stream = None,
    input_type: str = "variation",
    output_channels: List[str] = None,
    realtime_interval: int = None,
    rename_input_channels: Dict[str, str] = None,
    rename_output_channels: Dict[str, str] = None,
    trim=True,
):
    input_channels = input_channels or algorithm.get_input_channels()
    output_channels = output_channels or algorithm.get_output_channels()
    next_starttime = algorithm.get_next_starttime()
    starttime = next_starttime or starttime
    # input
    timeseries = input_timeseries or _get_input_timeseries(
        algorithm=algorithm,
        input_factory=input_factory,
        input_channels=input_channels,
        input_interval=input_interval,
        input_type=input_type,
        observatories=observatories,
        starttime=starttime,
        endtime=endtime,
    )
    if timeseries.count() == 0:
        # no data to process
        return
    # pre-process
    if next_starttime and realtime_interval:
        # when running a stateful algorithms with the realtime option
        # pad/trim timeseries to the interval:
        # [next_starttime, max(timeseries.endtime, now-options.realtime)]
        input_start, input_end = TimeseriesUtility.get_stream_start_end_times(
            timeseries=timeseries, without_gaps=True
        )
        realtime_gap = endtime - realtime_interval
        if input_end < realtime_gap:
            input_end = realtime_gap
        # pad to the start of the "realtime gap"
        TimeseriesUtility.pad_timeseries(
            timeseries=timeseries, starttime=next_starttime, endtime=input_end
        )
    # process
    if rename_input_channels:
        timeseries = _rename_channels(
            timeseries=timeseries, renames=rename_input_channels
        )
    processed = algorithm.process(timeseries)
    # trim if --no-trim is not set
    if trim:
        processed.trim(starttime=starttime, endtime=endtime)
    if rename_output_channels:
        processed = _rename_channels(
            timeseries=processed, renames=rename_output_channels
        )
    # output
    output_factory.put_timeseries(
        timeseries=processed,
        starttime=starttime,
        endtime=endtime,
        channels=output_channels,
    )


def run_as_update(
    algorithm: Algorithm,
    input_factory: TimeseriesFactory,
    observatories: List[str],
    output_factory: TimeseriesFactory,
    starttime: UTCDateTime,
    endtime: UTCDateTime,
    input_channels: List[str] = None,
    input_interval: str = "second",
    input_type: str = "variation",
    output_channels: List[str] = None,
    output_interval: str = "second",
    output_observatories: List[str] = None,
    output_type: str = "variation",
    realtime_interval: int = None,
    rename_input_channels: Dict[str, str] = None,
    rename_output_channels: Dict[str, str] = None,
    update_limit: int = 0,
    update_count: int = 0,
):
    """Updates data.
    Parameters
    ----------
    options: dictionary
        The dictionary of all the command line arguments. Could in theory
        contain other options passed in by the controller.

    Notes
    -----
    Finds gaps in the target data, and if there's new data in the input
        source, calls run with the start/end time of a given gap to fill
        in.
    It checks the start of the target data, and if it's missing, and
        there's new data available, it backs up the starttime/endtime,
        and recursively calls itself, to check the previous period, to see
        if new data is available there as well. Calls run for each new
        period, oldest to newest.
    """
    # If an update_limit is set, make certain we don't step past it.
    if update_limit > 0 and update_count >= update_limit:
        return
    if algorithm.get_next_starttime() is not None:
        raise AlgorithmException("Stateful algorithms cannot use run_as_update")
    input_channels = input_channels or algorithm.get_input_channels()
    output_channels = output_channels or algorithm.get_output_channels()
    output_observatories = output_observatories or observatories
    print(
        "checking gaps",
        starttime,
        endtime,
        output_observatories,
        output_channels,
        file=sys.stderr,
    )
    # request output to see what has already been generated
    output_timeseries = _get_output_timeseries(
        observatories=output_observatories,
        output_channels=output_channels,
        output_factory=output_factory,
        output_interval=output_interval,
        output_type=output_type,
        starttime=starttime,
        endtime=endtime,
    )
    if len(output_timeseries) > 0:
        # find gaps in output, so they can be updated
        output_gaps = TimeseriesUtility.get_merged_gaps(
            TimeseriesUtility.get_stream_gaps(output_timeseries)
        )
    else:
        output_gaps = [
            [
                starttime,
                endtime,
                # next sample time not used
                None,
            ]
        ]
    for output_gap in output_gaps:
        gap_starttime, gap_endtime = output_gap[0], output_gap[1]
        input_timeseries = _get_input_timeseries(
            algorithm=algorithm,
            input_channels=input_channels,
            input_factory=input_factory,
            input_interval=input_interval,
            input_type=input_type,
            observatories=observatories,
            starttime=gap_starttime,
            endtime=gap_endtime,
        )
        if not algorithm.can_produce_data(
            starttime=gap_starttime, endtime=gap_endtime, stream=input_timeseries
        ):
            continue
        # check for fillable gap at start
        if gap_starttime == starttime:
            # found fillable gap at start, recurse to previous interval
            interval = endtime - starttime
            update_starttime = starttime - interval
            update_endtime = starttime - 1
            run_as_update(
                algorithm=algorithm,
                input_channels=input_channels,
                input_factory=input_factory,
                input_interval=input_interval,
                input_type=input_type,
                observatories=observatories,
                output_channels=output_channels,
                output_factory=output_factory,
                output_interval=output_interval,
                output_type=output_type,
                realtime_interval=realtime_interval,
                rename_input_channels=rename_input_channels,
                rename_output_channels=rename_output_channels,
                # update arguments
                output_observatories=output_observatories,
                starttime=update_starttime,
                endtime=update_endtime,
                update_count=update_count + 1,
                update_limit=update_limit,
            )
        # fill gap
        print(
            "processing",
            gap_starttime,
            gap_endtime,
            output_observatories,
            output_channels,
            file=sys.stderr,
        )
        run(
            algorithm=algorithm,
            input_channels=input_channels,
            input_factory=input_factory,
            input_interval=input_interval,
            input_type=input_type,
            observatories=observatories,
            output_channels=output_channels,
            output_factory=output_factory,
            realtime_interval=realtime_interval,
            rename_input_channels=rename_input_channels,
            rename_output_channels=rename_output_channels,
            # gap specific arguments
            starttime=gap_starttime,
            endtime=gap_endtime,
            input_timeseries=input_timeseries,
        )
