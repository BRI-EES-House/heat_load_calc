"""窓の透過日射熱取得の計算

"""

import numpy as np

from heat_load_calc.initializer import external_boundaries_direction
from heat_load_calc.initializer import inclined_surface_solar_radiation
from heat_load_calc.initializer import solar_shading
from heat_load_calc.initializer import oblique_incidence_charac


class TransmissionSolarRadiation:

    def __init__(self):
        pass

    @classmethod
    def create(cls, d: dict, solar_shading_part: solar_shading.SolarShadingSimple):

        if d['boundary_type'] == 'external_transparent_part':

            if bool(d['is_sun_striked_outside']):

                return TransmissionSolarRadiationTransparentSunStrike(
                    direction=d['direction'],
                    area=d['area'],
                    solar_shading_part=solar_shading_part,
                    glazing_type=d['incident_angle_characteristics'],
                    eta_value=d['eta_value'],
                )

            else:

                return TransmissionSolarRadiationNot()

        else:

            return TransmissionSolarRadiationNot()

    def get_qgt(self, a_sun_ns, h_sun_ns, i_dn_ns, i_sky_ns):

        raise NotImplementedError()


class TransmissionSolarRadiationTransparentSunStrike(TransmissionSolarRadiation):

    def __init__(
            self,
            direction: str,
            area: float,
            solar_shading_part: solar_shading.SolarShadingSimple,
            glazing_type: str,
            eta_value: float
    ):
        """

        Args:
            direction: 境界が面する方位
            area: 面積, m2
            solar_shading_part: 日よけの仕様（SolarShadingPartクラス）
            glazing_type: ガラスの入射角特性タイプ = 'single' or 'multiple'
            eta_value: 日射熱取得率
        """

        super().__init__()

        self._direction = direction
        self._area = area
        self._solar_shading_part = solar_shading_part
        self._glazing_type = glazing_type
        self._eta_value = eta_value

    def get_qgt(self, a_sun_ns, h_sun_ns, i_dn_ns, i_sky_ns):

        # 境界jの傾斜面の方位角, rad
        # 境界jの傾斜面の傾斜角, rad
        w_alpha_j, w_beta_j = external_boundaries_direction.get_w_alpha_j_w_beta_j(direction_j=self._direction)

        # ステップnの境界jにおける傾斜面に入射する太陽の入射角, rad, [8760 * 4]
        theta_aoi_j_ns = inclined_surface_solar_radiation.get_theta_aoi_j_n(
            h_sun_ns=h_sun_ns, a_sun_ns=a_sun_ns, w_alpha_j=w_alpha_j, w_beta_j=w_beta_j)

        # ステップnにおける境界jにおける傾斜面の日射量のうち直達成分, W / m2K, [8760 * 4]
        # ステップnにおける境界jにおける傾斜面の日射量のうち天空成分, W / m2K, [8760 * 4]
        # ステップnにおける境界jにおける傾斜面の日射量のうち地盤反射成分, W / m2K, [8760 * 4]
        i_inc_d_j_ns, i_inc_sky_j_ns, i_inc_ref_j_ns = inclined_surface_solar_radiation.get_i_is_j_ns(
            i_dn_ns=i_dn_ns,
            i_sky_ns=i_sky_ns,
            h_sun_ns=h_sun_ns,
            a_sun_ns=a_sun_ns,
            w_alpha_j=w_alpha_j,
            w_beta_j=w_beta_j
        )

        # 日除けの影面積比率, [8760 * 4]
        f_sdw_j_ns = self._solar_shading_part.get_f_sdw_j_ns(h_sun_ns, a_sun_ns, self._direction)

        # 境界jにおける透明な開口部の拡散日射に対する基準化透過率
        c_d_j = oblique_incidence_charac.get_c_d_j(glazing_type_j=self._glazing_type)

        # 境界jにおける透明な開口部の直達日射に対する基準化透過率, [8760 * 4]
        tau_d_j_ns = oblique_incidence_charac.get_tau_d_j_ns(theta_aoi_j_ns=theta_aoi_j_ns, glazing_type_j=self._glazing_type)

        # 透過日射熱取得（直達成分）, W/m2, [8760 * 4]
        q_gt_d_j_ns = self._eta_value * (1.0 - f_sdw_j_ns) * tau_d_j_ns * i_inc_d_j_ns

        # 拡散成分, W/m2, [8760 * 4]
        q_gt_s_j_ns = self._eta_value * c_d_j * (i_inc_sky_j_ns + i_inc_ref_j_ns)

        # 透過日射量, W, [8760 * 4]
        q_gt_ns = (q_gt_d_j_ns + q_gt_s_j_ns) * self._area

        return q_gt_ns


class TransmissionSolarRadiationNot(TransmissionSolarRadiation):

    def __init__(self):
        super().__init__()

    def get_qgt(self, a_sun_ns, h_sun_ns, i_dn_ns, i_sky_ns):

        return np.zeros(8760*4, dtype=float)

