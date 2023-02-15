from typing import Tuple
import numpy as np

from heat_load_calc.direction import Direction
from heat_load_calc.weather import Weather


def get_i_s_j_ns(
    w: Weather,
    drct_j: Direction
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """傾斜面の方位角・傾斜角に応じて傾斜面の日射量を計算する。
    Args:
        w: Weather Class
        drct_j: Direction Class
    Returns:
        (1) ステップnにおける境界jの傾斜面に入射する日射量のうち直達成分, W/m2, [N+1]
        (2) ステップnにおける境界jの傾斜面に入射する日射量のうち天空成分, W/m2, [N+1]
        (3) ステップnにおける境界jの傾斜面に入射する日射量のうち地盤反射成分, W/m2, [N+1]
        (4) ステップnにおける境界jの傾斜面の夜間放射量, W/m2, [N+1]
    """

    # ステップnにおける法線面直達日射量, W/m2K [N+1]
    i_dn_ns = w.i_dn_ns_plus
    # ステップnにおける水平面天空日射量, W/m2K [N+1]
    i_sky_ns = w.i_sky_ns_plus
    # ステップnにおける夜間放射量, W/m2, [N+1]
    r_n_ns = w.r_n_ns_plus
    # ステップnにおける太陽高度, rad [N+1]
    h_sun_ns = w.h_sun_ns_plus
    # ステップnにおける太陽方位角, rad [N+1]
    a_sun_ns = w.a_sun_ns_plus

    # 境界jの傾斜面の傾斜角, rad
    beta_w_j = drct_j.beta_w_j

    # ステップnにおける境界jに入射する太陽の入射角, deg, [N+1]
    phi_j_ns = get_phi_j_ns(h_sun_ns=h_sun_ns, a_sun_ns=a_sun_ns, drct_j=drct_j)

    # ステップ n における水平面全天日射量, W/m2, [n]
    i_hrz_ns = _get_i_hrz_ns(i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, h_sun_ns=h_sun_ns)

    # 境界jの傾斜面の天空に対する形態係数, -
    f_sky_j = _get_f_sky_j(beta_w_j=beta_w_j)

    # 境界 j の地面に対する傾斜面の形態係数, -
    f_gnd_j = _get_f_gnd_j(f_sky_j=f_sky_j)

    # ステップ n における境界 j の傾斜面の夜間放射量, W/m2, [N+1]
    r_s_n_j_ns = _get_r_s_n_j_ns(r_eff_ns=r_n_ns, f_sky_j=f_sky_j)

    # ステップnにおける境界jに入射する日射量の地盤反射成分, W/m2, [N+1]
    i_s_ref_j_ns = _get_i_s_ref_j_ns(f_gnd_j=f_gnd_j, i_hrz_ns=i_hrz_ns)

    # ステップnにおける境界jに入射する日射量の天空成分, W/m2, [N+1]
    i_s_sky_j_ns = _get_i_s_sky_j_ns(i_sky_ns=i_sky_ns, f_sky_j=f_sky_j)

    # ステップnにおける境界jに入射する日射量の直達成分, W/m2, [N+1]
    i_s_dn_j_ns = _get_i_s_dn_j_ns(i_dn_ns=i_dn_ns, phi_j_ns=phi_j_ns)

    return i_s_dn_j_ns, i_s_sky_j_ns, i_s_ref_j_ns, r_s_n_j_ns


def _get_i_s_dn_j_ns(i_dn_ns: np.ndarray, phi_j_ns: np.ndarray) -> np.ndarray:
    """ステップnにおける境界jに入射する日射量の直達成分を計算する。
    Args:
        i_dn_ns: ステップnにおける法線面直達日射量, W/m2, [N+1]
        phi_j_ns: ステップnにおける境界jに入射する日射の入射角, rad, [N+1]
    Returns:
        ステップnにおける境界jに入射する日射量の直達成分, W/m2, [N+1]
    Notes:
        式(1)
    """

    i_srf_dn_j_ns = i_dn_ns * np.cos(phi_j_ns)

    return i_srf_dn_j_ns


def _get_i_s_sky_j_ns(i_sky_ns: np.ndarray, f_sky_j: float) -> np.ndarray:
    """ステップnにおける境界jに入射する日射量の天空成分を計算する。
    Args:
        i_sky_ns: ステップnにおける水平面天空日射量, W/m2, [N+1]
        f_sky_j: 境界jの天空に対する傾斜面の形態係数, -
    Returns:
        ステップnにおける境界jに入射する日射量の天空成分, W/m2, [N+1]
    Notes:
        式(2)
    """

    i_s_sky_j_ns = f_sky_j * i_sky_ns

    return i_s_sky_j_ns


def _get_i_s_ref_j_ns(f_gnd_j: float, i_hrz_ns: np.ndarray) -> np.ndarray:
    """傾斜面の日射量のうち地盤反射成分を求める。
    Args:
        f_gnd_j: 境界 j の地面に対する傾斜面の形態係数, -
        i_hrz_ns: ステップ n における水平面全天日射量, W/m2, [N+1]
    Returns:
        ステップnにおける境界jに入射する日射量の地盤反射成分, W/m2, [N+1]
    Notes:
        式(3)
    """

    # 地面の日射反射率
    rho_gnd = 0.1

    i_s_ref_j_ns = f_gnd_j * rho_gnd * i_hrz_ns

    return i_s_ref_j_ns


def _get_r_s_n_j_ns(r_eff_ns: np.ndarray, f_sky_j: float) -> np.ndarray:
    """
    傾斜面の方位角・傾斜角に応じて傾斜面の夜間放射量を計算する。

    Args:
        r_eff_ns: ステップnにおける水平面の夜間放射量, W/m2, [N+1]
        f_sky_j: 境界jの天空に対する傾斜面の形態係数, -
    Returns:
        ステップnにおける境界jの夜間放射量, W/m2, [N+1]
    Notes:
        式(4)
    """

    r_srf_eff_j_ns = f_sky_j * r_eff_ns

    return r_srf_eff_j_ns


def _get_f_gnd_j(f_sky_j: float) -> float:
    """境界jの地面に対する傾斜面の形態係数を計算する。
    Args:
        f_sky_j: 境界jの天空に対する傾斜面の形態係数, -
    Returns:
        境界jの地面に対する傾斜面の形態係数, -
    Notes:
        式(5)
    """

    f_gnd_j = 1.0 - f_sky_j

    return f_gnd_j


def _get_f_sky_j(beta_w_j: float) -> float:
    """
    境界jの傾斜面の天空に対する形態係数を計算する。
    Args:
        beta_w_j: 境界jの傾斜面の傾斜角, rad
    Returns:
        境界jの傾斜面の天空に対する形態係数
    Notes:
        式(6)
        境界jの傾斜面の傾斜角 は水平面を0とし、垂直面をπ/2とし、オーバーハング床等における下に向いた面はπとし、値は0～πの範囲をとる。
    """

    if beta_w_j < 0:
        raise Exception("傾斜面の傾斜角が0より小さい値となっています。")

    if beta_w_j > np.pi:
        raise Exception("傾斜角の傾斜面がπより大きい値となっています。")

    f_sky_j = (1.0 + np.cos(beta_w_j)) / 2.0

    return f_sky_j


def _get_i_hrz_ns(i_dn_ns: np.ndarray, i_sky_ns: np.ndarray, h_sun_ns: np.ndarray) -> np.ndarray:
    """水平面全天日射量を計算する。
    Args:
        i_dn_ns: ステップ n における法線面直達日射量, W/m2, [n]
        i_sky_ns: ステップ n における水平面天空日射量, W/m2, [n]
        h_sun_ns: ステップ n における太陽高度, rad, [n]
    Returns:
        ステップ n における水平面全天日射量, W/m2, [n]
    Notes:
        式(7)
    """

    # ステップnにおける太陽高度 h_sun_ns が 0 未満の場合は 0 とする。
    i_hsr_ns = np.sin(h_sun_ns.clip(min=0.0)) * i_dn_ns + i_sky_ns

    return i_hsr_ns


def get_phi_j_ns(h_sun_ns: np.ndarray, a_sun_ns: np.ndarray, drct_j: Direction) -> np.ndarray:
    """傾斜面に入射する太陽の入射角を計算する。
    Args:
        h_sun_ns: ステップnにおける太陽高度, rad, [N+1]
        a_sun_ns: ステップnにおける太陽方位角, rad, [N+1]
        drct_j: Direction Class
    Returns:
        ステップnにおける境界jに入射する太陽の入射角, rad, [N+1]
    Notes:
        式(8), 式(9)
    """

    # 方位が上面・下面（beta_w_j=0）の場合は、厳密には方位角（alpha_w_j）は定義できないため、条件分岐により式を分ける。
    if drct_j in [Direction.TOP, Direction.BOTTOM]:

        cos_phi_j_ns = np.clip(np.sin(h_sun_ns), 0.0, None)

    else:

        # 境界jの方位角, rad
        alpha_w_j = drct_j.alpha_w_j

        # 境界jの傾斜角, rad
        beta_w_j = drct_j.beta_w_j

        # ステップnにおける境界jに入射する太陽の入射角の余弦, -, [n]
        # cos(h_sun_ns) == 0.0 の場合は太陽が天頂にある時であり、太陽の方位角が定義されない。
        # その場合、cos(h_sun_ns)がゼロとなり、下式の第2項・第3項がゼロになる。
        # これを回避するために場合分けを行っている。
        # 余弦がマイナス（入射角が90°～270°）の場合は傾斜面の裏面に太陽が位置していることになるため、値をゼロにする。
        # （法線面直達日射量にこの値をかけるため、結果的に日射があたらないという計算になる。）
        cos_phi_j_ns = np.zeros_like(a=h_sun_ns, dtype=float)
        f = np.cos(h_sun_ns) == 0.0
        cos_phi_j_ns[f] = np.clip(np.sin(h_sun_ns[f]) * np.cos(beta_w_j), 0.0, None)
        cos_phi_j_ns[~f] = np.clip(np.sin(h_sun_ns[~f]) * np.cos(beta_w_j)
            + np.cos(h_sun_ns[~f]) * np.sin(a_sun_ns[~f]) * np.sin(beta_w_j) * np.sin(alpha_w_j)
            + np.cos(h_sun_ns[~f]) * np.cos(a_sun_ns[~f]) * np.sin(beta_w_j) * np.cos(alpha_w_j)
            , 0.0, None)

        # cos_phi_j_ns = np.where(
        #     np.cos(h_sun_ns) == 0.0,
        #     np.clip(np.sin(h_sun_ns) * np.cos(beta_w_j), 0.0, None),
        #     np.clip(np.sin(h_sun_ns) * np.cos(beta_w_j)
        #             + np.cos(h_sun_ns) * np.sin(a_sun_ns) * np.sin(beta_w_j) * np.sin(alpha_w_j)
        #             + np.cos(h_sun_ns) * np.cos(a_sun_ns) * np.sin(beta_w_j) * np.cos(alpha_w_j)
        #             , 0.0, None)
        # )

    # ステップnにおける境界jに入射する日射の入射角, rad, [N+1]
    phi_j_ns = np.arccos(cos_phi_j_ns)

    return phi_j_ns





