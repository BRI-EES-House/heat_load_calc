import numpy as np

import s4_1_sensible_heat as s41
import s4_2_latent_heat as s42

import a1_calculation_surface_temperature as a1
import a9_rear_surface_equivalent_temperature as a9
import a12_indoor_radiative_heat_transfer as a12
import a13_Win_ACselect as a13
import a16_blowing_condition_rac as a16
import a29_local_vent_schedule as a29
import a30_internal_heat_schedule as a30
import a31_lighting_schedule as a31
import a32_resident_schedule as a32
import a35_1_PMV as a35_1
import a35_2_set_point_temperature as a35_2

from NextVent import update_oldstate
from common import get_nday, conca, conrowa, conra
from Psychrometrics import xtrh, rhtx


# 室温、熱負荷の計算
def calcHload(space, is_actual_calc, calc_time_interval, spaces, dtmNow, Ta: float, xo: float, sequence_number: int):
    # 室間換気の風上室温をアップデート
    for roomvent in space.RoomtoRoomVent:
        windward_roomname = roomvent.windward_roomname
        update_oldstate(roomvent, spaces[windward_roomname].oldTr, spaces[windward_roomname].oldxr)

    # ********** 毎時計算5 裏面相当温度の計算 **********

    for surface in space.input_surfaces:
        # 前時刻の相当外気温度を控える
        surface.oldTeo = surface.Teo

        # 裏面温度の計算
        surface.Teo = a9.calc_Teo(surface, Ta, space.oldTr, spaces, sequence_number)

    # ********** 毎時計算8 内部発熱、内部発湿の計算、計画換気、すきま風、局所換気の設定 **********

    # 当該時刻の機器・調理発熱の読み込み
    heat_generation_appliances, heat_generation_cooking, vapor_generation_cooking \
        = a30.get_hourly_internal_heat_schedules(space, dtmNow)

    # 当該時刻の照明発熱の読み込み
    heat_generation_lighting = a31.get_hourly_lighting_schedules(space, dtmNow)

    # 当該時刻の人体発熱の読み込み
    number_of_people, Humans, Humanl = a32.get_hourly_resident_schedules(space, dtmNow)

    # 内部発熱[W]
    Hn = heat_generation_appliances + heat_generation_lighting + Humans + heat_generation_cooking

    # 内部発湿[kg/s]
    Lin = vapor_generation_cooking / 1000.0 / 3600.0 + Humanl

    # 当該時刻の局所換気量の読み込み
    LocalVentset = a29.get_hourly_local_vent_schedules(space, dtmNow)

    # 保存
    space.heat_generation_appliances = heat_generation_appliances
    space.heat_generation_cooking = heat_generation_cooking
    space.vapor_generation_cooking = vapor_generation_cooking
    space.heat_generation_lighting = heat_generation_lighting
    space.number_of_people = number_of_people
    space.Humans = Humans
    space.Humanl = Humanl
    space.Lin = Lin
    space.LocalVentset = LocalVentset

    # ********** 当該時刻の空調スケジュールの読み込み **********
    is_upper_temp_limit_set, \
        is_lower_temp_limit_set, \
            pmv_upper_limit, \
                pmv_lower_limit, \
                    air_conditioning_demand = a13.get_hourly_air_conditioning_schedules(space, dtmNow)

    space.is_upper_temp_limit_set = is_upper_temp_limit_set
    space.is_lower_temp_limit_set = is_lower_temp_limit_set
    space.pmv_upper_limit = pmv_upper_limit
    space.pmv_lower_limit = pmv_lower_limit
    space.air_conditioning_demand = air_conditioning_demand

    # 室内表面の吸収日射量
    a12.distribution_transmitted_solar_radiation(space, space.Qgt[sequence_number])

    # 流入外気風量の計算
    # 計画換気・すきま風量
    space.Ventset = space.Vent

    # すきま風量未実装につき、とりあえず０とする
    space.Infset = 0.0

    # 自然室温計算時窓開閉条件の設定
    # 空調需要がなければ窓閉鎖、空調需要がある場合は前時刻の窓開閉状態
    is_now_window_open = space.is_prev_window_open and air_conditioning_demand

    # 配列の準備
    fot = np.array([x.fot for x in space.input_surfaces])
    area = np.array([x.area for x in space.input_surfaces])
    Fmrt = np.array([x.Fmrt for x in space.input_surfaces])
    hic = np.array([x.hic for x in space.input_surfaces])
    hi = np.array([x.hi for x in space.input_surfaces])
    hir = np.array([x.hir for x in space.input_surfaces])
    RSsol = np.array([x.RSsol for x in space.input_surfaces])
    flr = np.array([x.hi for x in space.input_surfaces])
    oldTsd_t = np.array([x.oldTsd_t for x in space.input_surfaces])
    oldTsd_a = np.array([x.oldTsd_a for x in space.input_surfaces])

    RFT0 = np.array([x.RFT0 for x in space.input_surfaces])
    Teo = np.array([x.Teo for x in space.input_surfaces])
    RFA0 = np.array([x.RFA0 for x in space.input_surfaces])
    RFT1 = np.array([x.RFT1 for x in space.input_surfaces])
    RFA1 = np.array([x.RFA1 for x in space.input_surfaces])
    Nroot = np.array([x.Nroot for x in space.input_surfaces])
    oldTeo = np.array([x.oldTeo for x in space.input_surfaces])
    oldqi = np.array([x.oldqi for x in space.input_surfaces])
    Row = np.array([x.Row for x in space.input_surfaces])
    nextroom_volume = np.array([x.volume for x in space.RoomtoRoomVent])
    nextroom_oldTr = np.array([x.oldTr for x in space.RoomtoRoomVent])

    # 畳み込み積分 式(27)
    for i in range(space.Nsurf):
        oldTsd_t[i] = oldTeo[i] * RFT1[i] + Row[i] * oldTsd_t[i]
        oldTsd_a[i] = oldqi[i] * RFA1[i] + Row[i] * oldTsd_a[i]

    # 畳み込み演算 式(26)
    matCVL = a1.get_CVL(oldTsd_t, oldTsd_a, Nroot)

    # {CRX}の作成  式(24)
    matCRX = a1.get_CRX(RFT0, Teo, RSsol, RFA0)

    # {WSC}=[XA]*{CRX} 式(24)
    matWSC = a1.get_WSC(space.matAX, matCRX)

    # {WSV}=[XA]*{CVL} 式(24)
    matWSV = a1.get_WSV(space.matAX, matCVL)

    # 室温・熱負荷計算のための定数項BRCの計算 式(6)
    BRC = s41.get_BRC(matWSC, matWSV, area, hic, calc_time_interval, Ta, Hn, space.Ventset, space.Infset,
                  space.LocalVentset, space.Hcap, space.oldTr, space.Capfun, space.Cfun, space.Qsolfun,
                  space.oldTfun, nextroom_volume, nextroom_oldTr)

    # 窓開閉、空調発停判定のための自然室温計算
    # 通風なしでの係数を控えておく
    space.BRMnoncv = space.BRM[sequence_number]
    space.BRCnoncv = BRC

    # 通風計算用に係数を補正（前時刻が通風状態の場合は非空調作用温度を通風状態で計算する）
    temp = get_temp(is_now_window_open, space.Vcrossvent)

    # ********** 毎時計算10. BRMot,BRCot,BRLotの計算 **********

    BRMot, BRLot, BRCot, Xot, XLr, XC = s41.calc_OT_coeff(BRC=BRC + temp * Ta, BRM=space.BRM[sequence_number] + temp,
                                                          matWSV=matWSV, matWSC=matWSC, fot=fot, matWSR=space.matWSR,
                                                          matWSB=space.matWSB, kc=space.kc, kr=space.kr,
                                                          BRL=space.BRL[sequence_number])

    # ********** 非空調作用温度、PMV の計算 **********

    # 自然作用温度の計算
    OT, Lcs, Lrs = calc_Tr_Ls(0, space.is_radiative_heating, BRCot, BRMot, BRLot, 0, 0.0)

    # 自然室温を計算
    Tr = s41.get_Tr(Lrs, OT, Xot, XLr, XC)

    # 自然MRTを計算
    MRT = (OT - space.kc * Tr) / space.kr

    # 着衣量
    I_cl = a35_2.calc_clothing(OT)

    # 自然PMVを計算する
    PMV = a35_1.calcPMV(Tr, MRT, space.RH, 0.0 if not is_now_window_open else 0.1, 1.0, 0.0, I_cl)

    # ********** 窓開閉、空調発停の決定 **********

    # 窓開閉と空調発停の判定をする
    is_now_window_open, now_air_conditioning_mode \
        = a13.mode_select(space.air_conditioning_demand, space.prev_air_conditioning_mode, space.is_prev_window_open, PMV)

    # 目標PMVの計算（冷房時は上限、暖房時は下限PMVを目標値とする）
    pmv_set = space.pmv_lower_limit if now_air_conditioning_mode > 0 else space.pmv_upper_limit

    # 通風なら通風量を設定
    temp = get_temp(is_now_window_open, space.Vcrossvent)

    # 最終計算のための係数整備
    space.BRM[sequence_number] += temp
    BRC += temp * Ta

    # OT計算用の係数補正
    BRMot, BRLot, BRCot, Xot, XLr, XC = s41.calc_OT_coeff(BRC=BRC, BRM=space.BRM[sequence_number], matWSV=matWSV, matWSC=matWSC, fot=fot,
                                                          matWSR=space.matWSR, matWSB=space.matWSB, kc=space.kc,
                                                          kr=space.kr, BRL=space.BRL[sequence_number])

    # ********** 空調設定温度の計算 **********

    # 目標作用温度、代謝量、着衣量、風速の計算
    OTset, Met, Clo, Vel = a35_2.calcOTset(now_air_conditioning_mode, space.is_radiative_heating, space.RH, pmv_set)

    # 仮の作用温度、熱負荷の計算
    OT, Lcs, Lrs = calc_Tr_Ls(now_air_conditioning_mode,
                                                    space.is_radiative_heating, BRCot, BRMot,
                                                    BRLot, 0, OTset)
    # 放射空調の過負荷状態をチェックする
    now_air_conditioning_mode = a13.reset_SW(now_air_conditioning_mode, Lcs, Lrs, space.is_radiative_heating, space.radiative_heating_max_capacity)

    # 最終作用温度・熱負荷の再計算
    OT, Lcs, Lrs = calc_Tr_Ls(now_air_conditioning_mode,
                                                    space.is_radiative_heating, BRCot, BRMot,
                                                    BRLot, space.radiative_heating_max_capacity, OTset)

    # ********** 室温 Tr、表面温度 Ts、室内表面熱流 q の計算 **********

    # 室温を計算
    Tr = s41.get_Tr(Lrs, OT, Xot, XLr, XC)

    # 表面温度の計算 式(23)
    Ts = a1.get_surface_temperature(space.matWSR, space.matWSB, matWSC, matWSV, Tr, Lrs)

    # MRT、AST、平均放射温度の計算
    MRT = get_MRT(fot, Ts)
    AST = get_AST(area, Ts, space.Atotal)

    # 平均放射温度の計算
    Tsx = a1.get_Tsx(Fmrt, Ts)

    # 室内側等価温度の計算 式(29)
    Tei = a1.calc_Tei(hic, hi, hir, RSsol, flr, area, Tr, Fmrt, Ts, Lrs, space.Beta)

    # 室内表面熱流の計算 式(28)
    Qc, Qr, Lr, RS, Qt, oldqi = a1.calc_qi(hic, area, hir, RSsol, flr, Ts, Tr, Fmrt, Lrs, space.Beta)

    # 保存1
    for i, surface in enumerate(space.input_surfaces):
        surface.Tei = Tei[i]
        surface.Qc = Qc[i]
        surface.Qr = Qr[i]
        surface.Lr = Lr[i]
        surface.RS = RS[i]
        surface.Qt = Qt[i]
        surface.Ts = Ts[i]
        surface.oldqi = oldqi[i]
        surface.oldTsd_t = oldTsd_t[i]
        surface.oldTsd_a = oldTsd_a[i]

    # 保存2
    space.MRT = MRT
    space.AST = AST
    space.Tsx = Tsx
    space.Tr = Tr
    space.OT = OT
    space.Lcs = Lcs
    space.Lrs = Lrs
    space.Met = Met
    space.Clo = Clo
    space.Vel = Vel
    space.OTset = OTset
    space.BRC = BRC
    space.BRMot = BRMot
    space.BRLot = BRLot
    space.BRCot = BRCot
    space.Xot = Xot
    space.XLr = XLr
    space.XC = XC
    space.is_now_window_open = is_now_window_open
    space.Hn = Hn

    # ********** 室湿度 xr、除湿量 G_hum、湿加湿熱量 Ll の計算 **********


    # 式(17)
    BRMX_pre = s42.get_BRMX(
        Ventset = space.Ventset,
        Infset=space.Infset,
        LocalVentset=space.LocalVentset,
        Gf=space.Gf,
        Cx=space.Cx,
        volume=space.volume,
        RoomtoRoomVent=space.RoomtoRoomVent,
        Dtime=calc_time_interval,
    )

    # 式(18)
    BRXC_pre = s42.get_BRXC(
        Ventset = space.Ventset,
        Infset=space.Infset,
        LocalVentset=space.LocalVentset,
        Gf=space.Gf,
        Cx=space.Cx,
        volume=space.volume,
        RoomtoRoomVent=space.RoomtoRoomVent,
        oldxr=space.oldxr,
        oldxf=space.oldxf,
        Lin=space.Lin,
        Dtime=calc_time_interval,
        xo=xo
    )

    # ==== ルームエアコン吹出絶対湿度の計算 ====

    # バイパスファクターBF 式(114)
    BF = a16.get_BF()

    # 空調の熱交換部飽和絶対湿度の計算
    Vac, Teout, xeout = a16.calcVac_xeout(space.Lcs, space.Vmin, space.Vmax, space.qmin_c,
                                                  space.qmax_c, space.Tr, BF, now_air_conditioning_mode)

    # 空調機除湿の項 式(20)より
    RhoVac = get_RhoVac(Vac, BF)

    # 室絶対湿度[kg/kg(DA)]の計算
    BRMX_base = BRMX_pre + RhoVac
    BRXC_base = BRXC_pre + RhoVac * xeout

    # 室絶対湿度の計算 式(16)
    xr_base = s42.get_xr(BRXC_base, BRMX_base)

    # 補正前の加湿量の計算 [ks/s] 式(20)
    Ghum_base = s42.get_Ghum(RhoVac, xeout, xr_base)

    # 除湿量が負値になった場合にはルームエアコン風量V_(ac,n)をゼロとして再度室湿度を計算する
    if Ghum_base > 0.0:
        Ghum = 0.0
        BRMX = BRMX_pre
        BRXC = BRXC_pre

        # 空調機除湿の項の再計算（除湿なしで計算） ???
        space.Va = 0.0

        # 室絶対湿度の計算 式(16)
        xr = s42.get_xr(BRXC_pre, BRMX_pre)
    else:
        Ghum = Ghum_base
        BRMX = BRMX_base
        BRXC = BRXC_base
        xr = xr_base

    # 除湿量から室加湿熱量を計算 式(21)
    Lcl = get_Lcl(Ghum)

    # 当面は放射空調の潜熱は0
    Lrl = get_Lrl()

    # 室相対湿度の計算 式(22)
    RH = rhtx(space.Tr, xr)

    # 計算結果の保存 (3)
    space.BRMX = BRMX
    space.BRXC = BRXC
    space.xr = xr
    space.Lcl = Lcl
    space.Lrl = Lrl
    space.Ghum = Ghum
    space.RH = RH
    space.Vac = Vac
    space.xeout = xeout
    space.Teout = Teout

    # ********** 家具温度 T_fun、備品類の絶対湿度 xf の計算 **********

    # 家具の温度を計算
    if space.Capfun > 0.0:
        # 家具の温度 式(15)
        Tfun = s41.get_Tfun(calc_time_interval, space.Capfun, space.oldTfun, space.Cfun, Tr, space.Qsolfun)
        Qfuns = s41.get_Qfuns(space.Cfun, Tr, Tfun)
    else:
        Tfun = 0
        Qfuns = 0

    # 備品類の絶対湿度の計算
    xf = s42.get_xf(calc_time_interval, space.Gf, space.oldxf, space.Cx, xr)
    Qfunl = s42.get_Qfunl(space.Cx, xr, xf)

    space.Tfun, space.Qfuns = Tfun, Qfuns
    space.xf, space.Qfunl = xf, Qfunl

    # 年間熱負荷の積算
    # 助走計算以外の時だけ積算
    if is_actual_calc == True:
        calc_annual_heat_load(space, calc_time_interval)

    # PMVの計算 (ここでもう一度PMVを計算している理由が不明)
    PMV = a35_1.calcPMV(Tr, MRT, space.RH, Vel, Met, space.Wme, Clo)

    # ********** 窓開閉、空調発停の決定 **********

    # 当該時刻の空調状態、窓開閉状態を控える
    space.prev_air_conditioning_mode = now_air_conditioning_mode
    space.is_prev_window_open = space.is_now_window_open

    # 保存(4)
    space.now_air_conditioning_mode = now_air_conditioning_mode
    space.PMV = PMV

    return 0


