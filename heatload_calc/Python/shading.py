import math
import numpy as np

"""
付録8．ひさしの影面積の計算
"""


# 日除けの影面積を計算する（当面、簡易入力のみに対応）式(79)
def calc_shading_area_ratio(depth: float, d_e: float, d_h: float, a_s: np.ndarray, h_s: np.ndarray, Wa: float) -> np.ndarray:
    """
    :param depth: 出幅 [m]
    :param d_e: 窓の上端から庇までの距離 [m]
    :param d_h: 窓の高さ [m]
    :param a_s: 太陽方位角 [rad]
    :param h_s: 太陽高度 [rad]
    :param Wa: 庇の設置してある窓の傾斜面方位角[rad]
    :return: 日除けの影面積比率 [-]
    """

    # DPの計算[m]
    DP = get_DP(depth, h_s, a_s, Wa)

    # DH'の計算[m]
    DH_dash = get_DH_dash(d_e, DP)

    #DHの計算[m]
    DH = get_DH(d_h, DH_dash)

    # 日影面積率の計算
    shading_area_ratio = get_F_SDW(d_h, DH)

    # 日が出ていないときは0
    shading_area_ratio[h_s <= 0] = 0.0

    return shading_area_ratio

# 式(79)
def get_F_SDW(d_h, DH):
    """
    :param d_h: 窓の高さ [m]
    :param DH:
    :return:
    """
    return DH / d_h


# 式(81)
def get_DH(d_h, DH_dash):
    """
    :param d_h: 窓の高さ [m]
    :param DH_dash:
    :return:
    """
    return np.clip(DH_dash, 0.0, d_h)


# 式(82)
def get_DH_dash(d_e, DP):
    """
    :param d_e: 窓の上端から庇までの距離 [m]
    :param DP: DP
    :return:
    """
    return DP - d_e

# 式(83)
def get_DP(depth, h_s, a_s, Wa):
    """
    :param depth: 出幅 [m]
    :param d_h: 窓の高さ [m]
    :param a_s: 太陽方位角 [rad]
    :param Wa: 庇の設置してある窓の傾斜面方位角[rad]
    :return:
    """
    # γの計算[rad]
    gamma = a_s - Wa

    # tan(プロファイル角)の計算
    tan_fai = np.tan(h_s) / np.cos(gamma)

    DP = depth * tan_fai
    return DP


