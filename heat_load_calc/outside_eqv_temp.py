import numpy as np

from heat_load_calc import inclined_surface_solar_radiation
from heat_load_calc.weather import Weather
from heat_load_calc.direction import Direction
from heat_load_calc.solar_shading import SolarShading
from heat_load_calc.window import Window


def get_theta_o_eqv_j_ns_for_internal(w: Weather) -> np.ndarray:
    """
    間仕切りの相当外気温度を計算する。

    Args:
        w: Weather クラス

    Returns:
        ステップnにおけるの境界jの相当外気温度, degree C, [N+1]

    Notes:
        本来であれば、間仕切り壁において相当外気温度は定義できない概念ではあるが、
        後々の numpy の行列計算において、相当外気温度を 0.0 にしておく方が都合がよいので、
        ここでは0.0に初期化することにした。
        間仕切り壁に対する外気温度の影響はゼロなので、ここで定める値は何に設定しても用いられることはなく、計算結果に影響しない。
    """

    # eq.1
    return np.zeros(w.number_of_data_plus)


def get_theta_o_eqv_j_ns_for_external_general_part_and_external_opaque_part(
        drct_j: Direction,
        a_s_j: float,
        eps_r_o_j: float,
        r_s_o_j: float,
        ssp_j: SolarShading,
        w: Weather
) -> np.ndarray:
    """
    相当外気温度を計算する。

    Args:
        drct_j: 境界jのDirectionクラス
        a_s_j: 境界jの室外側日射吸収率, -
        eps_r_o_j: 境界jの室外側長波長放射率, -
        r_s_o_j: 境界jの室外側熱伝達抵抗, m2K/W
        ssp_j: 境界jのSolarShadingPartクラス
        w: Weather クラス

    Returns:
        ステップnにおける境界jの相当外気温度, degree C, [N+1]
    Notes:
        eq.2
    """

    # ステップnにおける境界jの直達日射に対する日よけの影面積比率, -, [N+1]
    f_ss_dn_j_ns = ssp_j.get_f_ss_dn_j_ns(h_sun_ns=w.h_sun_ns_plus, a_sun_ns=w.a_sun_ns_plus)

    # ステップnにおける境界jの天空日射に対する日よけの影面積比率, -
    f_ss_sky_j_ns = ssp_j.get_f_ss_sky_j()

    # ステップnにおける境界jの地面反射日射に対する日よけの影面積比率, -
    f_ss_ref_j_ns = ssp_j.get_f_ss_ref_j()

    # ステップnにおける境界jに入射する日射量の直達成分, W/m2, [N+1]
    # ステップnにおける境界jに入射する日射量の天空成分, W/m2, [N+1]
    # ステップnにおける境界jに入射する日射量の地盤反射成分, W/m2 [N+1]
    # ステップnにおける境界jの夜間放射量, W/m2, [N+1]
    i_s_dn_j_ns, i_s_sky_j_ns, i_s_ref_j_ns, r_s_n_j_ns = inclined_surface_solar_radiation.get_i_s_j_ns(
        w=w,
        drct_j=drct_j
    )

    # ステップnにおける境界jの相当外気温度, ℃, [N+1]
    # 一般部位・不透明な開口部の場合、日射・長波長放射を考慮する。
    # eq.2
    theta_o_eqv_j_ns = w.theta_o_ns_plus + (
        a_s_j * (
            i_s_dn_j_ns * (1.0 - f_ss_dn_j_ns)
            + i_s_sky_j_ns * (1.0 - f_ss_sky_j_ns)
            + i_s_ref_j_ns * (1.0 - f_ss_ref_j_ns)
        ) - eps_r_o_j * r_s_n_j_ns
    ) * r_s_o_j

    return theta_o_eqv_j_ns


