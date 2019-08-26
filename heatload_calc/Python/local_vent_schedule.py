from common import get_nday

# JSONファイルから局所換気スケジュールを読み込む
def read_local_vent_schedules_from_json(space, d_room):
    # 局所換気
    space.local_vent_amount_schedule = d_room['schedule']['local_vent_amount']

# 局所換気スケジュールの読み込み
def create_hourly_local_vent_schedules(space, dtmNow):
    # スケジュールのリスト番号の計算
    item = (get_nday(dtmNow.month, dtmNow.day) - 1) * 24 + dtmNow.hour

    # 局所換気量
    space.LocalVentset = space.local_vent_amount_schedule[item]
