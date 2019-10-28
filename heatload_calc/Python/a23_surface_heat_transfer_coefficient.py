import numpy as np
import a18_initial_value_constants as a18

"""
付録23．	表面熱伝達率
"""


# 表面熱伝達率の計算 式(123) 表16
def calc_surface_transfer_coefficient(eps_m, FF_m, hi_i_k_n):
    # 室内側表面放射熱伝達率 式(123)
    hr_i_k_n = get_hr_i_k_n(eps_m, FF_m)

    # 室内側表面対流熱伝達率 表(16)より
    hc_i_k_n = get_hc_i_k_n(hi_i_k_n, hr_i_k_n)

    return hr_i_k_n, hc_i_k_n


# 室外側表面総合熱伝達率 式(121)
def get_ho_i_k_n(Ro_i_k_n):
    return 1.0 / Ro_i_k_n


# 室内側表面総合熱伝達率 式(122)
def get_hi_i_k_n(Ri_i_k_n):
    return 1.0 / Ri_i_k_n


# 放射熱伝達率 式(123)
def get_hr_i_k_n(eps_m, FF_m):
    """
    :param eps_m: 放射率 [-]
    :param FF_m: 形態係数 [-]
    :param MRT: 平均放射温度 [℃]
    :return:
    """
    MRT = get_MRT()

    Sgm = a18.get_Sgm()

    # hr_i_k_n = eps_m / (1.0 - eps_m * FF_m) * 4.0 * Sgm * (MRT + 273.15) ** 3.0
    hr_i_k_n = np.repeat([eps_m * 4.0 * Sgm * (MRT + 273.15) ** 3.0], FF_m.size)

    return hr_i_k_n


# 平均放射温度MRT
def get_MRT():
    return 20.0


# 室内側表面対流熱伝達率 表16より
def get_hc_i_k_n(hi_i_k_n, hr_i_k_n):
    return np.clip(hi_i_k_n - hr_i_k_n, 0, None)
