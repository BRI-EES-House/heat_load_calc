"""窓の入射角特性

"""
import math

import numpy as np


def get_tau_d_j_ns(theta_aoi_j_ns: np.ndarray, glazing_type_j: str) -> np.ndarray:
    """
    透明部位の入射角特性
    直達日射の入射角特性の計算

    Args:
        theta_aoi_j_ns:
        glazing_type_j:

    Returns:
        直達日射に対する規準化透過率
    """

    if glazing_type_j == 'single':
        return _get_tau_norm_glass_i_k_n(theta_aoi_i_k=theta_aoi_j_ns)

    elif glazing_type_j == 'multiple':
        return _get_taud_n_double(theta_aoi_i_k=theta_aoi_j_ns)

    else:
        raise ValueError()

def get_rho_d_j_ns(theta_aoi_j_ns: np.ndarray, glazing_type_j: str) -> np.ndarray:
    """
    透明部位の入射角特性
    直達日射の反射率入射角特性の計算

    Args:
        theta_aoi_j_ns:
        glazing_type_j:

    Returns:
        直達日射に対する規準化反射率
    """

    if glazing_type_j == 'single':
        return _get_rhod_n_single(theta_aoi_i_k=theta_aoi_j_ns)

    elif glazing_type_j == 'multiple':
        return _get_rhod_n_double(theta_aoi_i_k=theta_aoi_j_ns)

    else:
        raise ValueError()


def get_c_d_j(glazing_type_j: str) -> float:
    """
    窓ガラスのガラスの入射角特性タイプから拡散日射に対する規準化透過率を求める。

    Args:
        glazing_type_j: 室iの境界kにおける透明な開口部のガラスの入射角特性タイプ

    Returns:
        室iの境界kにおける透明な開口部の拡散日射に対する規準化透過率
    """

    # 入射角特性タイプが単板ガラスの場合
    if glazing_type_j == 'single':
        return _get_c_d_single()

    # 入射角特性タイプが複層ガラスの場合
    elif glazing_type_j == 'multiple':
        return _get_c_d_double()

    else:
        raise ValueError()


def get_r_d_j(glazing_type_j: str) -> float:
    """
    窓ガラスのガラスの入射角特性タイプから拡散日射に対する規準化反射率を求める。

    Args:
        glazing_type_j: 室iの境界kにおける透明な開口部のガラスの入射角特性タイプ

    Returns:
        室iの境界kにおける透明な開口部の拡散日射に対する規準化反射率
    """

    # 入射角特性タイプが単板ガラスの場合
    if glazing_type_j == 'single':
        return _get_r_d_single()

    # 入射角特性タイプが複層ガラスの場合
    elif glazing_type_j == 'multiple':
        return _get_r_d_double()

    else:
        raise ValueError()


# TODO:吸収日射取得率の入射角特性は、1-τ-ρで暫定対応（τ：透過率の規準化透過率、ρ：反射率の規準化反射率）
def get_ashgc_d_j(glazing_type_j: str) -> float:
    """
    窓ガラスのガラスの入射角特性タイプから拡散日射に対する規準化日射熱取得率を求める。

    Args:
        glazing_type_j: 室iの境界kにおける透明な開口部のガラスの入射角特性タイプ

    Returns:
        室iの境界kにおける透明な開口部の拡散日射に対する規準化反射率
    """


    # 入射角特性タイプが単板ガラスの場合
    if glazing_type_j == 'single':
        return max(1.0 - _get_c_d_single() - _get_r_d_single(), 0.0)

    # 入射角特性タイプが複層ガラスの場合
    elif glazing_type_j == 'multiple':
        return max(1.0 - _get_c_d_double() - _get_r_d_double(), 0.0)

    else:
        raise ValueError()


# 直達日射に対する規準化透過率の計算（単層ガラス）
def _get_tau_norm_glass_i_k_n(theta_aoi_i_k: np.ndarray) -> np.ndarray:

    c = np.cos(theta_aoi_i_k)



    return 0.000 * c ** 0.0 + 2.552 * c ** 1.0 + 1.364 * c ** 2.0 \
           - 11.388 * c ** 3.0 + 13.617 * c ** 4.0 - 5.146 * c ** 5.0


# 直達日射に対する規準化反射率の計算（単層ガラス）
def _get_rhod_n_single(theta_aoi_i_k) -> np.ndarray:

    cos = np.cos(theta_aoi_i_k)

    return 1.000 * cos ** 0.0 - 5.189 * cos ** 1.0 + 12.392 * cos ** 2.0 \
           - 16.593 * cos ** 3.0 + 11.851 * cos ** 4.0 - 3.461 * cos ** 5.0


