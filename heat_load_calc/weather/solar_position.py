# 附属書X5 太陽位置
# 地域の区分からステップnにおける太陽高度及び太陽方位角を計算する。

import math
import numpy as np

from heat_load_calc.weather import calc_interval


def calc_solar_position(phi_loc: float, lambda_loc: float, interval: str) -> (np.ndarray, np.ndarray):
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
    lambda_loc_mer = get_lambda_loc_mer()

    # ステップnにおける年通算日（1/1を1とする） [n]
    d_ns = get_d_ns(interval=interval)

    # 1968年との年差
    n = get_n()

    # 平均軌道上の近日点通過日（暦表時による1968年1月1日正午基準の日差）, d
    d_0 = get_d_0(n=n)

    # ステップnにおける平均近点離角, rad [n]
    m_ns = get_m_ns(d_ns=d_ns, d_0=d_0)

    # ステップnにおける近日点と冬至点の角度, rad [n]
    epsilon_ns = get_epsilon_ns(m_ns=m_ns, n=n)

    # ステップnにおける真近点離角, rad [n]
    v_ns = get_v_ns(m_ns=m_ns)

    # ステップnにおける均時差, rad [n]
    e_t_ns = get_e_t_ns(m_ns=m_ns, epsilon_ns=epsilon_ns, v_ns=v_ns)

    # ステップnにおける赤緯, rad [n]
    delta_ns = get_delta_ns(epsilon_ns=epsilon_ns, v_ns=v_ns)

    # ステップnにおける標準時, d [n]
    # 1h: 0, 1.0, .... , 23.0, 0, 1.0, ...23.0
    # 30m: 0, 0.5, 1.0, 1.5, .... , 23.5, 0, 0.5, ...23.5
    # 15m: 0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, .... , 23.75, 0, 0.25, ...23.75
    t_m_ns = get_t_m_ns(interval=interval)

    # ステップnにおける時角, rad [n]
    omega_ns = get_omega_ns(t_m_ns=t_m_ns, lambda_loc=lambda_loc, lambda_loc_mer=lambda_loc_mer, e_t_ns=e_t_ns)

    # 太陽高度, rad [n]
    h_sun_ns = get_h_sun_ns(phi_loc=phi_loc, omega_ns=omega_ns, delta_ns=delta_ns)

    # 太陽方位角, rad [n]
    a_sun_ns = get_a_sun_ns(omega_ns=omega_ns, phi_loc=phi_loc, delta_ns=delta_ns, h_sun_ns=h_sun_ns)

    return h_sun_ns, a_sun_ns


def get_lambda_loc_mer() -> float:
    """
    標準子午線を取得する。

    Returns:
        標準子午線における経度, rad
    """

    # 標準子午線における経度を135°とする。
    return math.radians(135.0)


def get_d_ns(interval: str) -> np.ndarray:
    """
    ステップnにおける年通算日を取得する 年通算日（1/1を1とする）, d
    Args:
        interval: 生成するデータの時間間隔であり、以下の文字列で指定する。
            1h: 1時間間隔
            30m: 30分間隔
            15m: 15分間隔
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
    """

    # 1時間を分割するステップ数
    n_hour = calc_interval.get_n_hour(interval)

    return np.repeat(np.arange(365) + 1, 24 * n_hour)


def get_n() -> int:
    """
    1968年との年差を計算する。

    Returns:
        1968年との年差, year
    """

    # 太陽位置の計算においては1989年で行う。
    y = 1989

    return y - 1968


def get_d_0(n: int) -> float:
    """
    平均軌道上の近日点通過日を取得する。

    Args:
        n: 1968年との年差, year

    Returns:
        平均軌道上の近日点通過日（暦表時による1968年1月1日正午基準の日差）, d
    """

    return 3.71 + 0.2596 * n - int((n + 3.0) / 4.0)


