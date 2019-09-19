import numpy as np
import math

"""
付録31．	照明発熱スケジュール
"""


# JSONファイルから局所換気スケジュールを読み込む
def read_lighting_schedules_from_json(d_room):
    # 照明
    return np.repeat(d_room['schedule']['heat_generation_lighting'], 4)
