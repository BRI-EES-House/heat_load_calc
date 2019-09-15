import numpy as np
from apdx10_oblique_incidence_characteristics import get_taud_i_k_n

"""
付録11．窓の透過日射熱取得の計算
"""


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
    QGT_i_k_n = (QGTD_i_k_n + QGTS_i_k_n) * A_i_k

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
    QGTD = T * (1.0 - F_SDW_i_k) * CID * I_D_i_k_n

    return QGTD


# 透過日射熱取得（拡散成分）[W/m2]の計算
def get_QGTS_i_k_n(T: float, Cd: np.ndarray, I_S_i_k_n: np.ndarray, I_R_i_k_n: np.ndarray) -> np.ndarray:
    """
    :param I_S_i_k_n: 傾斜面入射天空日射量[W/m2]
    :param I_R_i_k_n: 傾斜面入射反射日射量[W/m2]
    :return: 透過日射熱取得（拡散成分）[W/m2]
    """
    QGTS = T * Cd * (I_S_i_k_n + I_R_i_k_n)
    return QGTS


# 透過日射を集約する
""" def summarize_transparent_solar_radiation(surfaces, calc_time_interval, weather):
    # 透過日射熱取得収録配列の初期化とメモリ確保
    QGT_i_n = []
    QGT_i_n = [0.0 for j in range(int(8760.0 * 3600.0 / float(calc_time_interval)))]

    ntime = int(24 * 3600 / calc_time_interval)
    nnow = 0
    item = 0
    start_date = datetime.datetime(1989, 1, 1)
    for nday in range(get_nday(1, 1), get_nday(12, 31) + 1):
        for tloop in range(ntime):
            dtime = datetime.timedelta(days=nnow + float(tloop) / float(ntime))
            dtmNow = dtime + start_date

            # 太陽位置の計算
            solar_position = calc_solar_position(weather, dtmNow)
            # 傾斜面日射量の計算
            I_DN = WeaData(weather, enmWeatherComponent.I_DN, dtmNow, solar_position)
            I_sky = WeaData(weather, enmWeatherComponent.I_sky, dtmNow, solar_position)
            for surface in surfaces:
                # 外表面に日射が当たる場合
                if surface.is_sun_striked_outside and surface.boundary_type == "external_transparent_part":
                    sin_h_s = solar_position.sin_h_s
                    cos_h_s = solar_position.cos_h_s
                    sin_a_s = solar_position.sin_a_s
                    cos_a_s = solar_position.cos_a_s
                    wa = surface.backside_boundary_condition.w_alpha_i_k
                    wb = surface.backside_boundary_condition.w_beta_i_k

                    if 'external' in surface.backside_boundary_condition.Type and surface.backside_boundary_condition.is_sun_striked_outside:
                        cos_t = calc_cos_incident_angle(sin_h_s, cos_h_s, sin_a_s, cos_a_s, wa, wb)
                        surface.backside_boundary_condition.cos_Theta_i_g_n = cos_t
                        Fs = surface.backside_boundary_condition.Fs
                        dblFg = surface.backside_boundary_condition.dblFg
                        Rg = surface.backside_boundary_condition.Rg
                        surface.I_D_i_k_n, surface.I_sky, surface.I_R_i_k_n, surface.Iw_i_k_n = calc_slope_sol(
                            I_DN, I_sky, sin_h_s, cos_t, Fs, dblFg, Rg)
                    else:
                        surface.backside_boundary_condition.cos_Theta_i_g_n = 0.0
                        surface.I_D_i_k_n, surface.I_sky, surface.I_R_i_k_n, surface.Iw_i_k_n = 0.0, 0.0, 0.0, 0.0


                    # 日除けの日影面積率の計算
                    if surface.sunbrk.existance:
                        surface.FSDW_i_k_n = calc_F_SDW_i_k_n(surface, solar_position)
                    QGT_i_n[item] += calc_QGT_i_n(surface)

            item += 1
        nnow += 1
    return QGT_i_n """