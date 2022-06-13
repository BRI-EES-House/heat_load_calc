"""窓の透過日射熱取得の計算

"""

import numpy as np

from heat_load_calc import external_boundaries_direction, inclined_surface_solar_radiation, window, solar_shading
from heat_load_calc.outdoor_condition import OutdoorCondition


class TransmissionSolarRadiation:

    def __init__(self):
        pass

    @classmethod
    def create(cls, b: dict, ssp: solar_shading.SolarShading):

        if b['boundary_type'] == 'external_transparent_part':

            if bool(b['is_sun_striked_outside']):

                return TransmissionSolarRadiationTransparentSunStrike(
                    direction=b['direction'],
                    area=b['area'],
                    solar_shading_part=ssp,
                    glazing_type=b['incident_angle_characteristics'],
                    eta_value=b['eta_value'],
                    glass_area_ratio=b['glass_area_ratio']
                )

            else:

                return TransmissionSolarRadiationNot()

        else:

            return TransmissionSolarRadiationNot()

    def get_qgt(self, oc: OutdoorCondition) -> np.ndarray:
        """

        Args:
            oc: OutdoorCondition クラス

        Returns:

        """

        raise NotImplementedError()


class TransmissionSolarRadiationTransparentSunStrike(TransmissionSolarRadiation):

    def __init__(
            self,
            direction: str,
            area: float,
            solar_shading_part: solar_shading.SolarShadingSimple,
            glazing_type: str,
            eta_value: float,
            glass_area_ratio: float
    ):
        """

        Args:
            direction: 境界が面する方位
            area: 面積, m2
            solar_shading_part: 日よけの仕様（SolarShadingPartクラス）
            glazing_type: ガラスの入射角特性タイプ = 'single' or 'multiple'
            eta_value: 日射熱取得率
            glass_area_ratio: ガラス面積率
        """

        super().__init__()

        self._direction = direction
        self._area = area
        self._solar_shading_part = solar_shading_part
        self._glazing_type = glazing_type
        self._eta_value = eta_value
        self._glass_area_ratio = glass_area_ratio

    def get_qgt(self, oc: OutdoorCondition) -> np.ndarray:
        """

        Args:
            oc: OutdoorCondition クラス

        Returns:

        """

        # 境界jの傾斜面の方位角, rad
        # 境界jの傾斜面の傾斜角, rad
        alpha_w_j, beta_w_j = external_boundaries_direction.get_w_alpha_j_w_beta_j(direction_j=self._direction)

        # ステップ n における境界 j の傾斜面に入射する太陽の入射角, rad, [N+1]
        theta_aoi_j_ns = inclined_surface_solar_radiation.get_theta_aoi_j_ns(
            h_sun_ns=oc.h_sun_ns_plus, a_sun_ns=oc.a_sun_ns_plus, alpha_w_j=alpha_w_j, beta_w_j=beta_w_j)

        # ステップ n における境界 j の傾斜面に入射する日射量のうち直達成分, W/m2 [N+1]
        # ステップ n における境界 j の傾斜面に入射する日射量のうち天空成分, W/m2 [N+1]
        # ステップ n における境界 j の傾斜面に入射する日射量のうち地盤反射成分, W/m2 [N+1]
        # ステップ n における境界 j の傾斜面の夜間放射量, W/m2, [N+1]
        i_inc_d_j_ns, i_inc_sky_j_ns, i_inc_ref_j_ns, r_srf_eff_j_ns = inclined_surface_solar_radiation.get_i_is_j_ns(
            i_dn_ns=oc.i_dn_ns_plus,
            i_sky_ns=oc.i_sky_ns_plus,
            r_eff_ns=oc.r_n_ns_plus,
            h_sun_ns=oc.h_sun_ns_plus,
            a_sun_ns=oc.a_sun_ns_plus,
            alpha_w_j=alpha_w_j,
            beta_w_j=beta_w_j
        )

        # ---日よけの影面積比率

        # 直達日射に対する日よけの影面積比率, [N+1]
        f_ss_d_j_ns = self._solar_shading_part.get_f_ss_d_j_ns(oc.h_sun_ns_plus, oc.a_sun_ns_plus)

        # 天空日射に対する日よけの影面積比率
        f_ss_s_j_ns = self._solar_shading_part.get_f_ss_s_j()

        # 地面反射日射に対する日よけの影面積比率
        f_ss_r_j_ns = 0.0

        # 透過率の計算
        tau_value, ashgc_value, rho_value, a_value = window.get_tau_and_ashgc_rho_a(
            eta_w=self._eta_value,
            glazing_type_j=self._glazing_type,
            glass_area_ratio_j=self._glass_area_ratio
        )

        # ---基準透過率

        # 境界jにおける透明な開口部の直達日射に対する規準化透過率, [8760 * 4]
        tau_d_j_ns = window.get_tau_d_j_ns(
            theta_aoi_j_ns=theta_aoi_j_ns, glazing_type_j=self._glazing_type)

        # 境界jにおける透明な開口部の拡散日射に対する規準化透過率
        c_d_j = window.get_c_d_j(glazing_type_j=self._glazing_type)

        # ---透過日射量, W/m2

        # 直達日射に対する透過日射量, W/m2, [8760 * 4]
        q_gt_d_j_ns = tau_value * (1.0 - f_ss_d_j_ns) * tau_d_j_ns * i_inc_d_j_ns

        # 天空日射に対する透過日射量, W/m2, [8760 * 4]
        q_gt_sky_j_ns = tau_value * (1.0 - f_ss_s_j_ns) * c_d_j * i_inc_sky_j_ns

        # 地盤反射日射に対する透過日射量, W/m2, [8760 * 4]
        q_gt_ref_j_ns = tau_value * (1.0 - f_ss_r_j_ns) * c_d_j * i_inc_ref_j_ns

        # 透過日射量, W, [8760 * 4]
        q_gt_ns = (q_gt_d_j_ns + q_gt_sky_j_ns + q_gt_ref_j_ns) * self._area

        return q_gt_ns


class TransmissionSolarRadiationNot(TransmissionSolarRadiation):

    def __init__(self):
        super().__init__()

    def get_qgt(self, oc: OutdoorCondition) -> np.ndarray:
        """

        Args:
            oc: OutdoorCondition クラス

        Returns:

        """

        return np.zeros(oc.number_of_data_plus, dtype=float)
