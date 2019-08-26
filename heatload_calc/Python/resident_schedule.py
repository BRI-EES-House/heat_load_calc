from common import get_nday
from apdx3_human_body import get_q_hum_and_x_hum

# JSONファイルから在室人数スケジュールを読み込む
def read_resident_schedules_from_json(space, d_room):
    # 人体顕熱
    space.number_of_people_schedule = d_room['schedule']['number_of_people']

# 在室人数スケジュールの読み込み
def create_hourly_resident_schedules(space, dtmNow):
    # スケジュールのリスト番号の計算
    item = (get_nday(dtmNow.month, dtmNow.day) - 1) * 24 + dtmNow.hour

    # 在室人員[人]
    space.number_of_people = space.number_of_people_schedule[item]
    # 1人あたりの人体発熱(W)・発湿(kg/s)
    q_hum, x_hum = get_q_hum_and_x_hum(space.oldTr)
    # 人体顕熱[W]
    space.Humans = space.number_of_people * q_hum
    # 人体潜熱[kg/s]
    space.Humanl = space.number_of_people * x_hum
