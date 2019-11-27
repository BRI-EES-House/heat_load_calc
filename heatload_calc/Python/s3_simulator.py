import numpy as np
from typing import List

import s4_1_sensible_heat as s41
import s4_2_latent_heat as s42

import a1_calculation_surface_temperature as a1
import apdx3_human_body as a3
import a9_rear_surface_equivalent_temperature as a9
import a12_indoor_radiative_heat_transfer as a12
import a13_Win_ACselect as a13
import a16_blowing_condition_rac as a16
import a18_initial_value_constants as a18
import a28_operative_temperature as a28
import a35_PMV as a35
import a37_groundonly_runup_calculation as a37
from s3_space_loader import Space

from Psychrometrics import rhtx


# 地盤の計算
def run_tick_groundonly(spaces: List[Space], To_n: float, n: int):

    for s in spaces:

        # 配列の準備
        Row = s.row_bdry_i_jstrs

        Phi_A_i_k_0 = s.rfa0_bdry_i_jstrs
        hi_i_k = s.h_i_bdry_i_jstrs
        a0 = a37.get_a0(To_n)

        # 畳み込み積分 式(27)
        for g in range(s.n_bnd_i_jstrs):
            if s.boundary_type_i_jstrs[g] == "ground":
                s.TsdA_l_n_m[g, n] = s.oldqi[g] * s.rfa1_bdry_i_jstrs[g] + Row[g] * s.TsdA_l_n_m[g, n - 1]
                s.Ts_i_k_n[g, n] = a37.get_Ts_i_n_k(Phi_A_i_k_0[g], hi_i_k[g], To_n, s.TsdA_l_n_m[g, n], a0)
                # 室内表面熱流の計算 式(28)
                s.oldqi[g] = hi_i_k[g] * (To_n - s.Ts_i_k_n[g, n])


# 室温、熱負荷の計算
def run_tick(spaces: List[Space], To_n: float, xo_n: float, n: int):

    # ステップnの室iにおける室温, degree C, [i]
    # 室内壁の場合の裏面温度を計算する際に隣りの室の室温を持ちるために使用する。
    # 本当はこの式は n-1 ではなくて、nが正しい。
    # 新しい室温を計算する部分が修正した後、最後に修正すること。
    theta_r_is_n = np.array([s.theta_r_i_ns[n-1] for s in spaces])

    for i, s in enumerate(spaces):

        # ステップnの室iにおける室温, degree C
        theta_r_i_n = theta_r_is_n[i]

        # ステップnの室iの集約された境界j*の傾斜面における相当外気温度, degree C, [j*]
        theta_o_sol_bnd_i_jstrs_n = np.array(
            [s.theta_o_sol_bnd_i_jstrs_ns[jstr][n] for jstr in range(s.n_bnd_i_jstrs)])

        # ステップnの室iの集約された境界j*における裏面温度, degree C, [j*]
        theta_rear_i_jstrs_n = a9.get_theta_rear_i_jstrs_n(
            theta_r_i_n=theta_r_i_n,
            n_bnd_i_jstrs=s.n_bnd_i_jstrs,
            boundary_type_i_jstrs=s.boundary_type_i_jstrs,
            h_bnd_i_jstrs=s.h_bnd_i_jstrs,
            next_room_type_bnd_i_jstrs=s.next_room_type_bnd_i_jstrs,
            theta_r_is_n=theta_r_is_n,
            theta_o_sol_bnd_i_jstrs_n=theta_o_sol_bnd_i_jstrs_n
        )

        s.logger.theta_rear_i_jstrs_ns[:, n] = theta_rear_i_jstrs_n

        # ********** 人体発熱および、内部発熱・発湿の計算 **********

        # 人体発熱(W)・発湿(kg/s)
        s.Hhums[n], s.Hhuml[n] = a3.calc_Hhums_and_Hhuml(theta_r_i_n, s.number_of_people_schedule[n])

#        Hns = s.heat_generation_appliances_schedule + s.heat_generation_lighting_schedule + s.Hhums + s.heat_generation_cooking_schedule
        # print(len(s.heat_generation_appliances_schedule)) # 35040 = 365 * 96
        # print(len(s.heat_generation_lighting_schedule))
