import matplotlib
from matplotlib.testing.decorators import image_comparison
import math
import unittest
import nbimporter
import EnergySave as nb

class TestEnergySave(unittest.TestCase):

    def get_target(self):
        d = {
            'EnergySave': {
                'IsUseVentilation' : True,
                'AirChangeRate'    : 5.0,
                'IsUseHeatStorage' : False,
                'IsUseHEXVent'     : True
            }
        }
        energysave = nb.EnergySave(d)
        return energysave

    #通風の換気回数を取得
    def test_VentRate(self):
        energysave = self.get_target()
        self.assertEqual(5.0, energysave.VentRate())

    #蓄熱の有無を取得
    def test_Storage(self):
        energysave = self.get_target()
        self.assertEqual(False, energysave.Storage())

    #熱交換換気有無を取得
    def test_HexVent(self):
        energysave = self.get_target()
        self.assertEqual(True, energysave.HexVent())
    
if __name__ == '__main__':
    unittest.main()