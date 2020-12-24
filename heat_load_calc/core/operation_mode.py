from enum import IntEnum


class OperationMode(IntEnum):

    # 冷房
    COOLING = 1

    # 暖房
    HEATING = 2

    # 暖房・冷房停止で窓「開」
    STOP_OPEN = 3

    # 暖房・冷房停止で窓「閉」
    STOP_CLOSE = 4

    # 暖房かつ冷房
    HEATING_AND_COOLING = 5
