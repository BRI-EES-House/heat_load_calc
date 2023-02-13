import numpy as np

from heat_load_calc import inclined_surface_solar_radiation
from heat_load_calc.weather import Weather
from heat_load_calc.direction import Direction
from heat_load_calc.solar_shading import SolarShading
from heat_load_calc.window import Window


def get_qgt_for_not(w: Weather) -> np.ndarray:
    """
    透過日射量を計算する。

    Args:
        w:  Weather クラス

    Returns:
        透過日射量, W, [N+1]
    """

    return np.zeros(w.number_of_data_plus, dtype=float)


def get_qgt_for_transparent_sun_strike(
        direction: Direction,
        area: float,
        ss: SolarShading,
        window: Window,
        w: Weather
) -> np.ndarray:
    """

    Args:
        direction: 境界が面する方位
        area: 面積, m2
        ss: 日よけの仕様（SolarShadingPartクラス）
        window: Windowクラス
        w: Weather クラス

    Returns:
        透過日射量, W, [N+1]

    """

    # ステップ n における境界 j の傾斜面に入射する太陽の入射角, rad, [N+1]
    phi_j_ns = inclined_surface_solar_radiation.get_theta_aoi_j_ns(
        h_sun_ns=w.h_sun_ns_plus, a_sun_ns=w.a_sun_ns_plus, direction=direction)

    # ステップ n における境界 j の傾斜面に入射する日射量のうち直達成分, W/m2 [N+1]
    # ステップ n における境界 j の傾斜面に入射する日射量のうち天空成分, W/m2 [N+1]
    # ステップ n における境界 j の傾斜面に入射する日射量のうち地盤反射成分, W/m2 [N+1]
    # ステップ n における境界 j の傾斜面の夜間放射量, W/m2, [N+1]
    i_s_dn_j_ns, i_s_sky_j_ns, i_s_ref_j_ns, r_s_eff_j_ns = inclined_surface_solar_radiation.get_i_is_j_ns(
        i_dn_ns=w.i_dn_ns_plus,
        i_sky_ns=w.i_sky_ns_plus,
        r_n_ns=w.r_n_ns_plus,
        h_sun_ns=w.h_sun_ns_plus,
        a_sun_ns=w.a_sun_ns_plus,
        drct_j=direction
    )

    # ---日よけの影面積比率

    # 直達日射に対する日よけの影面積比率, [N+1]
    f_ss_d_j_ns = ss.get_f_ss_dn_j_ns(h_sun_n=w.h_sun_ns_plus, a_sun_n=w.a_sun_ns_plus)

    # 天空日射に対する日よけの影面積比率
    f_ss_s_j_ns = ss.get_f_ss_sky_j()

    # 地面反射日射に対する日よけの影面積比率
    f_ss_r_j_ns = ss.get_f_ss_ref_j()

    # ステップnにおける境界jの窓の直達日射に対する日射透過率, -, [N+1]
    tau_w_d_j_ns = window.get_tau_w_d_j_ns(phi_j_ns=phi_j_ns)

    # 境界jの窓の天空日射に対する日射透過率, -
    tau_w_s_j = window.tau_w_s_j

    # 境界jの窓の地盤反射日射に対する日射透過率, -
    tau_w_r_j = window.tau_w_r_j

    # 直達日射に対する透過日射量, W/m2, [N+1]
    q_gt_d_j_ns = tau_w_d_j_ns * (1.0 - f_ss_d_j_ns) * i_s_dn_j_ns

    # 天空日射に対する透過日射量, W/m2, [N+1]
    q_gt_sky_j_ns = tau_w_s_j * (1.0 - f_ss_s_j_ns) * i_s_sky_j_ns

    # 地盤反射日射に対する透過日射量, W/m2, [N+1]
    q_gt_ref_j_ns = tau_w_r_j * (1.0 - f_ss_r_j_ns) * i_s_ref_j_ns

    # 透過日射量, W, [N+1]
    q_gt_ns = (q_gt_d_j_ns + q_gt_sky_j_ns + q_gt_ref_j_ns) * area

    return q_gt_ns
