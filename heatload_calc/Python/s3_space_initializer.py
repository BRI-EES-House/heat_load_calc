import math
import numpy as np
from typing import Dict

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
import a29_local_vent_schedule as a29
import a30_internal_heat_schedule as a30
import a31_lighting_schedule as a31
import a32_resident_schedule as a32
import a34_building_part_summarize as a34
import s4_1_sensible_heat as s41

from s3_space_loader import Space
import s3_surface_initializer as s3
import s3_space_loader as s3sl
import s3_surface_loader

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
               h_sun_ns: np.ndarray, a_sun_ns: np.ndarray):

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

    name_bdry_i_jstrs = ib.name_i_jstrs
    sub_name_bdry_i_jstrs = ib.sub_name_i_jstrs
    boundary_type_i_jstrs = ib.boundary_type_i_jstrs
    a_bdry_i_jstrs = ib.a_i_jstrs
    is_sun_striked_outside_bdry_i_jstrs = ib.is_sun_striked_outside_i_jstrs
    h_bdry_i_jstrs = ib.h_i_jstrs
    next_room_type_bdry_i_jstrs = ib.next_room_type_i_jstrs
    is_solar_absorbed_inside_bdry_i_jstrs = ib.is_solar_absorbed_inside_i_jstrs
    h_i_bdry_i_jstrs = ib.h_i_i_jstrs
    theta_o_sol_bdry_i_jstrs_ns = ib.theta_o_sol_i_jstrs_ns
    n_root_bdry_i_jstrs = ib.n_root_i_jstrs
    row_bdry_i_jstrs = ib.Rows
    rft0_bdry_i_jstrs = ib.RFT0s
    rfa0_bdry_i_jstrs = ib.RFA0s
    rft1_bdry_i_jstrs = ib.RFT1s
    rfa1_bdry_i_jstrs = ib.RFA1s
    n_bdry_i_jstrs = ib.NsurfG_i


    space = Space(
        d_room=room,
        name_i=name_i,
        room_type_i=room_type_i,
        v_room_cap_i=v_room_cap_i,
        v_vent_ex_i=v_vent_ex_i,
        name_vent_up_i_nis=name_vent_up_i_nis,
        v_vent_up_i_nis=v_vent_up_i_nis,
        name_bdry_i_jstrs=name_bdry_i_jstrs,
        sub_name_bdry_i_jstrs=sub_name_bdry_i_jstrs,
        boundary_type_i_jstrs=boundary_type_i_jstrs,
        a_bdry_i_jstrs=a_bdry_i_jstrs,
        is_sun_striked_outside_bdry_i_jstrs=is_sun_striked_outside_bdry_i_jstrs,
        h_bdry_i_jstrs=h_bdry_i_jstrs,
        next_room_type_bdry_i_jstrs=next_room_type_bdry_i_jstrs,
        is_solar_absorbed_inside_bdry_i_jstrs=is_solar_absorbed_inside_bdry_i_jstrs,
        h_i_bdry_i_jstrs=h_i_bdry_i_jstrs,
        theta_o_sol_bdry_i_jstrs_ns=theta_o_sol_bdry_i_jstrs_ns,
        n_root_bdry_i_jstrs=n_root_bdry_i_jstrs,
        row_bdry_i_jstrs=row_bdry_i_jstrs,
        rft0_bdry_i_jstrs=rft0_bdry_i_jstrs,
        rfa0_bdry_i_jstrs=rfa0_bdry_i_jstrs,
        rft1_bdry_i_jstrs=rft1_bdry_i_jstrs,
        rfa1_bdry_i_jstrs=rfa1_bdry_i_jstrs,
        n_bdry_i_jstrs=n_bdry_i_jstrs
    )

    # 透過日射熱取得の集約し、i室のn時点における透過日射熱取得 QGT_i_n を計算
    space.QGT_i_n = np.sum(
        s3.get_transmitted_solar_radiation(
            boundaries=d_boundary_i_ks, i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, h_sun_ns=h_sun_ns, a_sun_ns=a_sun_ns
        ), axis=0)

    # 空調や通風などの需要があるかどうか, bool * 365 * 96
    space.air_conditioning_demand = space.is_upper_temp_limit_set_schedule | space.is_lower_temp_limit_set_schedule

    # 部位ごとの計算結果用変数
    space.Ts_i_k_n = np.zeros((space.n_bdry_i_jstrs, 24 * 365 * 4 * 4))
    space.Teo_i_k_n = np.full((space.n_bdry_i_jstrs, 24 * 365 * 4 * 4), a18.get_Teo_initial())  # i室の部位kにおけるn時点の裏面相当温度
    space.Tei_i_k_n = np.zeros((space.n_bdry_i_jstrs, 24 * 365 * 4 * 4))  # i室の部位kにおけるn時点の室内等価温度
    space.TsdA_l_n_m = np.full((space.n_bdry_i_jstrs, 24 * 365 * 4 * 4, 12), a18.get_TsdT_initial())  # （26）式中の〖CVL〗_(i,l)の計算式右辺
    space.TsdT_l_n_m = np.full((space.n_bdry_i_jstrs, 24 * 365 * 4 * 4, 12), a18.get_TsdT_initial())  # （26）式中の〖CVL〗_(i,l)の計算式右辺
    space.Sol_i_g_n = np.zeros((space.n_bdry_i_jstrs, 24 * 365 * 4 * 4))
    space.Qc = np.zeros((space.n_bdry_i_jstrs, 24 * 365 * 4 * 4))
    space.Qr = np.zeros((space.n_bdry_i_jstrs, 24 * 365 * 4 * 4))
    # 前時刻の室内側表面熱流
    space.oldqi = np.zeros(space.n_bdry_i_jstrs)
    eps_m = a18.get_eps()

    # 部位の人体に対する形態係数を計算 表6
    space.Fot_i_g = a12.calc_form_factor_for_human_body(space.a_bdry_i_jstrs, space.is_solar_absorbed_inside_bdry_i_jstrs)

    # 合計面積の計算
    space.A_total_i = np.sum(space.a_bdry_i_jstrs)

    # 合計床面積の計算
    A_fs_i = np.sum(space.a_bdry_i_jstrs * space.is_solar_absorbed_inside_bdry_i_jstrs)

    # ルームエアコンの仕様の設定 式(107)-(111)
    space.qrtd_c_i = a15.get_qrtd_c(A_fs_i)
    space.qmax_c_i = a15.get_qmax_c(space.qrtd_c_i)
    space.qmin_c_i = a15.get_qmin_c()
    space.Vmax_i = a15.get_Vmax(space.qrtd_c_i)
    space.Vmin_i = a15.get_Vmin(space.Vmax_i)

    # 放射暖房の発熱部位の設定（とりあえず床発熱） 表7
    space.flr_i_k = a12.get_flr(space.a_bdry_i_jstrs, A_fs_i, space.is_radiative_heating,
                                space.is_solar_absorbed_inside_bdry_i_jstrs)


    # 微小点に対する室内部位の形態係数の計算（永田先生の方法） 式(94)
    FF_m = a12.calc_form_factor_of_microbodies(space.name_i, space.a_bdry_i_jstrs)

    # 表面熱伝達率の計算 式(123) 表16
    space.hr_i_g_n, space.hc_i_g_n = a23.calc_surface_transfer_coefficient(eps_m, FF_m, space.h_i_bdry_i_jstrs)

    # 平均放射温度計算時の各部位表面温度の重み計算 式(101)
    space.F_mrt_i_g = a12.get_F_mrt_i_g(space.a_bdry_i_jstrs, space.hr_i_g_n)

    # 日射吸収比率の計算

    # 床の室内部位表面吸収比率の設定 表(5) 床の場合
    space.Rsol_floor_i_g = a12.get_SolR(space.a_bdry_i_jstrs, space.is_solar_absorbed_inside_bdry_i_jstrs, A_fs_i)

    space.Rsol_fun_i = a12.calc_absorption_ratio_of_transmitted_solar_radiation()

    # *********** 室内表面熱収支計算のための行列作成 ***********

    rhoa = a18.get_rhoa()
    space.Ga = space.v_room_cap_i * rhoa  # 室空気の質量[kg]

    # FIA, FLBの作成 式(26)
    FIA_i_l = a1.get_FIA(space.rfa0_bdry_i_jstrs, space.hc_i_g_n)
    FLB_i_l = a1.get_FLB(space.rfa0_bdry_i_jstrs, space.flr_i_k, space.Beta_i, space.a_bdry_i_jstrs)

    # 行列AX 式(25)
    space.AX_k_l = a1.get_AX(space.rfa0_bdry_i_jstrs, space.hr_i_g_n, space.F_mrt_i_g, space.h_i_bdry_i_jstrs, space.n_bdry_i_jstrs)

    # WSR, WSB の計算 式(24)
    space.WSR_i_k = a1.get_WSR(space.AX_k_l, FIA_i_l)
    space.WSB_i_k = a1.get_WSB(space.AX_k_l, FLB_i_l)

    # ****************************************************

    # BRMの計算 式(5) ※ただし、通風なし
    space.BRMnoncv_i = s41.get_BRM_i(
        Hcap=space.Hcap,
        WSR_i_k=space.WSR_i_k,
        Cap_fun_i=space.Capfun,
        C_fun_i=space.Cfun,
        Vent=space.v_vent_ex_i,
        local_vent_amount_schedule=space.local_vent_amount_schedule,
        A_i_k=space.a_bdry_i_jstrs,
        hc_i_k_n=space.hc_i_g_n,
        V_nxt=space.v_vent_up_i_nis
    )

    # BRLの計算 式(7)
    space.BRL_i = s41.get_BRL_i(
        Beta_i=space.Beta_i,
        WSB_i_k=space.WSB_i_k,
        A_i_k=space.a_bdry_i_jstrs,
        hc_i_k_n=space.hc_i_g_n
    )

    return space
