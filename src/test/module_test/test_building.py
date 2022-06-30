import unittest
import logging

from heat_load_calc import building


@unittest.skip("作成中")
class TestBuilding(unittest.TestCase):

    def test_use_default_value(self):

        building.Building.create_building(
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
