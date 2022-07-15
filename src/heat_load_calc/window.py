import math
from typing import Tuple
import numpy as np
from enum import Enum


class GlazingType(Enum):

    Single = 'single'
    Multiple = 'multiple'


class Window:

    def __init__(self, r_a_glass_j: float, eta_w_j: float, glazing_type_j: GlazingType):
        """

        Args:
            r_a_glass_j: 境界 j の開口部の面積に対するグレージングの面積の比, -
            eta_w_j: 境界 j の開口部の日射熱取得率, -
            glazing_type_j: 境界 ｊ の開口部のグレージングの種類

        """

        # 境界 j の開口部のグレージングの日射熱取得率, -
        eta_g_j = self._get_eta_g_j(eta_w_j=eta_w_j, r_a_glass_j=r_a_glass_j)

        # 境界 j の開口部のグレージングの日射透過率, -
        tau_g_j = self._get_tau_g_j(eta_g_j=eta_g_j, glazing_type_j=glazing_type_j)

        # 境界 j の開口部のグレージングの吸収日射熱取得率, -
        b_g_j = self._get_b_g_j(eta_g_j, tau_g_j)

        # 境界 j の開口部のグレージングの日射吸収率, -
        a_g_j = self._get_a_g_j(b_g_j=b_g_j, glazing_type_j=glazing_type_j, tau_g_j=tau_g_j)

        # 境界 j の開口部のグレージングの日射反射率, -
        rho_g_j = self._get_rho_g_j(a_g_j=a_g_j, tau_g_j=tau_g_j)

        tau_w_j = tau_g_j * r_a_glass_j

        ashgc_value = eta_w_j - tau_w_j

        a_w = a_g_j * r_a_glass_j

        rho_w = rho_g_j * r_a_glass_j

        self._r_a_glass_j = r_a_glass_j
        self._eta_w_j = eta_w_j
        self._glazing_type_j = glazing_type_j
        self._tau_value = tau_w_j
        self._ashgc_value = ashgc_value
        self._rho_value = rho_w
        self._a_value = a_w

    @property
    def glass_area_ratio(self):
        return self._r_a_glass_j

    @property
    def eta_value(self):
        return self._eta_w_j

    @property
    def glazing_type(self):
        return self._glazing_type_j

    @property
    def tau_value(self):
        return self._tau_value

    @property
    def ashgc_value(self):
        return self._ashgc_value

    @property
    def rho_value(self):
        return self._rho_value

    @property
    def a_value(self):
        return self._a_value

    @classmethod
    def _get_rho_g_j(cls, a_g_j: float, tau_g_j: float):
        """開口部のグレージングの日射反射率を取得する。

        Args:
            a_g_j: 境界 j の開口部のグレージングの日射吸収率, -
            tau_g_j: 境界 j の開口部のグレージングの日射透過率, -

        Returns:
            境界 j の開口部のグレージングの日射反射率, -
        """

        return 1.0 - tau_g_j - a_g_j

    @classmethod
    def _get_b_g_j(cls, eta_g_j: float, tau_g_j: float):
        """開口部のグレージングの吸収日射熱取得率を取得する。

        Args:
            eta_g_j: 境界 j の開口部のグレージングの日射熱取得率, -
            tau_g_j: 境界 j の開口部のグレージングの日射透過率, -

        Returns:
            境界 j の開口部のグレージングの吸収日射熱取得率, -
        """
        return eta_g_j - tau_g_j

    @classmethod
    def _get_eta_g_j(cls, eta_w_j: float, r_a_glass_j: float):
        """開口部のグレージングの日射熱取得率

        Args:
            eta_w_j: 境界 j の開口部の日射熱取得率, -
            r_a_glass_j: 境界 j の開口部の面積に対するグレージングの面積の比, -

        Returns:
            境界 j の開口部のグレージングの日射熱取得率, -
        """

        return eta_w_j / r_a_glass_j

    @classmethod
    def _get_a_g_j(cls, b_g_j: float, glazing_type_j: GlazingType, tau_g_j: float):
        """

        Args:
            b_g_j: 境界 j の開口部のグレージングの吸収日射熱取得率, -
            glazing_type_j: 境界 ｊ の開口部のグレージングの種類
            tau_g_j: 境界 j の開口部のグレージングの日射透過率, -

        Returns:

        """

        if glazing_type_j == GlazingType.Single:
            if tau_g_j + 3.01 * b_g_j < 1.0:
                return 3.01 * b_g_j
            else:
                return 1.0 - tau_g_j
        elif glazing_type_j == GlazingType.Multiple:
            if tau_g_j + 3.76 * b_g_j < 1.0:
                return 3.76 * b_g_j
            else:
                return 1.0 - tau_g_j
        else:
            raise ValueError()

    @classmethod
    def _get_tau_g_j(cls, eta_g_j: float, glazing_type_j: GlazingType):
        """開口部のグレージングの日射透過率を取得する。

        Args:
            eta_g_j: 境界 j の開口部のグレージングの日射熱取得率, -
            glazing_type_j: 境界 ｊ の開口部のグレージングの種類

        Returns:
            境界 j の開口部のグレージングの日射透過率, -
        """

        if glazing_type_j == GlazingType.Single:

            return -0.70 * eta_g_j ** 3 + 1.94 * eta_g_j ** 2 - 0.19 * eta_g_j

        elif glazing_type_j == GlazingType.Multiple:

            return -0.34 * eta_g_j ** 3 + 0.81 * eta_g_j ** 2 + 0.46 * eta_g_j

        else:

            KeyError()


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


