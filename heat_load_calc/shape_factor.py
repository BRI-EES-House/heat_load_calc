import numpy as np
import logging
from typing import Union
from enum import Enum

from heat_load_calc.global_number import get_sgm, get_eps
from scipy import optimize


class ShapeFactorMethod(Enum):

    AREA_AVERAGE = 'area_average'
    NAGATA = 'Nagata'


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


def get_h_s_r_js(a_s_js: np.ndarray, p_is_js: np.ndarray, eps_r_i_js: np.ndarray, method: ShapeFactorMethod) -> np.ndarray:
    """Calculate indoor surface radiant heat transfer coefficient of boundary j.

    Args:
        a_s_js: surface area of boundary j, [J, 1]
        p_is_js: matrix representing the relationship between rooms and boundaries, (0 or 1), [I, J]
        eps_r_i_js: inside long wave radiative emissivity of boundary j, -, [J, 1]
        method: method for calculation of mutual shape factor of each boundaries, AREA_AVERAGE or NAGATA

    Returns:
        indoor surface radiant heat transfer coefficient of boundary j, W/m2K, [J, 1]
    """

    match method:

        case ShapeFactorMethod.AREA_AVERAGE:
            return _get_h_s_r_js_AreaAverage(a_s_js=a_s_js, p_is_js=p_is_js, eps_r_i_js=eps_r_i_js)
        case ShapeFactorMethod.NAGATA:
            return _get_h_s_r_js_Nagata(a_s_js=a_s_js, p_is_js=p_is_js, eps_r_js=eps_r_i_js)
        case _:
            raise ValueError()


def _get_h_s_r_js_AreaAverage(a_s_js: np.ndarray, eps_r_i_js: np.ndarray, p_is_js: np.ndarray) -> np.ndarray:
    """Calculate inside surface radiant heat transfer coefficient of boundary j (Area Ratio Method)
    
    Args:
        a_s_js: surface area of boundary j, m2, [J, 1]
        eps_r_i_js: inside long wave emissivity of boundary j, -, [J, 1]
        p_is_js: matrix representing the relationship between rooms and boundaries, (0 or 1), [I, J]

    Returns:
        inside surface radiant heat transfer coefficient of boundary j, W/m2K, [J, 1]
    """

    # ratio of the area of the boundary j to the sum of the arera of the boundary connecting to room i, -, [J, 1]
    r_a_js = _get_r_a_js(a_s_js=a_s_js, p_is_js=p_is_js)

    # The shape factor is considered equal to the area ratio.
    f_js = r_a_js

    _check_sum_f_value(p_is_js=p_is_js, f_js=f_js)

    h_s_r_js = _get_h_s_r_i_js(eps_r_i_js=eps_r_i_js, f_js=f_js)

    return h_s_r_js


def _get_h_s_r_js_Nagata(a_s_js: np.ndarray, eps_r_js: np.ndarray, p_is_js: np.ndarray) -> np.ndarray:
    """境界 j の室内側放射熱伝達率（永田メソッド）を求める。

    Args:
        a_s_js: 境界 j の面積, m2, [j, 1]
        eps_r_js: 境界 j の室内側長波長放射率, -, [j, 1]
        p_is_js: 

    Returns:
        境界 j の室内側放射熱伝達率, W/m2K, [j, 1]
    """

    # ratio of the area of the boundary j to the sum of the arera of the boundary connecting to room i, -, [J, 1]
    r_a_js = _get_r_a_js(a_s_js=a_s_js, p_is_js=p_is_js)

    # area ratio of the boundary j in room i, [I, J]
    r_a_is_js = p_is_js * r_a_js.flatten()[np.newaxis, :]

    # 非線形方程式L(f̅)=0の解, [I, 1]
    f_ver_is = _get_f_ver_is(r_a_is_js=r_a_is_js)

    # 放射伝熱計算で使用する微小球に対する部位の形態係数, -, [j]
    f_is_js = _get_f_i_k(f_ver_is=f_ver_is, r_a_is_js=r_a_is_js)

    f_js = f_is_js.sum(axis=0).reshape(-1,1)

    _check_sum_f_value(p_is_js=p_is_js, f_js=f_js)

    h_s_r_js = _get_h_s_r_i_js(eps_r_i_js=eps_r_js, f_js=f_js)

    return h_s_r_js


