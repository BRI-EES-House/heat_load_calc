import math
import numpy as np
from typing import Dict
import json

import a12_indoor_radiative_heat_transfer as a12
import a13_Win_ACselect as a13
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

from s3_space_loader import Space
import s3_surface_initializer as s3
import s3_space_loader as s3sl
import s3_surface_loader
import s4_1_sensible_heat as s41

# # 室温・熱負荷を計算するクラス

# ## １）室内部位に関連するクラス

# 室内部位に関する情報を保持します。
# 
# - is_skin:      外皮フラグ, 外皮の場合True
# - boundary:  方位・隣室名, string
# - unsteady:  非定常フラグ, 非定常壁体の場合True
# - name:      壁体・開口部名称, string
# - A_i_g:      面積, m2
# - sunbreak:  ひさし名称, string
# - flr_i_k:       放射暖房吸収比率, －
# - fot:       人体に対する形態係数, －

# ## ４）空間に関するクラス

# 空間に関する情報を保持します。
# 
# - roomname:      室区分, string
# - roomdiv:       室名称, string
# - HeatCcap:      最大暖房能力（対流）[W]
# - HeatRcap:      最大暖房能力（放射）[W]
# - CoolCcap:      最大冷房能力（対流）[W]
# - CoolRcap:      最大冷房能力（放射）[W]
# - Vol:           室気積, m3
# - Fnt:           家具熱容量, kJ/m3K
# - Vent:          計画換気量, m3/h
# - Inf:           すきま風量[Season]（list型、暖房・中間期・冷房の順）, m3/h
# - CrossVentRoom: 通風計算対象室, False
# - is_radiative_heating:       放射暖房対象室フラグ, True
# - Betat:         放射暖房対流比率, －
# - RoomtoRoomVents:      室間換気量（list型、暖房・中間期・冷房、風上室名称）, m3/h
# - d:             室内部位に関連するクラス, Surface

