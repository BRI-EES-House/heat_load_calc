import numpy as np

from heat_load_calc import inclined_surface_solar_radiation
from heat_load_calc.weather import Weather
from heat_load_calc.direction import Direction
from heat_load_calc.solar_shading import SolarShading
from heat_load_calc.window import Window


def get_q_trs_sol_j_ns_for_not(w: Weather) -> np.ndarray:
    """「透明な開口部」以外の境界又は「透明な開口部」であって日射が当たらない場合のステップnにおける境界jの透過日射量を計算する。
    Args:
        w: Weather Class
    Returns:
        ステップnにおける境界jの透過日射量, W, [N+1]
    """

    return np.zeros(w.number_of_data_plus, dtype=float)


def get_q_trs_sol_j_ns_for_transparent_sun_striked(
        drct_j: Direction,
        a_s_j: float,
        ssp_j: SolarShading,
        wdw_j: Window,
        w: Weather
) -> np.ndarray:
    """

    Args:
        drct_j: 境界jの Direction Class
        a_s_j: 境界jの面積, m2
        ssp_j: 境界jの SolarShadingPart Class
        wdw_j: 境界jの Window Class
        w: Weather Class
    Returns:
        ステップnにおける境界jの透過日射量, W, [N+1]
    """

    # ステップnにおける境界jの傾斜面に入射する太陽の入射角, rad, [N+1]
    phi_j_ns = inclined_surface_solar_radiation.get_phi_j_ns(
        h_sun_ns=w.h_sun_ns_plus, a_sun_ns=w.a_sun_ns_plus, direction=drct_j)

    # ステップnにおける境界jの傾斜面に入射する日射量のうち直達成分, W/m2 [N+1]
    # ステップnにおける境界jの傾斜面に入射する日射量のうち天空成分, W/m2 [N+1]
    # ステップnにおける境界jの傾斜面に入射する日射量のうち地盤反射成分, W/m2 [N+1]
    # ステップnにおける境界jの傾斜面の夜間放射量, W/m2, [N+1]
    i_s_dn_j_ns, i_s_sky_j_ns, i_s_ref_j_ns, _ = inclined_surface_solar_radiation.get_i_s_j_ns(
        i_dn_ns=w.i_dn_ns_plus,
        i_sky_ns=w.i_sky_ns_plus,
        r_n_ns=w.r_n_ns_plus,
        h_sun_ns=w.h_sun_ns_plus,
        a_sun_ns=w.a_sun_ns_plus,
        w=w,
        drct_j=drct_j
    )

    # ---日よけの影面積比率

    # ステップnにおける境界jの直達日射に対する日よけの影面積比率, [N+1]
    f_ss_d_j_ns = ssp_j.get_f_ss_dn_j_ns(h_sun_ns=w.h_sun_ns_plus, a_sun_ns=w.a_sun_ns_plus)

    # ステップnにおける境界jの天空日射に対する日よけの影面積比率
    f_ss_s_j_ns = ssp_j.get_f_ss_sky_j()

    # ステップnにおける境界jの地面反射日射に対する日よけの影面積比率
    f_ss_r_j_ns = ssp_j.get_f_ss_ref_j()

    # ステップnにおける境界jの窓の直達日射に対する日射透過率, -, [N+1]
    tau_w_d_j_ns = wdw_j.get_tau_w_d_j_ns(phi_j_ns=phi_j_ns)

    # 境界jの窓の天空日射に対する日射透過率, -
    tau_w_s_j = wdw_j.tau_w_s_j

    # 境界jの窓の地盤反射日射に対する日射透過率, -
    tau_w_r_j = wdw_j.tau_w_r_j

    # ステップnにおける境界jの直達日射に対する単位面積当たりの透過日射量, W/m2, [N+1]
    q_trs_sol_dn_j_ns = tau_w_d_j_ns * (1.0 - f_ss_d_j_ns) * i_s_dn_j_ns

    # ステップnにおける境界jの天空日射に対する単位面積当たりの透過日射量, W/m2, [N+1]
    q_trs_sol_sky_j_ns = tau_w_s_j * (1.0 - f_ss_s_j_ns) * i_s_sky_j_ns

    # ステップnにおける境界jの地盤反射日射に対する単位面積当たりの透過日射量, W/m2, [N+1]
    q_trs_sol_ref_j_ns = tau_w_r_j * (1.0 - f_ss_r_j_ns) * i_s_ref_j_ns

    # ステップnにおける境界jの透過日射量, W, [N+1]
    q_trs_sol_j_ns = (q_trs_sol_dn_j_ns + q_trs_sol_sky_j_ns + q_trs_sol_ref_j_ns) * a_s_j

    return q_trs_sol_j_ns
