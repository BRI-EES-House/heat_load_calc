from enum import Enum


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
