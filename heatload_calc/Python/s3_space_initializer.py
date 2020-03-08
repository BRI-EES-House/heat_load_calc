import math
import numpy as np
from typing import Dict, List
import json

import a12_indoor_radiative_heat_transfer as a12
import a14_furniture as a14
import a15_air_flow_rate_rac as a15
import a18_initial_value_constants as a18
import a1_calculation_surface_temperature as a1
import a20_room_spec as a20
import a21_next_vent_spec as a21
import a22_radiative_heating_spec as a22
import a23_surface_heat_transfer_coefficient as a23
import a34_building_part_summarize as a34
import a38_schedule as a38
from a39_global_parameters import SpaceType

from s3_space_loader import Space, Spaces
from s3_surface_loader import Boundary
import s3_surface_initializer as s3
from s3_surface_initializer import IntegratedBoundaries
import s3_space_loader as s3sl
import s3_surface_loader
import s4_1_sensible_heat as s41


def make_house(d, i_dn_ns, i_sky_ns, r_n_ns, theta_o_ns, h_sun_ns, a_sun_ns):

    # 空気の比熱, J/kg K
    ca = a18.get_c_air()

    # 空気の密度, kg/m3
    rhoa = a18.get_rho_air()

    rooms = d['rooms']

    # 室の数
    number_of_spaces = len(rooms)

    # 室iの名称, [i]
    room_names = [r['name'] for r in rooms]

    # 室iの気積, m3, [i]
    v_room_cap_is = np.array([r['volume'] for r in rooms])

    # 室iの空気の熱容量, J/K
    c_room_is = v_room_cap_is * rhoa * ca

    # 室iの家具等の熱容量, J/K
    c_cap_frnt_is = a14.get_c_cap_frnt_is(v_room_cap_is)

    # 室iの家具等と空気間の熱コンダクタンス, W/K, [i]
    c_frnt_is = a14.get_Cfun(c_cap_frnt_is)

    # 室iの家具等の湿気容量, kg/m3 kg/kgDA, [i]
    g_f_is = a14.get_g_f_is(v_room_cap_is)  # i室の備品類の湿気容量

    # 室iの家具等と空気間の湿気コンダクタンス, kg/s kg/kgDA
    c_x_is = a14.get_c_x_is(g_f_is)

    # 室iの気積, m3, [i, i]
    v_int_vent_is = get_v_int_vent_is(rooms)

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

    # 統合された境界j*の名前, [j*]
    name_bdry_jstrs = np.concatenate([ib.name_i_jstrs for ib in ibs])

    # 統合された境界j*の名前2, [j*]
    sub_name_bdry_jstrs = np.concatenate([ib.sub_name_i_jstrs for ib in ibs])

    # 統合された境界j*の種類, [j*]
    type_bdry_jstrs = np.concatenate([ib.boundary_type_i_jstrs for ib in ibs])

    # 統合された境界j*の面積, m2, [j*]
    a_bdry_jstrs = np.concatenate([ib.a_i_jstrs for ib in ibs])

    # 室iの統合された境界j*の温度差係数, [j*]
    h_bdry_jstrs = np.concatenate([ib.h_i_jstrs for ib in ibs])




    spaces = []
    for i, room in enumerate(rooms):
        space = make_space(room=room, i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, r_n_ns=r_n_ns, theta_o_ns=theta_o_ns, h_sun_ns=h_sun_ns, a_sun_ns=a_sun_ns, i=i, d_bdry_is_ks=d_bdry_is_ks, ibs=ibs)
        spaces.append(space)

    spaces2 = Spaces(
        spaces=spaces,
        number_of_spaces=number_of_spaces,
        space_names=room_names,
        v_room_cap_is=v_room_cap_is,
        g_f_is=g_f_is,
        c_x_is=c_x_is,
        c_room_is=c_room_is,
        c_cap_frnt_is=c_cap_frnt_is,
        c_frnt_is=c_frnt_is,
        v_int_vent_is=v_int_vent_is,
        name_bdry_jstrs=name_bdry_jstrs,
        sub_name_bdry_jstrs=sub_name_bdry_jstrs,
        type_bdry_jstrs=type_bdry_jstrs,
        a_bdry_jstrs=a_bdry_jstrs,
        h_bdry_jstrs=h_bdry_jstrs
    )

    return spaces2


