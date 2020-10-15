import unittest
from heat_load_calc.convert import ees_house


class LayerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:

        print('\n testing EES house layer')

        cls._layer1 = ees_house.Layer.make_layer(
            d={
                'name': 'test_layer1',
                'heat_resistance_input_method': 'conductivity',
                'thermal_conductivity': 1.6,
                'thickness': 0.12,
                'volumetric_specific_heat': 1600.0
            }
        )

        cls._layer2 = ees_house.Layer.make_layer(
            d={
                'name': 'test_layer2',
                'heat_resistance_input_method': 'resistance',
                'thermal_resistance': 0.075,
                'thickness': 0.12,
                'volumetric_specific_heat': 1600.0
            }
        )

    def test_name(self):

        self.assertEqual('test_layer1', self._layer1.name)
        self.assertEqual('test_layer2', self._layer2.name)

    def test_thickness(self):

        self.assertEqual(0.12, self._layer1.thickness)
        self.assertEqual(0.12, self._layer2.thickness)

    def test_volumetric_specific_heat(self):

        self.assertEqual(1600.0, self._layer1.volumetric_specific_heat)
        self.assertEqual(1600.0, self._layer2.volumetric_specific_heat)

    def test_r(self):

        self.assertAlmostEqual(0.075, self._layer1.r)
        self.assertAlmostEqual(0.075, self._layer2.r)

    def test_c(self):

        self.assertAlmostEqual(192.0, self._layer1.c)
        self.assertAlmostEqual(192.0, self._layer2.c)

    def test_make_initializer_dict(self):

        d1 = self._layer1.make_initializer_dict(r_res_sub=0.9)
        d2 = self._layer2.make_initializer_dict(r_res_sub=0.9)

        self.assertEqual('test_layer1', d1['name'])
        self.assertAlmostEqual(0.0675, d1['thermal_resistance'])
        self.assertAlmostEqual(192.0, d1['thermal_capacity'])

        self.assertEqual('test_layer2', d2['name'])
        self.assertAlmostEqual(0.0675, d2['thermal_resistance'])
        self.assertAlmostEqual(192.0, d2['thermal_capacity'])


class GeneralPartPartTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:

        print('\n testing EES house general part part')

        cls._gpp1 = ees_house.GeneralPartPart.make_general_part_part(
            d={
                'name': 'test_general_part_part1',
                'part_area_ratio': 0.2,
                'layers': [
                    {
                        'name': 'layer1',
                        'heat_resistance_input_method': 'conductivity',
                        'thermal_conductivity': 1.6,
                        'thickness': 0.12,
                        'volumetric_specific_heat': 1600.0
                    }
                ]
            }
        )

        cls._gpp2 = ees_house.GeneralPartPart.make_general_part_part(
            d={
                'name': 'general',
                'part_area_ratio': 0.83,
                'layers': [
                    {
                        'name': 'gypsum_board',
                        'heat_resistance_input_method': 'conductivity',
                        'thickness': 0.0095,
                        'volumetric_specific_heat': 830.0,
                        'thermal_conductivity': 0.22
                    },
                    {
                        'name': 'GWHG14-38',
                        'heat_resistance_input_method': 'conductivity',
                        'thickness': 0.105,
                        'volumetric_specific_heat': 14.0,
                        'thermal_conductivity': 0.038
                    },
                    {
                        'name': 'plywood',
                        'heat_resistance_input_method': 'conductivity',
                        'thickness': 0.012,
                        'volumetric_specific_heat': 720.0,
                        'thermal_conductivity': 0.16
                    }
                ]
            }
        )

    def test_name(self):

        self.assertEqual('test_general_part_part1', self._gpp1.name)
        self.assertEqual('general', self._gpp2.name)

    def test_part_area_ratio(self):

        self.assertEqual(0.2, self._gpp1.part_area_ratio)
        self.assertEqual(0.83, self._gpp2.part_area_ratio)

    def test_part_layers(self):

        # レイヤー数
        self.assertEqual(1, len(self._gpp1.layers))
        self.assertEqual(3, len(self._gpp2.layers))

        # レイヤー名
        self.assertEqual('layer1', self._gpp1.layers[0].name)
        self.assertEqual('gypsum_board', self._gpp2.layers[0].name)
        self.assertEqual('GWHG14-38', self._gpp2.layers[1].name)
        self.assertEqual('plywood', self._gpp2.layers[2].name)

        # 厚さ
        self.assertEqual(0.12, self._gpp1.layers[0].thickness)
        self.assertEqual(0.0095, self._gpp2.layers[0].thickness)
        self.assertEqual(0.105, self._gpp2.layers[1].thickness)
        self.assertEqual(0.012, self._gpp2.layers[2].thickness)

        # 熱容量
        self.assertEqual(1600.0, self._gpp1.layers[0].volumetric_specific_heat)
        self.assertEqual(830.0, self._gpp2.layers[0].volumetric_specific_heat)
        self.assertEqual(14.0, self._gpp2.layers[1].volumetric_specific_heat)
        self.assertEqual(720.0, self._gpp2.layers[2].volumetric_specific_heat)

        # 熱抵抗
        self.assertEqual(0.075, self._gpp1.layers[0].r)
        self.assertEqual(0.04318181818181818, self._gpp2.layers[0].r)
        self.assertEqual(2.763157894736842, self._gpp2.layers[1].r)
        self.assertEqual(0.075, self._gpp2.layers[2].r)

        # 熱容量
        self.assertEqual(192.0, self._gpp1.layers[0].c)
        self.assertEqual(7.885, self._gpp2.layers[0].c)
        self.assertEqual(1.47, self._gpp2.layers[1].c)
        self.assertEqual(8.64, self._gpp2.layers[2].c)

        # 熱抵抗の合計
        self.assertAlmostEqual(0.075, self._gpp1.get_r_total())
        self.assertAlmostEqual(2.88133971291866018, self._gpp2.get_r_total())

    def test_r_total(self):
        self.assertAlmostEqual(0.12/1.6, self._gpp1.get_r_total())
        self.assertAlmostEqual(0.0095/0.22 + 0.105/0.038 + 0.012/0.16, self._gpp2.get_r_total())

    def test_get_as_dict(self):

        d1 = self._gpp1.get_as_dict()
        d2 = ees_house.GeneralPartPart.make_general_part_part(d=d1).get_as_dict()
        self.assertEqual(d1, d2)

        d1 = self._gpp2.get_as_dict()
        d2 = ees_house.GeneralPartPart.make_general_part_part(d=d1).get_as_dict()
        self.assertEqual(d1, d2)

    def test_make_initializer_dict(self):

        ds = self._gpp1.make_initializer_dict(r_res_sub=0.7)
        self.assertEqual(1, len(ds))
        self.assertEqual('layer1', ds[0]['name'])
        self.assertAlmostEqual(0.12 / 1.6 * 0.7, ds[0]['thermal_resistance'])
        self.assertAlmostEqual(0.12 * 1600.0, ds[0]['thermal_capacity'])

        ds = self._gpp2.make_initializer_dict(r_res_sub=0.7)
        self.assertEqual(3, len(ds))
        self.assertEqual('gypsum_board', ds[0]['name'])
        self.assertAlmostEqual(0.0095 / 0.22 * 0.7, ds[0]['thermal_resistance'])
        self.assertAlmostEqual(0.0095 * 830.0, ds[0]['thermal_capacity'])
        self.assertEqual('GWHG14-38', ds[1]['name'])
        self.assertAlmostEqual(0.105 / 0.038 * 0.7, ds[1]['thermal_resistance'])
        self.assertAlmostEqual(0.105 * 14.0, ds[1]['thermal_capacity'])
        self.assertEqual('plywood', ds[2]['name'])
        self.assertAlmostEqual(0.012 / 0.16 * 0.7, ds[2]['thermal_resistance'])
        self.assertAlmostEqual(0.012 * 720.0, ds[2]['thermal_capacity'])


class GeneralPartSpecTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:

        print('\n testing EES house general part spec')

        # 木造
        cls._gps_wood = ees_house.GeneralPartSpec.make_general_part_spec(
            d={
                'structure': 'wood',
                'r_srf_in': 0.11,
                'r_srf_ex': 0.11,
                'parts': [
                    {
                        'name': 'general',
                        'part_area_ratio': 0.83,
                        'layers': [
                            {
                                'name': 'gypsum_board',
                                'heat_resistance_input_method': 'conductivity',
                                'thickness': 0.0095,
                                'volumetric_specific_heat': 830.0,
                                'thermal_conductivity': 0.22
                            },
                            {
                                'name': 'GWHG14-38',
                                'heat_resistance_input_method': 'conductivity',
                                'thickness': 0.105,
                                'volumetric_specific_heat': 14.0,
                                'thermal_conductivity': 0.038
                            },
                            {
                                'name': 'plywood',
                                'heat_resistance_input_method': 'conductivity',
                                'thickness': 0.012,
                                'volumetric_specific_heat': 720.0,
                                'thermal_conductivity': 0.16
                            }
                        ]
                    },
                    {
                        'name': 'heat_bridge',
                        'part_area_ratio': 0.17,
                        'layers': [
                            {
                                'name': 'gypsum_board',
                                'heat_resistance_input_method': 'conductivity',
                                'thickness': 0.0095,
                                'volumetric_specific_heat': 830.0,
                                'thermal_conductivity': 0.22
                            },
                            {
                                'name': 'wood',
                                'heat_resistance_input_method': 'conductivity',
                                'thickness': 0.105,
                                'volumetric_specific_heat': 520.0,
                                'thermal_conductivity': 0.12
                            },
                            {
                                'name': 'plywood',
                                'heat_resistance_input_method': 'conductivity',
                                'thickness': 0.012,
                                'volumetric_specific_heat': 720.0,
                                'thermal_conductivity': 0.16
                            }
                        ]
                    }
                ]
            },
            general_part_type='wall'
        )

        # RC造
        cls._gps_rc = ees_house.GeneralPartSpec.make_general_part_spec(
            d={
                'structure': 'rc',
                'r_srf_in': 0.11,
                'r_srf_ex': 0.04,
                'parts': [
                    {
                        'name': 'general',
                        'part_area_ratio': 1.0,
                        'layers': [
                            {
                                'name': 'gypsum_board',
                                'heat_resistance_input_method': 'conductivity',
                                'thickness': 0.0095,
                                'volumetric_specific_heat': 830.0,
                                'thermal_conductivity': 0.22
                            },
                            {
                                'name': 'GWHG14-38',
                                'heat_resistance_input_method': 'conductivity',
                                'thickness': 0.105,
                                'volumetric_specific_heat': 14.0,
                                'thermal_conductivity': 0.038
                            },
                            {
                                'name': 'concrete',
                                'heat_resistance_input_method': 'conductivity',
                                'thickness': 0.150,
                                'volumetric_specific_heat': 2000.0,
                                'thermal_conductivity': 1.6
                            }
                        ]
                    }
                ]
            },
            general_part_type='wall'
        )

        # S造
        cls._gps_steel = ees_house.GeneralPartSpec.make_general_part_spec(
            d={
                'structure': 'steel',
                'u_r_value_steel': 0.18,
                'r_srf_in': 0.11,
                'r_srf_ex': 0.11,
                'parts': [
                    {
                        'name': 'general',
                        'part_area_ratio': 1.0,
                        'layers': [
                            {
                                'name': 'gypsum_board',
                                'heat_resistance_input_method': 'conductivity',
                                'thickness': 0.0095,
                                'volumetric_specific_heat': 830.0,
                                'thermal_conductivity': 0.22
                            },
                            {
                                'name': 'GWHG14-38',
                                'heat_resistance_input_method': 'conductivity',
                                'thickness': 0.105,
                                'volumetric_specific_heat': 14.0,
                                'thermal_conductivity': 0.038
                            },
                            {
                                'name': 'plywood',
                                'heat_resistance_input_method': 'conductivity',
                                'thickness': 0.012,
                                'volumetric_specific_heat': 720.0,
                                'thermal_conductivity': 0.16
                            }
                        ]
                    }
                ]
            },
            general_part_type='wall'
        )

        # その他造（屋根） 軽い
        cls._gps_other_roof_light = ees_house.GeneralPartSpec.make_general_part_spec(
            d={
                'structure': 'other',
                'u_value_other': 1.5,
                'weight': 'light'
            },
            general_part_type='roof'
        )

        # その他造（屋根） 重い
        cls._gps_other_roof_heavy = ees_house.GeneralPartSpec.make_general_part_spec(
            d={
                'structure': 'other',
                'u_value_other': 1.5,
                'weight': 'heavy'
            },
            general_part_type='roof'
        )

        # その他造（天井） 軽い
        cls._gps_other_ceiling_light = ees_house.GeneralPartSpec.make_general_part_spec(
            d={
                'structure': 'other',
                'u_value_other': 1.5,
                'weight': 'light'
            },
            general_part_type='ceiling'
        )

        # その他造（天井） 重い
        cls._gps_other_ceiling_heavy = ees_house.GeneralPartSpec.make_general_part_spec(
            d={
                'structure': 'other',
                'u_value_other': 1.5,
                'weight': 'heavy'
            },
            general_part_type='ceiling'
        )

        # その他造（壁） 軽い
        cls._gps_other_wall_light = ees_house.GeneralPartSpec.make_general_part_spec(
            d={
                'structure': 'other',
                'u_value_other': 1.5,
                'weight': 'light'
            },
            general_part_type='wall'
        )

        # その他造（壁） 重い
        cls._gps_other_wall_heavy = ees_house.GeneralPartSpec.make_general_part_spec(
            d={
                'structure': 'other',
                'u_value_other': 1.5,
                'weight': 'heavy'
            },
            general_part_type='wall'
        )

        # その他造（床） 軽い
        cls._gps_other_floor_light = ees_house.GeneralPartSpec.make_general_part_spec(
            d={
                'structure': 'other',
                'u_value_other': 1.5,
                'weight': 'light'
            },
            general_part_type='floor'
        )

        # その他造（床） 重い
        cls._gps_other_floor_heavy = ees_house.GeneralPartSpec.make_general_part_spec(
            d={
                'structure': 'other',
                'u_value_other': 1.5,
                'weight': 'heavy'
            },
            general_part_type='floor'
        )

        # その他造（界床上側） 軽い
        cls._gps_other_upward_boundary_floor_light = ees_house.GeneralPartSpec.make_general_part_spec(
            d={
                'structure': 'other',
                'u_value_other': 1.5,
                'weight': 'light'
            },
            general_part_type='upward_boundary_floor'
        )

        # その他造（界床上側） 重い
        cls._gps_other_upward_boundary_floor_heavy = ees_house.GeneralPartSpec.make_general_part_spec(
            d={
                'structure': 'other',
                'u_value_other': 1.5,
                'weight': 'heavy'
            },
            general_part_type='upward_boundary_floor'
        )

        # その他造（界壁） 軽い
        cls._gps_other_boundary_wall_light = ees_house.GeneralPartSpec.make_general_part_spec(
            d={
                'structure': 'other',
                'u_value_other': 1.5,
                'weight': 'light'
            },
            general_part_type='boundary_wall'
        )

        # その他造（界壁） 重い
        cls._gps_other_boundary_wall_heavy = ees_house.GeneralPartSpec.make_general_part_spec(
            d={
                'structure': 'other',
                'u_value_other': 1.5,
                'weight': 'heavy'
            },
            general_part_type='boundary_wall'
        )

        # その他造（界床下側） 軽い
        cls._gps_other_downward_boundary_floor_light = ees_house.GeneralPartSpec.make_general_part_spec(
            d={
                'structure': 'other',
                'u_value_other': 1.5,
                'weight': 'light'
            },
            general_part_type='downward_boundary_floor'
        )

        # その他造（界床下側） 重い
        cls._gps_other_downward_boundary_floor_heavy = ees_house.GeneralPartSpec.make_general_part_spec(
            d={
                'structure': 'other',
                'u_value_other': 1.5,
                'weight': 'heavy'
            },
            general_part_type='downward_boundary_floor'
        )

    def test_u(self):

        u_wood = 0.83 / (0.11 + 0.0095/0.22 + 0.105/0.038 + 0.012/0.16 + 0.11) \
               + 0.17 / (0.11 + 0.0095/0.22 + 0.105/0.120 + 0.012/0.16 + 0.11)
        self.assertAlmostEqual(u_wood, self._gps_wood.get_u())

        u_rc = 1 / (0.11 + 0.0095/0.22 + 0.105/0.038 + 0.15/1.6 + 0.04)
        self.assertAlmostEqual(u_rc, self._gps_rc.get_u())

        u_steel = 1 / (0.11 + 0.0095/0.22 + 0.105/0.038 + 0.012/0.16 + 0.11) + 0.18
        self.assertAlmostEqual(u_steel, self._gps_steel.get_u())

        self.assertAlmostEqual(1.5, self._gps_other_roof_light.get_u())
        self.assertAlmostEqual(1.5, self._gps_other_ceiling_light.get_u())
        self.assertAlmostEqual(1.5, self._gps_other_wall_light.get_u())
        self.assertAlmostEqual(1.5, self._gps_other_floor_light.get_u())
        self.assertAlmostEqual(1.5, self._gps_other_upward_boundary_floor_light.get_u())
        self.assertAlmostEqual(1.5, self._gps_other_boundary_wall_light.get_u())
        self.assertAlmostEqual(1.5, self._gps_other_downward_boundary_floor_light.get_u())

    def test_eta(self):

        eta_wood = (0.83 / (0.11 + 0.0095/0.22 + 0.105/0.038 + 0.012/0.16 + 0.11)
                    + 0.17 / (0.11 + 0.0095/0.22 + 0.105/0.120 + 0.012/0.16 + 0.11)
                    ) * 0.034
        self.assertAlmostEqual(eta_wood, self._gps_wood.get_eta())

        eta_rc = 0.034 * 1 / (0.11 + 0.0095/0.22 + 0.105/0.038 + 0.15/1.6 + 0.04)
        self.assertAlmostEqual(eta_rc, self._gps_rc.get_eta())

        eta_steel = (1 / (0.11 + 0.0095/0.22 + 0.105/0.038 + 0.012/0.16 + 0.11) + 0.18) * 0.034
        self.assertAlmostEqual(eta_steel, self._gps_steel.get_eta())

        self.assertAlmostEqual(0.051, self._gps_other_roof_light.get_eta())
        self.assertAlmostEqual(0.051, self._gps_other_ceiling_light.get_eta())
        self.assertAlmostEqual(0.051, self._gps_other_wall_light.get_eta())
        self.assertAlmostEqual(0.051, self._gps_other_floor_light.get_eta())
        self.assertAlmostEqual(0.051, self._gps_other_upward_boundary_floor_light.get_eta())
        self.assertAlmostEqual(0.051, self._gps_other_boundary_wall_light.get_eta())
        self.assertAlmostEqual(0.051, self._gps_other_downward_boundary_floor_light.get_eta())

    def test_make_initializer_dict(self):

        def get_r_res(r, r_in, r_ex, u_add):
            u = 1.0 / (r + r_in + r_ex)
            ud = u + u_add
            rd = 1.0 / ud - r_in - r_ex
            r_res = rd / r
            return r_res

        parts = self._gps_wood.make_initializer_dict(u_add=0.1)

        layers = parts[0]
        r_res = get_r_res(r=0.0095/0.22 + 0.105/0.038 + 0.012/0.16, r_in=0.11, r_ex=0.11, u_add=0.1)

        layer = layers[0]
        self.assertEqual('gypsum_board', layer['name'])
        self.assertAlmostEqual(r_res * 0.0095/0.22, layer['thermal_resistance'])
        self.assertAlmostEqual(0.0095*830.0, layer['thermal_capacity'])
        layer = layers[1]
        self.assertEqual('GWHG14-38', layer['name'])
        self.assertAlmostEqual(r_res * 0.105/0.038, layer['thermal_resistance'])
        self.assertAlmostEqual(0.105*14.0, layer['thermal_capacity'])
        layer = layers[2]
        self.assertEqual('plywood', layer['name'])
        self.assertAlmostEqual(r_res * 0.012/0.16, layer['thermal_resistance'])
        self.assertAlmostEqual(0.012*720.0, layer['thermal_capacity'])

        layers = parts[1]
        r_res = get_r_res(r=0.0095/0.22 + 0.105/0.12 + 0.012/0.16, r_in=0.11, r_ex=0.11, u_add=0.1)

        layer = layers[0]
        self.assertEqual('gypsum_board', layer['name'])
        self.assertAlmostEqual(r_res * 0.0095/0.22, layer['thermal_resistance'])
        self.assertAlmostEqual(0.0095*830.0, layer['thermal_capacity'])
        layer = layers[1]
        self.assertEqual('wood', layer['name'])
        self.assertAlmostEqual(r_res * 0.105/0.12, layer['thermal_resistance'])
        self.assertAlmostEqual(0.105*520.0, layer['thermal_capacity'])
        layer = layers[2]
        self.assertEqual('plywood', layer['name'])
        self.assertAlmostEqual(r_res * 0.012/0.16, layer['thermal_resistance'])
        self.assertAlmostEqual(0.012*720.0, layer['thermal_capacity'])

        parts = self._gps_rc.make_initializer_dict(u_add=0.1)

        layers = parts[0]
        r_res = get_r_res(r=0.0095/0.22 + 0.105/0.038 + 0.150/1.6, r_in=0.11, r_ex=0.04, u_add=0.1)

        layer = layers[0]
        self.assertEqual('gypsum_board', layer['name'])
        self.assertAlmostEqual(r_res * 0.0095/0.22, layer['thermal_resistance'])
        self.assertAlmostEqual(0.0095*830.0, layer['thermal_capacity'])
        layer = layers[1]
        self.assertEqual('GWHG14-38', layer['name'])
        self.assertAlmostEqual(r_res * 0.105/0.038, layer['thermal_resistance'])
        self.assertAlmostEqual(0.105*14.0, layer['thermal_capacity'])
        layer = layers[2]
        self.assertEqual('concrete', layer['name'])
        self.assertAlmostEqual(r_res * 0.150/1.6, layer['thermal_resistance'])
        self.assertAlmostEqual(0.150*2000.0, layer['thermal_capacity'])

        parts = self._gps_steel.make_initializer_dict(u_add=0.1)

        layers = parts[0]
        r_res = get_r_res(r=0.0095/0.22 + 0.105/0.038 + 0.012/0.16, r_in=0.11, r_ex=0.11, u_add=0.1+0.18)

        layer = layers[0]
        self.assertEqual('gypsum_board', layer['name'])
        self.assertAlmostEqual(r_res * 0.0095/0.22, layer['thermal_resistance'])
        self.assertAlmostEqual(0.0095*830.0, layer['thermal_capacity'])
        layer = layers[1]
        self.assertEqual('GWHG14-38', layer['name'])
        self.assertAlmostEqual(r_res * 0.105/0.038, layer['thermal_resistance'])
        self.assertAlmostEqual(0.105*14.0, layer['thermal_capacity'])
        layer = layers[2]
        self.assertEqual('plywood', layer['name'])
        self.assertAlmostEqual(r_res * 0.012/0.16, layer['thermal_resistance'])
        self.assertAlmostEqual(0.012*720.0, layer['thermal_capacity'])


    def test_get_as_dict(self):

        d_wood = self._gps_wood.get_as_dict()
        d_wood2 = ees_house.GeneralPartSpec.make_general_part_spec(d=d_wood, general_part_type='wall').get_as_dict()
        self.assertEqual(d_wood, d_wood2)

        d_rc = self._gps_rc.get_as_dict()
        d_rc2 = ees_house.GeneralPartSpec.make_general_part_spec(d=d_rc, general_part_type='wall').get_as_dict()
        self.assertEqual(d_rc, d_rc2)

        d_steel = self._gps_steel.get_as_dict()
        d_steel2 = ees_house.GeneralPartSpec.make_general_part_spec(d=d_steel, general_part_type='wall').get_as_dict()
        self.assertEqual(d_steel, d_steel2)

        d_other1 = self._gps_other_roof_light.get_as_dict()
        self.assertEqual('other', d_other1['structure'])
        self.assertEqual(1.5, d_other1['u_value_other'])

        d_other2 = self._gps_other_ceiling_light.get_as_dict()
        self.assertEqual('other', d_other2['structure'])
        self.assertEqual(1.5, d_other2['u_value_other'])

        d_other3 = self._gps_other_wall_light.get_as_dict()
        self.assertEqual('other', d_other3['structure'])
        self.assertEqual(1.5, d_other3['u_value_other'])

        d_other4 = self._gps_other_floor_light.get_as_dict()
        self.assertEqual('other', d_other4['structure'])
        self.assertEqual(1.5, d_other4['u_value_other'])

        d_other5 = self._gps_other_upward_boundary_floor_light.get_as_dict()
        self.assertEqual('other', d_other5['structure'])
        self.assertEqual(1.5, d_other5['u_value_other'])

        d_other6 = self._gps_other_boundary_wall_light.get_as_dict()
        self.assertEqual('other', d_other6['structure'])
        self.assertEqual(1.5, d_other6['u_value_other'])

        d_other7 = self._gps_other_downward_boundary_floor_light.get_as_dict()
        self.assertEqual('other', d_other7['structure'])
        self.assertEqual(1.5, d_other7['u_value_other'])

    def test_get_r_srf_in(self):

        self.assertAlmostEqual(0.09, self._gps_other_roof_light.r_srf_in)
        self.assertAlmostEqual(0.09, self._gps_other_ceiling_light.r_srf_in)
        self.assertAlmostEqual(0.11, self._gps_other_wall_light.r_srf_in)
        self.assertAlmostEqual(0.15, self._gps_other_floor_light.r_srf_in)
        self.assertAlmostEqual(0.09, self._gps_other_upward_boundary_floor_light.r_srf_in)
        self.assertAlmostEqual(0.11, self._gps_other_boundary_wall_light.r_srf_in)
        self.assertAlmostEqual(0.15, self._gps_other_downward_boundary_floor_light.r_srf_in)

    def test_get_r_srf_ex(self):

        self.assertAlmostEqual(0.04, self._gps_other_roof_light.r_srf_ex)
        self.assertAlmostEqual(0.09, self._gps_other_ceiling_light.r_srf_ex)
        self.assertAlmostEqual(0.04, self._gps_other_wall_light.r_srf_ex)
        self.assertAlmostEqual(0.15, self._gps_other_floor_light.r_srf_ex)
        self.assertAlmostEqual(0.09, self._gps_other_upward_boundary_floor_light.r_srf_ex)
        self.assertAlmostEqual(0.11, self._gps_other_boundary_wall_light.r_srf_ex)
        self.assertAlmostEqual(0.15, self._gps_other_downward_boundary_floor_light.r_srf_ex)

    def test_convert_to_general_part_spec_detail_roof_light(self):

        gpd = self._gps_other_roof_light.convert_to_general_part_spec_detail()
        self.assertAlmostEqual(0.09, gpd.r_srf_in)
        self.assertAlmostEqual(0.04, gpd.r_srf_ex)
        self.assertEqual(1, len(gpd.parts))

        part = gpd.parts[0]
        self.assertEqual('sole_part', part.name)
        self.assertEqual(1.0, part.part_area_ratio)
        self.assertEqual(2, len(part.layers))

        layer = part.layers[0]
        self.assertEqual('gypsum_board', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.0095, layer.thickness)
        self.assertEqual(830.0, layer.volumetric_specific_heat)
        self.assertEqual(0.221, layer._thermal_conductivity)

        layer = part.layers[1]
        self.assertEqual('default_insulation', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertAlmostEqual((1 / 1.5 - 0.09 - 0.04 - 0.0095 / 0.221) * 0.045, layer.thickness)
        self.assertEqual(13.0, layer.volumetric_specific_heat)
        self.assertEqual(0.045, layer._thermal_conductivity)

    def test_convert_to_general_part_spec_detail_roof_heavy(self):

        gpd = self._gps_other_roof_heavy.convert_to_general_part_spec_detail()
        self.assertAlmostEqual(0.09, gpd.r_srf_in)
        self.assertAlmostEqual(0.04, gpd.r_srf_ex)
        self.assertEqual(1, len(gpd.parts))

        part = gpd.parts[0]
        self.assertEqual('sole_part', part.name)
        self.assertEqual(1.0, part.part_area_ratio)
        self.assertEqual(3, len(part.layers))

        layer = part.layers[0]
        self.assertEqual('gypsum_board', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.0095, layer.thickness)
        self.assertEqual(830.0, layer.volumetric_specific_heat)
        self.assertEqual(0.221, layer._thermal_conductivity)

        layer = part.layers[1]
        self.assertEqual('default_insulation', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertAlmostEqual((1 / 1.5 - 0.09 - 0.04 - 0.0095 / 0.221 - 0.120 / 1.6) * 0.045, layer.thickness)
        self.assertEqual(13.0, layer.volumetric_specific_heat)
        self.assertEqual(0.045, layer._thermal_conductivity)

        layer = part.layers[2]
        self.assertEqual('concrete', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.120, layer.thickness)
        self.assertEqual(2000.0, layer.volumetric_specific_heat)
        self.assertEqual(1.6, layer._thermal_conductivity)

    def test_convert_to_general_part_spec_detail_ceiling_light(self):

        gpd = self._gps_other_ceiling_light.convert_to_general_part_spec_detail()
        self.assertAlmostEqual(0.09, gpd.r_srf_in)
        self.assertAlmostEqual(0.09, gpd.r_srf_ex)
        self.assertEqual(1, len(gpd.parts))

        part = gpd.parts[0]
        self.assertEqual('sole_part', part.name)
        self.assertEqual(1.0, part.part_area_ratio)
        self.assertEqual(2, len(part.layers))

        layer = part.layers[0]
        self.assertEqual('gypsum_board', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.0095, layer.thickness)
        self.assertEqual(830.0, layer.volumetric_specific_heat)
        self.assertEqual(0.221, layer._thermal_conductivity)

        layer = part.layers[1]
        self.assertEqual('default_insulation', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertAlmostEqual((1 / 1.5 - 0.09 - 0.09 - 0.0095 / 0.221) * 0.045, layer.thickness)
        self.assertEqual(13.0, layer.volumetric_specific_heat)
        self.assertEqual(0.045, layer._thermal_conductivity)

    def test_convert_to_general_part_spec_detail_ceiling_heavy(self):

        gpd = self._gps_other_ceiling_heavy.convert_to_general_part_spec_detail()
        self.assertAlmostEqual(0.09, gpd.r_srf_in)
        self.assertAlmostEqual(0.09, gpd.r_srf_ex)
        self.assertEqual(1, len(gpd.parts))

        part = gpd.parts[0]
        self.assertEqual('sole_part', part.name)
        self.assertEqual(1.0, part.part_area_ratio)
        self.assertEqual(3, len(part.layers))

        layer = part.layers[0]
        self.assertEqual('gypsum_board', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.0095, layer.thickness)
        self.assertEqual(830.0, layer.volumetric_specific_heat)
        self.assertEqual(0.221, layer._thermal_conductivity)

        layer = part.layers[1]
        self.assertEqual('default_insulation', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertAlmostEqual((1 / 1.5 - 0.09 - 0.09 - 0.0095 / 0.221 - 0.120 / 1.6) * 0.045, layer.thickness)
        self.assertEqual(13.0, layer.volumetric_specific_heat)
        self.assertEqual(0.045, layer._thermal_conductivity)

        layer = part.layers[2]
        self.assertEqual('concrete', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.120, layer.thickness)
        self.assertEqual(2000.0, layer.volumetric_specific_heat)
        self.assertEqual(1.6, layer._thermal_conductivity)

    def test_convert_to_general_part_spec_detail_wall_light(self):

        gpd = self._gps_other_wall_light.convert_to_general_part_spec_detail()
        self.assertAlmostEqual(0.11, gpd.r_srf_in)
        self.assertAlmostEqual(0.04, gpd.r_srf_ex)
        self.assertEqual(1, len(gpd.parts))

        part = gpd.parts[0]
        self.assertEqual('sole_part', part.name)
        self.assertEqual(1.0, part.part_area_ratio)
        self.assertEqual(3, len(part.layers))

        layer = part.layers[0]
        self.assertEqual('gypsum_board', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.0095, layer.thickness)
        self.assertEqual(830.0, layer.volumetric_specific_heat)
        self.assertEqual(0.221, layer._thermal_conductivity)

        layer = part.layers[1]
        self.assertEqual('default_insulation', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertAlmostEqual((1 / 1.5 - 0.11 - 0.04 - 0.0095 / 0.221 - 0.012 / 0.16) * 0.045, layer.thickness)
        self.assertEqual(13.0, layer.volumetric_specific_heat)
        self.assertEqual(0.045, layer._thermal_conductivity)

        layer = part.layers[2]
        self.assertEqual('plywood', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.012, layer.thickness)
        self.assertEqual(720.0, layer.volumetric_specific_heat)
        self.assertEqual(0.16, layer._thermal_conductivity)

    def test_convert_to_general_part_spec_detail_wall_heavy(self):

        gpd = self._gps_other_wall_heavy.convert_to_general_part_spec_detail()
        self.assertAlmostEqual(0.11, gpd.r_srf_in)
        self.assertAlmostEqual(0.04, gpd.r_srf_ex)
        self.assertEqual(1, len(gpd.parts))

        part = gpd.parts[0]
        self.assertEqual('sole_part', part.name)
        self.assertEqual(1.0, part.part_area_ratio)
        self.assertEqual(3, len(part.layers))

        layer = part.layers[0]
        self.assertEqual('gypsum_board', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.0095, layer.thickness)
        self.assertEqual(830.0, layer.volumetric_specific_heat)
        self.assertEqual(0.221, layer._thermal_conductivity)

        layer = part.layers[1]
        self.assertEqual('default_insulation', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertAlmostEqual((1 / 1.5 - 0.11 - 0.04 - 0.0095 / 0.221 - 0.120 / 1.6) * 0.045, layer.thickness)
        self.assertEqual(13.0, layer.volumetric_specific_heat)
        self.assertEqual(0.045, layer._thermal_conductivity)

        layer = part.layers[2]
        self.assertEqual('concrete', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.120, layer.thickness)
        self.assertEqual(2000.0, layer.volumetric_specific_heat)
        self.assertEqual(1.6, layer._thermal_conductivity)

    def test_convert_to_general_part_spec_detail_floor_light(self):

        gpd = self._gps_other_floor_light.convert_to_general_part_spec_detail()
        self.assertAlmostEqual(0.15, gpd.r_srf_in)
        self.assertAlmostEqual(0.15, gpd.r_srf_ex)
        self.assertEqual(1, len(gpd.parts))

        part = gpd.parts[0]
        self.assertEqual('sole_part', part.name)
        self.assertEqual(1.0, part.part_area_ratio)
        self.assertEqual(2, len(part.layers))

        layer = part.layers[0]
        self.assertEqual('plywood', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.024, layer.thickness)
        self.assertEqual(720.0, layer.volumetric_specific_heat)
        self.assertEqual(0.16, layer._thermal_conductivity)

        layer = part.layers[1]
        self.assertEqual('default_insulation', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertAlmostEqual((1 / 1.5 - 0.15 - 0.15 - 0.024 / 0.16) * 0.045, layer.thickness)
        self.assertEqual(13.0, layer.volumetric_specific_heat)
        self.assertEqual(0.045, layer._thermal_conductivity)

    def test_convert_to_general_part_spec_detail_floor_heavy(self):

        gpd = self._gps_other_floor_heavy.convert_to_general_part_spec_detail()
        self.assertAlmostEqual(0.15, gpd.r_srf_in)
        self.assertAlmostEqual(0.15, gpd.r_srf_ex)
        self.assertEqual(1, len(gpd.parts))

        part = gpd.parts[0]
        self.assertEqual('sole_part', part.name)
        self.assertEqual(1.0, part.part_area_ratio)
        self.assertEqual(3, len(part.layers))

        layer = part.layers[0]
        self.assertEqual('plywood', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.024, layer.thickness)
        self.assertEqual(720.0, layer.volumetric_specific_heat)
        self.assertEqual(0.16, layer._thermal_conductivity)

        layer = part.layers[1]
        self.assertEqual('default_insulation', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertAlmostEqual((1 / 1.5 - 0.15 - 0.15 - 0.024 / 0.16 - 0.120 / 1.6) * 0.045, layer.thickness)
        self.assertEqual(13.0, layer.volumetric_specific_heat)
        self.assertEqual(0.045, layer._thermal_conductivity)

        layer = part.layers[2]
        self.assertEqual('concrete', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.120, layer.thickness)
        self.assertEqual(2000.0, layer.volumetric_specific_heat)
        self.assertEqual(1.6, layer._thermal_conductivity)

    def test_convert_to_general_part_spec_detail_upward_boundary_floor_light(self):

        gpd = self._gps_other_upward_boundary_floor_light.convert_to_general_part_spec_detail()
        self.assertAlmostEqual(0.09, gpd.r_srf_in)
        self.assertAlmostEqual(0.09, gpd.r_srf_ex)
        self.assertEqual(1, len(gpd.parts))

        part = gpd.parts[0]
        self.assertEqual('sole_part', part.name)
        self.assertEqual(1.0, part.part_area_ratio)
        self.assertEqual(3, len(part.layers))

        layer = part.layers[0]
        self.assertEqual('gypsum_board', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.0095, layer.thickness)
        self.assertEqual(830.0, layer.volumetric_specific_heat)
        self.assertEqual(0.221, layer._thermal_conductivity)

        layer = part.layers[1]
        self.assertEqual('default_insulation', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertAlmostEqual((1 / 1.5 - 0.09 - 0.09 - 0.0095 / 0.221 - 0.024 / 0.16) * 0.045, layer.thickness)
        self.assertEqual(13.0, layer.volumetric_specific_heat)
        self.assertEqual(0.045, layer._thermal_conductivity)

        layer = part.layers[2]
        self.assertEqual('plywood', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.024, layer.thickness)
        self.assertEqual(720.0, layer.volumetric_specific_heat)
        self.assertEqual(0.16, layer._thermal_conductivity)

    def test_convert_to_general_part_spec_detail_upward_boundary_floor_heavy(self):

        gpd = self._gps_other_upward_boundary_floor_heavy.convert_to_general_part_spec_detail()
        self.assertAlmostEqual(0.09, gpd.r_srf_in)
        self.assertAlmostEqual(0.09, gpd.r_srf_ex)
        self.assertEqual(1, len(gpd.parts))

        part = gpd.parts[0]
        self.assertEqual('sole_part', part.name)
        self.assertEqual(1.0, part.part_area_ratio)
        self.assertEqual(4, len(part.layers))

        layer = part.layers[0]
        self.assertEqual('gypsum_board', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.0095, layer.thickness)
        self.assertEqual(830.0, layer.volumetric_specific_heat)
        self.assertEqual(0.221, layer._thermal_conductivity)

        layer = part.layers[1]
        self.assertEqual('concrete', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.120, layer.thickness)
        self.assertEqual(2000.0, layer.volumetric_specific_heat)
        self.assertEqual(1.6, layer._thermal_conductivity)

        layer = part.layers[2]
        self.assertEqual('default_insulation', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertAlmostEqual((1 / 1.5 - 0.09 - 0.09 - 0.0095 / 0.221 - 0.120 / 1.6 - 0.024 / 0.16) * 0.045, layer.thickness)
        self.assertEqual(13.0, layer.volumetric_specific_heat)
        self.assertEqual(0.045, layer._thermal_conductivity)

        layer = part.layers[3]
        self.assertEqual('plywood', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.024, layer.thickness)
        self.assertEqual(720.0, layer.volumetric_specific_heat)
        self.assertEqual(0.16, layer._thermal_conductivity)

    def test_convert_to_general_part_spec_detail_boundary_wall_light(self):

        gpd = self._gps_other_boundary_wall_light.convert_to_general_part_spec_detail()
        self.assertAlmostEqual(0.11, gpd.r_srf_in)
        self.assertAlmostEqual(0.11, gpd.r_srf_ex)
        self.assertEqual(1, len(gpd.parts))

        part = gpd.parts[0]
        self.assertEqual('sole_part', part.name)
        self.assertEqual(1.0, part.part_area_ratio)
        self.assertEqual(3, len(part.layers))

        layer = part.layers[0]
        self.assertEqual('gypsum_board', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.0095, layer.thickness)
        self.assertEqual(830.0, layer.volumetric_specific_heat)
        self.assertEqual(0.221, layer._thermal_conductivity)

        layer = part.layers[1]
        self.assertEqual('default_insulation', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertAlmostEqual((1 / 1.5 - 0.11 - 0.11 - 0.0095 / 0.221 - 0.0095 / 0.221) * 0.045, layer.thickness)
        self.assertEqual(13.0, layer.volumetric_specific_heat)
        self.assertEqual(0.045, layer._thermal_conductivity)

        layer = part.layers[2]
        self.assertEqual('gypsum_board', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.0095, layer.thickness)
        self.assertEqual(830.0, layer.volumetric_specific_heat)
        self.assertEqual(0.221, layer._thermal_conductivity)

    def test_convert_to_general_part_spec_detail_boundary_wall_heavy(self):

        gpd = self._gps_other_boundary_wall_heavy.convert_to_general_part_spec_detail()
        self.assertAlmostEqual(0.11, gpd.r_srf_in)
        self.assertAlmostEqual(0.11, gpd.r_srf_ex)
        self.assertEqual(1, len(gpd.parts))

        part = gpd.parts[0]
        self.assertEqual('sole_part', part.name)
        self.assertEqual(1.0, part.part_area_ratio)
        self.assertEqual(3, len(part.layers))

        layer = part.layers[0]
        self.assertEqual('gypsum_board', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.0095, layer.thickness)
        self.assertEqual(830.0, layer.volumetric_specific_heat)
        self.assertEqual(0.221, layer._thermal_conductivity)

        layer = part.layers[1]
        self.assertEqual('default_insulation', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertAlmostEqual((1 / 1.5 - 0.11 - 0.11 - 0.0095 / 0.221 - 0.0095 / 0.221) * 0.045, layer.thickness)
        self.assertEqual(13.0, layer.volumetric_specific_heat)
        self.assertEqual(0.045, layer._thermal_conductivity)

        layer = part.layers[2]
        self.assertEqual('gypsum_board', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.0095, layer.thickness)
        self.assertEqual(830.0, layer.volumetric_specific_heat)
        self.assertEqual(0.221, layer._thermal_conductivity)

    def test_convert_to_general_part_spec_detail_downward_boundary_floor_light(self):

        gpd = self._gps_other_downward_boundary_floor_light.convert_to_general_part_spec_detail()
        self.assertAlmostEqual(0.15, gpd.r_srf_in)
        self.assertAlmostEqual(0.15, gpd.r_srf_ex)
        self.assertEqual(1, len(gpd.parts))

        part = gpd.parts[0]
        self.assertEqual('sole_part', part.name)
        self.assertEqual(1.0, part.part_area_ratio)
        self.assertEqual(3, len(part.layers))

        layer = part.layers[0]
        self.assertEqual('plywood', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.024, layer.thickness)
        self.assertEqual(720.0, layer.volumetric_specific_heat)
        self.assertEqual(0.16, layer._thermal_conductivity)

        layer = part.layers[1]
        self.assertEqual('default_insulation', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertAlmostEqual((1 / 1.5 - 0.15 - 0.15 - 0.024 / 0.16 - 0.0095 / 0.221) * 0.045, layer.thickness)
        self.assertEqual(13.0, layer.volumetric_specific_heat)
        self.assertEqual(0.045, layer._thermal_conductivity)

        layer = part.layers[2]
        self.assertEqual('gypsum_board', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.0095, layer.thickness)
        self.assertEqual(830.0, layer.volumetric_specific_heat)
        self.assertEqual(0.221, layer._thermal_conductivity)

    def test_convert_to_general_part_spec_detail_downward_boundary_floor_heavy(self):

        gpd = self._gps_other_downward_boundary_floor_heavy.convert_to_general_part_spec_detail()
        self.assertAlmostEqual(0.15, gpd.r_srf_in)
        self.assertAlmostEqual(0.15, gpd.r_srf_ex)
        self.assertEqual(1, len(gpd.parts))

        part = gpd.parts[0]
        self.assertEqual('sole_part', part.name)
        self.assertEqual(1.0, part.part_area_ratio)
        self.assertEqual(4, len(part.layers))

        layer = part.layers[0]
        self.assertEqual('plywood', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.024, layer.thickness)
        self.assertEqual(720.0, layer.volumetric_specific_heat)
        self.assertEqual(0.16, layer._thermal_conductivity)

        layer = part.layers[1]
        self.assertEqual('default_insulation', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertAlmostEqual((1 / 1.5 - 0.15 - 0.15 - 0.024 / 0.16 - 0.120 / 1.6 - 0.0095 / 0.221) * 0.045, layer.thickness)
        self.assertEqual(13.0, layer.volumetric_specific_heat)
        self.assertEqual(0.045, layer._thermal_conductivity)

        layer = part.layers[2]
        self.assertEqual('concrete', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.120, layer.thickness)
        self.assertEqual(2000.0, layer.volumetric_specific_heat)
        self.assertEqual(1.6, layer._thermal_conductivity)

        layer = part.layers[3]
        self.assertEqual('gypsum_board', layer.name)
        self.assertEqual(ees_house.HeatResistanceInputMethod.CONDUCTIVITY, layer._heat_resistance_input_method)
        self.assertEqual(0.0095, layer.thickness)
        self.assertEqual(830.0, layer.volumetric_specific_heat)
        self.assertEqual(0.221, layer._thermal_conductivity)


if __name__ == '__main__':
    unittest.main()
