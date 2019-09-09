import numpy as np
from inclined_surface_solar_radiation import calc_slope_sol
from NextVent import update_oldstate
from rear_surface_equivalent_temperature import calcTeo
from common import get_nday, conca, conrowa, conra
import blowing_condition_rac as a16     #付録.16
from indoor_radiative_heat_transfer import distribution_transmitted_solar_radiation
from calculation_surface_temperature import get_surface_temperature, get_Tei, \
    calc_CRX_WSC, get_Tei, calc_CVL_WSV, calc_qi, update_Tsd
from Win_ACselect import reset_SW, mode_select
from PMV import calcPMV
from Psychrometrics import xtrh, rhtx
from set_point_temperature import calcOTset, calc_clothing
from apdx6_direction_cos_incident_angle import calc_cos_incident_angle
from local_vent_schedule import get_hourly_local_vent_schedules
from internal_heat_schedule import get_hourly_internal_heat_schedules
from lighting_schedule import get_hourly_lighting_schedules
from resident_schedule import get_hourly_resident_schedules
from Win_ACselect import get_hourly_air_conditioning_schedules

# 室温、熱負荷の計算
def calcHload(space, is_actual_calc, calc_time_interval, spaces, dtmNow, Ta: float, xo: float, sequence_number: int):
    # 室間換気の風上室温をアップデート
    for roomvent in space.RoomtoRoomVent:
        windward_roomname = roomvent.windward_roomname
        update_oldstate(roomvent, spaces[windward_roomname].oldTr, spaces[windward_roomname].oldxr)

    # 裏面温度の計算
    for surface in space.input_surfaces:
        calcTeo(surface, Ta, space.oldTr, spaces, sequence_number)

    # スケジュールの読み込み
    # 当該時刻の局所換気量の読み込み
    space.LocalVentset = get_hourly_local_vent_schedules(space, dtmNow)
    # 当該時刻の機器・調理発熱の読み込み
    space.heat_generation_appliances, space.heat_generation_cooking, space.vapor_generation_cooking \
        = get_hourly_internal_heat_schedules(space, dtmNow)
    # 当該時刻の照明発熱の読み込み
    space.heat_generation_lighting = get_hourly_lighting_schedules(space, dtmNow)
    # 当該時刻の人体発熱の読み込み
    space.number_of_people, space.Humans, space.Humanl = get_hourly_resident_schedules(space, dtmNow)
    # 内部発熱[W]
    space.Hn = space.heat_generation_appliances + space.heat_generation_lighting + space.Humans + space.heat_generation_cooking
    # 内部発湿[kg/s]
    space.Lin = space.vapor_generation_cooking / 1000.0 / 3600.0 + space.Humanl

    # 当該時刻の空調スケジュールの読み込み
    space.is_upper_temp_limit_set, \
        space.is_lower_temp_limit_set, \
            space.pmv_upper_limit, \
                space.pmv_lower_limit, \
                    space.air_conditioning_demand = get_hourly_air_conditioning_schedules(space, dtmNow)

    # 室内表面の吸収日射量
    distribution_transmitted_solar_radiation(space, space.Qgt[sequence_number])

    # 流入外気風量の計算
    # 計画換気・すきま風量
    space.Ventset = space.Vent

    # すきま風量未実装につき、とりあえず０とする
    space.Infset = 0.0

    # 自然室温計算時窓開閉条件の設定
    # 空調需要がなければ窓閉鎖、空調需要がある場合は前時刻の窓開閉状態
    space.is_now_window_open = False
    if space.air_conditioning_demand:
        space.is_now_window_open = space.is_prev_window_open

    # 室温・熱負荷計算のための係数BRM、BRLの計算
    # space.BRM, space.BRL = calc_BRM_BRL(space, calc_time_interval)

    # 室温・熱負荷計算のための定数項BRCの計算
    space.BRC = calc_BRC(space, calc_time_interval, Ta, sequence_number)

    # 窓開閉、空調発停判定のための自然室温計算
    # 通風なしでの係数を控えておく
    space.BRMnoncv = space.BRM[sequence_number]
    space.BRCnoncv = space.BRC
    # 通風計算用に係数を補正（前時刻が通風状態の場合は非空調作用温度を通風状態で計算する）
    if space.is_now_window_open == True:
        temp = conca * conrowa * space.Vcrossvent / 3600.0
        space.BRM[sequence_number] += temp
        space.BRC += temp * Ta

    # OT計算用の係数補正
    space.BRMot, space.BRLot, space.BRCot, space.Xot, space.XLr, space.XC = convert_coefficient_for_operative_temperature(space, sequence_number)
    
    # 自然作用温度の計算
    space.OT, space.Lcs, space.Lrs = calc_Tr_Ls(0, space.is_radiative_heating, space.BRCot, space.BRMot,
                                                space.BRLot, 0, 0.0)
    # 自然室温を計算
    space.Tr = space.Xot * space.OT - space.XLr * space.Lrs - space.XC
    # 自然MRTを計算
    space.MRT = (space.OT - space.kc * space.Tr) / space.kr
    # 自然PMVを計算する
    space.PMV = calcPMV(space.Tr, space.MRT, space.RH, \
        0.0 if not space.is_now_window_open else 0.1, 1.0, 0.0, calc_clothing(space.OT))
    # 窓開閉と空調発停の判定をする
    space.is_now_window_open, space.now_air_conditioning_mode \
        = mode_select(space.air_conditioning_demand, space.prev_air_conditioning_mode, space.is_prev_window_open, space.PMV)
    # 目標PMVの計算（冷房時は上限、暖房時は下限PMVを目標値とする）
    pmv_set = space.pmv_lower_limit if space.now_air_conditioning_mode > 0 else space.pmv_upper_limit

    # 最終計算のための係数整備
    space.BRC = space.BRCnoncv
    space.BRM[sequence_number] = space.BRMnoncv
    # 通風なら通風量を設定
    if space.is_now_window_open == 1:
        temp = conca * conrowa * space.Vcrossvent / 3600.0
        space.BRM[sequence_number] += temp
        space.BRC += temp * Ta
    
    # OT計算用の係数補正
    space.BRMot, space.BRLot, space.BRCot, space.Xot, space.XLr, space.XC = convert_coefficient_for_operative_temperature(space, sequence_number)
    
    # 目標作用温度、代謝量、着衣量、風速の計算
    space.OTset, space.Met, space.Clo, space.Vel = calcOTset(space.now_air_conditioning_mode, space.is_radiative_heating, space.RH, pmv_set)

    # 仮の作用温度、熱負荷の計算
    space.OT, space.Lcs, space.Lrs = calc_Tr_Ls(space.now_air_conditioning_mode,
                                                    space.is_radiative_heating, space.BRCot, space.BRMot,
                                                    space.BRLot, 0, space.OTset)
    # 放射空調の過負荷状態をチェックする
    space.now_air_conditioning_mode = reset_SW(space.now_air_conditioning_mode, space.Lcs, space.Lrs, space.is_radiative_heating, space.radiative_heating_max_capacity)

    # 最終作用温度・熱負荷の再計算
    space.OT, space.Lcs, space.Lrs = calc_Tr_Ls(space.now_air_conditioning_mode,
                                                    space.is_radiative_heating, space.BRCot, space.BRMot,
                                                    space.BRLot, space.radiative_heating_max_capacity, space.OTset)
    # 室温を計算
    space.Tr = space.Xot * space.OT - space.XLr * space.Lrs - space.XC
    
    # 表面温度の計算
    Ts = get_surface_temperature(space.matWSR, space.matWSV, space.matWSC, space.matWSB, space.input_surfaces, space.Tr, space.Lrs)
    for i in range(space.Nsurf):
        space.input_surfaces[i].Ts = Ts[i]

    # 配列の準備
    fot = np.array([x.fot for x in space.input_surfaces])
    area = np.array([x.area for x in space.input_surfaces])
    Fmrt = np.array([x.Fmrt for x in space.input_surfaces])
    hic = np.array([x.hic for x in space.input_surfaces])
    hi = np.array([x.hi for x in space.input_surfaces])
    hir = np.array([x.hir for x in space.input_surfaces])
    RSsol = np.array([x.RSsol for x in space.input_surfaces])
    flr = np.array([x.hi for x in space.input_surfaces])

    # MRT、AST、平均放射温度の計算
    space.MRT = get_MRT(fot, Ts)
    space.AST = get_AST(area, Ts, space.Atotal)
    space.Tsx = get_Tsx(Fmrt, Ts)

    # 室内側等価温度の計算
    Tei = get_Tei(hic, hi, hir, RSsol, flr, area, space.Tr, space.Tsx, space.Lrs, space.Beta)

    # 室内表面熱流の計算
    Qc, Qr, Lr, RS, Qt, oldqi = \
        calc_qi(hic, area, hir, RSsol, flr, Ts, space.Tr, space.Tsx, space.Lrs, space.Beta)

    for i, surface in enumerate(space.input_surfaces):
        surface.Tei = Tei[i]
        surface.Qc = Qc[i]
        surface.Qr = Qr[i]
        surface.Lr = Lr[i]
        surface.RS = RS[i]
        surface.Qt = Qt[i]
        surface.oldqi = oldqi[i]

    # ======= 4.2 潜熱 =======

    # 室内湿度と潜熱負荷の計算
    calc_xr_Ll_residential(space, calc_time_interval, xo)

    # 家具の温度を計算
    if space.Capfun > 0.0:
        space.Tfun, space.Qfuns = calcTfun(
            Capfun=space.Capfun,
            oldTfun=space.oldTfun,
            Cfun=space.Cfun,
            Tr=space.Tr,
            Qsolfun=space.Qsolfun,
            calc_time_interval=calc_time_interval
        )

    space.xf, space.Qfunl = calcxf(
        Gf=space.Gf,
        oldxf=space.oldxf,
        Cx=space.Cx,
        xr=space.xr,
        calc_time_interval=calc_time_interval
    )

    # 年間熱負荷の積算
    # 助走計算以外の時だけ積算
    if is_actual_calc == True:
        calc_annual_heat_load(space, calc_time_interval)

    # PMVの計算
    space.PMV = calcPMV(space.Tr, space.MRT, space.RH, space.Vel, space.Met, space.Wme, space.Clo)

    # 当該時刻の空調状態、窓開閉状態を控える
    space.prev_air_conditioning_mode = space.now_air_conditioning_mode
    space.is_prev_window_open = space.is_now_window_open

    return 0

