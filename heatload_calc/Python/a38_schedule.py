import numpy as np
import json
from typing import Dict, List


def get_all_schedules(n_p: float, room_name_is: List[str])\
        -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray):
    """スケジュールを取得する。

    Args:
        n_p: 居住人数（注意：小数　整数ではない。）
        room_name_is: 室iの名称, [i]

    Returns:
        局所換気量, m3/h, [i, 365*96]
        TODO: 単位を確認すること
        機器発熱, W, [i, 365*96]
        調理発熱, W, [i, 365*96]
        調理発湿, kg/s, [i, 365*96]
        照明発熱, W/m2, [i, 365*96]
        在室人数, [i, 365*96]
        空調のON/OFF, bool型, [i, 365*96]
    """

    # スケジュールを記述した辞書の読み込み
    d = load_schedule()

    # カレンダーの読み込み（日にちの種類（'平日', '休日外', '休日在'), [365]）
    calendar = np.array(d['calendar'])

    # 局所換気量, m3/s, [i, 365*96]
    v_mec_vent_local_is_ns = np.concatenate([[
        get_schedule(
            room_name_i=room_name,
            n_p=n_p,
            calendar=calendar,
            daily_schedule=d['daily_schedule']['local_vent_amount']
        )] for room_name in room_name_is])

    # 機器発熱, W, [i, 365*96]
    q_gen_app_is_ns = np.concatenate([[
        get_schedule(
            room_name_i=room_name,
            n_p=n_p,
            calendar=calendar,
            daily_schedule=d['daily_schedule']['heat_generation_appliances']
        )] for room_name in room_name_is])

    # 調理発熱, W, [i, 365*96]
    q_gen_ckg_is_ns = np.concatenate([[
        get_schedule(
            room_name_i=room_name,
            n_p=n_p,
            calendar=calendar,
            daily_schedule=d['daily_schedule']['vapor_generation_cooking']
        )] for room_name in room_name_is])

    # 調理発湿, kg/s, [i, 365*96]
    # jsonファイルでは、g/h で示されているため、単位換算(g/h->kg/s)を行っている。
    x_gen_ckg_is_ns = np.concatenate([[
        get_schedule(
            room_name_i=room_name,
            n_p=n_p,
            calendar=calendar,
            daily_schedule=d['daily_schedule']['heat_generation_cooking']
        )] for room_name in room_name_is]) / 1000.0 / 3600.0

    # 照明発熱, W/m2, [i, 365*96]
    # 単位面積あたりで示されていることに注意
    q_gen_lght_is_ns = np.concatenate([[
        get_schedule(
            room_name_i=room_name,
            n_p=n_p,
            calendar=calendar,
            daily_schedule=d['daily_schedule']['heat_generation_lighting']
        )] for room_name in room_name_is])

    # 在室人数, [i, 365*96]
    # 居住人数で按分しているため、整数ではなく小数であることに注意
    n_hum_is_ns = np.concatenate([[
        get_schedule(
            room_name_i=room_name,
            n_p=n_p,
            calendar=calendar,
            daily_schedule=d['daily_schedule']['number_of_people']
        )] for room_name in room_name_is])

    # 空調のON/OFF, bool型, [i, 365*96]
    # jsonファイルでは、ｓｔｒ（”on", "off")で示されているため、次の行でbool型に変換を行っている。
    ac_demand_is_ns_on_off = np.concatenate([[
        get_schedule(
            room_name_i=room_name,
            n_p=n_p,
            calendar=calendar,
            daily_schedule=d['daily_schedule']['is_temp_limit_set']
        )] for room_name in room_name_is])
    ad_demand_is_ns = np.where(ac_demand_is_ns_on_off == 1, True, False)

    return v_mec_vent_local_is_ns, q_gen_app_is_ns, q_gen_ckg_is_ns, x_gen_ckg_is_ns, q_gen_lght_is_ns, n_hum_is_ns, ad_demand_is_ns


def load_schedule() -> Dict:
    """スケジュールを読み込む
    """
    js = open('schedules.json', 'r', encoding='utf-8')
    d_json = json.load(js)
    return d_json


def get_schedule(room_name_i: str, n_p: float, calendar: np.ndarray, daily_schedule: Dict) -> np.ndarray:
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


def get_schedule2(room_name_i: str, calendar: np.ndarray, daily_schedule: Dict) -> np.ndarray:
    """スケジュールを取得する。

    Args:
        room_name_i: 室iの名称
        calendar: 日にちの種類（'平日', '休日外', '休日在'), [365]
        daily_schedule: スケジュール（辞書型）
    Returns:
        スケジュール, [365*96]
    Notes:
        get_schedule とは違い、ここでは按分操作をしていない。
        仮に居住人数4人としている。
        空調スケジュールのON/OFF値は按分できないため、何らかの抜本的な対策が必要。
        TODO: 仮置している居住人数4人について改善が必要。
    """

    d_365_96 = np.full((365, 96), "", dtype=np.object)

    d_365_96[calendar == '平日'] = daily_schedule['平日'][room_name_i]['4']
    d_365_96[calendar == '休日外'] = daily_schedule['休日外'][room_name_i]['4']
    d_365_96[calendar == '休日在'] = daily_schedule['休日在'][room_name_i]['4']

    d = d_365_96.flatten()

    return d

