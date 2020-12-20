import numpy as np
import math


def get_infiltration_residential(
        c_value: float,
        v_room_is: np.ndarray,
        story: int,
        inside_pressure: str,
        theta_r_is_n: np.ndarray,
        theta_o_npls: float
) -> np.ndarray:
    """すきま風量を取得する。

    Args:
        c_value: 相当隙間面積, cm2/m2
        v_room_is: 室iの容積, m3, [i,1]
        story: 階
        inside_pressure: 室内側の圧力
            'negative': 負圧
            'positive': 正圧
            'balanced': バランス圧力
        theta_r_is_n: 時刻nの室温, degree C, [i,1]
        theta_o_npls: 時刻n+1の外気温度, degree C

    Returns:
        すきま風量, m3/s, [i,1]
    """
    # 室気積の合計値, m3, float
    total_air_volume = np.sum(v_room_is)
    # 室気積加重平均室温theta_r_nの計算, degree C, float
    theta_average_r_n = np.average(theta_r_is_n, weights=v_room_is)

    # 室内外温度差の計算, degree C, float
    delta_theta = abs(theta_average_r_n-theta_o_npls)

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