# MRTの計算
def get_MRT(fot, Ts):
    return np.sum(fot * Ts)

# ASTの計算
def get_AST(area, Ts, Atotal):
    return np.sum(area * Ts / Atotal)

# 平均放射温度の計算
def get_Tsx(Fmrt, Ts):
    return np.sum(Fmrt * Ts)

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

# 作用温度設定用係数への換算
def convert_coefficient_for_operative_temperature(space, sequence_number):
    Xot = 0.0
    XLr = 0.0
    XC = 0.0
    fot_WSR = 0.0
    fot_WSB = 0.0
    fot_WSC_WSV = 0.0
    for (matWSR, matWSB, matWSC, matWSV, surface) in zip(space.matWSR, space.matWSB, space.matWSC, space.matWSV, space.input_surfaces):
        fot_WSR += (surface.fot * matWSR)
        fot_WSB += surface.fot * matWSB
        fot_WSC_WSV += surface.fot * (matWSC + matWSV)

    Deno = space.kc + space.kr * fot_WSR
    Xot = 1.0 / Deno
    XLr = space.kr * fot_WSB / Deno
    XC = space.kr * fot_WSC_WSV / Deno
    BRMot = space.BRM[sequence_number] * Xot
    BRCot = space.BRC + space.BRM[sequence_number] * XC
    BRLot = space.BRL[sequence_number] + space.BRM[sequence_number] * XLr

    return BRMot, BRLot, BRCot, Xot, XLr, XC

