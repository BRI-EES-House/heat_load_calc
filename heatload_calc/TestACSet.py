import matplotlib
from matplotlib.testing.decorators import image_comparison
import math
import unittest
import nbimporter
import ACSet as nb

class TestACSet(unittest.TestCase):

    def test_ACSet(self):
        ac = nb.ACSet()
        temp = ac.ACSet('主たる居室','','冷房','平日','温度', 23)
        self.assertEqual(27, temp)
    
if __name__ == '__main__':
    unittest.main()