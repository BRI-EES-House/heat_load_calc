import numpy as np

import s4_1_sensible_heat as s41
import s4_2_latent_heat as s42

import a1_calculation_surface_temperature as a1
import a9_rear_surface_equivalent_temperature as a9
import a12_indoor_radiative_heat_transfer as a12
import a13_Win_ACselect as a13
import a16_blowing_condition_rac as a16
import a18_initial_value_constants as a18
import a29_local_vent_schedule as a29
import a30_internal_heat_schedule as a30
import a31_lighting_schedule as a31
import a32_resident_schedule as a32
import a35_1_PMV as a35_1
import a35_2_set_point_temperature as a35_2

from Psychrometrics import rhtx


# 室温、熱負荷の計算
def calcHload(is_actual_calc, spaces, dtmNow, To_n: float, xo: float, n: int):
    for i, s in spaces.items():

        # ********** 毎時計算5 裏面相当温度の計算 **********

        # 裏面温度の計算
        s.Teo_i_k_n[:, n] = a9.calc_Teo(s.surfG_i, To_n, s.Tr_i_n[n - 1], spaces, n)

        # ********** 毎時計算8 内部発熱、内部発湿の計算、計画換気、すきま風、局所換気の設定 **********

        # 当該時刻の機器・調理発熱の読み込み
        heat_generation_appliances, heat_generation_cooking, vapor_generation_cooking \
            = a30.get_hourly_internal_heat_schedules(s, dtmNow)

        # 当該時刻の照明発熱の読み込み
        heat_generation_lighting = a31.get_hourly_lighting_schedules(s, dtmNow)

        # 当該時刻の人体発熱の読み込み
        number_of_people, Humans, Humanl = a32.get_hourly_resident_schedules(s, dtmNow, n)

        # 内部発熱[W]
        Hn = heat_generation_appliances + heat_generation_lighting + Humans + heat_generation_cooking

        # 内部発湿[kg/s]
        Lin = vapor_generation_cooking / 1000.0 / 3600.0 + Humanl

        # 当該時刻の局所換気量の読み込み
        LocalVentset = a29.get_hourly_local_vent_schedules(s, dtmNow)

        # 保存
        s.heat_generation_appliances = heat_generation_appliances
        s.heat_generation_cooking = heat_generation_cooking
        s.vapor_generation_cooking = vapor_generation_cooking
        s.heat_generation_lighting = heat_generation_lighting
        s.number_of_people = number_of_people
        s.Humans = Humans
        s.Humanl = Humanl
        s.Lin = Lin
        s.LocalVentset = LocalVentset

        # ********** 当該時刻の空調スケジュールの読み込み **********
        # TODO: 一括読み込みにしたい
        is_upper_temp_limit_set, \
        is_lower_temp_limit_set, \
        pmv_upper_limit, \
        pmv_lower_limit, \
        air_conditioning_demand = a13.get_hourly_air_conditioning_schedules(s, dtmNow)

        s.is_upper_temp_limit_set = is_upper_temp_limit_set
        s.is_lower_temp_limit_set = is_lower_temp_limit_set
        s.pmv_upper_limit = pmv_upper_limit
        s.pmv_lower_limit = pmv_lower_limit
        s.air_conditioning_demand = air_conditioning_demand

        # **** 透過日射の家具、室内部位表面発熱量への分配 ****

        # 室の透過日射熱取得から室内各部位の吸収日射量 式(91)
        s.Sol_i_g_n[:, n] = a12.get_Sol(s.QGT_i_n[n], s.Rsol_floor_i_g, s.surfG_i.A_i_g)

        # 家具の吸収日射量[W] 式(92)
        s.Qsolfun_i_n[n] = a12.get_Qsolfun(s.QGT_i_n[n], s.Rsol_fun_i)

        # 流入外気風量の計算
        # 計画換気・すきま風量
        s.Ventset = s.Vent

        # すきま風量未実装につき、とりあえず０とする
        s.Infset = 0.0

        # 自然室温計算時窓開閉条件の設定
        # 空調需要がなければ窓閉鎖、空調需要がある場合は前時刻の窓開閉状態
        is_now_window_open = s.is_now_window_open_i_n[n - 1] and air_conditioning_demand

        # 配列の準備
        Nroot = s.surfG_i.Nroot
        Row = s.surfG_i.Row
        Tr_next_i_j_nm1 = np.array([spaces[x].Tr_i_n[n - 1] for x in s.Rtype_i_j])
        xr_next_i_j_nm1 = np.array([spaces[x].xr_i_n[n - 1] for x in s.Rtype_i_j])

        # 畳み込み積分 式(27)
        for g in range(s.NsurfG_i):
            s.TsdA_l_n_m[g, n] = s.oldqi[g] * s.surfG_i.RFA1[g] + Row[g] * s.TsdA_l_n_m[g, n - 1]
            s.TsdT_l_n_m[g, n] = s.Teo_i_k_n[g, n - 1] * s.surfG_i.RFT1[g] + Row[g] * s.TsdT_l_n_m[g, n - 1]

        # 畳み込み演算 式(26)
        CVL_i_l = a1.get_CVL(s.TsdT_l_n_m[:, n, :], s.TsdA_l_n_m[:, n, :], Nroot)

        # 表面温度を計算するための各種係数  式(24)
        CRX_i_j = a1.get_CRX(s.surfG_i.RFT0, s.Teo_i_k_n[:, n], s.Sol_i_g_n[:, n], s.surfG_i.RFA0)
        WSC_i_k = a1.get_WSC(s.AX_k_l, CRX_i_j)
        WSV_i_k = a1.get_WSV(s.AX_k_l, CVL_i_l)

        # 室温・熱負荷計算のための定数項BRCの計算 式(6)
        BRC_i = s41.get_BRC_i(
            WSC_i_k=WSC_i_k,
            WSV_i_k=WSV_i_k,
            area=s.surfG_i.A_i_g,
            hc_i_k_n=s.hc_i_g_n,
            Ta=To_n,
            Hn=Hn,
            Ventset=s.Ventset,
            Infset=s.Infset,
            LocalVentset=s.LocalVentset,
            Hcap=s.Hcap,
            oldTr=s.Tr_i_n[n - 1],
            Cap_fun_i=s.Capfun,
            C_fun_i=s.Cfun,
            Qsolfun=s.Qsolfun_i_n[n],
            oldTfun=s.Tfun_i_n[n - 1],
            Vnext_i_j=s.Vnext_i_j,
            Tr_next_i_j_nm1=Tr_next_i_j_nm1
        )

        # 窓開閉、空調発停判定のための自然室温計算
        # 通風なしでの係数を控えておく
        s.BRMnoncv = s.BRM_i[n]
        s.BRCnoncv = BRC_i

        # 通風計算用に係数を補正（前時刻が通風状態の場合は非空調作用温度を通風状態で計算する）
        temp = get_temp(is_now_window_open, s.NV_i_n[n])

        # ********** 毎時計算10. BRMot,BRCot,BRLotの計算 **********

        BRMot, BRLot, BRCot, Xot, XLr, XC = s41.calc_OT_coeff(
            BRC_i=BRC_i + temp * To_n,
            BRM_i=s.BRM_i[n] + temp,
            WSV_i_k=WSV_i_k,
            WSC_i_k=WSC_i_k,
            fot=s.Fot_i_g,
            WSR_i_k=s.WSR_i_k,
            WSB_i_k=s.WSB_i_k,
            kc_i=s.kc_i,
            kr_i=s.kr_i,
            BRL_i=s.BRL_i[n]
        )

        # ********** 非空調作用温度、PMV_i_n の計算 **********

        # 自然作用温度の計算
        OT_natural, Lcs_natural, Lrs_natural = calc_Tr_Ls(0, s.is_radiative_heating, BRCot, BRMot, BRLot, 0, 0.0)

        # 自然室温を計算
        Tr_natural = s41.get_Tr_i_n(Lrs_natural, OT_natural, Xot, XLr, XC)

        # 自然MRTを計算
        MRT_natural = (OT_natural - s.kc_i * Tr_natural) / s.kr_i

        # 着衣量
        I_cl = a35_2.calc_clothing(OT_natural)

        # 自然PMVを計算する
        PMV_natural = a35_1.calc_PMV(Tr_natural, MRT_natural, s.RH_i_n[n - 1], 0.0 if not is_now_window_open else 0.1,
                                     1.0, 0.0, I_cl)

        # ********** 窓開閉、空調発停の決定 **********

        # 窓開閉と空調発停の判定をする
        s.is_now_window_open_i_n[n], now_air_conditioning_mode \
            = a13.mode_select(s.air_conditioning_demand, s.prev_air_conditioning_mode, s.is_prev_window_open,
                              PMV_natural)

        # 目標PMVの計算（冷房時は上限、暖房時は下限PMVを目標値とする）
        pmv_set = s.pmv_lower_limit if now_air_conditioning_mode > 0 else s.pmv_upper_limit

        # 通風なら通風量を設定
        temp = get_temp(s.is_now_window_open_i_n[n], s.NV_i_n[n])

        # 最終計算のための係数整備
        s.BRM_i[n] += temp
        BRC_i += temp * To_n

        # OT計算用の係数補正
        BRMot, BRLot, BRCot, Xot, XLr, XC = s41.calc_OT_coeff(
            BRC_i=BRC_i,
            BRM_i=s.BRM_i[n],
            WSV_i_k=WSV_i_k,
            WSC_i_k=WSC_i_k,
            fot=s.Fot_i_g,
            WSR_i_k=s.WSR_i_k,
            WSB_i_k=s.WSB_i_k,
            kc_i=s.kc_i,
            kr_i=s.kr_i,
            BRL_i=s.BRL_i[n]
        )

        # ********** 空調設定温度の計算 **********

        # 目標作用温度、代謝量、着衣量、風速の計算
        OTset, s.Met_i_n[n], s.Clo_i_n[n], s.Vel_i_n[n] = a35_2.calcOTset(now_air_conditioning_mode,
                                                                          s.is_radiative_heating, s.RH_i_n[n - 1],
                                                                          pmv_set)

        # 仮の作用温度、熱負荷の計算
        OT_tmp, Lcs_tmp, Lrs_tmp = calc_Tr_Ls(
            now_air_conditioning_mode=now_air_conditioning_mode,
            is_radiative_heating=s.is_radiative_heating,
            BRC=BRCot,
            BRM=BRMot,
            BRL=BRLot,
            Lrcap=0,
            Tset=OTset
        )

        # 放射空調の過負荷状態をチェックする
        now_air_conditioning_mode = a13.reset_SW(now_air_conditioning_mode, Lcs_tmp, Lrs_tmp, s.is_radiative_heating,
                                                 s.Lrcap_i)

        # 最終作用温度・熱負荷の再計算
        s.OT_i_n[n], s.Lcs_i_n[n], s.Lrs_i_n[n] = calc_Tr_Ls(now_air_conditioning_mode,
                                                             s.is_radiative_heating, BRCot, BRMot,
                                                             BRLot, s.Lrcap_i, OTset)

        # ********** 室温 Tr、表面温度 Ts_i_k_n、室内表面熱流 q の計算 **********

        # 室温を計算
        s.Tr_i_n[n] = s41.get_Tr_i_n(s.Lrs_i_n[n], s.OT_i_n[n], Xot, XLr, XC)

        # 表面温度の計算 式(23)
        s.Ts_i_k_n[:, n] = a1.get_surface_temperature(s.WSR_i_k, s.WSB_i_k, WSC_i_k, WSV_i_k, s.Tr_i_n[n], s.Lrs_i_n[n])

        # MRT_i_n、AST、平均放射温度の計算
        s.MRT_i_n[n] = get_MRT(s.Fot_i_g, s.Ts_i_k_n[:, n])
        _ = get_AST(s.surfG_i.A_i_g, s.Ts_i_k_n[:, n], s.A_total_i)

        # 平均放射温度の計算
        _ = a1.get_Tsx(s.F_mrt_i_g, s.Ts_i_k_n[:, n])

        # 室内側等価温度の計算 式(29)
        s.Tei_i_k_n[:, n] = a1.calc_Tei(s.hc_i_g_n, s.surfG_i.hi_i_g_n, s.hr_i_g_n, s.Sol_i_g_n[:, n], s.flr_i_k,
                                        s.surfG_i.A_i_g, s.Tr_i_n[n], s.F_mrt_i_g, s.Ts_i_k_n[:, n], s.Lrs_i_n[n],
                                        s.Beta_i)

        # 室内表面熱流の計算 式(28)
        Qc, Qr, Lr, RS, Qt, oldqi = a1.calc_qi(s.hc_i_g_n, s.surfG_i.A_i_g, s.hr_i_g_n, s.Sol_i_g_n[:, n], s.flr_i_k,
                                               s.Ts_i_k_n[:, n], s.Tr_i_n[n], s.F_mrt_i_g, s.Lrs_i_n[n], s.Beta_i)

        # 保存1
        s.Lr = Lr
        s.RS = RS
        s.Qc = Qc
        s.Qr = Qr
        s.oldqi = oldqi

        # ********** 室湿度 xr、除湿量 G_hum、湿加湿熱量 Ll の計算 **********

        # 式(17)
        BRMX_pre = s42.get_BRMX(
            Ventset=s.Ventset,
            Infset=s.Infset,
            LocalVentset=s.LocalVentset,
            Gf=s.Gf_i,
            Cx=s.Cx_i,
            volume=s.volume,
            Vnext_i_j=s.Vnext_i_j
        )

        # 式(18)
        BRXC_pre = s42.get_BRXC(
            Ventset=s.Ventset,
            Infset=s.Infset,
            LocalVentset=s.LocalVentset,
            Gf=s.Gf_i,
            Cx=s.Cx_i,
            volume=s.volume,
            Vnext_i_j=s.Vnext_i_j,
            xr_next_i_j_nm1=xr_next_i_j_nm1,
            xr_i_nm1=s.xr_i_n[n - 1],
            xf_i_nm1=s.xf_i_n[n - 1],
            Lin=s.Lin,
            xo=xo
        )

        # ==== ルームエアコン吹出絶対湿度の計算 ====

        # バイパスファクターBF 式(114)
        BF = a16.get_BF()

        # 空調の熱交換部飽和絶対湿度の計算
        s.Vac_n[n], s.xeout_i_n[n] = a16.calcVac_xeout(s.Lcs_i_n[n], s.Vmin_i, s.Vmax_i, s.qmin_c_i,
                                                       s.qmax_c_i, s.Tr_i_n[n], BF, now_air_conditioning_mode)

        # 空調機除湿の項 式(20)より
        RhoVac = get_RhoVac(s.Vac_n[n], BF)

        # 室絶対湿度[kg/kg(DA)]の計算
        BRMX_base = BRMX_pre + RhoVac
        BRXC_base = BRXC_pre + RhoVac * s.xeout_i_n[n]

        # 室絶対湿度の計算 式(16)
        xr_base = s42.get_xr(BRXC_base, BRMX_base)

        # 補正前の加湿量の計算 [ks/s] 式(20)
        Ghum_base = s42.get_Ghum(RhoVac, s.xeout_i_n[n], xr_base)

        # 除湿量が負値になった場合にはルームエアコン風量V_(ac,n)をゼロとして再度室湿度を計算する
        if Ghum_base > 0.0:
            s.Ghum_i_n[n] = 0.0
            BRMX = BRMX_pre
            BRXC = BRXC_pre

            # 空調機除湿の項の再計算（除湿なしで計算） ???
            s.Va = 0.0

            # 室絶対湿度の計算 式(16)
            s.xr_i_n[n] = s42.get_xr(BRXC_pre, BRMX_pre)
        else:
            s.Ghum_i_n[n] = Ghum_base
            BRMX = BRMX_base
            BRXC = BRXC_base
            s.xr_i_n[n] = xr_base

        # 除湿量から室加湿熱量を計算 式(21)
        s.Lcl_i_n[n] = get_Lcl(s.Ghum_i_n[n])

        # 当面は放射空調の潜熱は0
        s.Lrl_i_n[n] = get_Lrl()

        # 室相対湿度の計算 式(22)
        s.RH_i_n[n] = rhtx(s.Tr_i_n[n], s.xr_i_n[n])

        # ********** 家具温度 T_fun、備品類の絶対湿度 xf の計算 **********

        # 家具の温度を計算
        if s.Capfun > 0.0:
            # 家具の温度 式(15)
            s.Tfun_i_n[n] = s41.get_Tfun_i_n(s.Capfun, s.Tfun_i_n[n - 1], s.Cfun, s.Tr_i_n[n], s.Qsolfun_i_n[n])
            s.Qfuns_i_n[n] = s41.get_Qfuns(s.Cfun, s.Tr_i_n[n], s.Tfun_i_n[n])
        else:
            s.Tfun_i_n[n] = 0
            s.Qfuns_i_n[n] = 0

        # 備品類の絶対湿度の計算
        s.xf_i_n[n] = s42.get_xf(s.Gf_i, s.xf_i_n[n - 1], s.Cx_i, s.xr_i_n[n])
        s.Qfunl_i_n[n] = s42.get_Qfunl(s.Cx_i, s.xr_i_n[n], s.xf_i_n[n])

        # 年間熱負荷の積算
        # 助走計算以外の時だけ積算
        if is_actual_calc == True:
            calc_annual_heat_load(s, n)

        # PMVの計算
        s.PMV_i_n[n] = a35_1.calc_PMV(s.Tr_i_n[n], s.MRT_i_n[n], s.RH_i_n[n], s.Vel_i_n[n], s.Met_i_n[n], s.Wme_i_n[n],
                                      s.Clo_i_n[n])

        # ********** 窓開閉、空調発停の決定 **********

        # 当該時刻の空調状態、窓開閉状態を控える
        s.prev_air_conditioning_mode = now_air_conditioning_mode

        # 保存(4)
        s.now_air_conditioning_mode = now_air_conditioning_mode


