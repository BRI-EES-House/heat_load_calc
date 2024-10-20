import unittest
import numpy as np

from heat_load_calc.direction import Direction
from heat_load_calc.weather import Weather, Interval
from heat_load_calc import inclined_surface_solar_radiation as issr


class TestInclinedSurfaceSolarRadiation(unittest.TestCase):

    itv = Interval.M15

    n = itv.get_n_step_annual()

    a_sun_ns = np.zeros(n, dtype=float)

#    a_sun_ns = np.array([
#        0.0, 0.0, 0.0, 0.0,
#        np.pi, np.pi, np.pi, np.pi
#    ])

    a_sun_ns[:8] = np.array([-np.pi/4, 0.0, np.pi/4, np.pi/2, -np.pi/4, 0.0, np.pi/4, np.pi/2])

    h_sun_ns = np.zeros(n, dtype=float)

#    h_sun_ns = np.array([
#        -np.pi/4, 0.0, np.pi/4, np.pi/2,
#        -np.pi/4, 0.0, np.pi/4, np.pi/2,
#    ])

    h_sun_ns[:8] = np.array([-np.pi/4, 0.0, np.pi/4, np.pi/2, -np.pi/4, 0.0, np.pi/4, np.pi/2])

    w = Weather(
        a_sun_ns=a_sun_ns,
        h_sun_ns=h_sun_ns,
        i_dn_ns=np.full(shape=(n), fill_value=100.0, dtype=float),
        i_sky_ns=np.full(shape=(n), fill_value=50.0, dtype=float),
        r_n_ns=np.full(shape=(n), fill_value=30.0, dtype=float),
        theta_o_ns=np.full(shape=(n), fill_value=3.0, dtype=float),
        x_o_ns=np.full(shape=(n), fill_value=0.0, dtype=float),
        itv=itv
    )

    def test_get_phi_j_ns_top(self):

        result = issr.get_phi_j_ns(h_sun_ns=self.h_sun_ns, a_sun_ns=self.a_sun_ns, drct_j=Direction.TOP)

        self.assertAlmostEqual(result[0], np.pi/2)
        self.assertAlmostEqual(result[1], np.pi/2)
        self.assertAlmostEqual(result[2], np.pi/4)
        self.assertAlmostEqual(result[3], 0.0)


    def test_get_phi_j_ns_bottom(self):

        result = issr.get_phi_j_ns(h_sun_ns=self.h_sun_ns, a_sun_ns=self.a_sun_ns, drct_j=Direction.BOTTOM)

        self.assertAlmostEqual(result[0], np.pi/2)
        self.assertAlmostEqual(result[1], np.pi/2)
        self.assertAlmostEqual(result[2], np.pi/2)
        self.assertAlmostEqual(result[3], np.pi/2)


    def test_get_phi_j_ns_south(self):

        result = issr.get_phi_j_ns(h_sun_ns=self.h_sun_ns, a_sun_ns=self.a_sun_ns, drct_j=Direction.S)

        expected = np.arccos(
            np.clip(np.sin(self.h_sun_ns) * np.cos(np.radians(90.0))
            + np.cos(self.h_sun_ns) * np.sin(self.a_sun_ns) * np.sin(np.radians(90.0)) * np.sin(0.0)
            + np.cos(self.h_sun_ns) * np.cos(self.a_sun_ns) * np.sin(np.radians(90.0)) * np.cos(0.0)
            , 0.0, None)
        )
        self.assertAlmostEqual(result[0], expected[0])
        self.assertAlmostEqual(result[1], expected[1])
        self.assertAlmostEqual(result[2], expected[2])
        self.assertAlmostEqual(result[3], expected[3])


    def test_get_i_s_dn_j_ns_top(self):

        result, _, _, _ = issr.get_i_s_j_ns(w=self.w, drct_j=Direction.TOP)

        phi_j_ns = issr.get_phi_j_ns(h_sun_ns=self.w.h_sun_ns_plus, a_sun_ns=self.w.a_sun_ns_plus, drct_j=Direction.TOP)

        expected = self.w.i_dn_ns_plus * np.cos(phi_j_ns)

        self.assertAlmostEqual(result[0], expected[0])
        self.assertAlmostEqual(result[1], expected[1])
        self.assertAlmostEqual(result[2], expected[2])
        self.assertAlmostEqual(result[3], expected[3])
        self.assertAlmostEqual(result[4], expected[4])
        self.assertAlmostEqual(result[5], expected[5])
        self.assertAlmostEqual(result[6], expected[6])
        self.assertAlmostEqual(result[7], expected[7])
        self.assertAlmostEqual(result[8], expected[8])


    def test_get_i_s_dn_j_ns_south(self):

        result, _, _, _ = issr.get_i_s_j_ns(w=self.w, drct_j=Direction.S)

        phi_j_ns = issr.get_phi_j_ns(h_sun_ns=self.w.h_sun_ns_plus, a_sun_ns=self.w.a_sun_ns_plus, drct_j=Direction.S)

        expected = self.w.i_dn_ns_plus * np.cos(phi_j_ns)

        self.assertAlmostEqual(result[0], expected[0])
        self.assertAlmostEqual(result[1], expected[1])
        self.assertAlmostEqual(result[2], expected[2])
        self.assertAlmostEqual(result[3], expected[3])
        self.assertAlmostEqual(result[4], expected[4])
        self.assertAlmostEqual(result[5], expected[5])
        self.assertAlmostEqual(result[6], expected[6])
        self.assertAlmostEqual(result[7], expected[7])
        self.assertAlmostEqual(result[8], expected[8])


    def test_get_i_s_sky_j_ns_top(self):

        _, result, _, _ = issr.get_i_s_j_ns(w=self.w, drct_j=Direction.TOP)

        expected = self.w.i_sky_ns_plus

        self.assertAlmostEqual(result[0], expected[0])
        self.assertAlmostEqual(result[1], expected[1])
        self.assertAlmostEqual(result[2], expected[2])
        self.assertAlmostEqual(result[3], expected[3])
        self.assertAlmostEqual(result[4], expected[4])
        self.assertAlmostEqual(result[5], expected[5])
        self.assertAlmostEqual(result[6], expected[6])
        self.assertAlmostEqual(result[7], expected[7])
        self.assertAlmostEqual(result[8], expected[8])


    def test_get_i_s_sky_j_ns_south(self):

        _, result, _, _ = issr.get_i_s_j_ns(w=self.w, drct_j=Direction.S)

        expected = self.w.i_sky_ns_plus / 2

        self.assertAlmostEqual(result[0], expected[0])
        self.assertAlmostEqual(result[1], expected[1])
        self.assertAlmostEqual(result[2], expected[2])
        self.assertAlmostEqual(result[3], expected[3])
        self.assertAlmostEqual(result[4], expected[4])
        self.assertAlmostEqual(result[5], expected[5])
        self.assertAlmostEqual(result[6], expected[6])
        self.assertAlmostEqual(result[7], expected[7])
        self.assertAlmostEqual(result[8], expected[8])


    def test_get_i_s_ref_j_ns_top(self):

        _, _, result, _ = issr.get_i_s_j_ns(w=self.w, drct_j=Direction.TOP)

        expected = np.zeros_like(a=self.w.h_sun_ns_plus, dtype=float)

        self.assertAlmostEqual(result[0], expected[0])
        self.assertAlmostEqual(result[1], expected[1])
        self.assertAlmostEqual(result[2], expected[2])
        self.assertAlmostEqual(result[3], expected[3])
        self.assertAlmostEqual(result[4], expected[4])
        self.assertAlmostEqual(result[5], expected[5])
        self.assertAlmostEqual(result[6], expected[6])
        self.assertAlmostEqual(result[7], expected[7])
        self.assertAlmostEqual(result[8], expected[8])


    def test_get_i_s_ref_j_ns_south(self):

        _, _, result, _ = issr.get_i_s_j_ns(w=self.w, drct_j=Direction.S)

        i_hrz_ns = np.sin(self.w.h_sun_ns_plus.clip(min=0.0)) * 100.0 + 50.0

        expected = i_hrz_ns * 0.1 * 0.5

        self.assertAlmostEqual(result[0], expected[0])
        self.assertAlmostEqual(result[1], expected[1])
        self.assertAlmostEqual(result[2], expected[2])
        self.assertAlmostEqual(result[3], expected[3])
        self.assertAlmostEqual(result[4], expected[4])
        self.assertAlmostEqual(result[5], expected[5])
        self.assertAlmostEqual(result[6], expected[6])
        self.assertAlmostEqual(result[7], expected[7])
        self.assertAlmostEqual(result[8], expected[8])


    def test_get_r_s_n_j_ns_top(self):

        _, _, _, result = issr.get_i_s_j_ns(w=self.w, drct_j=Direction.TOP)

        expected = self.w.r_n_ns_plus

        self.assertAlmostEqual(result[0], expected[0])
        self.assertAlmostEqual(result[1], expected[1])
        self.assertAlmostEqual(result[2], expected[2])
        self.assertAlmostEqual(result[3], expected[3])
        self.assertAlmostEqual(result[4], expected[4])
        self.assertAlmostEqual(result[5], expected[5])
        self.assertAlmostEqual(result[6], expected[6])
        self.assertAlmostEqual(result[7], expected[7])
        self.assertAlmostEqual(result[8], expected[8])


    def test_get_r_s_n_j_ns_south(self):

        _, _, _, result = issr.get_i_s_j_ns(w=self.w, drct_j=Direction.S)

        expected = self.w.r_n_ns_plus / 2

        self.assertAlmostEqual(result[0], expected[0])
        self.assertAlmostEqual(result[1], expected[1])
        self.assertAlmostEqual(result[2], expected[2])
        self.assertAlmostEqual(result[3], expected[3])
        self.assertAlmostEqual(result[4], expected[4])
        self.assertAlmostEqual(result[5], expected[5])
        self.assertAlmostEqual(result[6], expected[6])
        self.assertAlmostEqual(result[7], expected[7])
        self.assertAlmostEqual(result[8], expected[8])


