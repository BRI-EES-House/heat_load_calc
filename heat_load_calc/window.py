from enum import Enum, auto
from typing import Optional, Tuple, Union, TypeVar
from math import sin, cos, pi
import numpy as np
from abc import ABC, abstractmethod

T = TypeVar("T", float, np.ndarray)

class FlameType(Enum):
    """フレーム材質
    """

    # 樹脂製製建具
    RESIN = auto()
    # 木製建具
    WOOD = auto()
    # 木と金属の複合材料製建具
    MIXED_WOOD = auto()
    # 樹脂と金属の複合材料製建具
    MIXED_RESIN = auto()
    # 金属製建具
    ALUMINUM = auto()

    def get_default_r_a_w_g(self) -> float:
        """Get the ratio of area of glazing to window.

        Returns:
            境界jの窓の面積に対するグレージングの面積の比
        """

        return {
            FlameType.RESIN: 0.72,
            FlameType.WOOD: 0.72,
            FlameType.ALUMINUM: 0.8,
            FlameType.MIXED_WOOD: 0.8,
            FlameType.MIXED_RESIN: 0.8
        }[self]
    
    def get_u_w_f_j(self) -> float:
        """建具部分の熱損失係数（U値）を取得する。
        Args:
            flame_type: 建具（フレーム）材質の種類
        Returns:
            境界jの窓の建具部分の熱損失係数（U値）, W/m2K
        Notes:
            table 4
        """

        return {
            FlameType.RESIN: 2.2,
            FlameType.WOOD: 2.2,
            FlameType.ALUMINUM: 6.6,
            FlameType.MIXED_WOOD: 4.7,
            FlameType.MIXED_RESIN: 4.7
        }[self]


class GlassType(Enum):
    """ガラスの構成
    """

    # 単層
    SINGLE = 'single'
    # 複層
    MULTIPLE = 'multiple'


class Glazing(ABC):

    # The number of segments
    # for numerical integration to calculate the difference in sky radiation transmittance
    M = 1000

    @classmethod
    def create(cls, t_glz_j: GlassType, u_w_g_j: float, eta_w_g_j: float):
        """create class

        Args:
            t_glz_j: GlassType
            u_w_g_j: u value of glazing(normal, at winter condition), W/m2K
            eta_w_g_j: eta value of glazing
        """

        match t_glz_j:

            case GlassType.SINGLE:

                return SingleGlazing(u_w_g_j=u_w_g_j, eta_w_g_j=eta_w_g_j)

            case GlassType.MULTIPLE:

                # When glass type is multiple, double glazing is assumed as multiple in this calculation.
                return DoubleGlazing(u_w_g_j=u_w_g_j, eta_w_g_j=eta_w_g_j)
    
    @abstractmethod
    def get_b_w_g_j_phis(self, phis: T) -> T:
        pass

    @abstractmethod
    def get_tau_w_g_j_phis(self, phis: T) -> T:
        pass

    def get_tau_w_g_c_j(self) -> float:
        """Calculate solar transmittance of a quarter-sphere for uniformly diffuse solar radiation.

        Returns:
            solar transmittance of quarter-sphere for uniformly diffuse solar radiation
        """

        phi_ms = self._get_phi_ms()

        return np.pi / self.M * np.sum(self.get_tau_w_g_j_phis(phis=phi_ms) * np.sin(phi_ms) * np.cos(phi_ms))

    def get_b_w_g_c_j(self) -> float:
        """Calculate absorbed solar heat of a quater-sphere for uniformly diffuse solar radiation.

        Returns:
            absorbed solar heat of quater-sphere for uniformly diffuse solar radiation
        """

        phi_ms = self._get_phi_ms()

        return np.pi / self.M * np.sum(self.get_b_w_g_j_phis(phis=phi_ms) * np.sin(phi_ms) * np.cos(phi_ms))

    @classmethod
    def _get_phi_ms(cls):

        M = cls.M

        ms = np.arange(1, M + 1)

        return np.pi / 2 * (ms - 1 / 2) / M
        

