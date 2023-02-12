import unittest

from heat_load_calc.interval import Interval
from heat_load_calc import period


class TestPeriod(unittest.TestCase):

    def test_15m(self):

        n_step_main, n_step_run_up, n_step_run_up_build = period.get_n_step(
            n_d_main=365, n_d_run_up=180, n_d_run_up_build=30, itv=Interval.M15
        )

        self.assertEqual(365*4*24, n_step_main)
        self.assertEqual(180*4*24, n_step_run_up)
        self.assertEqual(30*4*24, n_step_run_up_build)

    def test_30m(self):

        n_step_main, n_step_run_up, n_step_run_up_build = period.get_n_step(
            n_d_main=365, n_d_run_up=180, n_d_run_up_build=30, itv=Interval.M30
        )

        self.assertEqual(365*2*24, n_step_main)
        self.assertEqual(180*2*24, n_step_run_up)
        self.assertEqual(30*2*24, n_step_run_up_build)

    def test_1h(self):

        n_step_main, n_step_run_up, n_step_run_up_build = period.get_n_step(
            n_d_main=365, n_d_run_up=180, n_d_run_up_build=30, itv=Interval.H1
        )

        self.assertEqual(365*24, n_step_main)
        self.assertEqual(180*24, n_step_run_up)
        self.assertEqual(30*24, n_step_run_up_build)

    def test_run_up_check(self):

        with self.assertRaises(ValueError):
            _, _, _ = period.get_n_step(
                n_d_main=365, n_d_run_up=30, n_d_run_up_build=180, itv=Interval.H1
            )
