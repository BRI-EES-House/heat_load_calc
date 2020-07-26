"""窓の透過日射熱取得の計算

"""

import numpy as np
from typing import List

import heat_load_calc.x_07_inclined_surface_solar_radiation as x_07
import heat_load_calc.x_19_external_boundaries_direction as x_19

from heat_load_calc.apdx10_oblique_incidence_characteristics import get_taud_i_k_n
import heat_load_calc.apdx10_oblique_incidence_characteristics as a10
from heat_load_calc.s3_surface_loader import Boundary
import heat_load_calc.a8_shading as a8
from heat_load_calc.a8_shading import SolarShadingPart


class TransmissionSolarRadiation():

    def __init__(self):
        pass

    @classmethod
    def create(cls, d: dict, solar_shading_part: SolarShadingPart):

        if d['boundary_type'] == 'external_transparent_part':

            if bool(d['is_sun_striked_outside']):

                return TransmissionSolarRadiationTransparentSunStrike(
                    direction=d['direction'],
                    area=d['area'],
                    solar_shading_part=solar_shading_part,
                    incident_angle_characteristics=d['transparent_opening_part_spec']['incident_angle_characteristics'],
                    eta_value=d['transparent_opening_part_spec']['eta_value'],
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
            solar_shading_part: SolarShadingPart,
            incident_angle_characteristics: str,
            eta_value: float
    ):

        super().__init__()

        self._direction = direction
        self._area = area
        self._solar_shading_part = solar_shading_part
        self._incident_angle_characteristics = incident_angle_characteristics
        self._eta_value = eta_value

    def get_qgt(self, a_sun_ns, h_sun_ns, i_dn_ns, i_sky_ns):

        FSDW_i_k_n = self._solar_shading_part.get_FSDW_i_k_n2(h_sun_ns, a_sun_ns, self._direction)
        # 室iの境界jの傾斜面の方位角, rad
        # 室iの境界jの傾斜面の傾斜角, rad

        w_alpha_i_j, w_beta_i_j = x_19.get_w_alpha_i_j_w_beta_i_j(direction_i_j=self._direction)
        # ステップnの室iの境界jにおける傾斜面に入射する太陽の入射角, rad, [365*24*4]

        theta_aoi_i_j_n = x_07.get_theta_aoi_i_j_n(
            h_sun_ns=h_sun_ns, a_sun_ns=a_sun_ns, w_alpha_i_j=w_alpha_i_j, w_beta_i_j=w_beta_i_j)
        # ステップnにおける室iの境界jにおける傾斜面の日射量のうち直達成分, W / m2K
        # ステップnにおける室iの境界jにおける傾斜面の日射量のうち天空成分, W / m2K
        # ステップnにおける室iの境界jにおける傾斜面の日射量のうち地盤反射成分, W / m2K

        i_inc_d, i_inc_sky, i_inc_ref = x_07.get_i_is_i_j_ns(
            i_dn_ns=i_dn_ns,
            i_sky_ns=i_sky_ns,
            h_sun_ns=h_sun_ns,
            a_sun_ns=a_sun_ns,
            w_alpha_i_j=w_alpha_i_j,
            w_beta_i_j=w_beta_i_j
        )

        qgt = calc_QGT_i_k_n(
            theta_aoi_i_k=theta_aoi_i_j_n,
            incident_angle_characteristics_i_ks=self._incident_angle_characteristics,
            i_inc_d_i_k_n=i_inc_d,
            FSDW_i_k_n=FSDW_i_k_n,
            i_inc_sky_i_k_n=i_inc_sky,
            i_inc_ref_i_k_n=i_inc_ref,
            a_i_ks=self._area,
            tau_i_k=self._eta_value,
        )
        return qgt


class TransmissionSolarRadiationNot(TransmissionSolarRadiation):

    def __init__(self):
        super().__init__()

    def get_qgt(self, a_sun_ns, h_sun_ns, i_dn_ns, i_sky_ns):

        return np.zeros(8760*4, dtype=float)


# 透過日射量[W]、吸収日射量[W]の計算 式(90)
def calc_QGT_i_k_n(
        theta_aoi_i_k: np.ndarray,
        incident_angle_characteristics_i_ks: str,
        i_inc_d_i_k_n: np.ndarray,
        FSDW_i_k_n: np.ndarray,
        i_inc_sky_i_k_n: np.ndarray,
        i_inc_ref_i_k_n: np.ndarray,
        a_i_ks: float,
        tau_i_k: float,
):

    # 室iの境界kにおける透明な開口部の拡散日射に対する基準化透過率
    c_d_i_k = a10.get_c_d_i_k(incident_angle_characteristics_i_ks=incident_angle_characteristics_i_ks)

    # 直達日射の入射角特性の計算
    taud_i_k_n = get_taud_i_k_n(
        theta_aoi_i_k=theta_aoi_i_k,
        incident_angle_characteristics_i_ks=incident_angle_characteristics_i_ks)

    # 直達成分
    QGTD_i_k_n = get_QGTD_i_k_n(
        tau_i_k=tau_i_k, i_inc_d_i_k_n=i_inc_d_i_k_n, taud_i_k_n=taud_i_k_n, F_SDW_i_k_n=FSDW_i_k_n)

    # 拡散成分
    QGTS_i_k_n = get_QGTS_i_k_n(tau_i_k, c_d_i_k, i_inc_sky_i_k_n, i_inc_ref_i_k_n)

    # 透過日射量の計算
    QGT_i_k_n = (QGTD_i_k_n + QGTS_i_k_n) * a_i_ks

    return QGT_i_k_n


# 透過日射熱取得（直達成分）[W/m2]の計算
def get_QGTD_i_k_n(
        tau_i_k: float, i_inc_d_i_k_n: np.ndarray, taud_i_k_n: np.ndarray, F_SDW_i_k_n: np.ndarray
) -> np.ndarray:

    # 透過日射熱取得（直達成分）[W/m2]の計算
    QGTD = tau_i_k * (1.0 - F_SDW_i_k_n) * taud_i_k_n * i_inc_d_i_k_n

    return QGTD


# 透過日射熱取得（拡散成分）[W/m2]の計算
def get_QGTS_i_k_n(
        T: float, Cd: float, I_S_i_k_n: np.ndarray, I_R_i_k_n: np.ndarray) -> np.ndarray:
    """
    :param I_S_i_k_n: 傾斜面入射天空日射量[W/m2]
    :param I_R_i_k_n: 傾斜面入射反射日射量[W/m2]
    :return: 透過日射熱取得（拡散成分）[W/m2]
    """
    QGTS = T * Cd * (I_S_i_k_n + I_R_i_k_n)
    return QGTS
