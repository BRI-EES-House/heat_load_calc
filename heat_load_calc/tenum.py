from enum import Enum, IntEnum


class EInterval(Enum):
    """Interval for calculation.
    
    Notes:
        Interval is selected by;
            1 hour
            30 minutes
            15 minutes.
    """

    H1 = '1h'
    M30 = '30m'
    M15 = '15m'


class EWeatherMethod(Enum):
    """Weather input method"""

    EES = 'ees'
    FILE = 'file'


class ERegion(IntEnum):

    Region1 = '1'
    Region2 = '2'
    Region3 = '3'
    Region4 = '4'
    Region5 = '5'
    Region6 = '6'
    Region7 = '7'
    Region8 = '8'