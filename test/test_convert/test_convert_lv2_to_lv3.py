import unittest

import heat_load_calc.convert.convert_lv2_to_lv3 as t


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
                        'spec': 'something',
                    }
                ]
            }
        }

        result = t.get_general_parts(
            a_f_mr=d['common']['main_occupant_room_floor_area'],
            a_f_or=d['common']['other_occupant_room_floor_area'],
            a_f_total=d['common']['total_floor_area'],
            general_parts=d['envelope']['general_parts']
        )

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
        self.assertEqual('something', result[0]['spec'])
        self.assertEqual('something', result[1]['spec'])
        self.assertEqual('something', result[2]['spec'])

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
                        'spec': 'something',
                    }
                ]
            }
        }

        result = t.get_windows(
            a_f_mr=d['common']['main_occupant_room_floor_area'],
            a_f_or=d['common']['other_occupant_room_floor_area'],
            a_f_total=d['common']['total_floor_area'],
            windows=d['envelope']['windows']
        )

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
        self.assertEqual('something', result[0]['spec'])
        self.assertEqual('something', result[1]['spec'])
        self.assertEqual('something', result[2]['spec'])

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
                        'spec': 'something',
                    }
                ]
            }
        }

        result = t.get_doors(
            a_f_mr=d['common']['main_occupant_room_floor_area'],
            a_f_or=d['common']['other_occupant_room_floor_area'],
            a_f_total=d['common']['total_floor_area'],
            doors=d['envelope']['doors']
        )

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
        self.assertEqual('something', result[0]['spec'])
        self.assertEqual('something', result[1]['spec'])
        self.assertEqual('something', result[2]['spec'])

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
                        'next_space': 'outdoor',
                        'direction': 'top',
                        'length': 2.0,
                        'spec': 'something',
                    }
                ]
            }
        }

        result = t.get_heatbridges(
            a_f_mr=d['common']['main_occupant_room_floor_area'],
            a_f_or=d['common']['other_occupant_room_floor_area'],
            a_f_total=d['common']['total_floor_area'],
            heatbridges=d['envelope']['heatbridges']
        )

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
        self.assertEqual(2.0 * 30.0 / 120.0, result[0]['length'])
        self.assertEqual(2.0 * 60.0 / 120.0, result[1]['length'])
        self.assertEqual(2.0 * 30.0 / 120.0, result[2]['length'])
        self.assertEqual('something', result[0]['spec'])
        self.assertEqual('something', result[1]['spec'])
        self.assertEqual('something', result[2]['spec'])

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
                        'direction': 'top',
                        'length': 2.0,
                        'spec': 'something',
                    }
                ]
            }
        }

        result = t.get_earthfloor_perimeters(d['envelope']['earthfloor_perimeters'])

        self.assertEqual(1, len(result))
        self.assertEqual('test_part', result[0]['name'])
        self.assertEqual('outdoor', result[0]['next_space'])
        self.assertEqual('top', result[0]['direction'])
        self.assertEqual(2.0, result[0]['length'])
        self.assertEqual('something', result[0]['spec'])

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
                    }
                ]
            }
        }

        result = t.get_earthfloor_centers(d['envelope']['earthfloor_centers'])

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
                        'spec': 'something',
                    },
                    {
                        'name': 'test_part2',
                        'general_part_type': 'ceiling',
                        'next_space': 'outdoor',
                        'direction': 'top',
                        'area': 67.8,
                        'spec': 'something',
                    }
                ],
                'windows': [
                    {
                        'name': 'test_part1',
                        'next_space': 'outdoor',
                        'direction': 'sw',
                        'area': 30.25,
                        'spec': 'something',
                    },
                    {
                        'name': 'test_part2',
                        'next_space': 'outdoor',
                        'direction': 'sw',
                        'area': 30.25,
                        'spec': 'something',
                    }
                ],
                'doors': [
                    {
                        'name': 'test_part1',
                        'next_space': 'outdoor',
                        'direction': 'nw',
                        'area': 2.52,
                        'spec': 'something',
                    },
                    {
                        'name': 'test_part2',
                        'next_space': 'outdoor',
                        'direction': 'nw',
                        'area': 2.52,
                        'spec': 'something',
                    },
                ],
                'heatbridges': [
                    {
                        'name': 'test_part1',
                        'next_space': ['outdoor', 'outdoor'],
                        'direction': ['s', 'w'],
                        'length': 2.0,
                        'spec': 'something',
                    },
                    {
                        'name': 'test_part2',
                        'next_space': ['outdoor', 'outdoor'],
                        'direction': ['s', 'w'],
                        'length': 2.0,
                        'spec': 'something',
                    }
                ],
                'earthfloor_perimeters': [
                    {
                        'name': 'test_part1',
                        'next_space': 'outdoor',
                        'direction': 'ne',
                        'length': 2.43,
                        'spec': 'something',
                    },
                    {
                        'name': 'test_part2',
                        'next_space': 'outdoor',
                        'direction': 'ne',
                        'length': 2.43,
                        'spec': 'something',
                    }
                ],
                'earthfloor_centers': [
                    {
                        'name': 'test_part1',
                        'area': 45.0,
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
        self.assertEqual('something', gp['spec'])

        gp = tgt['general_parts'][1]
        self.assertEqual('test_part1_other_occupant_room', gp['name'])
        self.assertEqual('ceiling', gp['general_part_type'])
        self.assertEqual('outdoor', gp['next_space'])
        self.assertEqual('top', gp['direction'])
        self.assertEqual(33.9, gp['area'])
        self.assertEqual('something', gp['spec'])

        gp = tgt['general_parts'][2]
        self.assertEqual('test_part1_non_occupant_room', gp['name'])
        self.assertEqual('ceiling', gp['general_part_type'])
        self.assertEqual('outdoor', gp['next_space'])
        self.assertEqual('top', gp['direction'])
        self.assertEqual(16.95, gp['area'])
        self.assertEqual('something', gp['spec'])

        gp = tgt['general_parts'][3]
        self.assertEqual('test_part2_main_occupant_room', gp['name'])
        self.assertEqual('ceiling', gp['general_part_type'])
        self.assertEqual('outdoor', gp['next_space'])
        self.assertEqual('top', gp['direction'])
        self.assertEqual(16.95, gp['area'])
        self.assertEqual('something', gp['spec'])

        gp = tgt['general_parts'][4]
        self.assertEqual('test_part2_other_occupant_room', gp['name'])
        self.assertEqual('ceiling', gp['general_part_type'])
        self.assertEqual('outdoor', gp['next_space'])
        self.assertEqual('top', gp['direction'])
        self.assertEqual(33.9, gp['area'])
        self.assertEqual('something', gp['spec'])

        gp = tgt['general_parts'][5]
        self.assertEqual('test_part2_non_occupant_room', gp['name'])
        self.assertEqual('ceiling', gp['general_part_type'])
        self.assertEqual('outdoor', gp['next_space'])
        self.assertEqual('top', gp['direction'])
        self.assertEqual(16.95, gp['area'])
        self.assertEqual('something', gp['spec'])

        w = tgt['windows'][0]
        self.assertEqual('test_part1_main_occupant_room', w['name'])
        self.assertEqual('outdoor', w['next_space'])
        self.assertEqual('sw', w['direction'])
        self.assertEqual(7.5625, w['area'])
        self.assertEqual('main_occupant_room', w['space_type'])
        self.assertEqual('something', w['spec'])

        w = tgt['windows'][1]
        self.assertEqual('test_part1_other_occupant_room', w['name'])
        self.assertEqual('outdoor', w['next_space'])
        self.assertEqual('sw', w['direction'])
        self.assertEqual(15.125, w['area'])
        self.assertEqual('other_occupant_room', w['space_type'])
        self.assertEqual('something', w['spec'])

        w = tgt['windows'][2]
        self.assertEqual('test_part1_non_occupant_room', w['name'])
        self.assertEqual('outdoor', w['next_space'])
        self.assertEqual('sw', w['direction'])
        self.assertEqual(7.5625, w['area'])
        self.assertEqual('non_occupant_room', w['space_type'])
        self.assertEqual('something', w['spec'])

        w = tgt['windows'][3]
        self.assertEqual('test_part2_main_occupant_room', w['name'])
        self.assertEqual('outdoor', w['next_space'])
        self.assertEqual('sw', w['direction'])
        self.assertEqual(7.5625, w['area'])
        self.assertEqual('main_occupant_room', w['space_type'])
        self.assertEqual('something', w['spec'])

        w = tgt['windows'][4]
        self.assertEqual('test_part2_other_occupant_room', w['name'])
        self.assertEqual('outdoor', w['next_space'])
        self.assertEqual('sw', w['direction'])
        self.assertEqual(15.125, w['area'])
        self.assertEqual('other_occupant_room', w['space_type'])
        self.assertEqual('something', w['spec'])

        w = tgt['windows'][5]
        self.assertEqual('test_part2_non_occupant_room', w['name'])
        self.assertEqual('outdoor', w['next_space'])
        self.assertEqual('sw', w['direction'])
        self.assertEqual(7.5625, w['area'])
        self.assertEqual('non_occupant_room', w['space_type'])
        self.assertEqual('something', w['spec'])

        d = tgt['doors'][0]
        self.assertEqual('test_part1_main_occupant_room', d['name'])
        self.assertEqual('outdoor', d['next_space'])
        self.assertEqual('nw', d['direction'])
        self.assertEqual(0.63, d['area'])
        self.assertEqual('main_occupant_room', d['space_type'])
        self.assertEqual('something', d['spec'])

        d = tgt['doors'][1]
        self.assertEqual('test_part1_other_occupant_room', d['name'])
        self.assertEqual('outdoor', d['next_space'])
        self.assertEqual('nw', d['direction'])
        self.assertEqual(1.26, d['area'])
        self.assertEqual('other_occupant_room', d['space_type'])
        self.assertEqual('something', d['spec'])

        d = tgt['doors'][2]
        self.assertEqual('test_part1_non_occupant_room', d['name'])
        self.assertEqual('outdoor', d['next_space'])
        self.assertEqual('nw', d['direction'])
        self.assertEqual(0.63, d['area'])
        self.assertEqual('non_occupant_room', d['space_type'])
        self.assertEqual('something', d['spec'])

        d = tgt['doors'][3]
        self.assertEqual('test_part2_main_occupant_room', d['name'])
        self.assertEqual('outdoor', d['next_space'])
        self.assertEqual('nw', d['direction'])
        self.assertEqual(0.63, d['area'])
        self.assertEqual('main_occupant_room', d['space_type'])
        self.assertEqual('something', d['spec'])

        d = tgt['doors'][4]
        self.assertEqual('test_part2_other_occupant_room', d['name'])
        self.assertEqual('outdoor', d['next_space'])
        self.assertEqual('nw', d['direction'])
        self.assertEqual(1.26, d['area'])
        self.assertEqual('other_occupant_room', d['space_type'])
        self.assertEqual('something', d['spec'])

        d = tgt['doors'][5]
        self.assertEqual('test_part2_non_occupant_room', d['name'])
        self.assertEqual('outdoor', d['next_space'])
        self.assertEqual('nw', d['direction'])
        self.assertEqual(0.63, d['area'])
        self.assertEqual('non_occupant_room', d['space_type'])
        self.assertEqual('something', d['spec'])

        h = tgt['heatbridges'][0]
        self.assertEqual('test_part1_main_occupant_room', h['name'])
        self.assertEqual(['outdoor', 'outdoor'], h['next_space'])
        self.assertEqual(['s', 'w'], h['direction'])
        self.assertEqual('main_occupant_room', h['space_type'])
        self.assertEqual(0.5, h['length'])
        self.assertEqual('something', h['spec'])

        h = tgt['heatbridges'][1]
        self.assertEqual('test_part1_other_occupant_room', h['name'])
        self.assertEqual(['outdoor', 'outdoor'], h['next_space'])
        self.assertEqual(['s', 'w'], h['direction'])
        self.assertEqual('other_occupant_room', h['space_type'])
        self.assertEqual(1.0, h['length'])
        self.assertEqual('something', h['spec'])

        h = tgt['heatbridges'][2]
        self.assertEqual('test_part1_non_occupant_room', h['name'])
        self.assertEqual(['outdoor', 'outdoor'], h['next_space'])
        self.assertEqual(['s', 'w'], h['direction'])
        self.assertEqual('non_occupant_room', h['space_type'])
        self.assertEqual(0.5, h['length'])
        self.assertEqual('something', h['spec'])

        h = tgt['heatbridges'][3]
        self.assertEqual('test_part2_main_occupant_room', h['name'])
        self.assertEqual(['outdoor', 'outdoor'], h['next_space'])
        self.assertEqual(['s', 'w'], h['direction'])
        self.assertEqual('main_occupant_room', h['space_type'])
        self.assertEqual(0.5, h['length'])
        self.assertEqual('something', h['spec'])

        h = tgt['heatbridges'][4]
        self.assertEqual('test_part2_other_occupant_room', h['name'])
        self.assertEqual(['outdoor', 'outdoor'], h['next_space'])
        self.assertEqual(['s', 'w'], h['direction'])
        self.assertEqual('other_occupant_room', h['space_type'])
        self.assertEqual(1.0, h['length'])
        self.assertEqual('something', h['spec'])

        h = tgt['heatbridges'][5]
        self.assertEqual('test_part2_non_occupant_room', h['name'])
        self.assertEqual(['outdoor', 'outdoor'], h['next_space'])
        self.assertEqual(['s', 'w'], h['direction'])
        self.assertEqual('non_occupant_room', h['space_type'])
        self.assertEqual(0.5, h['length'])
        self.assertEqual('something', h['spec'])

        efp = tgt['earthfloor_perimeters'][0]
        self.assertEqual('test_part1', efp['name'])
        self.assertEqual('outdoor', efp['next_space'])
        self.assertEqual('ne', efp['direction'])
        self.assertEqual(2.43, efp['length'])
        self.assertEqual('underfloor', efp['space_type'])
        self.assertEqual('something', efp['spec'])

        efp = tgt['earthfloor_perimeters'][1]
        self.assertEqual('test_part2', efp['name'])
        self.assertEqual('outdoor', efp['next_space'])
        self.assertEqual('ne', efp['direction'])
        self.assertEqual(2.43, efp['length'])
        self.assertEqual('underfloor', efp['space_type'])
        self.assertEqual('something', efp['spec'])

        ec = tgt['earthfloor_centers'][0]
        self.assertEqual('test_part1', ec['name'])
        self.assertEqual(45.0, ec['area'])
        self.assertEqual('underfloor', ec['space_type'])


if __name__ == '__main__':
    unittest.main()
