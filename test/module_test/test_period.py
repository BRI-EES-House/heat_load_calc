import unittest

from heat_load_calc.interval import Interval
from heat_load_calc import period


class TestPeriod(unittest.TestCase):

    def test_15m(self):

        n_step_main, n_step_run_up, n_step_run_up_build = period.get_n_step(
            d_common={
                'calculation_day':{
                    'main': 365,
                    'run_up': 180,
                    'run_up_building': 30
                }
            },
            itv=Interval.M15
        )

        self.assertEqual(365*4*24, n_step_main)
        self.assertEqual(180*4*24, n_step_run_up)
        self.assertEqual(30*4*24, n_step_run_up_build)

    def test_30m(self):

        n_step_main, n_step_run_up, n_step_run_up_build = period.get_n_step(
            d_common={
                'calculation_day':{
                    'main': 365,
                    'run_up': 180,
                    'run_up_building': 30
                }
            },
            itv=Interval.M30
        )

        self.assertEqual(365*2*24, n_step_main)
        self.assertEqual(180*2*24, n_step_run_up)
        self.assertEqual(30*2*24, n_step_run_up_build)

    def test_1h(self):

        n_step_main, n_step_run_up, n_step_run_up_build = period.get_n_step(
            d_common={
                'calculation_day':{
                    'main': 365,
                    'run_up': 180,
                    'run_up_building': 30
                }
            },
            itv=Interval.H1
        )

        self.assertEqual(365*24, n_step_main)
        self.assertEqual(180*24, n_step_run_up)
        self.assertEqual(30*24, n_step_run_up_build)
    
    def test_default_value(self):

        n_step_main, n_step_run_up, n_step_run_up_build = period.get_n_step(
            d_common={},
            itv=Interval.H1
        )

        self.assertEqual(365*24, n_step_main)
        self.assertEqual(365*24, n_step_run_up)
        self.assertEqual(183*24, n_step_run_up_build)
        
    def test_default_value_calculation_days(self):

        n_step_main, n_step_run_up, n_step_run_up_build = period.get_n_step(
            d_common={
                'calculation_days':{}
            },
            itv=Interval.H1
        )

        self.assertEqual(365*24, n_step_main)
        self.assertEqual(365*24, n_step_run_up)
        self.assertEqual(183*24, n_step_run_up_build)

    def test_run_up_check(self):

        with self.assertRaises(ValueError):
            _, _, _ = period.get_n_step(
                d_common={
                    'calculation_day':{
                        'main': 365,
                        'run_up': 30,
                        'run_up_building': 180
                    }
                },
                itv=Interval.H1
            )
