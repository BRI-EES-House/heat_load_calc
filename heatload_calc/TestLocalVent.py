import matplotlib
from matplotlib.testing.decorators import image_comparison
import math
import unittest
import nbimporter
import LocalVent as nb

class TestLocalVent(unittest.TestCase):

    #指定した時刻の局所換気量を取得
    def test_Appl(self):
        ve = nb.LocalVent()
        self.assertEqual(0.0, ve.Vent('主たる居室','','平日',23))
    
if __name__ == '__main__':
    unittest.main()