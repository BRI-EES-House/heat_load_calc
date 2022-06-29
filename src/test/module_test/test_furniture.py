import unittest

from heat_load_calc import furniture


class TestFurniture(unittest.TestCase):

    def test_use_default_value(self):

        c_lh_frt_i, c_sh_frt_i, g_lh_frt_i, g_sh_frt_i = furniture.get_furniture_specs(
            dict_furniture_i={'input_method': 'default'},
            v_rm_i=100.0
        )

        self.assertAlmostEqual(1260000, c_sh_frt_i)
        self.assertAlmostEqual(1260000 * 0.00022, g_sh_frt_i)
        self.assertAlmostEqual(1680, c_lh_frt_i)
        self.assertAlmostEqual(1680*0.0018, g_lh_frt_i)

    def test_use_specified_value(self):

        c_lh_frt_i, c_sh_frt_i, g_lh_frt_i, g_sh_frt_i = furniture.get_furniture_specs(
            dict_furniture_i={
                'input_method': 'default',
                'heat_capacity': 1260000,
                'heat_cond': 1260000 * 0.00022,
                'moisture_capacity': 1680,
                'moisture_cond': 1680*0.0018
            },
            v_rm_i=100.0
        )

        self.assertAlmostEqual(1260000, c_sh_frt_i)
        self.assertAlmostEqual(1260000 * 0.00022, g_sh_frt_i)
        self.assertAlmostEqual(1680, c_lh_frt_i)
        self.assertAlmostEqual(1680*0.0018, g_lh_frt_i)
