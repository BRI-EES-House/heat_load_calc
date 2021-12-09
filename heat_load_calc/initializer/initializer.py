import numpy as np
import csv
from enum import Enum

from heat_load_calc.initializer import schedule_loader
from heat_load_calc.initializer import residents_number


class RoomType(Enum):
    """
    室のタイプ
    """
    # 主たる居室
    MAIN_OCCUPANT_ROOM = 'main_occupant_room'
    # その他の居室
    OTHER_OCCUPANT_ROOM = 'other_occupant_room'
    # 非居室
    NON_OCCUPANT_ROOM = 'non_occupant_room'
    # 床下
    UNDERFLOOR = 'underfloor'


def make_house(d, input_data_dir, output_data_dir):

    rooms = d['rooms']

    # 室iの名称, [i]
    room_name_is = [r['name'] for r in rooms]

    # 室iの床面積, m2, [i]
    a_floor_is = np.array([r['floor_area'] for r in rooms])

    # 床面積の合計, m2
    a_floor_total = a_floor_is.sum()

    # 居住人数
    n_p = residents_number.get_total_number_of_residents(a_floor_total=a_floor_total)

    # 以下のスケジュールの取得, [i, 365*96]
    #   ステップnの室iにおける人体発熱を除く内部発熱, W, [i, 8760*4]
    # 　　ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [i, 8760*4]
    #   ステップnの室iにおける局所換気量, m3/s, [i, 8760*4]
    #   ステップnの室iにおける在室人数, [i, 8760*4]
    #   ステップnの室iにおける空調割合, [i, 8760*4]
    q_gen_is_ns, x_gen_is_ns, v_mec_vent_local_is_ns, n_hum_is_ns, ac_demand_is_ns\
        = schedule_loader.get_compiled_schedules(
            n_p=n_p,
            room_name_is=room_name_is,
            a_floor_is=a_floor_is
        )

    # ステップnの室iにおける局所換気量, m3/s, [i, 8760*4]
    with open(output_data_dir + '/mid_data_local_vent.csv', 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(v_mec_vent_local_is_ns.T.tolist())

    # ステップnの室iにおける内部発熱, W, [8760*4]
    with open(output_data_dir + '/mid_data_heat_generation.csv', 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(q_gen_is_ns.T.tolist())

    # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [8760*4]
    with open(output_data_dir + '/mid_data_moisture_generation.csv', 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(x_gen_is_ns.T.tolist())

    # ステップnの室iにおける在室人数, [8760*4]
    with open(output_data_dir + '/mid_data_occupants.csv', 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(n_hum_is_ns.T.tolist())

    # ステップnの室iにおける空調需要, [8760*4]
    with open(output_data_dir + '/mid_data_ac_demand.csv', 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(ac_demand_is_ns.T.tolist())

