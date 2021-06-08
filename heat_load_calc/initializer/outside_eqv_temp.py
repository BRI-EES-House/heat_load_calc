"""裏面相当温度を計算するモジュール

TODO:
    配列の数が 8760 * 4 に固定されている。
"""

import numpy as np

from heat_load_calc.initializer import external_boundaries_direction
from heat_load_calc.initializer import inclined_surface_solar_radiation
from heat_load_calc.initializer import solar_shading


class OutsideEqvTemp:

    def __init__(self):
        pass

    @classmethod
    def create(cls, b: dict):

        if b['boundary_type'] == 'internal':

            return OutsideEqvTempInternal()

        elif b['boundary_type'] in ['external_general_part', 'external_opaque_part']:

            if b['is_sun_striked_outside']:

                return OutsideEqvTempExternalGeneralPartAndExternalOpaquePart(
                    direction=b['direction'],
                    a_s=float(b['outside_solar_absorption']),
                    eps_r=float(b['outside_emissivity']),
                    r_surf=float(b['outside_heat_transfer_resistance']),
                    solar_shading=solar_shading.SolarShadingSimple.create(b)
                )

            else:

                return OutsideEqvTempExternalNotSunStriked()

        elif b['boundary_type'] == 'external_transparent_part':

            if b['is_sun_striked_outside']:

                return OutsideEqvTempExternalTransparentPart(
                    direction=b['direction'],
                    eps_r=float(b['outside_emissivity']),
                    r_surf_o=float(b['outside_heat_transfer_resistance'])
                )

            else:

                return OutsideEqvTempExternalNotSunStriked()

        elif b['boundary_type'] == 'ground':

            return OutsideEqvTempGround()

        else:

            raise KeyError()

    def get_theta_o_sol_i_j_ns(
            self,
            theta_o_ns: np.ndarray,
            i_dn_ns: np.ndarray,
            i_sky_ns: np.ndarray,
            r_n_ns: np.ndarray,
            a_sun_ns: np.ndarray,
            h_sun_ns: np.ndarray
    ):
        """相当外気温度を計算する。
        本関数はアブストラクトメソッド。継承されたクラスによりオーバーライドされる。

        Args:
            theta_o_ns: ステップnにおける外気温度, ℃, [8760 * 4]
            i_dn_ns: ステップnにおける法線面直達日射量, W/m2, [8760 * 4]
            i_sky_ns: ステップnにおける水平面天空日射量, W/m2, [8760 * 4]
            r_n_ns: ステップnにおける夜間放射量, W/m2, [8760 * 4]
            a_sun_ns: ステップnにおける太陽高度, deg, [8760 * 4]
            h_sun_ns: ステップnにおける太陽方位, deg, [8760 * 4]

        Returns:
            室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [8760*4]
        """

        raise NotImplementedError()


class OutsideEqvTempInternal(OutsideEqvTemp):

    def __init__(self):
        super().__init__()
        pass

    def get_theta_o_sol_i_j_ns(
            self,
            theta_o_ns: np.ndarray,
            i_dn_ns: np.ndarray,
            i_sky_ns: np.ndarray,
            r_n_ns: np.ndarray,
            a_sun_ns: np.ndarray,
            h_sun_ns: np.ndarray
    ):
        """
        相当外気温度を計算する。

        Args:
            theta_o_ns: ステップnにおける外気温度, ℃, [8760 * 4]
            i_dn_ns: ステップnにおける法線面直達日射量, W/m2, [8760 * 4]
            i_sky_ns: ステップnにおける水平面天空日射量, W/m2, [8760 * 4]
            r_n_ns: ステップnにおける夜間放射量, W/m2, [8760 * 4]
            a_sun_ns: ステップnにおける太陽高度, deg, [8760 * 4]
            h_sun_ns: ステップnにおける太陽方位, deg, [8760 * 4]

        Returns:
            室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [8760 * 4]
        """

        # この値は使用しないのでNoneでもよいはず
        # 集約化する際にNoneだと変な挙動を示すかも知れないのでとりあえずゼロにしておく。

        return np.zeros(24 * 365 * 4)


