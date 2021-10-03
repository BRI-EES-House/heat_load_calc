"""
家具の熱容量・熱コンダクタンスと備品等の湿気容量・湿気コンダクタンスを計算するモジュール
"""

import numpy as np
from typing import List


def get_furniture_specs(
        furnitures: List[dict], v_rm_is: np.ndarray
) -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray):
    """
        家具に関する物性値を取得する。
    Args:
        furnitures: 家具に関する入力情報
        v_rm_is: 室容量, m3, [i, 1]
    Returns:
        家具に関する物性値
            室iの家具等の熱容量, J/K, [i, 1]
            室iの家具等と空気間の熱コンダクタンス, W/K, [i, 1]
            室iの家具等の湿気容量, kg/m3 kg/kgDA, [i, 1]
            室iの家具等と空気間の湿気コンダクタンス, kg/s (kg/kgDA), [i, 1]
    """

    # 室iの家具等の熱容量, J/K, [i, 1]
    c_sh_frt_is = []
    # 室iの家具等と空気間の熱コンダクタンス, W/K, [i, 1]
    g_sh_frt_is = []
    # 室iの家具等の湿気容量, kg/m3 kg/kgDA, [i, 1]
    c_lh_frt_is = []
    # 室iの家具等と空気間の湿気コンダクタンス, kg/s (kg/kgDA), [i, 1]
    g_lh_frt_is = []

    for i, f in enumerate(furnitures):

        volume = v_rm_is[i]

        if f['input_method'] == 'default':

            # 入力方法がデフォルト指定している場合は室容積から各物性値を推定する。

            c_sh_frt_i = _get_c_sh_frt(v_rm=volume)
            g_sh_frt_i = _get_g_sh_frt(c_sh_frt=c_sh_frt_i)
            c_lh_frt_i = _get_c_lh_frt(v_rm=volume)
            g_lh_frt_i = _get_g_lh_frt(c_lh_frt=c_lh_frt_i)

        elif f['input_method'] == 'specify':

            # 入力方法が指定するようになっている場合は、入力用辞書からその値を取得する。

            c_sh_frt_i = float(f['heat_capacity'])
            g_sh_frt_i = float(f['heat_cond'])
            c_lh_frt_i = float(f['moisture_capacity'])
            g_lh_frt_i = float(f['moisture_cond'])

        else:
            raise Exception()

        c_sh_frt_is.append(c_sh_frt_i)
        g_sh_frt_is.append(g_sh_frt_i)
        c_lh_frt_is.append(c_lh_frt_i)
        g_lh_frt_is.append(g_lh_frt_i)

    c_sh_frt_is = np.array(c_sh_frt_is).reshape(-1, 1)
    g_sh_frt_is = np.array(g_sh_frt_is).reshape(-1, 1)
    c_lh_frt_is = np.array(c_lh_frt_is).reshape(-1, 1)
    g_lh_frt_is = np.array(g_lh_frt_is).reshape(-1, 1)

    return c_lh_frt_is, c_sh_frt_is, g_lh_frt_is, g_sh_frt_is


def _get_c_sh_frt(v_rm: float) -> float:
    """
    家具の熱容量を計算する。
    Args:
        v_rm: 室iの気積, m3
    Returns:
        家具の熱容量, J/K
    """

    # 室の家具の顕熱容量, kJ/m3 K
    furniture_sensible_capacity = 12.6

    # 家具熱容量, J/K
    c_sh_frt = furniture_sensible_capacity * v_rm * 1000.0

    return c_sh_frt


def _get_g_sh_frt(c_sh_frt: float) -> float:
    """
    家具と空気間の熱コンダクタンスを取得する。
    Args:
        c_sh_frt: 家具の熱容量, J/K
    Returns:
        家具と空気間の熱コンダクタンス, W/K
    """

    g_sh_frt_is = 0.00022 * c_sh_frt

    return g_sh_frt_is


def _get_c_lh_frt(v_rm: float) -> float:
    """
    家具類の湿気容量を計算する。
    Args:
        v_rm: 室iの気積, m3
    Returns:
        家具類の湿気容量, kg
    """

    # 室の家具の潜熱容量, kg/(m3 kg/kg(DA))
    furniture_latent_capacity = 16.8

    # 家具類の湿気容量, kg
    c_lh_frt_is = furniture_latent_capacity * v_rm

    return c_lh_frt_is


def _get_g_lh_frt(c_lh_frt: float) -> float:
    """
    空気と家具類間の湿気コンダクタンスを取得する。
    Args:
        c_lh_frt: 室iの家具等の湿気容量, kg/m3 kg/kgDA
    Returns:
        室空気と家具類間の湿気コンダクタンス, kg/(s･kg/kg(DA))
    """

    g_lh_frt_is = 0.0018 * c_lh_frt

    return g_lh_frt_is
