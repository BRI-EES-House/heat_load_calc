"""裏面相当温度を計算するモジュール

TODO:
    配列の数が 8760 * 4 に固定されている。
"""

import numpy as np

import heat_load_calc.x_07_inclined_surface_solar_radiation as x_07
import heat_load_calc.x_19_external_boundaries_direction as x_19


class OutsideEqvTemp:

    def __init__(self):
        pass

    @classmethod
    def create(cls, b: dict):

        if b['boundary_type'] == 'internal':

            return OutsideEqvTempInternal()

        elif b['boundary_type'] in ['external_general_part', 'external_opaque_part']:

            if b['is_sun_striked_outside']:

                if b['boundary_type'] == 'external_general_part':
                    spec = b['general_part_spec']
                elif b['boundary_type'] == 'external_opaque_part':
                    spec = b['opaque_opening_part_spec']
                else:
                    raise ValueError()

                return OutsideEqvTempExternalGeneralPartAndExternalOpaquePart(
                    direction=b['direction'],
                    a_s=float(spec['outside_solar_absorption']),
                    eps_r=float(spec['outside_emissivity']),
                    r_surf=float(spec['outside_heat_transfer_resistance'])

                )
            else:
                return OutsideEqvTempExternalNotSunStriked()

        elif b['boundary_type'] == 'external_transparent_part':

            if b['is_sun_striked_outside']:

                spec = b['transparent_opening_part_spec']

                return OutsideEqvTempExternalTransparentPart(
                    direction=b['direction'],
                    eps_r=float(spec['outside_emissivity']),
                    r_surf_o=float(spec['outside_heat_transfer_resistance'])
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

    def __init__(self, direction: str, a_s, eps_r, r_surf):
        """

        Args:
            direction: 方位
        """

        super().__init__()

        self._direction = direction
        self._a_s = a_s
        self._eps_r = eps_r
        self._r_surf = r_surf

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
        w_alpha_i_j, w_beta_i_j = x_19.get_w_alpha_i_j_w_beta_i_j(direction_i_j=self._direction)

        # ステップnにおける室iの境界jにおける傾斜面の夜間放射量, W/m2, [8760 * 4]
        r_n_is_i_j_ns = x_07.get_r_n_is_i_j_ns(r_n_ns=r_n_ns, w_beta_i_j=w_beta_i_j)

        # ステップnにおける室iの境界jにおける傾斜面の日射量のうち直達成分, W/m2K [8760*4]
        # ステップnにおける室iの境界jにおける傾斜面の日射量のうち天空成分, W/m2K [8760*4]
        # ステップnにおける室iの境界jにおける傾斜面の日射量のうち地盤反射成分, W/m2K [8760*4]
        i_is_d_i_j_ns, i_is_sky_i_j_ns, i_is_ref_i_j_ns = x_07.get_i_is_i_j_ns(
            i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, h_sun_ns=h_sun_ns, a_sun_ns=a_sun_ns,
            w_alpha_i_j=w_alpha_i_j, w_beta_i_j=w_beta_i_j)

        # 室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [8760*4]
        # 一般部位・不透明な開口部の場合、日射・長波長放射を考慮する。
        theta_o_sol_i_j_ns = theta_o_ns + (
                self._a_s * (i_is_d_i_j_ns + i_is_sky_i_j_ns + i_is_ref_i_j_ns) - self._eps_r * r_n_is_i_j_ns
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
        w_alpha_i_j, w_beta_i_j = x_19.get_w_alpha_i_j_w_beta_i_j(direction_i_j=self._direction)

        # ステップnにおける室iの境界jにおける傾斜面の夜間放射量, W/m2, [8760 * 4]
        r_n_is_i_j_ns = x_07.get_r_n_is_i_j_ns(r_n_ns=r_n_ns, w_beta_i_j=w_beta_i_j)

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
