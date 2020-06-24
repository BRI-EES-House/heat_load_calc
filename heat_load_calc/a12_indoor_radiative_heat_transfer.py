import math
import numpy as np

from heat_load_calc.external.global_number import get_sgm, get_eps


"""
付録12．	室内表面の吸収日射量、形態係数、放射暖房放射成分吸収比率
"""


def get_f_mrt_is_js(a_srf_js, h_r_js, k_is_js):

    ah = a_srf_js * h_r_js

    return k_is_js * ah.T / np.dot(k_is_js, ah)


def get_r_sol_frnt() -> float:
    """室内侵入日射のうち家具に吸収される割合を計算する。

    Returns:
        室内侵入日射のうち家具に吸収される割合
    """

    return 0.5


def get_r_sol_bnd_i_jstrs(a_bnd_i_jstrs: np.ndarray, is_solar_absorbed_inside_bnd_i_jstrs: np.ndarray) -> np.ndarray:
    """室の統合された境界における室内側表面の日射吸収比率を計算する。

    Args:
        a_bnd_i_jstrs: 室iの統合された境界j*の面積, [j*]
        is_solar_absorbed_inside_bnd_i_jstrs: 室iの統合された境界j*の室内侵入日射吸収の有無, [j*]
        a_floor_i: 室iの床面積の合計, m2, [j*]

    Returns:
        室iの統合された境界j*における室内側表面の日射吸収比率
    """

    # 室内侵入日射のうち統合された境界の室内側表面に吸収される割合
    r_sol_bnds = 1.0 - get_r_sol_frnt()

    return r_sol_bnds * a_bnd_i_jstrs * is_solar_absorbed_inside_bnd_i_jstrs\
        / np.sum(a_bnd_i_jstrs * is_solar_absorbed_inside_bnd_i_jstrs)


def get_q_sol_floor_i_jstrs_ns(
        q_trs_sol_i_ns: np.ndarray,
        a_bnd_i_jstrs: np.ndarray,
        is_solar_absorbed_inside_bnd_i_jstrs
):
    """統合された境界における室の透過日射熱取得のうちの吸収日射量を計算する。

    Args:
        q_trs_sol_i_ns: ステップnの室iにおける窓の透過日射熱取得, W, [8760*4]
        a_bnd_i_jstrs: 室iの統合された境界j*の面積, [j*]
        is_solar_absorbed_inside_bnd_i_jstrs: 室iの統合された境界j*の床室内侵入日射吸収の有無, [j*]

    Returns:
        室iの統合された境界j*における室の透過日射熱取得のうちの吸収日射量, W/m2, [j*, 8760*4]
    """

    # 室iの統合された境界j*における室内側表面の日射吸収比率
    r_sol_floor_i_jstrs = get_r_sol_bnd_i_jstrs(
        a_bnd_i_jstrs=a_bnd_i_jstrs,
        is_solar_absorbed_inside_bnd_i_jstrs=is_solar_absorbed_inside_bnd_i_jstrs,
    )

    return q_trs_sol_i_ns[np.newaxis, :] * r_sol_floor_i_jstrs[:, np.newaxis] / a_bnd_i_jstrs[:, np.newaxis]


def get_q_sol_frnt_i_ns(q_trs_sol_i_ns):
    """家具の吸収日射量を計算する。

    Args:
        q_trs_sol_i_ns: ステップnの室iにおける窓の透過日射熱取得, W, [8760*4]

    Returns:
        ステップnの室iにおける家具の吸収日射量, W, [8760*4]
    """

    # 室内侵入日射のうち家具に吸収される割合
    r_sol_frnt = get_r_sol_frnt()

    return q_trs_sol_i_ns * r_sol_frnt


# 放射暖房放射成分吸収比率 表7
def get_flr(A_i_g, A_fs_i, is_radiative_heating, is_solar_absorbed_inside):
    return (A_i_g / A_fs_i) * is_radiative_heating * is_solar_absorbed_inside


