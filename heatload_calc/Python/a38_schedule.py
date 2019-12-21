import numpy as np
import json
import math

def get_local_vent_schedules(room, n_p):
    """局所換気スケジュールを取得する。

    Args:
        room:

    Returns:
        局所換気スケジュール[m3/h]
    """
    js = open('schedules.json', 'r', encoding='utf-8')
    d_json = json.load(js)
    calendar = d_json['calendar']
    daily_schedule = d_json['daily_schedule']['local_vent_amount']
    # 世帯人数切り上げ、切り下げ
    ceil_np, floor_np = get_ceil_floor_np(n_p)
    local_vent_schedules = np.array([])
    for day in calendar:
        local_vent_schedules = np.append(local_vent_schedules, interpolate_np(n_p, ceil_np, floor_np, daily_schedule[day][room['name']]))
    return local_vent_schedules

# 世帯人数から切り上げ、切り下げた人数を返す
def get_ceil_floor_np(n_p: float):# 世帯人数切り上げ、切り下げ
    if n_p >= 0.0 and n_p < 2.0:
        ceil_np = 2
        floor_np = 1
    elif n_p >= 2.0 and n_p < 3.0:
        ceil_np = 3
        floor_np = 2
    elif n_p >= 3.0:
        ceil_np = 4
        floor_np = 3
    return (ceil_np, floor_np)

# 世帯人数で線形補間してリストを返す
def interpolate_np(n_p: float, ceil_np: int, floor_np: int, daily_schedule: dict):
    ceil_schedule = np.array(daily_schedule[str(ceil_np)])
    floor_schedule = np.array(daily_schedule[str(floor_np)])
    interpolate_np_schedule = ceil_schedule * (n_p - float(floor_np)) + floor_schedule * (float(ceil_np) - n_p)
    return interpolate_np_schedule

def get_sensible_heat_generation_of_cooking(room, n_p):
    """調理潜熱発熱スケジュールを取得する。

    Args:
        room:

    Returns:
        調理潜熱発熱スケジュール[W]
    """
    js = open('schedules.json', 'r', encoding='utf-8')
    d_json = json.load(js)
    calendar = d_json['calendar']
    daily_schedule = d_json['daily_schedule']['heat_generation_cooking']
    sensible_heat_generation_of_cooking = np.array([])
    # 世帯人数切り上げ、切り下げ
    ceil_np, floor_np = get_ceil_floor_np(n_p)
    for day in calendar:
        sensible_heat_generation_of_cooking = np.append(sensible_heat_generation_of_cooking, \
            interpolate_np(n_p, ceil_np, floor_np, daily_schedule[day][room['name']]))
    return sensible_heat_generation_of_cooking


def get_latent_heat_generation_of_cooking(room, n_p):
    """調理発熱スケジュールを取得する。

    Args:
        room:

    Returns:
        調理発熱スケジュール[g/h]
    """
    js = open('schedules.json', 'r', encoding='utf-8')
    d_json = json.load(js)
    calendar = d_json['calendar']
    daily_schedule = d_json['daily_schedule']['vapor_generation_cooking']
    latent_heat_generation_of_cooking = np.array([])
    # 世帯人数切り上げ、切り下げ
    ceil_np, floor_np = get_ceil_floor_np(n_p)
    for day in calendar:
        latent_heat_generation_of_cooking = np.append(latent_heat_generation_of_cooking, \
            interpolate_np(n_p, ceil_np, floor_np, daily_schedule[day][room['name']]))
    return latent_heat_generation_of_cooking


def get_heat_generation_of_appliances(room, n_p):
    """機器発熱スケジュールを取得する。

    Args:
        room:

    Returns:
        機器発熱スケジュール[W]
    """

    js = open('schedules.json', 'r', encoding='utf-8')
    d_json = json.load(js)
    calendar = d_json['calendar']
    daily_schedule = d_json['daily_schedule']['heat_generation_appliances']
    heat_generation_of_appliances = np.array([])
    # 世帯人数切り上げ、切り下げ
    ceil_np, floor_np = get_ceil_floor_np(n_p)
    for day in calendar:
        heat_generation_of_appliances = np.append(heat_generation_of_appliances, \
            interpolate_np(n_p, ceil_np, floor_np, daily_schedule[day][room['name']]))
    return heat_generation_of_appliances


def get_heat_generation_of_lighting(room, n_p):
    """照明発熱スケジュールを取得する。

    Args:
        room:

    Returns:
        照明発熱スケジュール[W]
    """
    js = open('schedules.json', 'r', encoding='utf-8')
    d_json = json.load(js)
    calendar = d_json['calendar']
    daily_schedule = d_json['daily_schedule']['heat_generation_lighting']
    heat_generation_of_lighting = np.array([])
    # 世帯人数切り上げ、切り下げ
    ceil_np, floor_np = get_ceil_floor_np(n_p)
    for day in calendar:
        # 照明発熱は[W/m2]
        heat_generation_of_lighting = np.append(heat_generation_of_lighting, \
            interpolate_np(n_p, ceil_np, floor_np, daily_schedule[day][room['name']]))
    # 床面積を乗じる
    # TODO 床面積を乗じるのを忘れないように
    return heat_generation_of_lighting * 1.0


def get_number_of_residents(room, n_p):
    """在室人数スケジュールを取得する。

    Args:
        room:

    Returns:
        在室人数スケジュール[人]
    """
    js = open('schedules.json', 'r', encoding='utf-8')
    d_json = json.load(js)
    calendar = d_json['calendar']
    daily_schedule = d_json['daily_schedule']['number_of_people']
    number_of_residents = np.array([])
    # 世帯人数切り上げ、切り下げ
    ceil_np, floor_np = get_ceil_floor_np(n_p)
    for day in calendar:
        number_of_residents = np.append(number_of_residents, interpolate_np(n_p, ceil_np, floor_np, daily_schedule[day][room['name']]))
    return number_of_residents


def get_air_conditioning_schedules(room, n_p) -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray):
    """空調スケジュールを取得する。

    Args:
        room:

    Returns:
        空調スケジュール
    """

    # 空調スケジュールの読み込み
    # 設定温度／PMV上限値の設定
    is_upper_temp_limit_set_schedule = np.repeat(room['schedule']['is_upper_temp_limit_set'], 4)
    # 設定温度／PMV下限値の設定
    is_lower_temp_limit_set_schedule = np.repeat(room['schedule']['is_lower_temp_limit_set'], 4)

    # PMV上限値
    pmv_upper_limit_schedule = np.repeat(room['schedule']['pmv_upper_limit'], 4)
    # PMV下限値
    pmv_lower_limit_schedule = np.repeat(room['schedule']['pmv_lower_limit'], 4)

    return is_upper_temp_limit_set_schedule, \
           is_lower_temp_limit_set_schedule, \
           pmv_upper_limit_schedule, \
           pmv_lower_limit_schedule


