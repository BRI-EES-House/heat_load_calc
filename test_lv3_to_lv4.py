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
                    'space_type' : 'main_occupant_room',
                    'area'       : 55.5,
                    'direction'  : 'bottom',
                },
                {
                    'space_type' : 'other_occupant_room',
                    'area'       : 15.2,
                    'direction'  : 'downward',
                },
                {
                    'space_type' : 'non_occupant_room',
                    'area'       : 55.5,
                    'direction'  : 'top',
                },
            ]
        }
        
        result1_mr, result1_or, result1_nr = nb.get_earthfloor_total_area(envelope1)
        
        self.assertEqual(55.5, result1_mr)
        self.assertEqual(15.2, result1_or)
        self.assertEqual(55.5, result1_nr)
        
        # in case that ther is no earthfloor 
        
        envelope2 = {}
        
        result2_mr, result2_or, result2_nr = nb.get_earthfloor_total_area(envelope2)
        
        self.assertEqual(0.0, result2_mr)
        self.assertEqual(0.0, result2_or)
        self.assertEqual(0.0, result2_nr)
        
if __name__ == '__main__':
    unittest.main()
    