class SingleGlazing(Glazing):

    def __init__(self, u_w_g_j: float, eta_w_g_j: float):

        # thermal resistance of surface, m2K/W
        r_w_o_w, r_w_i_w, r_w_o_s, r_w_i_s = _get_r_w()

        # u value of glazing(at summer condition), W/m2K
        u_w_g_s_j = _get_u_w_g_s_j(u_w_g_j=u_w_g_j, r_w_o_w=r_w_o_w, r_w_i_w=r_w_i_w, r_w_o_s=r_w_o_s, r_w_i_s=r_w_i_s)

        # ratio of inside heat flow to absorbed heat of glazing
        r_r_w_g_j = self._get_r_r_w_g_j(u_w_g_j=u_w_g_j, u_w_g_s_j=u_w_g_s_j, r_w_o_w=r_w_o_w, r_w_i_w=r_w_i_w, r_w_o_s=r_w_o_s)

        # reflectance of the first plate glass (front side) from the exterior side
        rho_w_g_s1f_j = _get_rho_w_g_s1f_j(r_r_w_g_j=r_r_w_g_j, eta_w_g_j=eta_w_g_j)

        # solar transmittance
        tau_w_g_j = self._get_tau_w_g_j(eta_w_g_j=eta_w_g_j, r_r_w_g_j=r_r_w_g_j, rho_w_g_s1f_j=rho_w_g_s1f_j)

        # solar transmittance of the first plate glass from the exterior side
        tau_w_g_s1_j = self._get_tau_w_g_s1_j(tau_w_g_j=tau_w_g_j)

        # u value of glazing(at summer condition), W/m2K
        self._u_w_g_s_j = u_w_g_s_j

        # ratio of inside heat flow to absorbed heat of glazing
        self._r_r_w_g_j = r_r_w_g_j

        # reflectance of the first plate glass (front side) from the exterior side
        self._rho_w_g_s1f_j = rho_w_g_s1f_j

        # solar transmittance
        self._tau_w_g_j = tau_w_g_j

        # solar transmittance of the first plate glass from the exterior side
        self._tau_w_g_s1_j = tau_w_g_s1_j

    def get_b_w_g_j_phis(self, phis: T) -> T:
        """入射角Φに対する境界jの窓のガラス部分の吸収日射熱取得率を取得する。
        Args:
            phis: ステップnにおける入射角, rad
        Returns:
            入射角Φに対する境界jの窓のガラス部分の吸収日射熱取得率, -
        Notes:
            eq.11
        """
        tau_w_g_j_phis = self.get_tau_w_g_j_phis(phis=phis)
        rho_w_g_j_phis = self._get_rho_w_g_j_phis(phis=phis)
        return (1 - tau_w_g_j_phis - rho_w_g_j_phis) * self._r_r_w_g_j

    def get_tau_w_g_j_phis(self, phis: T) -> T:
        """入射角Φに対する境界jの窓のガラス部分の日射透過率を計算する。
        Args:
            phis: 入射角Φ, rad
        Returns:
            入射角Φに対する境界jの窓のガラス部分の日射透過率, -
        Notes:
            eq.12
            単層版
        """

        tau_w_g_s1_j_phis = self._get_tau_w_g_s1_j_phis(phis=phis)
        return tau_w_g_s1_j_phis

    def _get_rho_w_g_j_phis(self, phis: T) -> T:
        """入射角Φに対する境界jの窓のガラス部分の日射反射率を計算する。
        Args:
            phis: 入射角, rad
        Returns:
            入射角Φに対する境界jの窓のガラス部分の日射反射率, -
        Notes:
            eq.13
            単層版
        """

        rho_w_g_s1f_j_phis = self._get_rho_w_g_s1f_j_phis(phis=phis)
        return rho_w_g_s1f_j_phis

    def _get_tau_w_g_s1_j_phis(self, phis: T) -> T:
        """入射角Φに対する境界jの窓のガラス部分の室外側から1枚目の板ガラスの透過率を計算する。
        Args:
            phis: 入射角Φ, rad
        Returns:
            入射角Φに対する境界jの窓のガラス部分の室外側から1枚目の板ガラスの透過率, -
        Notes:
            eq.14
        """
        return self._tau_w_g_s1_j * _get_tau_n_phi(phi=phis)

    def _get_rho_w_g_s1f_j_phis(self, phis: T) -> T:
        """入射角Φに対する境界jの窓のガラス部分の室外側から1枚目の板ガラスの反射率（正面側）を計算する。
        Args:
            phis: 入射角Φ, rad
        Returns:
            入射角Φに対する境界jの窓のガラス部分の室外側から1枚目の板ガラスの反射率（正面側）, -
        Notes:
            eq.16
        """
        return self._rho_w_g_s1f_j + (1 - self._rho_w_g_s1f_j) * _get_rho_n_phi(phi_ns=phis)

    @staticmethod
    def _get_r_r_w_g_j(u_w_g_j: float, u_w_g_s_j: float, r_w_o_w: float, r_w_i_w: float, r_w_o_s: float) -> float:
        """境界jの窓のガラス部分の日射吸収量に対する室内側に放出される量の割合を計算する。
        Args:
            u_w_g_j: 境界jの窓のガラス部分の熱損失係数（U値）, W/m2K
            u_w_g_s_j: 境界jの窓のガラス部分の熱損失係数（夏期条件）, W/m2K
            r_w_o_w: 窓の室外側表面熱伝達抵抗（冬期条件）, m2K/W
            r_w_i_w: 窓の室内側表面熱伝達抵抗（冬期条件）, m2K/W
            r_w_o_s: 窓の室外側表面熱伝達抵抗（夏期条件）, m2K/W
        Returns:
            境界jの窓のガラス部分の日射吸収量に対する室内側に放出される量の割合, -
        Notes:
            eq.28
        """

        return (1 / 2 * (1 / u_w_g_j - r_w_o_w - r_w_i_w) + r_w_o_s) * u_w_g_s_j

    @staticmethod
    def _get_tau_w_g_j(eta_w_g_j: float, r_r_w_g_j: float, rho_w_g_s1f_j: float) -> float:
        """窓のガラス部分の日射透過率を計算する。
        Args:
            eta_w_g_j: 境界jの窓のガラス部分の日射熱取得率, -
            r_r_w_g_j: 境界jの窓のガラス部分の日射吸収量に対する室内側に放出される量の割合, -
            rho_w_g_s1f_j: 境界jの窓のガラス部分の室外側から1枚目の板ガラスの反射率（正面側）, -
        Returns:
            境界jの窓のガラス部分の日射透過率, -
        Notes:
            eq.24
            単層ガラス用
        """

        return (eta_w_g_j - (1 - rho_w_g_s1f_j) * r_r_w_g_j) / (1 - r_r_w_g_j)

    @staticmethod
    def _get_tau_w_g_s1_j(tau_w_g_j: float) -> float:
        """境界jの窓のガラス部分の室外側から1枚目の板ガラスの透過率を計算する。

        Args:
            tau_w_g_j: 境界jの窓のガラス部分の日射透過率, -

        Returns:
            境界jの窓のガラス部分の室外側から1枚目の板ガラスの透過率, -
        Notes:
            eq.23
            単層用
        """

        return tau_w_g_j


