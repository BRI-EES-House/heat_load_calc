"""
付録15．	ルームエアコンの定格能力、風量の計算
"""

import numpy as np


def get_q_rtd(a_floor_is: np.ndarray) -> (np.ndarray, np.ndarray):
    """
    定格能力を計算する。
    Args:
        a_floor_is: 床面積, m2, [i]
    Returns:
        以下のタプル
            定格暖房能力, W, [i]
            定格冷房能力, W, [i]
    """

#    q_rtd_c = np.minimum(190.5 * a_floor_is + 45.6, 5600.0)
    q_rtd_c = 190.5 * a_floor_is + 45.6

    q_rtd_h = 1.2090 * q_rtd_c - 85.1

    return q_rtd_h, q_rtd_c


def get_q_max(q_rtd_h_is: np.ndarray, q_rtd_c_is: np.ndarray) -> (np.ndarray, np.ndarray):
    """
    最大能力を取得する。
    Args:
        q_rtd_h_is: 定格暖房能力, W, [i]
        q_rtd_c_is: 定格冷房能力, W, [i]
    Returns:
        以下のタプル
            最大暖房能力, W, [i]
            最大冷房能力, W, [i]
    """

#    q_max_c = np.maximum(0.8462 * q_rtd_c_is + 1205.9, q_rtd_c_is)
    q_max_c = 0.8462 * q_rtd_c_is + 1205.9

#    q_max_h = np.maximum(1.7597 * q_max_c - 413.7, q_rtd_h_is)
    q_max_h = 1.7597 * q_max_c - 413.7

    return q_max_h, q_max_c


def get_q_min_h():
    """
    最小能力を計算する。
    Returns:
        以下のタプル
            最小暖房能力, W, [i]
    Notes:
        とりあえず500Wで固定する。
    """

    return 500.0


def get_q_min_c():
    """
    最小能力を計算する。
    Returns:
        以下のタプル
            最小冷房能力, W, [i]
    Notes:
        とりあえず500Wで固定する。
    """

    return 500.0


# 最大風量[m3/min]の計算 式(107)
def get_v_max(qrtd_c):
    """
    :param qrtd_c: 定格冷房能力[W]
    :return:
    """
    Vmax = 11.076 * (qrtd_c / 1000.0) ** 0.3432
    return Vmax


# 最小風量[m3/min]の計算 式(108)
def get_v_min(Vmax):
    """
    :param Vmax: 最大風量[m3/min]
    :return:
    """
    Vmin = Vmax * 0.55
    return Vmin


