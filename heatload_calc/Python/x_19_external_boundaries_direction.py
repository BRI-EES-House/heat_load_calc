# 附属書X19 傾斜面の方位角・傾斜角
# 境界の向きから傾斜面の方位角・傾斜角を決定する。

import numpy as np


def get_w_alpha_i_k_w_beta_i_k(direction_i_k: str) -> (float, float):
    """
    方向名称から傾斜面の方位角・傾斜角を求める。

    Args:
        direction_i_k: 室iの境界kにおける方向

    Returns:
        以下のタプル
            (1) 室iの境界kの傾斜面の方位角, rad
            (2) 室iの境界kの傾斜面の傾斜角, rad
    """

    w_alpha_i_k_degree, w_beta_i_k_degree = {
        's': (0.0, 90.0),
        'sw': (45.0, 90.0),
        'w': (90.0, 90.0),
        'nw': (135.0, 90.0),
        'n': (180.0, 90.0),
        'ne': (-135.0, 90.0),
        'e': (-90.0, 90.0),
        'se': (-45.0, 90.0),
        'top': (0.0, 0.0),
        'bottom': (0.0, 180.0)
    }[direction_i_k]

    return np.radians(w_alpha_i_k_degree), np.radians(w_beta_i_k_degree)




