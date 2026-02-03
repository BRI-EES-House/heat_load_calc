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


class ENumberOfOccupants(Enum):
    """specified method of number of occupants / 居住人数の指定方法
    Specify the number of the occupants from one to four, or "auto".
    "auto" is the way that the number of the occupants is decided based on the total floor area.
    1~4人を指定するか、auto の場合は床面積から居住人数を指定する方法を選択する。

    """

    One = "1"
    Two = "2"
    Three = "3"
    Four = "4"
    Auto = "auto"


class EScheduleType(Enum):
    """Schedule type
    number = specify each schedule for one, two theree and four occupant(s)
    const = specify constant schedule not depending the number of occupants
    """

    NUMBER = "number"
    CONST = "const"
