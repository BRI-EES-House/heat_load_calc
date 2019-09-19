import numpy as np

"""
付録30．	機器発熱スケジュール
"""


# JSONファイルから機器・調理発熱スケジュールを読み込む
def read_internal_heat_schedules_from_json(d_room):
    # 機器顕熱
    heat_generation_appliances_schedule = np.repeat(d_room['schedule']['heat_generation_appliances'], 4)

    # 調理顕熱
    heat_generation_cooking_schedule = np.repeat(d_room['schedule']['heat_generation_cooking'], 4)

    # 調理潜熱
    vapor_generation_cooking_schedule = np.repeat(d_room['schedule']['vapor_generation_cooking'], 4)

    return heat_generation_appliances_schedule, heat_generation_cooking_schedule, vapor_generation_cooking_schedule
