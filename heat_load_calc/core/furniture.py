"""
家具に関するモジュール
仕様書：備品等
"""

import numpy as np
from typing import List


def get_furniture_specs(d_frt: List[dict], v_rm_is: np.ndarray) -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray):
    """
        備品等に関する物性値を取得する。
    Args:
        d_frt: 備品等に関する入力情報
        v_rm_is: 室 i の容量, m3, [i, 1]
    Returns:
        家具に関する物性値
            室 i の備品等の熱容量, J/K, [i, 1]
            室 i の空気と備品等間の熱コンダクタンス, W/K, [i, 1]
            室 i の備品等の湿気容量, kg/(kg/kgDA), [i, 1]
            室 i の空気と備品等間の湿気コンダクタンス, kg/(s (kg/kgDA)), [i, 1]
    Notes:
        各値は、特定の値の入力を受け付ける他に、以下の式(1)～(4)により室容積から推定する方法を設定する。
    """

    # 室 i の備品等の熱容量, J/K, [i, 1]
    c_sh_frt_is = []
    # 室 i の空気と備品等間の熱コンダクタンス, W/K, [i, 1]
    g_sh_frt_is = []
    # 室 i の備品等の湿気容量, kg/(kg/kgDA), [i, 1]
    c_lh_frt_is = []
    # 室 i の空気と備品等間の湿気コンダクタンス, kg/(s (kg/kgDA)), [i, 1]
    g_lh_frt_is = []

    for i, f in enumerate(d_frt):

        v_rm_i = v_rm_is[i]

        if f['input_method'] == 'default':

            # 入力方法がデフォルト指定している場合は室容積から各物性値を推定する。

            c_sh_frt_i = _get_c_sh_frt_i(v_rm_i=v_rm_i)
            g_sh_frt_i = _get_g_sh_frt_i(c_sh_frt_i=c_sh_frt_i)
            c_lh_frt_i = _get_c_lh_frt_i(v_rm_i=v_rm_i)
            g_lh_frt_i = _get_g_lh_frt_i(c_lh_frt_i=c_lh_frt_i)

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


def _get_c_sh_frt_i(v_rm_i: float) -> float:
    """
    備品等の熱容量を計算する。
    Args:
        v_rm_i: 室iの気積, m3
    Returns:
        室 i の備品等の熱容量, J/K
    Notes:
        式(4)
    """

    # 室の気積あたりの備品等の熱容量を表す係数, J/(m3 K)
    f_c_sh_frt = 12.6 * 1000.0

    return f_c_sh_frt * v_rm_i


def _get_g_sh_frt_i(c_sh_frt_i: float) -> float:
    """
    空気と備品等間の熱コンダクタンスを取得する。
    Args:
        c_sh_frt_i: 室 i の備品等の熱容量, J/K
    Returns:
        室 i の空気と備品等間の熱コンダクタンス, W/K
    Notes:
        式(3)
    """

    # 備品等の熱容量あたりの空気との間の熱コンダクタンスを表す係数, 1/s
    f_g_sh_frt = 0.00022

    return f_g_sh_frt * c_sh_frt_i


def _get_c_lh_frt_i(v_rm_i: float) -> float:
    """
    備品等の湿気容量を計算する。
    Args:
        v_rm_i: 室iの気積, m3
    Returns:
        室 i の備品等の湿気容量, kg/(kg/kg(DA))
    Notes:
        式(2)
    """

    # 室の気積あたりの備品等の湿気容量を表す係数, kg/(m3 kg/kg(DA))
    f_c_lh_frt = 16.8

    return f_c_lh_frt * v_rm_i


def _get_g_lh_frt_i(c_lh_frt_i: float) -> float:
    """
    空気と備品等間の湿気コンダクタンスを取得する。
    Args:
        c_lh_frt_i: 室iの備品等の湿気容量, kg/(kg/kg(DA))
    Returns:
        室iの空気と備品等間の湿気コンダクタンス, kg/(s kg/kg(DA))
    Notes:
        式(1)
    """

    # 備品等の湿気容量あたりの空気との間の湿気コンダクタンスを表す係数, 1/s
    f_g_lh_frt = 0.0018

    return f_g_lh_frt * c_lh_frt_i

