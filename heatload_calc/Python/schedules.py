from common import get_nday, conra
from apdx3_human_body import get_q_hum_and_x_hum

# スケジュールの読み込み
def create_hourly_schedules(space, dtmNow):
    # スケジュールのリスト番号の計算
    item = (get_nday(dtmNow.month, dtmNow.day) - 1) * 24 + dtmNow.hour
    # 機器顕熱[W]
    space.heat_generation_appliances = space.heat_generation_appliances_schedule[item]
    # 調理顕熱[W]
    space.heat_generation_cooking = space.heat_generation_cooking_schedule[item]
    # 調理潜熱[g/h]
    space.vapor_generation_cooking = space.vapor_generation_cooking_schedule[item]
    # 照明発熱[W]
    space.heat_generation_lighting = space.heat_generation_lighting_schedule[item]
    # 在室人員[人]
    space.number_of_people = space.number_of_people_schedule[item]

    # 1人あたりの人体発熱(W)・発湿(kg/s)
    q_hum, x_hum = get_q_hum_and_x_hum(space.oldTr)

    # 人体顕熱[W]
    space.Humans = space.number_of_people * q_hum

    # 人体潜熱[kg/s]
    space.Humanl = space.number_of_people * x_hum

    # 内部発熱[W]
    space.Hn = space.heat_generation_appliances + space.heat_generation_lighting + space.Humans + space.heat_generation_cooking

    # 内部発湿[kg/s]
    space.Lin = space.vapor_generation_cooking / 1000.0 / 3600.0 + space.Humanl
    
    # 局所換気量
    space.LocalVentset = space.local_vent_amount_schedule[item]

    # 上限PMV設定フラグ
    space.is_upper_temp_limit_set = space.is_upper_temp_limit_set_schedule[item]
    # 下限温度設定フラグ
    space.is_lower_temp_limit_set = space.is_lower_temp_limit_set_schedule[item]
    # 上限PMV
    space.pmv_upper_limit = space.pmv_upper_limit_schedule[item]
    # 下限PMV
    space.pmv_lower_limit = space.pmv_lower_limit_schedule[item]

    # 空調や通風などの需要がある場合にTrue
    space.air_conditioning_demand = space.is_upper_temp_limit_set or space.is_lower_temp_limit_set

# JSONファイルから各種スケジュールを読み込む
def read_schedules_from_json(space, d_room, Gdata):
    # 空調スケジュールの読み込み
    # 設定温度／PMV上限値の設定
    space.is_upper_temp_limit_set_schedule = d_room['schedule']['is_upper_temp_limit_set']
    # 設定温度／PMV下限値の設定
    space.is_lower_temp_limit_set_schedule = d_room['schedule']['is_lower_temp_limit_set']
    
    # PMV上限値
    space.pmv_upper_limit_schedule = d_room['schedule']['pmv_upper_limit']
    # PMV下限値
    space.pmv_lower_limit_schedule = d_room['schedule']['pmv_lower_limit']

    # 内部発熱の初期化
    # 機器顕熱
    space.heat_generation_appliances_schedule = d_room['schedule']['heat_generation_appliances']
    # 調理顕熱
    space.heat_generation_cooking_schedule = d_room['schedule']['heat_generation_cooking']
    # 調理潜熱
    space.vapor_generation_cooking_schedule = d_room['schedule']['vapor_generation_cooking']
    
    # 照明
    space.heat_generation_lighting_schedule = d_room['schedule']['heat_generation_lighting']
    # 人体顕熱
    space.number_of_people_schedule = d_room['schedule']['number_of_people']

    # 局所換気
    space.local_vent_amount_schedule = d_room['schedule']['local_vent_amount']