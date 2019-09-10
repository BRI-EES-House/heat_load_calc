import numpy as np
from common import get_nday

"""
付録29．	局所換気のスケジュール
"""

# JSONファイルから局所換気スケジュールを読み込む
def read_local_vent_schedules_from_json(d_room):
    # 局所換気
    return np.array(d_room['schedule']['local_vent_amount'])

# 局所換気スケジュールの読み込み
def get_hourly_local_vent_schedules(space, dtmNow):
    # スケジュールのリスト番号の計算
    item = (get_nday(dtmNow.month, dtmNow.day) - 1) * 24 + dtmNow.hour

    # 局所換気量
    return space.local_vent_amount_schedule[item]
