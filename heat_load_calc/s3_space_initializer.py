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
import heat_load_calc.s3_surface_loader as s3_loader

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

    # 室iの境界k,　boundaryクラスのリスト, [i, k]
    d_bdry_is_ks = [s3_loader.read_d_boundary_i_ks(input_dict_boundaries=r['boundaries']) for r in rooms]

    # 室iの統合された境界j*, IntegratedBoundaryクラス, [j*]
    ibs = [s3.init_surface(
        boundaries=d_boundary_i_ks,
        i_dn_ns=i_dn_ns,
        i_sky_ns=i_sky_ns,
        r_n_ns=r_n_ns,
        theta_o_ns=theta_o_ns,
        h_sun_ns=h_sun_ns,
        a_sun_ns=a_sun_ns) for d_boundary_i_ks in d_bdry_is_ks]

    # 統合された境界j*の数, [j*]
    number_of_bdry_is = np.array([len(ib.name_i_jstrs) for ib in ibs])

    # 統合された境界j*の名前, [j*]
    name_bdry_jstrs = np.concatenate([ib.name_i_jstrs for ib in ibs])

    # 統合された境界j*の総数
    number_of_boundaries = len(name_bdry_jstrs)

    # 統合された境界j*の名前2, [j*]
    sub_name_bdry_jstrs = np.concatenate([ib.sub_name_i_jstrs for ib in ibs])

    # 統合された境界j*の種類, [j*]
    type_bdry_jstrs = np.concatenate([ib.boundary_type_i_jstrs for ib in ibs])

    is_ground_jstrs = type_bdry_jstrs == BoundaryType.Ground

    # 統合された境界j*の面積, m2, [j*]
    a_bdry_jstrs = np.concatenate([ib.a_i_jstrs for ib in ibs])

    # 室iの統合された境界j*の温度差係数, [j*]
    h_bdry_jstrs = np.concatenate([ib.h_i_jstrs for ib in ibs])

    # 統合された境界j*の項別公比法における項mの公比, [j*, 12]
    r_bdry_jstrs_ms = np.concatenate([ib.Rows for ib in ibs])

    # 統合された境界j*の貫流応答係数の初項, [j*]
    phi_t0_bdry_jstrs = np.concatenate([ib.RFT0s for ib in ibs])

    # 統合された境界j*の吸熱応答係数の初項, m2K/W, [j*]
    phi_a0_bdry_jstrs = np.concatenate([ib.RFA0s for ib in ibs])

    # 統合された境界j*の項別公比法における項mの貫流応答係数の第一項, [j*,12]
    phi_t1_bdry_jstrs_ms = np.concatenate([ib.RFT1s for ib in ibs])

    # 統合された境界j*の項別公比法における項mの吸熱応答係数の第一項 , m2K/W, [j*, 12]
    phi_a1_bdry_jstrs_ms = np.concatenate([ib.RFA1s for ib in ibs])

    # ステップnの室iにおける窓の透過日射熱取得, W, [8760*4]
    q_trs_sol_is_ns = np.concatenate([[
        np.sum(
            s3.get_transmitted_solar_radiation(
                boundaries=d_bdry_i_ks, i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, h_sun_ns=h_sun_ns, a_sun_ns=a_sun_ns
            ), axis=0)
    ] for d_bdry_i_ks in d_bdry_is_ks])

    print(np.array([np.sum(ib.q_trs_i_jstrs_ns, axis=0) for ib in ibs]))
    print(q_trs_sol_is_ns)
    print(np.sum(np.array([np.sum(ib.q_trs_i_jstrs_ns, axis=0) for ib in ibs]), axis=1))
    print(np.sum(q_trs_sol_is_ns, axis=1))
    q_trs_sol_is_ns = np.array([np.sum(ib.q_trs_i_jstrs_ns, axis=0) for ib in ibs])

    # 室iの床面積, m2, [i]
    a_floor_is = np.array([
        np.sum(ib.a_i_jstrs[ib.is_solar_absorbed_inside_i_jstrs])
        for ib in ibs])

    # 床面積の合計, m2
    a_floor_total = float(np.sum(a_floor_is))

    # 居住人数
    n_p = residents_number.get_total_number_of_residents(a_floor_total=a_floor_total)
