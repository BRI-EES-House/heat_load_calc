import matplotlib
from matplotlib.testing.decorators import image_comparison
import math
import unittest
import nbimporter
import Appl as nb

class TestAppl(unittest.TestCase):

    #指定した時刻の機器発熱量を取得
    def test_Appl(self):
        ap = nb.Appl()
        self.assertEqual(0.0, ap.Appl('主たる居室','','平日','顕熱',23))
        self.assertEqual(0.0, ap.Appl('主たる居室','','平日','顕熱',23))
    
if __name__ == '__main__':
    unittest.main()