#        print(len(s.Hhums)) # 105120
#        print(len(s.heat_generation_cooking_schedule)) # 35040
        # 内部発熱[W]
        Hn = (s.heat_generation_appliances_schedule[n] + s.heat_generation_lighting_schedule[n] +
              s.Hhums[n] + s.heat_generation_cooking_schedule[n])
#        print(Hn == Hns[n])

        # 内部発湿[kg/s]
        Lin = s.vapor_generation_cooking_schedule[n] / 1000.0 / 3600.0 + s.Hhuml[n]

        # **** 透過日射の家具、室内部位表面発熱量への分配 ****

        # 室の透過日射熱取得から室内各部位の吸収日射量 式(91)
        s.Sol_i_g_n[:, n] = a12.get_Sol(s.q_trs_sol_i_ns[n], s.Rsol_floor_i_g, s.a_bdry_i_jstrs)

        # 家具の吸収日射量[W] 式(92)
        s.Qsolfun_i_n[n] = a12.get_Qsolfun(s.q_trs_sol_i_ns[n], s.Rsol_fun_i)

        # すきま風量未実装につき、とりあえず０とする
        s.Infset = 0.0

        # 自然室温計算時窓開閉条件の設定
        # 空調需要がなければ窓閉鎖、空調需要がある場合は前時刻の窓開閉状態
        is_now_window_open = s.is_now_window_open_i_n[n - 1] and s.air_conditioning_demand[n]

        # 配列の準備
        Nroot = s.n_root_bdry_i_jstrs
        Row = s.row_bdry_i_jstrs

#        print([s.name_i for s in spaces])
#        print(str(i) + ': ' + str(s.Rtype_i_j))
        # ここのコードはもう少し構造を考え直さないといけない
        # 室名が重複して指定された場合に破綻する。
        idxs = [[i for i, space in enumerate(spaces) if space.name_i == x][0] for x in s.name_vent_up_i_nis]
#        print(str(i) + ':' + str(idxs))
        Tr_next_i_j_nm1 = np.array([theta_r_is_n[x] for x in idxs])
        xr_next_i_j_nm1 = np.array([spaces[x].x_r_i_ns[n - 1] for x in idxs])
