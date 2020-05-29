import numpy as np
from typing import Dict, List
import json
import csv

import a9_rear_surface_equivalent_temperature as a9
import a12_indoor_radiative_heat_transfer as a12
import a14_furniture as a14
import a15_air_flow_rate_rac as a15
import a16_blowing_condition_rac as a16
import a18_initial_value_constants as a18
import a1_calculation_surface_temperature as a1
import a20_room_spec as a20
import a21_next_vent_spec as a21
import a22_radiative_heating_spec as a22
import a23_surface_heat_transfer_coefficient as a23
import a34_building_part_summarize as a34
import a38_schedule as a38
from a39_global_parameters import SpaceType
from a39_global_parameters import BoundaryType

import a39_global_parameters as a39

from s3_space_loader import PreCalcParameters
from s3_surface_loader import Boundary
import s3_surface_initializer as s3
from s3_surface_initializer import IntegratedBoundaries
import s3_space_loader as s3sl
import s3_surface_loader
import s4_1_sensible_heat as s41

import x_35_occupants as x35


def make_house(d, i_dn_ns, i_sky_ns, r_n_ns, theta_o_ns, h_sun_ns, a_sun_ns):

    rooms = d['rooms']

    # 室の数
    number_of_spaces = len(rooms)

    # 室iの名称, [i]
    room_names = [r['name'] for r in rooms]

    # 室iのタイプ
    #   main_occupant_room: 主たる居室
    #   other_occupant_room: その他の居室
    #   non_occupant_room: 非居室
    #   underfloor: 床下空間
    # jsonファイルではstr型を読み込んで、列挙型に変換をかけている。
    room_type_is = [{
        1: SpaceType.MAIN_HABITABLE_ROOM,
        2: SpaceType.OTHER_HABITABLE_ROOM,
        3: SpaceType.NON_HABITABLE_ROOM,
        4: SpaceType.UNDERFLOOR
    }[room['room_type']] for room in rooms]

    # 室iの気積, m3, [i]
    v_room_cap_is = np.array([r['volume'] for r in rooms])

    # 室iの外気からの機械換気量, m3/h, [i]
    v_vent_ex_is = np.array([r['vent'] for r in rooms])

    # 室iのC値, [i]
    c_value_is = np.array([r['c_value'] for r in rooms])

    # 室iの自然風利用時の換気回数, 1/h, [i]
    n_ntrl_vent_is = np.array([r['natural_vent_time'] for r in rooms])

    # 室iの隣室からの機会書き量, m3/h, [i, i]
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
    d_bdry_is_ks = [s3_surface_loader.read_d_boundary_i_ks(input_dict_boundaries=r['boundaries']) for r in rooms]

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

    # TODO 居住人数。これは1～4の値（小数値。整数ではない。）が入る。床面積の合計から推定すること。
    n_p = 4.0

    # 以下のスケジュールの取得, [i, 365*96]
    #   局所換気量, m3/h
    #   TODO: 単位を確認する
    #   機器発熱, W
    #   調理発熱, W
    #   調理発湿, kg/s
    #   照明発熱, W/m2
    #   TODO 床面積を乗じるのを忘れないように
    #   ステップnの室iにおける在室人数, [8760*4]
    #   ON/OFF
    v_mec_vent_local_is_ns,\
    q_gen_app_is_ns,\
    q_gen_ckg_is_ns,\
    x_gen_ckg_is_ns,\
    q_gen_lght_is_ns,\
    n_hum_is_ns,\
    ac_demand_is_ns = a38.get_v_mec_vent_local_is_ns(n_p=n_p, room_name_is=room_names)

    # 内部発熱, W
    q_gen_is_ns = q_gen_app_is_ns + q_gen_ckg_is_ns + q_gen_lght_is_ns

    # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [8760*4]
