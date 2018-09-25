import matplotlib
from matplotlib.testing.decorators import image_comparison
import math
import unittest
import nbimporter
import LV1toLV2 as nb
from RoundNumber import round_number

class TestLV1toLV2(unittest.TestCase):

    def test_get_design_parts_area(self):
        self.assertEqual(67.8, nb.get_design_parts_area(50.85,120))

    def test_convert_common(self):
        result = nb.convert_common(
            Region = 6,
            MainOccupantRoomFloorArea = 30.0,
            OtherOccupantRoomFloorArea = 60.0,
            TotalFloorArea = 120.0
        )

        self.assertEqual(6, result['Region'])
        self.assertEqual(30.0, result['MainOccupantRoomFloorArea'])
        self.assertEqual(60.0, result['OtherOccupantRoomFloorArea'])
        self.assertEqual(120.0, result['TotalFloorArea'])
        self.assertEqual(True, result['IsSimplifiedInput'])
    
    def test_get_gypsum(self):
        m = nb.get_gypsum()
        self.assertEqual('GPB', m.name)
        self.assertEqual(0.0095, m.thick)
        self.assertEqual(0.22, m.cond)
        self.assertEqual(830.0, m.spech)

    def test_get_plywood(self):
        m = nb.get_plywood()
        self.assertEqual('PED', m.name)
        self.assertEqual(0.012, m.thick)
        self.assertEqual(0.16, m.cond)
        self.assertEqual(720.0, m.spech)

    def test_get_concrete(self):
        m = nb.get_concrete()
        self.assertEqual('RC', m.name)
        self.assertEqual(0.120, m.thick)
        self.assertEqual(1.60, m.cond)
        self.assertEqual(2000.0, m.spech)

    def test_convert_u_value_to_spec___Wood_Ceiling(self):
        
        layer = nb.convert_u_value_to_spec('Wood', 'Ceiling', 0.1)
        m = layer[1]

        R = 1.0 / 0.1
        Ro, Ri = 0.040, 0.090
        d = math.floor( max(0, (R - (Ro + m.R() + Ri)) * 0.045) * 1000) / 1000

        self.assertEqual('GW16K', layer[0].name)
        self.assertEqual(0.045, layer[0].cond)
        self.assertEqual(13.0, layer[0].spech)
        self.assertEqual(d, layer[0].thick)
        self.assertEqual('GPB', m.name)

    def test_convert_u_value_to_spec___Steel_Wall(self):
        
        layer = nb.convert_u_value_to_spec('Steel', 'Wall', 0.1)
        m = layer[1]

        R = 1.0 / 0.1
        Ro, Ri = 0.040, 0.110
        d = math.floor( max(0, (R - (Ro + m.R() + Ri)) * 0.045) * 1000) / 1000

        self.assertEqual('GW16K', layer[0].name)
        self.assertEqual(0.045, layer[0].cond)
        self.assertEqual(13.0, layer[0].spech)
        self.assertEqual(d, layer[0].thick)
        self.assertEqual('GPB', m.name)

    def test_convert_u_value_to_spec___Other_Floor(self):
        
        layer = nb.convert_u_value_to_spec('Other', 'Floor', 0.1)
        m = layer[1]

        R = 1.0 / 0.1
        Ro, Ri = 0.040, 0.150
        d = math.floor( max(0, (R - (Ro + m.R() + Ri)) * 0.045) * 1000) / 1000

        self.assertEqual('GW16K', layer[0].name)
        self.assertEqual(0.045, layer[0].cond)
        self.assertEqual(13.0, layer[0].spech)
        self.assertEqual(d, layer[0].thick)
        self.assertEqual('PED', m.name)

    def test_convert_u_value_to_spec___RC(self):
        
        layer = nb.convert_u_value_to_spec('RC', 'BoundaryWall', 0.1)
        m = layer[0]

        R = 1.0 / 0.1
        Ro, Ri = 0.110, 0.110
        d = math.floor( max(0, (R - (Ro + m.R() + Ri)) * 0.045) * 1000) / 1000

        self.assertEqual('RC', m.name)
        self.assertEqual('GW16K', layer[1].name)
        self.assertEqual(0.045, layer[1].cond)
        self.assertEqual(13.0, layer[1].spech)
        self.assertEqual(d, layer[1].thick)

    def test_make_wall(self):
        wall = nb.make_wall(
            Name = 'MyCeiling', 
            Type = 'Ceiling', 
            Structure = 'Wood', 
            Direction = 'Top',    
            UA = 7.7,  
            Area = 50.85,
            TotalFloorArea = 120.0
        )

        self.assertEqual('MyCeiling', wall['Name'])
        self.assertEqual('Ceiling', wall['Type'])
        self.assertEqual('Wood', wall['Structure'])
        self.assertEqual('Top', wall['Direction'])
        #self.assertEqual(, wall.Area)
        self.assertEqual(1, len(wall['Parts']))

        part = wall['Parts'][0]
        self.assertEqual(1.0, part['AreaRatio'])

    def test_convert_wall(self):
        result = nb.convert_wall(
            Region = 6,
            MainOccupantRoomFloorArea = 30.0,
            OtherOccupantRoomFloorArea = 60.0,
            TotalFloorArea = 120.0,
            InsulationType = 'FloorIns',
            URoof = 7.7,
            UWall = 6.67,
            UFloor = 5.27,
            UDoor = 4.65,
            IsInputPsiBase = True,
            PsiBaseOthers = 1.8,
            PsiBaseEntrance = 1.8
        )
        self.assertEqual(6, len(result))

    def test_get_coefficients(self):
        self.assertEqual((0.01, 5, 20, 3), nb.get_coefficients('heating', 7, 'SE'))
        self.assertEqual((0.01, 16, 24, 2), nb.get_coefficients('cooling', 7, 'SW'))
        self.assertEqual((0.01, 16, 24, 2), nb.get_coefficients('cooling', 8, 'NW'))

        #8地域暖房はエラー
        with self.assertRaises(ValueError):
            nb.get_coefficients('heating', 8, 'SE')

    def test_calc_overhang_width(self):
        # f/a -b <= 0
        self.assertEqual(5.0, nb.calc_overhang_width(a = 2.0, f = 6.0, b = 3.0, c = 0, d = 0, y1 = 0, y2 = 0))
        #  c * (d * y1 + y2) / (( f / a ) - b) < 5.0
        self.assertEqual(4.99, nb.calc_overhang_width(a = 1.0, f = 1.0, b = 0, c = 1, d = 2, y1 = 2, y2 = 0.99))
        #  c * (d * y1 + y2) / (( f / a ) - b) > 5.0
        self.assertEqual(5.0, nb.calc_overhang_width(a = 1.0, f = 1.0, b = 0, c = 1, d = 2, y1 = 2, y2 = 1.01))
    
    def test_get_overhang_width_for_heating(self):
        #a, b, c, d = 0.01, 10, 15, 2
        #y1, y2 = 0, 1.1
        #f = 0.7
        #overhang = (15 * (2 * 0 + 1.1)) / ( 0.7 / 0.01 - 10 ) = 16.5 / 60 = 0.275
        self.assertEqual(0.275, nb.get_overhang_width_for_heating(4, 'NW', 0, 1.1, 0.7))

        ### 取得日射熱補正係数の上限は0.72とする。
        ### 出巾の計算結果は切り上げの処理を行う。
        #a, b, c, d = 0.01, 10, 15, 2
        #y1, y2 = 0, 1.1
        #f = 0.73 => 0.72で計算される
        #overhang = (15 * (2 * 0 + 1.1)) / ( 0.72 / 0.01 - 10 ) = 16.5 / 62 = 0.266129 => 0.267 (小数点以下第3位まで切り上げ)
        self.assertEqual(0.267, nb.get_overhang_width_for_heating(4, 'NW', 0, 1.1, 0.73))

        ### 8地域では暖房期の出巾が定義されていないため、エラーとする。
        with self.assertRaises(ValueError):
            self.assertEqual(0.267, nb.get_overhang_width_for_heating(8, 'NW', 0, 1.1, 0.73))
    
    def test_get_overhang_width_for_cooling(self):
        ### 出巾の計算結果は切り捨ての処理を行う。
        #a, b, c, d = 0.01, 16, 24, 2
        #y1, y2 = 0, 1.1
        #f = 0.9
        #overhang = (24 * (2 * 0 + 1.1)) / ( 0.9 / 0.01 - 16 ) = 26.4 / 74 = 0.356756 => 0.356 (小数点以下第3位まで切り下げ)
        self.assertEqual(0.356, nb.get_overhang_width_for_cooling(4, 'NW', 0, 1.1, 0.9))

        ### 取得日射熱補正係数の上限は0.93とする。
        #a, b, c, d = 0.01, 16, 24, 2
        #y1, y2 = 0, 1.1
        #f = 0.94 => 0.93で計算される
        #overhang = (24 * (2 * 0 + 1.1)) / ( 0.93 / 0.01 - 16 ) = 26.4 / 77 = 0.342857143 => 0.342 (小数点以下第3位まで切り下げ)
        self.assertEqual(0.342, nb.get_overhang_width_for_cooling(4, 'NW', 0, 1.1, 0.94))
    
    def test_make_window(self):
        ### F値あり

        #### 8地域以外
        window = nb.make_window(
            Name = 'MyWindow',
            Direction = 'SW',
            Area = 22.69,
            TotalFloorArea = 120.0,
            UWnd = 3.49,
            Region = 6,
            EtaDC = 0.51,
            EtaDH = 0.52,
            IsInputFValue = True,
            FValueC = 0.9,
            FValueH = 0.7,
            y1 = 0,
            y2 = 1.1        
        )
        z_h = nb.get_overhang_width_for_heating(6, 'SW', 0, 1.1, 0.7)
        z_c = nb.get_overhang_width_for_cooling(6, 'SW', 0, 1.1, 0.9)
        z = round_number( (z_h + z_c) / 2, 3)
        self.assertEqual('MyWindow', window['Name'])
        self.assertEqual('SW', window['Direction'])
        self.assertEqual('Single', window['TypeWindow'])
        self.assertEqual(0.51, window['etaCooling'])
        self.assertEqual(0.52, window['etaHeating'])
        self.assertEqual(3.49, window['UW'])
        self.assertEqual(True, window['IsSunshadeInput'])
        self.assertEqual(0, window['Y1'])
        self.assertEqual(1.1, window['Y2'])
        self.assertEqual(z, window['z'])

        #### 8地域
        window = nb.make_window(
            Name = 'MyWindow',
            Direction = 'SW',
            Area = 22.69,
            TotalFloorArea = 120.0,
            UWnd = 3.49,
            Region = 8,
            EtaDC = 0.51,
            EtaDH = None,
            IsInputFValue = True,
            FValueC = 0.9,
            FValueH = None,
            y1 = 0,
            y2 = 1.1        
        )
        z_c = nb.get_overhang_width_for_cooling(8, 'SW', 0, 1.1, 0.9)
        self.assertEqual(0.51, window['etaCooling'])
        self.assertEqual(None, window['etaHeating'])
        self.assertEqual(3.49, window['UW'])
        self.assertEqual(True, window['IsSunshadeInput'])
        self.assertEqual(0, window['Y1'])
        self.assertEqual(1.1, window['Y2'])
        self.assertEqual(z_c, window['z'])

        ### F値なし
        window = nb.make_window(
            Name = 'MyWindow',
            Direction = 'SW',
            Area = 22.69,
            TotalFloorArea = 120.0,
            UWnd = 3.49,
            Region = 4,
            EtaDC = 0.51,
            EtaDH = 0.52,
            IsInputFValue = False
        )
        z_c = nb.get_overhang_width_for_cooling(8, 'SW', 0, 1.1, 0.9)
        self.assertEqual(False, window['IsSunshadeInput'])

    def test_convert_window(self):
        window = nb.convert_window(
            Region = 6,
            MainOccupantRoomFloorArea = 30.0,
            OtherOccupantRoomFloorArea = 60.0,
            TotalFloorArea = 120.0,
            UWnd = 3.49,
            EtaDC = 0.51,       
            EtaDH = 0.51, 
            IsInputFValue = True, 
            FValueC = 0.9,
            FValueH = 0.7
        )
        self.assertEqual(4, len(window))
    
    def test_make_door(self):
        door = nb.make_door(
            Name = 'MyDoor',
            Direction = 'NW',
            Area = 2.52,
            TotalFloorArea = 120.0,
            UDoor = 2.33
        )
        area = nb.get_design_parts_area(2.52, 120.0)
        self.assertEqual('MyDoor', door['Name'])
        self.assertEqual('NW', door['Direction'])
        self.assertEqual(area, door['Area'])
        self.assertEqual(2.33, door['U'])
        self.assertEqual(False, door['IsSunshadeInput'])
    
    def test_convert_door(self):
        door = nb.convert_door(
            TotalFloorArea = 120.0,
            UDoor = 2.33,
        )
        self.assertEqual(2, len(door))

    def test_make_earth_floor(self):
        ef = nb.make_earth_floor(
            Name = 'MyEarthFloor',
            Direction = 'NW',
            Length = 3.5,
            Psi = 1.8,
            TotalFloorArea = 120.0
        )
        length = nb.get_design_parts_area(3.5, 120.0)
        self.assertEqual('MyEarthFloor', ef['Name'])
        self.assertEqual('NW', ef['Direction'])
        self.assertEqual(length, ef['Length'])
        self.assertEqual(1.8, ef['Psi'])

    def test_convert_earthfloor_perimeters(self):
        ## 実行時エラーにならないことを確認 ##
        #FloorIns / IsInputPsiBase = False
        nb.convert_earthfloor_perimeters( 
            InsulationType = 'FloorIns',
            TotalFloorArea = 120.0,
            IsInputPsiBase = False
        )
        #FloorIns / IsInputPsiBase = True
        nb.convert_earthfloor_perimeters( 
            InsulationType = 'FloorIns',
            TotalFloorArea = 120.0,
            IsInputPsiBase = True,
            PsiBaseOthers = 1.5,
            PsiBaseEntrance = 1.2
        )
        #BaseIns / IsInputPsiBase = False
        nb.convert_earthfloor_perimeters( 
            InsulationType = 'BaseIns',
            TotalFloorArea = 120.0,
            IsInputPsiBase = False
        )
        #BaseIns / IsInputPsiBase = True
        nb.convert_earthfloor_perimeters( 
            InsulationType = 'BaseIns',
            TotalFloorArea = 120.0,
            IsInputPsiBase = True,
            PsiBaseOthers = 1.5,
            PsiBaseEntrance = 1.2
        )

    def test_convert(self):
        ## 実行時エラーにならないことを確認 ##
        d = {
            'Region' : 6,
            'MainOccupantRoomFloorArea': 30.0,
            'OtherOccupantRoomFloorArea': 60.0,
            'TotalFloorArea': 120.0,
            'InsulationType' : 'FloorIns',
            'URoof' : 7.7,
            'UWall' : 6.67,
            'UFloor' : 5.27,
            'UDoor' : 4.65,
            'UWnd' : 3.49,
            'EtaDC' : 0.51,       
            'EtaDH' : 0.51, 
            'IsInputFValue' : True, 
            'FValueC' : 0.9,
            'FValueH' : 0.7,
            'IsInputPsiBase' : True,
            'PsiBaseOthers' : 1.8,
            'PsiBaseEntrance' :1.8
        }
        nb.convert(d)    
    
if __name__ == '__main__':
    unittest.main()