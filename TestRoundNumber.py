import matplotlib
from matplotlib.testing.decorators import image_comparison
import math
import unittest
import nbimporter
import RoundNumber as nb

class TestRoundNumber(unittest.TestCase):

    def test_round_number(self):
        self.assertEqual(-0.348, nb.round_number(-0.347500, 3))
        self.assertEqual(-0.347, nb.round_number(-0.347499, 3))
        self.assertEqual(0.348, nb.round_number(0.347500, 3))
    
if __name__ == '__main__':
    unittest.main()