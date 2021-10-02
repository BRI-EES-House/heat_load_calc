"""
家具の熱容量・熱コンダクタンスと備品等の湿気容量・湿気コンダクタンスを計算するモジュール
"""

import numpy as np


def get_c_cap_frt_is(v_room_cap_is: np.ndarray) -> np.ndarray:
    """
    家具の熱容量を計算する。
    Args:
        v_room_cap_is: 室iの気積, m3, [i]
    Returns:
        家具の熱容量, J/K, [i]
    """

    # 室の家具の顕熱容量, kJ/m3 K
    furniture_sensible_capacity = 12.6

    # 家具熱容量, J/K, [i]
    c_cap_frt_is = furniture_sensible_capacity * v_room_cap_is * 1000.0

    return c_cap_frt_is


def get_g_sh_frt_is(c_sh_frt_is: np.ndarray) -> np.ndarray:
    """
    家具と空気間の熱コンダクタンスを取得する。
    Args:
        c_sh_frt_is: 家具の熱容量, J/K, [i]
    Returns:
        家具と空気間の熱コンダクタンス, W/K, [i]
    """

    g_sh_frt_is = 0.00022 * c_sh_frt_is

    return g_sh_frt_is


def get_c_lh_frt_is(v_room_cap_is: np.ndarray) -> np.ndarray:
    """
    家具類の湿気容量を計算する。
    Args:
        v_room_cap_is: 室iの気積, m3, [i]
    Returns:
        家具類の湿気容量, kg, [i]
    """

    # 室の家具の潜熱容量, kg/(m3 kg/kg(DA))
    furniture_latent_capacity = 16.8

    # 家具類の湿気容量, kg, [i]
    c_lh_frt_is = furniture_latent_capacity * v_room_cap_is

    return c_lh_frt_is


def get_g_lh_frt_is(c_lh_frt_is: np.ndarray) -> np.ndarray:
    """
    空気と家具類間の湿気コンダクタンスを取得する。
    Args:
        c_lh_frt_is: 室iの家具等の湿気容量, kg/m3 kg/kgDA, [i]
    Returns:
        室空気と家具類間の湿気コンダクタンス, kg/(s･kg/kg(DA)), [i]
    """

    g_lh_frt_is = 0.0018 * c_lh_frt_is

    return g_lh_frt_is