#    n_p = 4.0

    # 以下のスケジュールの取得, [i, 365*96]
    #   ステップnの室iにおける人体発熱を除く内部発熱, W, [i, 8760*4]
    # 　　ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [i, 8760*4]
    #   ステップnの室iにおける局所換気量, m3/s, [i, 8760*4]
    #   ステップnの室iにおける在室人数, [i, 8760*4]
    #   ステップnの室iにおける空調割合, [i, 8760*4]
    q_gen_is_ns, x_gen_is_ns, v_mec_vent_local_is_ns, n_hum_is_ns, ac_demand_is_ns = schedule_loader.get_compiled_schedules(n_p=n_p, room_name_is=room_names)
    ac_demand_is_ns = np.where(ac_demand_is_ns == 1, True, False)

    # TODO: この係数は本来であれば入力ファイルに書かれないといけない。
    # 裏面がどの境界の表面に属するのかを表す
    k_ei_id_js_js = [
        None, None, None, None, None, None, 6, None, 30, 17,
        22, None, None, None, None, None, 31, 9, None, None,
        None, 21, 10, None, None, None, None, None, 28, None,
        8, 16
    ]
    #　ある境界表面が境界の裏面に与える影響
    k_ei_coef_js_js = [
        None, None, None, None, None, None, 0.3, None, 1.0, 1.0,
        1.0, None, None, None, None, None, 1.0, 1.0, None, None,
        None, 0.3, 1.0, None, None, None, None, None, 0.3, None,
        1.0, 1.0
    ]
    k_ei_js = [
        None,
        None,
        None,
        None,
        None,
        None,
        {'id': 6, 'coef': 0.3},
        None,
        {'id': 30, 'coef': 1.0},
        {'id': 17, 'coef': 1.0},
        {'id': 22, 'coef': 1.0},
        None,
        None,
        None,
        None,
        None,
        {'id': 31, 'coef': 1.0},
        {'id': 9, 'coef': 1.0},
        None,
        None,
        None,
        {'id': 21, 'coef': 0.3},
        {'id': 10, 'coef': 1.0},
        None,
        None,
        None,
        None,
        None,
        {'id': 28, 'coef': 0.3},
        None,
        {'id': 8, 'coef': 1.0},
        {'id': 16, 'coef': 1.0},
    ]

    idx_bdry_is = np.insert(np.cumsum(number_of_bdry_is), 0, 0)

    split_indices = np.cumsum(number_of_bdry_is)[0:-1]

    space_idx_bdry_jstrs = np.zeros(sum(number_of_bdry_is))
    for i, ib in enumerate(ibs):
        space_idx_bdry_jstrs[idx_bdry_is[i]:idx_bdry_is[i+1]] = i

    # 室iの在室者に対する境界j*の形態係数
    f_mrt_hum_is = np.concatenate([
        x35.get_f_mrt_hum_is(
            a_bdry_i_jstrs=ib.a_i_jstrs,
            is_solar_absorbed_inside_bdry_i_jstrs=ib.is_solar_absorbed_inside_i_jstrs
        ) for ib in ibs])

    theta_o_sol_js_ns = np.concatenate([ib.theta_o_sol_i_jstrs_ns for ib in ibs])

    h_def_js = np.concatenate([ib.h_i_jstrs for ib in ibs])

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
    flr_jstrs = np.concatenate([
        a12.get_flr(
            A_i_g=ib.a_i_jstrs,
            A_fs_i=a_floor_is[i],
            is_radiative_heating=is_radiative_heating_is[i],
            is_solar_absorbed_inside=ib.is_solar_absorbed_inside_i_jstrs
        ) for i, ib in enumerate(ibs)])

    # 室iの統合された境界j*の室内側表面総合熱伝達率, W/m2K, [j*]
    h_i_bnd_jstrs = np.concatenate([ib.h_i_i_jstrs for ib in ibs])

    is_solar_absorbed_inside_is_jstrs = np.concatenate([ib.is_solar_absorbed_inside_i_jstrs for ib in ibs])

    Beta_i = 0.0  # 放射暖房対流比率

    Beta_is = np.full(len(rooms), Beta_i)

    p = np.zeros((number_of_spaces, sum(number_of_bdry_is)))
    for i in range(number_of_spaces):
        p[i, idx_bdry_is[i]:idx_bdry_is[i + 1]] = 1.0

    spaces = []
    for i in range(number_of_spaces):
        spaces.append({
            'id': i,
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
    for i in range(number_of_boundaries):
        bdrs.append({
            'id': i,
            'name': name_bdry_jstrs[i],
            'sub_name': sub_name_bdry_jstrs[i],
            'is_ground': {True: 'true', False: 'false'}[is_ground_jstrs[i]],
            'connected_space_id': int(space_idx_bdry_jstrs[i]),
            'area': a_bdry_jstrs[i],
            'phi_a0': phi_a0_bdry_jstrs[i],
            'phi_a1': list(phi_a1_bdry_jstrs_ms[i]),
            'phi_t0': phi_t0_bdry_jstrs[i],
            'phi_t1': list(phi_t1_bdry_jstrs_ms[i]),
            'r': list(r_bdry_jstrs_ms[i]),
            'h_i': h_i_bnd_jstrs[i],
            'flr': flr_jstrs[i],
            'is_solar_absorbed': str(is_solar_absorbed_inside_is_jstrs[i]),
            'f_mrt_hum': f_mrt_hum_is[i],
            'k_outside': h_def_js[i],
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

