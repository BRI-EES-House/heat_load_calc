import matplotlib
from matplotlib.testing.decorators import image_comparison
import math
import unittest
import nbimporter
import Wall
from Wall import Wall, Layer

class TestWall(unittest.TestCase):

    def test_Name(self):
        """名前が正しく保持されることの確認"""
        target = Wall( '1F_floor', 0.90, 0.80, 1.70, 5.00, [] )
        self.assertEqual('1F_floor', target.Name())

    def test_hi(self):
        """室内側伝達率 = 室内側対流熱伝達率 + 室内側放射熱伝達率 であることの確認"""
        target = Wall( '1F_floor', 0.90, 0.80, 1.70, 5.00, [] )
        self.assertEqual(1.70 + 5.00, target.hi())
    
    def test_hic(self):
        """室内側対流伝達率が正しく保持されることの確認"""
        target = Wall( '1F_floor', 0.90, 0.80, 1.70, 5.00, [] )
        self.assertEqual(1.70, target.hic())
    
    def test_hir(self):
        """室内側放射熱伝達率が正しく保持されることの確認"""
        target = Wall( '1F_floor', 0.90, 0.80, 1.70, 5.00, [] )
        self.assertEqual(5.00, target.hir())

    def test_ho(self):
        """室外側熱伝達率 = 最も外側のレイヤーの熱伝達率 であることの確認"""
        target = Wall( '1F_floor', 0.90, 0.80, 1.70, 5.00, [ \
                Layer( 'Plywood', 0.16, 720.0, 0.022 ), \
                Layer( 'GW16K', 0.045, 13.0, 0.150 ), \
                Layer( 'Ro', 25.0, 0.0, 0.0) \
            ])
        self.assertEqual(25.0, target.ho())

    def test_Eo(self):
        """室外側放射率が正しく保持されることの確認"""
        target = Wall( '1F_floor', 0.90, 0.80, 1.70, 5.00, [] )
        self.assertEqual(0.90, target.Eo())

    def test_Solas(self):
        """室外側日射吸収率が正しく保持されることの確認"""
        target = Wall( '1F_floor', 0.90, 0.80, 1.70, 5.00, [] )
        self.assertEqual(0.80, target.Solas())

    def test_Layers(self):
        target = Wall( '1F_floor', 0.90, 0.80, 1.70, 5.00, [ \
                Layer( 'Plywood', 0.16, 720.0, 0.022 ), \
                Layer( 'GW16K', 0.045, 13.0, 0.150 ), \
                Layer( 'Ro', 25.0, 0.0, 0.0) \
            ])
        layers = target.Layers()
        self.assertEqual(3, len(layers))
        self.assertEqual('Plywood', layers[0].name)
        self.assertEqual(0.150, layers[1].dblDim())

    def test_lngNLayer(self):
        target = Wall( '1F_floor', 0.90, 0.80, 1.70, 5.00, [ \
                Layer( 'Plywood', 0.16, 720.0, 0.022 ), \
                Layer( 'GW16K', 0.045, 13.0, 0.150 ), \
                Layer( 'Ro', 25.0, 0.0, 0.0) \
            ])
        self.assertEqual(3, target.lngNlayer())