# 室温・負荷計算の定数項BRCを計算する
def calc_BRC(space, Dtime, Ta, sequence_number):
    # 定数項の計算
    BRC = 0.0

    # 配列の準備
    area = np.array([x.area for x in space.input_surfaces])
    hic = np.array([x.hic for x in space.input_surfaces])
    RFT0 = np.array([x.RFT0 for x in space.input_surfaces])
    Teo = np.array([x.Teo for x in space.input_surfaces])
    RSsol = np.array([x.RSsol for x in space.input_surfaces])
    RFA0 = np.array([x.RFA0 for x in space.input_surfaces])
    
    # 行列CRX、WSCの計算
    matCRX, matWSC = calc_CRX_WSC(RFT0, Teo, RSsol, RFA0, space.matAX, sequence_number)
    space.matCRX = matCRX
    space.matWSC = matWSC
    
    # {BRC}の計算
    BRC += np.sum(matWSC * area * hic)

    # 外気流入風（換気＋すきま風）
    BRC += conca * conrowa * \
            (space.Ventset + space.Infset + space.LocalVentset) \
            * Ta / 3600.0

    # 室間換気流入風
    for room_vent in space.RoomtoRoomVent:
        BRC += conca * conrowa * room_vent.volume \
                * room_vent.oldTr / 3600.0

    # RM/Δt*oldTrの項
    BRC += space.Hcap / Dtime * space.oldTr

    # 家具からの熱取得の項
    if space.Capfun > 0.0:
        BRC += (space.Capfun / Dtime * space.oldTfun + space.Qsolfun) \
                / (space.Capfun / (Dtime * space.Cfun) + 1.)

    # Tsdの更新
    update_Tsd(space)

    # 行列CVL、WSVの計算
    matCVL, matWSV = calc_CVL_WSV(space.matAX, space.input_surfaces)

    space.matCVL= matCVL
    space.matWSV = matWSV
    
    # 畳み込み後の室内表面温度の計算
    BRC += np.sum(area * hic * matWSV)

    # 定数項への内部発熱の加算
    BRC += space.Hn

    return BRC

