import unittest
import copy
import numpy as np

from heat_load_calc.initializer import building_part_summarize as bps
from heat_load_calc.initializer import boundary_simple as bs


class MyTestCase(unittest.TestCase):

    def test_part_integratable(self):

        '''
        部位が集約可能かどうかのテスト
        '''

        print('test_part_integratable')

        # 部位情報の入力
        d1 = {
            'id': 0,
            'name': 'bp1',
            'connected_room_id': 0,
            'boundary_type': 'external_general_part',
            'area': 10.0,
            'is_sun_striked_outside': True,
            'solar_shading_part': {
                'existence': False
            },
            'outside_heat_transfer_resistance': 0.04,
            'outside_emissivity': 0.9,
            'outside_solar_absorption': 0.8,
            'temp_dif_coef': 1.0,
            'is_solar_absorbed_inside': False,
            'direction': 's',
            'inside_heat_transfer_resistance': 9.1,
            'layers': [
                {
                    'name': 'plaster_board',
                    'thermal_resistance': 0.0432,
                    'thermal_capacity': 7.885
                }
            ]
        }

        # BoundarySimpleクラスの作成
        bs1 = bs.get_boundary_simple(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, d1)

        self.assertEqual(True, bps._is_boundary_integratable(bs1=bs1, bs2=bs1))

        # 部位情報のコピー
        d15 = copy.deepcopy(d1)
        d15['id'] = 1
        d15['name'] = 'bp15'
        d15['area'] = 20.0
        # BoundarySimpleクラスの作成
        bs15 = bs.get_boundary_simple(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, d15)

        self.assertEqual(True, bps._is_boundary_integratable(bs1=bs1, bs2=bs15))

        # 部位情報のコピー
        d2 = copy.deepcopy(d1)
        d2['id'] = 1
        d2['name'] = 'bp2'
        d2['connected_room_id'] = 1

        # BoundarySimpleクラスの作成
        bs2 = bs.get_boundary_simple(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, d2)

        self.assertEqual(False, bps._is_boundary_integratable(bs1=bs1, bs2=bs2))

        # 部位情報のコピー
        d3 = copy.deepcopy(d1)
        d3['id'] = 1
        d3['name'] = 'bp3'
        d3['temp_dif_coef'] = 0.3

        # BoundarySimpleクラスの作成
        bs3 = bs.get_boundary_simple(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, d3)

        self.assertEqual(False, bps._is_boundary_integratable(bs1=bs1, bs2=bs3))

        # 部位情報のコピー
        d4 = copy.deepcopy(d1)
        d4['id'] = 1
        d4['name'] = 'bp4'
        d4['is_solar_absorbed_inside'] = True

        # BoundarySimpleクラスの作成
        bs4 = bs.get_boundary_simple(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, d4)

        self.assertEqual(False, bps._is_boundary_integratable(bs1=bs1, bs2=bs4))

        # 部位情報のコピー
        d5 = copy.deepcopy(d1)
        d5['id'] = 1
        d5['name'] = 'bp5'
        d5['is_sun_striked_outside'] = False

        # BoundarySimpleクラスの作成
        bs5 = bs.get_boundary_simple(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, d5)

        self.assertEqual(False, bps._is_boundary_integratable(bs1=bs1, bs2=bs5))

        # 部位情報のコピー
        d6 = copy.deepcopy(d1)
        d6['id'] = 1
        d6['name'] = 'bp6'
        d6['direction'] = 'n'

        # BoundarySimpleクラスの作成
        bs6 = bs.get_boundary_simple(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, d6)

        self.assertEqual(False, bps._is_boundary_integratable(bs1=bs1, bs2=bs6))

        # 部位情報のコピー
        d7 = copy.deepcopy(d1)
        d7['id'] = 1
        d7['name'] = 'bp7'
        d7['inside_heat_transfer_resistance'] = 6.7

        # BoundarySimpleクラスの作成
        bs7 = bs.get_boundary_simple(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, d7)

        self.assertEqual(False, bps._is_boundary_integratable(bs1=bs1, bs2=bs7))

        # 部位情報の入力
        d8 = {
            'id': 0,
            'name': 'bp1',
            'connected_room_id': 1,
            'boundary_type': 'external_opaque_part',
            'area': 10.0,
            'is_sun_striked_outside': True,
            'solar_shading_part': {
                'existence': False
            },
            'outside_heat_transfer_resistance': 0.04,
            'outside_emissivity': 0.9,
            'outside_solar_absorption': 0.8,
            'temp_dif_coef': 1.0,
            'is_solar_absorbed_inside': False,
            'direction': 's',
            'inside_heat_transfer_resistance': 9.1,
            'u_value': 4.65
        }

        # BoundarySimpleクラスの作成
        bs8 = bs.get_boundary_simple(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, d8)

        self.assertEqual(False, bps._is_boundary_integratable(bs1=bs1, bs2=bs8))

        # 部位情報の入力
        d9 = {
            "id": 0,
            "name": "internal_wall_non_occupant",
            "connected_room_id": 0,
            "boundary_type": "internal",
            "area": 21.6125,
            "is_sun_striked_outside": False,
            "temp_dif_coef": 1.0,
            "next_room_type": "non_occupant_room",
            "rear_surface_boundary_id": 45,
            "is_solar_absorbed_inside": False,
            "inside_heat_transfer_resistance": 0.11,
            "outside_heat_transfer_resistance": 0.11,
            "layers": [
                {
                    "name": "plaster_board",
                    "thermal_resistance": 0.0568,
                    "thermal_capacity": 10.375
                }
            ],
            "solar_shading_part": {
                "existence": False
            }
        }

        # BoundarySimpleクラスの作成
        bs9 = bs.get_boundary_simple(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, d9)

        # 部位情報の入力
        d10 = copy.deepcopy(d9)
        d10['id'] = 1

        # BoundarySimpleクラスの作成
        bs10 = bs.get_boundary_simple(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, d10)

        self.assertEqual(True, bps._is_boundary_integratable(bs1=bs9, bs2=bs10))

        # 部位情報の入力
        d11 = copy.deepcopy(d9)
        d11['id'] = 1
        d11["next_room_type"] = 'other_occupant_room'

        # BoundarySimpleクラスの作成
        bs11 = bs.get_boundary_simple(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, d11)

        self.assertEqual(False, bps._is_boundary_integratable(bs1=bs9, bs2=bs11))

    def test_steady_part_summarize(self):

        '''
        定常部位の集約結果のテスト
        '''

        print('test_steady_part_summarize')

        # 部位情報の入力
        d1 = {
            "id": 0,
            "name": "bp1",
            "connected_room_id": 0,
            "boundary_type": "external_transparent_part",
            "area": 1.0,
            "is_sun_striked_outside": True,
            "temp_dif_coef": 1.0,
            "direction": "s",
            "is_solar_absorbed_inside": False,
            "inside_heat_transfer_resistance": 0.11,
            "outside_heat_transfer_resistance": 0.04,
            "outside_emissivity": 0.9,
            "incident_angle_characteristics": "multiple",
            "eta_value": 0.4,
            "u_value": 4.0,
            "solar_shading_part": {
                "existence": False
            }
        }

        # BoundarySimpleクラスの作成
        bs1 = bs.get_boundary_simple(0.0, np.zeros(8760 * 4), np.full(8760 * 4, 50.0), 0.0, np.zeros(8760 * 4), np.full(8760 * 4, 0.0), d1)

        # 部位情報の入力
        d2 = {
            "id": 5,
            "name": "bp2",
            "connected_room_id": 0,
            "boundary_type": "external_transparent_part",
            "area": 3.0,
            "is_sun_striked_outside": True,
            "temp_dif_coef": 1.0,
            "direction": "s",
            "is_solar_absorbed_inside": False,
            "inside_heat_transfer_resistance": 0.11,
            "outside_heat_transfer_resistance": 0.04,
            "outside_emissivity": 0.9,
            "incident_angle_characteristics": "multiple",
            "eta_value": 0.6,
            "u_value": 2.0,
            "solar_shading_part": {
                "existence": False
            }
        }

        # BoundarySimpleクラスの作成
        bs2 = bs.get_boundary_simple(0.0, np.zeros(8760 * 4), np.full(8760 * 4, 50.0), 0.0, np.zeros(8760 * 4), np.full(8760 * 4, 0.0), d2)

        self.assertEqual(True, bps._is_boundary_integratable(bs1=bs1, bs2=bs2))

        # 部位の集約
        bs3 = bps.integrate([bs1, bs2])
        # 集約結果のテスト
        # 名称
        self.assertEqual('integrated_boundary0', bs3[0].name)

        # 面積
        self.assertAlmostEqual(4.0, bs3[0].area)

        # 貫流応答の初項
        self.assertAlmostEqual(1.0, bs3[0].rft0)

        # 吸熱応答の初項
        rm1 = 1.0 / d1['u_value'] - d1['inside_heat_transfer_resistance']
        rm2 = 1.0 / d2['u_value'] - d2['inside_heat_transfer_resistance']
        rm3 = (rm1 * d1['area'] + rm2 * d2['area']) / (d1['area'] + d2['area'])
        self.assertAlmostEqual(rm3, bs3[0].rfa0)

        # 透過日射のテスト
        self.assertAlmostEqual(bs1.q_trs_sol[0] + bs2.q_trs_sol[0], bs3[0].q_trs_sol[0])


    def test_unsteady_part_summarize(self):

        '''
        非定常部位の集約結果のテスト
        '''

        print('test_unsteady_part_summarize')

        # 部位情報
        d1 = {
            "id": 4,
            "name": "south_exterior_wall",
            "connected_room_id": 0,
            "boundary_type": "external_general_part",
            "area": 10.0,
            "is_sun_striked_outside": True,
            "temp_dif_coef": 1.0,
            "direction": "s",
            "is_solar_absorbed_inside": False,
            "inside_heat_transfer_resistance": 0.11,
            "outside_heat_transfer_resistance": 0.04,
            "outside_emissivity": 0.9,
            "outside_solar_absorption": 0.8,
            "layers": [
                {
                    "name": "plaster_board",
                    "thermal_resistance": 0.0432,
                    "thermal_capacity": 7.885
                },
                {
                    "name": "non-hermetic_air_layer",
                    "thermal_resistance": 0.09,
                    "thermal_capacity": 0.0
                },
                {
                    "name": "glass_wool_10K",
                    "thermal_resistance": 1.28,
                    "thermal_capacity": 0.512
                },
                {
                    "name": "plywood",
                    "thermal_resistance": 0.075,
                    "thermal_capacity": 8.64
                },
                {
                    "name": "wood-wool_and_flake_boards",
                    "thermal_resistance": 0.0882,
                    "thermal_capacity": 25.1789
                }
            ],
            "solar_shading_part": {
                "existence": False
            }
        }

        d2 = {
            "id": 5,
            "name": "south_exterior_wall",
            "connected_room_id": 0,
            "boundary_type": "external_general_part",
            "area": 20.0,
            "is_sun_striked_outside": True,
            "temp_dif_coef": 1.0,
            "direction": "s",
            "is_solar_absorbed_inside": False,
            "inside_heat_transfer_resistance": 0.11,
            "outside_heat_transfer_resistance": 0.04,
            "outside_emissivity": 0.9,
            "outside_solar_absorption": 0.8,
            "layers": [
                {
                    "name": "plaster_board",
                    "thermal_resistance": 0.0432,
                    "thermal_capacity": 7.885
                }
            ],
            "solar_shading_part": {
                "existence": False
            }
        }

        # BoundarySimpleの作成
        bs1 = bs.get_boundary_simple(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, d1)
        bs2 = bs.get_boundary_simple(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, d2)

        # 部位の集約
        bs3 = bps.integrate([bs1, bs2])

        # 応答係数初稿のテスト
        self.assertAlmostEqual((bs1.rft0 * bs1.area + bs2.rft0 * bs2.area)
                               / (bs1.area + bs2.area), bs3[0].rft0)
        self.assertAlmostEqual((bs1.rfa0 * bs1.area + bs2.rfa0 * bs2.area)
                               / (bs1.area + bs2.area), bs3[0].rfa0)

        # 指数項別応答係数のテスト
        for i in range(10):
            self.assertAlmostEqual((bs1.rft1[i] * bs1.area + bs2.rft1[i] * bs2.area)
                                   / (bs1.area + bs2.area), bs3[0].rft1[i])
            self.assertAlmostEqual((bs1.rfa1[i] * bs1.area + bs2.rfa1[i] * bs2.area)
                                   / (bs1.area + bs2.area), bs3[0].rfa1[i])


if __name__ == '__main__':
    unittest.main()
