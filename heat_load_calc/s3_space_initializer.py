import numpy as np
from typing import Dict, List
import json
import csv
import pandas as pd

import heat_load_calc.a12_indoor_radiative_heat_transfer as a12
import heat_load_calc.a14_furniture as a14
import heat_load_calc.a15_air_flow_rate_rac as a15
import heat_load_calc.a22_radiative_heating_spec as a22
from heat_load_calc.initializer.boundary_type import BoundaryType
import heat_load_calc.s3_surface_initializer as s3
import heat_load_calc.x_35_occupants as x35
import heat_load_calc.a34_building_part_summarize as a34

from heat_load_calc.initializer import schedule_loader
from heat_load_calc.initializer import residents_number


def make_house(d, input_data_dir, output_data_dir):

    pp = pd.read_csv(input_data_dir + '/weather.csv', index_col=0)

    theta_o_ns = pp['temperature [degree C]'].values
    x_o_ns = pp['absolute humidity [kg/kg(DA)]'].values
    i_dn_ns = pp['normal direct solar radiation [W/m2]'].values
    i_sky_ns = pp['horizontal sky solar radiation [W/m2]'].values
    r_n_ns = pp['outward radiation [W/m2]'].values
    h_sun_ns = pp['sun altitude [rad]'].values
    a_sun_ns = pp['sun azimuth [rad]'].values

    rooms = d['rooms']

    # 室の数
    number_of_spaces = len(rooms)

    # 室のID
    # TODO: ID が0始まりで1ずつ増え、一意であることのチェックを行うコードを追記する。
    room_ids = [int(r['id']) for r in rooms]

    # 室iの名称, [i]
    room_names = [r['name'] for r in rooms]

    # 室iの気積, m3, [i]
    v_room_cap_is = np.array([r['volume'] for r in rooms])

    # 室iの外気からの機械換気量, m3/h, [i]
    v_vent_ex_is = np.array([r['vent'] for r in rooms])

    # 室iのC値, [i]
    c_value_is = np.array([r['c_value'] for r in rooms])

    # 室iの自然風利用時の換気回数, 1/h, [i]
    n_ntrl_vent_is = np.array([r['natural_vent_time'] for r in rooms])

    # 室iの隣室からの機会換気量, m3/h, [i, i]
    v_int_vent_is = get_v_int_vent_is(rooms)

    # 室iの自然風利用時の換気量, m3/s, [i]
    v_ntrl_vent_is = v_room_cap_is * n_ntrl_vent_is / 3600

    # 室iの家具等の熱容量, J/K
    c_cap_frnt_is = a14.get_c_cap_frnt_is(v_room_cap_is)

    # 室iの家具等と空気間の熱コンダクタンス, W/K, [i]
    c_frnt_is = a14.get_Cfun(c_cap_frnt_is)

    # 室iの家具等の湿気容量, kg/m3 kg/kgDA, [i]
    g_f_is = a14.get_g_f_is(v_room_cap_is)  # i室の備品類の湿気容量

    # 室iの家具等と空気間の湿気コンダクタンス, kg/s kg/kgDA
    c_x_is = a14.get_c_x_is(g_f_is)

    # 室iの境界j
    # メモ [12, 26, 12]
    bss = [
        [
            s3.get_boundary_simple(
                theta_o_ns=theta_o_ns,
                i_dn_ns=i_dn_ns,
                i_sky_ns=i_sky_ns,
                r_n_ns=r_n_ns,
                a_sun_ns=a_sun_ns,
                h_sun_ns=h_sun_ns,
                b=b_dict
            ) for b_dict in r['boundaries']
        ] for r in rooms
    ]

    # BoundarySimple をフラット化する。
    bss2 = np.concatenate(bss)

    # 集約化可能な境界には同じIDを振り、境界ごとにそのIDを取得する。
    # BoundarySimple の数のIDを持つ ndarray
    # 例
    # [ 0  1  2  3  4  5  6  7  8  9  9 10 11 12 13 14 15 16 11 12 15 16 17 18
    #  19 11 12 15 16 17 20 11 12 13 21 15 16 22 23 24 25 26 27 28 29 30 31 31
    #  31 31]
    gp_idxs = a34.get_group_indices(bss=bss2)

    # 先頭のインデックスのリスト
    # [ 0  1  2  3  4  5  6  7  8  9 11 12 13 14 15 16 17 22 23 24 30 34 37 38
    #  39 40 41 42 43 44 45 46]
    first_idx = np.array([np.where(gp_idxs == k)[0][0] for k in np.unique(gp_idxs)], dtype=np.int)

    # 統合された境界j*の総数
    bs_n = len(first_idx)

    # 境界jの名称, [j]
    name_js = ['integrated_boundary' + str(i) for i in np.unique(gp_idxs)]

    # 境界jの副名称（統合する前の境界の名前を'+'記号でつなげたもの）, [j]
    sub_name_js = ['+'.join([bs.name for bs in bss2[gp_idxs == i]]) for i in np.unique(gp_idxs)]

    # 境界jの面する室のID, [j]
    connected_room_id_js = [bss2[first_idx[i]].connected_room_id for i in np.unique(gp_idxs)]

    # 境界jの種類, [j]
    boundary_type_js = [bss2[first_idx[i]].boundary_type for i in np.unique(gp_idxs)]

    # 境界ｊが地盤か否か, [j]
    is_ground_js = [b == BoundaryType.Ground for b in boundary_type_js]

    # 境界jの面積, m2, [j]
    a_js = [sum([bs.area for bs in bss2[gp_idxs == i]]) for i in np.unique(gp_idxs)]

    # 境界jの温度差係数, [j]
    h_td_js = [bss2[first_idx[i]].h_td for i in np.unique(gp_idxs)]

    # 日射吸収の有無, [j]
    is_solar_absorbed_inside_js = [bss2[first_idx[i]].is_solar_absorbed_inside for i in np.unique(gp_idxs)]

    # 境界jの裏面の境界ID, [j]
    rear_surface_boundary_id_js = []
    for i in np.unique(gp_idxs):
        # 統合する前の裏面の境界id
        id = bss2[first_idx[i]].rear_surface_boundary_id
        # 統合後の裏面の境界id (None の場合は None を代入する。）
        id2 = None if id is None else gp_idxs[id]
        rear_surface_boundary_id_js.append(id2)

    k_ei_js = []

    for i in range(bs_n):

        if boundary_type_js[i] in [
            BoundaryType.ExternalOpaquePart,
            BoundaryType.ExternalTransparentPart,
            BoundaryType.ExternalGeneralPart
        ]:
            # 温度差係数が1.0でない場合はk_ei_jsに値を代入する。
            # id は自分自身の境界IDとし、自分自身の表面の影響は1.0から温度差係数を減じた値になる。
            if h_td_js[i] < 1.0:
                k_ei_js.append({'id': i, 'coef': round(1.0 - h_td_js[i], 1)})
            else:
                # 温度差係数が1.0の場合はNoneとする。
                k_ei_js.append(None)
        elif boundary_type_js[i] == BoundaryType.Internal:
            # 室内壁の場合にk_ei_jsを登録する。
            k_ei_js.append({'id': int(rear_surface_boundary_id_js[i]), 'coef': 1.0})
        else:
            # 外皮に面していない場合、室内壁ではない場合（地盤の場合が該当）は、Noneとする。
            k_ei_js.append(None)

    # 室iの統合された境界j*の室内侵入日射吸収の有無, [j*]
    # is_solar_absorbed_inside_i_jstrs = np.array([bss[first_idx[i]].is_solar_absorbed_inside for i in np.unique(gp_idxs)])

    # 境界jの室内側表面総合熱伝達率, W/m2K, [j]
    h_i_js = [bss2[first_idx[i]].h_i for i in np.unique(gp_idxs)]

    # 境界jの傾斜面のステップnにおける相当外気温度, degree C, [j, 8760 * 4]
    theta_o_sol_js_ns = np.array([
        s3.get_area_weighted_averaged_values_two_dimension(
            v=np.array([bs.theta_o_sol for bs in bss2[gp_idxs == i]]),
            a=np.array([bs.area for bs in bss2[gp_idxs == i]])
        )
        for i in np.unique(gp_idxs)
    ])

    # ステップnの室iにおける窓の透過日射熱取得, W, [8760*4]
    q_trs_sol_is_ns = np.array([
        np.sum(np.array([bs.q_trs_sol for bs in bss2 if bs.connected_room_id == i]), axis=0)
        for i in range(number_of_spaces)
    ])

    # 室iの統合された境界j*の応答係数法（項別公比法）における根の数, [j*]
    # n_root_i_jstrs = np.array([bss[first_idx[i]].n_root for i in np.unique(gp_idxs)])

    # 境界jの項別公比法における項mの公比, [j, 12]
    rows_js = [list(bss2[first_idx[i]].row) for i in np.unique(gp_idxs)]

    # 境界jの貫流応答係数の初項, [j]
    phi_t0_js = np.array([
        s3.get_area_weighted_averaged_values_one_dimension(
            v=np.array([bs.rft0 for bs in bss2[gp_idxs == i]]),
            a=np.array([bs.area for bs in bss2[gp_idxs == i]])
        )
        for i in np.unique(gp_idxs)
    ])

    # 境界jの吸熱応答係数の初項, m2K/W, [j]
    phi_a0_js = np.array([
        s3.get_area_weighted_averaged_values_one_dimension(
            v=np.array([bs.rfa0 for bs in bss2[gp_idxs == i]]),
            a=np.array([bs.area for bs in bss2[gp_idxs == i]])
        )
        for i in np.unique(gp_idxs)
    ])

    # 境界jの項別公比法における項mの貫流応答係数の第一項, [j, 12]
    phi_t1_js = [
        list(s3.get_area_weighted_averaged_values_two_dimension(
            v=np.array([bs.rft1 for bs in bss2[gp_idxs == i]]),
            a=np.array([bs.area for bs in bss2[gp_idxs == i]])
        ))
        for i in np.unique(gp_idxs)
    ]

    # 境界jの項別公比法における項mの吸熱応答係数の第一項 , m2K/W, [j, 12]
    phi_a1_js = [
        list(s3.get_area_weighted_averaged_values_two_dimension(
            v=np.array([bs.rfa1 for bs in bss2[gp_idxs == i]]),
            a=np.array([bs.area for bs in bss2[gp_idxs == i]])
        ))
        for i in np.unique(gp_idxs)
    ]

    # 室iの床面積, m2, [i]
    # TODO: is_solar_absorbed_inside_js を使用すべき。
    a_floor_is = np.array([
        np.sum(np.array([bs.area for bs in bss2 if bs.connected_room_id == i and bs.is_solar_absorbed_inside]))
        for i in range(number_of_spaces)
    ])

    # 床面積の合計, m2
    a_floor_total = float(np.sum(a_floor_is))

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
            room_name_is=room_names,
            a_floor_is=a_floor_is
        )
    ac_demand_is_ns = np.where(ac_demand_is_ns == 1, True, False)





    # 室iの統合された境界j*, IntegratedBoundaryクラス, [j*]
    # メモ　3つのIntegratedBoundariesクラスのリスト
    # IntegratedBoundaries クラスが複数のパラメータをもつ
    ibs = [s3.init_surface(bss=bs) for bs in bss]

    # 室iの在室者に対する境界j*の形態係数
    f_mrt_hum_is = np.concatenate([
        x35.get_f_mrt_hum_is(
            a_bdry_i_jstrs=ib.a_i_jstrs,
            is_solar_absorbed_inside_bdry_i_jstrs=ib.is_solar_absorbed_inside_i_jstrs
        ) for ib in ibs])

    qrtd_c_is = np.array([a15.get_qrtd_c(a_floor_i) for a_floor_i in a_floor_is])
    qmax_c_is = np.array([a15.get_qmax_c(qrtd_c_i) for qrtd_c_i in qrtd_c_is])
    qmin_c_is = np.array([a15.get_qmin_c() for qrtd_c_i in qrtd_c_is])
    Vmax_is = np.array([a15.get_Vmax(qrtd_c_i) for qrtd_c_i in qrtd_c_is])
    Vmin_is = np.array([a15.get_Vmin(Vmax_i) for Vmax_i in Vmax_is])

    # 暖房設備仕様の読み込み
    # 放射暖房有無（Trueなら放射暖房あり）
    is_radiative_heating_is = [a22.read_is_radiative_heating(room) for room in rooms]

    # 放射暖房最大能力[W]
    Lrcap_is = np.array([a22.read_radiative_heating_max_capacity(room) for room in rooms])

    equip_heating_radiative = []
    for i, is_radiative in enumerate(is_radiative_heating_is):
        if is_radiative:
            equip_heating_radiative.append({
                'installed': True,
                'max_capacity': Lrcap_is[i]
            })
        else:
            equip_heating_radiative.append({
                'installed': False
            })

    # 冷房設備仕様の読み込み

    # 放射冷房有無（Trueなら放射冷房あり）
    is_radiative_cooling_is = [a22.read_is_radiative_cooling(room) for room in rooms]

    # 放射冷房最大能力[W]
    radiative_cooling_max_capacity_is = np.array([a22.read_is_radiative_cooling(room) for room in rooms])

    equip_cooling_radiative = []
    for i, is_radiative in enumerate(is_radiative_cooling_is):
        if is_radiative:
            equip_cooling_radiative.append({
                'installed': True,
                'max_capacity': radiative_cooling_max_capacity_is[i]
            })
        else:
            equip_cooling_radiative.append({
                'installed': False
            })

    # 熱交換器種類
    heat_exchanger_type_is = [a22.read_heat_exchanger_type(room) for room in rooms]

    # 放射暖房の発熱部位の設定（とりあえず床発熱） 表7
    # TODO: 発熱部位を指定して、面積按分するように変更すべき。
    flr_jstrs = np.concatenate([
        a12.get_flr(
            A_i_g=np.array([a_j for a_j, connected_room_id_j in zip(a_js, connected_room_id_js) if connected_room_id_j == i]),
            A_fs_i=a_floor_is[i],
            is_radiative_heating=is_radiative_heating_is[i],
            is_solar_absorbed_inside=np.array([is_solar_absorbed_inside_j for is_solar_absorbed_inside_j, connected_room_id_j in zip(is_solar_absorbed_inside_js, connected_room_id_js) if connected_room_id_j == i])
        ) for i in range(number_of_spaces)])

    Beta_i = 0.0  # 放射暖房対流比率

    Beta_is = np.full(len(rooms), Beta_i)

    spaces = []

    for i in range(number_of_spaces):

        spaces.append({
            'id': room_ids[i],
            'name': room_names[i],
            'volume': v_room_cap_is[i],
            'c_value': c_value_is[i],
            'beta': Beta_is[i],
            'ventilation': {
                'mechanical': v_vent_ex_is[i]/3600,
                'next_spaces': v_int_vent_is.tolist()[i],
                'natural': v_ntrl_vent_is[i]
            },
            'furniture': {
                'heat_capacity': c_cap_frnt_is[i],
                'heat_cond': c_frnt_is[i],
                'moisture_capacity': g_f_is[i],
                'moisture_cond': c_x_is[i]
            },
            'equipment': {
                'heating': {
                    'radiative': equip_heating_radiative[i],
                    'convective': {}
                },
                'cooling': {
                    'radiative': equip_cooling_radiative[i],
                    'convective': {
                        'q_min': qmin_c_is[i],
                        'q_max': qmax_c_is[i],
                        'v_min': Vmin_is[i],
                        'v_max': Vmax_is[i]
                    }
                }
            }
        })

    bdrs = []
    for i in range(bs_n):

        bdrs.append({
            'id': i,
            'name': name_js[i],
            'sub_name': sub_name_js[i],
            'is_ground': {True: 'true', False: 'false'}[is_ground_js[i]],
            'connected_space_id': connected_room_id_js[i],
            'area': a_js[i],
            'phi_a0': phi_a0_js[i],
            'phi_a1': phi_a1_js[i],
            'phi_t0': phi_t0_js[i],
            'phi_t1': phi_t1_js[i],
            'r': rows_js[i],
            'h_i': h_i_js[i],
            'flr': flr_jstrs[i],
            'is_solar_absorbed': str(is_solar_absorbed_inside_js[i]),
            'f_mrt_hum': f_mrt_hum_is[i],
            'k_outside': h_td_js[i],
            'k_inside': k_ei_js[i]
        })

    wd = {
        'spaces': spaces,
        'boundaries': bdrs
    }

    with open(output_data_dir + '/mid_data_house.json', 'w') as f:
        json.dump(wd, f, indent=4)

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

    # ステップnの室iにおける窓の透過日射熱取得, W, [8760*4]
    with open(output_data_dir + '/mid_data_q_trs_sol.csv', 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(q_trs_sol_is_ns.T.tolist())

    # ステップnの室iにおける窓の透過日射熱取得, W, [8760*4]
    with open(output_data_dir + '/mid_data_q_trs_sol.csv', 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(q_trs_sol_is_ns.T.tolist())

    # ステップnの境界jにおける裏面等価温度, ℃, [j, 8760*4]
    with open(output_data_dir + '/mid_data_theta_o_sol.csv', 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(theta_o_sol_js_ns.T.tolist())


def get_v_int_vent_is(rooms: List[Dict]) -> np.ndarray:
    """

    Args:
        rooms: 部屋（入力）（辞書型）

    Returns:
        隣室iから室iへの機械換気量マトリクス, m3/s, [i, i]
            例えば、
                室0→室1:3.0
                室0→室2:4.0
                室1→室2:3.0
                室3→室1:1.5
                室3→室2:1.0
            の場合、
                [[0.0, 0.0, 0.0, 0.0],
                 [3.0, 0.0, 0.0, 1.5],
                 [4.0, 3.0, 0.0, 1.0],
                 [0.0, 0.0, 0.0, 0.0]]
    """

    # 室の数
    number_of_rooms = len(rooms)

    # 隣室iから室iへの機械換気量, m3/s, [i, i]
    v_int_vent_is = np.concatenate([[
        get_v_int_vent_i(
            next_vents=r['next_vent'],
            number_of_rooms=number_of_rooms
        )
    ] for r in rooms])

    return v_int_vent_is


def get_v_int_vent_i(next_vents: List[Dict], number_of_rooms: int) -> np.ndarray:
    """隣室から室への機械換気量の配列を取得する。

    Args:
        next_vents: 隣室からの機械換気量
            辞書型：
                上流側の室の名称
                換気量, m3/h
        number_of_rooms: 部屋の数

    Returns:
        隣室から室への機械換気量の配列, m3/s, [i]
            例えば、
                室インデックス0からの換気量が 10.0
                室インデックス1からの換気量が  0.0
                室インデックス2からの換気量が  8.0
                室インデックス3からの換気量が  6.0
            の場合は、
            [10.0, 0.0, 8.0, 6.0]

    Notes:
        室インデックスが重なって指定された場合はそこで指定された換気量は加算される。
            例えば、
                室インデックス0からの換気量が 10.0
                室インデックス1からの換気量が  0.0
                室インデックス2からの換気量が  8.0
                室インデックス3からの換気量が  6.0
                室インデックス0からの換気量が  2.0
            の場合は、
            [12.0, 0.0, 8.0, 6.0]

    """

    # 室iの隣室からの機械換気量, m3/s, [i]
    v_int_vent_i = np.zeros(number_of_rooms)

    for next_vent in next_vents:

        idx = {
            'main_occupant_room': 0,
            'other_occupant_room': 1,
            'non_occupant_room': 2,
            'underfloor': 3
        }[next_vent['upstream_room_type']]

        # m3/hからm3/sへの単位変換を行っている
        v_int_vent_i[idx] = v_int_vent_i[idx] + next_vent['volume'] / 3600.0

    return v_int_vent_i