class DoubleGlazing(Glazing):

    def __init__(self, u_w_g_j: float, eta_w_g_j: float):

        # thermal resistance of surface, m2K/W
        r_w_o_w, r_w_i_w, r_w_o_s, r_w_i_s = _get_r_w()

        # u value of glazing(at summer condition), W/m2K
        u_w_g_s_j = _get_u_w_g_s_j(u_w_g_j=u_w_g_j, r_w_o_w=r_w_o_w, r_w_i_w=r_w_i_w, r_w_o_s=r_w_o_s, r_w_i_s=r_w_i_s)

        # ratio of inside heat flow to absorbed heat of glazing
        r_r_w_g_j = self._get_r_r_w_g_j(u_w_g_j=u_w_g_j, u_w_g_s_j=u_w_g_s_j, r_w_o_w=r_w_o_w, r_w_i_w=r_w_i_w, r_w_o_s=r_w_o_s)

        # reflectance of the first plate glass (front side) from the exterior side
        rho_w_g_s1f_j = _get_rho_w_g_s1f_j(r_r_w_g_j=r_r_w_g_j, eta_w_g_j=eta_w_g_j)

        # reflectance of the second plate glass (front side) from the exterior side
        rho_w_g_s2f_j = _get_rho_w_g_s2f_j()

        # solar transmittance
        tau_w_g_j = self._get_tau_w_g_j(eta_w_g_j=eta_w_g_j, r_r_w_g_j=r_r_w_g_j, rho_w_g_s1f_j=rho_w_g_s1f_j, rho_w_g_s2f_j=rho_w_g_s2f_j)

        # solar transmittance of the first plate glass from the exterior side
        tau_w_g_s1_j = self._get_tau_w_g_s1_j(tau_w_g_j=tau_w_g_j, rho_w_g_s2f_j=rho_w_g_s2f_j)

        # solar transmittance of the second plate glass from the exterior side
        tau_w_g_s2_j = _get_tau_w_g_s2_j(tau_w_g_s1_j=tau_w_g_s1_j)

        # reflectance (back side) of the first sheet of plate glass on the exterior side
        rho_w_g_s1b_j = _get_rho_w_g_s1b_j(tau_w_g_s1_j=tau_w_g_s1_j)

        # u value of glazing(at summer condition), W/m2K
        self._u_w_g_s_j = u_w_g_s_j

        # ratio of inside heat flow to absorbed heat of glazing
        self._r_r_w_g_j = r_r_w_g_j

        # reflectance of the first plate glass (front side) from the exterior side
        self._rho_w_g_s1f_j = rho_w_g_s1f_j

        # reflectance of the second plate glass (front side) from the exterior side
        self._rho_w_g_s2f_j = rho_w_g_s2f_j

        # solar transmittance
        self._tau_w_g_j = tau_w_g_j

        # solar transmittance of the first plate glass from the exterior side
        self._tau_w_g_s1_j = tau_w_g_s1_j

        # solar transmittance of the second plate glass from the exterior side
        self._tau_w_g_s2_j = tau_w_g_s2_j

        # reflectance (back side) of the first sheet of plate glass on the exterior side
        self._rho_w_g_s1b_j = rho_w_g_s1b_j

    def get_b_w_g_j_phis(self, phis: T) -> T:
        """入射角Φに対する境界jの窓のガラス部分の吸収日射熱取得率を取得する。
        Args:
            phis: ステップnにおける入射角, rad
        Returns:
            入射角Φに対する境界jの窓のガラス部分の吸収日射熱取得率, -
        Notes:
            eq.11
        """
        tau_w_g_j_phis = self.get_tau_w_g_j_phis(phis=phis)
        rho_w_g_j_phis = self._get_rho_w_g_j_phis(phis=phis)
        return (1 - tau_w_g_j_phis - rho_w_g_j_phis) * self._r_r_w_g_j

    def get_tau_w_g_j_phis(self, phis: T) -> T:
        """入射角Φに対する境界jの窓のガラス部分の日射透過率を計算する。
        Args:
            phis: 入射角Φ, rad
        Returns:
            入射角Φに対する境界jの窓のガラス部分の日射透過率, -
        Notes:
            eq.12
            複層版
        """

        rho_w_g_s1b_j_phis = self._get_rho_w_g_s1b_j_phis(phis=phis)
        rho_w_g_s2f_j_phis = self._get_rho_w_g_s2f_j_phis(phis=phis)
        tau_w_g_s1_j_phis = self._get_tau_w_g_s1_j_phis(phis=phis)
        tau_w_g_s2_j_phis = self._get_tau_w_g_s2_j_phis(phis=phis)
        return tau_w_g_s1_j_phis * tau_w_g_s2_j_phis / (1 - np.minimum(rho_w_g_s1b_j_phis * rho_w_g_s2f_j_phis, 0.9999))

    def _get_rho_w_g_j_phis(self, phis: T) -> T:
        """入射角Φに対する境界jの窓のガラス部分の日射反射率を計算する。
        Args:
            phis: 入射角, rad
        Returns:
            入射角Φに対する境界jの窓のガラス部分の日射反射率, -
        Notes:
            eq.13
            複層版
        """

        rho_w_g_s1f_j_phis = self._get_rho_w_g_s1f_j_phis(phis=phis)
        rho_w_g_s1b_j_phis = self._get_rho_w_g_s1b_j_phis(phis=phis)
        rho_w_g_s2f_j_phis = self._get_rho_w_g_s2f_j_phis(phis=phis)
        tau_w_g_s1_j_phis = self._get_tau_w_g_s1_j_phis(phis=phis)
        tau_w_g_s2_j_phis = self._get_tau_w_g_s2_j_phis(phis=phis)
        return rho_w_g_s1f_j_phis + tau_w_g_s1_j_phis * tau_w_g_s2_j_phis * rho_w_g_s2f_j_phis / (
                    1 - np.minimum(rho_w_g_s1b_j_phis * rho_w_g_s2f_j_phis, 0.9999))

    def _get_tau_w_g_s1_j_phis(self, phis: T) -> T:
        """入射角Φに対する境界jの窓のガラス部分の室外側から1枚目の板ガラスの透過率を計算する。
        Args:
            phis: 入射角Φ, rad
        Returns:
            入射角Φに対する境界jの窓のガラス部分の室外側から1枚目の板ガラスの透過率, -
        Notes:
            eq.14
        """
        return self._tau_w_g_s1_j * _get_tau_n_phi(phi=phis)

    def _get_tau_w_g_s2_j_phis(self, phis: T) -> T:
        """入射角Φに対する境界jの窓のガラス部分の室外側から2枚目の板ガラスの透過率を計算する。
        Args:
            phis: 入射角Φ, rad
        Returns:
            入射角Φに対する境界jの窓のガラス部分の室外側から2枚目の板ガラスの透過率, -
        Notes:
            この値は複層ガラスのみ計算される。
            eq.15
        """
        return self._tau_w_g_s2_j * _get_tau_n_phi(phi=phis)

    def _get_rho_w_g_s1f_j_phis(self, phis: T) -> T:
        """入射角Φに対する境界jの窓のガラス部分の室外側から1枚目の板ガラスの反射率（正面側）を計算する。
        Args:
            phis: 入射角Φ, rad
        Returns:
            入射角Φに対する境界jの窓のガラス部分の室外側から1枚目の板ガラスの反射率（正面側）, -
        Notes:
            eq.16
        """
        return self._rho_w_g_s1f_j + (1 - self._rho_w_g_s1f_j) * _get_rho_n_phi(phi_ns=phis)

    def _get_rho_w_g_s1b_j_phis(self, phis: T) -> T:
        """入射角Φに対する境界jの窓のガラス部分の室外側から1枚目の板ガラスの反射率（背面側）を計算する。
        Args:
            phis: 入射角Φ, rad
        Returns:
            入射角Φに対する境界jの窓のガラス部分の室外側から1枚目の板ガラスの反射率（背面側）, -
        Notes:
            この値は複層ガラスのみ計算される。
            eq.17
        """
        return self._rho_w_g_s1b_j + (1 - self._rho_w_g_s1b_j) * _get_rho_n_phi(phi_ns=phis)

    def _get_rho_w_g_s2f_j_phis(self, phis: T) -> T:
        """入射角Φに対する境界jの窓のガラス部分の室外側から2枚目の板ガラスの反射率（正面側）を計算する。
        Args:
            phis: 入射角Φ, rad
        Returns:
            入射角Φに対する境界jの窓のガラス部分の室外側から2枚目の板ガラスの反射率（正面側）, -
        Notes:
            この値は複層ガラスのみ計算される。
            eq.18
        """
        return self._rho_w_g_s2f_j + (1 - self._rho_w_g_s2f_j) * _get_rho_n_phi(phi_ns=phis)


    @staticmethod
    def _get_r_r_w_g_j(u_w_g_j: float, u_w_g_s_j: float, r_w_o_w: float, r_w_i_w: float, r_w_o_s: float) -> float:
        """境界jの窓のガラス部分の日射吸収量に対する室内側に放出される量の割合を計算する。
        Args:
            u_w_g_j: 境界jの窓のガラス部分の熱損失係数（U値）, W/m2K
            u_w_g_s_j: 境界jの窓のガラス部分の熱損失係数（夏期条件）, W/m2K
            r_w_o_w: 窓の室外側表面熱伝達抵抗（冬期条件）, m2K/W
            r_w_i_w: 窓の室内側表面熱伝達抵抗（冬期条件）, m2K/W
            r_w_o_s: 窓の室外側表面熱伝達抵抗（夏期条件）, m2K/W
        Returns:
            境界jの窓のガラス部分の日射吸収量に対する室内側に放出される量の割合, -
        Notes:
            eq.28
        """

        # 複層ガラスにおける窓の中空層の熱伝達抵抗, m2K/W
        r_w_air = 0.003
        return (1 / 4 * (1 / u_w_g_j - r_w_o_w - r_w_i_w - r_w_air) + r_w_o_s) * u_w_g_s_j

    @staticmethod
    def _get_tau_w_g_j(eta_w_g_j: float, r_r_w_g_j: float, rho_w_g_s1f_j: float, rho_w_g_s2f_j: float) -> float:
        """窓のガラス部分の日射透過率を計算する。
        Args:
            eta_w_g_j: 境界jの窓のガラス部分の日射熱取得率, -
            r_r_w_g_j: 境界jの窓のガラス部分の日射吸収量に対する室内側に放出される量の割合, -
            rho_w_g_s1f_j: 境界jの窓のガラス部分の室外側から1枚目の板ガラスの反射率（正面側）, -
            rho_w_g_s2f_j: 境界jの窓のガラス部分の室外側から2枚目の板ガラスの反射率（正面側）, -
        Returns:
            境界jの窓のガラス部分の日射透過率, -
        Notes:
            eq.24
            複層ガラス用
        """

        return (eta_w_g_j - (1 - rho_w_g_s1f_j) * r_r_w_g_j) / ((1 - r_r_w_g_j) - rho_w_g_s2f_j * r_r_w_g_j)

    @staticmethod
    def _get_tau_w_g_s1_j(tau_w_g_j: float, rho_w_g_s2f_j: float) -> float:
        """境界jの窓のガラス部分の室外側から1枚目の板ガラスの透過率を計算する。
        Args:
            tau_w_g_j: 境界jの窓のガラス部分の日射透過率, -
            rho_w_g_s2f_j: 境界jの窓のガラス部分の室外側から2枚目の板ガラスの反射率（正面側）, -

        Returns:
            境界jの窓のガラス部分の室外側から1枚目の板ガラスの透過率, -

        Notes:
            eq.23
        """

        return (0.379 * rho_w_g_s2f_j * tau_w_g_j + ((0.379 * rho_w_g_s2f_j * tau_w_g_j) ** 2 - 4 * (0.379 * rho_w_g_s2f_j - 1) * tau_w_g_j) ** 0.5) / 2


