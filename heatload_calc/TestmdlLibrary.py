import matplotlib
from matplotlib.testing.decorators import image_comparison
import math
import datetime
import unittest
import nbimporter
import mdlLibrary as nb

class TestmdlLibrary(unittest.TestCase):

    #当該日の通日を計算する関数
    def test_Nday(self):
        self.assertEqual(2, nb.Nday(datetime.datetime.strptime('2017/01/02 12:00:00', '%Y/%m/%d %H:%M:%S')))
        self.assertEqual(214, nb.Nday(datetime.datetime.strptime('08月02日', '%m月%d日')))
    
if __name__ == '__main__':
    unittest.main()