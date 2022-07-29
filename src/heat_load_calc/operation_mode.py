from enum import IntEnum, Enum
import numpy as np


class OperationMode(Enum):

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

    @property
    def is_window_open(self):
        return self == OperationMode.STOP_OPEN

    def is_convective_ac(self, is_radiative_heating_installed: bool, is_radiative_cooling_installed: bool):

        # 対流暖房を行っているかどうか
        does_convective_heat = (self == OperationMode.HEATING) and (not is_radiative_heating_installed)

        # 対流冷房を行っているかどうか
        does_convective_cool = (self == OperationMode.COOLING) and (not is_radiative_cooling_installed)

        return does_convective_heat or does_convective_cool

    @staticmethod
    def u_is_window_open(oms: np.ndarray):
        return np.vectorize(lambda om: om.is_window_open)(oms)

    @staticmethod
    def u_is_convective_ac(oms: np.ndarray, is_radiative_heating_is, is_radiative_cooling_is):
        return np.vectorize(
            lambda om, is_radiative_heating, is_radiative_cooling: om.is_convective_ac(is_radiative_heating, is_radiative_cooling)
        )(oms, is_radiative_heating_is, is_radiative_cooling_is)

