import numpy as np
import logging
from typing import List, Dict
from typing import Union

from heat_load_calc.global_number import get_sgm, get_eps
from scipy import optimize


def get_f_mrt_is_js(a_s_js: np.ndarray, h_s_r_js: np.ndarray, p_is_js: np.ndarray) -> np.ndarray:
    """室 i の微小球に対する境界 j の重み係数を求める

    Args:
        a_s_js: 境界 j の面積, m2, [j, 1]
        h_s_r_js: 境界 ｊ の室内側放射熱伝達率, W/m2K, [j, 1]
        p_is_js: 室 i と境界 j の関係を表す係数（境界から室への変換）, [i, j]

    Returns:
        室 i の微小球に対する境界 j の重み係数, -, [i, j]

    Notes:
        式(1)
    """

    ah = a_s_js * h_s_r_js

    return p_is_js * ah.T / np.dot(p_is_js, ah)


def get_h_s_r_js(a_s_js: np.ndarray, p_is_js: np.ndarray) -> np.ndarray:
    """境界 j の室内側放射熱伝達率を求める。

    Args:
        a_s_js: 境界 j の面積, m2, [j, 1]
        p_is_js: 

    Returns:
        境界 j の室内側放射熱伝達率, W/m2K, [j, 1]
    """

    a_s_js = a_s_js.flatten()

    h_s_r_is = np.zeros_like(a=a_s_js, dtype=float)

    for p_i_js in p_is_js:

        is_connected = p_i_js.astype(bool)

        h_s_r_is[is_connected] = _calc_h_s_r_i_js(a_s_i_js=a_s_js[is_connected])

    return h_s_r_is.reshape(-1, 1)


def _calc_h_s_r_i_js(a_s_i_js: np.ndarray) -> np.ndarray:
    """ 放射熱伝達率（室単位で計算する）

    Args:
        a_s_i_js: 境界jの面積, m2, [j, 1]
    Returns:
        放射熱伝達率, W/m2K, [j, 1]
    """

    # 面積比, [j]
    r_a_i_js = a_s_i_js / sum(a_s_i_js)

    # 非線形方程式L(f̅)=0の解, float
    f_ver = _get_f_ver(r_a_i_k=r_a_i_js)

    # 放射伝熱計算で使用する微小球に対する部位の形態係数, -, [j]
    f_i_js = _get_f_i_k(f_ver_i=f_ver, r_a_i_k=r_a_i_js)

    # 総和のチェック
    if abs(np.sum(f_i_js) - 1.0) > 1.0e-3:
        logging.warning('形態係数の合計値が不正 TotalFF=', np.sum(f_i_js))

    h_s_r_i_js = _get_h_s_r_i_js(f_i_js=f_i_js)

    return h_s_r_i_js


def _get_h_s_r_i_js(f_i_js):
    """室 i に接する境界 j の放射熱伝達率を計算する。

    Args:
        f_i_js: 室 i の微小球からみた境界 j への形態係数

    Returns:
        室 i に接する境界 j の放射熱伝達率, W/m2K, [j]
    """

    # 境界間の放射熱伝達率を決定する際、平均放射温度を20℃固定値であるとして計算する。
    theta_mrt = 20.0

    return get_eps() / (1.0 - get_eps() * f_i_js) * 4.0 * get_sgm() * (273.15 + theta_mrt) ** 3.0


def _get_f_ver(r_a_i_k: np.ndarray) -> float:
    """
    非線形方程式L(f̅)=0の解
    Args:
        r_a_i_k: 面積比, [j]
    Returns:
        非線形方程式L(f̅)=0の解
    Notes:
        式(5)
    """

    def function_L(f_ver_i):
        """
        Args:
            f_ver_i: 非線形方程式L(f_ver_i)の解
        """
        return np.sum(_get_f_i_k(f_ver_i=f_ver_i, r_a_i_k=r_a_i_k)) - 1.0

    f_ver = float(optimize.fsolve(function_L, np.array(1.0))[0])

    return f_ver


def _get_f_i_k(f_ver_i: float, r_a_i_k: np.ndarray) -> np.ndarray:
    """
    空間内の微小球からみた面iへの形態係数を計算する。
    Args:
        f_ver_i: 非線形方程式L(f_ver_i)の解, -
        r_a_i_k: 同一方位となる表面のグループ k の面積が室 i 内の表面積の総和に占める比, -, [k]
    Returns:
        室 i の微小球から同一方位となる表面のグループ k への形態係数
    Notes:
        式(4)
    """

    return 0.5 * (1.0 - np.sign(1.0 - 4.0 * r_a_i_k / f_ver_i) * np.sqrt(np.abs(1.0 - 4.0 * r_a_i_k / f_ver_i)))


