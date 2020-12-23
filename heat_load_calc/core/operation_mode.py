from enum import Enum, auto


class OperationMode(Enum):

    # 冷房
    COOLING = auto()

    # 暖房
    HEATING = auto()

    # 暖房かつ冷房
    HEATING_AND_COOLING = auto()

    # 暖房・冷房停止で窓「開」
    STOP_OPEN = auto()

    # 暖房・冷房停止で窓「閉」
    STOP_CLOSE = auto()
