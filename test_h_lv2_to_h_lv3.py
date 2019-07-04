import unittest
import nbimporter
import h_lv2_to_h_lv3 as nb

class TestLV2toLV3(unittest.TestCase):

    def test_get_separated_areas(self):

        areas = nb.get_separated_areas(75.0, 20.0, 50.0, 100.0)
        self.assertEqual(75.0 * 0.2, areas[0])
        self.assertEqual(75.0 * 0.5, areas[1])
        self.assertEqual(75.0 * 0.3, areas[2])

    def test_get_separated_length(self):

        lengths = nb.get_separated_lengths(5.0, 20.0, 50.0, 100.0)
        self.assertEqual(5.0 * 0.2, lengths[0])
        self.assertEqual(5.0 * 0.5, lengths[1])
        self.assertEqual(5.0 * 0.3, lengths[2])

    def test_get_space_types(self):
        
        space_types = nb.get_space_types()
        self.assertEqual('main_occupant_room', space_types[0])
        self.assertEqual('other_occupant_room', space_types[1])
        self.assertEqual('non_occupant_room', space_types[2])

    def test_get_general_parts(self):
        
        d = {
            'common' : {
                'region' : 6,
                'main_occupant_room_floor_area': 30.0,
                'other_occupant_room_floor_area': 60.0,
                'total_floor_area': 120.0,
            },
            'envelope' : {
                'general_parts' : [
                    {
                        'name' : 'test_part',
                        'general_part_type' : 'wall',
                        'next_space' : 'outdoor',
                        'external_surface_type' : 'outdoor',
                        'direction' : 'top',
                        'area' : 67.8,
                        'spec' : 'something',
                    }
                ]
            }
        }
                        
        result = nb.get_general_parts(d['envelope']['general_parts'], d['common'])
        
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
        self.assertEqual('outdoor', result[0]['external_surface_type'])
        self.assertEqual('outdoor', result[1]['external_surface_type'])
        self.assertEqual('outdoor', result[2]['external_surface_type'])
        self.assertEqual('top', result[0]['direction'])
        self.assertEqual('top', result[1]['direction'])
        self.assertEqual('top', result[2]['direction'])
        self.assertEqual(67.8*30.0/120.0, result[0]['area'])
        self.assertEqual(67.8*60.0/120.0, result[1]['area'])
        self.assertEqual(67.8*30.0/120.0, result[2]['area'])
        self.assertEqual('something', result[0]['spec'])
        self.assertEqual('something', result[1]['spec'])
        self.assertEqual('something', result[2]['spec'])

    def test_get_windows(self):
        
        d = {
            'common' : {
                'region' : 6,
                'main_occupant_room_floor_area': 30.0,
                'other_occupant_room_floor_area': 60.0,
                'total_floor_area': 120.0,
            },
            'envelope' : {
                'windows' : [
                    {
                        'name' : 'test_part',
                        'next_space' : 'outdoor',
                        'direction' : 'top',
                        'area' : 30.25,
                        'spec' : 'something',
                    }
                ]
            }
        }

        result = nb.get_windows(d['envelope']['windows'], d['common'])
        
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
        self.assertEqual(30.25*30.0/120.0, result[0]['area'])
        self.assertEqual(30.25*60.0/120.0, result[1]['area'])
        self.assertEqual(30.25*30.0/120.0, result[2]['area'])
        self.assertEqual('something', result[0]['spec'])
        self.assertEqual('something', result[1]['spec'])
        self.assertEqual('something', result[2]['spec'])

    def test_get_doors(self):
        
        d = {
            'common' : {
                'region' : 6,
                'main_occupant_room_floor_area': 30.0,
                'other_occupant_room_floor_area': 60.0,
                'total_floor_area': 120.0,
            },
            'envelope' : {
                'doors' : [
                    {
                        'name' : 'test_part',
                        'next_space' : 'outdoor',
                        'direction' : 'top',
                        'area' : 2.52,
                        'spec' : 'something',
                    }
                ]
            }
        }
                        
        result = nb.get_doors(d['envelope']['doors'], d['common'])
        
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
        self.assertEqual(2.52*30.0/120.0, result[0]['area'])
        self.assertEqual(2.52*60.0/120.0, result[1]['area'])
        self.assertEqual(2.52*30.0/120.0, result[2]['area'])
        self.assertEqual('something', result[0]['spec'])
        self.assertEqual('something', result[1]['spec'])
        self.assertEqual('something', result[2]['spec'])
        
    def test_get_heatbridges(self):
        
        d = {
            'common' : {
                'region' : 6,
                'main_occupant_room_floor_area': 30.0,
                'other_occupant_room_floor_area': 60.0,
                'total_floor_area': 120.0,
            },
            'envelope' : {
                'heatbridges' : [
                    {
                        'name' : 'test_part',
                        'next_space' : 'outdoor',
                        'direction' : 'top',
                        'length' : 2.0,
                        'spec' : 'something',
                    }
                ]
            }
        }

        result = nb.get_heatbridges(d['envelope']['heatbridges'], d['common'])
        
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
        self.assertEqual(2.0*30.0/120.0, result[0]['length'])
        self.assertEqual(2.0*60.0/120.0, result[1]['length'])
        self.assertEqual(2.0*30.0/120.0, result[2]['length'])
        self.assertEqual('something', result[0]['spec'])
        self.assertEqual('something', result[1]['spec'])
        self.assertEqual('something', result[2]['spec'])
        
    def test_get_earthfloor_perimeters(self):
        
        d = {
            'common' : {
                'region' : 6,
                'main_occupant_room_floor_area': 30.0,
                'other_occupant_room_floor_area': 60.0,
                'total_floor_area': 120.0,
            },
            'envelope' : {
                'earthfloor_perimeters' : [
                    {
                        'name' : 'test_part',
                        'next_space' : 'outdoor',
                        'direction' : 'top',
                        'length' : 2.0,
                        'spec' : 'something',
                    }
                ]
            }
        }
                        
        result = nb.get_earthfloor_perimeters(d['envelope']['earthfloor_perimeters'])
        
        self.assertEqual(1, len(result))
        self.assertEqual('test_part', result[0]['name'])
        self.assertEqual('outdoor', result[0]['next_space'])
        self.assertEqual('top', result[0]['direction'])
        self.assertEqual(2.0, result[0]['length'])
        self.assertEqual('something', result[0]['spec'])

    def test_get_earthfloor_centers(self):
        
        d = {
            'common' : {
                'region' : 6,
                'main_occupant_room_floor_area': 30.0,
                'other_occupant_room_floor_area': 60.0,
                'total_floor_area': 120.0,
            },
            'envelope' : {
                'earthfloor_centers' : [
                    {
                        'name' : 'test_part',
                        'area' : 45.0,
                    }
                ]
            }
        }

        result = nb.get_earthfloor_centers(d['envelope']['earthfloor_centers'])
        
        self.assertEqual(1, len(result))
        self.assertEqual('test_part', result[0]['name'])
        self.assertEqual(45.0, result[0]['area'])

    def test_convert_common(self):
        d = {
            'common': {
                'region' : 6,
                'main_occupant_room_floor_area': 30.0,
                'other_occupant_room_floor_area': 60.0,
                'total_floor_area': 120.0
            },
            'envelope' : {

            }
        }

        result = nb.convert(d)
        self.assertEqual(6, result['common']['region'])
        self.assertEqual(30.0, result['common']['main_occupant_room_floor_area'])
        self.assertEqual(60.0, result['common']['other_occupant_room_floor_area'])
        self.assertEqual(120.0, result['common']['total_floor_area'])

    def test_convert(self):

        ## 実行時エラーにならないことを確認 ##

        d = {
            'common' : {
                'region' : 6,
                'main_occupant_room_floor_area' : 30.0,
                'other_occupant_room_floor_area' : 60.0,
                'total_floor_area': 120.0
            },
            'envelope' : {
                'general_parts': [
                    {
                        'name' : 'test_part1',
                        'general_part_type' : 'ceiling',
                        'next_space' : 'outdoor',
                        'external_surface_type' : 'outdoor',
                        'direction' : 'top',
                        'area': 67.8,
                        'spec' : 'something',
                    },
                    {
                        'name': 'test_part2',
                        'general_part_type': 'ceiling',
                        'next_space' : 'outdoor',
                        'external_surface_type' : 'outdoor',
                        'direction': 'top',
                        'area': 67.8,
                        'spec': 'something',
                    }
                ],
                'windows' : [
                    {
                        'name' : 'test_part1',
                        'next_space' : 'outdoor',
                        'direction' : 'sw',
                        'area' : 30.25,
                        'spec' : 'something',
                    },
                    {
                        'name': 'test_part2',
                        'next_space': 'outdoor',
                        'direction': 'sw',
                        'area': 30.25,
                        'spec': 'something',
                    }
                ],
                'doors' : [
                    {
                        'name': 'test_part1',
                        'next_space' : 'outdoor',
                        'direction': 'nw',
                        'area': 2.52,
                        'spec' : 'something',
                    },
                    {
                        'name': 'test_part2',
                        'next_space' : 'outdoor',
                        'direction': 'nw',
                        'area': 2.52,
                        'spec' : 'something',
                    },
                ],
                'heatbridges' : [
                    {
                        'name' : 'test_part1',
                        'next_space' : {'outdoor'},
                        'direction' : {'s'},
                        'length' : 2.0,
                        'spec' : 'something',
                    },
                    {
                        'name': 'test_part2',
                        'next_space': {'outdoor'},
                        'direction': {'s'},
                        'length': 2.0,
                        'spec' : 'something',
                    }
                ],
                'earthfloor_perimeters' : [
                    {
                        'name' : 'test_part1',
                        'next_space' : 'outdoor',
                        'direction' : 'ne',
                        'length' : 2.43,
                        'spec' : 'something',
                    },
                    {
                        'name': 'test_part1',
                        'next_space' : 'outdoor',
                        'direction': 'ne',
                        'length': 2.43,
                        'spec': 'something',
                    }
                ],
                'earthfloor_centers' : [
                    {
                        'name': 'test_part1',
                        'area' : 45.0,
                    }
                ]
            }
        }

        nb.convert(d)

if __name__ == '__main__':
    unittest.main()