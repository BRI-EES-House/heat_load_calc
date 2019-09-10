import math
import numpy as np
from typing import List

"""
付録5．	太陽位置の計算
"""

# 太陽位置を計算するクラス
class defSolpos:
    """VBA では、mdlDefine モジュールにあったものを、モジュール　SolarPosision で記述することにした。"""

    def __init__(self, Sw, Ss, h_s, sin_h_s, cos_h_s, a_s, sin_a_s, cos_a_s):
        """
        :param Sw: cos(h)*sin(A)
        :param Ss: cos(h)*cos(A)
        :param h_s: 太陽高度[rad]
        :param sin_h_s: sin(h)
        :param a_s: 太陽方位角[rad]
        """
        self.Sw = Sw  # cos h sin A
        self.Ss = Ss  # cos h cos A
        self.h_s = h_s  # 太陽高度
        self.sin_h_s = sin_h_s  # sin h
        self.cos_h_s = cos_h_s
        self.a_s = a_s  # 太陽方位角
        self.sin_a_s = sin_a_s
        self.cos_a_s = cos_a_s


def get_n(y: int) -> int:
    """
    Args:
        y: 年, year
    Returns:
        1968年との年差, year
    """

    return y - 1968


def get_d0(n: int) -> float:
    """
    Args:
        n: 1968年との年差, year
    Returns:
        平均軌道上の近日点通過日（暦表時による1968年1月1日正午基準の日差）, d
    """

    return 3.71 + 0.2596 * n - int((n + 3.0) / 4.0)


def get_m(d: np.ndarray, d0: float) -> np.ndarray:
    """
    Args:
        d: 年通算日（1/1を1とする）, d
        d0: 平均軌道上の近日点通過日（暦表時による1968年1月1日正午基準の日差）, d
    Returns:
        平均近点離角, rad
    """

    # 近点年（近日点基準の公転周期日数）
    d_ay = 365.2596

    return 2 * math.pi * (d - d0) / d_ay


def get_epsilon(m: np.ndarray, n: int) -> np.ndarray:
    """
    Args:
        m: 平均近点離角, rad
        n: 1968年との年差
    Returns:
        近日点と冬至点の角度, rad
    """

    return np.radians(12.3901 + 0.0172 * (n + m / (2 * math.pi)))


def get_v(m: np.ndarray) -> np.ndarray:
    """
    Args:
        m: 平均近点離角, rad
    Returns:
        真近点離角, rad
    """

    return m + np.radians(1.914 * np.sin(m) + 0.02 * np.sin(2 * m))


def get_e_t(m: np.ndarray, epsilon: float, v: np.ndarray) -> np.ndarray:
    """
    Args:
        m: 平均近点離角, rad
        epsilon: 近日点と冬至点の角度, rad
        v: 真近点離角, rad
    Returns:
        均時差, deg,
    """

    # 均時差, rad
    e_t = (m - v) \
        - np.arctan(0.043 * np.sin(2.0 * (v + epsilon)) / (1.0 - 0.043 * np.cos(2.0 * (v + epsilon))))

    return e_t


def get_delta(epsilon: float, v: np.ndarray) -> (np.ndarray, np.ndarray):
    """
    Args:
        epsilon: 近日点と冬至点の角度, rad
        v: 真近点離角, rad
    Returns:
        赤緯の正弦
        赤緯の余弦
    """

    # 北半球の冬至の日赤緯, rad
    delta0 = math.radians(-23.4393)

    # 赤緯の正弦
    sin_delta = np.cos(v + epsilon) * math.sin(delta0)

    # 赤緯の余弦
    cos_delta = np.sqrt(1.0 - sin_delta ** 2)

    return sin_delta, cos_delta


def get_t(t_m: np.ndarray, l: float, l0: float, e_t: np.ndarray) -> np.ndarray:
    """
    Args:
        t_m:  標準時, h
        l: 経度, rad
        l0: 標準時の地点の経度, rad
        e_t: 均時差, rad
    Returns:
        時角, rad
    """

    return np.radians((t_m - 12.0) * 15.0) + (l - l0) + e_t


def get_h_s(phi: float, sin_delta: np.ndarray, cos_delta: np.ndarray, t: np.ndarray) -> (np.ndarray, np.ndarray, np.ndarray):
    """
    Args:
        phi: 経度, rad
        sin_delta: 赤緯の正弦
        cos_delta: 赤緯の余弦
        t: 時角, rad
    Returns:
        太陽高度, rad
        太陽高度の正弦
        太陽高度の余弦
    """

    sin_h_s = np.clip(math.sin(phi) * sin_delta + math.cos(phi) * cos_delta * np.cos(t), 0.0, None)
    cos_h_s = np.sqrt(1.0 - sin_h_s ** 2)
    h_s = np.arcsin(sin_h_s)

    return h_s, sin_h_s, cos_h_s


def get_a_s(
        sin_h_s: np.ndarray, cos_h_s: np.ndarray, sin_delta: float, cos_delta: np.ndarray,
        t: np.ndarray, phi: float) -> (float, float, float):
    """
    Args:
        sin_h_s: 太陽高度の正弦
        cos_h_s: 太陽高度の余弦
        sin_delta: 赤緯の正弦
        cos_delta: 赤緯の余弦
        t: 時角, rad
        phi: 緯度, rad
    Returns:
        太陽方位角, rad
        太陽方位角の正弦
        太陽方位角の余弦
    """

    f = sin_h_s <= 0.0

    sin_a_s = cos_delta * np.sin(t) / cos_h_s
    cos_a_s = (sin_h_s * math.sin(phi) - sin_delta) / (cos_h_s * math.cos(phi))
    a_s = np.sign(t) * np.arccos(cos_a_s)

    sin_a_s[f] = 0.0
    cos_a_s[f] = 0.0
    a_s[f] = 0.0

    return a_s, sin_a_s, cos_a_s


def get_solar_position(t_m: np.ndarray, d: np.ndarray, phi, l, l0) -> defSolpos:
    """
    太陽位置を計算する
    Args:
        t_m: 標準時,h
        d: 年通算日（1/1を1とする）, d
        phi: 緯度, rad
        l: 経度, rad
        l0: 標準時の地点の経度, rad
    Returns:
        defSolpos クラス
    """

    # 1968年との年差
    n = get_n(y=1989)

    # 平均軌道上の近日点通過日（暦表時による1968年1月1日正午基準の日差）, d
    d0 = get_d0(n)

    # 平均近点離角, rad
    m = get_m(d, d0)

    # 近日点と冬至点の角度, rad
    epsilon = get_epsilon(m, n)

    # 真近点離角, rad
    v = get_v(m)

    # 均時差, rad
    e_t = get_e_t(m, epsilon, v)

    # 赤緯の正弦, 赤緯の余弦
    sin_delta, cos_delta = get_delta(epsilon, v)

    # 時角, rad
    t = get_t(t_m, l, l0, e_t)

    # 太陽高度, rad, 太陽高度の正弦, 太陽高度の余弦
    h_s, sin_h_s, cos_h_s = get_h_s(phi, sin_delta, cos_delta, t)

    # 太陽方位角, rad, 太陽方位角の正弦, 太陽方位角の余弦
    a_s, sin_a_s, cos_a_s = get_a_s(sin_h_s, cos_h_s, sin_delta, cos_delta, t, phi)

    dblSs = cos_h_s * cos_a_s
    dblSw = cos_h_s * sin_a_s

    return defSolpos(dblSw, dblSs, h_s, sin_h_s, cos_h_s, a_s, sin_a_s, cos_a_s)