class Window:
    """窓を表すクラス
    """

    def __init__(
            self,
            u_w_std_j: float,
            eta_w_std_j: float,
            t_glz_j: GlassType,
            r_a_w_g_j: Optional[float] = None,
            t_flame: FlameType = FlameType.MIXED_WOOD
        ):
        """

        Args:
            u_w_std_j: standard heat transmittance coefficient (U value) of boundary j / 境界jの窓の熱損失係数, W/m2K
            eta_w_j: solar gain ratio (eta value) of boundary j / 境界 j の窓の日射熱取得率, -
            t_glz_j: grazing type of boundary j / 境界jの窓ガラスの種類
            r_a_w_g_j: grazing area ratio of boundary i / 境界jの窓の面積に対するグレージングの面積の比, -
            t_flame: _description_. Defaults to FlameType.MIXED.
        """

        # u value of flame, W/m2K
        u_w_f_j = t_flame.get_u_w_f_j()

        # ratio of glazing area to window area
        r_a_w_g_j = _get_r_a_w_g_j(r_a_w_g_j=r_a_w_g_j, flame_type=t_flame)

        # u value of glazing(normal, at winter condition), W/m2K
        u_w_g_j = _get_u_w_g_j(u_w_j=u_w_std_j, u_w_f_j=u_w_f_j, r_a_w_g_j=r_a_w_g_j)

        # eta value of glazing
        eta_w_g_j = _get_eta_w_g_j(eta_w_j=eta_w_std_j, r_a_w_g_j=r_a_w_g_j)

        glazing = Glazing.create(t_glz_j=t_glz_j, u_w_g_j=u_w_g_j, eta_w_g_j=eta_w_g_j)

        # u value of flame, W/m2K
        self._u_w_f_j = u_w_f_j

        # ratio of glazing area to window area
        self._r_a_w_g_j = r_a_w_g_j

        # u value of glazing(normal, at winter condition), W/m2K
        self._u_w_g_j = u_w_g_j

        # eta value of glazing
        self._eta_w_g_j = eta_w_g_j

        # solar transmittance of glazing
        self._tau_w_g_j = glazing._tau_w_g_j

        # glazing
        self._glazing = glazing

        # solar transmittance of quarter-sphere for uniformly diffuse solar radiation
        self._tau_w_c_j = self._get_tau_w_c_j()

        # absorbed solar heat of quater-sphere for uniformly diffuse solar radiation
        self._b_w_c_j = self._get_b_w_c_j()

    @property
    def glazing(self):
        """glazing of window"""
        return self._glazing

    @property
    def tau_w_s_j(self) -> float:
        """境界jの窓の天空日射に対する日射透過率, -
        
        Notes:
            eq.3
        """
        return self._tau_w_c_j

    @property
    def tau_w_r_j(self) -> float:
        """境界jの窓の地面反射日射に対する日射透過率, -
        Notes:
            eq.4
        """
        return self._tau_w_c_j

    @property
    def b_w_s_j(self):
        """境界jの窓の天空日射に対する吸収日射熱取得率, -
        Notes:
            eq.5
        """
        return self._b_w_c_j

    @property
    def b_w_r_j(self):
        """窓の地面反射に対する吸収日射熱取得率を取得する。
        Notes:
            eq.6
        """
        return self._b_w_c_j

    def get_tau_w_d_j_ns(self, phi_j_ns: T) -> T:
        """窓の直達日射に対する日射透過率を計算する。

        Args:
            phi_j_ns: ステップnにおける境界jの窓の直達日射の入射角, rad, [N+1]

        Returns:
            ステップnにおける境界jの窓の直達日射に対する日射透過率, -, [N+1]

        Notes:
            eq.1
        """

        return self._get_tau_w_j_phis(phis=phi_j_ns)

    def get_b_w_d_j_ns(self, phi_j_ns: T) -> T:
        """窓の直達日射に対する吸収日射熱取得率を計算する。

        Args:
            phi_j_ns: ステップnにおける境界jの窓の直達日射の入射角, rad, [N+1]

        Returns:
            ステップnにおける境界jの窓の直達日射に対する吸収日射熱取得率, [n]

        Notes:
            eq.2
        """

        return self._get_b_w_j_phis(phis=phi_j_ns)

    def _get_tau_w_c_j(self) -> float:
        """境界jの窓の1/4球の一様拡散日射に対する日射透過率を計算する。

        Returns:
            境界jの窓の1/4球の一様拡散日射に対する日射透過率, -

        Notes:
            eq.7
        """

        tau_w_g_c_j = self.glazing.get_tau_w_g_c_j()

        return tau_w_g_c_j * self._r_a_w_g_j
        
    def _get_b_w_c_j(self) -> float:
        """境界jの窓の1/4球の一様拡散日射に対する吸収日射熱取得率を計算する。

        Returns:
            境界jの窓の1/4球の一様拡散日射に対する吸収日射熱取得率, -

        Notes:
            eq.8
        """

        b_w_g_c_j = self.glazing.get_b_w_g_c_j()

        return b_w_g_c_j * self._r_a_w_g_j

    def _get_tau_w_j_phis(self, phis: T) -> T:
        """入射角Φに対する境界jの窓の日射透過率を取得する。
        Args:
            phis: 入射角Φ, rad
        Returns:
            入射角Φに対する境界jの窓の日射透過率, -
        Notes:
            eq.9
        """
        return self._glazing.get_tau_w_g_j_phis(phis=phis) * self.r_a_w_g_j

    def _get_b_w_j_phis(self, phis: T) -> T:
        """入射角Φに対する境界jの窓の吸収日射熱取得率を取得する。
        Args:
            phis: 入射角Φ, rad
        Returns:
            入射角Φに対する境界jの窓の吸収日射熱取得率, -
        Notes:
            eq.10
        """
        return self._glazing.get_b_w_g_j_phis(phis=phis) * self._r_a_w_g_j

    @property
    def u_w_f_j(self):
        """建具部分の熱損失係数（U値）を取得する。

        Returns:
            境界 j の窓の建具部分の熱損失係数（U値）, W/m2K
        """
        return self._u_w_f_j

    @property
    def r_a_w_g_j(self):
        """窓の面積に対するグレージングの面積の比を取得する。

        Returns:
            境界 j の窓の面積に対するグレージングの面積の比, -
        """
        return self._r_a_w_g_j

    @property
    def u_w_g_j(self):
        """窓のガラス部分の熱損失係数（U値）を取得する。

        Returns:
            境界 j の窓のガラス部分の熱損失係数（U値）, W/m2K
        """
        return self._u_w_g_j

    @property
    def eta_w_g_j(self):
        """窓のガラス部分の日射熱取得率を取得する。

        Returns:
            境界 j の窓のガラス部分の日射熱取得率, -
        """
        return self._eta_w_g_j

    @property
    def tau_w_g_j(self):
        """窓のガラス部分の日射透過率を取得する。

        Returns:
            境界 j の窓のガラス部分の日射透過率, -
        """
        return self._tau_w_g_j