class OutsideEqvTempExternalGeneralPartAndExternalOpaquePart(OutsideEqvTemp):

    def __init__(self, direction: str, a_s, eps_r, r_surf, solar_shading: solar_shading.SolarShadingSimple):
        """

        Args:
            direction: 方位
        """

        super().__init__()

        self._direction = direction
        self._a_s = a_s
        self._eps_r = eps_r
        self._r_surf = r_surf
        self._solar_shading_part = solar_shading

    def get_theta_o_sol_i_j_ns(
            self,
            theta_o_ns: np.ndarray,
            i_dn_ns: np.ndarray,
            i_sky_ns: np.ndarray,
            r_n_ns: np.ndarray,
            a_sun_ns: np.ndarray,
            h_sun_ns: np.ndarray
    ):
        """
        相当外気温度を計算する。

        Args:
            theta_o_ns: ステップnにおける外気温度, ℃, [8760 * 4]
            i_dn_ns: ステップnにおける法線面直達日射量, W/m2, [8760 * 4]
            i_sky_ns: ステップnにおける水平面天空日射量, W/m2, [8760 * 4]
            r_n_ns: ステップnにおける夜間放射量, W/m2, [8760 * 4]
            a_sun_ns: ステップnにおける太陽高度, deg, [8760 * 4]
            h_sun_ns: ステップnにおける太陽方位, deg, [8760 * 4]

        Returns:
            室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [8760 * 4]
        """

        # 室iの境界jの傾斜面の方位角, rad
        # 室iの境界jの傾斜面の傾斜角, rad
        w_alpha_i_j, w_beta_i_j = external_boundaries_direction.get_w_alpha_j_w_beta_j(direction_j=self._direction)

        # ---日よけの影面積比率

        # 直達日射に対する日よけの影面積比率, [8760 * 4]
        f_ss_d_j_ns = self._solar_shading_part.get_f_ss_d_j_ns(h_sun_ns, a_sun_ns)

        # 天空日射に対する日よけの影面積比率
        f_ss_s_j_ns = self._solar_shading_part.get_f_ss_s_j()

        # 地面反射日射に対する日よけの影面積比率
        f_ss_r_j_ns = 0.0

        # ステップnにおける室iの境界jにおける傾斜面の夜間放射量, W/m2, [8760 * 4]
        r_n_is_j_ns = inclined_surface_solar_radiation.get_r_n_is_j_ns(r_n_ns=r_n_ns, w_beta_j=w_beta_i_j)

        # ステップnにおける境界jにおける傾斜面の日射量のうち直達成分, W/m2K [8760*4]
        # ステップnにおける境界jにおける傾斜面の日射量のうち天空成分, W/m2K [8760*4]
        # ステップnにおける境界jにおける傾斜面の日射量のうち地盤反射成分, W/m2K [8760*4]
        i_is_d_j_ns, i_is_sky_j_ns, i_is_ref_j_ns = inclined_surface_solar_radiation.get_i_is_j_ns(
            i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, h_sun_ns=h_sun_ns, a_sun_ns=a_sun_ns,
            w_alpha_j=w_alpha_i_j, w_beta_j=w_beta_i_j)

        # 室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [8760*4]
        # 一般部位・不透明な開口部の場合、日射・長波長放射を考慮する。
        theta_o_sol_i_j_ns = theta_o_ns + (
                self._a_s * (i_is_d_j_ns * (1.0 - f_ss_d_j_ns) + i_is_sky_j_ns * (1.0 - f_ss_s_j_ns) + i_is_ref_j_ns + (1.0 - f_ss_r_j_ns)) - self._eps_r * r_n_is_j_ns
        ) * self._r_surf

        return theta_o_sol_i_j_ns


