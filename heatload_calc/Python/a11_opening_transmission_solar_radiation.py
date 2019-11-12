import numpy as np
from typing import List

import x_19_external_boundaries_direction as x_19

from apdx10_oblique_incidence_characteristics import get_taud_i_k_n
import a7_inclined_surface_solar_radiation as a7
import apdx10_oblique_incidence_characteristics as a10
from s3_surface_loader import Boundary
import a8_shading as a8

"""
付録11．窓の透過日射熱取得の計算
"""


def test(
        boundaries: List[Boundary],
        I_DN_n,
        I_sky_n,
        h_sun_ns,
        a_sun_ns
):
    """

    Args:
        boundaries: 境界
        a_i_ks: 面積（境界数）
        tau_i_k: 室iの境界kの日射熱取得率（境界数）
        I_DN_n: 直達日射（ステップn）
        I_sky_n: 天空放射（ステップn）
        h_sun_ns: 太陽高度
        a_sun_ns: 太陽方位角
    Returns:

    """

    qgts = []

    for i, b in enumerate(boundaries):

        FSDW_i_k_n = a8.get_FSDW_i_k_n2(a_sun_ns, b.direction, h_sun_ns, b.solar_shading_part)

        # 室iの境界kの傾斜面の方位角, rad
        # 室iの境界kの傾斜面の傾斜角, rad
        w_alpha_i_k, w_beta_i_k = x_19.get_w_alpha_i_j_w_beta_i_j(direction_i_j=b.direction)

        # ステップnの室iの境界kにおける傾斜面に入射する太陽の入射角 * 365 * 24 * 4
        theta_aoi_i_k_n = a7.get_theta_aoi_i_k_n(
            w_alpha_i_k=w_alpha_i_k,
            w_beta_i_k=w_beta_i_k,
            h_sun_ns=h_sun_ns,
            a_sun_ns=a_sun_ns
        )

        # ステップnにおける室iの境界kにおける傾斜面の日射量, W / m2K
        # ステップnにおける室iの境界kにおける傾斜面の日射量のうち直達成分, W / m2K
        # ステップnにおける室iの境界kにおける傾斜面の日射量のうち天空成分, W / m2K
        # ステップnにおける室iの境界kにおける傾斜面の日射量のうち地盤反射成分, W / m2K
        _, i_inc_d, i_inc_sky, i_inc_ref = a7.get_i_inc_i_k_n(
            i_dn_ns=I_DN_n,
            i_sky_ns=I_sky_n,
            h_sun_ns=h_sun_ns,
            a_sun_ns=a_sun_ns,
            w_alpha_i_k=w_alpha_i_k,
            w_beta_i_k=w_beta_i_k
        )

        qgt = calc_QGT_i_k_n(
            theta_aoi_i_k=theta_aoi_i_k_n,
            incident_angle_characteristics_i_ks=b.spec.incident_angle_characteristics,
            i_inc_d_i_k_n=i_inc_d,
            FSDW_i_k_n=FSDW_i_k_n,
            i_inc_sky_i_k_n=i_inc_sky,
            i_inc_ref_i_k_n=i_inc_ref,
            a_i_ks=b.area,
            tau_i_k=b.spec.eta_value,
        )

        qgts.append(qgt)

    qgt_i_k_ns = np.array(qgts)

    return qgt_i_k_ns



# 透過日射量[W]、吸収日射量[W]の計算 式(90)
def calc_QGT_i_k_n(
        theta_aoi_i_k: np.ndarray,
        incident_angle_characteristics_i_ks: str,
        i_inc_d_i_k_n: np.ndarray,
        FSDW_i_k_n: np.ndarray,
        i_inc_sky_i_k_n: np.ndarray,
        i_inc_ref_i_k_n: np.ndarray,
        a_i_ks: float,
        tau_i_k: float,
):

    # 室iの境界kにおける透明な開口部の拡散日射に対する基準化透過率
    c_d_i_k = a10.get_c_d_i_k(incident_angle_characteristics_i_ks=incident_angle_characteristics_i_ks)

    # 直達日射の入射角特性の計算
    taud_i_k_n = get_taud_i_k_n(
        theta_aoi_i_k=theta_aoi_i_k,
        incident_angle_characteristics_i_ks=incident_angle_characteristics_i_ks)

    # 直達成分
    QGTD_i_k_n = get_QGTD_i_k_n(
        tau_i_k=tau_i_k, i_inc_d_i_k_n=i_inc_d_i_k_n, taud_i_k_n=taud_i_k_n, F_SDW_i_k_n=FSDW_i_k_n)

    # 拡散成分
    QGTS_i_k_n = get_QGTS_i_k_n(tau_i_k, c_d_i_k, i_inc_sky_i_k_n, i_inc_ref_i_k_n)

    # 透過日射量の計算
    QGT_i_k_n = (QGTD_i_k_n + QGTS_i_k_n) * a_i_ks

    return QGT_i_k_n


# 透過日射熱取得（直達成分）[W/m2]の計算
def get_QGTD_i_k_n(
        tau_i_k: float, i_inc_d_i_k_n: np.ndarray, taud_i_k_n: np.ndarray, F_SDW_i_k_n: np.ndarray
) -> np.ndarray:

    # 透過日射熱取得（直達成分）[W/m2]の計算
    QGTD = tau_i_k * (1.0 - F_SDW_i_k_n) * taud_i_k_n * i_inc_d_i_k_n

    return QGTD


# 透過日射熱取得（拡散成分）[W/m2]の計算
def get_QGTS_i_k_n(
        T: float, Cd: float, I_S_i_k_n: np.ndarray, I_R_i_k_n: np.ndarray) -> np.ndarray:
    """
    :param I_S_i_k_n: 傾斜面入射天空日射量[W/m2]
    :param I_R_i_k_n: 傾斜面入射反射日射量[W/m2]
    :return: 透過日射熱取得（拡散成分）[W/m2]
    """
    QGTS = T * Cd * (I_S_i_k_n + I_R_i_k_n)
    return QGTS