def get_theta_o_eqv_j_ns_for_external_transparent_part(
    drct_j: Direction,
    eps_r_o_j: float,
    r_s_o_j: float,
    u_j: float,
    ssp_j: SolarShading,
    wdw_j: Window,
    w: Weather
) -> np.ndarray:
    """
    透明な開口部の場合の相当外気温度を計算する。

    Args:
        w: Weather クラス
        drct_j: Direction クラス
        eps_r_o_j: 室外側長波長放射率, -
        r_s_o_j: 境界jの室外側熱伝達抵抗, m2K/W
        u_j: 境界jの熱貫流率, W/m2K
        ssp_j: SolarShading クラス
        wdw: Window クラス
        w: Weather クラス

    Returns:
        ステップnにおける境界jの相当外気温度, degree C, [N+1]
    Notes:
        eq.3~7
    """

    # ステップ n の境界 j における傾斜面に入射する太陽の入射角, rad, [n]
    phi_j_ns = inclined_surface_solar_radiation.get_phi_j_ns(
        h_sun_ns=w.h_sun_ns_plus, a_sun_ns=w.a_sun_ns_plus, drct_j=drct_j)

    # ステップnにおける境界jに入射する日射量の直達成分, W / m2, [n]
    # ステップnにおける境界jに入射する日射量の天空成分, W / m2, [n]
    # ステップnにおける境界jに入射する日射量の地盤反射成分, W / m2, [n]
    # ステップnにおける境界jの夜間放射量, W/m2, [n]
    i_s_dn_j_ns, i_s_sky_j_ns, i_s_ref_j_ns, r_s_n_j_ns = inclined_surface_solar_radiation.get_i_s_j_ns(
        w=w,
        drct_j=drct_j
    )

    # ---日よけの影面積比率

    # ステップ n における境界ｊの直達日射に対する日よけの影面積比率, [N+1]
    f_ss_d_j_ns = ssp_j.get_f_ss_dn_j_ns(h_sun_ns=w.h_sun_ns_plus, a_sun_ns=w.a_sun_ns_plus)

    # 天空日射に対する日よけの影面積比率
    f_ss_s_j_ns = ssp_j.get_f_ss_sky_j()

    # 地面反射日射に対する日よけの影面積比率
    f_ss_r_j_ns = ssp_j.get_f_ss_ref_j()

    # ステップ n における境界ｊの開口部の直達日射に対する吸収日射熱取得率, -, [N+1]
    # b_w_d_j_ns = window.get_alpha_w_j_n(phi_ns=theta_aoi_j_ns)
    b_w_d_j_ns = wdw_j.get_b_w_d_j_ns(phi_j_ns=phi_j_ns)

    # 境界 ｊ　の開口部の天空日射に対する吸収日射熱取得率, -
    # b_w_s_j = window.alpha_w_s_j
    b_w_s_j = wdw_j.b_w_s_j

    # 境界 ｊ　の開口部の地盤反射日射に対する吸収日射熱取得率, -
    # b_w_r_j = window.alpha_w_r_j
    b_w_r_j = wdw_j.b_w_r_j

    # 直達日射に起因する吸収日射熱取得量, W/m2, [N+1]
    # eq.5
    q_b_dn_j_ns = b_w_d_j_ns * (1.0 - f_ss_d_j_ns) * i_s_dn_j_ns

    # 天空日射に起因する吸収日射熱取得量, W/m2, [N+1]
    # eq.6
    q_b_sky_j_ns = b_w_s_j * (1.0 - f_ss_s_j_ns) * i_s_sky_j_ns

    # 地盤反射日射に起因する吸収日射熱取得量, W/m2, [N+1]
    # eq.7
    q_b_ref_j_ns = b_w_r_j * (1.0 - f_ss_r_j_ns) * i_s_ref_j_ns

    # 吸収日射熱取得量, W/m2, [N+1]
    # eq.4
    q_b_all_j_ns = (q_b_dn_j_ns + q_b_sky_j_ns + q_b_ref_j_ns)

    # 室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [N+1]
    # 透明な開口部の場合、透過日射はガラス面への透過の項で扱うため、ここでは吸収日射、長波長放射のみ考慮する。
    # eq.3
    return w.theta_o_ns_plus - eps_r_o_j * r_s_n_j_ns * r_s_o_j + q_b_all_j_ns / u_j


def get_theta_o_eqv_j_ns_for_external_not_sun_striked(w: Weather) -> np.ndarray:
    """
    日射があたっていない場合の外皮の相当外気温度を計算する。

    Args:
        w: Weather クラス

    Returns:
        ステップnにおける境界jの相当外気温度, degree C, [N+1]
    Notes:
        eq.8
    """

    return w.theta_o_ns_plus


def get_theta_o_eqv_j_ns_for_ground(w: Weather) -> np.ndarray:
    """地盤の相当外気温度を計算する。

    Args:
        w: Weather クラス

    Returns:
        ステップ n における室 i の境界 j の傾斜面の相当外気温度, ℃, [N+1]
    """

    return np.full(w.number_of_data_plus, w.get_theta_o_ave())
