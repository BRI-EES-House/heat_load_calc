from common import get_nday, conra

# スケジュールの読み込み
def create_hourly_schedules(space, dtmNow, is_residential):
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
    # 人体顕熱[W]
    space.Humans = space.number_of_people \
                    * min(63.0 - 4.0 * (space.oldTr - 24.0), 119.0)
    # 人体潜熱[W]
    space.Humanl = max(space.number_of_people * 119.0 - space.Humans, 0.0)
    space.Hn = space.heat_generation_appliances + space.heat_generation_lighting + space.Humans + space.heat_generation_cooking

    # 内部発湿[kg/s]
    space.Lin = space.vapor_generation_cooking / 1000.0 / 3600.0 + space.Humanl / conra
    
    # 局所換気量
    space.LocalVentset = space.local_vent_amount_schedule[item]

    # 非住宅の室温、湿度の上下限値関連スケジュールの読み込み
    if not is_residential:
        # 上限温度設定フラグ
        space.is_upper_temp_limit_set = space.is_upper_temp_limit_set_schedule[item]
        # 設定上限温度
        space.temperature_upper_limit = space.temperature_upper_limit_schedule[item]
        # 下限温度設定フラグ
        space.is_lower_temp_limit_set = space.is_lower_temp_limit_set_schedule[item]
        # 設定下限温度
        space.temperature_lower_limit = space.temperature_lower_limit_schedule[item]

        # 上限湿度設定フラグ
        space.is_upper_humidity_limit_set = space.is_upper_humidity_limit_set_schedule[item]
        # 設定上限湿度
        space.relative_humidity_upper_limit = space.relative_humidity_upper_limit_schedule[item]
        # 下限湿度設定フラグ
        space.is_lower_humidity_limit_set = space.is_lower_humidity_limit_set_schedule[item]
        # 設定下限湿度
        space.relative_humidity_lower_limit = space.relative_humidity_lower_limit_schedule[item]

# JSONファイルから各種スケジュールを読み込む
def read_schedules_from_json(space, d_room, Gdata):
    # 空調スケジュールの読み込み
    # 設定温度／PMV上限値の設定
    if 'is_upper_temp_limit_set' in d_room['schedule']:
        space.is_upper_temp_limit_set_schedule = d_room['schedule']['is_upper_temp_limit_set']
    # 設定温度／PMV下限値の設定
    if 'is_lower_temp_limit_set' in d_room['schedule']:
        space.is_lower_temp_limit_set_schedule = d_room['schedule']['is_lower_temp_limit_set']
    # 非住宅の場合
    if not Gdata.is_residential:
        # 室温上限値
        space.temperature_upper_limit_schedule = d_room['schedule']['temperature_upper_limit']
        # 室温下限値
        space.temperature_lower_limit_schedule = d_room['schedule']['temperature_lower_limit']
        # 相対湿度上限値の設定
        space.is_upper_humidity_limit_set_schedule = d_room['schedule']['is_upper_humidity_limit_set']
        # 相対湿度下限値の設定
        space.is_lower_humidity_limit_set_schedule = d_room['schedule']['is_lower_humidity_limit_set']
        # 相対湿度上限値
        space.relative_humidity_upper_limit_schedule = d_room['schedule']['relative_humidity_upper_limit']
        # 相対湿度下限値
        space.relative_humidity_lower_limit_schedule = d_room['schedule']['relative_humidity_lower_limit']
    # 住宅の場合
    else:
        # PMV上限値
        if 'pmv_upper_limit' in d_room['schedule']:
            space.pmv_upper_limit_schedule = d_room['schedule']['pmv_upper_limit']
        # PMV下限値
        if 'pmv_lower_limit' in d_room['schedule']:
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