import matplotlib
from matplotlib.testing.decorators import image_comparison
import math
import unittest
import nbimporter
import Wall 
from Wall import Layer

class TestLayer(unittest.TestCase):

    def test_name(self):
        target = Layer('PlasterBoard', 0.22, 830.0, 0.012)
        self.assertEqual('PlasterBoard', target.name)
    
    def test_dblLam(self):
        target = Layer('PlasterBoard', 0.22, 830.0, 0.012)
        self.assertEqual(0.22, target.dblLam())
    
    def test_dblSpcheat(self):
        target = Layer('PlasterBoard', 0.22, 830.0, 0.012)
        self.assertEqual(830.0 * 1000, target.dblSpcheat())
    
    def test_dblDim(self):
        target = Layer('PlasterBoard', 0.22, 830.0, 0.012)
        self.assertEqual(0.012, target.dblDim())
    
    def test_dblR_under_1mm(self):
        target = Layer('PlasterBoard', 0.22, 830.0, 0.00099)
        self.assertEqual(1 / 0.22, target.dblR())
    
    def test_dblR_over_1mm(self):
        target = Layer('PlasterBoard', 0.22, 830.0, 0.001)
        self.assertEqual(0.001 / 0.22, target.dblR())

    def test_dblC(self):
        target = Layer('PlasterBoard', 0.22, 830.0, 0.012)
        self.assertEqual(830.0 * 1000 * 0.012, target.dblC())
