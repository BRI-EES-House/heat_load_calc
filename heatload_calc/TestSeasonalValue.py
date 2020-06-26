import matplotlib
from matplotlib.testing.decorators import image_comparison
import math
import datetime
import unittest
import nbimporter
import SeasonalValue as nb

class TestSeasonalValue(unittest.TestCase):

    #冬期の特性値
    def test_winter(self):
        target = nb.SeasonalValue(1,2,3)
        self.assertEqual(1, target.winter())

    #中間期の特性値
    def test_winter(self):
        target = nb.SeasonalValue(1,2,3)
        self.assertEqual(2, target.inter())

    #夏期の特性値
    def test_summer(self):
        target = nb.SeasonalValue(1,2,3)
        self.assertEqual(3, target.summer())
    
if __name__ == '__main__':
    unittest.main()