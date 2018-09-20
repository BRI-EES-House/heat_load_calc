import matplotlib
from matplotlib.testing.decorators import image_comparison
import math
import unittest
import nbimporter
import LV2toLV3 as nb

class TestLV2toLV3(unittest.TestCase):

    def test_get_area_rate(self):
        a, b, c = nb.get_area_rate(20, 50, 100)
        self.assertEqual(0.2, a)
        self.assertEqual(0.5, b)
        self.assertEqual(0.3, c)

    def test_get_area_by_room_use(self):
        adic = nb.get_area_by_room_use(75, 20, 50, 100)
        self.assertEqual(75 * 0.2, adic['main'])
        self.assertEqual(75 * 0.5, adic['other'])
        self.assertEqual(75 * 0.3, adic['nonliving'])

    def test_get_length_by_room_use(self):
        ldic = nb.get_area_by_room_use(5, 20, 50, 100)
        self.assertEqual(5 * 0.2, ldic['main'])
        self.assertEqual(5 * 0.5, ldic['other'])
        self.assertEqual(5 * 0.3, ldic['nonliving'])

    def test_convert_common(self):
        d = {
            'Common': {
                'Region' : 6,
                'IsSimplifiedInput': True,
                'MainOccupantRoomFloorArea': 30.0,
                'OtherOccupantRoomFloorArea': 60.0,
                'TotalFloorArea': 120.0
            }
        }
        ret = nb.convert_common(d)
        self.assertEqual(6, ret['Region'])
        self.assertEqual(True, ret['IsSimplifiedInput'])
        self.assertEqual(30.0, ret['MainOccupantRoomFloorArea'])
        self.assertEqual(60.0, ret['OtherOccupantRoomFloorArea'])
        self.assertEqual(120.0, ret['TotalFloorArea'])

    def test_make_wall(self):
        ret = nb.make_wall(
            name = 'WAL1',
            direction = 'N',
            area = 20,
            space = 'main'
        )
        self.assertEqual('WAL1_main', ret['name'])
        self.assertEqual('N', ret['direction'])
        self.assertEqual(20, ret['area'])
        self.assertEqual('main', ret['space'])

    def test_convert_wall(self):
        d = {
            'Common': {
                'MainOccupantRoomFloorArea': 30.0,
                'OtherOccupantRoomFloorArea': 60.0,
                'TotalFloorArea': 120.0,
            },
            'Walls': [
                { 'area': 67.8, 'direction': 'top', 'name': 'Ceiling' },
                { 'area': 40.63, 'direction': 'SW', 'name': 'Wall_SW',}
            ]
        }
        ret = nb.convert_wall(d)

        #Wallsに指定した壁が主居室・そのほか居室・非居室に割り付けられる
        # →入力に対して3倍の壁が返ってくる
        self.assertEqual(6, len(ret))

    def test_make_window(self):
        ret = nb.make_window(
            name = 'WND1',
            direction = 'S',
            area = 2,
            space = 'other'
        )
        self.assertEqual('WND1_other', ret['name'])
        self.assertEqual('S', ret['direction'])
        self.assertEqual(2, ret['area'])
        self.assertEqual('other', ret['space'])

    def test_convert_window(self):
        d = {
            'Common': {
                'MainOccupantRoomFloorArea': 30.0,
                'OtherOccupantRoomFloorArea': 60.0,
                'TotalFloorArea': 120.0,
            },
            'Windows': [
                { 'name': 'WindowSW', 'direction': 'SW', 'area': 30.25 },
                { 'name': 'WindowNW', 'direction': 'NW', 'area': 3.17  }
            ]
        }    
        ret = nb.convert_window(d)
        self.assertEqual(6, len(ret))

    def test_make_door(self):
        ret = nb.make_door(
            name = 'DOOR1',
            direction = 'W',
            area = 3,
            space = 'nonliving'
        )
        self.assertEqual('DOOR1_nonliving', ret['name'])
        self.assertEqual('W', ret['direction'])
        self.assertEqual(3, ret['area'])
        self.assertEqual('nonliving', ret['space'])

    def test_convert_door(self):
        d = {
            'Common': {
                'MainOccupantRoomFloorArea': 30.0,
                'OtherOccupantRoomFloorArea': 60.0,
                'TotalFloorArea': 120.0,
            },
            'Doors': [
                { 'name': 'DoorNW', 'direction': 'NW', 'area': 52 }
            ]
        }    
        ret = nb.convert_door(d)
        self.assertEqual(3, len(ret))

    def test_make_heatbridge(self):
        ret = nb.make_heatbridge(
            structure = 'rc',
            direction1 = 'NW',
            direction2 = 'NE',
            length = 10,
            space = 'main'
        )
        self.assertEqual('rc', ret['structure'])
        self.assertEqual('NW', ret['direction1'])
        self.assertEqual('NE', ret['direction2'])
        self.assertEqual(10, ret['length'])
        self.assertEqual('main', ret['space'])

    def test_convert_heatbridge(self):
        d = {
            'Common': {
                'MainOccupantRoomFloorArea': 30.0,
                'OtherOccupantRoomFloorArea': 60.0,
                'TotalFloorArea': 120.0,
            },
            'Heatbridges': [
                { 'structure': 'rc', 'direction1': 'NW', 'direction2': 'NE', 'length': 10 }
            ]
        }    
        ret = nb.convert_heatbridge(d)
        self.assertEqual(3, len(ret))

    def test_make_earthfloorperimeter(self):
        ret = nb.make_earthfloorperimeter(
            direction = 'NW',
            length = 2.43,
            name = 'other_NW',
            psi = 1.8
        )
        self.assertEqual('NW', ret['direction'])
        self.assertEqual(2.43, ret['length'])
        self.assertEqual('other_NW', ret['name'])
        self.assertEqual(1.8, ret['psi'])
        self.assertEqual('underfloor', ret['space'])

    def test_convert_earthfloorperimeter(self):
        d = {
            'EarthfloorPerimeters': [
                { 'direction': 'NW', 'length': 2.43, 'name': 'other_NW', 'psi': 1.8 },
                { 'direction': 'NE', 'length': 2.43, 'name': 'other_NE', 'psi': 1.8 }
            ]
        }    
        ret = nb.convert_earthfloorperimeter(d)
        self.assertEqual(2, len(ret))

    def test_make_earthfloor(self):
        ret = nb.make_earthfloor(
            name = 'other',
            area = 5.0,
        )
        self.assertEqual('other', ret['name'])
        self.assertEqual(5.0, ret['area'])
        self.assertEqual('underfloor', ret['space'])

    def test_convert_earthfloor(self):
        d = {
            'Earthfloors': [
                { 'name': 'other', 'area': 5.0 }
            ]
        }    
        ret = nb.convert_earthfloor(d)
        self.assertEqual(1, len(ret))


    def test_convert(self):
        ## 実行時エラーにならないことを確認 ##
        d = {
            'Common': {
                'Region': 6,
                'MainOccupantRoomFloorArea': 30.0,
                'OtherOccupantRoomFloorArea': 60.0,
                'TotalFloorArea': 120.0
            },
            'Walls': [
                { 'area': 67.8, 'direction': 'top', 'name': 'Ceiling', 'structure': 'wood', 'type': 'ceiling' },
                { 'area': 40.63, 'direction': 'SW', 'name': 'Wall_SW', 'structure': 'wood', 'type': 'wall' },
            ],
            'Windows': [
                { 'area': 30.25, 'direction': 'SW', 'name': 'WindowSW', 'type': 'single' },
                { 'area': 3.17, 'direction': 'NW', 'name': 'WindowNW', 'type': 'single' },
            ],
            'Doors': [
                { 'area': 2.52, 'direction': 'NW', 'name': 'DoorNW'},
                { 'area': 2.16, 'direction': 'NE', 'name': 'DoorNE'}
            ],
            'EarthfloorPerimeters': [
                { 'direction': 'NW', 'length': 2.43, 'name': 'other_NW', 'psi': 1.8 },
                { 'direction': 'NE', 'length': 2.43, 'name': 'other_NE', 'psi': 1.8 }
            ],
            'Earthfloors': [
                { 'area': 5.0, 'name': 'other' },
                { 'area': 5.0, 'name': 'entrance' }
            ]
        }
        nb.convert(d)    
    
if __name__ == '__main__':
    unittest.main()