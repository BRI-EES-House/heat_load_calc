from typing import Dict, Tuple, Optional
from datetime import datetime
import numpy as np
import pandas as pd

from heat_load_calc import region
from heat_load_calc import weather

class Season:

    def __init__(self, summer: np.ndarray, winter: np.ndarray, middle: np.ndarray):

        self._summer = summer
        self._winter = winter
        self._middle = middle
    
    @property
    def summer(self):
        return self._summer
    
    @property
    def winter(self):
        return self._winter
    
    @property
    def middle(self):
        return self._middle


def make_season(d_common: Dict, w: weather.Weather):
    """make season class

    Args:
        d_common: The item 'common' tag of the input file.
    """

    summer_start, summer_end, winter_start, winter_end, is_summer_period_set, is_winter_period_set = _get_season_status(d_common=d_common, w=w)

    summer, winter, middle = _get_bool_list_for_season_as_str(
        summer_start=summer_start,
        summer_end=summer_end,
        winter_start=winter_start,
        winter_end=winter_end,
        is_summer_period_set=is_summer_period_set,
        is_winter_period_set=is_winter_period_set
    )

    return Season(summer=summer, winter=winter, middle=middle)


def _get_season_status(d_common: Dict, w: weather.Weather | None = None) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], bool, bool]:
    """get season status

    Args:
        d_common: common tag in input file.
        w: Weather class. Defaults to None.

    Returns:
        - The date the summer begins.
        - The date the summer ends.
        - The date the winter begins.
        - The date the winter ends.
        - Is the summer period specified ?
        - Is the winter period specified ?
    
    Notes:
        If the summer period set, the date the summer begins and the date the summer ends should be defined.
        If the sinter period set, the date the winter begins and the date the sinter ends should be defined.
    """

    # Check the existance of the item season in common item.
    if 'season' in d_common:
        
        # item 'season'
        d_season = d_common['season']

        # Check the existance of the item "is_summer_period_set" in season item.
        if 'is_summer_period_set' not in d_season:
            raise KeyError('Key is_summer_period_set could not be found')

        is_summer_period_set = d_season['is_summer_period_set']

        # Check the existance of the item "is_winter_period_set" in season item.
        if 'is_winter_period_set' not in d_season:
            raise KeyError('Key is_winter_period_set could not be found')
        
        is_winter_period_set = d_season['is_winter_period_set']
        
        if is_summer_period_set:
            summer_start = d_season['summer_start']
            summer_end = d_season['summer_end']
        else:
            summer_start = None
            summer_end = None
        
        if is_winter_period_set:
            winter_start = d_season['winter_start']
            winter_end = d_season['winter_end']
        else:
            winter_start = None
            winter_end = None

        return summer_start, summer_end, winter_start, winter_end, is_summer_period_set, is_winter_period_set

    # If tag 'season' is not defined, the season status are decided as follows.
    # In case that the method is 'ees', these status depends on the region.
    # In case that the method is 'file', these status are decided depending on the outside air temperature analyzed bassed on Fourier analysis.
    else:

        # Check the existance of the item 'weather' in common item.
        if 'weather' not in d_common:
            raise KeyError('Key weather could not be found in common tag.')
    
        # item 'weather'
        d_weather = d_common['weather']

        # Check the existance of the item  'method' in weather item.
        if 'method' not in d_weather:
            raise KeyError('Key method could not be found in weather tag.')

        # item 'method'
        d_method = d_weather['method']

        # The method "ees" is the method that the weather data is loaded from the pre set data based on the region of the Japanese Energy Efficiency Standard.
        # And the season of heating(winter) and cooling(summer) are desided depends on the region.
        if d_method == 'ees':

            # Check the existance of the item "region" in weather item.
            if 'region' not in d_weather:
                raise KeyError('Key region should be specified if the ees method applied.')
        
            # item 'region'
            r = region.Region(int(d_weather['region']))

            summer_start, summer_end, winter_start, winter_end, is_summer_period_set, is_winter_period_set = r.get_season_status()

            return summer_start, summer_end, winter_start, winter_end, is_summer_period_set, is_winter_period_set
        
        # The method "file" is the method that the weather data is loaded from the file specified by user.
        # If the method "file" is specified, the season are automatically calculated based on the outdoor air temperature,
        # which is replaced to the simplified sin/cos curve througy the Fourier tranform method.
        elif d_method == 'file':

            if w is None:

                raise ValueError('Argument as Weather class is not defined. Weather should be defined when using file method in making season period.')

            else:

                return _get_season_status_by_fourier_tranform(w=w)
        
        else:

            raise ValueError('Invalid value is specified for the method.')


