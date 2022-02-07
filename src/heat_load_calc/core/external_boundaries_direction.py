"""境界の向きから傾斜面の方位角・傾斜角を決定する。
附属書X19 傾斜面の方位角・傾斜角
"""

from typing import Tuple
import numpy as np


def get_w_alpha_j_w_beta_j(direction_j: str) -> Tuple[float, float]:
    """
    方向名称から傾斜面の方位角・傾斜角を求める。

    Args:
        direction_j: 境界jにおける方向

    Returns:
        以下のタプル
            (1) 室iの境界jの傾斜面の方位角, rad
            (2) 室iの境界jの傾斜面の傾斜角, rad
    """

    w_alpha_j_degree, w_beta_j_degree = {
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
    }[direction_j]

    return np.radians(w_alpha_j_degree), np.radians(w_beta_j_degree)




