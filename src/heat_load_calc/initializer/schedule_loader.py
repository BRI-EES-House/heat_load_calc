import numpy as np
import json
from typing import Dict, List, Tuple
import os


def _load_schedule() -> Dict:
    """スケジュールを読み込む
    """
    js = open(str(os.path.dirname(__file__)) + '/schedules.json', 'r', encoding='utf-8')
    d_json = json.load(js)
    js.close()
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

