import numpy as np
import math


def get_infiltration(c_value: float, v_room_cap_is: np.ndarray, story: int, vent_type: int,
                     delta_theta: float) -> np.ndarray:
    """すきま風量を取得する。

    Args:
        c_value: 相当隙間面積, cm2/m2, [i, 1]
        v_room_cap_is: 室気積, m3, [i,1]
        story: 階
        vent_type: 換気方式, 第?種換気
        delta_theta: 内外温度差, degree C

    Returns:
        すきま風量, m3/s, [i,1]
    """

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
        1: {
            1: 0.00,
            2: 0.0
        }[story],
        2: {
            1: 0.26,
            2: 0.14
        }[story],
        3: {
            1: 0.28,
            2: 0.13
        }[story]
    }[vent_type]

    # print(a, b)
    # 換気回数の計算
    # 切片bの符号は-が正解（報告書は間違っている）
    infiltration_rate = np.maximum(a * (c_value * math.sqrt(delta_theta)) - b, 0)

    # すきま風量の計算
    infiltration = infiltration_rate * v_room_cap_is / 3600.0

    return infiltration


def test():
    c_value = np.array([2.0, 0.5, 1.0])
    v_room_cap_is = np.array([50.0, 20.0, 60.0])
    story = 2
    vent_type = 3
    delta_theta = 20.
    print(get_infiltration(
        c_value=c_value,
        v_room_cap_is=v_room_cap_is,
        story=story,
        vent_type=vent_type,
        delta_theta=delta_theta
    )
    )
