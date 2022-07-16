import numpy as np

from heat_load_calc import direction, inclined_surface_solar_radiation, window
from heat_load_calc.weather import Weather
from heat_load_calc.direction import Direction
from heat_load_calc.solar_shading import SolarShading
from heat_load_calc.boundary_type import BoundaryType
from heat_load_calc.window import Window


class TransmissionSolarRadiation:

    def __init__(self):
        pass

    @classmethod
    def create(
            cls,
            ss: SolarShading,
            boundary_type: BoundaryType,
            direction: Direction,
            area: float,
            window: Window,
            is_sun_striked_outside: bool
    ):

        if boundary_type == BoundaryType.ExternalTransparentPart:

            if is_sun_striked_outside:

                return TransmissionSolarRadiationTransparentSunStrike(
                    direction=direction,
                    area=area,
                    ss=ss,
                    window=window
                )

            else:

                return TransmissionSolarRadiationNot()

        else:

            return TransmissionSolarRadiationNot()

    def get_qgt(self, oc: Weather) -> np.ndarray:
        """

        Args:
            oc: OutdoorCondition クラス

        Returns:

        """

        raise NotImplementedError()


class TransmissionSolarRadiationTransparentSunStrike(TransmissionSolarRadiation):

    def __init__(self, direction: Direction, area: float, ss: SolarShading, window: Window):
        """

        Args:
            direction: 境界が面する方位
            area: 面積, m2
            ss: 日よけの仕様（SolarShadingPartクラス）
            window: Windowクラス
        """

        super().__init__()

        self._direction = direction
        self._area = area
        self._ss = ss
        self._glazing_type = window.glazing_type_j.value
        self._window = window

    def get_qgt(self, oc: Weather) -> np.ndarray:
        """

        Args:
            oc: Weather クラス

        Returns:

        """

        # ステップ n における境界 j の傾斜面に入射する太陽の入射角, rad, [N+1]
        theta_aoi_j_ns = inclined_surface_solar_radiation.get_theta_aoi_j_ns(
            h_sun_ns=oc.h_sun_ns_plus, a_sun_ns=oc.a_sun_ns_plus, direction=self._direction)

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
            direction=self._direction
        )

        # ---日よけの影面積比率

        # 直達日射に対する日よけの影面積比率, [N+1]
        f_ss_d_j_ns = self._ss.get_f_ss_d_j_ns(h_sun_n=oc.h_sun_ns_plus, a_sun_n=oc.a_sun_ns_plus)

        # 天空日射に対する日よけの影面積比率
        f_ss_s_j_ns = self._ss.get_f_ss_s_j()

        # 地面反射日射に対する日よけの影面積比率
        f_ss_r_j_ns = self._ss.get_f_ss_r_j()

        # ステップ n における境界 j の透明な開口部の直達日射に対する日射透過率, -, [N+1]
        tau_d_j_ns = self._window.get_tau_d_j_ns(theta_aoi_j_ns=theta_aoi_j_ns)

        # 境界 j の透明な開口部の天空日射に対する日射透過率, -, [N+1]
        tau_s_j = self._window.get_tau_s_j()

        # 境界 j の透明な開口部の地盤反射日射に対する日射透過率, -, [N+1]
        tau_r_j = self._window.get_tau_r_j()

        # 直達日射に対する透過日射量, W/m2, [N+1]
        q_gt_d_j_ns = tau_d_j_ns * (1.0 - f_ss_d_j_ns) * i_inc_d_j_ns

        # 天空日射に対する透過日射量, W/m2, [N+1]
        q_gt_sky_j_ns = tau_s_j * (1.0 - f_ss_s_j_ns) * i_inc_sky_j_ns

        # 地盤反射日射に対する透過日射量, W/m2, [N+1]
        q_gt_ref_j_ns = tau_r_j * (1.0 - f_ss_r_j_ns) * i_inc_ref_j_ns

        # 透過日射量, W, [N+1]
        q_gt_ns = (q_gt_d_j_ns + q_gt_sky_j_ns + q_gt_ref_j_ns) * self._area

        return q_gt_ns


class TransmissionSolarRadiationNot(TransmissionSolarRadiation):

    def __init__(self):
        super().__init__()

    def get_qgt(self, oc: Weather) -> np.ndarray:
        """

        Args:
            oc: OutdoorCondition クラス

        Returns:

        """

        return np.zeros(oc.number_of_data_plus, dtype=float)
