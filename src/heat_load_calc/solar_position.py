import math
from typing import Tuple
import numpy as np

from heat_load_calc.interval import Interval

"""
ステップnにおける太陽位置を計算する。
"""


def calc_solar_position(phi_loc: float, lambda_loc: float, interval: Interval) -> Tuple[np.ndarray, np.ndarray]:
    """
    太陽位置を計算する

    Args:
        phi_loc: 緯度, rad
        lambda_loc: 経度, rad
        interval: 生成するデータの時間間隔であり、以下の文字列で指定する。
            1h: 1時間間隔
            30m: 30分間隔
            15m: 15分間隔

    Returns:
        タプル
            (1) 太陽高度, rad [n]
            (2) 太陽方位角, rad [n]
    """

    # 標準子午線(meridian), rad
    lambda_loc_mer = _get_lambda_loc_mer()

    # ステップnにおける年通算日（1/1を1とする）, [n]
    d_ns = _get_d_ns(interval=interval)

    # 1968年との年差
    n = _get_n()

    # 平均軌道上の近日点通過日（暦表時による1968年1月1日正午基準の日差）, d
    d_0 = _get_d_0(n=n)

    # ステップnにおける平均近点離角, rad, [n]
    m_ns = _get_m_ns(d_ns=d_ns, d_0=d_0)

    # ステップnにおける近日点と冬至点の角度, rad, [n]
    epsilon_ns = _get_epsilon_ns(m_ns=m_ns, n=n)

    # ステップnにおける真近点離角, rad, [n]
    v_ns = _get_v_ns(m_ns=m_ns)

    # ステップnにおける均時差, rad, [n]
    e_t_ns = _get_e_t_ns(m_ns=m_ns, epsilon_ns=epsilon_ns, v_ns=v_ns)

    # ステップnにおける赤緯, rad, [n]
    delta_ns = _get_delta_ns(epsilon_ns=epsilon_ns, v_ns=v_ns)

    # ステップnにおける標準時, d, [n]
    # 1h: 0, 1.0, .... , 23.0, 0, 1.0, ...23.0
    # 30m: 0, 0.5, 1.0, 1.5, .... , 23.5, 0, 0.5, ...23.5
    # 15m: 0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, .... , 23.75, 0, 0.25, ...23.75
    t_m_ns = _get_t_m_ns(interval=interval)

    # ステップnにおける時角, rad, [n]
    omega_ns = _get_omega_ns(t_m_ns=t_m_ns, lambda_loc=lambda_loc, lambda_loc_mer=lambda_loc_mer, e_t_ns=e_t_ns)

    # ステップnにおける太陽高度, rad, [n]
    h_sun_ns = _get_h_sun_ns(phi_loc=phi_loc, omega_ns=omega_ns, delta_ns=delta_ns)

    # 太陽の位置が天頂にないか（天頂にある = False, 天頂にない = True）, [n]
    is_not_zenith_ns = _get_is_not_zenith_ns(h_sun_ns=h_sun_ns)

    # ステップnにおける太陽の方位角の正弦（太陽が天頂に無い場合のみに定義される）, [n]
    sin_a_sun_ns = _get_sin_a_sun_ns(delta_ns=delta_ns, h_sun_ns=h_sun_ns, omega_ns=omega_ns, inzs=is_not_zenith_ns)

    # ステップnにおける太陽の方位角の余弦（太陽が天頂に無い場合のみに定義される）, [n]
    cos_a_sun_ns = _get_cos_a_sun_ns(delta_ns=delta_ns, h_sun_ns=h_sun_ns, phi_loc=phi_loc, inzs=is_not_zenith_ns)

    # ステップnにおける太陽の方位角（太陽が天頂に無い場合のみに定義される）, rad, [n]
    a_sun_ns = _get_a_sun_ns(cos_a_sun_ns=cos_a_sun_ns, sin_a_sun_ns=sin_a_sun_ns, inzs=is_not_zenith_ns)

    return h_sun_ns, a_sun_ns


def _get_lambda_loc_mer() -> float:
    """
    標準子午線を取得する。

    Returns:
        標準子午線における経度, rad

    Notes:
        式(14)
    """

    # 標準子午線における経度を135°とする。
    return math.radians(135.0)


def _get_d_ns(interval: Interval) -> np.ndarray:
    """
    ステップnにおける年通算日を取得する 年通算日（1/1を1とする）, d
    Args:
        interval: 生成するデータの時間間隔
    Returns:
        ステップnにおける年通算日, d [n]
    Notes:
        1月1日を1とする。
        返り値は、365✕24✕n_hour の長さの配列
        n_hour: 1時間を何ステップで区切るのか
            1h: 1
            30m: 2
            15m: 4
        出力イメージ （n_hour = 1 の場合）
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,.....365,365,365,365

        式(13)
    """

    # 1時間を分割するステップ数
    n_hour = interval.get_n_hour()

    return np.repeat(np.arange(365) + 1, 24 * n_hour)


