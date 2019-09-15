import numpy as np

"""
付録10．窓の入射角特性
"""


# 透明部位の入射角特性
# 直達日射の入射角特性の計算
def get_taud_i_k_n(cos_Theta_i_k_n: np.ndarray, IAC_i_k: np.ndarray) -> np.ndarray:
    """
    :param cos_Theta_i_k_n: 入射角の方向余弦
    :param IAC_i_k: ガラスの入射角特性タイプ
    :return: 直達日射の入射角特性
    """
    taud_i_k_n = np.zeros((len(IAC_i_k), 24*365*4))

    taud_i_k_n[IAC_i_k == "single"] = get_taud_n_single(cos_Theta_i_k_n[IAC_i_k == "single"])
    taud_i_k_n[IAC_i_k == "multiple"] = get_taud_n_double(cos_Theta_i_k_n[IAC_i_k == "multiple"])

    taud_i_k_n[cos_Theta_i_k_n <= 0.0] = 0.0

    return taud_i_k_n

# 拡散日射の入射角特性の計算
def get_Cd(IAC: np.ndarray) -> np.ndarray:
    Cd = np.zeros(len(IAC))

    Cd[IAC == "single"] = get_taus_n_single()
    Cd[IAC == "multiple"] = get_taus_n_double()

    return Cd


# 直達日射に対する基準化透過率の計算（単層ガラス）
def get_taud_n_single(cos_phi: np.ndarray) -> np.ndarray:
    return 0.000 * cos_phi ** 0.0 + 2.552 * cos_phi ** 1.0 + 1.364 * cos_phi ** 2.0 \
        - 11.388 * cos_phi ** 3.0 + 13.617 * cos_phi ** 4.0 - 5.146 * cos_phi ** 5.0


# 直達日射に対する基準化反射率の計算（単層ガラス）
def get_rhod_n_single(cos_phi: np.ndarray) -> np.ndarray:
    return 1.000 * cos_phi ** 0.0 - 5.189 * cos_phi ** 1.0 + 12.392 * cos_phi ** 2.0 \
        - 16.593 * cos_phi ** 3.0 + 11.851 * cos_phi ** 4.0 - 3.461 * cos_phi ** 5.0


# 直達日射に対する基準化透過率の計算（複層ガラス）
def get_taud_n_double(cos_phi: float) -> float:
    return get_taud_n_single(cos_phi) ** 2.0 / (1.0 - get_rhod_n_single(cos_phi) ** 2.0)


# 拡散日射に対する基準化透過率（単層ガラス）
def get_taus_n_single() -> float:
    return 0.900


# 拡散日射に対する基準化透過率（複層ガラス）
def get_taus_n_double() -> float:
    return 0.832
