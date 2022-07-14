import unittest
import numpy as np

from heat_load_calc.solar_shading import SolarShading
from heat_load_calc.direction import Direction


class TestSolarShading(unittest.TestCase):

    def test_solar_shading_not(self):

        ss = SolarShading.create(
            ssp_dict={
                'existence': False
            },
            direction=Direction.S
        )

        self.assertEqual(ss.get_f_ss_d_j_ns(h_sun_n=np.array([0.0]), a_sun_n=np.array([0.0])), np.array([0.0]))
        self.assertEqual(ss.get_f_ss_s_j(), 0.0)

    def test_solar_shading_simple(self):

        ss = SolarShading.create(
            ssp_dict={
                'existence': True,
                'input_method': 'simple',
                'depth': 0.4,
                'd_h': 2.0,
                'd_e': 0.1
            },
            direction=Direction.S
        )

        results = ss.get_f_ss_d_j_ns(
            h_sun_n=np.array([0.0, np.pi/4, np.pi/4]),
            a_sun_n=np.array([0.0, 0.0, np.pi/4])
        )
        expected = [0.0, 0.15, (0.4*2**0.5-0.1)/2.0]

        for r, e in zip(results, expected):
            with self.subTest(r=r, e=e):
                self.assertAlmostEqual(r, e)

        self.assertAlmostEqual(ss.get_f_ss_s_j(), 0.068638682)

    @unittest.skip('not implemented')
    def test_solar_shading_detail(self):
        pass


if __name__ == '__main__':
    unittest.main()
