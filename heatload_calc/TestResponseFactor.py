import matplotlib
from matplotlib.testing.decorators import image_comparison
import math
import unittest
import nbimporter
import Wall
from Wall import Layer, Wall, ResponseFactor

class TestResponseFactor(unittest.TestCase):

    def test_init(self):
        """作成できることだけ確認"""
        layers =[
            Layer( 'Plywood', 0.16, 720.0, 0.022 ),
            Layer( 'GW16K', 0.045, 13.0, 0.150 ),
        ]
        wall = Wall( '1F_floor', 0.90, 0.80, 1.70, 5.00, layers )
        rf = ResponseFactor('wall', 3600, 50, wall)

        rf.StepRespOfWall()
        rf.RFTRI()
        rf.ATstep()
        rf.AAstep()
        rf.RFT()
        rf.RFA()
        rf.Row()
        rf.RFT1()
        rf.RFA1()
        rf.RFT0()
        rf.RFA0()
        rf.Alp()
    
    def test_Wall(self):
        layers =[
            Layer( 'Plywood', 0.16, 720.0, 0.022 ),
            Layer( 'GW16K', 0.045, 13.0, 0.150 ),
        ]
        wall = Wall( '1F_floor', 0.90, 0.80, 1.70, 5.00, layers )
        rf = ResponseFactor('wall', 3600, 50, wall)
        self.assertEqual('1F_floor', rf.Wall().Name())







        
