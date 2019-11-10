import numpy as np

"""
付録10．窓の入射角特性
"""


# 透明部位の入射角特性
# 直達日射の入射角特性の計算
def get_taud_i_k_n(
        theta_aoi_i_k: np.ndarray,
        incident_angle_characteristics_i_ks: str) -> np.ndarray:

    if incident_angle_characteristics_i_ks == 'single':
        return get_tau_norm_glass_i_k_n(theta_aoi_i_k=theta_aoi_i_k)

    elif incident_angle_characteristics_i_ks == 'multiple':
        return get_taud_n_double(theta_aoi_i_k=theta_aoi_i_k)

    else:
        raise ValueError()


def get_c_d_i_k(incident_angle_characteristics_i_ks: str) -> float:
    """
    窓ガラスのガラスの入射角特性タイプから拡散日射に対する基準化透過率を求める。

    Args:
        incident_angle_characteristics_i_ks: 室iの境界kにおける透明な開口部のガラスの入射角特性タイプ

    Returns:
        室iの境界kにおける透明な開口部の拡散日射に対する基準化透過率
    """

    # 入射角特性タイプが単板ガラスの場合
    if incident_angle_characteristics_i_ks == 'single':
        return get_c_d_single()

    # 入射角特性タイプが複層ガラスの場合
    elif incident_angle_characteristics_i_ks == 'multiple':
        return get_c_d_double()

    else:
        raise ValueError()


# 直達日射に対する基準化透過率の計算（単層ガラス）
def get_tau_norm_glass_i_k_n(theta_aoi_i_k: np.ndarray) -> np.ndarray:

    c = np.cos(theta_aoi_i_k)



    return 0.000 * c ** 0.0 + 2.552 * c ** 1.0 + 1.364 * c ** 2.0 \
           - 11.388 * c ** 3.0 + 13.617 * c ** 4.0 - 5.146 * c ** 5.0


# 直達日射に対する基準化反射率の計算（単層ガラス）
def get_rhod_n_single(theta_aoi_i_k) -> np.ndarray:

    cos = np.cos(theta_aoi_i_k)

    return 1.000 * cos ** 0.0 - 5.189 * cos ** 1.0 + 12.392 * cos ** 2.0 \
           - 16.593 * cos ** 3.0 + 11.851 * cos ** 4.0 - 3.461 * cos ** 5.0


# 直達日射に対する基準化透過率の計算（複層ガラス）
def get_taud_n_double(theta_aoi_i_k: np.ndarray) -> np.ndarray:

    return get_tau_norm_glass_i_k_n(
        theta_aoi_i_k=theta_aoi_i_k) ** 2.0 / (1.0 - get_rhod_n_single(theta_aoi_i_k) ** 2.0)


def get_c_d_single() -> float:
    """
    透明な開口部の拡散日射に対する基準化透過率（単層ガラス）を定義する。

    Returns:
        透明な開口部の拡散日射に対する基準化透過率（単層ガラス）
    """

    return 0.900


def get_c_d_double() -> float:
    """
    透明な開口部の拡散日射に対する基準化透過率（複層ガラス）を定義する。

    Returns:
        透明な開口部の拡散日射に対する基準化透過率（複層ガラス）
    """

    return 0.832
