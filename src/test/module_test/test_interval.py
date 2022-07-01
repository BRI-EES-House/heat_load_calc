import unittest

from heat_load_calc.interval import Interval


class TestInterval(unittest.TestCase):

    def test_get_n_hour(self):

        self.assertEqual(4, Interval.M15.get_n_hour())
        self.assertEqual(2, Interval.M30.get_n_hour())
        self.assertEqual(1, Interval.H1.get_n_hour())

    def test_get_time(self):

        self.assertEqual(0.25, Interval.M15.get_time())
        self.assertEqual(0.5, Interval.M30.get_time())
        self.assertEqual(1.0, Interval.H1.get_time())

    def test_get_annual_number(self):

        self.assertEqual(8760*4, Interval.M15.get_annual_number())
        self.assertEqual(8760*2, Interval.M30.get_annual_number())
        self.assertEqual(8760*1, Interval.H1.get_annual_number())

    def test_get_pandas_freq(self):

        self.assertEqual('15min', Interval.M15.get_pandas_freq())
        self.assertEqual('30min', Interval.M30.get_pandas_freq())
        self.assertEqual('H', Interval.H1.get_pandas_freq())