def _get_r_a_js(a_s_js: np.ndarray, p_is_js: np.ndarray) -> np.ndarray:
    """Get the ratio of the area of boundary i to the sum of the area in each room.

    Args:
        a_s_js: area of boundary j, [J, 1]
        p_is_js: matrix of the relationship between rooms and boundaries, [I, J]

    Returns:
        ratio of area of boundary i, [J, 1]
    """

    # sum of the area of the boundary connecting to room i, m2, [I, 1]
    a_s_sum_is = np.dot(p_is_js, a_s_js)

    # ratio of the area of the boundary j to the sum of the arera of the boundary connecting to room i, -, [J, 1]
    r_a_js = a_s_js / np.dot(p_is_js.T, a_s_sum_is)

    return r_a_js


def _get_h_s_r_i_js(eps_r_i_js: np.ndarray, f_js: np.ndarray) -> np.ndarray:
    """室 i に接する境界 j の放射熱伝達率を計算する。

    Args:
        eps_r_i_js: inside long wave radiative emissivity of boundary j, -, [J, 1]
        f_is_js: shape factor from micro-spheres in room of boundary j, -, [J, 1]

    Returns:
        室 i に接する境界 j の放射熱伝達率, W/m2K, [j]
    """

    # 境界間の放射熱伝達率を決定する際、平均放射温度を20℃固定値であるとして計算する。
    theta_mrt = 20.0

    # radiative heat transfer efficient of boundary i, W/ m2K
    h_s_r_js = (eps_r_i_js / (1.0 - eps_r_i_js * f_js) * 4.0 * get_sgm() * (273.15 + theta_mrt) ** 3.0)

    return h_s_r_js


def _get_f_ver_is(r_a_is_js: np.ndarray) -> np.ndarray:
    """
    非線形方程式L(f̅)=0の解
    Args:
        r_a_is_js: the area ratio of the boundary j to the sum of the area of boundary connecting to rooms, [I, J]
    Returns:
        非線形方程式L(f̅)=0の解, [I, 1]
    Notes:
        式(5)
    """

    return  np.array([_get_f_ver(r_a_i_js=r_a_i_js) for r_a_i_js in r_a_is_js]).reshape(-1, 1)


def _get_f_ver(r_a_i_js: np.ndarray) -> float:

    def function_L(f_ver_i):
        """
        Args:
            f_ver_i: 非線形方程式L(f_ver_i)の解
        """
        return np.sum(_get_f_i_k(f_ver_is=f_ver_i, r_a_is_js=r_a_i_js)) - 1.0

    return float(optimize.fsolve(function_L, np.array(1.0))[0])


def _get_f_i_k(f_ver_is: np.ndarray, r_a_is_js: np.ndarray) -> np.ndarray:
    """空間内の微小球からみた面iへの形態係数を計算する。
    
    Args:
        f_ver_i: 非線形方程式L(f_ver_i)の解, -, [I, 1]
        r_a_is_js: ratio of area ou boundary i to the sum of area of the boundaries connected room i, -, [I, J]
    Returns:
        室 i の微小球から同一方位となる表面のグループ k への形態係数
    Notes:
        式(4)
    """

    return 0.5 * (1.0 - np.sign(1.0 - 4.0 * r_a_is_js / f_ver_is) * np.sqrt(np.abs(1.0 - 4.0 * r_a_is_js / f_ver_is)))


def _check_sum_f_value(p_is_js, f_js):

    f_sum_is = np.dot(p_is_js, f_js)

    # Check whether the sum of f value in each room are equal to 1.0.
    for f_sum_i in f_sum_is.flatten():
        if abs(f_sum_i - 1.0) > 1.0e-3:
            logging.warning('形態係数の合計値が不正 TotalFF=', f_sum_i)

