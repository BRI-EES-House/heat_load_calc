import numpy as np
import json
from typing import Dict, List
import os


def get_compiled_schedules(
        n_p: float, room_name_is: List[str], a_floor_is: np.array
) -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray):
    """
    各種スケジュールを取得する。

    Args:
        n_p: 居住人数
        room_name_is: 室iの名称, [i]
        a_floor_is: 床面積, m2, [i]

    Returns:
        ステップnの室iにおける人体発熱を除く内部発熱, W
        ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [8760*4]
        ステップnの室iにおける局所換気量, m3/s, [i, 365*96]
        ステップnの室iにおける在室人数(float型), [i, 365*96]
        ステップnの室iにおける空調割合(float型), [i, 365*96]
    """

    # 変数
    #   局所換気量, m3/s, [i, 365*96]
    #   機器発熱, W, [i, 365*96]
    #   調理発熱, W, [i, 365*96]
    #   調理発湿, kg/s, [i, 365*96]
    #   照明発熱, W/m2, [i, 365*96]
    #   在室人数(float型）, [i, 365*96]
    #   空調割合(float型), [i, 365*96]
    v_mec_vent_local_is_ns,\
    q_gen_app_is_ns,\
    q_gen_ckg_is_ns,\
    x_gen_ckg_is_ns,\
    q_gen_lght_is_ns,\
    n_hum_is_ns,\
    ac_demand_is_ns = _get_each_schedules(n_p=n_p, room_name_is=room_name_is)

    # ステップnの室iにおける人体発熱を除く内部発熱, W
    q_gen_is_ns = q_gen_app_is_ns + q_gen_ckg_is_ns + q_gen_lght_is_ns * a_floor_is[:, np.newaxis]

    # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [8760*4]
    x_gen_is_ns = x_gen_ckg_is_ns

    return q_gen_is_ns, x_gen_is_ns, v_mec_vent_local_is_ns, n_hum_is_ns, ac_demand_is_ns


def _get_each_schedules(n_p: float, room_name_is: List[str])\
        -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray):
    """スケジュールを取得する。
    Args:
        n_p: 居住人数（注意：小数　整数ではない。）
        room_name_is: 室iの名称, [i]
    Returns:
        局所換気量, m3/s, [i, 365*96]
        機器発熱, W, [i, 365*96]
        調理発熱, W, [i, 365*96]
        調理発湿, kg/s, [i, 365*96]
        照明発熱, W/m2, [i, 365*96]
        在室人数(float型), [i, 365*96]
        空調のON/OFF(float型）, [i, 365*96]
    """

    # スケジュールを記述した辞書の読み込み
    d = _load_schedule()

    # カレンダーの読み込み（日にちの種類（'平日', '休日外', '休日在'））, [365]
    calendar = np.array(d['calendar'])

    # 局所換気量, m3/s, [i, 365*96]
    # jsonファイルでは、 m3/h で示されているため、単位換算(m3/h -> m3/s)を行っている。
    v_mec_vent_local_is_ns = np.concatenate([[
        _get_schedule(
            room_name_i=room_name_i,
            n_p=n_p,
            calendar=calendar,
            daily_schedule=d['daily_schedule'],
            schedule_type='local_vent_amount'
        )] for room_name_i in room_name_is]) / 3600.0

    # 機器発熱, W, [i, 365*96]
    q_gen_app_is_ns = np.concatenate([[
        _get_schedule(
            room_name_i=room_name,
            n_p=n_p,
            calendar=calendar,
            daily_schedule=d['daily_schedule'],
                schedule_type='heat_generation_appliances'
        )] for room_name in room_name_is])

    # 調理発熱, W, [i, 365*96]
    q_gen_ckg_is_ns = np.concatenate([[
        _get_schedule(
            room_name_i=room_name,
            n_p=n_p,
            calendar=calendar,
            daily_schedule=d['daily_schedule'],
            schedule_type='vapor_generation_cooking'
        )] for room_name in room_name_is])

    # 調理発湿, kg/s, [i, 365*96]
    # jsonファイルでは、g/h で示されているため、単位換算(g/h->kg/s)を行っている。
    x_gen_ckg_is_ns = np.concatenate([[
        _get_schedule(
            room_name_i=room_name,
            n_p=n_p,
            calendar=calendar,
            daily_schedule=d['daily_schedule'],
            schedule_type='heat_generation_cooking'
        )] for room_name in room_name_is]) / 1000.0 / 3600.0

    # 照明発熱, W/m2, [i, 365*96]
    # 単位面積あたりで示されていることに注意
    q_gen_lght_is_ns = np.concatenate([[
        _get_schedule(
            room_name_i=room_name,
            n_p=n_p,
            calendar=calendar,
            daily_schedule=d['daily_schedule'],
            schedule_type='heat_generation_lighting'
        )] for room_name in room_name_is])

    # 在室人数, [i, 365*96]
    # 居住人数で按分しているため、整数ではなく小数であることに注意
    n_hum_is_ns = np.concatenate([[
        _get_schedule(
            room_name_i=room_name,
            n_p=n_p,
            calendar=calendar,
            daily_schedule=d['daily_schedule'],
            schedule_type='number_of_people'
        )] for room_name in room_name_is])

    # 空調割合, float型, [i, 365*96]
    ac_demand_is_ns = np.concatenate([[
        _get_schedule(
            room_name_i=room_name,
            n_p=n_p,
            calendar=calendar,
            daily_schedule=d['daily_schedule'],
            schedule_type='is_temp_limit_set'
        )] for room_name in room_name_is])

    return v_mec_vent_local_is_ns, q_gen_app_is_ns, q_gen_ckg_is_ns, x_gen_ckg_is_ns, q_gen_lght_is_ns, n_hum_is_ns, ac_demand_is_ns


