import numpy as np

from heat_load_calc import inclined_surface_solar_radiation
from heat_load_calc.weather import Weather
from heat_load_calc.direction import Direction
from heat_load_calc.solar_shading import SolarShading
from heat_load_calc.window import Window


def get_theta_o_sol_i_j_ns_for_internal(w: Weather) -> np.ndarray:
    """
    間仕切りの相当外気温度を計算する。

    Args:
        w: Weather クラス

    Returns:
        ステップ n における室 i の境界 j の傾斜面の相当外気温度, degree C, [N+1]

    Notes:
        本来であれば、間仕切り壁において相当外気温度は定義できない概念ではあるが、
        後々の numpy の行列計算において、相当外気温度を 0.0 にしておく方が都合がよいので、
        ここでは0.0に初期化することにした。
        間仕切り壁に対する外気温度の影響はゼロなので、ここで定める値は何に設定しても用いられることはなく、計算結果に影響しない。
    """

    return np.zeros(w.number_of_data_plus)


def get_theta_o_sol_i_j_ns_for_external_general_part_and_external_opaque_part(
        direction: Direction,
        a_s: float,
        eps_r: float,
        r_surf: float,
        ss: SolarShading,
        w: Weather
) -> np.ndarray:
    """
    相当外気温度を計算する。

    Args:
        direction: Direction クラス
        a_s: 室外側日射吸収率, -
        eps_r: 室外側長波長放射率, -
        r_surf: 室外側熱伝達抵抗, m2K/W
        w: OutdoorCondition クラス

    Returns:
        ステップ n における室 i の境界 j の傾斜面の相当外気温度, degree C, [N+1]
    """

    # 直達日射に対する日よけの影面積比率, [8760 * 4]
    f_ss_d_j_ns = ss.get_f_ss_d_j_ns(h_sun_n=w.h_sun_ns_plus, a_sun_n=w.a_sun_ns_plus)

    # 天空日射に対する日よけの影面積比率
    f_ss_s_j_ns = ss.get_f_ss_s_j()

    # 地面反射日射に対する日よけの影面積比率
    f_ss_r_j_ns = 0.0

    # ステップ n における境界 j の傾斜面に入射する日射量の直達成分, W/m2 [n]
    # ステップ n における境界 j の傾斜面に入射する日射量の天空成分, W/m2 [n]
    # ステップ n における境界 j の傾斜面に入射する日射量の地盤反射成分, W/m2 [n]
    # ステップ n における境界 j の傾斜面の夜間放射量, W/m2, [n]
    i_is_d_j_ns, i_is_sky_j_ns, i_is_ref_j_ns, r_srf_eff_j_ns = inclined_surface_solar_radiation.get_i_is_j_ns(
        i_dn_ns=w.i_dn_ns_plus,
        i_sky_ns=w.i_sky_ns_plus,
        r_eff_ns=w.r_n_ns_plus,
        h_sun_ns=w.h_sun_ns_plus,
        a_sun_ns=w.a_sun_ns_plus,
        direction=direction
    )

    # 室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [8760*4]
    # 一般部位・不透明な開口部の場合、日射・長波長放射を考慮する。
    theta_o_sol_i_j_ns = w.theta_o_ns_plus + (
        a_s * (
            i_is_d_j_ns * (1.0 - f_ss_d_j_ns)
            + i_is_sky_j_ns * (1.0 - f_ss_s_j_ns)
            + i_is_ref_j_ns * (1.0 - f_ss_r_j_ns)
        ) - eps_r * r_srf_eff_j_ns
    ) * r_surf

    return theta_o_sol_i_j_ns


def get_theta_o_sol_i_j_ns_for_external_not_sun_striked(w: Weather) -> np.ndarray:
    """
    日射があたっていない場合の外皮の相当外気温度を計算する。

    Args:
        w: Weather クラス

    Returns:
        ステップ n における室 i の境界 j の傾斜面の相当外気温度, degree C, [N+1]
    """

    return w.theta_o_ns_plus


