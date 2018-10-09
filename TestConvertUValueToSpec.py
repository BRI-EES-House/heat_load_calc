import matplotlib
from matplotlib.testing.decorators import image_comparison
import math
import unittest
import nbimporter
import ConvertUValueToSpec as nb
from RoundNumber import round_number

class TestConvertUValueToSpec(unittest.TestCase):

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

if __name__ == '__main__':
    unittest.main()