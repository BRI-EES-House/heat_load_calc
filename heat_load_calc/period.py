from typing import Tuple, Dict

from heat_load_calc import interval


N_D_MAIN_DEFAULT = 365              # 365 days
N_D_RUN_UP_DEFAULT = 365            # 365 days
N_D_RUN_UP_BUILD_DEFAULT = 183      # 183 days


def get_n_step(d_common: Dict, itv: interval.Interval) -> Tuple[int, int, int]:
    """Calculate the number of steps for calculation based on the calculation days.

    Args:
        d_common: common dictionary
        itv: time interval

    Returns:
        (1) number of steps for main calculation
        (2) number of steps for run-up calculation
        (3) number of steps to calculate the building in the run-up calculation
    """

    if 'calculation_day' in d_common:
        
        d_common_calculation_day = d_common['calculation_day']
        
        if 'main' in d_common_calculation_day:
            n_d_main = int(d_common_calculation_day['main'])
        else:
            n_d_main = N_D_MAIN_DEFAULT
        
        if 'run_up' in d_common_calculation_day:
            n_d_run_up = int(d_common_calculation_day['run_up'])
        else:
            n_d_run_up = N_D_RUN_UP_DEFAULT
        
        if 'run_up_building' in d_common_calculation_day:
            n_d_run_up_build = int(d_common_calculation_day['run_up_building'])
        else:
            n_d_run_up_build = N_D_RUN_UP_BUILD_DEFAULT
    
    else:
        n_d_main = N_D_MAIN_DEFAULT
        n_d_run_up =N_D_RUN_UP_DEFAULT
        n_d_run_up_build = N_D_RUN_UP_BUILD_DEFAULT

    # check the value n_d_main
    if n_d_main > 365:
        raise ValueError('The identified number of the calculation day should not be more than 365.')
    
    # check the value n_d_run_up
    if n_d_run_up > 365:
        raise ValueError('THe identified number of the run-up calculation day should not be more than 365.')

    # n_d_run_up must not be less than n_d_run_up_build.
    if n_d_run_up < n_d_run_up_build:
        raise ValueError('n_d_run_up should be more than or equal to n_d_run_up_build.')

    # number of steps divideing hour / 1時間を分割するステップ数
    n_hour = itv.get_n_hour()

    # number of steps for main calculation
    n_step_main = _get_n_step_main(n_hour=n_hour, n_d_main=n_d_main)

    # number of steps for run-up calculation
    n_step_run_up = _get_n_step_run_up(n_hour=n_hour, n_d_run_up=n_d_run_up)

    # number of steps to calculate building in the run-up calculation
    n_step_run_up_build = _get_n_step_run_up_build(n_hour=n_hour, n_d_run_up_build=n_d_run_up_build)

    return n_step_main, n_step_run_up, n_step_run_up_build


def _get_n_step_main(n_hour: int, n_d_main: int) -> int:
    """calculate the number of steps for main calculation

    Args:
        n_hour: number of steps in 1 hour
        n_d_main: number of days for main calculation, d

    Returns:
        number of steps for main calculation
    """

    return n_d_main * n_hour * 24


def _get_n_step_run_up(n_hour: int, n_d_run_up: int) -> int:
    """calculate the number of steps for run-up calculation

    Args:
        n_hour: number of steps in 1 hour
        n_d_run_up: number of days for main calculation, d

    Returns:
        number of steps for run-up calculation
    """

    return n_d_run_up * n_hour * 24


def _get_n_step_run_up_build(n_hour: int, n_d_run_up_build: int) -> int:
    """calculate the number of steps to calculate buildging in the run-up calculation

    Args:
        n_hour: number of steps in 1 hour
        n_d_run_up_build: number of days to calculate building in the run-up calculation, d
    
    Returns:
        number of steps to calculate building in the run-up calculation
    """

    return n_d_run_up_build * n_hour * 24