def make_space(room: Dict,
               i_dn_ns: np.ndarray, i_sky_ns: np.ndarray, r_n_ns: np.ndarray, theta_o_ns: np.ndarray,
               h_sun_ns: np.ndarray, a_sun_ns: np.ndarray, i: int):

    # 室iの名称
    name_i = room['name']

    # 室iのタイプ
    #   main_occupant_room: 主たる居室
    #   other_occupant_room: その他の居室
    #   non_occupant_room: 非居室
    #   underfloor: 床下空間
    room_type_i = room['room_type']

    # 室iの気積, m3
    v_room_cap_i = room['volume']

    # 室iの外気からの機械換気量, m3/h
    v_vent_ex_i = room['vent']

    # 室iの隣室からの機械換気量niの上流側の室の名称, [ni]
    name_vent_up_i_nis = [next_vent['upstream_room_type'] for next_vent in room['next_vent']]

    # 室iの隣室からの機械換気量niの換気量, m3/h, [ni]
    v_vent_up_i_nis = np.array([next_vent['volume'] for next_vent in room['next_vent']])

    # 室iの境界k
    d_boundary_i_ks = s3_surface_loader.read_d_boundary_i_ks(input_dict_boundaries=room['boundaries'])

    # i室の部位の初期化
    ib = s3.init_surface(
        boundaries=d_boundary_i_ks,
        i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, r_n_ns=r_n_ns, theta_o_ns=theta_o_ns, h_sun_ns=h_sun_ns, a_sun_ns=a_sun_ns)

    name_bnd_i_jstrs = ib.name_i_jstrs
    sub_name_bnd_i_jstrs = ib.sub_name_i_jstrs
    boundary_type_i_jstrs = ib.boundary_type_i_jstrs
    a_bnd_i_jstrs = ib.a_i_jstrs
    h_bnd_i_jstrs = ib.h_i_jstrs
    next_room_type_bnd_i_jstrs = ib.next_room_type_i_jstrs
    is_solar_absorbed_inside_bnd_i_jstrs = ib.is_solar_absorbed_inside_i_jstrs
    h_i_bnd_i_jstrs = ib.h_i_i_jstrs
    theta_o_sol_bnd_i_jstrs_ns = ib.theta_o_sol_i_jstrs_ns
    n_root_bnd_i_jstrs = ib.n_root_i_jstrs
    row_bnd_i_jstrs = ib.Rows
    rft0_bnd_i_jstrs = ib.RFT0s
    rfa0_bnd_i_jstrs = ib.RFA0s
    rft1_bnd_i_jstrs = ib.RFT1s
    rfa1_bnd_i_jstrs = ib.RFA1s
    n_bnd_i_jstrs = ib.NsurfG_i

    # ステップnの室iにおける窓の透過日射熱取得, W, [8760*4]
    q_trs_sol_i_ns = np.sum(
        s3.get_transmitted_solar_radiation(
            boundaries=d_boundary_i_ks, i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, h_sun_ns=h_sun_ns, a_sun_ns=a_sun_ns
        ), axis=0)

    # 室iの自然風利用時の換気回数, 1/h
    n_ntrl_vent_i = room['natural_vent_time']

    # 室iの初期温度, degree C
    theta_r_i_initial = a18.get_theta_r_initial()

    # TODO 居住人数。これは1～4の値（小数値。整数ではない。）が入る。床面積の合計から推定すること。
    n_p = 4.0

    # スケジュールの読み込み
    js = open('schedules.json', 'r', encoding='utf-8')
    d_json = json.load(js)
    calendar = np.array(d_json['calendar'])

    # 局所換気
    local_vent_amount_schedule = a38.get_schedule(
        room_name=name_i, n_p=n_p, calendar=calendar, daily_schedule=d_json['daily_schedule']['local_vent_amount'])
    heat_generation_appliances_schedule = a38.get_schedule(
        room_name=name_i, n_p=n_p, calendar=calendar, daily_schedule=d_json['daily_schedule']['heat_generation_appliances'])
    heat_generation_cooking_schedule = a38.get_schedule(
        room_name=name_i, n_p=n_p, calendar=calendar, daily_schedule=d_json['daily_schedule']['vapor_generation_cooking'])
    # 機器発熱
    vapor_generation_cooking_schedule = a38.get_schedule(
        room_name=name_i, n_p=n_p, calendar=calendar, daily_schedule=d_json['daily_schedule']['heat_generation_cooking'])
    # 照明発熱
    # TODO 床面積を乗じるのを忘れないように
    heat_generation_lighting_schedule = a38.get_schedule(
        room_name=name_i, n_p=n_p, calendar=calendar, daily_schedule=d_json['daily_schedule']['heat_generation_lighting'])
    # 在室人数
    number_of_people_schedule = a38.get_schedule(
        room_name=name_i, n_p=n_p, calendar=calendar, daily_schedule=d_json['daily_schedule']['number_of_people'])

    air_conditioning_demand2 = a38.get_air_conditioning_schedules2(
        room_name=name_i, calendar=calendar, daily_schedule=d_json['daily_schedule']['is_temp_limit_set'])

    air_conditioning_demand = np.where(air_conditioning_demand2 == "on", True, False)

    theta_rear_initial = a18.get_Teo_initial()

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

    rhoa = a18.get_rho_air()
    # 室空気の質量[kg]
    Ga = v_room_cap_i * rhoa

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
    ca = a18.get_c_air()
    rhoa = a18.get_rho_air()
    c_room_i = v_room_cap_i * rhoa * ca

    # 家具の熱容量、湿気容量の計算
    # Capfun:家具熱容量[J/K]、Cfun:家具と室空気間の熱コンダクタンス[W/K]
    Capfun = a14.get_Capfun(v_room_cap_i)
    Cfun = a14.get_Cfun(Capfun)


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

    q_gen_i_ns = heat_generation_appliances_schedule + heat_generation_lighting_schedule + heat_generation_cooking_schedule

    next_room_idxs_i = []
    for x in name_vent_up_i_nis:
        next_room_idxs_i.append(
            {
                'main_occupant_room': 0,
                'other_occupant_room': 1,
                'non_occupant_room': 2,
                'underfloor': 3
            }[x]
        )

    # 室iの自然風利用時の換気量, m3/s
    v_ntrl_vent_i = v_room_cap_i * n_ntrl_vent_i / 3600

    # ステップnの室iにおける機械換気量（全般換気量+局所換気量）, m3/s
    v_mec_vent_i_ns = (v_vent_ex_i + local_vent_amount_schedule) / 3600

    space = Space(
        i = i,
        name_i=name_i,
        room_type_i=room_type_i,
        v_room_cap_i=v_room_cap_i,
        name_vent_up_i_nis=name_vent_up_i_nis,
        v_vent_up_i_nis=v_vent_up_i_nis,
        name_bnd_i_jstrs=name_bnd_i_jstrs,
        sub_name_bnd_i_jstrs=sub_name_bnd_i_jstrs,
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
        theta_r_i_initial=theta_r_i_initial,
        heat_generation_appliances_schedule=heat_generation_appliances_schedule,
        x_gen_except_hum_i_ns=vapor_generation_cooking_schedule/1000.0/3600.0,
        heat_generation_lighting_schedule=heat_generation_lighting_schedule,
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
        Ga=Ga,
        Beta_i=Beta_i,
        AX_k_l=AX_k_l,
        WSR_i_k=WSR_i_k,
        WSB_i_k=WSB_i_k,
        BRMnoncv_i=BRMnoncv_i,
        BRL_i=BRL_i,
        c_room_i=c_room_i,
        c_cap_frnt_i=Capfun,
        c_fun_i=Cfun,
        q_gen_except_hum_i_ns=q_gen_i_ns,
        q_sol_srf_i_jstrs_ns=q_sol_floor_i_jstrs_ns,
        q_sol_frnt_i_ns=q_sol_frnt_i_ns,
        next_room_idxs_i=next_room_idxs_i,
        v_ntrl_vent_i=v_ntrl_vent_i,
        v_mec_vent_i_ns=v_mec_vent_i_ns
    )


    return space