def _get_bool_list_for_season_as_str(
        summer_start: Optional[str] = None,
        summer_end: Optional[str] = None,
        winter_start: Optional[str] = None,
        winter_end: Optional[str] = None,
        is_summer_period_set: Optional[bool] = True,
        is_winter_period_set: Optional[bool] = True
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """get the bool list of summer, winter and middle season

    Returns:
        - Bool array for summer season.
        - Bool array for winter season.
        - Bool array for middle season.
        Every array length is 365.
    """

    if is_summer_period_set:
        if (summer_start is None) or (summer_end is None):
            raise ValueError('If summer period is set, both summer_start and summer_end should be set.')
        else:
            summer_start_num, summer_end_num = _get_total_day(date_str=summer_start), _get_total_day(date_str=summer_end)
    else:
        summer_start_num, summer_end_num = None, None
    
    if is_winter_period_set:
        if (winter_start is None) or (winter_end is None):
            raise ValueError('If winter period is set, both winter_start and winter_end should be set.')
        else:
            winter_start_num, winter_end_num = _get_total_day(date_str=winter_start), _get_total_day(date_str=winter_end)
    else:
        winter_start_num, winter_end_num = None, None

    summer, winter, middle = _get_bool_list_for_four_season_as_int(
        summer_start=summer_start_num,
        summer_end=summer_end_num,
        winter_start=winter_start_num,
        winter_end=winter_end_num,
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
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:

    if is_summer_period_set:
        if (summer_start is None) or (summer_end is None):
            raise ValueError('If summer period is set, both summer_start and summer_end should be set.')
        else:
            summer_list = _get_bool_list_by_start_day_and_end_day(nstart=summer_start, nend=summer_end)
    else:
        summer_list = np.full(shape=365, fill_value=False, dtype=bool)

    if is_winter_period_set:
        if (winter_start is None) or (winter_end is None):
            raise ValueError('If winter period is set, both winter_start and winter_end should be set.')
        else:
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


def _get_season_status_by_fourier_tranform(w: weather.Weather) -> tuple[str | None, str | None, str | None, str | None, bool, bool]:
    """Calculate the summer and winter season by the outdoor temperature.

    Args:
        w: Weather class.

    Returns:
        Tuple data consists of six parameters as follows.
        - summer start date
        - summer end date
        - winter start date
        - winter end date
        - is summer period set?
        - is winter period set?
    """
    # Outside temperatures, degree C, [N+1]
    theta_o_array = np.array(w.theta_o_ns_plus[np.arange(len(w.theta_o_ns_plus)) % 4 == 0])

    # インデックス用の日時データを生成
    start_time = pd.Timestamp("1989-01-01 00:00")
    date_index = pd.date_range(start=start_time, periods=8761, freq="H")
    df = pd.DataFrame({'theta_o': theta_o_array}, index=date_index)
    
    # 日平均外気温度、日最高外気温度の計算
    df_daily = pd.DataFrame(
        index=pd.date_range(start=start_time, periods=365, freq="D"),
        columns=['theta_o_average', 'theta_o_max', 'theta_o_average_fft', 'theta_o_max_fft']
        )
    theta_o_average = df['theta_o'].resample('D').mean().to_numpy()[:-1]
    theta_o_max = df['theta_o'].resample('D').max().to_numpy()[:-1]
    df_daily['theta_o_average'] = theta_o_average
    df_daily['theta_o_max'] = theta_o_max

    n_samples = len(theta_o_average)
    sample_freq = 1
    frequencies = np.fft.fftfreq(n_samples, d=sample_freq)

    # フーリエ変換
    fft_result_average = np.fft.fft(theta_o_average)
    fft_result_max = np.fft.fft(theta_o_max)

    # 年周期成分 (1/365 周期/日) のインデックスを取得
    target_frequency = 1 / 365  # 周波数
    frequency_tolerance = 1e-6  # 周波数の誤差許容範囲
    filtered_fft_average = np.zeros_like(fft_result_average)
    filtered_fft_max = np.zeros_like(fft_result_max)

    # 年周期成分に対応する周波数をフィルタリング
    for i, freq in enumerate(frequencies):
        if np.abs(freq - target_frequency) < frequency_tolerance or np.abs(freq + target_frequency) < frequency_tolerance:
            filtered_fft_average[i] = fft_result_average[i]
            filtered_fft_max[i] = fft_result_max[i]

    # 直流成分（平均値）を加える
    filtered_fft_average[0] = fft_result_average[0]
    filtered_fft_max[0] = fft_result_max[0]

    # 逆フーリエ変換でフィルタ後のデータを取得
    theta_o_average_fft = np.fft.ifft(filtered_fft_average).real
    theta_o_max_fft = np.fft.ifft(filtered_fft_max).real
    df_daily['theta_o_average_fft'] = theta_o_average_fft
    df_daily['theta_o_max_fft'] = theta_o_max_fft

    # 暖房日、冷房日配列の作成
    df_daily['is_heating_day'] = theta_o_average_fft < 15.0
    df_daily['is_cooling_day'] = theta_o_max_fft > 24.0
    summer_start, summer_end = _find_first_and_last_true_days_with_special_conditions(df_daily, 'is_heating_day')
    winter_start, winter_end = _find_first_and_last_true_days_with_special_conditions(df_daily, 'is_cooling_day')

    return (
        summer_start.strftime("%m/%d")  if not summer_start is None else None, \
        summer_end.strftime("%m/%d")  if not summer_end is None else None, \
        winter_start.strftime("%m/%d")  if not winter_start is None else None, \
        winter_end.strftime("%m/%d")  if not winter_end is None else None, \
        (summer_end != None), \
        (winter_end != None)
    )


def _find_first_and_last_true_days_with_special_conditions(df, column_name):
    """
    1年間で指定された列(column_name)が最初にTrueになる日と最後にTrueになる日を抽出する関数。
    is_heating_dayが年に0, 1, 2回しか切り替わらない性質を考慮。

    Args:
        df (pd.DataFrame): データフレーム
        column_name (str): 対象のブール列名

    Returns:
        tuple: 最初にTrueになる日、最後にTrueになる日のタプル (Timestamp or None)
    """
    # シフトして前後の値を比較
    previous_value = df[column_name].shift(1, fill_value=df[column_name].iloc[-1])
    next_value = df[column_name].shift(-1, fill_value=df[column_name].iloc[0])

    # True の開始と終了を特定
    true_start_days = df.index[(~previous_value) & df[column_name]]
    true_end_days = df.index[df[column_name] & (~next_value)]

    # True が全く存在しない場合
    if len(true_start_days) == 0 or len(true_end_days) == 0:
        return None, None

    # 最初と最後のTrueの日を抽出
    first_true_day = true_start_days[0]
    last_true_day = true_end_days[-1]  # 最後に記録されたTrueの日を正確に取得

    return first_true_day, last_true_day
