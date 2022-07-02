import unittest

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

        self.assertEqual(bdg.c_value, 4.16)

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

        self.assertEqual(bdg.c_value, 4.16)

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

        self.assertEqual(bdg.c_value, 8.28)

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

        self.assertEqual(bdg.c_value, 8.28)

