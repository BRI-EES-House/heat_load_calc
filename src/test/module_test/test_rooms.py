import unittest

from heat_load_calc.rooms import Rooms


class TestRooms(unittest.TestCase):

    def test_rooms_furniture_default(self):

        rms = Rooms(ds=[
            {
                'id': 0,
                'name': 'test0',
                'sub_name': 'sub_test0',
                'floor_area': 30.0,
                'volume': 70.0,
                'ventilation': {
                    'natural': 350.0
                },
                'furniture': {
                    'input_method': 'default'
                },
                'schedule': {
                    'name': 'test1'
                }
            },
            {
                'id': 1,
                'name': 'test1',
                'sub_name': 'sub_test1',
                'floor_area': 40.0,
                'volume': 130.0,
                'ventilation': {
                    'natural': 620.0
                },
                'furniture': {
                    'input_method': 'default'
                },
                'schedule': {
                    'name': 'test1'
                }
            }
        ])

        self.assertEqual(rms.n_rm, 2)

        self.assertEqual(rms.id_rm_is[0, 0], 0)
        self.assertEqual(rms.id_rm_is[1, 0], 1)

        self.assertEqual(rms.name_rm_is[0, 0], 'test0')
        self.assertEqual(rms.name_rm_is[1, 0], 'test1')

        self.assertEqual(rms.sub_name_rm_is[0, 0], 'sub_test0')
        self.assertEqual(rms.sub_name_rm_is[1, 0], 'sub_test1')

        self.assertEqual(rms.floor_area_is[0, 0], 30.0)
        self.assertEqual(rms.floor_area_is[1, 0], 40.0)

        self.assertEqual(rms.v_rm_is[0, 0], 70.0)
        self.assertEqual(rms.v_rm_is[1, 0], 130.0)

        self.assertEqual(rms.c_sh_frt_is[0, 0], 882000.0)
        self.assertEqual(rms.c_sh_frt_is[1, 0], 1638000.0)

        self.assertEqual(rms.g_sh_frt_is[0, 0], 194.04000000000002)
        self.assertEqual(rms.g_sh_frt_is[1, 0], 360.36)

        self.assertEqual(rms.c_lh_frt_is[0, 0], 1176.0)
        self.assertEqual(rms.c_lh_frt_is[1, 0], 2184.0)

        self.assertEqual(rms.g_lh_frt_is[0, 0], 2.1168)
        self.assertEqual(rms.g_lh_frt_is[1, 0], 3.9312)

        self.assertAlmostEqual(rms.v_vent_ntr_set_is[0, 0], 350.0 / 3600.0)
        self.assertAlmostEqual(rms.v_vent_ntr_set_is[1, 0], 620.0 / 3600.0)

        self.assertAlmostEqual(rms.met_is[0, 0], 1.0)
        self.assertAlmostEqual(rms.met_is[1, 0], 1.0)

    def test_rooms_furniture_specify(self):

        rms = Rooms(ds=[
            {
                'id': 0,
                'name': 'test0',
                'sub_name': 'sub_test0',
                'floor_area': 30.0,
                'volume': 70.0,
                'ventilation': {
                    'natural': 350.0
                },
                'furniture': {
                    'input_method': 'specify',
                    'heat_capacity': 882000.0,
                    'heat_cond': 194.04000000000002,
                    'moisture_capacity': 1176.0,
                    'moisture_cond': 2.1168,
                },
                'schedule': {
                    'name': 'test1'
                }
            },
            {
                'id': 1,
                'name': 'test1',
                'sub_name': 'sub_test1',
                'floor_area': 40.0,
                'volume': 130.0,
                'ventilation': {
                    'natural': 620.0
                },
                'furniture': {
                    'input_method': 'specify',
                    'heat_capacity': 1638000.0,
                    'heat_cond': 360.36,
                    'moisture_capacity': 2184.0,
                    'moisture_cond': 3.9312,
                },
                'schedule': {
                    'name': 'test1'
                }
            }
        ])

        self.assertEqual(rms.n_rm, 2)

        self.assertEqual(rms.id_rm_is[0, 0], 0)
        self.assertEqual(rms.id_rm_is[1, 0], 1)

        self.assertEqual(rms.name_rm_is[0, 0], 'test0')
        self.assertEqual(rms.name_rm_is[1, 0], 'test1')

        self.assertEqual(rms.sub_name_rm_is[0, 0], 'sub_test0')
        self.assertEqual(rms.sub_name_rm_is[1, 0], 'sub_test1')

        self.assertEqual(rms.floor_area_is[0, 0], 30.0)
        self.assertEqual(rms.floor_area_is[1, 0], 40.0)

        self.assertEqual(rms.v_rm_is[0, 0], 70.0)
        self.assertEqual(rms.v_rm_is[1, 0], 130.0)

        self.assertEqual(rms.c_sh_frt_is[0, 0], 882000.0)
        self.assertEqual(rms.c_sh_frt_is[1, 0], 1638000.0)

        self.assertEqual(rms.g_sh_frt_is[0, 0], 194.04000000000002)
        self.assertEqual(rms.g_sh_frt_is[1, 0], 360.36)

        self.assertEqual(rms.c_lh_frt_is[0, 0], 1176.0)
        self.assertEqual(rms.c_lh_frt_is[1, 0], 2184.0)

        self.assertEqual(rms.g_lh_frt_is[0, 0], 2.1168)
        self.assertEqual(rms.g_lh_frt_is[1, 0], 3.9312)

        self.assertAlmostEqual(rms.v_vent_ntr_set_is[0, 0], 350.0 / 3600.0)
        self.assertAlmostEqual(rms.v_vent_ntr_set_is[1, 0], 620.0 / 3600.0)

        self.assertAlmostEqual(rms.met_is[0, 0], 1.0)
        self.assertAlmostEqual(rms.met_is[1, 0], 1.0)