# 湿度・潜熱負荷計算の係数BRMXを計算する
def calc_BRMX_BRXC(Ventset, Infset, LocalVentset, Dtime, Gf,Cx, xo, volume, RoomtoRoomVent, oldxr, oldxf, Lin):

    # 外気の流入量
    Voin = get_Voin(Ventset, Infset, LocalVentset)

    # 湿気容量の項
    temp = get_temp(Gf=Gf, Cx=Cx, Dtime=Dtime)

    BRMX = get_BRMX(
        temp=temp,
        Dtime=Dtime, 
        volume=volume,
        Voin=Voin,
        RoomtoRoomVent=RoomtoRoomVent
    )

    BRXC = get_BRXC(
        temp=temp,
        Dtime=Dtime,
        volume=volume,
        Voin=Voin,
        xo=xo,
        oldxr=oldxr,
        oldxf=oldxf,
        Lin=Lin,
        RoomtoRoomVent=RoomtoRoomVent
    )
    
    return BRMX, BRXC

# 外気の流入量
def get_Voin(Ventset, Infset, LocalVentset):
    return (Ventset + Infset + LocalVentset) / 3600.

def get_BRMX(temp, Dtime, volume, Voin, RoomtoRoomVent):

    # 配列準備
    next_volume = np.array([x.volume for x in RoomtoRoomVent])

    BRMX = (conrowa * (volume / Dtime + Voin)
           + temp
           + np.sum(conrowa * next_volume / 3600.0))

    return BRMX

