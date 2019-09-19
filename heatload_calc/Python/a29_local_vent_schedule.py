import numpy as np

"""
付録29．	局所換気のスケジュール
"""


# JSONファイルから局所換気スケジュールを読み込む
def read_local_vent_schedules_from_json(d_room):
    # 局所換気
    return np.repeat(d_room['schedule']['local_vent_amount'], 4)
