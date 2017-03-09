"""metadata.observatory module"""
from __future__ import absolute_import, print_function

import importlib
import pkgutil
import sys
from obspy import UTCDateTime


# module exports
__all__ = [
    'get_observatory'
]


# a dictionary of observatories, keyed by observatory ID
OBSERVATORIES = {}


# import all observatory metadata files
prefix = __name__ + '.'
__path__ = pkgutil.extend_path(__path__, __name__)
for importer, modname, ispkg in pkgutil.walk_packages(
        path=__path__,
        prefix=prefix):
    observatory = modname.replace(prefix, '')
    module = importlib.import_module(modname)
    if 'METADATA' not in dir(module):
        print(modname + ' missing METADATA attribute', file=sys.stderr)
    # add to OBSERVATORIES list
    OBSERVATORIES[observatory] = module.METADATA
    # export in __all__
    __all__.append(observatory)


def get_observatory(code, time=None, observatories=None):
    """Get observatory metadata

    Parameters
    ----------
    code : str
        case sensitive observatory code
    time : UTCDateTime
        Default: now
        time of metadata
    observatories : dict
        Default OBSERVATORIES
        a custom dictionary of observatory metadata to scan.

    Returns
    -------
    dict : dictionary of metadata, or
    None : when no matching metadata found
    """
    observatories = observatories or OBSERVATORIES
    if code not in observatories:
        return None
    time = time or UTCDateTime()
    for epoch in observatories[code]:
        starttime = epoch['starttime']
        if starttime is not None:
            starttime = UTCDateTime(starttime)
        endtime = epoch['endtime']
        if endtime is not None:
            endtime = UTCDateTime(endtime)
        if (starttime is None or starttime <= time) and \
                (endtime is None or endtime > time):
            return epoch
    return None
