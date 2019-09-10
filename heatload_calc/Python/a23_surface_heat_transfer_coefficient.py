import numpy as np
from common import Sgm

"""
付録23．	表面熱伝達率
"""


# 表面熱伝達率の計算
def calc_surface_transfer_coefficient(Ei, FF, hi):
    # 　== A23. 室内表面対流・放射熱伝達率の計算 ==
    MRT = get_MRT()

    # 室内側表面放射熱伝達率 式(123)
    hir = get_hr(Ei, FF, MRT)

    # 室内側表面対流熱伝達率 表(16)より
    hic = get_hc(hi, hir)

    return hir, hic


# 放射熱伝達率 式(123)
def get_hr(Ei, FF, MRT):
    """
    :param Ei: 放射率 [-]
    :param FF: 形態係数 [-]
    :param MRT: 平均放射温度 [℃]
    :return:
    """
    return Ei / (1.0 - Ei * FF) * 4.0 * Sgm * (MRT + 273.15) ** 3.0


# 平均放射温度MRT
def get_MRT():
    return 20.0


# 室内側表面対流熱伝達率 表16より
def get_hc(hi, hir):
    return np.clip(hi - hir, 0, None)