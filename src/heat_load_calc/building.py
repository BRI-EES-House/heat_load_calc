from enum import Enum
from typing import Dict
import logging
import numpy as np
import math


logger = logging.getLogger('HeatLoadCalc').getChild('building')


class Story(Enum):
    """
    建物の階数（共同住宅の場合は住戸の階数）
    """
    # 1階
    ONE = 1
    # 2階（2階以上の階数の場合も2階とする。）
    TWO = 2


class InsidePressure(Enum):
    """
    室内圧力
    """
    # 正圧
    POSITIVE = 'positive'
    # 負圧
    NEGATIVE = 'negative'
    # ゼロバランス
    BALANCED = 'balanced'


class Structure(Enum):
    """構造を表す列挙型
    """

    RC = 'rc'
    SRC = 'src'
    WOODEN = 'wooden'
    STEEL = 'steel'


class Building:

    def __init__(self, infiltration_method: str, story: Story, c_value: float, inside_pressure: InsidePressure):

        self._infiltration_method = infiltration_method
        self._story = story
        self._c_value = c_value
        self._inside_pressure = inside_pressure

    @classmethod
    def create_building(cls, d: Dict):

        ifl = d['infiltration']

        ifl_method = ifl['method']

        if ifl_method == 'balance_residential':

            # 建物の階数
            story = Story(ifl['story'])

            # C値
            if ifl['c_value_estimate'] == 'specify':

                c_value = ifl['c_value']

            elif ifl['c_value_estimate'] == 'calculate':

                c_value = cls._estimate_c_value(ua_value=ifl['ua_value'], struct=Structure(ifl['struct']))

            else:

                raise ValueError()

            # 換気の種類
            inside_pressure = InsidePressure(ifl['inside_pressure'])

        else:

            raise KeyError()

        return Building(
            infiltration_method=ifl_method,
            story=story,
            c_value=c_value,
            inside_pressure=inside_pressure
        )

    @property
    def infiltration_method(self):
        return self._infiltration_method

    @property
    def story(self):
        return self._story

    @property
    def c_value(self):
        return self._c_value

    @property
    def inside_pressure(self):
        return self._inside_pressure

    @classmethod
    def _estimate_c_value(cls, ua_value: float, struct: Structure):

        """
        Args
            ua_value: UA値, W/m2 K
            struct: 構造
        Returns:
            C値, cm2/m2
        """

        a = {
            Structure.RC: 4.16,       # RC造
            Structure.SRC: 4.16,      # SRC造
            Structure.WOODEN: 8.28,   # 木造
            Structure.STEEL: 8.28,    # 鉄骨造
        }[struct]

        return a * ua_value

    def get_v_leak_is_n(
            self,
            theta_r_is_n: np.ndarray,
            theta_o_n: float,
            v_room_is: np.ndarray,
    ):
        """すきま風量を取得する関数（住宅用、圧力バランスを解いた近似式バージョン）
        住宅を１つの空間に見立てて予め圧力バランスを解き、
        Args:
            theta_r_is_n: 時刻nの室温, degree C, [i,1]
            theta_o_n: 時刻n+1の外気温度, degree C
            v_room_is: 室iの容積, m3, [i,1]
        Returns:
            すきま風量, m3/s, [i,1]
        """

        return _get_infiltration_residential(
            theta_r_is_n=theta_r_is_n,
            theta_o_n=theta_o_n,
            c_value=self.c_value,
            v_room_is=v_room_is,
            story=self.story,
            inside_pressure=self.inside_pressure
        )


def _get_infiltration_residential(
        theta_r_is_n: np.ndarray,
        theta_o_n: float,
        c_value: float,
        v_room_is: np.ndarray,
        story: Story,
        inside_pressure: InsidePressure
) -> np.ndarray:
    """すきま風量を取得する関数（住宅用、圧力バランスを解いた近似式バージョン）

    Args:
        theta_r_is_n: 時刻nの室温, degree C, [i,1]
        theta_o_n: 時刻n+1の外気温度, degree C
        c_value: 相当隙間面積, cm2/m2
        v_room_is: 室iの容積, m3, [i,1]
        story: 階
        inside_pressure: 室内側の圧力
            'negative': 負圧
            'positive': 正圧
            'balanced': バランス圧力
    Returns:
        すきま風量, m3/s, [i,1]
    """

    # 室気積加重平均室温theta_r_nの計算, degree C, float
    theta_average_r_n = np.average(theta_r_is_n, weights=v_room_is)

    # 室内外温度差の計算, degree C, float
    delta_theta = abs(theta_average_r_n - theta_o_n)

    # 係数aの計算, 回/(h (cm2/m2 K^0.5))
    a = {
        # 1階建ての時の係数
        Story.ONE: 0.022,
        # 2階建ての時の係数
        Story.TWO: 0.020
    }[story]

    # 係数bの計算, 回/h
    # 階数と換気方式の組み合わせで決定する
    b = {
        InsidePressure.BALANCED: {
            Story.ONE: 0.00,
            Story.TWO: 0.0
        }[story],
        InsidePressure.POSITIVE: {
            Story.ONE: 0.26,
            Story.TWO: 0.14
        }[story],
        InsidePressure.NEGATIVE: {
            Story.ONE: 0.28,
            Story.TWO: 0.13
        }[story]
    }[inside_pressure]

    # 換気回数の計算
    # Note: 切片bの符号は-が正解（報告書は間違っている）
    infiltration_rate = np.maximum(a * (c_value * math.sqrt(delta_theta)) - b, 0)

    # すきま風量の計算
    infiltration = infiltration_rate * v_room_is / 3600.0

    return infiltration
