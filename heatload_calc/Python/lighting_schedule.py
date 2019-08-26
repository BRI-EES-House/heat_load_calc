from common import get_nday

# JSONファイルから局所換気スケジュールを読み込む
def read_lighting_schedules_from_json(space, d_room):
    # 照明
    space.heat_generation_lighting_schedule = d_room['schedule']['heat_generation_lighting']

# 局所換気スケジュールの読み込み
def create_hourly_lighting_schedules(space, dtmNow):
    # スケジュールのリスト番号の計算
    item = (get_nday(dtmNow.month, dtmNow.day) - 1) * 24 + dtmNow.hour

    # 照明発熱[W]
    space.heat_generation_lighting = space.heat_generation_lighting_schedule[item]
