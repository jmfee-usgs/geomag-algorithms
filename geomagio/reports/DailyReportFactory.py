from ..edge import EdgeFactory
from obspy.core import UTCDateTime
import numpy as np
from .Flag import Flag


class DailyReportFactory(object):
    """
    Factory for creating Flag objects
    """

    def __init__(self, observatory: str, starttime: UTCDateTime, endtime: UTCDateTime):
        self.observatory = observatory
        self.starttime = starttime
        self.endtime = endtime

    def get_timeseries(self):
        m = EdgeFactory()
        stream = m.get_timeseries(
            observatory=self.observatory,
            starttime=self.starttime,
            endtime=self.endtime,
            interval="minute",
            type="variation",
            channels=["G", "SQ", "SV", "D", "UK1", "UK2", "UK3"],
        )
        return stream

    def process_stream(self, stream):
        spikes = np.array([])
        gaps = np.array([])
        offsets = np.array([])
        for trace in stream:
            np.append(spikes, self.check_spikes(trace))
            np.append(gaps, self.check_gaps(trace))
            np.append(offsets, self.check_offsets(trace))
        flags = np.array([spikes, gaps, offsets])

        return flags.flatten()

    def check_spikes(self, trace):
        data = trace.data
        starttime = str(trace.stats.starttime)
        flags = []
        for i in range(len(data)):
            if abs(data[i] - data[i - 1]) > 0.5:
                f = Flag()
                f.type = "Spike"
                minute = int(starttime[14:16]) + trace.times()[i]
                f.starttime = starttime[0:14] + str(minute) + starttime[16::]
                f.endtime = f.starttime
                f.observatory = self.observatory
                f.channel = trace.stats.channel
                f.comment = self.create_default_comment(f)
                flags.append(f)
        return flags

    def check_gaps(self, trace):
        data = trace.data
        starttime = str(trace.stats.starttime)
        flags = []
        for i in range(len(data)):
            if np.isnan(data[i]):
                f = Flag()
                f.type = "Gap"
                minute = int(starttime[14:16]) + trace.times()[i]
                f.starttime = starttime[0:14] + str(minute) + starttime[16::]
                f.endtime = f.starttime
                f.observatory = self.observatory
                f.channel = trace.stats.channel
                f.comment = self.create_default_comment(f)
                flags.append(f)
        return flags

    def check_offsets(self, trace):
        data = trace.data
        diff = np.gradient(data)
        starttime = str(trace.stats.starttime)
        flags = []
        for i in range(1, len(data), 2):
            if abs(diff[i] - diff[i - 1]) > 0.5:
                f = Flag()
                f.type = "Offset"
                minute = int(starttime[14:16]) + trace.times()[i]
                f.starttime = starttime[0:14] + str(minute) + starttime[16::]
                f.endtime = f.starttime
                f.observatory = self.observatory
                f.channel = trace.stats.channel
                f.comment = self.create_default_comment(f)
                flags.append(f)
        return flags

    def create_default_comment(self, flag):
        return str(flag.type) + "in" + str(flag.channel) + "at" + str(flag.starttime)

    @classmethod
    def add_arguments(cls, parser):
        """Add command line arguments to argparse parser.
        Parameters
        ----------
        parser: ArgumentParser
            command line argument parser
        """

        parser.add_argument(
            "--flags",
            default=None,
            help="For Daily Reports. Returns a set of flags for requested data",
        )

    def configure(self, arguments):
        """Configure algorithm using comand line arguments.
        Parameters
        ----------
        arguments: Namespace
            parsed command line arguments
        """
        Algorithm.configure(self, arguments)
        # intialize filter with command line arguments
        self.coeff_filename = arguments.filter_coefficients
        self.input_sample_period = TimeseriesUtility.get_delta_from_interval(
            arguments.input_interval or arguments.interval
        )
        self.output_sample_period = TimeseriesUtility.get_delta_from_interval(
            arguments.output_interval or arguments.interval
        )
        self.load_state()
