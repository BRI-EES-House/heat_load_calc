import numpy as np

from heat_load_calc import direction, inclined_surface_solar_radiation, window, solar_shading
from heat_load_calc.weather import Weather
from heat_load_calc.direction import Direction


class OutsideEqvTemp:

    def __init__(self):
        pass

    @classmethod
    def create(cls, b: dict, ssp: solar_shading.SolarShading):

        if b['boundary_type'] == 'internal':

            return OutsideEqvTempInternal()

        elif b['boundary_type'] in ['external_general_part', 'external_opaque_part']:

            if b['is_sun_striked_outside']:

                return OutsideEqvTempExternalGeneralPartAndExternalOpaquePart(
                    direction=Direction(b['direction']),
                    a_s=float(b['outside_solar_absorption']),
                    eps_r=float(b['outside_emissivity']),
                    r_surf=float(b['outside_heat_transfer_resistance']),
                    solar_shading=ssp
                )

            else:

                return OutsideEqvTempExternalNotSunStriked()

        elif b['boundary_type'] == 'external_transparent_part':

            if b['is_sun_striked_outside']:

                return OutsideEqvTempExternalTransparentPart(
                    direction=Direction(b['direction']),
                    eps_r=float(b['outside_emissivity']),
                    r_surf_o=float(b['outside_heat_transfer_resistance']),
                    u_value_j=float(b['u_value']),
                    eta_value_j=float(b['eta_value']),
                    glazing_type_j=b['incident_angle_characteristics'],
                    glass_area_ratio_j=b['glass_area_ratio'],
                    solar_shading_part=ssp
                )

            else:

                return OutsideEqvTempExternalNotSunStriked()

        elif b['boundary_type'] == 'ground':

            return OutsideEqvTempGround()

        else:

            raise KeyError()

    def get_theta_o_sol_i_j_ns(self, oc: Weather) -> np.ndarray:
        """相当外気温度を計算する。
        本関数はアブストラクトメソッド。継承されたクラスによりオーバーライドされる。

        Args:
            oc: OutdoorCondition クラス

        Returns:
            ステップ n における室 i の境界 j の傾斜面の相当外気温度, degree C, [N+1]
        """

        raise NotImplementedError()


class OutsideEqvTempInternal(OutsideEqvTemp):

    def __init__(self):
        super().__init__()
        pass

    def get_theta_o_sol_i_j_ns(self, oc: Weather) -> np.ndarray:
        """
        相当外気温度を計算する。

        Args:
            oc: OutdoorCondition クラス

        Returns:
            ステップ n における室 i の境界 j の傾斜面の相当外気温度, degree C, [N+1]

        Notes:
            本来であれば、間仕切り壁において相当外気温度は定義できない概念ではあるが、
            後々の numpy の行列計算において、相当外気温度を 0.0 にしておく方が都合がよいので、
            ここでは0.0に初期化することにした。
        """

        return np.zeros(oc.number_of_data_plus)


class OutsideEqvTempExternalGeneralPartAndExternalOpaquePart(OutsideEqvTemp):

    def __init__(self, direction: Direction, a_s, eps_r, r_surf, solar_shading: solar_shading.SolarShading):
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

    def get_theta_o_sol_i_j_ns(self, oc: Weather) -> np.ndarray:
        """
        相当外気温度を計算する。

        Args:
            oc: OutdoorCondition クラス

        Returns:
            ステップ n における室 i の境界 j の傾斜面の相当外気温度, degree C, [N+1]
        """

        # 直達日射に対する日よけの影面積比率, [8760 * 4]
        f_ss_d_j_ns = self._solar_shading_part.get_f_ss_d_j_ns(oc.h_sun_ns_plus, oc.a_sun_ns_plus)

        # 天空日射に対する日よけの影面積比率
        f_ss_s_j_ns = self._solar_shading_part.get_f_ss_s_j()

        # 地面反射日射に対する日よけの影面積比率
        f_ss_r_j_ns = 0.0

        # ステップ n における境界 j の傾斜面に入射する日射量の直達成分, W/m2 [n]
        # ステップ n における境界 j の傾斜面に入射する日射量の天空成分, W/m2 [n]
        # ステップ n における境界 j の傾斜面に入射する日射量の地盤反射成分, W/m2 [n]
        # ステップ n における境界 j の傾斜面の夜間放射量, W/m2, [n]
        i_is_d_j_ns, i_is_sky_j_ns, i_is_ref_j_ns, r_srf_eff_j_ns = inclined_surface_solar_radiation.get_i_is_j_ns(
            i_dn_ns=oc.i_dn_ns_plus,
            i_sky_ns=oc.i_sky_ns_plus,
            r_eff_ns=oc.r_n_ns_plus,
            h_sun_ns=oc.h_sun_ns_plus,
            a_sun_ns=oc.a_sun_ns_plus,
            direction=self._direction
        )

        # 室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [8760*4]
        # 一般部位・不透明な開口部の場合、日射・長波長放射を考慮する。
        theta_o_sol_i_j_ns = oc.theta_o_ns_plus + (
                self._a_s * (i_is_d_j_ns * (1.0 - f_ss_d_j_ns) + i_is_sky_j_ns * (1.0 - f_ss_s_j_ns) + i_is_ref_j_ns * (1.0 - f_ss_r_j_ns)) - self._eps_r * r_srf_eff_j_ns
        ) * self._r_surf

        return theta_o_sol_i_j_ns