def _load_schedule() -> Dict:
    """スケジュールを読み込む
    """
    js = open(str(os.path.dirname(__file__)) + '/schedules.json', 'r', encoding='utf-8')
    d_json = json.load(js)
    return d_json


def _get_schedule(
        room_name_i: str, n_p: float, calendar: np.ndarray, daily_schedule: Dict, schedule_type: str
) -> np.ndarray:
    """
    スケジュールを取得する。
    Args:
        room_name_i: 室iの名称
        n_p: 居住人数
        calendar: 日にちの種類（'平日', '休日外', '休日在'), [365]
        daily_schedule: スケジュール（辞書型）
        schedule_type: どのようなスケジュールを扱うのか？　以下から指定する。
            'local_vent_amount'
            'heat_generation_appliances'
            'vapor_generation_cooking'
            'heat_generation_cooking'
            'heat_generation_lighting'
            'number_of_people'
            'is_temp_limit_set'
    Returns:
        スケジュール, [365*96]
    """

    def convert_schedule(day_type: str):
        return {
            '1': daily_schedule['1'][room_name_i][day_type][schedule_type],
            '2': daily_schedule['2'][room_name_i][day_type][schedule_type],
            '3': daily_schedule['3'][room_name_i][day_type][schedule_type],
            '4': daily_schedule['4'][room_name_i][day_type][schedule_type],
        }

    d_weekday = convert_schedule(day_type='平日')
    d_holiday_out = convert_schedule(day_type='休日外')
    d_holiday_in = convert_schedule(day_type='休日在')
    
    d_365_96 = np.full((365, 96), -1.0, dtype=float)
    d_365_96[calendar == '平日'] = _get_interpolated_schedule(n_p, d_weekday)
    d_365_96[calendar == '休日外'] = _get_interpolated_schedule(n_p, d_holiday_out)
    d_365_96[calendar == '休日在'] = _get_interpolated_schedule(n_p, d_holiday_in)
    d = d_365_96.flatten()

    return d


def _get_interpolated_schedule(n_p: float, daily_schedule: Dict) -> np.ndarray:
    """
    世帯人数で線形補間してリストを返す
    Args:
        n_p: 居住人数
        daily_schedule: スケジュール
            Keyは必ず'1', '2', '3', '4'
            Valueは96個のリスト形式の値
    Returns:
        線形補間したリスト, [96]
    """

    ceil_np, floor_np = _get_ceil_floor_np(n_p)

    ceil_schedule = np.array(daily_schedule[str(ceil_np)])
    floor_schedule = np.array(daily_schedule[str(floor_np)])

    interpolate_np_schedule = ceil_schedule * (n_p - float(floor_np)) + floor_schedule * (float(ceil_np) - n_p)

    return interpolate_np_schedule


def _get_ceil_floor_np(n_p: float) -> (int, int):
    """世帯人数から切り上げ・切り下げた人数を整数値で返す

    Args:
        n_p: 世帯人数

    Returns:
        タプル：
            切り上げた世帯人数
            切り下げた世帯人数
    """

    if 1.0 <= n_p < 2.0:
        ceil_np = 2
        floor_np = 1
    elif 2.0 <= n_p < 3.0:
        ceil_np = 3
        floor_np = 2
    elif 3.0 <= n_p <= 4.0:
        ceil_np = 4
        floor_np = 3
    else:
        raise ValueError('The number of people is out of range.')

    return ceil_np, floor_np