def get_BRXC(temp, Dtime, volume, Voin, xo, oldxr, oldxf, Lin, RoomtoRoomVent):

    # 配列準備
    next_volume = np.array([x.volume for x in RoomtoRoomVent])
    next_oldxr = np.array([x.oldxr for x in RoomtoRoomVent])

    BRXC = conrowa * (volume / Dtime * oldxr + Voin * xo) \
           + temp * oldxf \
           + Lin \
           + np.sum([conrowa * next_volume * next_oldxr / 3600.0])

    return BRXC

# 湿気容量の項
def get_temp(Gf, Cx, Dtime):
    temp = Gf * Cx / (Gf + Dtime * Cx)
    return temp

# 室温・負荷計算の係数BRMとBRLを計算する
def calc_BRM_BRL(space, Dtime):
    # BRM・BRLの初期化
    BRM = space.Hcap / Dtime
    BRL = space.Beta
    # BRLの計算
    for (matWSR, matWSB, surface) in zip(space.matWSR, space.matWSB, space.input_surfaces):
        # 室内対流熱伝達率×面積[W/K]
        AF0 = surface.area * surface.hic
        # hc×A×(1-WSR)の積算
        BRM += AF0 * (1.0 - matWSR)
        # BRLの計算
        BRL += AF0 * matWSB

    # 外気導入項の計算
    BRM += conca * conrowa * (space.Ventset + space.Infset + space.LocalVentset) / 3600.0
    # 室間換気
    for room_vent in space.RoomtoRoomVent:
        BRM += conca * conrowa * room_vent.volume / 3600.0
    
    # 家具からの熱取得
    if space.Capfun > 0.0:
        BRM += 1. / (Dtime / space.Capfun + 1. / space.Cfun)

    return BRM, BRL

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


