import unittest
import pytest

from heat_load_calc import interval
from heat_load_calc.interval import Interval


class TestInterval(unittest.TestCase):

    def test_get_n_hour(self):

        self.assertEqual(4, Interval.M15.get_n_hour())
        self.assertEqual(2, Interval.M30.get_n_hour())
        self.assertEqual(1, Interval.H1.get_n_hour())

    def test_get_time(self):

        self.assertEqual(0.25, Interval.M15.get_delta_h())
        self.assertEqual(0.5, Interval.M30.get_delta_h())
        self.assertEqual(1.0, Interval.H1.get_delta_h())

    def test_get_delta_t(self):

        self.assertEqual(900, Interval.M15.get_delta_t())
        self.assertEqual(1800, Interval.M30.get_delta_t())
        self.assertEqual(3600, Interval.H1.get_delta_t())

    def test_get_annual_number(self):

        self.assertEqual(8760*4, Interval.M15.get_n_step_annual())
        self.assertEqual(8760*2, Interval.M30.get_n_step_annual())
        self.assertEqual(8760*1, Interval.H1.get_n_step_annual())

    def test_get_pandas_freq(self):

        self.assertEqual('15min', Interval.M15.get_pandas_freq())
        self.assertEqual('30min', Interval.M30.get_pandas_freq())
        self.assertEqual('h', Interval.H1.get_pandas_freq())
    
    def test_set_interval(self):

        itv = interval.set_interval(d_common={'interval': '1h'})
        self.assertEqual(itv, Interval.H1)
    
        itv = interval.set_interval(d_common={'interval': '30m'})
        self.assertEqual(itv, Interval.M30)

        itv = interval.set_interval(d_common={'interval': '15m'})
        self.assertEqual(itv, Interval.M15)

        itv = interval.set_interval(d_common={})
        self.assertEqual(itv, Interval.M15)
    
    def test_set_interval_read_error_wrong_item(self):

        with pytest.raises(ValueError):
            _ = interval.set_interval(d_common={'interval': '20min'})
            
