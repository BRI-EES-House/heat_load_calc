import unittest
import pytest

from heat_load_calc import interval
from heat_load_calc.interval import EInterval, Interval


class TestInterval(unittest.TestCase):

    def test_get_n_hour(self):

        self.assertEqual(4, Interval(eitv=EInterval.M15).get_n_hour())
        self.assertEqual(2, Interval(eitv=EInterval.M30).get_n_hour())
        self.assertEqual(1, Interval(eitv=EInterval.H1).get_n_hour())

    def test_get_time(self):

        self.assertEqual(0.25, Interval(eitv=EInterval.M15).get_delta_h())
        self.assertEqual(0.5, Interval(eitv=EInterval.M30).get_delta_h())
        self.assertEqual(1.0, Interval(eitv=EInterval.H1).get_delta_h())

    def test_get_delta_t(self):

        self.assertEqual(900, Interval(eitv=EInterval.M15).get_delta_t())
        self.assertEqual(1800, Interval(eitv=EInterval.M30).get_delta_t())
        self.assertEqual(3600, Interval(eitv=EInterval.H1).get_delta_t())

    def test_get_annual_number(self):

        self.assertEqual(8760*4, Interval(eitv=EInterval.M15).get_n_step_annual())
        self.assertEqual(8760*2, Interval(eitv=EInterval.M30).get_n_step_annual())
        self.assertEqual(8760*1, Interval(eitv=EInterval.H1).get_n_step_annual())

    def test_get_pandas_freq(self):

        self.assertEqual('15min', Interval(eitv=EInterval.M15).get_pandas_freq())
        self.assertEqual('30min', Interval(eitv=EInterval.M30).get_pandas_freq())
        self.assertEqual('h', Interval(eitv=EInterval.H1).get_pandas_freq())
    