# 直達日射に対する規準化透過率の計算（複層ガラス）
def _get_taud_n_double(theta_aoi_i_k: np.ndarray) -> np.ndarray:

    return _get_tau_norm_glass_i_k_n(
        theta_aoi_i_k=theta_aoi_i_k) ** 2.0 / (1.0 - _get_rhod_n_single(theta_aoi_i_k) ** 2.0)


def _get_rhod_n_double(theta_aoi_i_k: np.ndarray) -> np.ndarray:
    '''
    直達日射に対する規準化反射率の計算（複層ガラス）　JIS A2103-2014  (8)式
    :param theta_aoi_i_k: 入射角
    :return: 斜入射時の規準化反射率
    '''
    tau = _get_tau_norm_glass_i_k_n(theta_aoi_i_k=theta_aoi_i_k)
    rho = _get_rhod_n_single(theta_aoi_i_k=theta_aoi_i_k)
    return rho + tau ** 2.0 * rho / (1.0 - rho ** 2.0)


def _get_c_d_single() -> float:
    """
    透明な開口部の拡散日射に対する規準化透過率（単層ガラス）を定義する。

    Returns:
        透明な開口部の拡散日射に対する規準化透過率（単層ガラス）
    """

    return 0.900


def _get_r_d_single() -> float:
    """
    透明な開口部の拡散日射に対する規準化反射率（単層ガラス）を定義する。
    :return:
        透明な開口部の拡散日射に対する規準化反射率（単層ガラス）
    """

    return 0.061

def _get_c_d_double() -> float:
    """
    透明な開口部の拡散日射に対する規準化透過率（複層ガラス）を定義する。

    Returns:
        透明な開口部の拡散日射に対する規準化透過率（複層ガラス）
    """

    return 0.832


def _get_r_d_double() -> float:
    """
    透明な開口部の拡散日射に対する規準化反射率（複層ガラス）を定義する。
    :return:
        透明な開口部の拡散日射に対する規準化反射率（複層ガラス）
    """

    return 0.088


def get_tau_and_ashgc(eta_w: float, glazing_type_j: str,
                       glass_area_ratio: float) -> (float, float):
    """
    日射熱取得率から透過率、吸収日射取得率を推定する
    :param eta_w: 窓の日射熱取得率
    :param glazing_type_j: ガラスの層数
    :param glass_area_ratio: 窓のガラス面積率
    :return: 日射透過率、吸収日射取得率
    """

    # ガラスの日射熱取得率
    eta_g = eta_w / glass_area_ratio

    if glazing_type_j == "single":
        tau_g = 0.77 * eta_g ** 2 + 0.41 * eta_g - 0.09
    elif glazing_type_j == "multiple":
        tau_g = 0.99 * eta_g - 0.10
    else:
        raise ValueError()

    # 窓の日射透過率
    tau_w = tau_g * glass_area_ratio

    return tau_w, eta_w - tau_w


# TODO:吸収日射取得率の入射角特性は、1-τ-ρで暫定対応（τ：透過率の規準化透過率、ρ：反射率の規準化反射率）
def get_c_ashgc(glazing_type_j: str, theta_aoi_i_k: np.ndarray) -> np.ndarray:
    '''
    吸収日射取得率の直達日射に対する入射角特性を計算（規準化吸収日射取得率）
    :param glazing_type_j: ガラスの層数
    :param theta_aoi_i_k: 入射角
    :return: 規準化吸収日射取得率
    '''

    if glazing_type_j == "single":
        tau = _get_tau_norm_glass_i_k_n(theta_aoi_i_k=theta_aoi_i_k)
        rho = _get_rhod_n_single(theta_aoi_i_k=theta_aoi_i_k)
    elif glazing_type_j == "multiple":
        tau = _get_taud_n_double(theta_aoi_i_k=theta_aoi_i_k)
        rho = _get_rhod_n_double(theta_aoi_i_k=theta_aoi_i_k)
    else:
        raise ValueError()

    return np.maximum(1.0 - tau - rho, 0.0)


if __name__ == "__main__":
    phi = np.ndarray(1)
    phi[0] = math.radians(0.0)
    print(get_rho_d_j_ns(phi, 'multiple'))
    print(get_tau_d_j_ns(phi, 'multiple'))