class OutsideEqvTempExternalTransparentPart(OutsideEqvTemp):

    def __init__(self, direction: str, eps_r, r_surf_o):
        """

        Args:
            direction: 方位
        """

        super().__init__()

        self._direction = direction
        self._eps_r = eps_r
        self._r_surf_o = r_surf_o

    def get_theta_o_sol_i_j_ns(
            self,
            theta_o_ns: np.ndarray,
            i_dn_ns: np.ndarray,
            i_sky_ns: np.ndarray,
            r_n_ns: np.ndarray,
            a_sun_ns: np.ndarray,
            h_sun_ns: np.ndarray
    ):
        """
        相当外気温度を計算する。

        Args:
            theta_o_ns: ステップnにおける外気温度, ℃, [8760 * 4]
            i_dn_ns: ステップnにおける法線面直達日射量, W/m2, [8760 * 4]
            i_sky_ns: ステップnにおける水平面天空日射量, W/m2, [8760 * 4]
            r_n_ns: ステップnにおける夜間放射量, W/m2, [8760 * 4]
            a_sun_ns: ステップnにおける太陽高度, deg, [8760 * 4]
            h_sun_ns: ステップnにおける太陽方位, deg, [8760 * 4]

        Returns:
            室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [8760 * 4]
        """

        # 室iの境界jの傾斜面の方位角, rad
        # 室iの境界jの傾斜面の傾斜角, rad
        w_alpha_i_j, w_beta_i_j = external_boundaries_direction.get_w_alpha_j_w_beta_j(direction_j=self._direction)

        # ステップnにおける室iの境界jにおける傾斜面の夜間放射量, W/m2, [8760 * 4]
        r_n_is_i_j_ns = inclined_surface_solar_radiation.get_r_n_is_j_ns(r_n_ns=r_n_ns, w_beta_j=w_beta_i_j)

        # 室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [8760*4]
        # 透明な開口部の場合、日射はガラス面への透過・吸収の項で扱うため、ここでは長波長放射のみ考慮する。
        return theta_o_ns - self._eps_r * r_n_is_i_j_ns * self._r_surf_o


class OutsideEqvTempExternalNotSunStriked(OutsideEqvTemp):

    def __init__(self):
        super().__init__()

    def get_theta_o_sol_i_j_ns(
            self,
            theta_o_ns: np.ndarray,
            i_dn_ns: np.ndarray,
            i_sky_ns: np.ndarray,
            r_n_ns: np.ndarray,
            a_sun_ns: np.ndarray,
            h_sun_ns: np.ndarray
    ):
        """
        相当外気温度を計算する。

        Args:
            theta_o_ns: ステップnにおける外気温度, ℃, [8760 * 4]
            i_dn_ns: ステップnにおける法線面直達日射量, W/m2, [8760 * 4]
            i_sky_ns: ステップnにおける水平面天空日射量, W/m2, [8760 * 4]
            r_n_ns: ステップnにおける夜間放射量, W/m2, [8760 * 4]
            a_sun_ns: ステップnにおける太陽高度, deg, [8760 * 4]
            h_sun_ns: ステップnにおける太陽方位, deg, [8760 * 4]

        Returns:
            室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [8760 * 4]
        """

        return theta_o_ns


class OutsideEqvTempGround(OutsideEqvTemp):

    def __init__(self):
        super().__init__()
        pass

    def get_theta_o_sol_i_j_ns(
            self,
            theta_o_ns: np.ndarray,
            i_dn_ns: np.ndarray,
            i_sky_ns: np.ndarray,
            r_n_ns: np.ndarray,
            a_sun_ns: np.ndarray,
            h_sun_ns: np.ndarray
    ):
        """
        相当外気温度を計算する。

        Args:
            theta_o_ns: ステップnにおける外気温度, ℃, [8760 * 4]
            i_dn_ns: ステップnにおける法線面直達日射量, W/m2, [8760 * 4]
            i_sky_ns: ステップnにおける水平面天空日射量, W/m2, [8760 * 4]
            r_n_ns: ステップnにおける夜間放射量, W/m2, [8760 * 4]
            a_sun_ns: ステップnにおける太陽高度, deg, [8760 * 4]
            h_sun_ns: ステップnにおける太陽方位, deg, [8760 * 4]

        Returns:
            室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [8760 * 4]
        """

        return np.full(24 * 365 * 4, np.average(theta_o_ns))