def _get_n() -> int:
    """
    1968年との年差を計算する。

    Returns:
        1968年との年差, year
    Notes:
        式(12)
    """

    # 太陽位置の計算においては1989年で行う。
    y = 1989

    return y - 1968


def _get_d_0(n: int) -> float:
    """
    平均軌道上の近日点通過日を取得する。

    Args:
        n: 1968年との年差, year

    Returns:
        平均軌道上の近日点通過日（暦表時による1968年1月1日正午基準の日差）, d

    Notes:
        式(11)
    """

    return 3.71 + 0.2596 * n - int((n + 3.0) / 4.0)


def _get_m_ns(d_ns: np.ndarray, d_0: float) -> np.ndarray:
    """
    平均近点離角を計算する。
    Args:
        d_ns: 年通算日（1/1を1とする）, d [n]
        d_0: 平均軌道上の近日点通過日（暦表時による1968年1月1日正午基準の日差）, d

    Returns:
        ステップnにおける平均近点離角, rad [n]

    Notes:
        式(10)
    """

    # 近点年（近日点基準の公転周期日数）
    d_ay = 365.2596

    # ステップnにおける平均近点離角, rad, [n]
    m_ns = 2 * math.pi * (d_ns - d_0) / d_ay

    return m_ns


def _get_epsilon_ns(m_ns: np.ndarray, n: int) -> np.ndarray:
    """
    ステップnにおける近日点と冬至点の角度を計算する。

    Args:
        m_ns: 平均近点離角, rad [n]
        n: 1968年との年差

    Returns:
        ステップnにおける近日点と冬至点の角度, rad [n]

    Notes:
        式(9)
    """

    return np.radians(12.3901 + 0.0172 * (n + m_ns / (2 * math.pi)))


def _get_v_ns(m_ns: np.ndarray) -> np.ndarray:
    """
    ステップnにおける真近点離角を計算する。

    Args:
        m_ns: ステップnにおける平均近点離角, rad [n]

    Returns:
        ステップnにおける真近点離角, rad [n]
    Notes:
        式(8)
    """

    return m_ns + np.radians(1.914 * np.sin(m_ns) + 0.02 * np.sin(2 * m_ns))


def _get_e_t_ns(m_ns: np.ndarray, epsilon_ns: np.ndarray, v_ns: np.ndarray) -> np.ndarray:
    """

    Args:
        m_ns: ステップnにおける平均近点離角, rad, [n]
        epsilon_ns: ステップnにおける近日点と冬至点の角度, rad, [n]
        v_ns: ステップnにおける真近点離角, rad, [n]
    Returns:
        ステップnにおける均時差, rad, [n]
    Notes:
        式(7)
    """

    e_t_ns = (m_ns - v_ns)\
        - np.arctan(0.043 * np.sin(2.0 * (v_ns + epsilon_ns)) / (1.0 - 0.043 * np.cos(2.0 * (v_ns + epsilon_ns))))

    return e_t_ns


def _get_delta_ns(epsilon_ns: np.ndarray, v_ns: np.ndarray) -> np.ndarray:
    """
    ステップnにおける赤緯を計算する。

    Args:
        epsilon_ns: ステップnにおける近日点と冬至点の角度, rad, [n]
        v_ns: ステップnにおける真近点離角, rad, [n]

    Returns:
        ステップnにおける赤緯, rad [n]

    Notes:
        赤緯は -π/2 ～ 0 π/2 の値をとる
        式(6)
    """

    # 北半球の冬至の日赤緯, rad
    delta_0 = math.radians(-23.4393)

    # 赤緯, rad, [n]
    delta_ns = np.arcsin(np.cos(v_ns + epsilon_ns) * math.sin(delta_0))

    return delta_ns


def _get_t_m_ns(interval: Interval) -> np.ndarray:
    """
    ステップnにおける標準時を計算する
    Args:
        interval: 生成するデータの時間間隔
    Returns:
        ステップnにおける標準時, d, [n]
    """

    # 1時間を何分割するか
    n_hour = interval.get_n_hour()

    # インターバル時間, h
    int_interval = interval.get_time()

    # 1h: 0, 1.0, .... , 23.0, 0, 1.0, ...23.0
    # 30m: 0, 0.5, 1.0, 1.5, .... , 23.5, 0, 0.5, ...23.5
    # 15m: 0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, .... , 23.75, 0, 0.25, ...23.75
    return np.tile(np.arange(24 * n_hour) * int_interval, 365)


def _get_omega_ns(t_m_ns: np.ndarray, lambda_loc: float, lambda_loc_mer: float, e_t_ns: np.ndarray) -> np.ndarray:
    """
    ステップnにおける時角を計算する。

    Args:
        t_m_ns: ステップnにおける標準時, h, [n]
        lambda_loc: 経度, rad
        lambda_loc_mer: 標準時の地点の経度, rad
        e_t_ns: ステップnにおける均時差, rad, [n]

    Returns:
        ステップnにおける時角, rad, [n]

    Notes:
        式(5)
    """

    return np.radians((t_m_ns - 12.0) * 15.0) + (lambda_loc - lambda_loc_mer) + e_t_ns


