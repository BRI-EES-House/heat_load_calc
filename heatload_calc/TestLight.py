import matplotlib
from matplotlib.testing.decorators import image_comparison
import math
import unittest
import nbimporter
import Light as nb

class TestLight(unittest.TestCase):

    #指定した時刻の照明発熱量を取得
    def test_Appl(self):
        li = nb.Light()
        self.assertEqual(0.0, li.Light('非居室','','平日',23))
    
if __name__ == '__main__':
    unittest.main()