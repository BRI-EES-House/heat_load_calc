import matplotlib
from matplotlib.testing.decorators import image_comparison
import unittest
import nbimporter
import LV1toLV2 as nb

class TestLV1toLV2(unittest.TestCase):

    def test_round_number(self):
        result = nb.round_number(-0.347500, 3)
        self.assertEqual(-0.348, result)

if __name__ == '__main__':
    unittest.main()