#        print(str(i) + ': ' + str(Tr_next_i_j_nm1))

        # 畳み込み積分 式(27)
        for g in range(s.n_bnd_i_jstrs):
            s.TsdA_l_n_m[g, n] = s.oldqi[g] * s.rfa1_bdry_i_jstrs[g] + Row[g] * s.TsdA_l_n_m[g, n - 1]
            s.TsdT_l_n_m[g, n] = theta_rear_i_jstrs_n[g] * s.rft1_bdry_i_jstrs[g] + Row[g] * s.TsdT_l_n_m[g, n - 1]

        # 畳み込み演算 式(26)
        CVL_i_l = a1.get_CVL(s.TsdT_l_n_m[:, n, :], s.TsdA_l_n_m[:, n, :], Nroot)

        # 表面温度を計算するための各種係数  式(24)
        CRX_i_j = a1.get_CRX(s.rft0_bdry_i_jstrs, theta_rear_i_jstrs_n, s.Sol_i_g_n[:, n], s.rfa0_bdry_i_jstrs)
        WSC_i_k = a1.get_WSC(s.AX_k_l, CRX_i_j)
        WSV_i_k = a1.get_WSV(s.AX_k_l, CVL_i_l)

        # 室温・熱負荷計算のための定数項BRCの計算 式(6) ※ただし、通風なし
        BRCnoncv = s41.get_BRC_i(
            WSC_i_k=WSC_i_k,
            WSV_i_k=WSV_i_k,
            area=s.a_bdry_i_jstrs,
            hc_i_k_n=s.hc_i_g_n,
            Ta=To_n,
            Hn=Hn,
            Ventset=s.v_vent_ex_i,
            Infset=s.Infset,
            LocalVentset=s.local_vent_amount_schedule[n],
            Hcap=s.Hcap,
            oldTr=theta_r_i_n,
            Cap_fun_i=s.Capfun,
            C_fun_i=s.Cfun,
            Qsolfun=s.Qsolfun_i_n[n],
            oldTfun=s.Tfun_i_n[n - 1],
            Vnext_i_j=s.v_vent_up_i_nis,
            Tr_next_i_j_nm1=Tr_next_i_j_nm1
        )

        # 仮の窓開閉条件における通風量 NVot の計算
        ca = a18.get_ca()
        rhoa = a18.get_rhoa()
        NVot = a13.get_NV(is_now_window_open, s.v_room_cap_i, s.n_ntrl_vent_i)

        # ********** 非空調(自然)作用温度、PMV の計算 **********

        BRMot_without_ac, BRCot_without_ac, _, Xot_without_ac, XLr_without_ac, XC_without_ac = s41.calc_OT_coeff(
            BRM_i=s.BRMnoncv_i[n] + ca * rhoa * NVot, BRC_i=BRCnoncv + ca * rhoa * NVot * To_n, BRL_i=s.BRL_i[n],
            WSR_i_k=s.WSR_i_k, WSB_i_k=s.WSB_i_k, WSC_i_k=WSC_i_k, WSV_i_k=WSV_i_k, fot=s.Fot_i_g, kc_i=s.kc_i,
            kr_i=s.kr_i)

        # 自然作用温度の計算
        OT_without_ac = s41.get_OT_without_ac(BRCot_without_ac, BRMot_without_ac)

        # 自然室温を計算 式(14)
        Tr_without_ac = s41.get_Tr_i_n(OT_without_ac, 0.0, Xot_without_ac, XLr_without_ac, XC_without_ac)

        # 自然MRTを計算 TODO:仕様書内の場所不明
        MRT_without_ac = (OT_without_ac - s.kc_i * Tr_without_ac) / s.kr_i

        # 着衣量 式(128)
        I_cl = a35.get_I_cl(OT_without_ac)

        # 自然PMVを計算する
        Met_without_ac = 1.0
        Vel_without_ac = 0.0 if not is_now_window_open else 0.1
        Wme_without_ac = 0.0
        PMV_without_ac = a35.calc_PMV(Tr_without_ac, MRT_without_ac, s.RH_i_n[n - 1], Vel_without_ac, Met_without_ac, Wme_without_ac,
                                   I_cl)

        # ********** 窓開閉、空調発停の決定 **********

        # 窓の開閉と空調発停の切り替え判定
        s.is_now_window_open_i_n[n], ac_mode \
            = a13.mode_select(s.air_conditioning_demand[n], s.prev_air_conditioning_mode, s.is_prev_window_open,
                              PMV_without_ac)

        # 目標PMVの計算（冷房時は上限、暖房時は下限PMVを目標値とする）
        # 空調モード: -1=冷房, 0=停止, 1=暖房, 2=, 3=    ==>  [停止, 暖房, 暖房(1), 暖房(2), 冷房]
        PMV_set = [None,
                   s.pmv_lower_limit_schedule[n],
                   s.pmv_lower_limit_schedule[n],
                   s.pmv_lower_limit_schedule[n],
                   s.pmv_upper_limit_schedule[n]][ac_mode]

        # 確定した窓開閉状態における通風量を計算
        NV = a13.get_NV(s.is_now_window_open_i_n[n], s.v_room_cap_i, s.n_ntrl_vent_i)

        # メモ: 窓開閉のいずれの条件で計算したBRM,BRCを採用しているだけに見える。
        #       ⇒両方計算して比較するように記述したほうがシンプル

        # 最終計算のための係数整備
        BRM_i = s.BRMnoncv_i[n] + ca * rhoa * NV
        BRC_i = BRCnoncv + ca * rhoa * NV * To_n

        # OT計算用の係数補正
        BRMot, BRCot, BRLot, Xot, XLr, XC = \
            s41.calc_OT_coeff(BRM_i, BRC_i, s.BRL_i[n], s.WSR_i_k, s.WSB_i_k, WSC_i_k, WSV_i_k, s.Fot_i_g, s.kc_i,
                              s.kr_i)

        # ********** 空調設定温度の計算 **********

        # 前時刻の相対湿度を用い、PMV目標値を満たすような目標作用温度を求める
        OTset, s.Met_i_n[n], s.Clo_i_n[n], s.Vel_i_n[n] = \
            a28.calc_OTset(ac_mode, s.is_radiative_heating, s.RH_i_n[n - 1], PMV_set)

        # 仮の作用温度、熱負荷の計算
        OT_tmp, Lcs_tmp, Lrs_tmp = s41.calc_heatload(ac_mode, s.is_radiative_heating, BRCot, BRMot, BRLot, 0.0, OTset)

        # 放射空調の過負荷状態をチェックする
        ac_mode = a13.reset_SW(ac_mode, Lcs_tmp, Lrs_tmp, s.is_radiative_heating, s.Lrcap_i)

        # 最終作用温度・熱負荷の再計算
        s.OT_i_n[n], s.Lcs_i_n[n], s.Lrs_i_n[n] = \
            s41.calc_heatload(ac_mode, s.is_radiative_heating, BRCot, BRMot, BRLot, s.Lrcap_i, OTset)

        # ********** 室温 Tr、家具温度 Tfun、表面温度 Ts_i_k_n、室内表面熱流 q の計算 **********

        # 自然室温 Tr を計算 式(14)
        s.theta_r_i_ns[n] = s41.get_Tr_i_n(s.OT_i_n[n], s.Lrs_i_n[n], Xot, XLr, XC)

        # 家具の温度 Tfun を計算 式(15)
        s.Tfun_i_n[n] = s41.get_Tfun_i_n(s.Capfun, s.Tfun_i_n[n - 1], s.Cfun, s.theta_r_i_ns[n], s.Qsolfun_i_n[n])
        s.Qfuns_i_n[n] = s41.get_Qfuns(s.Cfun, s.theta_r_i_ns[n], s.Tfun_i_n[n])

        # 表面温度の計算 式(23)
        s.Ts_i_k_n[:, n] = a1.get_surface_temperature(s.WSR_i_k, s.WSB_i_k, WSC_i_k, WSV_i_k, s.theta_r_i_ns[n], s.Lrs_i_n[n])

        # MRT_i_n、AST、平均放射温度の計算
        s.MRT_i_n[n] = get_MRT(s.Fot_i_g, s.Ts_i_k_n[:, n])
        _ = get_AST(s.a_bdry_i_jstrs, s.Ts_i_k_n[:, n], s.A_total_i)

        # 平均放射温度の計算
        _ = a1.get_Tsx(s.F_mrt_i_g, s.Ts_i_k_n[:, n])

        # 室内側等価温度の計算 式(29)
        s.Tei_i_k_n[:, n] = a1.calc_Tei(s.hc_i_g_n, s.h_i_bdry_i_jstrs, s.hr_i_g_n, s.Sol_i_g_n[:, n], s.flr_i_k,
                                        s.a_bdry_i_jstrs, s.theta_r_i_ns[n], s.F_mrt_i_g, s.Ts_i_k_n[:, n], s.Lrs_i_n[n],
                                        s.Beta_i)

        # 室内表面熱流の計算 式(28)
        s.Qc[:, n], s.Qr[:, n], s.Lr, s.RS, Qt, s.oldqi = a1.calc_qi(s.hc_i_g_n, s.a_bdry_i_jstrs, s.hr_i_g_n, s.Sol_i_g_n[:, n],
                                                                     s.flr_i_k,
                                                         s.Ts_i_k_n[:, n], s.theta_r_i_ns[n], s.F_mrt_i_g, s.Lrs_i_n[n],
                                                                     s.Beta_i)

        # ********** 室湿度 xr、除湿量 G_hum、湿加湿熱量 Ll の計算 **********

        # 式(17)
        BRMX_pre = s42.get_BRMX(
            Ventset=s.v_vent_ex_i,
            Infset=s.Infset,
            LocalVentset=s.local_vent_amount_schedule[n],
            Gf=s.Gf_i,
            Cx=s.Cx_i,
            volume=s.v_room_cap_i,
            Vnext_i_j=s.v_vent_up_i_nis
        )

        # 式(18)
        BRXC_pre = s42.get_BRXC(
            Ventset=s.v_vent_ex_i,
            Infset=s.Infset,
            LocalVentset=s.local_vent_amount_schedule[n],
            Gf=s.Gf_i,
            Cx=s.Cx_i,
            volume=s.v_room_cap_i,
            Vnext_i_j=s.v_vent_up_i_nis,
            xr_next_i_j_nm1=xr_next_i_j_nm1,
            xr_i_nm1=s.x_r_i_ns[n - 1],
            xf_i_nm1=s.xf_i_n[n - 1],
            Lin=Lin,
            xo=xo_n
        )

        # ==== ルームエアコン吹出絶対湿度の計算 ====

        # バイパスファクターBF 式(114)
        BF = a16.get_BF()

        # 空調の熱交換部飽和絶対湿度の計算
        s.Vac_n[n], s.xeout_i_n[n] = \
            a16.calcVac_xeout(s.Lcs_i_n[n], s.Vmin_i, s.Vmax_i, s.qmin_c_i, s.qmax_c_i, s.theta_r_i_ns[n], BF, ac_mode)

        # 空調機除湿の項 式(20)より
        RhoVac = get_RhoVac(s.Vac_n[n], BF)

        # 室絶対湿度[kg/kg(DA)]の計算
        BRMX_base = BRMX_pre + RhoVac
        BRXC_base = BRXC_pre + RhoVac * s.xeout_i_n[n]

        # 室絶対湿度の計算 式(16)
        xr_base = s42.get_xr(BRXC_base, BRMX_base)

        # 補正前の加湿量の計算 [ks/s] 式(20)
        Ghum_base = s42.get_Ghum(RhoVac, s.xeout_i_n[n], xr_base)

        # 除湿量が負値(加湿量が正)になった場合にはルームエアコン風量V_(ac,n)をゼロとして再度室湿度を計算する
        if Ghum_base > 0.0:
            s.Ghum_i_n[n] = 0.0
            BRMX = BRMX_pre
            BRXC = BRXC_pre

            # 空調機除湿の項の再計算（除湿なしで計算） ???
            s.Va = 0.0

            # 室絶対湿度の計算 式(16)
            s.x_r_i_ns[n] = s42.get_xr(BRXC_pre, BRMX_pre)
        else:
            s.Ghum_i_n[n] = Ghum_base
            BRMX = BRMX_base
            BRXC = BRXC_base
            s.x_r_i_ns[n] = xr_base

        # 除湿量から室加湿熱量を計算 式(21)
        s.Lcl_i_n[n] = get_Lcl(s.Ghum_i_n[n])

        # 当面は放射空調の潜熱は0
        s.Lrl_i_n[n] = get_Lrl()

        # 室相対湿度の計算 式(22)
        s.RH_i_n[n] = rhtx(s.theta_r_i_ns[n], s.x_r_i_ns[n])

        # ********** 備品類の絶対湿度 xf の計算 **********

        # 備品類の絶対湿度の計算
        s.xf_i_n[n] = s42.get_xf(s.Gf_i, s.xf_i_n[n - 1], s.Cx_i, s.x_r_i_ns[n])
        s.Qfunl_i_n[n] = s42.get_Qfunl(s.Cx_i, s.x_r_i_ns[n], s.xf_i_n[n])

        # PMVの計算
        s.PMV_i_n[n] = \
            a35.calc_PMV(s.theta_r_i_ns[n], s.MRT_i_n[n], s.RH_i_n[n], s.Vel_i_n[n], s.Met_i_n[n], s.Wme_i_n[n], s.Clo_i_n[n])

        # ********** 窓開閉、空調発停の決定 **********

        # 当該時刻の空調状態、窓開閉状態を控える
        s.prev_air_conditioning_mode = ac_mode

        # 保存(4)
        s.now_air_conditioning_mode[n] = ac_mode


# MRTの計算
def get_MRT(fot, Ts):
    return np.sum(fot * Ts)


# ASTの計算
def get_AST(area, Ts, Atotal):
    return np.sum(area * Ts / Atotal)


# 当面は放射空調の潜熱は0
def get_Lrl():
    return 0.0


# 除湿量から室加湿熱量を計算 式(21)
def get_Lcl(Ghum: float):
    """除湿量から室加湿熱量を計算

    :param Ghum: i室のn時点における除湿量 [ks/s]
    :return:
    """
    conra = a18.get_conra()
    return Ghum * conra


# 式(20)のうちの一部
def get_RhoVac(Vac: float, BF: float):
    rhoa = a18.get_rhoa()
    return rhoa * Vac * (1.0 - BF)
