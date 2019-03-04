import unittest
import nbimporter
import lv3_to_lv4 as nb

class TestLV3toLV4(unittest.TestCase):

    def test_get_inner_floor_spec(self):
        
        result = nb.get_inner_floor_spec()
        
        # number of array test
        self.assertEqual(1, len(result['layers']))
        
        layer0 = result['layers'][0]

        # name test
        self.assertEqual('plywood', layer0['name'])
        
        # thermal resistance input method test
        self.assertEqual('conductivity', layer0['thermal_resistance_input_method'])
        
        # thermal conductivity test
        self.assertEqual(0.16, layer0['thermal_conductivity'])
        
        # volumetric specific heat test
        self.assertEqual(720.0, layer0['volumetric_specific_heat'])

        # thickness test
        self.assertEqual(0.024, layer0['thickness'])
    
    def test_get_downward_envelope_total_area(self):
        
        # direction test
        
        envelope1 = {
            'general_parts' : [
                {
                    'space_type' : 'main_occupant_room',
                    'area'       : 55.5,
                    'direction'  : 'bottom',
                },
                {
                    'space_type' : 'main_occupant_room',
                    'area'       : 15.2,
                    'direction'  : 'downward',
                },
                {
                    'space_type' : 'main_occupant_room',
                    'area'       : 55.5,
                    'direction'  : 'top',
                },
                {
                    'space_type' : 'other_occupant_room',
                    'area'       : 44.4,
                    'direction'  : 'bottom',
                },
                {
                    'space_type' : 'other_occupant_room',
                    'area'       : 14.1,
                    'direction'  : 'downward',
                },
                {
                    'space_type' : 'other_occupant_room',
                    'area'       : 44.4,
                    'direction'  : 'top',
                },
                {
                    'space_type' : 'non_occupant_room',
                    'area'       : 33.3,
                    'direction'  : 'bottom',
                },
                {
                    'space_type' : 'non_occupant_room',
                    'area'       : 13.1,
                    'direction'  : 'downward',
                },
                {
                    'space_type' : 'non_occupant_room',
                    'area'       : 33.3,
                    'direction'  : 'top',
                },
            ]
        }
        
        result1_mr, result1_or, result1_nr = nb.get_downward_envelope_total_area(envelope1)
        
        self.assertEqual(70.7, result1_mr)
        self.assertEqual(58.5, result1_or)
        self.assertEqual(46.4, result1_nr)
        
        # envelope type included test
        
        envelope2 = {
            'general_parts' : [
                {
                    'space_type' : 'main_occupant_room',
                    'area'       : 55.5,
                    'direction'  : 'bottom',
                }
            ],
            'windows' : [
                {
                    'space_type' : 'main_occupant_room',
                    'area'       : 5.5,
                    'direction'  : 'bottom',
                }
            ],
            'doors' : [
                {
                    'space_type' : 'main_occupant_room',
                    'area'       : 4.4,
                    'direction'  : 'bottom',
                }
            ],
        }
        
        result2_mr, result2_or, result2_nr = nb.get_downward_envelope_total_area(envelope2)
        
        self.assertEqual(65.4, result2_mr)
        self.assertEqual(0.0, result2_or)
        self.assertEqual(0.0, result2_nr)

    def test_get_earthfloor_total_area(self):
        
        envelope1 = {
            'earthfloor_centers' : [
                {
                    'name'       : 'ec1',
                    'area'       : 55.5,
                    'space_type' : 'main_occupant_room',
                },
                {
                    'name'       : 'ec2',
                    'area'       : 44.4,
                    'space_type' : 'other_occupant_room',
                },
                {
                    'name'       : 'ec3',
                    'area'       : 33.3,
                    'space_type' : 'non_occupant_room',
                },
                {
                    'name'       : 'ec4',
                    'area'       : 22.2,
                    'space_type' : 'underfloor',
                },
                {
                    'name'       : 'ec5',
                    'area'       : 5.5,
                    'space_type' : 'main_occupant_room',
                },
                {
                    'name'       : 'ec6',
                    'area'       : 4.4,
                    'space_type' : 'other_occupant_room',
                },
                {
                    'name'       : 'ec7',
                    'area'       : 3.3,
                    'space_type' : 'non_occupant_room',
                },
                {
                    'name'       : 'ec8',
                    'area'       : 2.2,
                    'space_type' : 'underfloor',
                },
            ]
        }
        
        result1_mr, result1_or, result1_nr, result1_uf = nb.get_earthfloor_total_area(envelope1)
        
        self.assertEqual(55.5+5.5, result1_mr)
        self.assertEqual(44.4+4.4, result1_or)
        self.assertEqual(33.3+3.3, result1_nr)
        self.assertEqual(22.2+2.2, result1_uf)
        
        # in case that ther is no earthfloor 
        
        envelope2 = {}
        
        result2_mr, result2_or, result2_nr, result2_uf = nb.get_earthfloor_total_area(envelope2)
        
        self.assertEqual(0.0, result2_mr)
        self.assertEqual(0.0, result2_or)
        self.assertEqual(0.0, result2_nr)
        self.assertEqual(0.0, result2_uf)

    def test_get_inner_floor_total_area(self):
        
        # 答えが0より大の場合
        result1_mr, result1_or, result1_nr = nb.get_inner_floor_total_area(
                a_a=120.0, a_mr=50.0, a_or=40.0,
                a_evlp_down_mr=20.0, a_evlp_down_or=15.0, a_evlp_down_nr=10.0,
                a_ef_mr=7.0, a_ef_or=6.0, a_ef_nr=4.0)
        
        self.assertEqual(23.0, result1_mr)
        self.assertEqual(19.0, result1_or)
        self.assertEqual(16.0, result1_nr)
        
        # 答えが0より小の場合
        result2_mr, result2_or, result2_nr = nb.get_inner_floor_total_area(
                a_a=120.0, a_mr=50.0, a_or=40.0,
                a_evlp_down_mr=80.0, a_evlp_down_or=60.0, a_evlp_down_nr=40.0,
                a_ef_mr=50.0, a_ef_or=6.0, a_ef_nr=4.0)
        
        self.assertEqual(0.0, result2_mr)
        self.assertEqual(0.0, result2_or)
        self.assertEqual(0.0, result2_nr)
    
    def test_get_inner_floor_over_underfloor_total_area(self):
        
        # a_if_mr + a_if_or + a_if_nr > 0.0 の場合
        result1_mr, result1_or, result1_nr = nb.get_inner_floor_over_underfloor_total_area(
                a_if_mr=25.0, a_if_or=15.0, a_if_nr=10.0, a_ef_uf=30.0)
        
        self.assertEqual(15.0, result1_mr)
        self.assertEqual(9.0, result1_or)
        self.assertEqual(6.0, result1_nr)
        
        # a_if_mr + a_if_or + a_if_nr > 0.0 の場合
        result2_mr, result2_or, result2_nr = nb.get_inner_floor_over_underfloor_total_area(
                a_if_mr=25.0, a_if_or=15.0, a_if_nr=10.0, a_ef_uf=0.0)
        
        self.assertEqual(0.0, result2_mr)
        self.assertEqual(0.0, result2_or)
        self.assertEqual(0.0, result2_nr)

        # a_if_mr + a_if_or + a_if_nr > 0.0 の場合
        result3_mr, result3_or, result3_nr = nb.get_inner_floor_over_underfloor_total_area(
                a_if_mr=0.0, a_if_or=0.0, a_if_nr=0.0, a_ef_uf=30.0)
        
        self.assertEqual(0.0, result3_mr)
        self.assertEqual(0.0, result3_or)
        self.assertEqual(0.0, result3_nr)
    
    def test_get_inner_floor_between_rooms(self):
        
        # その他の居室と非居室の床面積の合計がともに0の場合
        a_if_mr_or1, a_if_mr_nr1, a_if_or_mr1, a_if_or_nr1, a_if_nr_mr1, a_if_nr_or1 \
        = nb.get_inner_floor_between_rooms(a_mr=120.0, a_or=0.0, a_a=120.0,
                                           a_if_mr=35.0, a_if_or=30.0, a_if_nr=25.0,
                                           a_if_mr_uf=8.0, a_if_or_uf=7.0, a_if_nr_uf=6.0)
        
        self.assertEqual(0.0, a_if_mr_or1)
        self.assertEqual(0.0, a_if_mr_nr1)
        self.assertEqual(0.0, a_if_or_mr1)
        self.assertEqual(0.0, a_if_or_nr1)
        self.assertEqual(0.0, a_if_nr_mr1)
        self.assertEqual(0.0, a_if_nr_or1)

        # その他の居室の床面積の合計が0で、非居室の床面積の合計が0ではない場合
        a_if_mr_or2, a_if_mr_nr2, a_if_or_mr2, a_if_or_nr2, a_if_nr_mr2, a_if_nr_or2 \
        = nb.get_inner_floor_between_rooms(a_mr=30.0, a_or=0.0, a_a=120.0,
                                           a_if_mr=35.0, a_if_or=30.0, a_if_nr=25.0,
                                           a_if_mr_uf=8.0, a_if_or_uf=7.0, a_if_nr_uf=6.0)
        
        self.assertEqual( 0.0, a_if_mr_or2)
        self.assertEqual(27.0, a_if_mr_nr2)
        self.assertEqual( 0.0, a_if_or_mr2)
        self.assertEqual( 0.0, a_if_or_nr2)
        self.assertEqual(19.0, a_if_nr_mr2)
        self.assertEqual( 0.0, a_if_nr_or2)

        # その他の居室の床面積の合計が0でなく、非居室の床面積の合計が0の場合
        a_if_mr_or3, a_if_mr_nr3, a_if_or_mr3, a_if_or_nr3, a_if_nr_mr3, a_if_nr_or3 \
        = nb.get_inner_floor_between_rooms(a_mr=30.0, a_or=90.0, a_a=120.0,
                                           a_if_mr=35.0, a_if_or=30.0, a_if_nr=25.0,
                                           a_if_mr_uf=8.0, a_if_or_uf=7.0, a_if_nr_uf=6.0)
        
        self.assertEqual(27.0, a_if_mr_or3)
        self.assertEqual( 0.0, a_if_mr_nr3)
        self.assertEqual(23.0, a_if_or_mr3)
        self.assertEqual( 0.0, a_if_or_nr3)
        self.assertEqual( 0.0, a_if_nr_mr3)
        self.assertEqual( 0.0, a_if_nr_or3)

        # その他の居室、非居室の床面積の合計がともに0ではない場合
        a_if_mr_or3, a_if_mr_nr3, a_if_or_mr3, a_if_or_nr3, a_if_nr_mr3, a_if_nr_or3 \
        = nb.get_inner_floor_between_rooms(a_mr=30.0, a_or=60.0, a_a=120.0,
                                           a_if_mr=35.0, a_if_or=30.0, a_if_nr=25.0,
                                           a_if_mr_uf=8.0, a_if_or_uf=7.0, a_if_nr_uf=6.0)
        
        self.assertEqual(13.5, a_if_mr_or3)
        self.assertEqual(13.5, a_if_mr_nr3)
        self.assertEqual(11.5, a_if_or_mr3)
        self.assertEqual(11.5, a_if_or_nr3)
        self.assertEqual( 9.5, a_if_nr_mr3)
        self.assertEqual( 9.5, a_if_nr_or3)

if __name__ == '__main__':
    unittest.main()
    