def get_temp(is_now_window_open, Vcrossvent):
    ca = a18.get_ca()
    rhoa = a18.get_rhoa()

    if is_now_window_open == True:
        temp = ca * rhoa * Vcrossvent / 3600.0
    else:
        temp = 0
    return temp


# MRTの計算
def get_MRT(fot, Ts):
    return np.sum(fot * Ts)


# ASTの計算
def get_AST(area, Ts, Atotal):
    return np.sum(area * Ts / Atotal)


# 年間熱負荷の積算
def calc_annual_heat_load(space, sequence_number):
    convert_J_GJ = 1.0e-9
    DTime = 900
    # 対流式空調（顕熱）の積算
    if space.Lcs_i_n[sequence_number] > 0.0:
        space.AnnualLoadcHs += space.Lcs_i_n[sequence_number] * DTime * convert_J_GJ
    else:
        space.AnnualLoadcCs += space.Lcs_i_n[sequence_number] * DTime * convert_J_GJ

    # 対流式空調（潜熱）の積算
    if space.Lcl_i_n[sequence_number] > 0.0:
        space.AnnualLoadcHl += space.Lcl_i_n[sequence_number] * DTime * convert_J_GJ
    else:
        space.AnnualLoadcCs += space.Lcl_i_n[sequence_number] * DTime * convert_J_GJ

    # 放射式空調（顕熱）の積算
    if space.Lrs_i_n[sequence_number] > 0.0:
        space.AnnualLoadrHs += space.Lrs_i_n[sequence_number] * DTime * convert_J_GJ
    else:
        space.AnnualLoadrCs += space.Lrs_i_n[sequence_number] * DTime * convert_J_GJ

    # 放射式空調（潜熱）の積算
    if space.Lrl_i_n[sequence_number] > 0.0:
        space.AnnualLoadrHl += space.Lrl_i_n[sequence_number] * DTime * convert_J_GJ
    else:
        space.AnnualLoadrCl += space.Lrl_i_n[sequence_number] * DTime * convert_J_GJ


