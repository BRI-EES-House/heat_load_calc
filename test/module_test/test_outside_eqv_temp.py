import unittest
import numpy as np


from heat_load_calc import outside_eqv_temp as oet
from heat_load_calc.weather import Weather
from heat_load_calc.interval import Interval
from heat_load_calc.direction import Direction
from heat_load_calc.solar_shading import SolarShading, SolarShadingSimple
from heat_load_calc import inclined_surface_solar_radiation
from heat_load_calc.window import Window, GlassType


class TestOutsideEqvTemp(unittest.TestCase):

    a_sun_ns = np.array([0.0, np.pi/6, np.pi/3, np.pi/2, np.pi*2/3, np.pi*5/6, np.pi])
    h_sun_ns = np.array([0.0, np.pi/6, np.pi/3, np.pi/2, np.pi/3, np.pi/6, 0.0])
    i_dn_ns = np.array([10.0, 100.0, 200.0, 300.0, 200.0, 100.0, 10.0])
    i_sky_ns = np.array([10.0, 100.0, 200.0, 300.0, 200.0, 100.0, 10.0])
    r_n_ns = np.array([20.0, 19.0, 18.0, 17.0, 18.0, 19.0, 20.0])
    theta_o_ns = np.array([-15.0, -12.0, 3.0, 5.0, 4.0, -3.0, -7.0])
    x_o_ns = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    itv = Interval.M15

    w = Weather(a_sun_ns=a_sun_ns, h_sun_ns=h_sun_ns, i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, r_n_ns=r_n_ns, theta_o_ns=theta_o_ns, x_o_ns=x_o_ns)

    ssp = SolarShadingSimple(alpha_w_j=-np.pi/4, l_z_j=0.4, l_y_h_j=1.5, l_y_e_j=0.3)

    def test_get_theta_o_eqv_j_ns_for_interval(self):

        result = oet.get_theta_o_eqv_j_ns_for_internal(w=self.w)

        self.assertEqual(result[0], 0.0)
        self.assertEqual(result[1], 0.0)
        self.assertEqual(result[2], 0.0)
        self.assertEqual(result[3], 0.0)
        self.assertEqual(result[4], 0.0)
        self.assertEqual(result[5], 0.0)
        self.assertEqual(result[6], 0.0)
        self.assertEqual(result[7], 0.0)

    def test_get_theta_o_eqv_j_ns_for_external_general_part_and_external_opaque_part(self):

        result = oet.get_theta_o_eqv_j_ns_for_external_general_part_and_external_opaque_part(
            drct_j=Direction.SE,
            a_s_j=0.8,
            eps_r_o_j=0.9,
            r_s_o_j=0.04,
            ssp_j=self.ssp,
            w=self.w
        )

        i_s_dn, i_s_sky, i_s_ref, r_s_n = inclined_surface_solar_radiation.get_i_s_j_ns(
            w=self.w,
            drct_j=Direction.SE
        )

        f_ss_dn = self.ssp.get_f_ss_dn_j_ns(h_sun_ns=self.w.h_sun_ns_plus, a_sun_ns=self.w.a_sun_ns_plus)
        f_ss_sky = self.ssp.get_f_ss_sky_j()
        f_ss_ref = self.ssp.get_f_ss_ref_j()

        self.assertEqual(result[0], -15.0 + (0.8 * ((1 - f_ss_dn[0]) * i_s_dn[0] + (1 - f_ss_sky) * i_s_sky[0] + (1 - f_ss_ref) * i_s_ref[0]) - 0.9 * r_s_n[0]) * 0.04)
        self.assertEqual(result[1], -12.0 + (0.8 * ((1 - f_ss_dn[1]) * i_s_dn[1] + (1 - f_ss_sky) * i_s_sky[1] + (1 - f_ss_ref) * i_s_ref[1]) - 0.9 * r_s_n[1]) * 0.04)
        self.assertEqual(result[2], 3.0 + (0.8 * ((1 - f_ss_dn[2]) * i_s_dn[2] + (1 - f_ss_sky) * i_s_sky[2] + (1 - f_ss_ref) * i_s_ref[2]) - 0.9 * r_s_n[2]) * 0.04)
        self.assertEqual(result[3], 5.0 + (0.8 * ((1 - f_ss_dn[3]) * i_s_dn[3] + (1 - f_ss_sky) * i_s_sky[3] + (1 - f_ss_ref) * i_s_ref[3]) - 0.9 * r_s_n[3]) * 0.04)
        self.assertEqual(result[4], 4.0 + (0.8 * ((1 - f_ss_dn[4]) * i_s_dn[4] + (1 - f_ss_sky) * i_s_sky[4] + (1 - f_ss_ref) * i_s_ref[4]) - 0.9 * r_s_n[4]) * 0.04)
        self.assertEqual(result[5], -3.0 + (0.8 * ((1 - f_ss_dn[5]) * i_s_dn[5] + (1 - f_ss_sky) * i_s_sky[5] + (1 - f_ss_ref) * i_s_ref[5]) - 0.9 * r_s_n[5]) * 0.04)
        self.assertEqual(result[6], -7.0 + (0.8 * ((1 - f_ss_dn[6]) * i_s_dn[6] + (1 - f_ss_sky) * i_s_sky[6] + (1 - f_ss_ref) * i_s_ref[6]) - 0.9 * r_s_n[6]) * 0.04)
        self.assertEqual(result[7], -15.0 + (0.8 * ((1 - f_ss_dn[7]) * i_s_dn[7] + (1 - f_ss_sky) * i_s_sky[7] + (1 - f_ss_ref) * i_s_ref[7]) - 0.9 * r_s_n[7]) * 0.04)

    def test_get_theta_o_eqv_j_ns_for_external_transparent_part(self):
        
        wdw = Window(u_w_j=3.0, eta_w_j=0.8, glass_type=GlassType.SINGLE)        
        result = oet.get_theta_o_eqv_j_ns_for_external_transparent_part(
            drct_j=Direction.SE,
            eps_r_o_j=0.9,
            r_s_o_j=0.04,
            u_j=3.0,
            ssp_j=self.ssp,
            wdw_j=wdw,
            w=self.w
        )

        phi = inclined_surface_solar_radiation.get_phi_j_ns(
            h_sun_ns=self.w.h_sun_ns_plus,
            a_sun_ns=self.w.a_sun_ns_plus,
            direction=Direction.SE
        )
        i_s_dn, i_s_sky, i_s_ref, r_s_n = inclined_surface_solar_radiation.get_i_s_j_ns(
            w=self.w,
            drct_j=Direction.SE
        )
        f_ss_dn = self.ssp.get_f_ss_dn_j_ns(h_sun_ns=self.w.h_sun_ns_plus, a_sun_ns=self.w.a_sun_ns_plus)
        f_ss_sky = self.ssp.get_f_ss_sky_j()
        f_ss_ref = self.ssp.get_f_ss_ref_j()

        q = (
            wdw.get_b_w_d_j_ns(phi_j_ns=phi) * (1 - f_ss_dn) * i_s_dn
            + wdw.b_w_s_j * (1 - f_ss_sky) * i_s_sky
            + wdw.b_w_r_j * (1 - f_ss_ref) * i_s_ref
        )

        self.assertEqual(result[0], -15.0 - 0.9 * r_s_n[0] * 0.04 + q[0]/3.0)
        self.assertEqual(result[1], -12.0 - 0.9 * r_s_n[1] * 0.04 + q[1]/3.0)
        self.assertEqual(result[2], 3.0 - 0.9 * r_s_n[2] * 0.04 + q[2]/3.0)
        self.assertEqual(result[3], 5.0 - 0.9 * r_s_n[3] * 0.04 + q[3]/3.0)
        self.assertEqual(result[4], 4.0 - 0.9 * r_s_n[4] * 0.04 + q[4]/3.0)
        self.assertEqual(result[5], -3.0 - 0.9 * r_s_n[5] * 0.04 + q[5]/3.0)
        self.assertEqual(result[6], -7.0 - 0.9 * r_s_n[6] * 0.04 + q[6]/3.0)
        self.assertEqual(result[7], -15.0 - 0.9 * r_s_n[7] * 0.04 + q[7]/3.0)

    def test_get_theta_o_eqv_j_ns_for_external_not_sun_striked(self):

        result = oet.get_theta_o_eqv_j_ns_for_external_not_sun_striked(w=self.w)

        self.assertEqual(result[0], -15.0)
        self.assertEqual(result[1], -12.0)
        self.assertEqual(result[2], 3.0)
        self.assertEqual(result[3], 5.0)
        self.assertEqual(result[4], 4.0)
        self.assertEqual(result[5], -3.0)
        self.assertEqual(result[6], -7.0)
        self.assertEqual(result[7], -15.0)

    def test_get_theta_o_eqv_j_ns_for_ground(self):

        result = oet.get_theta_o_eqv_j_ns_for_ground(w=self.w)

        self.assertAlmostEqual(result[0], -3.571428571)
        self.assertAlmostEqual(result[2], -3.571428571)
        self.assertAlmostEqual(result[3], -3.571428571)
        self.assertAlmostEqual(result[4], -3.571428571)
        self.assertAlmostEqual(result[5], -3.571428571)
        self.assertAlmostEqual(result[6], -3.571428571)
        self.assertAlmostEqual(result[7], -3.571428571)
        




