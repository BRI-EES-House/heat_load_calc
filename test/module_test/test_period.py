import unittest

from heat_load_calc.interval import EInterval, Interval
from heat_load_calc import period
from heat_load_calc.input_models.input_calculation_day import InputCalculationDay


class TestPeriod(unittest.TestCase):

    def test_15m(self):

        d_calculation_day={
            'main': 365,
            'run_up': 180,
            'run_up_building': 30
        }

        n_step_main, n_step_run_up, n_step_run_up_build = period.get_n_step(
            itv=Interval(eitv=EInterval.M15),
            ipt_calculation_day=InputCalculationDay.read(d_calculation_day=d_calculation_day)
        )

        self.assertEqual(365*4*24, n_step_main)
        self.assertEqual(180*4*24, n_step_run_up)
        self.assertEqual(30*4*24, n_step_run_up_build)

    def test_30m(self):

        d_calculation_day={
            'main': 365,
            'run_up': 180,
            'run_up_building': 30
        }

        n_step_main, n_step_run_up, n_step_run_up_build = period.get_n_step(
            itv=Interval(eitv=EInterval.M30),
            ipt_calculation_day=InputCalculationDay.read(d_calculation_day=d_calculation_day)
        )

        self.assertEqual(365*2*24, n_step_main)
        self.assertEqual(180*2*24, n_step_run_up)
        self.assertEqual(30*2*24, n_step_run_up_build)

    def test_1h(self):

        d_calculation_day={
            'main': 365,
            'run_up': 180,
            'run_up_building': 30
        }

        n_step_main, n_step_run_up, n_step_run_up_build = period.get_n_step(
            itv=Interval(eitv=EInterval.H1),
            ipt_calculation_day=InputCalculationDay.read(d_calculation_day=d_calculation_day)
        )

        self.assertEqual(365*24, n_step_main)
        self.assertEqual(180*24, n_step_run_up)
        self.assertEqual(30*24, n_step_run_up_build)
    
    def test_default_value(self):

        n_step_main, n_step_run_up, n_step_run_up_build = period.get_n_step(
            itv=Interval(eitv=EInterval.H1),
            ipt_calculation_day=None
        )

        self.assertEqual(365*24, n_step_main)
        self.assertEqual(365*24, n_step_run_up)
        self.assertEqual(183*24, n_step_run_up_build)
        

