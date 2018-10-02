import matplotlib
from matplotlib.testing.decorators import image_comparison
import math
import unittest
import nbimporter
import Layer as nb

class TestLayer(unittest.TestCase):

    def test_layer(self):
        m = nb.Layer( 'GPB', 0.0095, 0.22, 830 )
        self.assertEqual('GPB', m.name)
        self.assertEqual(0.0095, m.thick)
        self.assertEqual(0.22, m.cond)
        self.assertEqual(830, m.spech)
        self.assertAlmostEqual(0.04318, m.R(), delta=0.0001)
    
if __name__ == '__main__':
    unittest.main()