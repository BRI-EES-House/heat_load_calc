import matplotlib
from matplotlib.testing.decorators import image_comparison
import math
import unittest
import nbimporter
import Resi as nb

class TestResi(unittest.TestCase):

    #指定した時刻の在室人員数を取得
    def test_Nresi(self):
        re = nb.Resi()
        self.assertEqual(0, re.Nresi('主たる居室','','平日',23))
    
if __name__ == '__main__':
    unittest.main()