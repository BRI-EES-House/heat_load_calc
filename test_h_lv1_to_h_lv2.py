import unittest
import nbimporter
import h_lv1_to_h_lv2 as nb

class TestLV1toLV2(unittest.TestCase):

    def test_get_r_size(self):
        self.assertAlmostEqual(1.33333, nb.get_r_size(120.0),5)
    
    def test_get_direction(self):
        self.assertEqual('sw', nb.get_direction('0'))
        self.assertEqual('nw', nb.get_direction('90'))
        self.assertEqual('ne', nb.get_direction('180'))
        self.assertEqual('se', nb.get_direction('270'))
        self.assertEqual('top', nb.get_direction('top'))

    def test_get_general_parts_f_f(self):
        
        result = nb.get_general_parts(
            a_a=90.0,
            house_type='f_f',
            u_roof=7.7,
            u_wall=6.67,
            u_floor_other=5.27,
            u_floor_bath=5.27,
        )
        
        # number of array test
        self.assertEqual(7, len(result))
        
        # name test
        self.assertEqual('simple_general_part1', result[0]['name'])
        self.assertEqual('simple_general_part2', result[1]['name'])
        self.assertEqual('simple_general_part3', result[2]['name'])
        self.assertEqual('simple_general_part4', result[3]['name'])
        self.assertEqual('simple_general_part5', result[4]['name'])
        self.assertEqual('simple_general_part6', result[5]['name'])
        self.assertEqual('simple_general_part7', result[6]['name'])
        
        # envelope type test
        self.assertEqual('ceiling', result[0]['evlp_type'])
        self.assertEqual(   'wall', result[1]['evlp_type'])
        self.assertEqual(   'wall', result[2]['evlp_type'])
        self.assertEqual(   'wall', result[3]['evlp_type'])
        self.assertEqual(   'wall', result[4]['evlp_type'])
        self.assertEqual(  'floor', result[5]['evlp_type'])
        self.assertEqual(  'floor', result[6]['evlp_type'])
        
        # next space test
        self.assertEqual(        'outdoor', result[0]['next_space'])
        self.assertEqual(        'outdoor', result[1]['next_space'])
        self.assertEqual(        'outdoor', result[2]['next_space'])
        self.assertEqual(        'outdoor', result[3]['next_space'])
        self.assertEqual(        'outdoor', result[4]['next_space'])
        self.assertEqual('open_underfloor', result[5]['next_space'])
        self.assertEqual('open_underfloor', result[6]['next_space'])
        
        # direction test
        self.assertEqual(     'top', result[0]['direction'])
        self.assertEqual(      'sw', result[1]['direction'])
        self.assertEqual(      'nw', result[2]['direction'])
        self.assertEqual(      'ne', result[3]['direction'])
        self.assertEqual(      'se', result[4]['direction'])
        self.assertEqual('downward', result[5]['direction'])
        self.assertEqual('downward', result[6]['direction'])
            
        # area test
        self.assertEqual(50.85, result[0]['area'])
        self.assertEqual(30.47, result[1]['area'])
        self.assertEqual(22.37, result[2]['area'])
        self.assertEqual(47.92, result[3]['area'])
        self.assertEqual(22.28, result[4]['area'])
        self.assertEqual(45.05, result[5]['area'])
        self.assertEqual( 3.31, result[6]['area'])
        
        # structure test
        self.assertEqual('wood', result[0]['spec']['structure'])
        self.assertEqual('wood', result[1]['spec']['structure'])
        self.assertEqual('wood', result[2]['spec']['structure'])
        self.assertEqual('wood', result[3]['spec']['structure'])
        self.assertEqual('wood', result[4]['spec']['structure'])
        self.assertEqual('wood', result[5]['spec']['structure'])
        self.assertEqual('wood', result[6]['spec']['structure'])
        
        # u value input method
        self.assertEqual('u_value_directly', result[0]['spec']['u_value_input_method_wood'])
        self.assertEqual('u_value_directly', result[1]['spec']['u_value_input_method_wood'])
        self.assertEqual('u_value_directly', result[2]['spec']['u_value_input_method_wood'])
        self.assertEqual('u_value_directly', result[3]['spec']['u_value_input_method_wood'])
        self.assertEqual('u_value_directly', result[4]['spec']['u_value_input_method_wood'])
        self.assertEqual('u_value_directly', result[5]['spec']['u_value_input_method_wood'])
        self.assertEqual('u_value_directly', result[6]['spec']['u_value_input_method_wood'])
        
        # u value test
        self.assertEqual( 7.7, result[0]['spec']['u_value_wood'])
        self.assertEqual(6.67, result[1]['spec']['u_value_wood'])
        self.assertEqual(6.67, result[2]['spec']['u_value_wood'])
        self.assertEqual(6.67, result[3]['spec']['u_value_wood'])
        self.assertEqual(6.67, result[4]['spec']['u_value_wood'])
        self.assertEqual(5.27, result[5]['spec']['u_value_wood'])
        self.assertEqual(5.27, result[6]['spec']['u_value_wood'])
        
        # is sunshade input test
        self.assertEqual(False, result[0]['spec']['is_sunshade_input'])
        self.assertEqual(False, result[1]['spec']['is_sunshade_input'])
        self.assertEqual(False, result[2]['spec']['is_sunshade_input'])
        self.assertEqual(False, result[3]['spec']['is_sunshade_input'])
        self.assertEqual(False, result[4]['spec']['is_sunshade_input'])
        self.assertEqual(False, result[5]['spec']['is_sunshade_input'])
        self.assertEqual(False, result[6]['spec']['is_sunshade_input'])

    def test_get_general_parts_f_b(self):
        
        result = nb.get_general_parts(
            a_a=90.0,
            house_type='f_b',
            u_roof=7.7,
            u_wall=6.67,
            u_floor_other=5.27,
            u_floor_bath=5.27,
        )
        
        # number of array test
        self.assertEqual(6, len(result))
        
        # test below is skipped
        #   name test
        #   envelope type test
        #   next space test
        #   direction test
        #   structure test
        #   u value input method
        #   is sunshade input test
        
        # area test
        self.assertEqual(50.85, result[0]['area'])
        self.assertEqual(30.47, result[1]['area'])
        self.assertEqual(22.37, result[2]['area'])
        self.assertEqual(47.92, result[3]['area'])
        self.assertEqual(22.28, result[4]['area'])
        self.assertEqual(45.05, result[5]['area'])

        # u value test
        self.assertEqual( 7.7, result[0]['spec']['u_value_wood'])
        self.assertEqual(6.67, result[1]['spec']['u_value_wood'])
        self.assertEqual(6.67, result[2]['spec']['u_value_wood'])
        self.assertEqual(6.67, result[3]['spec']['u_value_wood'])
        self.assertEqual(6.67, result[4]['spec']['u_value_wood'])
        self.assertEqual(5.27, result[5]['spec']['u_value_wood'])
        
    def test_get_general_parts_f_n(self):
        
        result = nb.get_general_parts(
            a_a=90.0,
            house_type='f_n',
            u_roof=7.7,
            u_wall=6.67,
            u_floor_other=5.27,
            u_floor_bath=5.27,
        )
        
        # number of array test
        self.assertEqual(6, len(result))
        
        # test below is skipped
        #   name test
        #   envelope type test
        #   next space test
        #   direction test
        #   structure test
        #   u value input method
        #   is sunshade input test
        
        # area test
        self.assertEqual(50.85, result[0]['area'])
        self.assertEqual(30.47, result[1]['area'])
        self.assertEqual(22.37, result[2]['area'])
        self.assertEqual(47.92, result[3]['area'])
        self.assertEqual(22.28, result[4]['area'])
        self.assertEqual(48.36, result[5]['area'])

        # u value test
        self.assertEqual( 7.7, result[0]['spec']['u_value_wood'])
        self.assertEqual(6.67, result[1]['spec']['u_value_wood'])
        self.assertEqual(6.67, result[2]['spec']['u_value_wood'])
        self.assertEqual(6.67, result[3]['spec']['u_value_wood'])
        self.assertEqual(6.67, result[4]['spec']['u_value_wood'])
        self.assertEqual(5.27, result[5]['spec']['u_value_wood'])
    
    def test_get_general_parts_b(self):
        
        result = nb.get_general_parts(
            a_a=90.0,
            house_type='b',
            u_roof=7.7,
            u_wall=6.67,
            u_floor_other=5.27,
            u_floor_bath=5.27,
        )
        
        # number of array test
        self.assertEqual(5, len(result))
        
        # test below is skipped
        #   name test
        #   envelope type test
        #   next space test
        #   direction test
        #   structure test
        #   u value input method
        #   is sunshade input test
        
        # area test
        self.assertEqual(50.85, result[0]['area'])
        self.assertEqual(30.47, result[1]['area'])
        self.assertEqual(22.37, result[2]['area'])
        self.assertEqual(47.92, result[3]['area'])
        self.assertEqual(22.28, result[4]['area'])

        # u value test
        self.assertEqual( 7.7, result[0]['spec']['u_value_wood'])
        self.assertEqual(6.67, result[1]['spec']['u_value_wood'])
        self.assertEqual(6.67, result[2]['spec']['u_value_wood'])
        self.assertEqual(6.67, result[3]['spec']['u_value_wood'])
        self.assertEqual(6.67, result[4]['spec']['u_value_wood'])

    def test_get_general_parts_floor_area_conversion(self):
        
        result = nb.get_general_parts(
            a_a=120.0,
            house_type='f_f',
            u_roof=7.7,
            u_wall=6.67,
            u_floor_other=5.27,
            u_floor_bath=5.27,
        )
        
        # area test
        self.assertAlmostEqual(50.85*120.0/90.0, result[0]['area'])
        self.assertAlmostEqual(30.47*120.0/90.0, result[1]['area'])
        self.assertAlmostEqual(22.37*120.0/90.0, result[2]['area'])
        self.assertAlmostEqual(47.92*120.0/90.0, result[3]['area'])
        self.assertAlmostEqual(22.28*120.0/90.0, result[4]['area'])
        self.assertAlmostEqual(45.05*120.0/90.0, result[5]['area'])
        self.assertAlmostEqual( 3.31*120.0/90.0, result[6]['area'])
    
    def test_get_heating_overhang_width(self):
        
        # is_f_value_input == True
        
        # region 8 is error!!
        with self.assertRaises(ValueError):
            nb.get_heating_overhang_width(True, 8, 'se', 0.0, 0.0)
            
        # invalid region name is error!!
        with self.assertRaises(ValueError):
            nb.get_heating_overhang_width(True, 9, 'se', 0.0, 0.0)
        
        # f value が 0.72より大の場合は0.72と同じ結果になることの確認
        result1 = nb.get_heating_overhang_width(True, 6, 'se', 0.0, 1.1, 0.73)
        result2 = nb.get_heating_overhang_width(True, 6, 'se', 0.0, 1.1, 0.74)
        self.assertEqual(result1, result2)
        
        # f/a - b <= 0
        self.assertEqual(5.0, nb.get_heating_overhang_width(True, 6, 'se', 0.0, 1.1, 0.0))

        # value test        
        self.assertEqual(20*1.1/(0.7/0.01- 5), nb.get_heating_overhang_width(True, 6, 'se', 0.0, 1.1, 0.7))
        self.assertEqual(20*1.1/(0.7/0.01- 5), nb.get_heating_overhang_width(True, 6, 'sw', 0.0, 1.1, 0.7))
        self.assertEqual(15*1.1/(0.7/0.01-10), nb.get_heating_overhang_width(True, 6, 'nw', 0.0, 1.1, 0.7))
        self.assertEqual(15*1.1/(0.7/0.01-10), nb.get_heating_overhang_width(True, 6, 'ne', 0.0, 1.1, 0.7))
        # value test(result is over upper limit)
        self.assertEqual(5.0, nb.get_heating_overhang_width(True, 6, 'se', 0.0, 1.1, 0.06))
        
        # is_f_value_input == False
        self.assertEqual((0.0+1.1)*0.3, nb.get_heating_overhang_width(False, 6, 'se', 0.0, 1.1, 0.7))
    
    def test_get_cooling_overhang_width(self):
        
        # is_f_value_input == True
        
        # invalid region name is error!!
        with self.assertRaises(ValueError):
            nb.get_cooling_overhang_width(True, 9, 'se', 0.0, 0.0)
        
        # f value が 0.93より大の場合は0.93と同じ結果になることの確認
        result1 = nb.get_cooling_overhang_width(True, 6, 'se', 0.0, 1.1, 0.93)
        result2 = nb.get_cooling_overhang_width(True, 6, 'se', 0.0, 1.1, 0.94)
        self.assertEqual(result1, result2)
        
        # f/a - b <= 0
        self.assertEqual(5.0, nb.get_heating_overhang_width(True, 6, 'se', 0.0, 1.1, 0.0))

        # value test(region6)
        self.assertEqual(24*1.1/(0.7/0.01-16), nb.get_cooling_overhang_width(True, 6, 'se', 0.0, 1.1, 0.7))
        self.assertEqual(24*1.1/(0.7/0.01-16), nb.get_cooling_overhang_width(True, 6, 'sw', 0.0, 1.1, 0.7))
        self.assertEqual(24*1.1/(0.7/0.01-16), nb.get_cooling_overhang_width(True, 6, 'nw', 0.0, 1.1, 0.7))
        self.assertEqual(24*1.1/(0.7/0.01-16), nb.get_cooling_overhang_width(True, 6, 'ne', 0.0, 1.1, 0.7))
        # value test(region8)
        self.assertEqual(19*1.1/(0.7/0.01-16), nb.get_cooling_overhang_width(True, 8, 'se', 0.0, 1.1, 0.7))
        self.assertEqual(19*1.1/(0.7/0.01-16), nb.get_cooling_overhang_width(True, 8, 'sw', 0.0, 1.1, 0.7))
        self.assertEqual(24*1.1/(0.7/0.01-16), nb.get_cooling_overhang_width(True, 8, 'nw', 0.0, 1.1, 0.7))
        self.assertEqual(24*1.1/(0.7/0.01-16), nb.get_cooling_overhang_width(True, 8, 'ne', 0.0, 1.1, 0.7))
        # value test(result is over upper limit)
        self.assertEqual(5.0, nb.get_cooling_overhang_width(True, 6, 'se', 0.0, 1.1, 0.06))
        
        # is_f_alue_input == False
        self.assertEqual(0.0, nb.get_cooling_overhang_width(False, 6, 'se', 0.0, 1.1, 0.7))

    def test_get_y1_y2_z(self):
        
        # if_f_value_input = True
        # region8
        self.assertEqual(19*1.1/(0.7/0.01-16), nb.get_y1_y2_z(True, 8, 'se', 0.7, 0.7)[2])
        # region6
        self.assertEqual((20*1.1/(0.7/0.01- 5)+24*1.1/(0.7/0.01-16))/2, nb.get_y1_y2_z(True, 6, 'se', 0.7, 0.7)[2])
        
        # if_f_value_input = False
        # region8
        self.assertEqual(0.0, nb.get_y1_y2_z(False, 8, 'se', 0.7, 0.7)[2])
        # region6
        self.assertEqual((0.0+1.1)*0.3/2, nb.get_y1_y2_z(False, 6, 'se', 0.7, 0.7)[2])        
        
        # y1
        self.assertEqual(0.0, nb.get_y1_y2_z(True, 6, 'se', 0.7, 0.7)[0])
    
        # y2
        self.assertEqual(1.1, nb.get_y1_y2_z(True, 6, 'se', 0.7, 0.7)[1])

    def test_get_windows(self):
        
        result = nb.get_windows(
            a_a=90.0,
            region=6,
            u_window=3.49,
            eta_d_h=0.52,
            eta_d_c=0.51,
            is_f_value_input=True,
            f_h=0.7,
            f_c=0.7
        )
        
        # number of array test
        self.assertEqual(4, len(result))
        
        # name test
        self.assertEqual('simple_window_part1', result[0]['name'])
        self.assertEqual('simple_window_part2', result[1]['name'])
        self.assertEqual('simple_window_part3', result[2]['name'])
        self.assertEqual('simple_window_part4', result[3]['name'])
        
        # next space test
        self.assertEqual('outdoor', result[0]['next_space'])
        self.assertEqual('outdoor', result[1]['next_space'])
        self.assertEqual('outdoor', result[2]['next_space'])
        self.assertEqual('outdoor', result[3]['next_space'])

        # direction test
        self.assertEqual('sw', result[0]['direction'])
        self.assertEqual('nw', result[1]['direction'])
        self.assertEqual('ne', result[2]['direction'])
        self.assertEqual('se', result[3]['direction'])
        
        # area test
        self.assertEqual(22.69, result[0]['area'])
        self.assertEqual( 2.38, result[1]['area'])
        self.assertEqual( 3.63, result[2]['area'])
        self.assertEqual( 4.37, result[3]['area'])
        
        # window type test
        self.assertEqual('single', result[0]['spec']['window_type'])
        self.assertEqual('single', result[1]['spec']['window_type'])
        self.assertEqual('single', result[2]['spec']['window_type'])
        self.assertEqual('single', result[3]['spec']['window_type'])

        # u value input method test
        self.assertEqual('u_value_directly', result[0]['spec']['windows'][0]['u_value_input_method'])        
        self.assertEqual('u_value_directly', result[1]['spec']['windows'][0]['u_value_input_method'])        
        self.assertEqual('u_value_directly', result[2]['spec']['windows'][0]['u_value_input_method'])        
        self.assertEqual('u_value_directly', result[3]['spec']['windows'][0]['u_value_input_method'])        
        
        # u value test
        self.assertEqual(3.49, result[0]['spec']['windows'][0]['u_value'])
        self.assertEqual(3.49, result[1]['spec']['windows'][0]['u_value'])
        self.assertEqual(3.49, result[2]['spec']['windows'][0]['u_value'])
        self.assertEqual(3.49, result[3]['spec']['windows'][0]['u_value'])
        
        # eta d value input method test
        self.assertEqual('eta_d_value_directly', result[0]['spec']['windows'][0]['eta_d_value_input_method'])
        self.assertEqual('eta_d_value_directly', result[1]['spec']['windows'][0]['eta_d_value_input_method'])
        self.assertEqual('eta_d_value_directly', result[2]['spec']['windows'][0]['eta_d_value_input_method'])
        self.assertEqual('eta_d_value_directly', result[3]['spec']['windows'][0]['eta_d_value_input_method'])
        
        # eta d value test
        self.assertEqual(0.515, result[0]['spec']['windows'][0]['eta_d_value'])
        self.assertEqual(0.515, result[1]['spec']['windows'][0]['eta_d_value'])
        self.assertEqual(0.515, result[2]['spec']['windows'][0]['eta_d_value'])
        self.assertEqual(0.515, result[3]['spec']['windows'][0]['eta_d_value'])

        # glass type test
        self.assertEqual('single', result[0]['spec']['windows'][0]['glass_type'])
        self.assertEqual('single', result[1]['spec']['windows'][0]['glass_type'])
        self.assertEqual('single', result[2]['spec']['windows'][0]['glass_type'])
        self.assertEqual('single', result[3]['spec']['windows'][0]['glass_type'])
        
        # attachment type test
        self.assertEqual('none', result[0]['spec']['attachment_type'])
        self.assertEqual('none', result[1]['spec']['attachment_type'])
        self.assertEqual('none', result[2]['spec']['attachment_type'])
        self.assertEqual('none', result[3]['spec']['attachment_type'])
        
        # is windbreak room attached test
        self.assertEqual(False, result[0]['spec']['is_windbreak_room_attached'])
        self.assertEqual(False, result[1]['spec']['is_windbreak_room_attached'])
        self.assertEqual(False, result[2]['spec']['is_windbreak_room_attached'])
        self.assertEqual(False, result[3]['spec']['is_windbreak_room_attached'])
        
        # sunshade y1 test
        self.assertEqual(0.0, result[0]['spec']['sunshade']['y1'])
        self.assertEqual(0.0, result[1]['spec']['sunshade']['y1'])
        self.assertEqual(0.0, result[2]['spec']['sunshade']['y1'])
        self.assertEqual(0.0, result[3]['spec']['sunshade']['y1'])

        # sunshade y1 test
        self.assertEqual(1.1, result[0]['spec']['sunshade']['y2'])
        self.assertEqual(1.1, result[1]['spec']['sunshade']['y2'])
        self.assertEqual(1.1, result[2]['spec']['sunshade']['y2'])
        self.assertEqual(1.1, result[3]['spec']['sunshade']['y2'])
        
        # region6
        # in case that fH and fC = 0.7 in region 6
        z_sw = (20*1.1/(0.7/0.01- 5)+24*1.1/(0.7/0.01-16))/2
        z_nw = (15*1.1/(0.7/0.01-10)+24*1.1/(0.7/0.01-16))/2
        z_ne = (15*1.1/(0.7/0.01-10)+24*1.1/(0.7/0.01-16))/2
        z_se = (20*1.1/(0.7/0.01- 5)+24*1.1/(0.7/0.01-16))/2
        self.assertEqual(z_sw, result[0]['spec']['sunshade']['z'])
        self.assertEqual(z_nw, result[1]['spec']['sunshade']['z'])
        self.assertEqual(z_ne, result[2]['spec']['sunshade']['z'])
        self.assertEqual(z_se, result[3]['spec']['sunshade']['z'])
        
    def test_get_windows_floor_area_conversion(self):
        
        result = nb.get_windows(
            a_a=120.0,
            region=6,
            u_window=3.49,
            eta_d_h=0.52,
            eta_d_c=0.51,
            is_f_value_input=True,
            f_h=0.7,
            f_c=0.7
        )
        
        # area test
        self.assertEqual(22.69*120.0/90.0, result[0]['area'])
        self.assertEqual( 2.38*120.0/90.0, result[1]['area'])
        self.assertEqual( 3.63*120.0/90.0, result[2]['area'])
        self.assertEqual( 4.37*120.0/90.0, result[3]['area'])

    def test_get_doors(self):
        
        result = nb.get_doors(
            a_a=90.0,
            u_door=3.49
        )
        
        # number of array test
        self.assertEqual(2, len(result))
        
        # name test
        self.assertEqual('simple_door_part1', result[0]['name'])
        self.assertEqual('simple_door_part2', result[1]['name'])
        
        # next space test
        self.assertEqual('outdoor', result[0]['next_space'])
        self.assertEqual('outdoor', result[1]['next_space'])
        
        # direction test
        self.assertEqual('nw', result[0]['direction'])
        self.assertEqual('ne', result[1]['direction'])
        
        # area test
        self.assertEqual( 1.89, result[0]['area'])
        self.assertEqual( 1.62, result[1]['area'])
        
        # u value test
        self.assertEqual(3.49, result[0]['spec']['u_value'])
        self.assertEqual(3.49, result[1]['spec']['u_value'])
        
        # is sunshade input test
        self.assertEqual(False, result[0]['spec']['is_sunshade_input'])
        self.assertEqual(False, result[1]['spec']['is_sunshade_input'])

    def test_get_doors_area_conversion(self):
        
        result = nb.get_doors(
            a_a=120.0,
            u_door=3.49
        )
        
        self.assertAlmostEqual( 1.89*120.0/90.0, result[0]['area'])
        self.assertAlmostEqual( 1.62*120.0/90.0, result[1]['area'])
        
    def test_get_earthfloor_perimeters_f_f(self):
        
        result = nb.get_earthfloor_perimeters(
            a_a=90.0,
            house_type='f_f',
            psi_value_earthfloor_perimeter_entrance=1.8,
            psi_value_earthfloor_perimeter_bathroom=1.7,
            psi_value_earthfloor_perimeter_other=1.6,
        )
        
        # number of array test
        self.assertEqual(3, len(result))
        
        # name test
        self.assertEqual('simple_earthfloor_perimeter1', result[0]['name'])
        self.assertEqual('simple_earthfloor_perimeter2', result[1]['name'])
        self.assertEqual('simple_earthfloor_perimeter3', result[2]['name'])
        
        # next space test
        self.assertEqual(        'outdoor', result[0]['next_space'])
        self.assertEqual(        'outdoor', result[1]['next_space'])
        self.assertEqual('open_underfloor', result[2]['next_space'])
        
        # direction test
        self.assertEqual(   'nw', result[0]['direction'])
        self.assertEqual(   'ne', result[1]['direction'])
        self.assertEqual('other', result[2]['direction'])
            
        # length test
        self.assertEqual(1.82, result[0]['length'])
        self.assertEqual(1.37, result[1]['length'])
        self.assertEqual(3.19, result[2]['length'])

        # psi value test
        self.assertEqual(1.8, result[0]['spec']['psi_value'])
        self.assertEqual(1.8, result[1]['spec']['psi_value'])
        self.assertEqual(1.8, result[2]['spec']['psi_value'])
        
    def test_get_earthfloor_perimeters_f_b(self):
        
        result = nb.get_earthfloor_perimeters(
            a_a=90.0,
            house_type='f_b',
            psi_value_earthfloor_perimeter_entrance=1.8,
            psi_value_earthfloor_perimeter_bathroom=1.7,
            psi_value_earthfloor_perimeter_other=1.6,
        )
        
        # number of array test
        self.assertEqual(6, len(result))
        
        # name test
        self.assertEqual('simple_earthfloor_perimeter1', result[0]['name'])
        self.assertEqual('simple_earthfloor_perimeter2', result[1]['name'])
        self.assertEqual('simple_earthfloor_perimeter3', result[2]['name'])
        self.assertEqual('simple_earthfloor_perimeter4', result[3]['name'])
        self.assertEqual('simple_earthfloor_perimeter5', result[4]['name'])
        self.assertEqual('simple_earthfloor_perimeter6', result[5]['name'])
        
        # next space test
        self.assertEqual(        'outdoor', result[0]['next_space'])
        self.assertEqual(        'outdoor', result[1]['next_space'])
        self.assertEqual('open_underfloor', result[2]['next_space'])
        self.assertEqual(        'outdoor', result[3]['next_space'])
        self.assertEqual(        'outdoor', result[4]['next_space'])
        self.assertEqual('open_underfloor', result[5]['next_space'])
        
        # direction test
        self.assertEqual(   'nw', result[0]['direction'])
        self.assertEqual(   'ne', result[1]['direction'])
        self.assertEqual('other', result[2]['direction'])
        self.assertEqual(   'nw', result[3]['direction'])
        self.assertEqual(   'ne', result[4]['direction'])
        self.assertEqual('other', result[5]['direction'])
            
        # length test
        self.assertEqual(1.82, result[0]['length'])
        self.assertEqual(1.37, result[1]['length'])
        self.assertEqual(3.19, result[2]['length'])
        self.assertEqual(1.82, result[3]['length'])
        self.assertEqual(1.82, result[4]['length'])
        self.assertEqual(3.64, result[5]['length'])

        # psi value test
        self.assertEqual(1.8, result[0]['spec']['psi_value'])
        self.assertEqual(1.8, result[1]['spec']['psi_value'])
        self.assertEqual(1.8, result[2]['spec']['psi_value'])
        self.assertEqual(1.7, result[3]['spec']['psi_value'])
        self.assertEqual(1.7, result[4]['spec']['psi_value'])
        self.assertEqual(1.7, result[5]['spec']['psi_value'])

    def test_get_earthfloor_perimeters_f_n(self):
        
        result = nb.get_earthfloor_perimeters(
            a_a=90.0,
            house_type='f_f',
            psi_value_earthfloor_perimeter_entrance=1.8,
            psi_value_earthfloor_perimeter_bathroom=1.7,
            psi_value_earthfloor_perimeter_other=1.6,
        )
        
        # number of array test
        self.assertEqual(3, len(result))
        
        # name test
        self.assertEqual('simple_earthfloor_perimeter1', result[0]['name'])
        self.assertEqual('simple_earthfloor_perimeter2', result[1]['name'])
        self.assertEqual('simple_earthfloor_perimeter3', result[2]['name'])
        
        # next space test
        self.assertEqual(        'outdoor', result[0]['next_space'])
        self.assertEqual(        'outdoor', result[1]['next_space'])
        self.assertEqual('open_underfloor', result[2]['next_space'])
        
        # direction test
        self.assertEqual(   'nw', result[0]['direction'])
        self.assertEqual(   'ne', result[1]['direction'])
        self.assertEqual('other', result[2]['direction'])
            
        # length test
        self.assertEqual(1.82, result[0]['length'])
        self.assertEqual(1.37, result[1]['length'])
        self.assertEqual(3.19, result[2]['length'])

        # psi value test
        self.assertEqual(1.8, result[0]['spec']['psi_value'])
        self.assertEqual(1.8, result[1]['spec']['psi_value'])
        self.assertEqual(1.8, result[2]['spec']['psi_value'])

    def test_get_earthfloor_perimeters_b(self):
        
        result = nb.get_earthfloor_perimeters(
            a_a=90.0,
            house_type='b',
            psi_value_earthfloor_perimeter_entrance=1.8,
            psi_value_earthfloor_perimeter_bathroom=1.7,
            psi_value_earthfloor_perimeter_other=1.6,
        )
        
        # number of array test
        self.assertEqual(8, len(result))
        
        # name test
        self.assertEqual('simple_earthfloor_perimeter1', result[0]['name'])
        self.assertEqual('simple_earthfloor_perimeter2', result[1]['name'])
        self.assertEqual('simple_earthfloor_perimeter3', result[2]['name'])
        self.assertEqual('simple_earthfloor_perimeter4', result[3]['name'])
        self.assertEqual('simple_earthfloor_perimeter5', result[4]['name'])
        self.assertEqual('simple_earthfloor_perimeter6', result[5]['name'])
        self.assertEqual('simple_earthfloor_perimeter7', result[6]['name'])
        self.assertEqual('simple_earthfloor_perimeter8', result[7]['name'])
        
        # next space test
        self.assertEqual('outdoor', result[0]['next_space'])
        self.assertEqual('outdoor', result[1]['next_space'])
        self.assertEqual('outdoor', result[2]['next_space'])
        self.assertEqual('outdoor', result[3]['next_space'])
        self.assertEqual('outdoor', result[4]['next_space'])
        self.assertEqual('outdoor', result[5]['next_space'])
        self.assertEqual('outdoor', result[6]['next_space'])
        self.assertEqual('outdoor', result[7]['next_space'])
        
        # direction test
        self.assertEqual('nw', result[0]['direction'])
        self.assertEqual('ne', result[1]['direction'])
        self.assertEqual('nw', result[2]['direction'])
        self.assertEqual('ne', result[3]['direction'])
        self.assertEqual('sw', result[4]['direction'])
        self.assertEqual('nw', result[5]['direction'])
        self.assertEqual('ne', result[6]['direction'])
        self.assertEqual('se', result[7]['direction'])
            
        # length test
        self.assertEqual( 1.82, result[0]['length'])
        self.assertEqual( 1.37, result[1]['length'])
        self.assertEqual( 1.82, result[2]['length'])
        self.assertEqual( 1.82, result[3]['length'])
        self.assertEqual(10.61, result[4]['length'])
        self.assertEqual( 1.15, result[5]['length'])
        self.assertEqual( 7.42, result[6]['length'])
        self.assertEqual( 4.79, result[7]['length'])

        # psi value test
        self.assertEqual(1.8, result[0]['spec']['psi_value'])
        self.assertEqual(1.8, result[1]['spec']['psi_value'])
        self.assertEqual(1.7, result[2]['spec']['psi_value'])
        self.assertEqual(1.7, result[3]['spec']['psi_value'])
        self.assertEqual(1.6, result[4]['spec']['psi_value'])
        self.assertEqual(1.6, result[5]['spec']['psi_value'])
        self.assertEqual(1.6, result[6]['spec']['psi_value'])
        self.assertEqual(1.6, result[7]['spec']['psi_value'])

    def test_area_conversion_test_f_f(self):

        result = nb.get_earthfloor_perimeters(
            a_a=120.0,
            house_type='f_f',
            psi_value_earthfloor_perimeter_entrance=1.8,
            psi_value_earthfloor_perimeter_bathroom=1.7,
            psi_value_earthfloor_perimeter_other=1.6,
        )
        
        self.assertAlmostEqual( 1.82*120.0/90.0, result[0]['length'], 5)
        self.assertAlmostEqual( 1.37*120.0/90.0, result[1]['length'], 5)
        self.assertAlmostEqual( 3.19*120.0/90.0, result[2]['length'], 5)

    def test_area_conversion_test_f_b(self):

        result = nb.get_earthfloor_perimeters(
            a_a=120.0,
            house_type='f_b',
            psi_value_earthfloor_perimeter_entrance=1.8,
            psi_value_earthfloor_perimeter_bathroom=1.7,
            psi_value_earthfloor_perimeter_other=1.6,
        )
        
        self.assertAlmostEqual( 1.82*120.0/90.0, result[0]['length'], 5)
        self.assertAlmostEqual( 1.37*120.0/90.0, result[1]['length'], 5)
        self.assertAlmostEqual( 3.19*120.0/90.0, result[2]['length'], 5)
        self.assertAlmostEqual( 1.82*120.0/90.0, result[3]['length'], 5)
        self.assertAlmostEqual( 1.82*120.0/90.0, result[4]['length'], 5)
        self.assertAlmostEqual( 3.64*120.0/90.0, result[5]['length'], 5)

    def test_area_conversion_test_f_n(self):

        result = nb.get_earthfloor_perimeters(
            a_a=120.0,
            house_type='f_n',
            psi_value_earthfloor_perimeter_entrance=1.8,
            psi_value_earthfloor_perimeter_bathroom=1.7,
            psi_value_earthfloor_perimeter_other=1.6,
        )
        
        self.assertAlmostEqual( 1.82*120.0/90.0, result[0]['length'], 5)
        self.assertAlmostEqual( 1.37*120.0/90.0, result[1]['length'], 5)
        self.assertAlmostEqual( 3.19*120.0/90.0, result[2]['length'], 5)

    def test_area_conversion_test_b(self):

        result = nb.get_earthfloor_perimeters(
            a_a=120.0,
            house_type='b',
            psi_value_earthfloor_perimeter_entrance=1.8,
            psi_value_earthfloor_perimeter_bathroom=1.7,
            psi_value_earthfloor_perimeter_other=1.6,
        )
        
        self.assertAlmostEqual( 1.82*120.0/90.0, result[0]['length'], 5)
        self.assertAlmostEqual( 1.37*120.0/90.0, result[1]['length'], 5)
        self.assertAlmostEqual( 1.82*120.0/90.0, result[2]['length'], 5)
        self.assertAlmostEqual( 1.82*120.0/90.0, result[3]['length'], 5)
        self.assertAlmostEqual(10.61*120.0/90.0, result[4]['length'], 5)
        self.assertAlmostEqual( 1.15*120.0/90.0, result[5]['length'], 5)
        self.assertAlmostEqual( 7.42*120.0/90.0, result[6]['length'], 5)
        self.assertAlmostEqual( 4.79*120.0/90.0, result[7]['length'], 5)

    def test_get_earthfloor_centers_f_f(self):
        
        result = nb.get_earthfloor_centers(
            total_floor_area = 90.0,
            house_type = 'f_f',
        )
        
        # number of array test
        self.assertEqual(1, len(result))
        
        # name test
        self.assertEqual('simple_earthfloor_center1', result[0]['name'])
        
        # area test
        self.assertEqual( 2.48, result[0]['area'])

    def test_get_earthfloor_centers_f_b(self):
        
        result = nb.get_earthfloor_centers(
            total_floor_area = 90.0,
            house_type = 'f_b',
        )
        
        # number of array test
        self.assertEqual(2, len(result))
        
        # name test
        self.assertEqual('simple_earthfloor_center1', result[0]['name'])
        self.assertEqual('simple_earthfloor_center2', result[1]['name'])
        
        # area test
        self.assertEqual( 2.48, result[0]['area'])
        self.assertEqual( 3.31, result[1]['area'])

    def test_get_earthfloor_centers_f_n(self):
        
        result = nb.get_earthfloor_centers(
            total_floor_area = 90.0,
            house_type = 'f_n',
        )
        
        # number of array test
        self.assertEqual(1, len(result))
        
        # name test
        self.assertEqual('simple_earthfloor_center1', result[0]['name'])
        
        # area test
        self.assertEqual( 2.48, result[0]['area'])

    def test_get_earthfloor_centers_b(self):
        
        result = nb.get_earthfloor_centers(
            total_floor_area = 90.0,
            house_type = 'b',
        )
        
        # number of array test
        self.assertEqual(3, len(result))
        
        # name test
        self.assertEqual('simple_earthfloor_center1', result[0]['name'])
        self.assertEqual('simple_earthfloor_center2', result[1]['name'])
        self.assertEqual('simple_earthfloor_center3', result[2]['name'])
        
        # area test
        self.assertEqual( 2.48, result[0]['area'])
        self.assertEqual( 3.31, result[1]['area'])
        self.assertEqual(45.05, result[2]['area'])

    # tests below is skipped
    #   test_earthfloor_centers_area_conversion_test_f_f
    #   test_earthfloor_centers_area_conversion_test_f_b
    #   test_earthfloor_centers_area_conversion_test_f_n

    def test_earthfloor_centers_area_conversion_test_b(self):

        result = nb.get_earthfloor_centers(
            total_floor_area = 120.0,
            house_type = 'b',
        )
        
        self.assertAlmostEqual( 2.48*120.0/90.0, result[0]['area'], 5)
        self.assertAlmostEqual( 3.31*120.0/90.0, result[1]['area'], 5)
        self.assertAlmostEqual(45.05*120.0/90.0, result[2]['area'], 5)

    def test_convert(self):
        ## 実行時エラーにならないことを確認 ##
        d = {
                'common' : {
                        'region' : 6,
                        'total_floor_area': 120.0,
                        },
                'envelope' : {
                        'simple_method' : {
                                'insulation_type' : 'floor',
                                'insulation_type_bathroom' : 'floor',
                                'u_value_roof' : 7.7,
                                'u_value_wall' : 6.67,
                                'u_value_floor_other' : 5.27,
                                'u_value_floor_bathroom' : 5.27,
                                'u_value_door' : 4.65,
                                'u_value_window'    : 3.49,
                                'eta_d_value_window_c' : 0.51,       
                                'eta_d_value_window_h' : 0.51, 
                                'is_f_value_input' : True, 
                                'f_value_c' : 0.9,
                                'f_value_h' : 0.7,
                                'psi_value_earthfloor_perimeter_entrance' : 1.8,
                                'psi_value_earthfloor_perimeter_bathroom' : 1.8,
                                }
                        }
                
        }
        nb.convert(d)    


if __name__ == '__main__':
    unittest.main()