def _get_h_sun_ns(phi_loc: float, omega_ns: np.ndarray, delta_ns: np.ndarray) -> np.ndarray:
    """
    ステップnにおける太陽高度を計算する。

    Args:
        phi_loc: 経度, rad
        omega_ns: ステップnにおける時角, rad, [n]
        delta_ns: ステップnにおける赤緯, rad, [n]

    Returns:
        ステップnにおける太陽高度, rad, [n]

    Notes:
        太陽高度はマイナスの値もとり得る。（太陽が沈んでいる場合）
        式(4)
    """

    h_sun_ns = np.arcsin(np.sin(phi_loc) * np.sin(delta_ns) + np.cos(phi_loc) * np.cos(delta_ns) * np.cos(omega_ns))

    return h_sun_ns


def _get_is_not_zenith_ns(h_sun_ns):
    """
    Args:
        h_sun_ns: ステップnにおける太陽高度, rad [n]

    Returns:
        太陽の位置が天頂にないか（天頂にある = False, 天頂にない = True）, [n]
    """

    return h_sun_ns != np.pi / 2


def _get_sin_a_sun_ns(delta_ns, h_sun_ns, omega_ns, inzs):
    """

    Args:
        delta_ns: ステップnにおける赤緯, rad [n]
        h_sun_ns: ステップnにおける太陽高度, rad [n]
        omega_ns: ステップnにおける時角, rad [n]
        inzs: ステップ n における太陽位置が天頂にあるか否か（True=天頂にない, False=天頂にある）

    Returns:
        ステップnにおける太陽の方位角の正弦（太陽が天頂に無い場合のみに定義される）, [n]

    Notes:
        式(3)
    """

    # 太陽が天頂にある場合は「定義なし = np.nan」とするため、まずは、np.nan で埋める。
    sin_a_sun_ns = np.full(len(h_sun_ns), np.nan)

    # 太陽の方位角の正弦（太陽が天頂に無い場合のみ計算する）
    sin_a_sun_ns[inzs] = np.cos(delta_ns[inzs]) * np.sin(omega_ns[inzs]) / np.cos(h_sun_ns[inzs])

    return sin_a_sun_ns


def _get_cos_a_sun_ns(delta_ns, h_sun_ns, phi_loc, inzs):
    """

    Args:
        delta_ns: ステップnにおける赤緯, rad [n]
        h_sun_ns: ステップnにおける太陽高度, rad [n]
        phi_loc: 緯度, rad
        inzs: ステップ n における太陽位置が天頂にあるか否か（True=天頂にない, False=天頂にある）

    Returns:
        ステップnにおける太陽の方位角の余弦（太陽が天頂に無い場合のみに定義される）, [n]

    Notes:
        式(2)

    """

    # 太陽が天頂にある場合は「定義なし = np.nan」とするため、まずは、np.nan で埋める。
    cos_a_sun_ns = np.full(len(h_sun_ns), np.nan)

    # 太陽の方位角の余弦（太陽が天頂に無い場合のみ計算する）
    cos_a_sun_ns[inzs] = (np.sin(h_sun_ns[inzs]) * np.sin(phi_loc) - np.sin(delta_ns[inzs])) \
        / (np.cos(h_sun_ns[inzs]) * np.cos(phi_loc))

    return cos_a_sun_ns


def _get_a_sun_ns(cos_a_sun_ns, sin_a_sun_ns, inzs):
    """

    Args:
        cos_a_sun_ns: ステップ n における太陽の方位角の余弦（太陽が天頂に無い場合のみ計算する）
        sin_a_sun_ns: ステップ n における太陽の方位角の正弦（太陽が天頂に無い場合のみ計算する）
        inzs: ステップ n における太陽位置が天頂にあるか否か（True=天頂にない, False=天頂にある）

    Returns:
        ステップ n における太陽の方位角（太陽が天頂に無い場合のみに定義される）, rad, [n]

    Notes:
        式(1)
    """

    # 太陽が天頂にある場合は「定義なし = np.nan」とするため、まずは、np.nan で埋める。
    a_sun_ns = np.full(len(sin_a_sun_ns), np.nan)

    # 太陽の方位角, rad [n] （太陽が天頂に無い場合のみ計算する）
    # arctan の注意点。
    # arctan2 は、座標上で第1引数をy, 第2引数をxにした際にx軸との角度を求める関数。
    # 従って、単射の通常良く用いられる -π/2 ～ 0 ～ π/2 ではない。
    #   sin_a_s_ns が正 かつ cos_a_s_ns が正 の場合は第1象限（0～π/2）
    #   sin_a_s_ns が正 かつ cos_a_s_ns が負 の場合は第2象限（π/2～π）
    #   sin_a_s_ns が負 かつ cos_a_s_ns が負 の場合は第3象限（-π～-π/2）
    #   sin_a_s_ns が負 かつ cos_a_s_ns が正 の場合は第4象限（-π/2～0）
    a_sun_ns[inzs] = np.arctan2(sin_a_sun_ns[inzs], cos_a_sun_ns[inzs])

    return a_sun_ns