#    x_gen_is_ns = x_gen_ckg_is_ns / 1000.0 / 3600.0
    x_gen_is_ns = x_gen_ckg_is_ns

    k_ei_is = np.concatenate([
        a9.get_k_ei_i(
            boundary_type_i_jstrs=ib.boundary_type_i_jstrs,
            h_bnd_i_jstrs=ib.h_i_jstrs,
            i=i,
            next_room_type_bnd_i_jstrs=ib.next_room_type_i_jstrs,
            number_of_boundaries=number_of_bdry_is[i],
            number_of_spaces=number_of_spaces
        ) for i, ib in enumerate(ibs)
    ])

    idx_bdry_is = np.insert(np.cumsum(number_of_bdry_is), 0, 0)

    split_indices = np.cumsum(number_of_bdry_is)[0:-1]

    space_idx_bdry_jstrs = np.zeros(sum(number_of_bdry_is))
    for i, ib in enumerate(ibs):
        space_idx_bdry_jstrs[idx_bdry_is[i]:idx_bdry_is[i+1]] = i

    # 室iの在室者に対する境界j*の形態係数
    f_mrt_hum_is = [
        x35.get_f_mrt_hum_is(
            a_bdry_i_jstrs=ib.a_i_jstrs,
            is_solar_absorbed_inside_bdry_i_jstrs=ib.is_solar_absorbed_inside_i_jstrs
        ) for ib in ibs]

    # 平均放射温度計算時の各部位表面温度の重み計算 式(101)
