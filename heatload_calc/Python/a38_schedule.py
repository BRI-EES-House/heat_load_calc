import numpy as np
import json
from typing import Dict, List


def get_schedule(room_name_i: str, n_p: float, calendar: List[str], daily_schedule):
    """スケジュールを取得する。

    Args:
        room_name_i: 室iの名称
        n_p: 居住人数
        calendar: 日にちの種類（'平日', '休日外', '休日在'), [365]
        daily_schedule: スケジュール（辞書型）
    Returns:
        スケジュール, [365*96]
    """

    d_365_96 = np.full((365, 96), -1.0)
    d_365_96[calendar == '平日'] = get_interpolated_schedule(n_p, daily_schedule['平日'][room_name_i])
    d_365_96[calendar == '休日外'] = get_interpolated_schedule(n_p, daily_schedule['休日外'][room_name_i])
    d_365_96[calendar == '休日在'] = get_interpolated_schedule(n_p, daily_schedule['休日在'][room_name_i])
    d = d_365_96.flatten()

    return d


def get_interpolated_schedule(n_p: float, daily_schedule: Dict) -> np.ndarray:
    """世帯人数で線形補間してリストを返す

    Args:
        n_p: 世帯人数
        daily_schedule: スケジュール
            Keyは必ず'1', '2', '3', '4'
            Valueは96個のリスト形式の値
    Returns:
        線形補間したリスト, [96]
    """

    ceil_np, floor_np = get_ceil_floor_np(n_p)

    ceil_schedule = np.array(daily_schedule[str(ceil_np)])
    floor_schedule = np.array(daily_schedule[str(floor_np)])

    interpolate_np_schedule = ceil_schedule * (n_p - float(floor_np)) + floor_schedule * (float(ceil_np) - n_p)

    return interpolate_np_schedule


def get_ceil_floor_np(n_p: float) -> (int, int):
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


def get_air_conditioning_schedules2(room_name, calendar, daily_schedule) -> (np.ndarray, np.ndarray):
    """空調スケジュールを取得する。

    Args:
        room:

    Returns:
        空調スケジュール
    """

    d_365_96 = np.full((365, 96), "", dtype=np.object)

    d_365_96[calendar == '平日'] = daily_schedule['平日'][room_name]['4']
    d_365_96[calendar == '休日外'] = daily_schedule['休日外'][room_name]['4']
    d_365_96[calendar == '休日在'] = daily_schedule['休日在'][room_name]['4']

    d = d_365_96.flatten()

    return d

