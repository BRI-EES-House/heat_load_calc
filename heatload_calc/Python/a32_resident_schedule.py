import numpy as np
import math
import apdx3_human_body as a3

"""
付録32．	人体発熱スケジュール
"""


# JSONファイルから在室人数スケジュールを読み込む
def read_resident_schedules_from_json(d_room):
    # 人体顕熱
    return np.repeat(d_room['schedule']['number_of_people'], 4)
