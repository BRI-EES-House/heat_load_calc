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
        

if __name__ == '__main__':
    unittest.main()
    