import math
import numpy as np

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
from s3_surface_initializer import init_surface
from s3_space_loader import Space
import s3_surface_initializer as s3

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

def init_spaces(space: Space,
                I_DN_n: np.ndarray, I_sky_n: np.ndarray, RN_n: np.ndarray, To_n: np.ndarray,
                h_s_n: np.ndarray, a_s_n: np.ndarray):

    # 空調や通風などの需要があるかどうか, bool * 365 * 96
    space.air_conditioning_demand = space.is_upper_temp_limit_set_schedule | space.is_lower_temp_limit_set_schedule

    # i室の部位の初期化
    space.surf_i = init_surface(space.d_boundary_i_ks, I_DN_n, I_sky_n, RN_n, To_n, h_s_n, a_s_n)

    # i室の境界条件が同じ部位kを集約し、部位gを作成
    space.surfG_i = a34.GroupedSurface(space.surf_i)

    # 透過日射熱取得の集約し、i室のn時点における透過日射熱取得 QGT_i_n を計算
    space.QGT_i_n = np.sum(
        s3.get_transmitted_solar_radiation(
            space.d_boundary_i_ks, I_DN_n, I_sky_n, h_s_n, a_s_n
        ), axis=0)

    # i室の部位の面数(集約後)
    space.NsurfG_i = space.surfG_i.NsurfG_i

    # 部位ごとの計算結果用変数
    space.Ts_i_k_n = np.zeros((space.NsurfG_i, 24 * 365 * 4 * 4))
    space.Teo_i_k_n = np.full((space.NsurfG_i, 24 * 365 * 4 * 4), a18.get_Teo_initial())  # i室の部位kにおけるn時点の裏面相当温度
    space.Tei_i_k_n = np.zeros((space.NsurfG_i, 24 * 365 * 4 * 4))  # i室の部位kにおけるn時点の室内等価温度
    space.TsdA_l_n_m = np.full((space.NsurfG_i, 24 * 365 * 4 * 4, 12), a18.get_TsdT_initial())  # （26）式中の〖CVL〗_(i,l)の計算式右辺
    space.TsdT_l_n_m = np.full((space.NsurfG_i, 24 * 365 * 4 * 4, 12), a18.get_TsdT_initial())  # （26）式中の〖CVL〗_(i,l)の計算式右辺
    space.Sol_i_g_n = np.zeros((space.NsurfG_i, 24 * 365 * 4 * 4))
    space.Qc = np.zeros((space.NsurfG_i, 24 * 365 * 4 * 4))
    space.Qr = np.zeros((space.NsurfG_i, 24 * 365 * 4 * 4))
    space.oldqi = space.surfG_i.oldqi

    eps_m = a18.get_eps()

    # 部位の人体に対する形態係数を計算 表6
    space.Fot_i_g = a12.calc_form_factor_for_human_body(space.surfG_i.A_i_g, space.surfG_i.is_solar_absorbed_inside)

    # 合計面積の計算
    space.A_total_i = np.sum(space.surfG_i.A_i_g)

    # 合計床面積の計算
    A_fs_i = np.sum(space.surfG_i.A_i_g * space.surfG_i.is_solar_absorbed_inside)

    # ルームエアコンの仕様の設定 式(107)-(111)
    space.qrtd_c_i = a15.get_qrtd_c(A_fs_i)
    space.qmax_c_i = a15.get_qmax_c(space.qrtd_c_i)
    space.qmin_c_i = a15.get_qmin_c()
    space.Vmax_i = a15.get_Vmax(space.qrtd_c_i)
    space.Vmin_i = a15.get_Vmin(space.Vmax_i)

    # 放射暖房の発熱部位の設定（とりあえず床発熱） 表7
    space.flr_i_k = a12.get_flr(space.surfG_i.A_i_g, A_fs_i, space.is_radiative_heating,
                                space.surfG_i.is_solar_absorbed_inside)

    # 微小点に対する室内部位の形態係数の計算（永田先生の方法） 式(94)
    FF_m = a12.calc_form_factor_of_microbodies(space.name_i, space.surfG_i.A_i_g)

    # 表面熱伝達率の計算 式(123) 表16
    space.hr_i_g_n, space.hc_i_g_n = a23.calc_surface_transfer_coefficient(eps_m, FF_m, space.surfG_i.hi_i_g_n)

    # 平均放射温度計算時の各部位表面温度の重み計算 式(101)
    space.F_mrt_i_g = a12.get_F_mrt_i_g(space.surfG_i.A_i_g, space.hr_i_g_n)

    # 日射吸収比率の計算

    # 床の室内部位表面吸収比率の設定 表(5) 床の場合
    space.Rsol_floor_i_g = a12.get_SolR(space.surfG_i.A_i_g, space.surfG_i.is_solar_absorbed_inside, A_fs_i)

    space.Rsol_fun_i = a12.calc_absorption_ratio_of_transmitted_solar_radiation()

    # *********** 室内表面熱収支計算のための行列作成 ***********

    rhoa = a18.get_rhoa()
    space.Ga = space.vol_i * rhoa  # 室空気の質量[kg]

    # FIA, FLBの作成 式(26)
    FIA_i_l = a1.get_FIA(space.surfG_i.RFA0, space.hc_i_g_n)
    FLB_i_l = a1.get_FLB(space.surfG_i.RFA0, space.flr_i_k, space.Beta_i, space.surfG_i.A_i_g)

    # 行列AX 式(25)
    space.AX_k_l = a1.get_AX(space.surfG_i.RFA0, space.hr_i_g_n, space.F_mrt_i_g, space.surfG_i.hi_i_g_n, space.NsurfG_i)

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
        Vent=space.Vent,
        local_vent_amount_schedule=space.local_vent_amount_schedule,
        A_i_k=space.surfG_i.A_i_g,
        hc_i_k_n=space.hc_i_g_n,
        V_nxt=space.Vnext_i_j
    )

    # BRLの計算 式(7)
    space.BRL_i = s41.get_BRL_i(
        Beta_i=space.Beta_i,
        WSB_i_k=space.WSB_i_k,
        A_i_k=space.surfG_i.A_i_g,
        hc_i_k_n=space.hc_i_g_n
    )
