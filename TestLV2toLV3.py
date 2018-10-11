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

    def test_get_spaceareas(self):
        adic = nb.get_spaceareas(75, 20, 50, 100)
        self.assertEqual(75 * 0.2, adic['main'])
        self.assertEqual(75 * 0.5, adic['other'])
        self.assertEqual(75 * 0.3, adic['nonliving'])

    def test_get_spacelengths(self):
        ldic = nb.get_spacelengths(5, 20, 50, 100)
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

    # 層の作成
    def test_make_layer(self):
        ret = nb.make_layer(
            name = 'wood',
            thick = 0.012,
            cond = 0.16,
            specH = 720
        )
        self.assertEqual('wood', ret['name'])
        self.assertEqual(0.012, ret['thick'])
        self.assertEqual(0.16, ret['cond'])
        self.assertEqual(720, ret['specH'])

    # 層構成の作成
    def test_make_layers(self):
        d = [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
             {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]
        ret = nb.make_layers(d)
        self.assertEqual('wood', ret['name'])
        self.assertEqual(0.012, ret['thick'])
        self.assertEqual(0.16, ret['cond'])
        self.assertEqual(720, ret['specH'])

    # 簡易入力
    def test_make_wall_simple(self):
        ret = nb.make_wall(
            IsSimplifiedInput = True,
            name = 'WAL1',
            direction = 'N',
            spacename = 'main',
            spacearea = 20,
            type = 'MyType',
            structure = 'MyStructure',
            IsSunshadeInput = False,
            UA = 2.44
        )
        self.assertEqual('WAL1_main', ret['name'])
        self.assertEqual('N', ret['direction'])
        self.assertEqual(20, ret['area'])
        self.assertEqual('main', ret['space'])
        self.assertEqual('MyType', ret['type'])
        self.assertEqual('MyStructure', ret['structure'])
        self.assertEqual(False, ret['IsSunshadeInput'])
        self.assertEqual(2.44, ret['UA'])

    # 日よけ設定
    def test_make_wall_sunshade(self):
        ret = nb.make_wall(
            IsSimplifiedInput = True,
            name = 'WAL1',
            direction = 'N',
            spacename = 'main',
            spacearea = 20,
            type = 'MyType',
            structure = 'MyStructure',
            IsSunshadeInput = True,
            UA = 2.44,
            Y1 = 4,
            Y2 = 5,
            Z = 6
        )
        self.assertEqual('WAL1_main', ret['name'])
        self.assertEqual('N', ret['direction'])
        self.assertEqual(20, ret['area'])
        self.assertEqual('main', ret['space'])
        self.assertEqual('MyType', ret['type'])
        self.assertEqual('MyStructure', ret['structure'])
        self.assertEqual(True, ret['IsSunshadeInput'])
        self.assertEqual(2.44, ret['UA'])
        self.assertEqual(4, ret['Y1'])
        self.assertEqual(5, ret['Y2'])
        self.assertEqual(6, ret['Z'])
    
    #詳細入力(木造/UA)
    def test_make_wall_wood_ua(self):
        ret = nb.make_wall(
            IsSimplifiedInput = False,
            name = 'WAL1',
            direction = 'N',
            spacename = 'main',
            spacearea = 20,
            type = 'MyType',
            structure = 'wood',
            IsSunshadeInput = False,
            InputMethod = 'InputUA',
            UA = 2.55
        )
        self.assertEqual('InputUA', ret['InputMethod'])
        self.assertEqual(2.55, ret['UA'])
    
    #詳細入力(木造/詳細)
    def test_make_wall_wood_detail(self):
        ret = nb.make_wall(
            IsSimplifiedInput = False,
            name = 'WAL1',
            direction = 'N',
            spacename = 'main',
            spacearea = 20,
            type = 'MyType',
            structure = 'wood',
            IsSunshadeInput = False,
            InputMethod = 'InputAllDetails',
            Parts = [{'AreaRatio': 0.8, 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                  {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]},
                    {'AreaRatio': 0.2, 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                  {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}]
        )
        self.assertEqual('InputAllDetails', ret['InputMethod'])
        self.assertEqual(2, len(ret['Parts']))
        self.assertEqual(0.8, ret['Parts'][0]['AreaRatio'])

    #詳細入力(木造/レイヤー/天井)
    def test_make_wall_wood_layer_ceiling(self):
        ret = nb.make_wall(
            IsSimplifiedInput = False,
            name = 'WAL1',
            direction = 'N',
            spacename = 'main',
            spacearea = 20,
            type = 'Ceiling',
            structure = 'wood',
            IsSunshadeInput = False,
            InputMethod = 'InputAllLayers',
            Parts = [{'AreaRatio': 0.8, 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                  {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]},
                    {'AreaRatio': 0.2, 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                  {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}],
            TypeRoof = 'MyRoofType'
        )
        self.assertEqual('InputAllLayers', ret['InputMethod'])
        self.assertEqual(2, len(ret['Parts']))
        self.assertEqual(0.8, ret['Parts'][0]['AreaRatio'])
        self.assertEqual('MyRoofType', ret['TypeRoof'])
    
    ##TODO: レイヤーその他のパターン
    
    #詳細入力(木造/UR)
    def test_make_wall_wood_ur(self):
        ret = nb.make_wall(
            IsSimplifiedInput = False,
            name = 'WAL1',
            direction = 'N',
            spacename = 'main',
            spacearea = 20,
            type = 'Ceiling',
            structure = 'wood',
            IsSunshadeInput = False,
            InputMethod = 'InputUR',
            Parts = [{'AreaRatio': 0.8, 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                  {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]},
                    {'AreaRatio': 0.2, 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                  {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}],
            UR = 5.77
        )
        self.assertEqual('InputUR', ret['InputMethod'])
        self.assertEqual(2, len(ret['Parts']))
        self.assertEqual(0.8, ret['Parts'][0]['AreaRatio'])
        self.assertEqual(5.77, ret['URWood'])
   
    #詳細入力(RC/UA)
    def test_make_wall_rc_ua(self):
        ret = nb.make_wall(
            IsSimplifiedInput = False,
            name = 'WAL1',
            direction = 'N',
            spacename = 'main',
            spacearea = 20,
            type = 'MyType',
            structure = 'RC',
            IsSunshadeInput = False,
            InputMethod = 'InputUA',
            UA = 2.55
        )
        self.assertEqual('InputUA', ret['InputMethod'])
        self.assertEqual(2.55, ret['UA'])

    #詳細入力(RC/レイヤー)
    def test_make_wall_rc_layer(self):
        ret = nb.make_wall(
            IsSimplifiedInput = False,
            name = 'WAL1',
            direction = 'N',
            spacename = 'main',
            spacearea = 20,
            type = 'Ceiling',
            structure = 'RC',
            IsSunshadeInput = False,
            InputMethod = 'InputLayers',
            Parts = [{'AreaRatio': 0.8, 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                  {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]},
                    {'AreaRatio': 0.2, 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                  {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}],
        )
        self.assertEqual('InputLayers', ret['InputMethod'])
        self.assertEqual(2, len(ret['Parts']))
        self.assertEqual(0.8, ret['Parts'][0]['AreaRatio'])
   
    #詳細入力(鉄骨/UA)
    def test_make_wall_steel_ua(self):
        ret = nb.make_wall(
            IsSimplifiedInput = False,
            name = 'WAL1',
            direction = 'N',
            spacename = 'main',
            spacearea = 20,
            type = 'MyType',
            structure = 'steel',
            IsSunshadeInput = False,
            InputMethod = 'InputUA',
            UA = 2.55
        )
        self.assertEqual('InputUA', ret['InputMethod'])
        self.assertEqual(2.55, ret['UA'])

    #詳細入力(鉄骨/UR)
    def test_make_wall_steel_ur(self):
        ret = nb.make_wall(
            IsSimplifiedInput = False,
            name = 'WAL1',
            direction = 'N',
            spacename = 'main',
            spacearea = 20,
            type = 'Ceiling',
            structure = 'steel',
            IsSunshadeInput = False,
            InputMethod = 'InputUR',
            Parts = [{'AreaRatio': 0.8, 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                  {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]},
                    {'AreaRatio': 0.2, 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                  {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}],
            UR = 5.77
        )
        self.assertEqual('InputUR', ret['InputMethod'])
        self.assertEqual(2, len(ret['Parts']))
        self.assertEqual(0.8, ret['Parts'][0]['AreaRatio'])
        self.assertEqual(5.77, ret['URSteel'])

    def test_convert_wall(self):
        d = {
            'Common': {
                'Region': 6,
                'IsSimplifiedInput': True,
                'MainOccupantRoomFloorArea': 30.0,
                'OtherOccupantRoomFloorArea': 60.0,
                'TotalFloorArea': 120.0,
            },
            'Walls': [
                { 'name': 'Ceiling', 'type': 'Ceiling', 'structure': 'wood', 'InputMethod' :'InputUA', 
                'direction': 'top', 'area': 67.8, 'UA': 0.24, 'IsSunshadeInput': False },
                { 'name': 'Ceiling', 'type': 'Ceiling', 'structure': 'wood', 'InputMethod' :'InputAllDetails', 'direction': 'top', 'area': 67.8,
                'Parts': [{'AreaRatio': 0.8, 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                        {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]},
                          {'AreaRatio': 0.2, 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                        {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}],
                'IsSunshadeInput': False },
                { 'name': 'Floor', 'type': 'Floor', 'structure': 'wood', 'InputMethod' :'InputAllLayers', 'direction': 'bottom', 'area': 67.8,
                'FloorConstructionMethod' :'FrameInsulcolumn',
                'Parts': [{'TypeFloor': 'Insulation', 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                                 {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]},
                          {'TypeFloor': 'Heatbridge', 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                                 {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}],
                'IsSunshadeInput': False },
                { 'name': 'Wall', 'type': 'Wall', 'structure': 'wood', 'InputMethod' :'InputAllLayers', 'direction': 'N', 'area': 67.8, 
                'WallConstructionMethod': 'WallInsuladdBackvertical',
                'Parts': [{'TypeWall': 'Insulation', 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                                {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]},
                          {'TypeWall': 'Heatbridge', 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                                {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}],         
                'IsSunshadeInput': False },
                { 'name': 'Ceiling', 'type': 'Ceiling', 'structure': 'wood', 'InputMethod' :'InputAllLayers', 'direction': 'top', 'area': 67.8,
                'RoofConstructionMethod': 'Insulrafter', 
                'Parts': [{'TypeRoof': 'Insulation', 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                                {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]},
                          {'TypeRoof': 'Heatbridge', 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                                {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}],
                'IsSunshadeInput': False },
                { 'name': 'BoundaryCeiling', 'type': 'BoundaryCeiling', 'structure': 'wood', 'InputMethod' :'InputAllLayers', 
                'direction': 'top', 'area': 67.8, 'CeilingConstructionMethod': 'Insulbeam', 
                'Parts': [{'TypeCeiling': 'Insulation', 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                                   {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]},
                          {'TypeCeiling': 'Heatbridge', 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                                   {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}],
                'IsSunshadeInput': False },
                { 'name': 'Ceiling', 'type': 'Ceiling', 'structure': 'wood', 'InputMethod' :'InputUR',
                'direction': 'top', 'area': 67.8, 'UR': 0.05,
                'Parts': [{'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                      {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}],
                'IsSunshadeInput': False },
                { 'name': 'Ceiling', 'type': 'Ceiling', 'structure': 'RC', 'InputMethod' :'InputUA', 
                'direction': 'top', 'area': 67.8, 'UA': 0.24, 'IsSunshadeInput': False },
                { 'name': 'Ceiling', 'type': 'Ceiling', 'structure': 'RC', 'InputMethod' :'InputLayers', 
                'direction': 'top', 'area': 67.8,
                'Parts': [{'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                      {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}],         
                'IsSunshadeInput': False },
                { 'name': 'Ceiling', 'type': 'Ceiling', 'structure': 'steel', 'InputMethod' :'InputUA', 
                'direction': 'top', 'area': 67.8, 'UA': 0.24, 'IsSunshadeInput': False },
                { 'name': 'Ceiling', 'type': 'Ceiling', 'structure': 'steel', 'InputMethod' :'InputUR', 
                'direction': 'top', 'area': 67.8, 'UR': 0.10, 
                'Parts': [{'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                      {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}],         
                'IsSunshadeInput': False },
                { 'name': 'Ceiling', 'type': 'Ceiling', 'structure': 'other', 'direction': 'top', 'area': 67.8, 'IsSunshadeInput': False }
            ]
        }
        ret = nb.convert_wall(d)

        #Wallsに指定した壁が主居室・そのほか居室・非居室に割り付けられる
        # →入力に対して3倍の壁が返ってくる
        self.assertEqual(12*3, len(ret))

    #簡易入力
    def test_make_window_simple(self):
        ret = nb.make_window(
            IsSimplifiedInput = True,
            name = 'WND1',
            direction = 'S',
            spacename = 'other',
            spacearea = 2,
            IsSunshadeInput = False,
            UW = 3
        )
        self.assertEqual('WND1_other', ret['name'])
        self.assertEqual('S', ret['direction'])
        self.assertEqual(2, ret['area'])
        self.assertEqual('other', ret['space'])
        self.assertEqual(3, ret['UW'])
        self.assertEqual(False, ret['IsSunshadeInput'])

    #詳細入力/一重窓
    def test_make_window_single_eta(self):
        ret = nb.make_window(
            IsSimplifiedInput = False,
            name = 'WND1',
            direction = 'S',
            spacename = 'other',
            spacearea = 2,
            UW = 3,
            IsSunshadeInput = False,
            TypeWindow = 'Single',
            IsEtaValueInput = True,
            Eta = 1.23
        )
        self.assertEqual(False, ret['IsSunshadeInput'])
        self.assertEqual('Single', ret['TypeWindow'])
        self.assertEqual(True, ret['IsEtaValueInput'])
        self.assertEqual(1.23, ret['Eta'])

    #詳細入力/一重窓
    def test_make_window_single(self):
        ret = nb.make_window(
            IsSimplifiedInput = False,
            name = 'WND1',
            direction = 'S',
            spacename = 'other',
            spacearea = 2,
            UW = 3,
            IsSunshadeInput = False,
            TypeWindow = 'Single',
            IsEtaValueInput = False,
            TypeFrame = 'MyTypeFrame',
            TypeGlass = 'MyTypeGlass',
            TypeShade = 'MyTypeShade'
        )
        self.assertEqual(False, ret['IsSunshadeInput'])
        self.assertEqual('Single', ret['TypeWindow'])
        self.assertEqual(False, ret['IsEtaValueInput'])
        self.assertEqual('MyTypeFrame', ret['TypeFrame'])
        self.assertEqual('MyTypeGlass', ret['TypeGlass'])
        self.assertEqual('MyTypeShade', ret['TypeShade'])

    #詳細入力/二重窓
    def test_make_window_double_eta(self):
        ret = nb.make_window(
            IsSimplifiedInput = False,
            name = 'WND1',
            direction = 'S',
            spacename = 'other',
            spacearea = 2,
            UW = 3,
            IsSunshadeInput = False,
            TypeWindow = 'Double',
            IsEtaValueInput = True,
            EtaInside = 1.01,
            EtaOutside = 1.02,
        )
        self.assertEqual(False, ret['IsSunshadeInput'])
        self.assertEqual('Double', ret['TypeWindow'])
        self.assertEqual(True, ret['IsEtaValueInput'])
        self.assertEqual(1.01, ret['EtaInside'])
        self.assertEqual(1.02, ret['EtaOutside'])

    #詳細入力/二重窓
    def test_make_window_double(self):
        ret = nb.make_window(
            IsSimplifiedInput = False,
            name = 'WND1',
            direction = 'S',
            spacename = 'other',
            spacearea = 2,
            UW = 3,
            IsSunshadeInput = False,
            TypeWindow = 'Double',
            IsEtaValueInput = False,
            TypeFrameInside = 'MyTypeFrameIn',
            TypeGlassInside = 'MyTypeGlassIn',
            TypeShadeInside = 'MyTypeShadeIn',
            TypeFrameOutside = 'MyTypeFrameOut',
            TypeGlassOutside = 'MyTypeGlassOut',
            TypeShadeOutside = 'MyTypeShadeOut'
        )
        self.assertEqual(False, ret['IsSunshadeInput'])
        self.assertEqual('Double', ret['TypeWindow'])
        self.assertEqual(False, ret['IsEtaValueInput'])
        self.assertEqual('MyTypeFrameIn', ret['TypeFrameInside'])
        self.assertEqual('MyTypeGlassIn', ret['TypeGlassInside'])
        self.assertEqual('MyTypeShadeIn', ret['TypeShadeInside'])
        self.assertEqual('MyTypeFrameOut', ret['TypeFrameOutside'])
        self.assertEqual('MyTypeGlassOut', ret['TypeGlassOutside'])
        self.assertEqual('MyTypeShadeOut', ret['TypeShadeOutside'])

    #日よけ/一重窓
    def test_make_window_sunshade_single(self):
        ret = nb.make_window(
            IsSimplifiedInput = True,
            name = 'WND1',
            direction = 'S',
            spacename = 'other',
            spacearea = 2,
            UW = 3,
            IsSunshadeInput = True,
            TypeWindow = 'Single',
            TypeGlass = 'MyGlassType',
            Y1 = 4,
            Y2 = 5,
            Z = 6
        )
        self.assertEqual(True, ret['IsSunshadeInput'])
        self.assertEqual('MyGlassType', ret['TypeGlass'])
        self.assertEqual(4, ret['Y1'])
        self.assertEqual(5, ret['Y2'])
        self.assertEqual(6, ret['Z'])

    #日よけ/二重窓
    def test_make_window_sunshade_double(self):
        ret = nb.make_window(
            IsSimplifiedInput = True,
            name = 'WND1',
            direction = 'S',
            spacename = 'other',
            spacearea = 2,
            UW = 3,
            IsSunshadeInput = True,
            TypeWindow = 'Double',
            TypeGlassInside = 'MyGlassTypeIn',
            TypeGlassOutside = 'MyGlassTypeOut',
            Y1 = 4,
            Y2 = 5,
            Z = 6
        )
        self.assertEqual(True, ret['IsSunshadeInput'])
        self.assertEqual('MyGlassTypeIn', ret['TypeGlassInside'])
        self.assertEqual('MyGlassTypeOut', ret['TypeGlassOutside'])
        self.assertEqual(4, ret['Y1'])
        self.assertEqual(5, ret['Y2'])
        self.assertEqual(6, ret['Z'])

    def test_convert_window(self):
        d = {
            'Common': {
                'Region': 6,
                'IsSimplifiedInput': False,
                'MainOccupantRoomFloorArea': 30.0,
                'OtherOccupantRoomFloorArea': 60.0,
                'TotalFloorArea': 120.0,
            },
            'Windows': [
                { 'name': 'WindowSW', 'direction': 'SW', 'area': 30.25, 'UW': 6.51, 'TypeWindow': 'Single', 
                'IsEtaValueInput': False, 'TypeFrame': 'WoodOrResin', 'TypeGlass': '3WgG', 'TypeShade': 'Shoji',
                'IsSunshadeInput': True, 'Y1': 0.00, 'Y2': 1.00, 'Z': 0.60 },
                { 'name': 'WindowNW', 'direction': 'NW', 'area': 3.17, 'UW': 4.65, 'TypeWindow': 'Single', 
                'IsEtaValueInput': True, 'Eta': 0.738, 'IsSunshadeInput': False },
                { 'name': 'WindowSW', 'direction': 'SW', 'area': 30.25, 'UW': 6.51, 'TypeWindow': 'Double', 'IsEtaValueInput': False,
                'TypeFrameInside': 'WoodOrResin', 'TypeGlassInside': '3WgG', 'TypeShadeInside': 'Shoji',
                'TypeFrameOutside': 'Steel', 'TypeGlassOutside': '3WgG', 'TypeShadeOutside': 'ExtarnalBlind',
                'IsSunshadeInput': True, 'Y1': 0.00, 'Y2': 1.00, 'Z': 0.60 },
                { 'name': 'WindowNW', 'direction': 'NW', 'area': 3.17, 'UW': 4.65, 'TypeWindow': 'Double', 'IsEtaValueInput': True,
                'EtaInside': 0.738, 'TypeGlassInside': '3WgG', 'EtaOutside': 0.738, 'TypeGlassOutside': '3WgG',
                'IsSunshadeInput': True, 'Y1': 0.00, 'Y2': 1.00, 'Z': 0.60 }
            ]
        }    
        ret = nb.convert_window(d)
        self.assertEqual(12, len(ret))

    def test_make_door(self):
        ret = nb.make_door(
            name = 'DOOR1',
            direction = 'W',
            spacename = 'nonliving',
            spacearea = 3,
            IsSunshadeInput = False,
            U = 2
        )
        self.assertEqual('DOOR1_nonliving', ret['name'])
        self.assertEqual('W', ret['direction'])
        self.assertEqual(3, ret['area'])
        self.assertEqual('nonliving', ret['space'])
        self.assertEqual(False, ret['IsSunshadeInput'])
        self.assertEqual(2, ret['U'])

    def test_make_door_sunshade(self):
        ret = nb.make_door(
            name = 'DOOR1',
            direction = 'W',
            spacename = 'nonliving',
            spacearea = 3,
            IsSunshadeInput = True,
            Y1 = 4,
            Y2 = 5,
            Z = 6,
            U = 2
        )
        self.assertEqual('DOOR1_nonliving', ret['name'])
        self.assertEqual('W', ret['direction'])
        self.assertEqual(3, ret['area'])
        self.assertEqual('nonliving', ret['space'])
        self.assertEqual(True, ret['IsSunshadeInput'])
        self.assertEqual(4, ret['Y1'])
        self.assertEqual(5, ret['Y2'])
        self.assertEqual(6, ret['Z'])
        self.assertEqual(2, ret['U'])

    def test_convert_door(self):
        d = {
            'Common': {
                'Region': 6,
                'IsSimplifiedInput': False,
                'MainOccupantRoomFloorArea': 30.0,
                'OtherOccupantRoomFloorArea': 60.0,
                'TotalFloorArea': 120.0,
            },
            'Doors': [
                { 'name': 'DoorNW', 'direction': 'NW', 'area': 2.52, 'U': 6.51, 'IsSunshadeInput': False },
                { 'name': 'DoorNE', 'direction': 'NE', 'area': 2.16, 'U': 4.65, 'IsSunshadeInput': True, 'Y1': 0.00, 'Y2': 1.00, 'Z': 0.60 }
            ]
        }    
        ret = nb.convert_door(d)
        self.assertEqual(6, len(ret))

    def test_make_heatbridge(self):
        ret = nb.make_heatbridge(
            structure = 'rc',
            direction1 = 'NW',
            direction2 = 'NE',
            spacename = 'main',
            spacelength = 10
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
                'IsSimplifiedInput': False,
                'MainOccupantRoomFloorArea': 30.0,
                'OtherOccupantRoomFloorArea': 60.0,
                'TotalFloorArea': 120.0
            },
            'Walls': [
                { 'name': 'Ceiling', 'type': 'Ceiling', 'structure': 'wood', 'InputMethod' :'InputUA', 
                'direction': 'top', 'area': 67.8, 'UA': 0.24, 'IsSunshadeInput': False },
                { 'name': 'Ceiling', 'type': 'Ceiling', 'structure': 'wood', 'InputMethod' :'InputAllDetails', 'direction': 'top', 'area': 67.8,
                'Parts': [{'AreaRatio': 0.8, 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                        {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]},
                            {'AreaRatio': 0.2, 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                        {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}],
                'IsSunshadeInput': False },
                { 'name': 'Floor', 'type': 'Floor', 'structure': 'wood', 'InputMethod' :'InputAllLayers', 'direction': 'bottom', 'area': 67.8,
                'FloorConstructionMethod' :'FrameInsulcolumn',
                'Parts': [{'TypeFloor': 'Insulation', 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                                 {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]},
                          {'TypeFloor': 'Heatbridge', 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                                 {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}],
                'IsSunshadeInput': False },
                { 'name': 'Wall', 'type': 'Wall', 'structure': 'wood', 'InputMethod' :'InputAllLayers', 'direction': 'N', 'area': 67.8, 
                'WallConstructionMethod': 'WallInsuladdBackvertical',
                'Parts': [{'TypeWall': 'Insulation', 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                                {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]},
                          {'TypeWall': 'Heatbridge', 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                                {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}],         
                'IsSunshadeInput': False },
                { 'name': 'Ceiling', 'type': 'Ceiling', 'structure': 'wood', 'InputMethod' :'InputAllLayers', 'direction': 'top', 'area': 67.8,
                'RoofConstructionMethod': 'Insulrafter', 
                'Parts': [{'TypeRoof': 'Insulation', 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                                {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]},
                          {'TypeRoof': 'Heatbridge', 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                                {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}],
                'IsSunshadeInput': False },
                { 'name': 'BoundaryCeiling', 'type': 'BoundaryCeiling', 'structure': 'wood', 'InputMethod' :'InputAllLayers', 
                'direction': 'top', 'area': 67.8, 'CeilingConstructionMethod': 'Insulbeam', 
                'Parts': [{'TypeCeiling': 'Insulation', 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                                   {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]},
                          {'TypeCeiling': 'Heatbridge', 'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                                                   {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}],
                'IsSunshadeInput': False },
                { 'name': 'Ceiling', 'type': 'Ceiling', 'structure': 'wood', 'InputMethod' :'InputUR',
                'direction': 'top', 'area': 67.8, 'UR': 0.05,
                'Parts': [{'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                      {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}],
                'IsSunshadeInput': False },
                { 'name': 'Ceiling', 'type': 'Ceiling', 'structure': 'RC', 'InputMethod' :'InputUA', 
                'direction': 'top', 'area': 67.8, 'UA': 0.24, 'IsSunshadeInput': False },
                { 'name': 'Ceiling', 'type': 'Ceiling', 'structure': 'RC', 'InputMethod' :'InputLayers', 
                'direction': 'top', 'area': 67.8,
                'Parts': [{'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                      {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}],         
                'IsSunshadeInput': False },
                { 'name': 'Ceiling', 'type': 'Ceiling', 'structure': 'steel', 'InputMethod' :'InputUA', 
                'direction': 'top', 'area': 67.8, 'UA': 0.24, 'IsSunshadeInput': False },
                { 'name': 'Ceiling', 'type': 'Ceiling', 'structure': 'steel', 'InputMethod' :'InputUR', 
                'direction': 'top', 'area': 67.8, 'UR': 0.10, 
                'Parts': [{'Layers': [{'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 },
                                      {'name': 'wood','thick': 0.012, 'cond': 0.16, 'specH': 720 }]}],         
                'IsSunshadeInput': False },
                { 'name': 'Ceiling', 'type': 'Ceiling', 'structure': 'other', 'direction': 'top', 'area': 67.8, 'IsSunshadeInput': False }
            ],
            'Windows': [
                { 'name': 'WindowSW', 'direction': 'SW', 'area': 30.25, 'UW': 6.51, 'TypeWindow': 'Single', 
                'IsEtaValueInput': False, 'TypeFrame': 'WoodOrResin', 'TypeGlass': '3WgG', 'TypeShade': 'Shoji',
                'IsSunshadeInput': True, 'Y1': 0.00, 'Y2': 1.00, 'Z': 0.60 },
                { 'name': 'WindowNW', 'direction': 'NW', 'area': 3.17, 'UW': 4.65, 'TypeWindow': 'Single', 
                'IsEtaValueInput': True, 'Eta': 0.738, 'IsSunshadeInput': False },
                { 'name': 'WindowSW', 'direction': 'SW', 'area': 30.25, 'UW': 6.51, 'TypeWindow': 'Double', 'IsEtaValueInput': False,
                'TypeFrameInside': 'WoodOrResin', 'TypeGlassInside': '3WgG', 'TypeShadeInside': 'Shoji',
                'TypeFrameOutside': 'Steel', 'TypeGlassOutside': '3WgG', 'TypeShadeOutside': 'ExtarnalBlind',
                'IsSunshadeInput': True, 'Y1': 0.00, 'Y2': 1.00, 'Z': 0.60 },
                { 'name': 'WindowNW', 'direction': 'NW', 'area': 3.17, 'UW': 4.65, 'TypeWindow': 'Double', 'IsEtaValueInput': True,
                'EtaInside': 0.738, 'TypeGlassInside': '3WgG', 'EtaOutside': 0.738, 'TypeGlassOutside': '3WgG',
                'IsSunshadeInput': True, 'Y1': 0.00, 'Y2': 1.00, 'Z': 0.60 }
            ],
            'Doors': [
                { 'name': 'DoorNW', 'direction': 'NW', 'area': 2.52, 'U': 6.51, 'IsSunshadeInput': False },
                { 'name': 'DoorNE', 'direction': 'NE', 'area': 2.16, 'U': 4.65, 'IsSunshadeInput': True, 'Y1': 0.00, 'Y2': 1.00, 'Z': 0.60 }
            ],
            'Heatbridges': [
                { 'name': 'NE', 'structure': 'RC', 'length': 1.00, 'psi': 1.8, 'direction1': 'N', 'direction2': 'E' },
                { 'name': 'NW', 'structure': 'Steel', 'length': 2.00, 'psi': 1.8, 'direction1': 'N', 'direction2': 'W' }
            ],
            'EarthfloorPerimeters': [
                { 'name': 'NW', 'direction': 'NW', 'length': 2.43, 'psi': 1.8 },
                { 'name': 'NE', 'direction': 'NE', 'length': 2.43, 'psi': 1.8 }
            ],
            'Earthfloors': [
                { 'area': 5.0, 'name': 'other' },
                { 'area': 5.0, 'name': 'entrance' }
            ]
        }
        nb.convert(d)    
    
if __name__ == '__main__':
    unittest.main()