def get_m_ns(d_ns: np.ndarray, d_0: float) -> np.ndarray:
    """
    平均近点離角を計算する。
    Args:
        d_ns: 年通算日（1/1を1とする）, d [n]
        d_0: 平均軌道上の近日点通過日（暦表時による1968年1月1日正午基準の日差）, d

    Returns:
        ステップnにおける平均近点離角, rad [n]
    """

    # 近点年（近日点基準の公転周期日数）
    d_ay = 365.2596

    # ステップnにおける平均近点離角, rad * 365 * 96
    m_ns = 2 * math.pi * (d_ns - d_0) / d_ay

    return m_ns


def get_epsilon_ns(m_ns: np.ndarray, n: int) -> np.ndarray:
    """
    ステップnにおける近日点と冬至点の角度を計算する。

    Args:
        m_ns: 平均近点離角, rad [n]
        n: 1968年との年差

    Returns:
        ステップnにおける近日点と冬至点の角度, rad [n]
    """

    return np.radians(12.3901 + 0.0172 * (n + m_ns / (2 * math.pi)))


def get_v_ns(m_ns: np.ndarray) -> np.ndarray:
    """
    ステップnにおける真近点離角を計算する。

    Args:
        m_ns: ステップnにおける平均近点離角, rad [n]

    Returns:
        ステップnにおける真近点離角, rad [n]
    """

    return m_ns + np.radians(1.914 * np.sin(m_ns) + 0.02 * np.sin(2 * m_ns))


def get_e_t_ns(m_ns: np.ndarray, epsilon_ns: np.ndarray, v_ns: np.ndarray) -> np.ndarray:
    """
    Args:
        m_ns: ステップnにおける平均近点離角, rad [n]]
        epsilon_ns: ステップnにおける近日点と冬至点の角度, rad [n]]
        v_ns: ステップnにおける真近点離角, rad [n]
    Returns:
        ステップnにおける均時差, rad [n]
    """

    e_t_ns = (m_ns - v_ns)\
        - np.arctan(0.043 * np.sin(2.0 * (v_ns + epsilon_ns)) / (1.0 - 0.043 * np.cos(2.0 * (v_ns + epsilon_ns))))

    return e_t_ns


def get_delta_ns(epsilon_ns: np.ndarray, v_ns: np.ndarray) -> np.ndarray:
    """
    ステップnにおける赤緯を計算する。

    Args:
        epsilon_ns: ステップnにおける近日点と冬至点の角度, rad [n]
        v_ns: ステップnにおける真近点離角, rad [n]

    Returns:
        ステップnにおける赤緯, rad [n]

    Notes:
        赤緯は -π/2 ～ 0 π/2 の値をとる
    """

    # 北半球の冬至の日赤緯, rad
    delta_0 = math.radians(-23.4393)

    # 赤緯, rad * 8760 * 96
    delta_ns = np.arcsin(np.cos(v_ns + epsilon_ns) * math.sin(delta_0))

    return delta_ns


def get_t_m_ns(interval: str) -> np.ndarray:
    """
    ステップnにおける標準時を計算する
    Args:
        interval: 生成するデータの時間間隔であり、以下の文字列で指定する。
            1h: 1時間間隔
            30m: 30分間隔
            15m: 15分間隔
    Returns:
        ステップnにおける標準時, d [n]
    """

    n_hour = calc_interval.get_n_hour(interval=interval)

    int_interval = {
        '1h': 1.0,
        '30m': 0.5,
        '15m': 0.25
    }[interval]

    # 1h: 0, 1.0, .... , 23.0, 0, 1.0, ...23.0
    # 30m: 0, 0.5, 1.0, 1.5, .... , 23.5, 0, 0.5, ...23.5
    # 15m: 0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, .... , 23.75, 0, 0.25, ...23.75
    return np.tile(np.arange(24 * n_hour) * int_interval, 365)


