import unittest
import numpy as np


from heat_load_calc import transmission_solar_radiation as tsr
from heat_load_calc.weather import Weather
from heat_load_calc.interval import Interval
from heat_load_calc.direction import Direction
from heat_load_calc.solar_shading import SolarShading, SolarShadingSimple
from heat_load_calc import inclined_surface_solar_radiation
from heat_load_calc.window import Window, GlassType


class TestTransmissionSolarRadiation(unittest.TestCase):

    a_sun_ns = np.array([0.0, np.pi/6, np.pi/3, np.pi/2, np.pi*2/3, np.pi*5/6, np.pi])
    h_sun_ns = np.array([0.0, np.pi/6, np.pi/3, np.pi/2, np.pi/3, np.pi/6, 0.0])
    i_dn_ns = np.array([10.0, 100.0, 200.0, 300.0, 200.0, 100.0, 10.0])
    i_sky_ns = np.array([10.0, 100.0, 200.0, 300.0, 200.0, 100.0, 10.0])
    r_n_ns = np.array([20.0, 19.0, 18.0, 17.0, 18.0, 19.0, 20.0])
    theta_o_ns = np.array([-15.0, -12.0, 3.0, 5.0, 4.0, -3.0, -7.0])
    x_o_ns = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    itv = Interval.M15

    w = Weather(a_sun_ns=a_sun_ns, h_sun_ns=h_sun_ns, i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, r_n_ns=r_n_ns, theta_o_ns=theta_o_ns, x_o_ns=x_o_ns)


    def test_get_q_trs_sol_j_ns_for_transparent_sun_striked(self):
        
        ssp = SolarShadingSimple(alpha_w_j=-np.pi/4, l_z_j=0.4, l_y_h_j=1.5, l_y_e_j=0.3)
        wdw = Window(u_w_std_j=3.0, eta_w_std_j=0.8, t_glz_j=GlassType.SINGLE)
        result = tsr.get_q_trs_sol_j_ns_for_transparent_sun_striked(
            t_drct_j=Direction.SE,
            a_s_j=10.0,
            ssp_j=ssp,
            window_j=wdw,
            w=self.w
        )

        phis = inclined_surface_solar_radiation.get_phi_j_ns(
            h_sun_ns=self.w.h_sun_ns_plus,
            a_sun_ns=self.w.a_sun_ns_plus,
            drct_j=Direction.SE
        )
        i_s_dn, i_s_sky, i_s_ref, _ = inclined_surface_solar_radiation.get_i_s_j_ns(
            w=self.w,
            drct_j=Direction.SE
        )
        f_ss_d = ssp.get_f_ss_dn_j_ns(h_sun_ns=self.w.h_sun_ns_plus, a_sun_ns=self.w.a_sun_ns_plus)
        f_ss_s = ssp.get_f_ss_sky_j()
        f_ss_r = ssp.get_f_ss_ref_j()
        tau_w_d = wdw.get_tau_w_d_j_ns(phi_j_ns=phis)
        tau_w_s = wdw.tau_w_s_j
        tau_w_r = wdw.tau_w_r_j
        q_trs_sol_dn = tau_w_d * (1 - f_ss_d) * i_s_dn
        q_trs_sol_sky = tau_w_s * (1 - f_ss_s) * i_s_sky
        q_trs_sol_ref = tau_w_r * (1 - f_ss_r) * i_s_ref
        q_trs_sol = (q_trs_sol_dn + q_trs_sol_sky + q_trs_sol_ref) * 10.0
        self.assertAlmostEqual(result[0], q_trs_sol[0])
        self.assertAlmostEqual(result[1], q_trs_sol[1])
        self.assertAlmostEqual(result[2], q_trs_sol[2])
        self.assertAlmostEqual(result[3], q_trs_sol[3])
        self.assertAlmostEqual(result[4], q_trs_sol[4])
        self.assertAlmostEqual(result[5], q_trs_sol[5])
        self.assertAlmostEqual(result[6], q_trs_sol[6])



