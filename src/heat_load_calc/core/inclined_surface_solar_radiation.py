"""傾斜面の日射量
附属書X7 傾斜面の日射量

次の関数からなる。
- 傾斜面の方位角・傾斜角から傾斜面の日射量（直達成分・天空成分・地盤反射成分）を計算する。
- 傾斜面の方位角・傾斜角から傾斜面の夜間放射量を計算する。
- 傾斜面の方位角・傾斜角から傾斜面に入射する太陽の入射角を計算する。

"""

from typing import Tuple
import numpy as np


def get_i_is_j_ns(
        i_dn_ns: np.ndarray,
        i_sky_ns: np.ndarray,
        r_eff_ns: np.ndarray,
        h_sun_ns: np.ndarray,
        a_sun_ns: np.ndarray,
        w_alpha_j: float,
        w_beta_j: float
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """傾斜面の方位角・傾斜角に応じて傾斜面の日射量を計算する。

    Args:
        i_dn_ns: ステップnにおける法線面直達日射量, W/m2K [8760*4]
        i_sky_ns: ステップnにおける水平面天空日射量, W/m2K [8760*4]
        r_eff_ns: ステップ n における夜間放射量, W/m2, [n]
        h_sun_ns: ステップnにおける太陽高度, rad [8760*4]
        a_sun_ns: ステップnにおける太陽方位角, rad [8760*4]
        w_alpha_j: 境界jの傾斜面の方位角, rad
        w_beta_j: 境界jの傾斜面の傾斜角, rad

    Returns:
        以下のタプル
            (1) ステップnにおける境界jにおける傾斜面の日射量のうち直達成分, W/m2K [8760*4]
            (2) ステップnにおける境界jにおける傾斜面の日射量のうち天空成分, W/m2K [8760*4]
            (3) ステップnにおける境界jにおける傾斜面の日射量のうち地盤反射成分, W/m2K [8760*4]

    Notes:
        添字 is は、傾斜面（inclined surface）
    """

    # ステップnの境界jにおける傾斜面に入射する太陽の入射角 [8760 * 4]
    theta_aoi_j_ns = get_theta_aoi_j_n(h_sun_ns=h_sun_ns, a_sun_ns=a_sun_ns, w_alpha_j=w_alpha_j, w_beta_j=w_beta_j)

    # ステップ n における水平面全天日射量, W/m2
    i_hrz_ns = _get_i_hrz_ns(i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, h_sun_ns=h_sun_ns)

    # 境界jの傾斜面の天空に対する形態係数
    f_sky_j = _get_f_sky_j(beta_w_j=w_beta_j)

    # 境界 j の地面に対する傾斜面の形態係数, -
    f_gnd_j = _get_f_gnd_j(f_sky_j=f_sky_j)

    # ステップ n における境界 j の傾斜面の夜間放射量, W/m2, [n]
    r_srf_eff_j_ns = _get_r_srf_eff_j_ns(r_eff_ns=r_eff_ns, f_sky_j=f_sky_j)

    # ステップ n における境界 j の傾斜面に入射する日射量の地盤反射成分, W/m2, [n]
    i_srf_ref_j_ns = _get_i_srf_ref_j_ns(f_gnd_j=f_gnd_j, i_hrz_ns=i_hrz_ns)

    # ステップ n における境界 j の傾斜面に入射する日射量の天空成分, W/m2, [n]
    i_srf_sky_j_ns = _get_i_srf_sky_j_ns(i_sky_ns=i_sky_ns, f_sky_j=f_sky_j)

    # ステップ n における境界 j の傾斜面に入射する日射量の直達成分, W/m2, [n]
    i_srf_dn_j_ns = _get_i_srf_dn_j_ns(i_dn_ns=i_dn_ns, theta_aoi_j_ns=theta_aoi_j_ns)

    return i_srf_dn_j_ns, i_srf_sky_j_ns, i_srf_ref_j_ns, r_srf_eff_j_ns


def _get_i_srf_dn_j_ns(i_dn_ns: np.ndarray, theta_aoi_j_ns: np.ndarray) -> np.ndarray:
    """
    傾斜面に入射する日射量の直達成分を計算する。

    Args:
        i_dn_ns: ステップ n における法線面直達日射量, W/m2, [n]
        theta_aoi_j_ns: ステップ n における境界 j の傾斜面に入射する日射の入射角, rad, [n]

    Returns:
        ステップ　n　における境界 j の傾斜面に入射する日射量の直達成分, W/m2, [n]

    Notes:
        式(1)
    """

    i_srf_dn_j_ns = i_dn_ns * np.cos(theta_aoi_j_ns)

    return i_srf_dn_j_ns


def _get_i_srf_sky_j_ns(i_sky_ns: np.ndarray, f_sky_j: float) -> np.ndarray:
    """
    傾斜面に入射する日射量の天空成分を計算する。

    Args:
        i_sky_ns: ステップ　n における水平面天空日射量, W/m2, [n]
        f_sky_j: 境界 j の天空に対する傾斜面の形態係数

    Returns:
        ステップ n における境界 j の傾斜面に入射する日射量の天空成分, W/m2, [n]

    Notes:
        式(2)
    """

    i_srf_sky_j_ns = f_sky_j * i_sky_ns

    return i_srf_sky_j_ns


def _get_i_srf_ref_j_ns( f_gnd_j: float, i_hrz_ns: np.ndarray) -> np.ndarray:
    """
    傾斜面の日射量のうち地盤反射成分を求める。

    Args:
        f_gnd_j: 境界 j の地面に対する傾斜面の形態係数, -
        i_hrz_ns: ステップ n における水平面全天日射量, W/m2, [n]

    Returns:
        ステップ n における境界 j の傾斜面に入射する日射量の地盤反射成分, W/m2, [n]

    Notes:
        式(3)
    """

    # 地面の日射反射率
    rho_gnd = 0.1

    i_srf_ref_j_ns = f_gnd_j * rho_gnd * i_hrz_ns

    return i_srf_ref_j_ns


def _get_r_srf_eff_j_ns(r_eff_ns: np.ndarray, f_sky_j: float) -> np.ndarray:
    """
    傾斜面の方位角・傾斜角に応じて傾斜面の夜間放射量を計算する。

    Args:
        r_eff_ns: ステップ n における水平面の夜間放射量, W/m2, [n]
        f_sky_j: 境界 j の天空に対する傾斜面の形態係数, -

    Returns:
        ステップ n における境界 j の傾斜面の夜間放射量, W/m2, [n]

    Notes:
        式(4)
    """

    r_srf_eff_j_ns = f_sky_j * r_eff_ns

    return r_srf_eff_j_ns


def get_theta_aoi_j_n(
        h_sun_ns: np.ndarray, a_sun_ns: np.ndarray, w_alpha_j: float, w_beta_j: float) -> np.ndarray:
    """
    傾斜面に入射する太陽の入射角を求める。

    Args:
        h_sun_ns: ステップnにおける太陽高度, rad, [365 * 24 * 4]
        a_sun_ns: ステップnにおける太陽方位角, rad, [365 * 24 * 4]
        w_alpha_j: 境界jにおける傾斜面の方位角, rad
        w_beta_j: 境界jにおける傾斜面の傾斜角, rad

    Returns:
        ステップnの境界jにおける傾斜面に入射する太陽の入射角, rad, [365 * 24 * 4]

    Notes:
        方向余弦がマイナス（入射角が90°～270°）の場合は傾斜面のり面に太陽が位置していることになるため
        値をゼロとする。
        （法線面直達日射量にこの値をかけるため、結果的に日射があたらないという計算になる。）
    """

    # ステップnの境界jにおける傾斜面に入射する太陽の入射角のコサイン, [8760 * 4]
    # h_sun_ns == 1.0 の場合は太陽が天頂にある時であり、太陽の方位角が定義されない。
    # その場合、cos(h_sun_ns)がゼロとなり、下式の第2項・第3項がゼロになる。
    cos_theta_aoi_j_n = np.where(
        np.cos(h_sun_ns) == 0.0,
        np.sin(h_sun_ns) * np.cos(w_beta_j),
        np.sin(h_sun_ns) * np.cos(w_beta_j)
        + np.cos(h_sun_ns) * np.sin(a_sun_ns) * np.sin(w_beta_j) * np.sin(w_alpha_j)
        + np.cos(h_sun_ns) * np.cos(a_sun_ns) * np.sin(w_beta_j) * np.cos(w_alpha_j)
    )

    # cos がマイナスの場合は入射角が90°～270°、つまり傾斜面の裏面に太陽が位置していることになるため、ゼロにする。
    cos_theta_aoi_j_n = np.clip(cos_theta_aoi_j_n, 0.0, None)

    # cos から radian に変換する。
    theta_aoi_j_n = np.arccos(cos_theta_aoi_j_n)

    return theta_aoi_j_n


def _get_i_hrz_ns(i_dn_ns, i_sky_ns, h_sun_ns):
    """
    水平面全天日射量を計算する。

    Args:
        i_dn_ns: ステップnにおける法線面直達日射量, W/m2K, [8760*4]
        i_sky_ns: ステップnにおける水平面天空日射量, W/m2K, [8760*4]
        h_sun_ns: ステップnにおける太陽高度, rad, [8760*4]

    Returns:
        ステップnにおける水平面全天日射量, W/m2K, [8760*4]
    """

    # ステップnにおける太陽高度の正弦
    # この値がゼロを下回る場合（太陽が地面に隠れている場合）はゼロとおく。
    sin_h_sun_ns = np.where(h_sun_ns > 0.0, np.sin(h_sun_ns), 0.0)

    # ステップnにおける水平面全天日射量, W/m2K, [8760*4]
    i_hsr_ns = sin_h_sun_ns * i_dn_ns + i_sky_ns

    return i_hsr_ns


def _get_f_sky_j(beta_w_j: float) -> float:
    """
    傾斜面の天空に対する形態係数を計算する。

    Args:
        beta_w_j: 境界 j の傾斜面の傾斜角, rad

    Returns:
        境界jの傾斜面の天空に対する形態係数

    Notes:
        境界jの傾斜面の傾斜角 は水平面を0°とし、垂直面を90°とし、
        オーバーハング床等における下に向いた面は180°とする。
        値は0°～180°の範囲をとる。
    """

    f_sky_j = (1.0 + np.cos(beta_w_j)) / 2.0

    return f_sky_j


def _get_f_gnd_j(f_sky_j: float) -> float:
    """
    地面に対する傾斜面の形態係数を計算する。

    Args:
        f_sky_j: 境界 j の天空に対する傾斜面の形態係数, -

    Returns:
        境界 j の地面に対する傾斜面の形態係数, -

    Notes:
        式(5)
    """

    f_gnd_j = 1.0 - f_sky_j

    return f_gnd_j