def get_omega_ns(t_m_ns: np.ndarray, lambda_loc: float, lambda_loc_mer: float, e_t_ns: np.ndarray) -> np.ndarray:
    """
    ステップnにおける時角を計算する。

    Args:
        t_m_ns:  標準時, h
        lambda_loc: 経度, rad
        lambda_loc_mer: 標準時の地点の経度, rad
        e_t_ns: 均時差, rad [n]

    Returns:
        ステップnにおける時角, rad [n]
    """

    return np.radians((t_m_ns - 12.0) * 15.0) + (lambda_loc - lambda_loc_mer) + e_t_ns


def get_h_sun_ns(phi_loc: float, omega_ns: np.ndarray, delta_ns: np.ndarray) -> np.ndarray:
    """
    ステップnにおける太陽高度を計算する。

    Args:
        phi_loc: 経度, rad
        omega_ns: ステップnにおける時角, rad [n]
        delta_ns: ステップnにおける赤緯, rad [n]

    Returns:
        ステップnにおける太陽高度, rad [n]

    Notes:
        太陽高度はマイナスの値もとり得る。（太陽が沈んでいる場合）
    """

    h_sun_ns = np.arcsin(np.sin(phi_loc) * np.sin(delta_ns) + np.cos(phi_loc) * np.cos(delta_ns) * np.cos(omega_ns))

    return h_sun_ns


def get_a_sun_ns(omega_ns: np.ndarray, phi_loc: float, delta_ns: np.ndarray, h_sun_ns: np.ndarray) -> np.ndarray:
    """
    Args:
        omega_ns: ステップnにおける時角, rad [n]
        phi_loc: 緯度, rad
        delta_ns: ステップnにおける赤緯, rad [n]
        h_sun_ns: ステップnにおける太陽高度, rad [n]

    Returns:
        太陽方位角, rad [n]
    """

    a_sun_ns = np.full(len(h_sun_ns), np.nan)
    sin_a_sun_ns = np.full(len(h_sun_ns), np.nan)
    cos_a_sun_ns = np.full(len(h_sun_ns), np.nan)

    # 太陽の位置が天頂にない場合をチェックする, 天頂にない場合がTrue [n]
    f = h_sun_ns != np.pi / 2

    # 太陽の方位角の正弦（太陽が天頂に無い場合のみ計算する）
    sin_a_sun_ns[f] = np.cos(delta_ns[f]) * np.sin(omega_ns[f]) / np.cos(h_sun_ns[f])

    # 太陽の方位角の余弦（太陽が天頂に無い場合のみ計算する）
    cos_a_sun_ns[f] = (np.sin(h_sun_ns[f]) * np.sin(phi_loc) - np.sin(delta_ns[f]))\
        / (np.cos(h_sun_ns[f]) * np.cos(phi_loc))

    # 太陽の方位角, rad [n] （太陽が天頂に無い場合のみ計算する）
    # 太陽が天頂にある場合は最初に定義した「定義なし=np.nan」のままである。
    # arctan の注意点。
    # arctan2 は、座標上で第1引数をy, 第2引数をxにした際にx軸との角度を求める関数です。
    # 従って、単射の通常良く用いられる -π/2 ～ 0 ～ π/2 ではないので、ここだけ小文字の arctan としてください。
    # 加えて、
    # sin_a_s_ns が正 かつ cos_a_s_ns が正 の場合は第1象限（0～π/2）
    # sin_a_s_ns が正 かつ cos_a_s_ns が負 の場合は第2象限（π/2～π）
    # sin_a_s_ns が負 かつ cos_a_s_ns が負 の場合は第3象限（-π～-π/2）
    # sin_a_s_ns が負 かつ cos_a_s_ns が正 の場合は第4象限（-π/2～0）
    # である旨の注釈をつけておいてください。
    a_sun_ns[f] = np.arctan2(sin_a_sun_ns[f], cos_a_sun_ns[f])

    return a_sun_ns

