import numpy as np

"""
付録7．傾斜面日射量
"""


def get_i_inc_i_k_n(
        i_dn_ns: np.ndarray, i_sky_ns: np.ndarray, h_sun_ns: np.ndarray, a_sun_ns,
        w_alpha_i_k: float, w_beta_i_k: float) -> (float, float, float, float):
    """
    Args:
        i_dn_ns: ステップnにおける法線面直達日射量, W/m2K
        i_sky_ns: ステップnにおける水平面天空日射量, W/m2K
        h_sun_ns: ステップnにおける太陽高度, rad
        a_sun_ns: ステップnにおける太陽方位角, rad
        w_alpha_i_k: 室iの境界kの傾斜面の方位角, rad
        w_beta_i_k: 室iの境界kの傾斜面の傾斜角, rad
    Returns:
        以下のタプル
            (1) ステップnにおける室iの境界kにおける傾斜面の日射量, W/m2K
            (2) ステップnにおける室iの境界kにおける傾斜面の日射量のうち直達成分, W/m2K
            (3) ステップnにおける室iの境界kにおける傾斜面の日射量のうち天空成分, W/m2K
            (4) ステップnにおける室iの境界kにおける傾斜面の日射量のうち地盤反射成分, W/m2K
    """

    # ステップnの室iの境界kにおける傾斜面に入射する太陽の入射角 * 365 * 24 * 4
    theta_aoi_i_k_n = get_theta_aoi_i_k_n(
        w_alpha_i_k=w_alpha_i_k,
        w_beta_i_k=w_beta_i_k,
        h_sun_ns=h_sun_ns,
        a_sun_ns=a_sun_ns
    )

    # 室iの境界kの傾斜面の天空に対する形態係数
    f_sky_i_k = get_f_sky_i_k(w_beta_i_k)

    # 室iの境界kの傾斜面の地面に対する形態係数
    f_gnd_i_k = get_f_gnd_i_k(f_sky_i_k)

    # 地面の日射に対する反射率（アルベド）
    rho_gnd_i_k = get_rho_gnd()

    # ステップnにおける室iの境界kにおける傾斜面の日射量のうち地盤反射成分, W/m2K
    i_inc_ref_i_k_n = get_i_inc_ref_i_k_n(
        i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, f_gnd_i_k=f_gnd_i_k, rho_gnd_i_k=rho_gnd_i_k, h_sun_ns=h_sun_ns)

    # ステップnにおける室iの境界kにおける傾斜面の日射量のうち天空成分, W/m2K
    i_inc_sky_i_k_n = get_i_inc_sky_i_k_n(i_sky_ns=i_sky_ns, f_sky_i_k=f_sky_i_k)

    # ステップnにおける室iの境界kにおける傾斜面の日射量のうち拡散日射成分, W/m2K
    i_inc_dif_i_k_n = get_i_inc_dif_i_k_n(i_inc_sky_i_k_n=i_inc_sky_i_k_n, i_inc_ref_i_k_n=i_inc_ref_i_k_n)

    # ステップnにおける室iの境界kにおける傾斜面の日射量のうち直達成分, W/m2K
    i_inc_d_i_k_n = get_i_inc_d_i_k_n(i_dn_ns=i_dn_ns, theta_aoi_i_k_n=theta_aoi_i_k_n)

    # ステップnにおける室iの境界kにおける傾斜面の日射量, W/m2K
    i_inc_i_k_n_all = get_i_inc_i_k_n_all(i_inc_d_i_k_n=i_inc_d_i_k_n, i_inc_dif_i_k_n=i_inc_dif_i_k_n)

    return i_inc_i_k_n_all, i_inc_d_i_k_n, i_inc_sky_i_k_n, i_inc_ref_i_k_n


def get_i_inc_i_k_n_all(i_inc_d_i_k_n: np.ndarray, i_inc_dif_i_k_n: np.ndarray) -> np.ndarray:
    """
        傾斜面の日射量を計算する。
    Args:
        i_inc_d_i_k_n: ステップnにおける室iの境界kにおける傾斜面の日射量のうち直達成分, W/m2K
        i_inc_dif_i_k_n: ステップnにおける室iの境界kにおける傾斜面の日射量のうち拡散日射成分, W/m2K

    Returns:
        ステップnにおける室iの境界kにおける傾斜面の日射量, W/m2K
    """

    i_inc_i_k_n_all = i_inc_d_i_k_n + i_inc_dif_i_k_n

    return i_inc_i_k_n_all


def get_i_inc_d_i_k_n(i_dn_ns: np.ndarray, theta_aoi_i_k_n: np.ndarray) -> np.ndarray:
    """
        傾斜面の日射量のうち直達成分を求める。
    Args:
        i_dn_ns: ステップnにおける法線面直達日射量, W/m2K
        theta_aoi_i_k_n: ステップnの室iの境界kのにおける傾斜面に入射する太陽の入射角

    Returns:
        ステップnにおける室iの境界kにおける傾斜面の日射量のうち直達成分, W/m2K
    """

    i_inc_d_i_k_n = i_dn_ns * np.cos(theta_aoi_i_k_n)

    return i_inc_d_i_k_n


def get_i_inc_dif_i_k_n(i_inc_sky_i_k_n: np.ndarray, i_inc_ref_i_k_n: np.ndarray) -> np.ndarray:
    """
    傾斜面の日射量のうち拡散日射成分を計算する。

    Args:
        i_inc_sky_i_k_n: ステップnにおける室iの境界kにおける傾斜面の日射量のうち天空成分, W/m2K
        i_inc_ref_i_k_n: ステップnにおける室iの境界kにおける傾斜面の日射量のうち地盤反射成分, W/m2K

    Returns:
        ステップnにおける室iの境界kにおける傾斜面の日射量のうち拡散日射成分, W/m2K
    """

    i_inc_dif_i_k_n = i_inc_sky_i_k_n + i_inc_ref_i_k_n

    return i_inc_dif_i_k_n


