import unittest

from heat_load_calc.convert import general_functions as gf


class TestRoundNumber(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        print('\n testing convert general functions')

    def test_round_number(self):

        self.assertEqual(-0.348, gf.round_num(-0.347500, 3))
        self.assertEqual(-0.347, gf.round_num(-0.347499, 3))
        self.assertEqual(0.348, gf.round_num(0.347500, 3))


if __name__ == '__main__':
    unittest.main()
