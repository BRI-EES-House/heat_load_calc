import unittest
import numpy as np

from heat_load_calc import occupants_form_factor


class TestOccupantsFormFactor(unittest.TestCase):

    p_is_js = np.array([
        [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1]
    ])

    n_rm = 3
    n_b = 12

    a_s_js = np.array([
        10.0, 11.0, 12.0, 13.0,
        14.0, 15.0, 16.0, 17.0,
        18.0, 19.0, 20.0, 21.0
    ]).reshape(-1, 1)

    is_floor_js = np.array([
        True, False, False, False,
        True, True, False, False,
        True, False, False, False
    ]).reshape(-1, 1)


    def test_func(self):
        
        results = occupants_form_factor.get_f_mrt_hum_js(
            p_is_js=self.p_is_js,
            a_s_js=self.a_s_js,
            is_floor_js=self.is_floor_js
        )

        self.assertAlmostEqual(results[0][0], 0.45)
        self.assertAlmostEqual(results[0][1], 0.55 * 11.0 / 36.0)
        self.assertAlmostEqual(results[0][2], 0.55 * 12.0 / 36.0)
        self.assertAlmostEqual(results[0][3], 0.55 * 13.0 / 36.0)
        self.assertAlmostEqual(results[0][4], 0.0)
        self.assertAlmostEqual(results[0][5], 0.0)
        self.assertAlmostEqual(results[0][6], 0.0)
        self.assertAlmostEqual(results[0][7], 0.0)
        self.assertAlmostEqual(results[0][8], 0.0)
        self.assertAlmostEqual(results[0][9], 0.0)
        self.assertAlmostEqual(results[0][10], 0.0)
        self.assertAlmostEqual(results[0][11], 0.0)

        self.assertAlmostEqual(results[1][0], 0.0)
        self.assertAlmostEqual(results[1][1], 0.0)
        self.assertAlmostEqual(results[1][2], 0.0)
        self.assertAlmostEqual(results[1][3], 0.0)
        self.assertAlmostEqual(results[1][4], 0.45 * 14.0 / 29.0)
        self.assertAlmostEqual(results[1][5], 0.45 * 15.0 / 29.0)
        self.assertAlmostEqual(results[1][6], 0.55 * 16.0 / 33.0)
        self.assertAlmostEqual(results[1][7], 0.55 * 17.0 / 33.0)
        self.assertAlmostEqual(results[1][8], 0.0)
        self.assertAlmostEqual(results[1][9], 0.0)
        self.assertAlmostEqual(results[1][10], 0.0)
        self.assertAlmostEqual(results[1][11], 0.0)

        self.assertAlmostEqual(results[2][0], 0.0)
        self.assertAlmostEqual(results[2][1], 0.0)
        self.assertAlmostEqual(results[2][2], 0.0)
        self.assertAlmostEqual(results[2][3], 0.0)
        self.assertAlmostEqual(results[2][4], 0.0)
        self.assertAlmostEqual(results[2][5], 0.0)
        self.assertAlmostEqual(results[2][6], 0.0)
        self.assertAlmostEqual(results[2][7], 0.0)
        self.assertAlmostEqual(results[2][8], 0.45)
        self.assertAlmostEqual(results[2][9], 0.55 * 19.0 / 60.0)
        self.assertAlmostEqual(results[2][10], 0.55 * 20.0 / 60.0)
        self.assertAlmostEqual(results[2][11], 0.55 * 21.0 / 60.0)


