import numpy as np
import math
from typing import Dict, Callable, List
from functools import partial
from enum import Enum

from heat_load_calc.building import Story, InsidePressure, Structure, Building


def make_get_infiltration_function(v_rm_is: np.ndarray, building: Building):
    """
    室温と外気温度から隙間風を計算する関数を作成する。
    Args:
        v_rm_is: 空間 i の気積, m3, [i, 1]
        building: Building クラス
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

    return partial(
        _get_infiltration_residential,
        c_value=building.c_value,
        v_room_is=v_rm_is,
        story=building.story,
        inside_pressure=building.inside_pressure
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


def _estimate_c_value(ua_value: float, struct: Structure) -> float:
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
