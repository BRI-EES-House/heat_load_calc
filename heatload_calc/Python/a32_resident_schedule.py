import numpy as np
from common import get_nday
import apdx3_human_body as a3

"""
付録32．	人体発熱スケジュール
"""


# JSONファイルから在室人数スケジュールを読み込む
def read_resident_schedules_from_json(d_room):
    # 人体顕熱
    return np.array(d_room['schedule']['number_of_people'])


# 在室人数スケジュールの読み込み
def get_hourly_resident_schedules(space, dtmNow, sequence_number):
    # スケジュールのリスト番号の計算
    item = (get_nday(dtmNow.month, dtmNow.day) - 1) * 24 + dtmNow.hour

    # 在室人員[人]
    number_of_people = space.number_of_people_schedule[item]
    # 1人あたりの人体発熱(W)・発湿(kg/s)
    q_hum, x_hum = a3.get_q_hum_and_x_hum(space.Tr_i_n[sequence_number - 1])
    # 人体顕熱[W]
    Humans = number_of_people * q_hum
    # 人体潜熱[kg/s]
    Humanl = number_of_people * x_hum

    return number_of_people, Humans, Humanl
