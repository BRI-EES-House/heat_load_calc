import matplotlib
from matplotlib.testing.decorators import image_comparison
import math
import unittest
import nbimporter
import WallMng 
from WallMng import WallMng

class TestWallMng(unittest.TestCase):

    def test_properties(self):
        d = {
            'Common': {
                'Region': 6,
                'TimeInterval': 3600,
                'ResponseFactorCalculationHours': 50
            },
            'Walls': [
                {
                    'Name': 'Ceiling',
                    'Layers': [
                        {'Name': 'GW16K', 'Cond': 0.045, 'Thick': 0.0, 'SpecH': 13.0},
                        {'Name': 'GPB', 'Cond': 0.22, 'Thick': 0.0095, 'SpecH': 830.0}
                    ],
        #            'OutHeatTrans' : 25.0,
                    'OutEmissiv' : 0.90,
                    'OutSolarAbs' : 0.80,
                    'InConHeatTrans' : 6.10,
                    'InRadHeatTrans' : 5.00
                },
                {
                    'Name': 'Wall_SW',
                    'Layers': [
                        {'Name': 'GW16K', 'Cond': 0.045, 'Thick': 0.0, 'SpecH': 13.0},
                        {'Name': 'GPB', 'Cond': 0.22, 'Thick': 0.0095, 'SpecH': 830.0}
                    ],
        #            'OutHeatTrans' : 25.0,
                    'OutEmissiv' : 0.90,
                    'OutSolarAbs' : 0.80,
                    'InConHeatTrans' : 4.10,
                    'InRadHeatTrans' : 5.00
                }
            ]
        }

        target = WallMng( d )

        #室内側伝達率の取得
        self.assertEqual(11.10, target.hi('Ceiling'))

        #室内側対流熱伝達率の取得
        self.assertEqual(6.10, target.hic('Ceiling'))

        #室内側放射熱伝達率
        self.assertEqual(5.00, target.hir('Ceiling'))

        #室外側熱伝達率
        self.assertEqual(0.22, target.ho('Ceiling'))

        #室外側放射率
        self.assertEqual(0.90, target.Eo('Ceiling'))

        #室外側日射吸収率
        self.assertEqual(0.80, target.Solas('Wall_SW'))
    
    def test_no_errors(self):
        d = {
            'Common': {
                'Region': 6,
                'TimeInterval': 3600,
                'ResponseFactorCalculationHours': 50
            },
            'Walls': [
                {
                    'Name': 'Ceiling',
                    'Layers': [
                        {'Name': 'GW16K', 'Cond': 0.045, 'Thick': 0.0, 'SpecH': 13.0},
                        {'Name': 'GPB', 'Cond': 0.22, 'Thick': 0.0095, 'SpecH': 830.0}
                    ],
        #            'OutHeatTrans' : 25.0,
                    'OutEmissiv' : 0.90,
                    'OutSolarAbs' : 0.80,
                    'InConHeatTrans' : 6.10,
                    'InRadHeatTrans' : 5.00
                },
                {
                    'Name': 'Wall_SW',
                    'Layers': [
                        {'Name': 'GW16K', 'Cond': 0.045, 'Thick': 0.0, 'SpecH': 13.0},
                        {'Name': 'GPB', 'Cond': 0.22, 'Thick': 0.0095, 'SpecH': 830.0}
                    ],
        #            'OutHeatTrans' : 25.0,
                    'OutEmissiv' : 0.90,
                    'OutSolarAbs' : 0.80,
                    'InConHeatTrans' : 4.10,
                    'InRadHeatTrans' : 5.00
                }
            ]
        }

        target = WallMng( d )

        target.RFT('Ceiling')
        target.RFA('Ceiling')
        target.Row('Ceiling')
        target.RFT1('Ceiling')
        target.RFA1('Ceiling')
        target.RFT0('Ceiling')
        target.RFA0('Ceiling')
        target.Nroot('Ceiling')