# TODO:吸収日射取得率の入射角特性は、1-τ-ρで暫定対応（τ：透過率の規準化透過率、ρ：反射率の規準化反射率）
def get_c_ashgc(glazing_type_j: str, tau_w: float, rho_w: float) -> float:
    '''
    吸収日射取得率の拡散日射に対する入射角特性を計算（規準化吸収日射取得率）
    :param glazing_type_j: ガラスの層数
    :param tau_w: 窓の日射透過率
    :param rho_w: 窓の日射反射率
    :return: 規準化吸収日射取得率
    '''

    # 日射吸収率の計算
    a_w = 1.0 - tau_w - rho_w

    # 日射透過率、日射反射率の計算
    tau = tau_w * get_c_d_j(glazing_type_j=glazing_type_j)
    rho = rho_w + (1.0 - rho_w) * _get_r_d_j(glazing_type_j=glazing_type_j)

    return (1.0 - tau - rho) / a_w


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


# TODO:吸収日射取得率の入射角特性は、1-τ-ρで暫定対応（τ：透過率の規準化透過率、ρ：反射率の規準化反射率）
def get_ashgc_d_j(glazing_type_j: str, tau_w: float, rho_w: float, theta_aoi_i_k: np.ndarray) -> np.ndarray:
    '''
    吸収日射取得率の直達日射に対する入射角特性を計算（規準化吸収日射取得率）
    :param glazing_type_j: ガラスの層数
    :param tau_w: 窓の日射透過率
    :param rho_w: 窓の日射反射率
    :param theta_aoi_i_k: 入射角
    :return: 規準化吸収日射取得率
    '''

    # 日射吸収率の計算
    a_w = 1.0 - tau_w - rho_w

    # 日射透過率、日射反射率の計算
    tau = tau_w * get_tau_d_j_ns(theta_aoi_j_ns=theta_aoi_i_k, glazing_type_j=glazing_type_j)
    rho = rho_w + (1.0 - rho_w) * _get_rho_d_j_ns(theta_aoi_j_ns=theta_aoi_i_k, glazing_type_j=glazing_type_j)

    return (1.0 - tau - rho) / a_w


def _get_rho_d_j_ns(theta_aoi_j_ns: np.ndarray, glazing_type_j: str) -> np.ndarray:
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


def _get_r_d_j(glazing_type_j: str) -> float:
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

