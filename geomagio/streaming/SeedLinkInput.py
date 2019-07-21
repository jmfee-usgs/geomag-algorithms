from obspy.core import Stream
from obspy.clients.seedlink import EasySeedLinkClient

from geomagio.miniseed import decode_stream


class SeedLinkInput(EasySeedLinkClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listeners = []

    def on_data(self, data):
        """Call all listeners with provided data.

        Parameters
        ----------
        data: obspy.core.Stream|obspy.core.Trace
            data produced during processing
        """
        stream = Stream()
        stream += data
        stream = decode_stream(stream)
        for listener in self.listeners:
            listener.on_data(stream)
