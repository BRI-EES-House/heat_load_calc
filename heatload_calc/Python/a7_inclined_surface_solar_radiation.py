import numpy as np

"""
付録7．傾斜面日射量
"""

def calc_slope_sol(
    I_DN_n: np.ndarray, I_sky_n: np.ndarray, Sh_n: np.ndarray, cos_Theta_i_k_n: np.ndarray,
    PhiS_i_k: float, PhiG_i_k: float, RhoG_l: float) ->(float, float, float, float):
    """
    Args:
        I_DN_n: 法線面直達日射量, W/m2K
        I_sky_n: 水平面天空日射量, W/m2K
        Sh_n: 太陽高度の正弦
        cos_Theta_i_k_n: 外表面における入射角の正弦
        PhiS_i_k: i室の部位kにおける天空に対する形態係数（付録19．による）
        PhiG_i_k: i室の部位kにおける地面に対する形態係数（付録19．による）
        RhoG_l: 部位lの地面日射反射率
    Returns:
        傾斜面直達日射量, W/m2K
        傾斜面天空日射量, W/m2K
        傾斜面反射日射量, W/m2K
        傾斜面日射量の合計, W/m2K
    """

    # 地物反射日射[W/m2] 式(78)
    I_R_i_k_n = get_I_R_i_k_n(I_DN_n, I_sky_n, PhiG_i_k, RhoG_l, Sh_n)

    # 傾斜面天空日射 式(77)
    I_S_i_k_n = get_I_S_i_k_n(I_sky_n, PhiS_i_k)

    # 傾斜面拡散日射量 式(76)
    I_d_i_k_n = get_I_d_i_k_n(I_S_i_k_n, I_R_i_k_n)

    # 傾斜面直達日射量 式(75)
    I_D_i_k_n = get_I_D_i_k_n(I_DN_n, cos_Theta_i_k_n)

    # 傾斜面全天日射量 式(74)
    I_w_i_k_n = get_I_w_i_k_n(I_D_i_k_n, I_d_i_k_n)

    return I_w_i_k_n, I_D_i_k_n, I_S_i_k_n, I_R_i_k_n


# 傾斜面全天日射量 式(74)
def get_I_w_i_k_n(I_D_i_k_n, I_d_i_k_n):
    I_w_i_k_n = I_D_i_k_n + I_d_i_k_n
    return I_w_i_k_n


# 傾斜面直達日射量 式(75)
def get_I_D_i_k_n(I_DN_n, cos_Theta_i_k_n):
    I_D_i_k_n = I_DN_n * cos_Theta_i_k_n
    return I_D_i_k_n


# 傾斜面拡散日射量 式(76)
def get_I_d_i_k_n(I_S_i_k_n, I_R_i_k_n):
    return I_S_i_k_n + I_R_i_k_n


# 傾斜面天空日射 式(77)
def get_I_S_i_k_n(I_sky_n, PhiS_i_k):
    return PhiS_i_k * I_sky_n


# 地物反射日射[W/m2] 式(78)
def get_I_R_i_k_n(I_DN_n, I_sky_n, PhiG_i_k, RhoG_l, Sh_n):
    I_HOL_n = Sh_n * I_DN_n + I_sky_n  # 水平面全天日射量
    I_R_i_k_n = PhiG_i_k * RhoG_l * I_HOL_n
    return I_R_i_k_n