def _get_tau_n_phi(phi: T) -> T:
    """規準化透過率を計算する。
    Args:
        phi: 入射角Φ, rad
    Returns:
        入射角Φに対する規準化透過率, -
    Notes:
        eq.19
    """
    return 2.552 * np.cos(phi) + 1.364 * np.power(np.cos(phi), 2) - 11.388 * np.power(np.cos(phi), 3) \
        + 13.617 * np.power(np.cos(phi), 4) - 5.146 * np.power(np.cos(phi), 5)


def _get_rho_n_phi(phi_ns: T) -> T:
    """規準化反射率を計算する。
    Args:
        phi: 入射角Φ, rad
    Returns:
        入射角Φに対する規準化反射率, -
    Notes:
        eq.20
    """
    return 1.0 - 5.189 * np.cos(phi_ns) + 12.392 * np.power(np.cos(phi_ns), 2) - 16.593 * np.power(np.cos(phi_ns), 3) \
           + 11.851 * np.power(np.cos(phi_ns), 4) - 3.461 * np.power(np.cos(phi_ns), 5)


def _get_rho_w_g_s1b_j(tau_w_g_s1_j: float) -> float:
    """境界jの窓のガラス部分の室外側から1枚目の板ガラスの反射率（背面側）を計算する。

    Args:
        tau_w_g_s1_j: 境界jの窓のガラス部分の室外側から1枚目の板ガラスの透過率, -
        
    Returns:
        境界jの窓のガラス部分の室外側から1枚目の板ガラスの反射率（背面側）, -
    Notes:
        複層ガラスの場合のみ定義される。
        eq.21
    """

    return 0.379 * (1 - tau_w_g_s1_j)


