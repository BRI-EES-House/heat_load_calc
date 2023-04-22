import unittest
import numpy as np

from heat_load_calc import building


class TestBuilding(unittest.TestCase):

    def test_method_error(self):

        with self.assertRaises(KeyError):

            _ = building.Building.create_building(
                d={
                    'infiltration': {
                        'method': 'error',
                        'story': 1,
                        'c_value_estimate': 'specify',
                        'c_value': 1.0,
                        'inside_pressure': 'negative'
                    }
                }
            )

    def test_specify(self):

        bdg = building.Building.create_building(
            d={
                'infiltration': {
                    'method': 'balance_residential',
                    'story': 1,
                    'c_value_estimate': 'specify',
                    'c_value': 1.0,
                    'inside_pressure': 'negative'
                }
            }
        )

        self.assertEqual(bdg.infiltration_method, 'balance_residential')
        self.assertEqual(bdg.story, building.Story.ONE)
        self.assertEqual(bdg.c_value, 1.0)
        self.assertEqual(bdg.inside_pressure, building.InsidePressure.NEGATIVE)

    def test_calculate_c_value_rc(self):

        bdg = building.Building.create_building(
            d={
                'infiltration': {
                    'method': 'balance_residential',
                    'story': 1,
                    'c_value_estimate': 'calculate',
                    'ua_value': 1.0,
                    'struct': 'rc',
                    'inside_pressure': 'negative'
                }
            }
        )

        self.assertAlmostEqual(bdg.c_value, 4.16)

    def test_calculate_c_value_src(self):
        bdg = building.Building.create_building(
            d={
                'infiltration': {
                    'method': 'balance_residential',
                    'story': 1,
                    'c_value_estimate': 'calculate',
                    'ua_value': 1.0,
                    'struct': 'src',
                    'inside_pressure': 'negative'
                }
            }
        )

        self.assertAlmostEqual(bdg.c_value, 4.16)

    def test_calculate_c_value_wooden(self):
        bdg = building.Building.create_building(
            d={
                'infiltration': {
                    'method': 'balance_residential',
                    'story': 1,
                    'c_value_estimate': 'calculate',
                    'ua_value': 1.0,
                    'struct': 'wooden',
                    'inside_pressure': 'negative'
                }
            }
        )

        self.assertAlmostEqual(bdg.c_value, 8.28)

    def test_calculate_c_value_steel(self):
        bdg = building.Building.create_building(
            d={
                'infiltration': {
                    'method': 'balance_residential',
                    'story': 1,
                    'c_value_estimate': 'calculate',
                    'ua_value': 1.0,
                    'struct': 'steel',
                    'inside_pressure': 'negative'
                }
            }
        )

        self.assertAlmostEqual(bdg.c_value, 8.28)

    def test_define_c_value(self):
        bdg = building.Building.create_building(
            d={
                'infiltration': {
                    'method': 'balance_residential',
                    'story': 1,
                    'c_value_estimate': 'specify',
                    'c_value': 0.2,
                    'inside_pressure': 'negative'
                }
            }
        )

        self.assertEqual(bdg.c_value, 0.2)

    def test_calculate_air_leakage_one_story_negative_pressure(self):

        bdg = building.Building.create_building(
            d={
                'infiltration': {
                    'method': 'balance_residential',
                    'story': 1,
                    'c_value_estimate': 'specify',
                    'c_value': 0.2,
                    'inside_pressure': 'negative'
                }
            }
        )

        result = bdg.get_v_leak_is_n(theta_r_is_n=np.array([20.0, 30.0]), theta_o_n=0.0, v_rm_is=np.array([40.0, 60.0]))

        n_leak = max(0.022 * 0.2 * pow(26.0, 0.5) - 0.28, 0.0)

        self.assertAlmostEqual(result[0], n_leak * 40.0 / 3600)
        self.assertAlmostEqual(result[1], n_leak * 60.0 / 3600)
 
    def test_calculate_air_leakage_one_story_positive_pressure(self):

        bdg = building.Building.create_building(
            d={
                'infiltration': {
                    'method': 'balance_residential',
                    'story': 1,
                    'c_value_estimate': 'specify',
                    'c_value': 0.2,
                    'inside_pressure': 'positive'
                }
            }
        )

        result = bdg.get_v_leak_is_n(theta_r_is_n=np.array([20.0, 30.0]), theta_o_n=0.0, v_rm_is=np.array([40.0, 60.0]))

        n_leak = max(0.022 * 0.2 * pow(26.0, 0.5) - 0.26, 0.0)

        self.assertAlmostEqual(result[0], n_leak * 40.0 / 3600)
        self.assertAlmostEqual(result[1], n_leak * 60.0 / 3600)

    def test_calculate_air_leakage_one_story_positive_balanced(self):

        bdg = building.Building.create_building(
            d={
                'infiltration': {
                    'method': 'balance_residential',
                    'story': 1,
                    'c_value_estimate': 'specify',
                    'c_value': 0.2,
                    'inside_pressure': 'balanced'
                }
            }
        )

        result = bdg.get_v_leak_is_n(theta_r_is_n=np.array([20.0, 30.0]), theta_o_n=0.0, v_rm_is=np.array([40.0, 60.0]))

        n_leak = max(0.022 * 0.2 * pow(26.0, 0.5), 0.0)

        self.assertAlmostEqual(result[0], n_leak * 40.0 / 3600)
        self.assertAlmostEqual(result[1], n_leak * 60.0 / 3600)

    def test_calculate_air_leakage_second_story_negative_pressure(self):

        bdg = building.Building.create_building(
            d={
                'infiltration': {
                    'method': 'balance_residential',
                    'story': 2,
                    'c_value_estimate': 'specify',
                    'c_value': 0.2,
                    'inside_pressure': 'negative'
                }
            }
        )

        result = bdg.get_v_leak_is_n(theta_r_is_n=np.array([20.0, 30.0]), theta_o_n=0.0, v_rm_is=np.array([40.0, 60.0]))

        n_leak = max(0.020 * 0.2 * pow(26.0, 0.5) - 0.13, 0.0)

        self.assertAlmostEqual(result[0], n_leak * 40.0 / 3600)
        self.assertAlmostEqual(result[1], n_leak * 60.0 / 3600)
 
    def test_calculate_air_leakage_second_story_positive_pressure(self):

        bdg = building.Building.create_building(
            d={
                'infiltration': {
                    'method': 'balance_residential',
                    'story': 2,
                    'c_value_estimate': 'specify',
                    'c_value': 0.2,
                    'inside_pressure': 'positive'
                }
            }
        )

        result = bdg.get_v_leak_is_n(theta_r_is_n=np.array([20.0, 30.0]), theta_o_n=0.0, v_rm_is=np.array([40.0, 60.0]))

        n_leak = max(0.020 * 0.2 * pow(26.0, 0.5) - 0.14, 0.0)

        self.assertAlmostEqual(result[0], n_leak * 40.0 / 3600)
        self.assertAlmostEqual(result[1], n_leak * 60.0 / 3600)

    def test_calculate_air_leakage_second_story_positive_balanced(self):

        bdg = building.Building.create_building(
            d={
                'infiltration': {
                    'method': 'balance_residential',
                    'story': 2,
                    'c_value_estimate': 'specify',
                    'c_value': 0.2,
                    'inside_pressure': 'balanced'
                }
            }
        )

        result = bdg.get_v_leak_is_n(theta_r_is_n=np.array([20.0, 30.0]), theta_o_n=0.0, v_rm_is=np.array([40.0, 60.0]))

        n_leak = max(0.020 * 0.2 * pow(26.0, 0.5), 0.0)

        self.assertAlmostEqual(result[0], n_leak * 40.0 / 3600)
        self.assertAlmostEqual(result[1], n_leak * 60.0 / 3600)