def get_theta_o_sol_i_j_ns_for_external_transparent_part(
        direction: Direction,
        eps_r,
        r_surf_o,
        u_value_j: float,
        ss: SolarShading,
        window: Window,
        w: Weather
) -> np.ndarray:
    """
    相当外気温度を計算する。

    Args:
        w: Weather クラス
        direction: Direction クラス
        eps_r: 室外側長波長放射率, -
        r_surf_o:
        u_value_j:
        ss: SolarShading クラス
        window: Window クラス
        w: Weather クラス

    Returns:
        ステップ n における室 i の境界 j の傾斜面の相当外気温度, degree C, [N+1]
    """

    # ステップ n の境界 j における傾斜面に入射する太陽の入射角, rad, [n]
    theta_aoi_j_ns = inclined_surface_solar_radiation.get_theta_aoi_j_ns(
        h_sun_ns=w.h_sun_ns_plus, a_sun_ns=w.a_sun_ns_plus, direction=direction)

    # ステップ n における境界 j の傾斜面に入射する日射量の直達成分, W / m2, [n]
    # ステップ n における境界 j の傾斜面に入射する日射量の天空成分, W / m2, [n]
    # ステップ n における境界 j の傾斜面に入射する日射量の地盤反射成分, W / m2, [n]
    # ステップ n における境界 j の傾斜面の夜間放射量, W/m2, [n]
    i_inc_d_j_ns, i_inc_sky_j_ns, i_inc_ref_j_ns, r_srf_eff_j_ns = inclined_surface_solar_radiation.get_i_is_j_ns(
        i_dn_ns=w.i_dn_ns_plus,
        i_sky_ns=w.i_sky_ns_plus,
        r_eff_ns=w.r_n_ns_plus,
        h_sun_ns=w.h_sun_ns_plus,
        a_sun_ns=w.a_sun_ns_plus,
        direction=direction
    )

    # ---日よけの影面積比率

    # 直達日射に対する日よけの影面積比率, [N+1]
    f_ss_d_j_ns = ss.get_f_ss_d_j_ns(h_sun_n=w.h_sun_ns_plus, a_sun_n=w.a_sun_ns_plus)

    # 天空日射に対する日よけの影面積比率
    f_ss_s_j_ns = ss.get_f_ss_s_j()

    # 地面反射日射に対する日よけの影面積比率
    f_ss_r_j_ns = ss.get_f_ss_r_j()

    # ステップ n における境界 ｊ　の開口部の直達日射に対する吸収日射熱取得率, -, [N+1]
    # b_w_d_j_ns = window.get_alpha_w_j_n(phi_ns=theta_aoi_j_ns)
    b_w_d_j_ns = window.get_b_w_j_n(phi_ns=theta_aoi_j_ns)

    # 境界 ｊ　の開口部の天空日射に対する吸収日射熱取得率, -
    # b_w_s_j = window.alpha_w_s_j
    b_w_s_j = window.b_w_s_j

    # 境界 ｊ　の開口部の地盤反射日射に対する吸収日射熱取得率, -
    # b_w_r_j = window.alpha_w_r_j
    b_w_r_j = window.b_w_r_j

    # 直達日射に対する吸収日射熱取得, W/m2, [N+1]
    q_gt_d_j_ns = b_w_d_j_ns * (1.0 - f_ss_d_j_ns) * i_inc_d_j_ns

    # 天空日射に対する吸収日射熱取得, W/m2, [N+1]
    q_gt_sky_j_ns = b_w_s_j * (1.0 - f_ss_s_j_ns) * i_inc_sky_j_ns

    # 地盤反射日射に対する吸収日射熱取得, W/m2, [N+1]
    q_gt_ref_j_ns = b_w_r_j * (1.0 - f_ss_r_j_ns) * i_inc_ref_j_ns

    # 吸収日射熱取得, W/m2, [N+1]
    q_ga_ns = (q_gt_d_j_ns + q_gt_sky_j_ns + q_gt_ref_j_ns)

    # 室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [N+1]
    # 透明な開口部の場合、透過日射はガラス面への透過の項で扱うため、ここでは吸収日射、長波長放射のみ考慮する。
    return w.theta_o_ns_plus - eps_r * r_srf_eff_j_ns * r_surf_o + q_ga_ns / u_value_j


def get_theta_o_sol_i_j_ns_for_ground(w: Weather) -> np.ndarray:
    """地盤の相当外気温度を計算する。

    Args:
        w: Weather クラス

    Returns:
        ステップ n における室 i の境界 j の傾斜面の相当外気温度, ℃, [N+1]
    """

    return np.full(w.number_of_data_plus, w.get_theta_o_ns_average())