def get_temp(is_now_window_open, Vcrossvent):
    if is_now_window_open == True:
        temp = conca * conrowa * Vcrossvent / 3600.0
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
def calc_annual_heat_load(space, DTime):
    convert_J_GJ = 1.0e-9
    # 対流式空調（顕熱）の積算
    if space.Lcs > 0.0:
        space.AnnualLoadcHs += space.Lcs * DTime * convert_J_GJ
    else:
        space.AnnualLoadcCs += space.Lcs * DTime * convert_J_GJ
    
    # 対流式空調（潜熱）の積算
    if space.Lcl > 0.0:
        space.AnnualLoadcHl += space.Lcl * DTime * convert_J_GJ
    else:
        space.AnnualLoadcCs += space.Lcl * DTime * convert_J_GJ

    # 放射式空調（顕熱）の積算
    if space.Lrs > 0.0:
        space.AnnualLoadrHs += space.Lrs * DTime * convert_J_GJ
    else:
        space.AnnualLoadrCs += space.Lrs * DTime * convert_J_GJ

    # 放射式空調（潜熱）の積算
    if space.Lrl > 0.0:
        space.AnnualLoadrHl += space.Lrl * DTime * convert_J_GJ
    else:
        space.AnnualLoadrCl += space.Lrl * DTime * convert_J_GJ


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


# 潜熱負荷の計算
def get_Lcl(Ghum):
    """除湿量から室加湿熱量を計算

    :param Ghum: i室のn時点における除湿量 [ks/s]
    :return:
    """
    return Ghum * conra


def get_RhoVac(Vac, BF):
    # 式(20)のうちの一部
    return conrowa * Vac * (1.0 - BF)