class OutsideEqvTempExternalTransparentPart(OutsideEqvTemp):

    def __init__(self, direction: Direction, eps_r, r_surf_o, u_value_j: float,
                 eta_value_j: float,
                 glazing_type_j: str,
                 glass_area_ratio_j: float,
                 solar_shading_part: solar_shading.SolarShading):
        """

        Args:
            direction: 方位
        """

        super().__init__()

        self._direction = direction
        self._eps_r = eps_r
        self._r_surf_o = r_surf_o
        self._u_value = u_value_j
        self._eta_value = eta_value_j
        self._glazing_type = glazing_type_j
        self._glass_area_ratio = glass_area_ratio_j
        self._shading_part = solar_shading_part

    def get_theta_o_sol_i_j_ns(self, oc: Weather) -> np.ndarray:
        """
        相当外気温度を計算する。

        Args:
            oc: OutdoorCondition クラス

        Returns:
            ステップ n における室 i の境界 j の傾斜面の相当外気温度, degree C, [N+1]
        """

        # ステップ n の境界 j における傾斜面に入射する太陽の入射角, rad, [n]
        theta_aoi_j_ns = inclined_surface_solar_radiation.get_theta_aoi_j_ns(
            h_sun_ns=oc.h_sun_ns_plus, a_sun_ns=oc.a_sun_ns_plus, direction=self._direction)

        # ステップ n における境界 j の傾斜面に入射する日射量の直達成分, W / m2, [n]
        # ステップ n における境界 j の傾斜面に入射する日射量の天空成分, W / m2, [n]
        # ステップ n における境界 j の傾斜面に入射する日射量の地盤反射成分, W / m2, [n]
        # ステップ n における境界 j の傾斜面の夜間放射量, W/m2, [n]
        i_inc_d_j_ns, i_inc_sky_j_ns, i_inc_ref_j_ns, r_srf_eff_j_ns = inclined_surface_solar_radiation.get_i_is_j_ns(
            i_dn_ns=oc.i_dn_ns_plus,
            i_sky_ns=oc.i_sky_ns_plus,
            r_eff_ns=oc.r_n_ns_plus,
            h_sun_ns=oc.h_sun_ns_plus,
            a_sun_ns=oc.a_sun_ns_plus,
            direction=self._direction
        )

        # ---日よけの影面積比率

        # 直達日射に対する日よけの影面積比率, [8760 * 4]
        f_ss_d_j_ns = self._shading_part.get_f_ss_d_j_ns(oc.h_sun_ns_plus, oc.a_sun_ns_plus)

        # 天空日射に対する日よけの影面積比率
        f_ss_s_j_ns = self._shading_part.get_f_ss_s_j()

        # 地面反射日射に対する日よけの影面積比率
        f_ss_r_j_ns = 0.0

        # 吸収日射取得率の計算
        tau_value, ashgc_value, rho_value, a_value = window.get_tau_and_ashgc_rho_a(
            eta_w=self._eta_value,
            glazing_type_j=self._glazing_type,
            glass_area_ratio_j=self._glass_area_ratio
        )
        
        # 境界jにおける透明な開口部の直達日射に対する規準化吸収日射取得率, [8760 * 4]
        ashgc_d_j_ns = window.get_ashgc_d_j(
            theta_aoi_i_k=theta_aoi_j_ns, glazing_type_j=self._glazing_type, tau_w=tau_value, rho_w=rho_value)

        # 境界jにおける透明な開口部の拡散日射に対する規準化吸収日射取得率
        ashgc_d_j = window.get_c_ashgc(glazing_type_j=self._glazing_type, tau_w=tau_value, rho_w=rho_value)
        
        # ---吸収日射熱取得, W/m2

        # 直達日射に対する吸収日射熱取得, W/m2, [8760 * 4]
        q_gt_d_j_ns = ashgc_value * (1.0 - f_ss_d_j_ns) * ashgc_d_j_ns * i_inc_d_j_ns

        # 天空日射に対する吸収日射熱取得, W/m2, [8760 * 4]
        q_gt_sky_j_ns = ashgc_value * (1.0 - f_ss_s_j_ns) * ashgc_d_j * i_inc_sky_j_ns

        # 地盤反射日射に対する吸収日射熱取得, W/m2, [8760 * 4]
        q_gt_ref_j_ns = ashgc_value * (1.0 - f_ss_r_j_ns) * ashgc_d_j * i_inc_ref_j_ns

        # 吸収日射熱取得, W/m2, [8760 * 4]
        q_ga_ns = (q_gt_d_j_ns + q_gt_sky_j_ns + q_gt_ref_j_ns)

        # 室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [8760*4]
        # 透明な開口部の場合、透過日射はガラス面への透過の項で扱うため、ここでは吸収日射、長波長放射のみ考慮する。
        return oc.theta_o_ns_plus - self._eps_r * r_srf_eff_j_ns * self._r_surf_o + q_ga_ns / self._u_value


class OutsideEqvTempExternalNotSunStriked(OutsideEqvTemp):

    def __init__(self):
        super().__init__()

    def get_theta_o_sol_i_j_ns(self, oc: Weather) -> np.ndarray:
        """
        相当外気温度を計算する。

        Args:
            oc: OutdoorCondition クラス

        Returns:
            ステップ n における室 i の境界 j の傾斜面の相当外気温度, degree C, [N+1]
        """

#        return theta_o_ns
        return oc.theta_o_ns_plus


class OutsideEqvTempGround(OutsideEqvTemp):

    def __init__(self):
        super().__init__()
        pass

    def get_theta_o_sol_i_j_ns(self, oc: Weather) -> np.ndarray:
        """相当外気温度を計算する。

        Args:
            oc: OutdoorCondition クラス

        Returns:
            ステップ n における室 i の境界 j の傾斜面の相当外気温度, ℃, [N+1]
        """

        return np.full(oc.number_of_data_plus, oc.get_theta_o_ns_average())
