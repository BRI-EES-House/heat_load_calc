import numpy as np
from apdx10_oblique_incidence_characteristics import get_taud_i_k_n
import apdx6_direction_cos_incident_angle as a6
import a7_inclined_surface_solar_radiation as a7
import apdx10_oblique_incidence_characteristics as a10
import a18_initial_value_constants as a18
import a19_external_surfaces as a19

"""
付録11．窓の透過日射熱取得の計算
"""


def test(
        n,
        IAC_i_k,
        FSDW_i_k_n: np.ndarray,
        A_i_k,
        tau_i_k,
        I_DN_n,
        I_sky_n,
        direction_i_ks,
        h_s_n,
        a_s_n
):
    """

    Args:
        n: 境界数
        IAC_i_k: 室iの境界kのガラスの入射角特性タイプ（境界数）
        FSDW_i_k_n: 日影面積率の計算（境界数　✕　ステップn）
        A_i_k: 面積（境界数）
        tau_i_k: 室iの境界kの日射熱取得率（境界数）
        I_DN_n: 直達日射（ステップn）
        I_sky_n: 天空放射（ステップn）
        direction_i_ks:方位 （境界数）
        h_s_n: 太陽高度
        a_s_n: 太陽方位角
    Returns:

    """

    # a_sun_sin_n: sin
    # a（ステップn)
    # a_sun_cos_n: cos
    # a（ステップn)
    a_sun_sin_n = np.where(h_s_n > 0.0, np.sin(a_s_n), 0.0)
    a_sun_cos_n = np.where(h_s_n > 0.0, np.cos(a_s_n), 0.0)

    # h_sun_sin_n: sin
    # h（ステップn)
    # h_sun_cos_n: cos
    # h（ステップn)
    h_sun_sin_n = np.where(h_s_n > 0.0, np.sin(h_s_n), 0.0)
    h_sun_cos_n = np.where(h_s_n > 0.0, np.cos(h_s_n), 1.0)

    # 方位角、傾斜面方位角 [rad]
    # w_alpha_k: 方位角（境界数）
    # w_beta_k: 傾斜角（境界数）
    w_alpha_k, w_beta_k = a19.get_slope_angle(direction_i_ks)


    # 傾斜面に関する変数であり、式(73)
    Wz_i_k, _, _ = \
        a19.get_slope_angle_intermediate_variables(w_alpha_k, w_beta_k)

    # 傾斜面の天空に対する形態係数の計算 式(120)
    # PhiS_i_k: 傾斜面の天空に対する形態係数の計算
    # 式(120)（境界数）
    PhiS_i_k = a19.get_Phi_S_i_k(Wz_i_k)

    # 傾斜面の地面に対する形態係数 式(119)
    # PhiG_i_k: 傾斜面の地面に対する形態係数
    # 式(119)（境界数）
    PhiG_i_k = a19.get_Phi_G_i_k(PhiS_i_k)

    # 地面反射率[-]
    # RhoG_l: 地面反射率[-]（境界数）
    RhoG_l = np.full(n, a18.get_RhoG())

    # 拡散日射の入射角特性
    # Cd_i_k: 拡散日射の入射角特性の計算（境界数）
    Cd_i_k = a10.get_Cd(IAC_i_k)

    # cos_Theta_i_k_n: 時刻nにおける入射角の方向余弦（境界数　✕　ステップn）
    cos_Theta_i_k_n = a6.calc_cos_incident_angle(
        h_sun_sin_n=h_sun_sin_n,
        h_sun_cos_n=h_sun_cos_n,
        a_sun_sin_n=a_sun_sin_n,
        a_sun_cos_n=a_sun_cos_n,
        w_alpha_k=w_alpha_k,
        w_beta_k=w_beta_k
    )

    # I_D_i_k_n: 傾斜面天空日射量, W / m2K（境界数　✕　ステップn）
    # I_S_i_k_n: 傾斜面反射日射量, W / m2K（境界数　✕　ステップn）
    # I_R_i_k_n: 傾斜面日射量の合計, W / m2K（境界数　✕　ステップn）
    _, I_D_i_k_n, I_S_i_k_n, I_R_i_k_n = a7.calc_slope_sol(
        I_DN_n=I_DN_n,
        I_sky_n=I_sky_n,
        Sh_n=h_sun_sin_n,
        cos_Theta_i_k_n=cos_Theta_i_k_n,
        PhiS_i_k=PhiS_i_k,
        PhiG_i_k=PhiG_i_k,
        RhoG_l=RhoG_l
    )

    return calc_QGT_i_k_n(
        cos_Theta_i_k_n,
        IAC_i_k,
        I_D_i_k_n,
        FSDW_i_k_n,
        I_S_i_k_n,
        I_R_i_k_n,
        A_i_k,
        tau_i_k,
        Cd_i_k
)

# 透過日射量[W]、吸収日射量[W]の計算 式(90)
def calc_QGT_i_k_n(
        cos_Theta_i_k_n: np.ndarray,
        IAC_i_k,
        I_D_i_k_n: np.ndarray,
        FSDW_i_k_n: np.ndarray,
        I_S_i_k_n: np.ndarray,
        I_R_i_k_n: np.ndarray,
        A_i_k,
        tau_i_k,
        Cd_i_k
):

    # 直達日射の入射角特性の計算
    taud_i_k_n = get_taud_i_k_n(cos_Theta_i_k_n, IAC_i_k)

    # 直達成分
    QGTD_i_k_n = get_QGTD_i_k_n(tau_i_k, I_D_i_k_n, taud_i_k_n, FSDW_i_k_n)

    # 拡散成分
    QGTS_i_k_n = get_QGTS_i_k_n(tau_i_k, Cd_i_k, I_S_i_k_n, I_R_i_k_n)

    # 透過日射量の計算
    QGT_i_k_n = (QGTD_i_k_n + QGTS_i_k_n) * A_i_k[:,np.newaxis]

    return QGT_i_k_n


# 透過日射熱取得（直達成分）[W/m2]の計算
def get_QGTD_i_k_n(T, I_D_i_k_n: np.ndarray, CID: np.ndarray, F_SDW_i_k: np.ndarray) -> np.ndarray:
    """
    :param I_D_i_k_n: 傾斜面入射直達日射量[W/m2]
    :param CID: 直達日射の入射角特性
    :param F_SDW_i_k: 日よけ等による日影面積率
    :return: 透過日射熱取得（直達成分）[W/m2]
    """
    # 透過日射熱取得（直達成分）[W/m2]の計算
    QGTD = T[:,np.newaxis] * (1.0 - F_SDW_i_k) * CID * I_D_i_k_n

    return QGTD


# 透過日射熱取得（拡散成分）[W/m2]の計算
def get_QGTS_i_k_n(T: float, Cd: np.ndarray, I_S_i_k_n: np.ndarray, I_R_i_k_n: np.ndarray) -> np.ndarray:
    """
    :param I_S_i_k_n: 傾斜面入射天空日射量[W/m2]
    :param I_R_i_k_n: 傾斜面入射反射日射量[W/m2]
    :return: 透過日射熱取得（拡散成分）[W/m2]
    """
    QGTS = T[:,np.newaxis] * Cd[:,np.newaxis] * (I_S_i_k_n + I_R_i_k_n)
    return QGTS
