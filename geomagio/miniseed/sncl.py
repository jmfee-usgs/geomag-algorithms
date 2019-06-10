"""MiniSEED utilities
"""

SEED_CHANNEL_PREFIX = {
    'B': 'tenhertz',
    'L': 'second',
    'U': 'minute',
    'R': 'hour',
    'P': 'day'
}
SEED_CHANNEL_TYPE = {
    'E': 'Volt',
    'Y': 'Bin'
}
SEED_LOCATION_PREFIX = {
    'R': 'variation',
    'A': 'adjusted',
    'Q': 'quasi-definitive',
    'D': 'definitive'
}
SEED_LOCATION_SUFFIX = {
    'D': 'Dist',
    'Q': 'SQ',
    'V': 'SV'
}

ELEMENT_CHANNEL_TYPE = {v: k for k, v in SEED_CHANNEL_TYPE.items()}
ELEMENT_LOCATION_SUFFIX = {v: k for k, v in SEED_LOCATION_SUFFIX.items()}
INTERVAL_CHANNEL_PREFIX = {v: k for k, v in SEED_CHANNEL_PREFIX.items()}
TYPE_LOCATION_PREFIX = {v: k for k, v in SEED_LOCATION_PREFIX.items()}


def decode_sncl(network, station, channel, location):
    """Translate SNCL to algorithms metadata.

    Parameters
    ----------
    network: str
        network code.
    station: str
        station code.
    channel: str
        channel code.
    location: str
        location code.

    Returns
    -------
    dict with keys for Geomag metadata
        network: str
            Geomag network
        observatory: str
            Geomag observatory
        element: str
            Geomag element
        data_interval: {'tenhertz', 'second', 'minute', 'hour', 'day'}
            Geomag data interval
        data_type: {'variation', 'adjusted', 'quasi-definitive', 'definitive'}
            Geomag data type
    """
    return {
        'network': network,
        'observatory': station,
        'element': get_element(network, station, channel, location),
        'data_interval': get_data_interval(
                network, station, channel, location),
        'data_type': get_data_type(network, station, channel, location)
    }


def encode_sncl(network, observatory, element, data_interval, data_type):
    """Translate algorithms metadata to SNCL.

    Parameters
    ----------
    network: str
        Geomag network
    observatory: str
        Geomag observatory
    element: str
        Geomag element
    data_interval: {'tenhertz', 'second', 'minute', 'hour', 'day'}
        Geomag data interval
    data_type: {'variation', 'adjusted', 'quasi-definitive', 'definitive'}
        Geomag data type

    Returns
    -------
    dict with keys for SNCL
        network: str
            network code.
        station: str
            station code.
        channel: str
            channel code.
        location: str
            location code.
    """
    return {
        'network': network,
        'station': observatory,
        'channel': get_sncl_channel(
                network, observatory, element, data_interval, data_type),
        'location': get_sncl_location(
                network, observatory, element, data_interval, data_type)
    }


def get_data_interval(network, station, channel, location):
    return SEED_CHANNEL_PREFIX[channel[0]]


def get_data_type(network, station, channel, location):
    return SEED_LOCATION_PREFIX[location[0]]


def get_element(network, station, channel, location):
    element_prefix = channel[2]
    element_suffix = ''
    channel_type = channel[1]
    if channel_type in SEED_CHANNEL_TYPE:
        element_suffix += '_' + SEED_CHANNEL_TYPE[channel_type]
    location_suffix = location[1]
    if location_suffix in SEED_LOCATION_SUFFIX:
        element_suffix += '_' + SEED_LOCATION_SUFFIX[location_suffix]
    return element_prefix + element_suffix


def get_sncl_channel(network, observatory, element, data_interval, data_type):
    channel_prefix = INTERVAL_CHANNEL_PREFIX[data_interval]
    element_parts = element.split('_')
    channel_suffix = element_parts[0]
    channel_middle = 'F'
    if len(element_parts) > 1:
        rest = element_parts[1]
        if rest in ELEMENT_CHANNEL_TYPE:
            channel_middle = ELEMENT_CHANNEL_TYPE[rest]
    return channel_prefix + channel_middle + channel_suffix


def get_sncl_location(network, observatory, element, data_interval, data_type):
    location_prefix = TYPE_LOCATION_PREFIX[data_type]
    location_suffix = '0'
    element_parts = element.split('_')
    if len(element_parts) > 1:
        rest = element_parts[1]
        if rest in ELEMENT_LOCATION_SUFFIX:
            location_suffix = ELEMENT_LOCATION_SUFFIX[rest]
    return location_prefix + location_suffix
