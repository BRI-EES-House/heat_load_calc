import numpy as np
import math
from typing import Dict, Callable, List
from functools import partial
from enum import Enum


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


def make_get_infiltration_function(infiltration: Dict, v_rm_is):
    """
    室温と外気温度から隙間風を計算する関数を作成する。
    Args:
        infiltration: 隙間風に関する辞書
        v_rm_is: 空間 i の気積, m3, [i, 1]
    Returns:
        室温と外気温度から隙間風を計算する関数
    Notes:
        作成される関数の引数と戻り値は以下のとおり。
            引数:
                theta_r_is_n: 時刻nの室温, degree C, [i,1]
                theta_o_n: 時刻n+1の外気温度, degree C
            戻り値:
                すきま風量, m3/s, [i,1]
    """

    # 隙間風の計算方法

    if infiltration['method'] == 'balance_residential':

        # 建物の階数
        story = Story(infiltration['story'])

        # C値
        c_value = infiltration['c_value']

        # 換気の種類
        inside_pressure = InsidePressure(infiltration['inside_pressure'])

        return partial(
            _get_infiltration_residential,
            c_value=c_value,
            v_room_is=v_rm_is,
            story=story,
            inside_pressure=inside_pressure
        )

    else:

        raise Exception


def _get_infiltration_residential(
        theta_r_is_n: np.ndarray,
        theta_o_n: float,
        c_value: float,
        v_room_is: np.ndarray,
        story: Story,
        inside_pressure: InsidePressure
) -> np.ndarray:
    """すきま風量を取得する関数（住宅用、圧力バランスを解いた近似式バージョン）
    住宅を１つの空間に見立てて予め圧力バランスを解き、
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