#    f_mrt_hum_jstrs = np.zeros((number_of_spaces, sum(number_of_bdry_is)))
#    for i, f_mrt_hum_i in enumerate(f_mrt_hum_is):
#        f_mrt_hum_jstrs[i, idx_bdry_is[i]:idx_bdry_is[i+1]] = f_mrt_hum_i

    f_mrt_hum_jstrs = np.zeros((number_of_spaces, sum(number_of_bdry_is)))
    for i, f_mrt_hum_i in enumerate(f_mrt_hum_is):
        f_mrt_hum_jstrs[i, space_idx_bdry_jstrs==i] = f_mrt_hum_i

    # 室iの床面積の合計, m2, [i]
    a_floor_is = np.array([
        np.sum(ib.a_i_jstrs[ib.is_solar_absorbed_inside_i_jstrs])
        for ib in ibs])

    # ステップnの室iの集約された境界j*の外乱による裏面温度, degree C, [j*, 8760*4]
    theta_dstrb_is_jstrs_ns = np.concatenate([
        ib.theta_o_sol_i_jstrs_ns * ib.h_i_jstrs.reshape(-1, 1)
        for ib in ibs])

    qrtd_c_is = np.array([a15.get_qrtd_c(a_floor_i) for a_floor_i in a_floor_is])
    qmax_c_is = np.array([a15.get_qmax_c(qrtd_c_i) for qrtd_c_i in qrtd_c_is])
    qmin_c_is = np.array([a15.get_qmin_c() for qrtd_c_i in qrtd_c_is])
    Vmax_is = np.array([a15.get_Vmax(qrtd_c_i) for qrtd_c_i in qrtd_c_is])
    Vmin_is = np.array([a15.get_Vmin(Vmax_i) for Vmax_i in Vmax_is])

    get_vac_xeout_def_is = [
        a16.make_get_vac_xeout_def(Vmin=Vmin_i, Vmax=Vmax_i, qmin_c=qmin_c_i, qmax_c=qmax_c_i)
        for Vmin_i, Vmax_i, qmin_c_i, qmax_c_i in zip(Vmin_is, Vmax_is, qmin_c_is, qmax_c_is)
    ]

    # 暖房設備仕様の読み込み
    # 放射暖房有無（Trueなら放射暖房あり）
    is_radiative_heating_is = [a22.read_is_radiative_heating(room) for room in rooms]

    # 放射暖房最大能力[W]
    Lrcap_is = np.array([a22.read_radiative_heating_max_capacity(room) for room in rooms])

    # 冷房設備仕様の読み込み

    # 放射冷房有無（Trueなら放射冷房あり）
    is_radiative_cooling_is = [a22.read_is_radiative_cooling(room) for room in rooms]

    # 放射冷房最大能力[W]
    radiative_cooling_max_capacity_is = np.array([a22.read_is_radiative_cooling(room) for room in rooms])

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

    is_solar_absorbed_inside_is_jstrs = [ib.is_solar_absorbed_inside_i_jstrs for ib in ibs]

    # 室iの統合された境界j*における室の透過日射熱取得のうちの吸収日射量, W/m2, [j*, 8760*4]
    q_sol_floor_jstrs_ns = np.concatenate([
        a12.get_q_sol_floor_i_jstrs_ns(
            q_trs_sol_i_ns=q_trs_sol_is_ns[i],
            a_bnd_i_jstrs=np.split(a_bdry_jstrs, split_indices)[i],
            is_solar_absorbed_inside_bnd_i_jstrs=is_solar_absorbed_inside_is_jstrs[i]
        ) for i in range(len(rooms))])

    # ステップnの室iにおける家具の吸収日射量, W, [i, 8760*4]
    q_sol_frnt_is_ns = np.concatenate([[
        a12.get_q_sol_frnt_i_ns(q_trs_sol_i_ns=q_trs_sol_is_ns[i])
    ] for i in range(len(rooms))
    ])

    Beta_i = 0.0  # 放射暖房対流比率

    Beta_is = np.full(len(rooms), Beta_i)

    p = np.zeros((number_of_spaces, sum(number_of_bdry_is)))
    for i in range(number_of_spaces):
        p[i, idx_bdry_is[i]:idx_bdry_is[i + 1]] = 1.0

    def get_vac_xeout_is(lcs_is_n, theta_r_is_npls, operation_mode_is_n):

        vac_is_n = []
        xeout_is_n = []

        for lcs_i_n, theta_r_i_npls, operation_mode_i_n, get_vac_xeout_def_i in zip(lcs_is_n, theta_r_is_npls, operation_mode_is_n, get_vac_xeout_def_is):
            Vac_n_i, xeout_i_n = get_vac_xeout_def_i(lcs_i_n, theta_r_i_npls, operation_mode_i_n)
            vac_is_n.append(Vac_n_i)
            xeout_is_n.append(xeout_i_n)

        return np.array(vac_is_n), np.array(xeout_is_n)

    spaces = []
    for i in range(number_of_spaces):
        spaces.append({
            'id': i,
            'name': room_names[i],
            'type': str(room_type_is[i]),
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
            }
        })

    bdrs = []
    for i in range(number_of_boundaries):
        bdrs.append({
            'id': i,
            'name': name_bdry_jstrs[i],
            'sub_name': sub_name_bdry_jstrs[i],
            'type': str(type_bdry_jstrs[i]),
            'is_ground': {True: 'true', False: 'false'}[is_ground_jstrs[i]],
            'connected_space_id': int(space_idx_bdry_jstrs[i]),
            'area': a_bdry_jstrs[i],
            'phi_a0': phi_a0_bdry_jstrs[i],
            'phi_a1': list(phi_a1_bdry_jstrs_ms[i]),
            'phi_t0': phi_t0_bdry_jstrs[i],
            'phi_t1': list(phi_t1_bdry_jstrs_ms[i]),
            'r': list(r_bdry_jstrs_ms[i]),
            'h_i': h_i_bnd_jstrs[i],
            'flr': flr_jstrs[i]
        })

    wd = {
        'spaces': spaces,
        'boundaries': bdrs
    }

    with open('mid_data_house.json', 'w') as f:
        json.dump(wd, f, indent=4)

    # ステップnの室iにおける局所換気量, m3/s, [i, 8760*4]
    with open('mid_data_local_vent.csv', 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows((v_mec_vent_local_is_ns / 3600.0).T.tolist())

    # ステップnの室iにおける内部発熱, W, [8760*4]
    with open('mid_data_heat_generation.csv', 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(q_gen_is_ns.T.tolist())

    # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [8760*4]
    with open('mid_data_moisture_generation.csv', 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(x_gen_is_ns.T.tolist())

    # ステップnの室iにおける在室人数, [8760*4]
    with open('mid_data_occupants.csv', 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(n_hum_is_ns.T.tolist())

    # ステップnの室iにおける空調需要, [8760*4]
    with open('mid_data_ac_demand.csv', 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(ac_demand_is_ns.T.tolist())

    # region Spacesへの引き渡し
    spaces2 = make_pre_calc_parameters(
        k_ei_is,
        number_of_bdry_is,
        f_mrt_hum_jstrs,
        theta_dstrb_is_jstrs_ns,
        q_trs_sol_is_ns,
        get_vac_xeout_def_is,
        is_radiative_heating_is,
        is_radiative_cooling_is,
        Lrcap_is,
        radiative_cooling_max_capacity_is,
        q_sol_floor_jstrs_ns,
        q_sol_frnt_is_ns,
        p,
        get_vac_xeout_is
    )
    # endregion

    return spaces2


def make_pre_calc_parameters(
    k_ei_is,
    number_of_bdry_is,
    f_mrt_hum_jstrs,
    theta_dstrb_is_jstrs_ns,
    q_trs_sol_is_ns,
    get_vac_xeout_def_is,
    is_radiative_heating_is,
    is_radiative_cooling_is,
    Lrcap_is,
    radiative_cooling_max_capacity_is,
    q_sol_floor_jstrs_ns,
    q_sol_frnt_is_ns,
    p,
    get_vac_xeout_is
):

    with open('mid_data_house.json') as f:
        rd = json.load(f)

    # region spaces の読み込み

    # spaces の取り出し
    ss = rd['spaces']

    # id, [i]
    spaces_id_is = [s['id'] for s in ss]

    # 空間iの名前, [i]
    room_names = [s['name'] for s in ss]

    # 空間iの気積, m3, [i]
    v_room_cap_is = np.array([s['volume'] for s in ss])

    # 空間iのC値, [i]
    c_value_is = np.array([s['c_value'] for s in ss])

    # 室iに設置された放射暖房の対流成分比率, [i]
    beta_is = np.array([s['beta'] for s in ss])

    # 室iの機械換気量（局所換気を除く）, m3/h, [i]
    v_vent_ex_is = np.array([s['ventilation']['mechanical'] for s in ss])

    v_int_vent_is = np.array([s['ventilation']['next_spaces'] for s in ss])

    v_ntrl_vent_is = np.array([s['ventilation']['natural'] for s in ss])

    # 室iの家具等の熱容量, J/K
    c_cap_frnt_is = np.array([s['furniture']['heat_capacity'] for s in ss])

    # 室iの家具等と空気間の熱コンダクタンス, W/K, [i]
    c_frnt_is = np.array([s['furniture']['heat_cond'] for s in ss])

    # 室iの家具等の湿気容量, kg/m3 kg/kgDA, [i]
    g_f_is = np.array([s['furniture']['moisture_capacity'] for s in ss])

    # 室iの家具等と空気間の湿気コンダクタンス, kg/s kg/kgDA
    c_x_is = np.array([s['furniture']['moisture_cond'] for s in ss])

    # endregion

    # region boundaries の読み込み

    # boundaries の取り出し
    bs = rd['boundaries']

    # id, [j]
    bdry_id_js = [b['id'] for b in bs]

    # 名前, [j]
    name_bdry_js = [b['name'] for b in bs]

    # 名前2, [j]
    sub_name_bdry_js= [b['sub_name'] for b in bs]

    # 地盤かどうか, [j]
    is_ground_js = [{'true': True, 'false': False}[b['is_ground']] for b in bs]

    # 隣接する空間のID, [j]
    connected_space_id_js = np.array([b['connected_space_id'] for b in bs])

    # 境界jの面積, m2, [j]
    a_srf_js = np.array([b['area'] for b in bs])

    # 境界jの吸熱応答係数の初項, m2K/W, [j]
    phi_a0_js = np.array([b['phi_a0'] for b in bs])

    # 境界jの項別公比法における項mの吸熱応答係数の第一項 , m2K/W, [j, 12]
    phi_a1_js_ms = np.array([b['phi_a1'] for b in bs])

    # 境界jの貫流応答係数の初項, [j]
    phi_t0_js = np.array([b['phi_t0'] for b in bs])

    # 境界jの項別公比法における項mの貫流応答係数の第一項, [j, 12]
    phi_t1_js_ms = np.array([b['phi_t1'] for b in bs])

    # 境界jの項別公比法における項mの公比, [j, 12]
    r_js_ms = np.array([b['r'] for b in bs])

    # 境界jの室内側表面総合熱伝達率, W/m2K, [j]
    h_i_js = np.array([b['h_i'] for b in bs])

    # 境界jの室に設置された放射暖房の放熱量のうち放射成分に対する境界jの室内側吸収比率
    flr_js = np.array([b['flr'] for b in bs])

    # endregion

    # region スケジュール化されたデータの読み込み

    # ステップnの室iにおける局所換気量, m3/s, [i, 8760*4]
    with open('mid_data_local_vent.csv', 'r') as f:
        r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        v_mec_vent_local_is_ns = np.array([row for row in r]).T

    # ステップnの室iにおける内部発熱, W, [8760*4]
    with open('mid_data_heat_generation.csv', 'r') as f:
        r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        q_gen_is_ns = np.array([row for row in r]).T

    # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [8760*4]
    with open('mid_data_moisture_generation.csv', 'r') as f:
        r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        x_gen_is_ns = np.array([row for row in r]).T

    # ステップnの室iにおける在室人数, [8760*4]
    with open('mid_data_occupants.csv', 'r') as f:
        r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        n_hum_is_ns = np.array([row for row in r]).T

    # ステップnの室iにおける空調需要, [8760*4]
    with open('mid_data_ac_demand.csv', 'r') as f:
        r = csv.reader(f)
        ac_demand_is_ns2 = np.array([row for row in r]).T
    # ｓｔｒ型からbool型に変更
    ac_demand_is_ns = np.vectorize(lambda x: {'True': True, 'False': False}[x])(ac_demand_is_ns2)

    # endregion

    # region 読み込んだ値から新たに係数を作成する

    # Spaceの数
    number_of_spaces = len(ss)

    # 室iの空気の熱容量, J/K
    c_room_is = v_room_cap_is * a39.get_rho_air() * a39.get_c_air()

    # 境界jの室内側表面放射熱伝達率, W/m2K, [j]
    h_r_js = a12.get_hr_i_k_n(a_bdry_jstrs=a_srf_js, space_idx_bdry_jstrs=connected_space_id_js, number_of_spaces=number_of_spaces)

    # 平均放射温度計算時の各部位表面温度の重み, [i, j]
    f_mrt_is_js =a12.get_f_mrt_is_js(a_bdry_jstrs=a_srf_js, h_r_bnd_jstrs=h_r_js, p=p)

    # 境界jの室内側表面対流熱伝達率, W/m2K, [j]
    h_c_js = np.clip(h_i_js - h_r_js, 0, None)

    # ステップnの室iにおける機械換気量（全般換気量+局所換気量）, m3/s
    v_mec_vent_is_ns = v_vent_ex_is[:, np.newaxis] + v_mec_vent_local_is_ns

    # AX, [j, j]
    ax_js_js = np.diag(1.0 + phi_a0_js * h_i_js) - np.dot(p.T * (phi_a0_js * h_r_js).reshape(-1,1), f_mrt_is_js)

    # AX^-1, [j, j]
    ivs_x_js_js = np.linalg.inv(ax_js_js)

    # FIA, [j]
    fia_js = phi_a0_js * h_c_js

    # CRX, W, [j, 8760*4]
    crx_js_ns = phi_t0_js[:, np.newaxis] * theta_dstrb_is_jstrs_ns + q_sol_floor_jstrs_ns * phi_a0_js[:, np.newaxis]

    # FLB, K/W, [j]
    flb_js = phi_a0_js * flr_js * (1.0 - np.dot(p.T, beta_is.reshape(-1, 1)).flatten()) / a_srf_js

    # WSR, [j]
    wsr_js = np.dot(ivs_x_js_js, fia_js.reshape(-1, 1)).flatten()

    # WSC, W, [j, 8760*4]
    wsc_js_ns = np.dot(ivs_x_js_js, crx_js_ns)

    # WSB, K/W, [j]
    wsb_js = np.dot(ivs_x_js_js, flb_js.reshape(-1, 1)).flatten()

    # BRL, [i]
    brl_is = np.dot(p, (h_c_js * a_srf_js * wsb_js).reshape(-1, 1)).flatten() + beta_is

    # BRM(通風なし), W/K, [i]
    brm_noncv_is = (
            c_room_is/900
            + np.dot(p, (a_srf_js * h_c_js * (1.0 - wsr_js)).reshape(-1, 1)).flatten()
            + v_int_vent_is.sum(axis=1) * a18.get_c_air() * a18.get_rho_air()
            + c_cap_frnt_is * c_frnt_is / (c_cap_frnt_is + c_frnt_is * 900)
    )[:, np.newaxis] + v_mec_vent_is_ns * a18.get_c_air() * a18.get_rho_air()

    # endregion

    pre_calc_parameters = PreCalcParameters(
        number_of_spaces=number_of_spaces,
        space_names=room_names,
        v_room_cap_is=v_room_cap_is,
        g_f_is=g_f_is,
        c_x_is=c_x_is,
        c_room_is=c_room_is,
        c_cap_frnt_is=c_cap_frnt_is,
        c_frnt_is=c_frnt_is,
        v_int_vent_is=v_int_vent_is,
        name_bdry_jstrs=name_bdry_js,
        sub_name_bdry_jstrs=sub_name_bdry_js,
        a_bdry_jstrs=a_srf_js,
        v_mec_vent_is_ns=v_mec_vent_is_ns,
        q_gen_is_ns=q_gen_is_ns,
        n_hum_is_ns=n_hum_is_ns,
        x_gen_is_ns=x_gen_is_ns,
        k_ei_is=k_ei_is,
        number_of_bdry_is=number_of_bdry_is,
        f_mrt_hum_jstrs=f_mrt_hum_jstrs,
        theta_dstrb_is_jstrs_ns=theta_dstrb_is_jstrs_ns,
        r_bdry_jstrs_ms=r_js_ms,
        phi_t0_bdry_jstrs=phi_t0_js,
        phi_a0_bdry_jstrs=phi_a0_js,
        phi_t1_bdry_jstrs_ms=phi_t1_js_ms,
        phi_a1_bdry_jstrs_ms=phi_a1_js_ms,
        q_trs_sol_is_ns=q_trs_sol_is_ns,
        v_ntrl_vent_is=v_ntrl_vent_is,
        ac_demand_is_ns=ac_demand_is_ns,
        get_vac_xeout_def_is=get_vac_xeout_def_is,
        is_radiative_heating_is=is_radiative_heating_is,
        is_radiative_cooling_is=is_radiative_cooling_is,
        Lrcap_is=Lrcap_is,
        radiative_cooling_max_capacity_is=radiative_cooling_max_capacity_is,
        flr_jstrs=flr_js,
        h_r_bnd_jstrs=h_r_js,
        h_c_bnd_jstrs=h_c_js,
        f_mrt_jstrs=f_mrt_is_js,
        q_sol_floor_jstrs_ns=q_sol_floor_jstrs_ns,
        q_sol_frnt_is_ns=q_sol_frnt_is_ns,
        Beta_is=beta_is,
        WSR_is_k=wsr_js,
        WSB_is_k=wsb_js,
        BRMnoncv_is=brm_noncv_is,
        ivs_x_is=ivs_x_js_js,
        brl_is=brl_is,
        p=p,
        get_vac_xeout_is=get_vac_xeout_is,
        is_ground_js=is_ground_js,
        wsc_js_ns=wsc_js_ns
    )

    return pre_calc_parameters


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

