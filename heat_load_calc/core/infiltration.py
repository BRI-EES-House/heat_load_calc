import numpy as np
import math
from typing import Dict, Callable


def make_get_infiltration_function(rd: Dict) -> Callable[[np.ndarray, float], np.ndarray]:
    """
    室温と外気温度から隙間風を計算する関数を作成する。
    Args:
        rd: 入力する辞書
    Returns:
        室温と外気温度から隙間風を計算する関数
    """

    # 建物全体に関すること
    bdg = rd['building']

    # 隙間風の計算方法

    if bdg['infiltration_method'] == 'balance_residential':

        # 建物の階数
        story = bdg['story']

        # C値
        c_value = bdg['c_value']

        # 換気の種類
        inside_p = bdg['inside_pressure']

        # spaces の取り出し
        ss = rd['spaces']

        # 空間iの気積, m3, [i, 1]
        v_room_is = np.array([float(s['volume']) for s in ss]).reshape(-1, 1)

        def get_infiltration(theta_r_is_n: np.ndarray, theta_o_n: float):

            return _get_infiltration_residential(
                c_value=c_value,
                v_room_is=v_room_is,
                story=story,
                inside_pressure=inside_p,
                theta_r_is_n=theta_r_is_n,
                theta_o_n=theta_o_n
            )

        return get_infiltration

    else:

        raise Exception


def _get_infiltration_residential(
        c_value: float,
        v_room_is: np.ndarray,
        story: int,
        inside_pressure: str,
        theta_r_is_n: np.ndarray,
        theta_o_n: float
) -> np.ndarray:
    """すきま風量を取得する関数（住宅用、圧力バランスを解いた近似式バージョン）
    住宅を１つの空間に見立てて予め圧力バランスを解き、
    Args:
        c_value: 相当隙間面積, cm2/m2
        v_room_is: 室iの容積, m3, [i,1]
        story: 階
        inside_pressure: 室内側の圧力
            'negative': 負圧
            'positive': 正圧
            'balanced': バランス圧力
        theta_r_is_n: 時刻nの室温, degree C, [i,1]
        theta_o_n: 時刻n+1の外気温度, degree C
    Returns:
        すきま風量, m3/s, [i,1]
    """

    # 室気積の合計値, m3, float
    total_air_volume = np.sum(v_room_is)
    # 室気積加重平均室温theta_r_nの計算, degree C, float
    theta_average_r_n = np.average(theta_r_is_n, weights=v_room_is)

    # 室内外温度差の計算, degree C, float
    delta_theta = abs(theta_average_r_n - theta_o_n)

    # 係数aの計算, 回/(h (cm2/m2 K^0.5))
    a = {
        # 1階建ての時の係数
        1: 0.022,
        # 2階建ての時の係数
        2: 0.020
    }[story]

    # 係数bの計算, 回/h
    # 階数と換気方式の組み合わせで決定する
    b = {
        'balanced': {
            1: 0.00,
            2: 0.0
        }[story],
        'positive': {
            1: 0.26,
            2: 0.14
        }[story],
        'negative': {
            1: 0.28,
            2: 0.13
        }[story]
    }[inside_pressure]

    # print(a, b)
    # 換気回数の計算
    # 切片bの符号は-が正解（報告書は間違っている）
    infiltration_rate = np.maximum(a * (c_value * math.sqrt(delta_theta)) - b, 0)

    # すきま風量の計算
    infiltration = infiltration_rate * v_room_is / 3600.0

    return infiltration
