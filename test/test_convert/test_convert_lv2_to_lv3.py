import unittest

import heat_load_calc.convert.convert_lv2_to_lv3 as t
from heat_load_calc.convert import ees_house


class TestConvertLv2toLv3(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:

        print('\n testing convert lv2 to lv3')

    def test_get_separated_areas(self):

        areas = t.get_separated_areas(75.0, 20.0, 50.0, 100.0)
        self.assertEqual(75.0 * 0.2, areas[0])
        self.assertEqual(75.0 * 0.5, areas[1])
        self.assertEqual(75.0 * 0.3, areas[2])

    def test_get_separated_length(self):

        lengths = t.get_separated_lengths(5.0, 20.0, 50.0, 100.0)
        self.assertEqual(5.0 * 0.2, lengths[0])
        self.assertEqual(5.0 * 0.5, lengths[1])
        self.assertEqual(5.0 * 0.3, lengths[2])

    def test_get_general_parts(self):

        d = {
            'common': {
                'region': 6,
                'main_occupant_room_floor_area': 30.0,
                'other_occupant_room_floor_area': 60.0,
                'total_floor_area': 120.0,
            },
            'envelope': {
                'general_parts': [
                    {
                        'name': 'test_part',
                        'general_part_type': 'wall',
                        'next_space': 'outdoor',
                        'direction': 'top',
                        'area': 67.8,
                        'space_type': 'undefined',
                        'sunshade': {
                            'is_defined': False
                        },
                        'spec': {
                            'structure': 'other',
                            'u_value_other': 1.2
                        },
                    }
                ]
            }
        }

        gps_lv3 = t.get_general_parts_lv3(
            a_f_mr=d['common']['main_occupant_room_floor_area'],
            a_f_or=d['common']['other_occupant_room_floor_area'],
            a_f_total=d['common']['total_floor_area'],
            gps=ees_house.GeneralPart.make_general_parts(ds=d['envelope']['general_parts'])
        )
        result = [gp_lv3.get_as_dict() for gp_lv3 in gps_lv3]

        self.assertEqual(3, len(result))
        self.assertEqual('test_part_main_occupant_room', result[0]['name'])
        self.assertEqual('test_part_other_occupant_room', result[1]['name'])
        self.assertEqual('test_part_non_occupant_room', result[2]['name'])
        self.assertEqual('wall', result[0]['general_part_type'])
        self.assertEqual('wall', result[1]['general_part_type'])
        self.assertEqual('wall', result[2]['general_part_type'])
        self.assertEqual('outdoor', result[0]['next_space'])
        self.assertEqual('outdoor', result[1]['next_space'])
        self.assertEqual('outdoor', result[2]['next_space'])
        self.assertEqual('top', result[0]['direction'])
        self.assertEqual('top', result[1]['direction'])
        self.assertEqual('top', result[2]['direction'])
        self.assertEqual(67.8 * 30.0 / 120.0, result[0]['area'])
        self.assertEqual(67.8 * 60.0 / 120.0, result[1]['area'])
        self.assertEqual(67.8 * 30.0 / 120.0, result[2]['area'])
        self.assertEqual('other', result[0]['spec']['structure'])
        self.assertEqual('other', result[1]['spec']['structure'])
        self.assertEqual('other', result[2]['spec']['structure'])

    def test_get_windows(self):

        d = {
            'common': {
                'region': 6,
                'main_occupant_room_floor_area': 30.0,
                'other_occupant_room_floor_area': 60.0,
                'total_floor_area': 120.0,
            },
            'envelope': {
                'windows': [
                    {
                        'name': 'test_part',
                        'next_space': 'outdoor',
                        'direction': 'top',
                        'area': 30.25,
                        'space_type': 'undefined',
                        'sunshade': {
                            'is_defined': True,
                            'input': 'not_input'
                        },
                        'spec': {
                            'window_type': 'single',
                            'windows': [
                                {
                                    'u_value_input_method': 'u_value_directly',
                                    'u_value': 3.0,
                                    'eta_value_input_method': 'eta_d_value_directly',
                                    'eta_d_h_value': 0.5,
                                    'eta_d_c_value': 0.5,
                                    'glass_type': 'single'
                                }
                            ],
                            'attachment_type': 'none',
                            'is_windbreak_room_attached': False
                        },
                    }
                ]
            }
        }

        ws_lv3 = t.get_windows_lv3(
            a_f_mr=d['common']['main_occupant_room_floor_area'],
            a_f_or=d['common']['other_occupant_room_floor_area'],
            a_f_total=d['common']['total_floor_area'],
            ws=ees_house.Window.make_windows(ds=d['envelope']['windows'])
        )

        result = [w_lv3.get_as_dict() for w_lv3 in ws_lv3]

        self.assertEqual(3, len(result))
        self.assertEqual('test_part_main_occupant_room', result[0]['name'])
        self.assertEqual('test_part_other_occupant_room', result[1]['name'])
        self.assertEqual('test_part_non_occupant_room', result[2]['name'])
        self.assertEqual('outdoor', result[0]['next_space'])
        self.assertEqual('outdoor', result[1]['next_space'])
        self.assertEqual('outdoor', result[2]['next_space'])
        self.assertEqual('top', result[0]['direction'])
        self.assertEqual('top', result[1]['direction'])
        self.assertEqual('top', result[2]['direction'])
        self.assertEqual(30.25 * 30.0 / 120.0, result[0]['area'])
        self.assertEqual(30.25 * 60.0 / 120.0, result[1]['area'])
        self.assertEqual(30.25 * 30.0 / 120.0, result[2]['area'])
        self.assertEqual('single', result[0]['spec']['window_type'])
        self.assertEqual('single', result[1]['spec']['window_type'])
        self.assertEqual('single', result[2]['spec']['window_type'])

    def test_get_doors(self):

        d = {
            'common': {
                'region': 6,
                'main_occupant_room_floor_area': 30.0,
                'other_occupant_room_floor_area': 60.0,
                'total_floor_area': 120.0,
            },
            'envelope': {
                'doors': [
                    {
                        'name': 'test_part',
                        'next_space': 'outdoor',
                        'direction': 'top',
                        'area': 2.52,
                        'space_type': 'undefined',
                        'sunshade': {
                            'is_defined': False
                        },
                        'spec': {
                            'u_value': 2.0
                        },
                    }
                ]
            }
        }

        ds_lv3 = t.get_doors_lv3(
            a_f_mr=d['common']['main_occupant_room_floor_area'],
            a_f_or=d['common']['other_occupant_room_floor_area'],
            a_f_total=d['common']['total_floor_area'],
            ds=ees_house.Door.make_doors(ds=d['envelope']['doors'])
        )
        result = [d_lv3.get_as_dict() for d_lv3 in ds_lv3]

        self.assertEqual(3, len(result))
        self.assertEqual('test_part_main_occupant_room', result[0]['name'])
        self.assertEqual('test_part_other_occupant_room', result[1]['name'])
        self.assertEqual('test_part_non_occupant_room', result[2]['name'])
        self.assertEqual('outdoor', result[0]['next_space'])
        self.assertEqual('outdoor', result[1]['next_space'])
        self.assertEqual('outdoor', result[2]['next_space'])
        self.assertEqual('top', result[0]['direction'])
        self.assertEqual('top', result[1]['direction'])
        self.assertEqual('top', result[2]['direction'])
        self.assertEqual(2.52 * 30.0 / 120.0, result[0]['area'])
        self.assertEqual(2.52 * 60.0 / 120.0, result[1]['area'])
        self.assertEqual(2.52 * 30.0 / 120.0, result[2]['area'])
        self.assertEqual(2.0, result[0]['spec']['u_value'])
        self.assertEqual(2.0, result[1]['spec']['u_value'])
        self.assertEqual(2.0, result[2]['spec']['u_value'])

    def test_get_heatbridges(self):

        d = {
            'common': {
                'region': 6,
                'main_occupant_room_floor_area': 30.0,
                'other_occupant_room_floor_area': 60.0,
                'total_floor_area': 120.0,
            },
            'envelope': {
                'heatbridges': [
                    {
                        'name': 'test_part',
                        'next_spaces': ['outdoor'],
                        'directions': ['top'],
                        'length': 2.0,
                        'space_type': 'undefine',
                        'spec': {
                            'psi_value': 1.5
                        },
                    }
                ]
            }
        }

        hbs_lv3 = t.get_heatbridges_lv3(
            a_f_mr=d['common']['main_occupant_room_floor_area'],
            a_f_or=d['common']['other_occupant_room_floor_area'],
            a_f_total=d['common']['total_floor_area'],
            hbs=ees_house.Heatbridge.make_heatbridges(ds=d['envelope']['heatbridges'])
        )

        result = [hb_lv3.get_as_dict() for hb_lv3 in hbs_lv3]

        self.assertEqual(3, len(result))
        self.assertEqual('test_part_main_occupant_room', result[0]['name'])
        self.assertEqual('test_part_other_occupant_room', result[1]['name'])
        self.assertEqual('test_part_non_occupant_room', result[2]['name'])
        self.assertEqual('outdoor', result[0]['next_spaces'][0])
        self.assertEqual('outdoor', result[1]['next_spaces'][0])
        self.assertEqual('outdoor', result[2]['next_spaces'][0])
        self.assertEqual('top', result[0]['directions'][0])
        self.assertEqual('top', result[1]['directions'][0])
        self.assertEqual('top', result[2]['directions'][0])
        self.assertEqual(2.0 * 30.0 / 120.0, result[0]['length'])
        self.assertEqual(2.0 * 60.0 / 120.0, result[1]['length'])
        self.assertEqual(2.0 * 30.0 / 120.0, result[2]['length'])
        self.assertEqual(1.5, result[0]['spec']['psi_value'])
        self.assertEqual(1.5, result[1]['spec']['psi_value'])
        self.assertEqual(1.5, result[2]['spec']['psi_value'])

    def test_get_earthfloor_perimeters(self):

        d = {
            'common': {
                'region': 6,
                'main_occupant_room_floor_area': 30.0,
                'other_occupant_room_floor_area': 60.0,
                'total_floor_area': 120.0,
            },
            'envelope': {
                'earthfloor_perimeters': [
                    {
                        'name': 'test_part',
                        'next_space': 'outdoor',
                        'length': 2.0,
                        'space_type': 'undefined',
                        'spec': {
                            'psi_value': 1.5
                        },
                    }
                ]
            }
        }

        eps_lv3 = t.get_earthfloor_perimeters_lv3(
            eps=ees_house.EarthfloorPerimeter.make_earthfloor_perimeters(ds=d['envelope']['earthfloor_perimeters'])
        )
        result = [ep_lv3.get_as_dict() for ep_lv3 in eps_lv3]

        self.assertEqual(1, len(result))
        self.assertEqual('test_part', result[0]['name'])
        self.assertEqual('outdoor', result[0]['next_space'])
        self.assertEqual(2.0, result[0]['length'])
        self.assertEqual(1.5, result[0]['spec']['psi_value'])

    def test_get_earthfloor_centers(self):

        d = {
            'common': {
                'region': 6,
                'main_occupant_room_floor_area': 30.0,
                'other_occupant_room_floor_area': 60.0,
                'total_floor_area': 120.0,
            },
            'envelope': {
                'earthfloor_centers': [
                    {
                        'name': 'test_part',
                        'area': 45.0,
                        'space_type': 'undefined',
                        'spec': {
                            'layers': []
                        }
                    }
                ]
            }
        }

        ecs_lv3 = t.get_earthfloor_centers_lv3(
            ecs=ees_house.EarthfloorCenter.make_earthfloor_centers(ds=d['envelope']['earthfloor_centers'])
        )

        result = [ec_lv3.get_as_dict() for ec_lv3 in ecs_lv3]

        self.assertEqual(1, len(result))
        self.assertEqual('test_part', result[0]['name'])
        self.assertEqual(45.0, result[0]['area'])

    def test_convert_spec(self):

        d = {
            'common': {
                'region': 6,
                'main_occupant_room_floor_area': 30.0,
                'other_occupant_room_floor_area': 60.0,
                'total_floor_area': 120.0
            },
            'envelope': {
                'general_parts': [
                    {
                        'name': 'test_part1',
                        'general_part_type': 'ceiling',
                        'next_space': 'outdoor',
                        'direction': 'top',
                        'area': 67.8,
                        'space_type': 'undefined',
                        'sunshade': {
                            'is_defined': False
                        },
                        'spec': {
                            'structure': 'other',
                            'u_value_other': 1.2
                        },
                    },
                    {
                        'name': 'test_part2',
                        'general_part_type': 'ceiling',
                        'next_space': 'outdoor',
                        'direction': 'top',
                        'area': 67.8,
                        'space_type': 'undefined',
                        'sunshade': {
                            'is_defined': False
                        },
                        'spec': {
                            'structure': 'other',
                            'u_value_other': 1.2
                        },
                    }
                ],
                'windows': [
                    {
                        'name': 'test_part1',
                        'next_space': 'outdoor',
                        'direction': 'sw',
                        'area': 30.25,
                        'space_type': 'undefined',
                        'sunshade': {
                            'is_defined': True,
                            'input': 'not_input'
                        },
                        'spec': {
                            'window_type': 'single',
                            'windows': [
                                {
                                    'u_value_input_method': 'u_value_directly',
                                    'u_value': 3.0,
                                    'eta_value_input_method': 'eta_d_value_directly',
                                    'eta_d_h_value': 0.5,
                                    'eta_d_c_value': 0.5,
                                    'glass_type': 'single'
                                }
                            ],
                            'attachment_type': 'none',
                            'is_windbreak_room_attached': False
                        },
                    },
                    {
                        'name': 'test_part2',
                        'next_space': 'outdoor',
                        'direction': 'sw',
                        'area': 30.25,
                        'space_type': 'undefined',
                        'sunshade': {
                            'is_defined': True,
                            'input': 'not_input'
                        },
                        'spec': {
                            'window_type': 'single',
                            'windows': [
                                {
                                    'u_value_input_method': 'u_value_directly',
                                    'u_value': 3.0,
                                    'eta_value_input_method': 'eta_d_value_directly',
                                    'eta_d_h_value': 0.5,
                                    'eta_d_c_value': 0.5,
                                    'glass_type': 'single'
                                }
                            ],
                            'attachment_type': 'none',
                            'is_windbreak_room_attached': False
                        },
                    }
                ],
                'doors': [
                    {
                        'name': 'test_part1',
                        'next_space': 'outdoor',
                        'direction': 'nw',
                        'area': 2.52,
                        'space_type': 'undefined',
                        'sunshade': {
                            'is_defined': False
                        },
                        'spec': {
                            'u_value': 2.0
                        },
                    },
                    {
                        'name': 'test_part2',
                        'next_space': 'outdoor',
                        'direction': 'nw',
                        'area': 2.52,
                        'space_type': 'undefined',
                        'sunshade': {
                            'is_defined': False
                        },
                        'spec': {
                            'u_value': 2.0
                        },
                    },
                ],
                'heat_bridges': [
                    {
                        'name': 'test_part1',
                        'next_spaces': ['outdoor', 'outdoor'],
                        'directions': ['s', 'w'],
                        'length': 2.0,
                        'space_type': 'undefined',
                        'spec': {
                            'psi_value': 0.7
                        },
                    },
                    {
                        'name': 'test_part2',
                        'next_spaces': ['outdoor', 'outdoor'],
                        'directions': ['s', 'w'],
                        'length': 2.0,
                        'space_type': 'undefined',
                        'spec': {
                            'psi_value': 0.7
                        },
                    }
                ],
                'earthfloor_perimeters': [
                    {
                        'name': 'test_part1',
                        'next_space': 'outdoor',
                        'length': 2.43,
                        'space_type': 'undefined',
                        'spec': {
                            'psi_value': 1.5
                        },
                    },
                    {
                        'name': 'test_part2',
                        'next_space': 'outdoor',
                        'length': 2.43,
                        'space_type': 'undefined',
                        'spec': {
                            'psi_value': 1.5
                        },
                    }
                ],
                'earthfloor_centers': [
                    {
                        'name': 'test_part1',
                        'area': 45.0,
                        'space_type': 'undefined',
                        'spec': {
                            'layers': []
                        }
                    }
                ]
            }
        }

        tgt = t.convert_spec(common=d['common'], envelope=d['envelope'])

        self.assertEqual(tgt['input_method'], 'detail_with_room_usage')

        gp = tgt['general_parts'][0]
        self.assertEqual('test_part1_main_occupant_room', gp['name'])
        self.assertEqual('ceiling', gp['general_part_type'])
        self.assertEqual('outdoor', gp['next_space'])
        self.assertEqual('top', gp['direction'])
        self.assertEqual(16.95, gp['area'])
        self.assertEqual('other', gp['spec']['structure'])

        gp = tgt['general_parts'][1]
        self.assertEqual('test_part1_other_occupant_room', gp['name'])
        self.assertEqual('ceiling', gp['general_part_type'])
        self.assertEqual('outdoor', gp['next_space'])
        self.assertEqual('top', gp['direction'])
        self.assertEqual(33.9, gp['area'])
        self.assertEqual('other', gp['spec']['structure'])

        gp = tgt['general_parts'][2]
        self.assertEqual('test_part1_non_occupant_room', gp['name'])
        self.assertEqual('ceiling', gp['general_part_type'])
        self.assertEqual('outdoor', gp['next_space'])
        self.assertEqual('top', gp['direction'])
        self.assertEqual(16.95, gp['area'])
        self.assertEqual('other', gp['spec']['structure'])

        gp = tgt['general_parts'][3]
        self.assertEqual('test_part2_main_occupant_room', gp['name'])
        self.assertEqual('ceiling', gp['general_part_type'])
        self.assertEqual('outdoor', gp['next_space'])
        self.assertEqual('top', gp['direction'])
        self.assertEqual(16.95, gp['area'])
        self.assertEqual('other', gp['spec']['structure'])

        gp = tgt['general_parts'][4]
        self.assertEqual('test_part2_other_occupant_room', gp['name'])
        self.assertEqual('ceiling', gp['general_part_type'])
        self.assertEqual('outdoor', gp['next_space'])
        self.assertEqual('top', gp['direction'])
        self.assertEqual(33.9, gp['area'])
        self.assertEqual('other', gp['spec']['structure'])

        gp = tgt['general_parts'][5]
        self.assertEqual('test_part2_non_occupant_room', gp['name'])
        self.assertEqual('ceiling', gp['general_part_type'])
        self.assertEqual('outdoor', gp['next_space'])
        self.assertEqual('top', gp['direction'])
        self.assertEqual(16.95, gp['area'])
        self.assertEqual('other', gp['spec']['structure'])

        w = tgt['windows'][0]
        self.assertEqual('test_part1_main_occupant_room', w['name'])
        self.assertEqual('outdoor', w['next_space'])
        self.assertEqual('sw', w['direction'])
        self.assertEqual(7.5625, w['area'])
        self.assertEqual('main_occupant_room', w['space_type'])
        self.assertEqual('single', w['spec']['window_type'])

        w = tgt['windows'][1]
        self.assertEqual('test_part1_other_occupant_room', w['name'])
        self.assertEqual('outdoor', w['next_space'])
        self.assertEqual('sw', w['direction'])
        self.assertEqual(15.125, w['area'])
        self.assertEqual('other_occupant_room', w['space_type'])
        self.assertEqual('single', w['spec']['window_type'])

        w = tgt['windows'][2]
        self.assertEqual('test_part1_non_occupant_room', w['name'])
        self.assertEqual('outdoor', w['next_space'])
        self.assertEqual('sw', w['direction'])
        self.assertEqual(7.5625, w['area'])
        self.assertEqual('non_occupant_room', w['space_type'])
        self.assertEqual('single', w['spec']['window_type'])

        w = tgt['windows'][3]
        self.assertEqual('test_part2_main_occupant_room', w['name'])
        self.assertEqual('outdoor', w['next_space'])
        self.assertEqual('sw', w['direction'])
        self.assertEqual(7.5625, w['area'])
        self.assertEqual('main_occupant_room', w['space_type'])
        self.assertEqual('single', w['spec']['window_type'])

        w = tgt['windows'][4]
        self.assertEqual('test_part2_other_occupant_room', w['name'])
        self.assertEqual('outdoor', w['next_space'])
        self.assertEqual('sw', w['direction'])
        self.assertEqual(15.125, w['area'])
        self.assertEqual('other_occupant_room', w['space_type'])
        self.assertEqual('single', w['spec']['window_type'])

        w = tgt['windows'][5]
        self.assertEqual('test_part2_non_occupant_room', w['name'])
        self.assertEqual('outdoor', w['next_space'])
        self.assertEqual('sw', w['direction'])
        self.assertEqual(7.5625, w['area'])
        self.assertEqual('non_occupant_room', w['space_type'])
        self.assertEqual('single', w['spec']['window_type'])

        d = tgt['doors'][0]
        self.assertEqual('test_part1_main_occupant_room', d['name'])
        self.assertEqual('outdoor', d['next_space'])
        self.assertEqual('nw', d['direction'])
        self.assertEqual(0.63, d['area'])
        self.assertEqual('main_occupant_room', d['space_type'])
        self.assertEqual(2.0, d['spec']['u_value'])

        d = tgt['doors'][1]
        self.assertEqual('test_part1_other_occupant_room', d['name'])
        self.assertEqual('outdoor', d['next_space'])
        self.assertEqual('nw', d['direction'])
        self.assertEqual(1.26, d['area'])
        self.assertEqual('other_occupant_room', d['space_type'])
        self.assertEqual(2.0, d['spec']['u_value'])

        d = tgt['doors'][2]
        self.assertEqual('test_part1_non_occupant_room', d['name'])
        self.assertEqual('outdoor', d['next_space'])
        self.assertEqual('nw', d['direction'])
        self.assertEqual(0.63, d['area'])
        self.assertEqual('non_occupant_room', d['space_type'])
        self.assertEqual(2.0, d['spec']['u_value'])

        d = tgt['doors'][3]
        self.assertEqual('test_part2_main_occupant_room', d['name'])
        self.assertEqual('outdoor', d['next_space'])
        self.assertEqual('nw', d['direction'])
        self.assertEqual(0.63, d['area'])
        self.assertEqual('main_occupant_room', d['space_type'])
        self.assertEqual(2.0, d['spec']['u_value'])

        d = tgt['doors'][4]
        self.assertEqual('test_part2_other_occupant_room', d['name'])
        self.assertEqual('outdoor', d['next_space'])
        self.assertEqual('nw', d['direction'])
        self.assertEqual(1.26, d['area'])
        self.assertEqual('other_occupant_room', d['space_type'])
        self.assertEqual(2.0, d['spec']['u_value'])

        d = tgt['doors'][5]
        self.assertEqual('test_part2_non_occupant_room', d['name'])
        self.assertEqual('outdoor', d['next_space'])
        self.assertEqual('nw', d['direction'])
        self.assertEqual(0.63, d['area'])
        self.assertEqual('non_occupant_room', d['space_type'])
        self.assertEqual(2.0, d['spec']['u_value'])

        h = tgt['heat_bridges'][0]
        self.assertEqual('test_part1_main_occupant_room', h['name'])
        self.assertEqual(['outdoor', 'outdoor'], h['next_spaces'])
        self.assertEqual(['s', 'w'], h['directions'])
        self.assertEqual('main_occupant_room', h['space_type'])
        self.assertEqual(0.5, h['length'])
        self.assertEqual(0.7, h['spec']['psi_value'])

        h = tgt['heat_bridges'][1]
        self.assertEqual('test_part1_other_occupant_room', h['name'])
        self.assertEqual(['outdoor', 'outdoor'], h['next_spaces'])
        self.assertEqual(['s', 'w'], h['directions'])
        self.assertEqual('other_occupant_room', h['space_type'])
        self.assertEqual(1.0, h['length'])
        self.assertEqual(0.7, h['spec']['psi_value'])

        h = tgt['heat_bridges'][2]
        self.assertEqual('test_part1_non_occupant_room', h['name'])
        self.assertEqual(['outdoor', 'outdoor'], h['next_spaces'])
        self.assertEqual(['s', 'w'], h['directions'])
        self.assertEqual('non_occupant_room', h['space_type'])
        self.assertEqual(0.5, h['length'])
        self.assertEqual(0.7, h['spec']['psi_value'])

        h = tgt['heat_bridges'][3]
        self.assertEqual('test_part2_main_occupant_room', h['name'])
        self.assertEqual(['outdoor', 'outdoor'], h['next_spaces'])
        self.assertEqual(['s', 'w'], h['directions'])
        self.assertEqual('main_occupant_room', h['space_type'])
        self.assertEqual(0.5, h['length'])
        self.assertEqual(0.7, h['spec']['psi_value'])

        h = tgt['heat_bridges'][4]
        self.assertEqual('test_part2_other_occupant_room', h['name'])
        self.assertEqual(['outdoor', 'outdoor'], h['next_spaces'])
        self.assertEqual(['s', 'w'], h['directions'])
        self.assertEqual('other_occupant_room', h['space_type'])
        self.assertEqual(1.0, h['length'])
        self.assertEqual(0.7, h['spec']['psi_value'])

        h = tgt['heat_bridges'][5]
        self.assertEqual('test_part2_non_occupant_room', h['name'])
        self.assertEqual(['outdoor', 'outdoor'], h['next_spaces'])
        self.assertEqual(['s', 'w'], h['directions'])
        self.assertEqual('non_occupant_room', h['space_type'])
        self.assertEqual(0.5, h['length'])
        self.assertEqual(0.7, h['spec']['psi_value'])

        efp = tgt['earthfloor_perimeters'][0]
        self.assertEqual('test_part1', efp['name'])
        self.assertEqual('outdoor', efp['next_space'])
        self.assertEqual(2.43, efp['length'])
        self.assertEqual('underfloor', efp['space_type'])
        self.assertEqual(1.5, efp['spec']['psi_value'])

        efp = tgt['earthfloor_perimeters'][1]
        self.assertEqual('test_part2', efp['name'])
        self.assertEqual('outdoor', efp['next_space'])
        self.assertEqual(2.43, efp['length'])
        self.assertEqual('underfloor', efp['space_type'])
        self.assertEqual(1.5, efp['spec']['psi_value'])

        ec = tgt['earthfloor_centers'][0]
        self.assertEqual('test_part1', ec['name'])
        self.assertEqual(45.0, ec['area'])
        self.assertEqual('underfloor', ec['space_type'])


if __name__ == '__main__':
    unittest.main()
