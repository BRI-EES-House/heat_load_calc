import numpy as np
from common import get_nday

"""
付録30．	機器発熱スケジュール
"""


# JSONファイルから機器・調理発熱スケジュールを読み込む
def read_internal_heat_schedules_from_json(d_room):
    # 内部発熱の初期化
    # 機器顕熱
    heat_generation_appliances_schedule = np.array(d_room['schedule']['heat_generation_appliances'])
    # 調理顕熱
    heat_generation_cooking_schedule = np.array(d_room['schedule']['heat_generation_cooking'])
    # 調理潜熱
    vapor_generation_cooking_schedule = np.array(d_room['schedule']['vapor_generation_cooking'])

    return heat_generation_appliances_schedule, heat_generation_cooking_schedule, vapor_generation_cooking_schedule


# 機器・調理発熱スケジュールの読み込み
def get_hourly_internal_heat_schedules(space, dtmNow):
    # スケジュールのリスト番号の計算
    item = (get_nday(dtmNow.month, dtmNow.day) - 1) * 24 + dtmNow.hour

    # 機器顕熱[W]
    heat_generation_appliances = space.heat_generation_appliances_schedule[item]

    # 調理顕熱[W]
    heat_generation_cooking = space.heat_generation_cooking_schedule[item]

    # 調理潜熱[g/h]
    vapor_generation_cooking = space.vapor_generation_cooking_schedule[item]

    return heat_generation_appliances, heat_generation_cooking, vapor_generation_cooking
