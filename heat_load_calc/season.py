from typing import Dict, Tuple, Optional
from datetime import datetime
import numpy as np
from enum import Enum

class Season:

    def __init__(self, d: Dict):

        pass


def get_bool_list_for_four_season_as_str(
        summer_start: str, summer_end: str, winter_start: str, winter_end: str, is_summer_period_set: bool = True, is_winter_period_set: bool = True
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:

    summer, winter, middle = _get_bool_list_for_four_season_as_int(
        summer_start=_get_total_day(date_str=summer_start),
        summer_end=_get_total_day(date_str=summer_end),
        winter_start=_get_total_day(winter_start),
        winter_end=_get_total_day(winter_end),
        is_summer_period_set=is_summer_period_set,
        is_winter_period_set=is_winter_period_set
    )

    return summer, winter, middle


def _get_bool_list_for_four_season_as_int(
        summer_start: Optional[int] = None,
        summer_end: Optional[int] = None,
        winter_start: Optional[int] = None,
        winter_end: Optional[int] = None,
        is_summer_period_set: Optional[bool] = True,
        is_winter_period_set: Optional[bool] = True
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:

    if is_summer_period_set:
        summer_list = _get_bool_list_by_start_day_and_end_day(nstart=summer_start, nend=summer_end)
    else:
        summer_list = np.full(shape=365, fill_value=False, dtype=bool)

    if is_winter_period_set:
        winter_list = _get_bool_list_by_start_day_and_end_day(nstart=winter_start, nend=winter_end)
    else:
        winter_list = np.full(shape=365, fill_value=False, dtype=bool)

    if np.any(summer_list & winter_list) == True:
        raise ValueError("The summer period and the winter period are duplicated.")

    middle_list = (~summer_list) & (~winter_list)

    return summer_list, winter_list, middle_list


def _get_bool_list_by_start_day_and_end_day(nstart: int, nend: int) -> np.ndarray:
    """make the list as numpy which length is 365 as boolean value.

    nstart is the day of the year which starts the operation.
    nend is the end of the year which ends the operation.

    When nstart value is less than and equal to nend value, the value between nstart and nend becomes True, and the other value is False.
    For example nstart is 100 and nend is 200, the value from 99 to 199 of the index are True.
    (The specified value starts 1, but the index of numpy list starts 0.)

    When nstart value is more than nend value, the value more than and equal to start value is True, and
    the value less than and equal to end value is True.
    For example nstart is 200 and nend is 100, the value from 1 to 99 and from 199 to 365 of the index are True.

    Args:
        nstart (int): the number of the start day of the year for some heating and cooling operation.
        nend (int): the number of the end day of the year for some heating and cooling operation.

    Returns:
        np.ndarray: the list of 365 as boolean.
    """

    if nstart <= nend:
        return _get_bool_list_by_start_day(n=nstart) & _get_bool_list_by_end_day(n=nend)
    else:
        return _get_bool_list_by_start_day(n=nstart) | _get_bool_list_by_end_day(n=nend)


def _get_total_day(date_str: str) -> int:
    """convert the date as string to the number of the day from January 1st.

    Args:
        date (str): date

    Note:
        "1/1" -> 1
        "1/2" -> 2
        "1/31" -> 31
        "2/1" -> 32
        "12/31" -> 365

        The number of the day of a year is 365.   
    """

    # base year
    # 2021 is used. Leap year should not used.
    base_year = 2021

    date = datetime.strptime(f"{base_year}/{date_str}", "%Y/%m/%d")
    
    start_of_year = datetime(base_year, 1, 1)

    n_day = (date - start_of_year).days + 1

    return n_day


def _get_bool_list_by_start_day(n: int) -> np.ndarray:

    _check_day_index(n)

    return np.arange(365) >= n - 1


def _get_bool_list_by_end_day(n: int) -> np.ndarray:

    _check_day_index(n)

    return np.arange(365) <= n - 1


def _check_day_index(n: int):
    """check the number is specified between 1 and 365.

    Args:
        n (int): the number of the date of the year (1 ~ 365)

    """

    if n > 365:
        raise IndexError("Over 365 can't be specified.")
    
    if n < 1:
        raise IndexError("Under 1 cna't be specified.")