def get_i_inc_sky_i_k_n(i_sky_ns: np.ndarray, f_sky_i_k: float) -> np.ndarray:
    """
    傾斜面の日射量のうち天空成分を計算する。

    Args:
        i_sky_ns: ステップnにおける水平面天空日射量, W/m2K
        f_sky_i_k: 室iの境界kにおける天空に対する傾斜面の形態係数

    Returns:
        ステップnにおける室iの境界kにおける傾斜面の日射量のうち天空成分, W/m2K
    """

    i_inc_sky_i_k_n = f_sky_i_k * i_sky_ns

    return i_inc_sky_i_k_n


def get_i_inc_ref_i_k_n(
        i_dn_ns: np.ndarray, i_sky_ns: np.ndarray, f_gnd_i_k: float, rho_gnd_i_k: float, h_sun_ns: np.ndarray
) -> np.ndarray:
    """
    傾斜面の日射量のうち地盤反射成分を求める。

    Args:
        i_dn_ns: ステップnにおける法線面直達日射量, W/m2K
        i_sky_ns: ステップnにおける水平面天空日射量, W/m2K
        f_gnd_i_k: 室iの境界kにおける地面に対する傾斜面の形態係数
        rho_gnd_i_k: 室iの境界kにおける地面の日射反射率
        h_sun_ns: ステップnにおける太陽高度, rad
    Returns:
        ステップnにおける室iの境界kにおける傾斜面の日射量のうち地盤反射成分, W / m2K
    """

    # ステップnにおける太陽高度の正弦
    # この値がゼロを下回る場合（太陽が地面に隠れている場合）はゼロとおく。
    sin_h_sun_ns = np.where(h_sun_ns > 0.0, np.sin(h_sun_ns), 0.0)

    # ステップnにおける水平面全天日射量, W/m2K
    i_hsr_ns = sin_h_sun_ns * i_dn_ns + i_sky_ns

    i_inc_ref_i_k_n = f_gnd_i_k * rho_gnd_i_k * i_hsr_ns

    return i_inc_ref_i_k_n


def get_f_sky_i_k(w_beta_i_k: float) -> float:
    """
    傾斜面の天空に対する形態係数を計算する。

    Args:
        w_beta_i_k: 室iの境界kの傾斜面の傾斜角, rad

    Returns:
        室iの境界kの傾斜面の天空に対する形態係数

    Notes:
        室iの境界kの傾斜面の傾斜角 は水平面を0°とし、垂直面を90°とし、
        オーバーハング床等における下に向いた面は180°とする。
        値は0°～180°の範囲をとる。
    """

    f_sky_i_k = (1.0 + np.cos(w_beta_i_k)) / 2.0

    return f_sky_i_k


def get_f_gnd_i_k(f_sky_i_k: float) -> float:
    """
    傾斜面の地面に対する形態係数を計算する。

    Args:
        f_sky_i_k: 室iの境界kの傾斜面の天空に対する形態係数

    Returns:
        室iの境界kの傾斜面の地面に対する形態係数
    """

    f_gnd_i_k = 1.0 - f_sky_i_k

    return f_gnd_i_k


def get_theta_aoi_i_k_n(
        w_alpha_i_k: float, w_beta_i_k: float,
        h_sun_ns: np.ndarray, a_sun_ns: np.ndarray
) -> np.ndarray:
    """
    傾斜面に入射する太陽の入射角を求める。

    Args:
        w_alpha_i_k: 室iの境界kにおける傾斜面の方位角, rad
        w_beta_i_k: 室iの境界kにおける傾斜面の傾斜角, rad
        h_sun_ns: ステップnにおける太陽高度, rad * 365 * 24 * 4
        a_sun_ns: ステップnにおける太陽方位角, rad * 365 * 24 * 4

    Returns:
        ステップnの室iの境界kにおける傾斜面に入射する太陽の入射角 * 365 * 24 * 4

    Notes:
        方向余弦がマイナス（入射角が90°～270°）の場合は傾斜面のり面に太陽が位置していることになるため
        値をゼロとする。
        （法線面直達日射量にこの値をかけるため、結果的に日射があたらないという計算になる。）
    """

    # h_sun_ns == 1.0 の場合は太陽が天頂にある時であり、太陽の方位角が定義されない。
    # その場合、cos(h_sun_ns)がゼロとなり、下式の第2項・第3項がゼロになる。
    cos_theta_aoi_i_k_n = np.where(
        h_sun_ns == 1.0,
        np.sin(h_sun_ns) * np.cos(w_beta_i_k),
        np.sin(h_sun_ns) * np.cos(w_beta_i_k)
        + np.cos(h_sun_ns) * np.sin(a_sun_ns) * np.sin(w_beta_i_k) * np.sin(w_alpha_i_k)
        + np.cos(h_sun_ns) * np.cos(a_sun_ns) * np.sin(w_beta_i_k) * np.cos(w_alpha_i_k)
    )

    cos_theta_aoi_i_k_n = np.clip(cos_theta_aoi_i_k_n, 0.0, None)

    theta_aoi_i_k_n = np.arccos(cos_theta_aoi_i_k_n)

    return theta_aoi_i_k_n


def get_rho_gnd() -> float:
    """
    地面の日射に対する反射率（アルベド）を計算する。

    Returns:
        地面の日射に対する反射率（アルベド）
    """
    return 0.1

