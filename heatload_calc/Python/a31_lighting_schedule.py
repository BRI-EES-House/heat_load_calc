import numpy as np
from common import get_nday

"""
付録31．	照明発熱スケジュール
"""


# JSONファイルから局所換気スケジュールを読み込む
def read_lighting_schedules_from_json(d_room):
    # 照明
    return np.array(d_room['schedule']['heat_generation_lighting'])


# 局所換気スケジュールの読み込み
def get_hourly_lighting_schedules(space, dtmNow):
    # スケジュールのリスト番号の計算
    item = (get_nday(dtmNow.month, dtmNow.day) - 1) * 24 + dtmNow.hour

    # 照明発熱[W]
    return space.heat_generation_lighting_schedule[item]
