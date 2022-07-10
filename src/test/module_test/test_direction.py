import unittest
import math

from heat_load_calc.direction import Direction


class TestDirection(unittest.TestCase):

    def test_alpha_w_j(self):

        self.assertEqual(Direction('s').alpha_w_j, math.radians(0.0))
        self.assertEqual(Direction('sw').alpha_w_j, math.radians(45.0))
        self.assertEqual(Direction('w').alpha_w_j, math.radians(90.0))
        self.assertEqual(Direction('nw').alpha_w_j, math.radians(135.0))
        self.assertEqual(Direction('n').alpha_w_j, math.radians(180.0))
        self.assertEqual(Direction('ne').alpha_w_j, math.radians(-135.0))
        self.assertEqual(Direction('e').alpha_w_j, math.radians(-90.0))
        self.assertEqual(Direction('se').alpha_w_j, math.radians(-45.0))

        with self.assertRaises(KeyError):
            _ = Direction('top').alpha_w_j
            _ = Direction('bottom').alpha_w_j

    def test_beta_w_j(self):

        self.assertEqual(Direction('s').beta_w_j, math.radians(90.0))
        self.assertEqual(Direction('sw').beta_w_j, math.radians(90.0))
        self.assertEqual(Direction('w').beta_w_j, math.radians(90.0))
        self.assertEqual(Direction('nw').beta_w_j, math.radians(90.0))
        self.assertEqual(Direction('n').beta_w_j, math.radians(90.0))
        self.assertEqual(Direction('ne').beta_w_j, math.radians(90.0))
        self.assertEqual(Direction('e').beta_w_j, math.radians(90.0))
        self.assertEqual(Direction('se').beta_w_j, math.radians(90.0))
        self.assertEqual(Direction('top').beta_w_j, math.radians(0.0))
        self.assertEqual(Direction('bottom').beta_w_j, math.radians(180.0))