def make_space(room: Dict,
               i_dn_ns: np.ndarray, i_sky_ns: np.ndarray, r_n_ns: np.ndarray, theta_o_ns: np.ndarray,
               h_sun_ns: np.ndarray, a_sun_ns: np.ndarray, i: int, d_bdry_is_ks: List[Boundary], ibs: List[IntegratedBoundaries]):

    # 室iの境界k
    d_boundary_i_ks = d_bdry_is_ks[i]

    boundary_type_i_jstrs = ibs[i].boundary_type_i_jstrs  # 済
    a_bnd_i_jstrs = ibs[i].a_i_jstrs  # 済

    # 室iの統合された境界j*の温度差係数, [j*]
    h_bnd_i_jstrs = ibs[i].h_i_jstrs  # 済

    # 室iの統合された境界j*の隣室タイプ, [j*]
    next_room_type_bnd_i_jstrs = ibs[i].next_room_type_i_jstrs

    # 室iの統合された境界j*の室内侵入日射吸収の有無, [j*]
    is_solar_absorbed_inside_bnd_i_jstrs = ibs[i].is_solar_absorbed_inside_i_jstrs

    # 室iの統合された境界j*の室内側表面総合熱伝達率, W/m2K, [j*]
    h_i_bnd_i_jstrs = ibs[i].h_i_i_jstrs

    # 室iの統合された境界j*の傾斜面のステップnにおける相当外気温度, ℃, [j*, 8760*4]
    theta_o_sol_bnd_i_jstrs_ns = ibs[i].theta_o_sol_i_jstrs_ns

    # 室iの統合された境界j*の応答係数法（項別公比法）における根の数, [j*]
    n_root_bnd_i_jstrs = ibs[i].n_root_i_jstrs

    row_bnd_i_jstrs = ibs[i].Rows
    rft0_bnd_i_jstrs = ibs[i].RFT0s
    rfa0_bnd_i_jstrs = ibs[i].RFA0s
    rft1_bnd_i_jstrs = ibs[i].RFT1s
    rfa1_bnd_i_jstrs = ibs[i].RFA1s
    n_bnd_i_jstrs = ibs[i].NsurfG_i

    # ステップnの室iにおける窓の透過日射熱取得, W, [8760*4]
    q_trs_sol_i_ns = np.sum(
        s3.get_transmitted_solar_radiation(
            boundaries=d_boundary_i_ks, i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, h_sun_ns=h_sun_ns, a_sun_ns=a_sun_ns
        ), axis=0)

    # 室iの自然風利用時の換気回数, 1/h
    n_ntrl_vent_i = room['natural_vent_time']

    # TODO 居住人数。これは1～4の値（小数値。整数ではない。）が入る。床面積の合計から推定すること。
    n_p = 4.0

    # スケジュールの読み込み
    js = open('schedules.json', 'r', encoding='utf-8')
    d_json = json.load(js)
    calendar = np.array(d_json['calendar'])

    # 室iの名称
    name_i = room['name']

    # 室iのタイプ
    #   main_occupant_room: 主たる居室
    #   other_occupant_room: その他の居室
    #   non_occupant_room: 非居室
    #   underfloor: 床下空間
    room_type_is = {
        1: SpaceType.MAIN_HABITABLE_ROOM,
        2: SpaceType.OTHER_HABITABLE_ROOM,
        3: SpaceType.NON_HABITABLE_ROOM,
        4: SpaceType.UNDERFLOOR
    }[room['room_type']]

    # 局所換気
    local_vent_amount_schedule = a38.get_schedule(
        room_name=name_i, n_p=n_p, calendar=calendar, daily_schedule=d_json['daily_schedule']['local_vent_amount'])
    q_gen_app_i_ns = a38.get_schedule(
        room_name=name_i, n_p=n_p, calendar=calendar, daily_schedule=d_json['daily_schedule']['heat_generation_appliances'])
    q_gen_ckg_i_ns = a38.get_schedule(
        room_name=name_i, n_p=n_p, calendar=calendar, daily_schedule=d_json['daily_schedule']['vapor_generation_cooking'])
    # 機器発熱
    vapor_generation_cooking_schedule = a38.get_schedule(
        room_name=name_i, n_p=n_p, calendar=calendar, daily_schedule=d_json['daily_schedule']['heat_generation_cooking'])
    # 照明発熱
    # TODO 床面積を乗じるのを忘れないように
    q_gen_lght_i_ns = a38.get_schedule(
        room_name=name_i, n_p=n_p, calendar=calendar, daily_schedule=d_json['daily_schedule']['heat_generation_lighting'])
    # 在室人数
    number_of_people_schedule = a38.get_schedule(
        room_name=name_i, n_p=n_p, calendar=calendar, daily_schedule=d_json['daily_schedule']['number_of_people'])

    air_conditioning_demand2 = a38.get_air_conditioning_schedules2(
        room_name=name_i, calendar=calendar, daily_schedule=d_json['daily_schedule']['is_temp_limit_set'])

    air_conditioning_demand = np.where(air_conditioning_demand2 == "on", True, False)

    # 部位の人体に対する形態係数を計算 表6
    Fot_i_g = a12.calc_form_factor_for_human_body(a_bnd_i_jstrs, is_solar_absorbed_inside_bnd_i_jstrs)

    # 合計面積の計算, m2
    A_total_i = sum(a_bnd_i_jstrs)

    # 室iにおける床面積の合計, m2
    a_floor_i = np.sum(a_bnd_i_jstrs * is_solar_absorbed_inside_bnd_i_jstrs)

    # ルームエアコンの仕様の設定 式(107)-(111)
    qrtd_c_i = a15.get_qrtd_c(a_floor_i)
    qmax_c_i = a15.get_qmax_c(qrtd_c_i)
    qmin_c_i = a15.get_qmin_c()
    Vmax_i = a15.get_Vmax(qrtd_c_i)
    Vmin_i = a15.get_Vmin(Vmax_i)

    # 暖房設備仕様の読み込み
    # 放射暖房有無（Trueなら放射暖房あり）
    is_radiative_heating = a22.read_is_radiative_heating(room)

    # 放射暖房最大能力[W]
    Lrcap_i = a22.read_radiative_heating_max_capacity(room)

    # 冷房設備仕様の読み込み

    # 放射冷房有無（Trueなら放射冷房あり）
    is_radiative_cooling = a22.read_is_radiative_cooling(room)

    # 放射冷房最大能力[W]
    radiative_cooling_max_capacity = a22.read_is_radiative_cooling(room)

    # 熱交換器種類
    heat_exchanger_type = a22.read_heat_exchanger_type(room)

    # 定格冷房能力[W]
    convective_cooling_rtd_capacity = a22.read_convective_cooling_rtd_capacity(room)

    # 放射暖房の発熱部位の設定（とりあえず床発熱） 表7
    flr_i_k = a12.get_flr(a_bnd_i_jstrs, a_floor_i, is_radiative_heating,
                                is_solar_absorbed_inside_bnd_i_jstrs)

    eps_m = a18.get_eps()

    # 微小点に対する室内部位の形態係数の計算（永田先生の方法） 式(94)
    FF_m = a12.calc_form_factor_of_microbodies(name_i, a_bnd_i_jstrs)

    # 表面熱伝達率の計算 式(123) 表16
    h_r_bnd_i_jstrs, h_c_bnd_i_jstrs = a23.calc_surface_transfer_coefficient(eps_m, FF_m, h_i_bnd_i_jstrs=h_i_bnd_i_jstrs)

    # 平均放射温度計算時の各部位表面温度の重み計算 式(101)
    F_mrt_i_g = a12.get_F_mrt_i_g(a_bnd_i_jstrs, h_r_bnd_i_jstrs)

    # 室iの統合された境界j*における室の透過日射熱取得のうちの吸収日射量, W/m2, [j*, 8760*4]
    q_sol_floor_i_jstrs_ns = a12.get_q_sol_floor_i_jstrs_ns(
        q_trs_sol_i_ns=q_trs_sol_i_ns, a_bnd_i_jstrs=a_bnd_i_jstrs,
        is_solar_absorbed_inside_bnd_i_jstrs=is_solar_absorbed_inside_bnd_i_jstrs, a_floor_i=a_floor_i
    )

    # ステップnの室iにおける家具の吸収日射量, W, [8760*4]
    q_sol_frnt_i_ns = a12.get_q_sol_frnt_i_ns(q_trs_sol_i_ns=q_trs_sol_i_ns)

    # *********** 室内表面熱収支計算のための行列作成 ***********

    Beta_i = 0.0  # 放射暖房対流比率

    # FIA, FLBの作成 式(26)
    FIA_i_l = a1.get_FIA(rfa0_bnd_i_jstrs, h_c_bnd_i_jstrs)
    FLB_i_l = a1.get_FLB(rfa0_bnd_i_jstrs, flr_i_k, Beta_i, a_bnd_i_jstrs)

    # 行列AX 式(25)
    AX_k_l = a1.get_AX(rfa0_bnd_i_jstrs, h_r_bnd_i_jstrs, F_mrt_i_g, h_i_bnd_i_jstrs, n_bnd_i_jstrs)

    # WSR, WSB の計算 式(24)
    WSR_i_k = a1.get_WSR(AX_k_l, FIA_i_l)
    WSB_i_k = a1.get_WSB(AX_k_l, FLB_i_l)

    # i室のn時点における窓開放時通風量
    # 室空気の熱容量

    # 空気の比熱[J/kg K]
    ca = a18.get_c_air()

    # 空気の密度[kg/m3]
    rhoa = a18.get_rho_air()

    # 室iの気積, m3
    v_room_cap_i = room['volume']

    c_room_i = v_room_cap_i * rhoa * ca

    # 家具の熱容量、湿気容量の計算
    # Capfun:家具熱容量[J/K]、Cfun:家具と室空気間の熱コンダクタンス[W/K]
    Capfun = a14.get_c_cap_frnt_is(v_room_cap_i)
    Cfun = a14.get_Cfun(Capfun)

    # 室iの外気からの機械換気量, m3/h
    v_vent_ex_i = room['vent']

    # 室iの隣室からの機械換気量niの換気量, m3/h, [ni]
    v_vent_up_i_nis = np.array([next_vent['volume'] for next_vent in room['next_vent']])

    # BRMの計算 式(5) ※ただし、通風なし
    BRMnoncv_i = s41.get_BRM_i(
        Hcap=c_room_i,
        WSR_i_k=WSR_i_k,
        Cap_fun_i=Capfun,
        C_fun_i=Cfun,
        Vent=v_vent_ex_i,
        local_vent_amount_schedule=local_vent_amount_schedule,
        A_i_k=a_bnd_i_jstrs,
        hc_i_k_n=h_c_bnd_i_jstrs,
        V_nxt=v_vent_up_i_nis
    )

    # BRLの計算 式(7)
    BRL_i = s41.get_BRL_i(
        Beta_i=Beta_i,
        WSB_i_k=WSB_i_k,
        A_i_k=a_bnd_i_jstrs,
        hc_i_k_n=h_c_bnd_i_jstrs
    )

    q_gen_i_ns = q_gen_app_i_ns + q_gen_lght_i_ns + q_gen_ckg_i_ns

    # 室iの自然風利用時の換気量, m3/s
    v_ntrl_vent_i = v_room_cap_i * n_ntrl_vent_i / 3600

    # ステップnの室iにおける機械換気量（全般換気量+局所換気量）, m3/s
    v_mec_vent_i_ns = (v_vent_ex_i + local_vent_amount_schedule) / 3600

    space = Space(
        i=i,
        boundary_type_i_jstrs=boundary_type_i_jstrs,
        a_bnd_i_jstrs=a_bnd_i_jstrs,
        h_bnd_i_jstrs=h_bnd_i_jstrs,
        next_room_type_bnd_i_jstrs=next_room_type_bnd_i_jstrs,
        is_solar_absorbed_inside_bnd_i_jstrs=is_solar_absorbed_inside_bnd_i_jstrs,
        theta_o_sol_bnd_i_jstrs_ns=theta_o_sol_bnd_i_jstrs_ns,
        n_root_bnd_i_jstrs=n_root_bnd_i_jstrs,
        row_bnd_i_jstrs=row_bnd_i_jstrs,
        rft0_bnd_i_jstrs=rft0_bnd_i_jstrs,
        rfa0_bnd_i_jstrs=rfa0_bnd_i_jstrs,
        rft1_bnd_i_jstrs=rft1_bnd_i_jstrs,
        rfa1_bnd_i_jstrs=rfa1_bnd_i_jstrs,
        n_bnd_i_jstrs=n_bnd_i_jstrs,
        q_trs_sol_i_ns=q_trs_sol_i_ns,
        x_gen_except_hum_i_ns=vapor_generation_cooking_schedule/1000.0/3600.0,
        number_of_people_schedule=number_of_people_schedule,
        air_conditioning_demand=air_conditioning_demand,
        Fot_i_g=Fot_i_g,
        A_total_i=A_total_i,
        qmax_c_i = qmax_c_i,
        qmin_c_i = qmin_c_i,
        Vmax_i = Vmax_i,
        Vmin_i = Vmin_i,
        is_radiative_heating=is_radiative_heating,
        Lrcap_i = Lrcap_i,
        is_radiative_cooling = is_radiative_cooling,
        radiative_cooling_max_capacity = radiative_cooling_max_capacity,
        heat_exchanger_type = heat_exchanger_type,
        convective_cooling_rtd_capacity = convective_cooling_rtd_capacity,
        flr_i_k=flr_i_k,
        h_r_bnd_i_jstrs=h_r_bnd_i_jstrs,
        h_c_bnd_i_jstrs=h_c_bnd_i_jstrs,
        F_mrt_i_g=F_mrt_i_g,
        Beta_i=Beta_i,
        AX_k_l=AX_k_l,
        WSR_i_k=WSR_i_k,
        WSB_i_k=WSB_i_k,
        BRMnoncv_i=BRMnoncv_i,
        BRL_i=BRL_i,
        q_gen_i_ns=q_gen_i_ns,
        q_sol_srf_i_jstrs_ns=q_sol_floor_i_jstrs_ns,
        q_sol_frnt_i_ns=q_sol_frnt_i_ns,
        v_ntrl_vent_i=v_ntrl_vent_i,
        v_mec_vent_i_ns=v_mec_vent_i_ns
    )


    return space


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