def _get_tau_w_g_s2_j(tau_w_g_s1_j: float) -> float:
    """境界jの窓のガラス部分の室外側から2枚目の板ガラスの透過率を計算する。

    Args:
        tau_w_g_s1_j: 境界jの窓のガラス部分の室外側から1枚目の板ガラスの透過率, -

    Returns:
        境界jの窓のガラス部分の室外側から2枚目の板ガラスの透過率, -
    Notes:
        複層ガラスの場合のみ定義される。
        eq.22
    """
    
    return tau_w_g_s1_j


def _get_rho_w_g_s2f_j() -> float:
    """境界jの窓のガラス部分の室外側から2枚目の板ガラスの反射率（正面側）を計算する。

    Returns:
        境界jの窓のガラス部分の室外側から2枚目の板ガラスの反射率（正面側）

    Notes:
        複層ガラスの場合のみ定義される。
        eq.25
    """
 
    return 0.077


def _get_rho_w_g_s1f_j(r_r_w_g_j: float, eta_w_g_j: float) -> float:
    """境界jの窓のガラス部分の室外側から1枚目の板ガラスの反射率（正面側）を計算する。

    Args:
        r_r_w_g_j: 境界jの窓のガラス部分の日射吸収量に対する室内側に放出される量の割合, -
        eta_w_g_j: 境界jの窓のガラス部分の日射熱取得率, -
    Returns:
        境界jの窓のガラス部分の室外側から1枚目の板ガラスの反射率（正面側）, -
    Notes:
        eq.26, 27
    """
    t_j = (-1.846 * r_r_w_g_j + ((1.846 * r_r_w_g_j) ** 2 + 4 * (1 - 1.846 * r_r_w_g_j) * eta_w_g_j) ** 0.5) / (
                2 * (1 - 1.846 * r_r_w_g_j))
    return 0.923 * (t_j ** 2) - 1.846 * t_j + 1


