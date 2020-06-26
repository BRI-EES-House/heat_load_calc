import matplotlib
from matplotlib.testing.decorators import image_comparison
import math
import unittest
import nbimporter
import AnnualCal as nb

class TestAnnualCal(unittest.TestCase):

    #曜日の取得
    def test_Week(self):
        cal = nb.AnnualCal()
        self.assertEqual('平日', cal.Week(10))

    #運転モードの取得
    def test_Season(self):
        cal = nb.AnnualCal()
        self.assertEqual('暖房', cal.Season(10))
    
if __name__ == '__main__':
    unittest.main()