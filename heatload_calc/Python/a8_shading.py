import numpy as np

"""
付録8．ひさしの影面積の計算
"""


# 日除けの影面積を計算する（当面、簡易入力のみに対応）式(79)
def calc_F_SDW_i_k(D_i_k: float, d_e: float, d_h: float, a_s_n: np.ndarray, h_s_n: np.ndarray, Wa_i_k: float) -> np.ndarray:
    """
    :param D_i_k: 出幅 [m]
    :param d_e: 窓の上端から庇までの距離 [m]
    :param d_h: 窓の高さ [m]
    :param a_s_n: 太陽方位角 [rad]
    :param h_s_n: 太陽高度 [rad]
    :param Wa_i_k: 庇の設置してある窓の傾斜面方位角[rad]
    :return: 日除けの影面積比率 [-]
    """

    # DPの計算[m] 式(83)
    D_P_i_k = get_D_P_i_k(D_i_k, h_s_n, a_s_n, Wa_i_k)

    # DH'の計算[m] 式(82)
    D_H_dash_i_k = get_D_H_dash_i_k(d_e, D_P_i_k)

    # DHの計算[m] 式(81)
    DH_i_k = get_D_H_i_k(d_h, D_H_dash_i_k)

    # 日影面積率の計算 式(79)
    F_SDW_i_k = get_F_SDW_i_k(d_h, DH_i_k, h_s_n)

    return F_SDW_i_k


# 日影面積率 式(79)
def get_F_SDW_i_k(d_h, DH, h_s_n):
    """
    :param d_h: 窓の高さ [m]
    :param DH:
    :return:
    """
    F_SDW_i_k = DH / d_h

    # 日が出ていないときは0
    F_SDW_i_k[h_s_n <= 0] = 0.0

    return F_SDW_i_k


# 式(80)
def get_A_SDW_i_k(W_R_i_k, D_H_i_k):
    return W_R_i_k * D_H_i_k

# 式(81)
def get_D_H_i_k(d_h, DH_dash):
    """
    :param d_h: 窓の高さ [m]
    :param DH_dash:
    :return:
    """
    return np.clip(DH_dash, 0.0, d_h)


# 式(82)
def get_D_H_dash_i_k(d_e, DP):
    """
    :param d_e: 窓の上端から庇までの距離 [m]
    :param DP: DP
    :return:
    """
    return DP - d_e

# 式(83)
def get_D_P_i_k(D_i_k, h_s, a_s, Wa):
    """
    :param D_i_k: 出幅 [m]
    :param d_h: 窓の高さ [m]
    :param a_s: 太陽方位角 [rad]
    :param Wa: 庇の設置してある窓の傾斜面方位角[rad]
    :return:
    """
    # γの計算[rad]
    gamma = a_s - Wa

    # tan(プロファイル角)の計算
    tan_fai = np.tan(h_s) / np.cos(gamma)

    DP = D_i_k * tan_fai
    return DP