def _get_u_w_g_s_j(u_w_g_j: float, r_w_o_w: float, r_w_i_w: float, r_w_o_s: float, r_w_i_s: float) -> float:
    """境界jの窓のガラス部分の熱損失係数（夏期条件）を計算する。
    Args:
        u_w_g_j: 境界jの窓のガラス部分の熱損失係数（U値）, W/m2K
        r_w_o_w: 窓の室外側表面熱伝達抵抗（冬期条件）, m2K/W
        r_w_i_w: 窓の室内側表面熱伝達抵抗（冬期条件）, m2K/W
        r_w_o_s: 窓の室外側表面熱伝達抵抗（夏期条件）, m2K/W
        r_w_i_s: 窓の室内側表面熱伝達抵抗（夏期条件）, m2K/W
    Returns:
        境界jの窓のガラス部分の熱損失係数（夏期条件）, W/m2K
    Notes:
        eq.29
    """
    return 1 / (1 / u_w_g_j - r_w_o_w - r_w_i_w + r_w_o_s + r_w_i_s)


def _get_r_w() -> Tuple[float, float, float, float]:
    """窓の表面熱伝達抵抗を求める。
    Returns:
        窓の室外側表面熱伝達抵抗（冬季条件）, m2K/W
        窓の室内側表面熱伝達抵抗（冬季条件）, m2K/W
        窓の室外側表面熱伝達抵抗（夏季条件）, m2K/W
        窓の室内側表面熱伝達抵抗（夏季条件）, m2K/W
    Notes:
        table 2
    """
    r_w_o_w = 0.0415
    r_w_i_w = 0.1228
    r_w_o_s = 0.0756
    r_w_i_s = 0.1317
    return r_w_o_w, r_w_i_w, r_w_o_s, r_w_i_s