# 湿度・潜熱負荷の計算ルーチン（住宅）
def calc_xr_Ll_residential(space, calc_time_interval, xo):

    # BRMX, BRXCの計算 式(17),(18)
    BRMX_pre, BRXC_pre = calc_BRMX_BRXC(
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

    # 空調の熱交換部飽和絶対湿度の計算
    a16.calcVac_xeout(space, space.now_air_conditioning_mode)

    # バイパスファクターBF 式(114)
    BF = a16.get_BF()

    # 空調機除湿の項 式(20)より
    RhoVac = get_RhoVac(space.Vac, BF)

    # 室絶対湿度[kg/kg(DA)]の計算
    BRMX_base = BRMX_pre + RhoVac
    BRXC_base = BRXC_pre + RhoVac * space.xeout

    # 室絶対湿度の計算 式(16)
    xr_base = get_xr(BRXC_base, BRMX_base)

    # 補正前の加湿量の計算 [ks/s] 式(20)
    Ghum_base = get_Ghum(RhoVac, space.xeout, xr_base)

    # 除湿量が負値になった場合にはルームエアコン風量V_(ac,n)をゼロとして再度室湿度を計算する
    if Ghum_base > 0.0:
        Ghum = 0.0
        BRMX = BRMX_pre
        BRXC = BRXC_pre

        # 空調機除湿の項の再計算（除湿なしで計算）
        space.Va = 0.0

        # 室絶対湿度の計算 式(16)
        xr = get_xr(BRXC_pre, BRMX_pre)
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

    # 計算結果の保存
    space.BRMX = BRMX
    space.BRXC = BRXC
    space.xr = xr
    space.Lcl = Lcl
    space.Lrl = Lrl
    space.Ghum = Ghum
    space.RH = RH


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


# 室絶対湿度の計算 式(16)
def get_xr(BRXC_i, BRMX_i):
    return BRXC_i / BRMX_i


# i室のn時点における除湿量 [ks/s] 式(20)
def get_Ghum(RhoVac, xeout, xr):
    """
    :param RhoVac:
    :param xeout:
    :param xr: 室空気の絶対湿度
    :return: i室のn時点における除湿量 [ks/s]
    """
    return RhoVac * (xeout - xr)


# 湿度・潜熱負荷の計算ルーチン（非住宅）
def calc_xr_Ll_non_residential(space):
    # 自然湿度の計算
    # 室絶対湿度[kg/kg(DA)]の計算
    space.xr = space.BRXC / space.BRMX
    # 相対湿度の計算
    space.RH = rhtx(space.Tr, space.xr)
    # 潜熱計算運転状態
    space.nowACx = 0
    # 潜熱負荷の初期化
    space.Lcl = 0.0
    # 上限湿度を超える場合は除湿
    if space.is_upper_humidity_limit_set and space.RH > space.relative_humidity_upper_limit:
        space.nowACx = -1
        RH_set = space.relative_humidity_upper_limit
        
    # 下限湿度を下回る場合は加湿
    elif space.is_lower_humidity_limit_set and space.RH < space.relative_humidity_lower_limit:
        space.nowACx = 1
        RH_set = space.relative_humidity_lower_limit

    # 設定絶対湿度の計算（潜熱運転のときだけ）
    if space.nowACx != 0:
        space.xr = xtrh(space.Tr, RH_set)
        space.RH = RH_set
        space.Lcl = - conra * (space.BRXC - space.BRMX * space.xr)

# 家具の温度を計算する
def calcTfun(Capfun, oldTfun, Cfun, Tr, Qsolfun, calc_time_interval):
    """

    :param Capfun: i室の家具の熱容量（付録14．による） [J/K]
    :param oldTfun: i室の家具の15分前の温度 [℃]
    :param Cfun: i室の家具と室空気間の熱コンダクタンス（付録14．による）
    :param Tr:
    :param Qsolfun: i室のn時点における家具の日射吸収熱量 [W]
    :param calc_time_interval:
    :return: i室の家具の温度 [℃]
    """
    Tfun = get_Tfun(calc_time_interval, Capfun, oldTfun, Cfun, Tr, Qsolfun)
    Qfuns = get_Qfuns(Cfun, Tr, Tfun)

    return Tfun, Qfuns


def get_Qfuns(Cfun, Tr, Tfun):
    """

    :param Cfun: i室の家具と室空気間の熱コンダクタンス（付録14．による）
    :param Tr:
    :param Tfun: i室の家具の温度 [℃]
    :return:
    """
    return Cfun * (Tr - Tfun)


# 家具の温度 式(15)
def get_Tfun(calc_time_interval, Capfun, oldTfun, Cfun, Tr, Qsolfun):
    """

    :param calc_time_interval:
    :param Capfun: i室の家具の熱容量（付録14．による） [J/K]
    :param oldTfun: i室の家具の15分前の温度 [℃]
    :param Cfun: i室の家具と室空気間の熱コンダクタンス（付録14．による）
    :param Tr:
    :param Qsolfun: i室のn時点における家具の日射吸収熱量 [W]
    :return:
    """
    return (((Capfun / calc_time_interval * oldTfun
                   + Cfun * Tr + Qsolfun)
                  / (Capfun / calc_time_interval + Cfun)))


# 家具類の湿度を計算する
def calcxf(Gf, oldxf, Cx, xr, calc_time_interval):
    xf = get_xf(calc_time_interval, Gf, oldxf, Cx, xr)
    Qfunl = get_Qfunl(Cx, xr, xf)

    return xf, Qfunl


def get_Qfunl(Cx, xr, xf):
    return Cx * (xr - xf)


def get_xf(calc_time_interval, Gf, oldxf, Cx, xr):
    return (Gf / calc_time_interval * oldxf + Cx * xr) / (Gf / calc_time_interval + Cx)