# 室温・顕熱熱負荷の計算ルーティン
def calc_Tr_Ls(now_air_conditioning_mode, is_radiative_heating, BRC, BRM, BRL, Lrcap, Tset):
    Lcs = 0.0
    Lrs = 0.0
    Tr = 0.0
    # 非空調時の計算
    if now_air_conditioning_mode == 0:
        Tr = BRC / BRM
    # 熱負荷計算（能力無制限）
    elif now_air_conditioning_mode == 1 or now_air_conditioning_mode == -1 or now_air_conditioning_mode == 4:
        # 対流式空調の場合
        if is_radiative_heating != True or is_radiative_heating and now_air_conditioning_mode < 0:
            Lcs = BRM * Tset - BRC
        # 放射式空調
        else:
            Lrs = (BRM * Tset - BRC) / BRL
        # 室温の計算
        Tr = (BRC + Lcs + BRL * Lrs) / BRM
    # 放射暖房最大能力運転（当面は暖房のみ）
    elif now_air_conditioning_mode == 3 and Lrcap > 0.0:
        Lrs = Lrcap
        # 室温は対流式で維持する
        Lcs = BRM * Tset - BRC - Lrs * BRL
        # 室温の計算
        Tr = (BRC + Lcs + BRL * Lrs) / BRM

    # 室温、対流空調熱負荷、放射空調熱負荷を返す
    return (Tr, Lcs, Lrs)


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
