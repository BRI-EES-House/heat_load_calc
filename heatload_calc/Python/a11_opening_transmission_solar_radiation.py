import numpy as np
from apdx10_oblique_incidence_characteristics import get_taud_i_k_n

"""
付録11．窓の透過日射熱取得の計算
"""


# 透過日射量[W]、吸収日射量[W]の計算 式(90)
def calc_QGT_i_k_n(
        cos_Theta_i_k_n: np.ndarray,
        IAC_i_k,
        I_D_i_k_n: np.ndarray,
        FSDW_i_k_n: np.ndarray,
        I_S_i_k_n: np.ndarray,
        I_R_i_k_n: np.ndarray,
        A_i_k,
        tau_i_k,
        Cd_i_k
):

    # 直達日射の入射角特性の計算
    taud_i_k_n = get_taud_i_k_n(cos_Theta_i_k_n, IAC_i_k)

    # 直達成分
    QGTD_i_k_n = get_QGTD_i_k_n(tau_i_k, I_D_i_k_n, taud_i_k_n, FSDW_i_k_n)

    # 拡散成分
    QGTS_i_k_n = get_QGTS_i_k_n(tau_i_k, Cd_i_k, I_S_i_k_n, I_R_i_k_n)

    # 透過日射量の計算
    QGT_i_k_n = (QGTD_i_k_n + QGTS_i_k_n) * A_i_k[:,np.newaxis]

    return QGT_i_k_n


# 透過日射熱取得（直達成分）[W/m2]の計算
def get_QGTD_i_k_n(T, I_D_i_k_n: np.ndarray, CID: np.ndarray, F_SDW_i_k: np.ndarray) -> np.ndarray:
    """
    :param I_D_i_k_n: 傾斜面入射直達日射量[W/m2]
    :param CID: 直達日射の入射角特性
    :param F_SDW_i_k: 日よけ等による日影面積率
    :return: 透過日射熱取得（直達成分）[W/m2]
    """
    # 透過日射熱取得（直達成分）[W/m2]の計算
    QGTD = T[:,np.newaxis] * (1.0 - F_SDW_i_k) * CID * I_D_i_k_n

    return QGTD


# 透過日射熱取得（拡散成分）[W/m2]の計算
def get_QGTS_i_k_n(T: float, Cd: np.ndarray, I_S_i_k_n: np.ndarray, I_R_i_k_n: np.ndarray) -> np.ndarray:
    """
    :param I_S_i_k_n: 傾斜面入射天空日射量[W/m2]
    :param I_R_i_k_n: 傾斜面入射反射日射量[W/m2]
    :return: 透過日射熱取得（拡散成分）[W/m2]
    """
    QGTS = T[:,np.newaxis] * Cd[:,np.newaxis] * (I_S_i_k_n + I_R_i_k_n)
    return QGTS