def _get_eta_w_g_j(eta_w_j: float, r_a_w_g_j: float) -> float:
    """境界jの窓のガラス部分の日射熱取得率を取得する。
    Args:
        eta_w_j: 境界 j の窓の日射熱取得率
        r_a_w_g_j: 境界 j の窓の面積に対するグレージングの面積の比, -
    Returns:
        境界jの窓のガラス部分の日射熱取得率, -
    Notes:
        eq.30
    """
    return eta_w_j / r_a_w_g_j


def _get_u_w_g_j(u_w_j: float, u_w_f_j: float, r_a_w_g_j: float) -> float:
    """境界jの窓のガラス部分の熱損失係数（U値）を取得する。
    Args:
        u_w_j: 境界jの窓の熱損失係数, W/m2K
        u_w_f_j: 境界jの窓の建具部分の熱損失係数（U値）, W/m2K
        r_a_w_g_j: 境界jの窓の面積に対するグレージングの面積の比, -
    Returns:
        境界jの窓のガラス部分の熱損失係数（U値）, W/m2K
    Notes:
        eq.31
    """
    return (u_w_j - u_w_f_j * (1 - r_a_w_g_j)) / r_a_w_g_j


def _get_r_a_w_g_j(r_a_w_g_j: Optional[float], flame_type: FlameType) -> float:
    """窓の面積に対するグレージングの面積の比が指定されていない場合に枠（フレーム）材質の種類に応じてデフォルト値を定める。

    Args:
        r_a_w_g_j: 境界jの窓の面積に対するグレージングの面積の比, -
        flame_type: 建具（フレーム）材質の種類
    Returns:
        境界jの窓の面積に対するグレージングの面積の比, -
    Notes:
        table 3
    """

    if r_a_w_g_j is None:
        return flame_type.get_default_r_a_w_g()
    else:
        return r_a_w_g_j


def _get_u_w_f_j(flame_type: FlameType) -> float:
    """建具部分の熱損失係数（U値）を取得する。
    Args:
        flame_type: 建具（フレーム）材質の種類
    Returns:
        境界jの窓の建具部分の熱損失係数（U値）, W/m2K
    Notes:
        table 4
    """

    return {
        FlameType.RESIN: 2.2,
        FlameType.WOOD: 2.2,
        FlameType.ALUMINUM: 6.6,
        FlameType.MIXED_WOOD: 4.7,
        FlameType.MIXED_RESIN: 4.7
    }[flame_type]


