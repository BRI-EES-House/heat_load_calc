from enum import Enum, IntEnum, auto


class ACMode(IntEnum):

    COOLING = -1
    STOP = 0
    HEATING = 1


class OperationMode(Enum):

    # 冷房
    COOLING = auto()

    # 暖房
    HEATING = auto()

    # 暖房・冷房停止で窓「開」
    STOP_OPEN = auto()

    # 暖房・冷房停止で窓「閉」
    STOP_CLOSE = auto()
