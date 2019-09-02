from inclined_surface_solar_radiation import calc_slope_sol
from NextVent import update_oldstate
from rear_surface_equivalent_temperature import calcTeo
from common import get_nday, conca, conrowa, conra
from blowing_condition_rac import calcVac_xeout
from indoor_radiative_heat_transfer import distribution_transmitted_solar_radiation
from calculation_surface_temperature import calc_surface_temperature, calc_Tei, convolution, \
    calc_CRX_WSC, calc_Tei, calc_CVL_WSV, calc_qi
from Win_ACselect import reset_SW, mode_select
from PMV import calcPMV
from Psychrometrics import xtrh, rhtx
from set_point_temperature import calcOTset, calc_clothing
from apdx6_direction_cos_incident_angle import calc_cos_incident_angle
from local_vent_schedule import create_hourly_local_vent_schedules
from internal_heat_schedule import create_hourly_internal_heat_schedules
from lighting_schedule import create_hourly_lighting_schedules
from resident_schedule import create_hourly_resident_schedules
from Win_ACselect import create_hourly_air_conditioning_schedules

# 室温、熱負荷の計算
def calcHload(space, is_actual_calc, calc_time_interval, spaces, dtmNow, Ta: float, xo: float, sequence_number: int):
    # 室間換気の風上室温をアップデート
    for roomvent in space.RoomtoRoomVent:
        windward_roomname = roomvent.windward_roomname
        update_oldstate(roomvent, spaces[windward_roomname].oldTr, spaces[windward_roomname].oldxr)

    # 裏面温度の計算
    for surface in space.input_surfaces:
        calcTeo(surface, Ta, space.oldTr, spaces, sequence_number)

    # 当該時刻の局所換気量の読み込み
    create_hourly_local_vent_schedules(space, dtmNow)
    # 当該時刻の機器・調理発熱の読み込み
    create_hourly_internal_heat_schedules(space, dtmNow)
    # 当該時刻の照明発熱の読み込み
    create_hourly_lighting_schedules(space, dtmNow)
    # 当該時刻の人体発熱の読み込み
    create_hourly_resident_schedules(space, dtmNow)
    # 内部発熱[W]
    space.Hn = space.heat_generation_appliances + space.heat_generation_lighting + space.Humans + space.heat_generation_cooking
    # 内部発湿[kg/s]
    space.Lin = space.vapor_generation_cooking / 1000.0 / 3600.0 + space.Humanl

    # 当該時刻の空調スケジュールの読み込み
    create_hourly_air_conditioning_schedules(space, dtmNow)

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
    space.BRM, space.BRL = calc_BRM_BRL(space, calc_time_interval)

    # 室温・熱負荷計算のための定数項BRCの計算
    space.BRC = calc_BRC(space, calc_time_interval, Ta, sequence_number)

    # 窓開閉、空調発停判定のための自然室温計算
    # 通風なしでの係数を控えておく
    space.BRMnoncv = space.BRM
    space.BRCnoncv = space.BRC
    # 通風計算用に係数を補正（前時刻が通風状態の場合は非空調作用温度を通風状態で計算する）
    if space.is_now_window_open == True:
        temp = conca * conrowa * space.Vcrossvent / 3600.0
        space.BRM += temp
        space.BRC += temp * Ta

    # OT計算用の係数補正
    space.BRMot, space.BRLot, space.BRCot, space.Xot, space.XLr, space.XC = convert_coefficient_for_operative_temperature(space)
    
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
    space.BRM = space.BRMnoncv
    # 通風なら通風量を設定
    if space.is_now_window_open == 1:
        temp = conca * conrowa * space.Vcrossvent / 3600.0
        space.BRM += temp
        space.BRC += temp * Ta
    
    # OT計算用の係数補正
    space.BRMot, space.BRLot, space.BRCot, space.Xot, space.XLr, space.XC = convert_coefficient_for_operative_temperature(space)
    
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
    calc_surface_temperature(space)
    # MRT、AST、平均放射温度の計算
    calc_MRT_AST_Tsx(space)

    # 室内側等価温度・熱流の計算
    for surface in space.input_surfaces:
        # 室内側等価温度の計算
        surface.Tei = calc_Tei(surface, space.Tr, space.Tsx, space.Lrs, space.Beta)
        # 室内表面熱流の計算
        calc_qi(surface, space.Tr, space.Tsx, space.Lrs, space.Beta)

    # ここから潜熱の計算
    space.BRMX, space.BRXC = calc_BRMX_BRXC(space, calc_time_interval, xo)
    # 室内湿度と潜熱負荷の計算
    calc_xr_Ll_residential(space)

    # 家具の温度を計算
    space.Tfun = calcTfun(space, calc_time_interval)
    space.xf = calcxf(space, calc_time_interval)

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

# 表面温度、MRT、AST、平均放射温度の計算
def calc_MRT_AST_Tsx(space):
    space.MRT = 0.0
    space.AST = 0.0
    space.Tsx = 0.0
    for surface in space.input_surfaces:
        # 人体に対する放射温度：MRT、面積荷重平均温度：AST、平均放射温度：Tsx
        space.MRT += surface.fot * surface.Ts
        space.AST += surface.area * surface.Ts / space.Atotal
        space.Tsx += surface.Fmrt * surface.Ts

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
def convert_coefficient_for_operative_temperature(space):
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
    BRMot = space.BRM * Xot
    BRCot = space.BRC + space.BRM * XC
    BRLot = space.BRL + space.BRM * XLr

    return BRMot, BRLot, BRCot, Xot, XLr, XC

# 室温・負荷計算の定数項BRCを計算する
def calc_BRC(space, Dtime, Ta, sequence_number):
    # 定数項の計算
    BRC = 0.0
    
    # 行列CRX、WSCの計算
    calc_CRX_WSC(space, sequence_number)
    
    # {BRC}の計算
    for (matWSC, surface) in zip(space.matWSC, space.input_surfaces):
        BRC += matWSC * surface.area * surface.hic

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

    # 行列CVL、WSVの計算
    calc_CVL_WSV(space)
    
    # 畳み込み後の室内表面温度の計算
    for (matWSV, surface) in zip(space.matWSV, space.input_surfaces):
        BRC += surface.area * surface.hic * matWSV

    # 定数項への内部発熱の加算
    BRC += space.Hn

    return BRC

# 湿度・潜熱負荷計算の係数BRMXを計算する
def calc_BRMX_BRXC(space, Dtime, xo):
    # 外気の流入量
    Voin = (space.Ventset + space.Infset + space.LocalVentset) / 3600.
    # 湿気容量の項
    temp = space.Gf * space.Cx / (space.Gf + Dtime * space.Cx)
    BRMX = conrowa * (space.volume / Dtime + Voin) + temp
    BRXC = conrowa * (space.volume / Dtime * space.oldxr + Voin * xo) \
            + temp * space.oldxf + space.Lin
    
    # 室間換気流入風
    for room_vent in space.RoomtoRoomVent:
        BRMX += conrowa * room_vent.volume / 3600.0
        BRXC += conrowa * room_vent.volume * room_vent.oldxr / 3600.0
    
    return BRMX, BRXC

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
def calc_xr_Ll_residential(space):
    # 空調の熱交換部飽和絶対湿度の計算
    calcVac_xeout(space, space.now_air_conditioning_mode)
    # 空調機除湿の項
    RhoVac = conrowa * space.Vac * (1.0 - space.bypass_factor_rac)
    space.BRMX += RhoVac
    space.BRXC += RhoVac * space.xeout
    # 室絶対湿度[kg/kg(DA)]の計算
    space.xr = space.BRXC / space.BRMX
    # 加湿量の計算
    space.Ghum = RhoVac * (space.xeout - space.xr)
    if space.Ghum > 0.0:
        space.Ghum = 0.0
        # 空調機除湿の項の再計算（除湿なしで計算）
        space.BRMX -= RhoVac
        space.BRXC -= RhoVac * space.xeout
        space.Va = 0.0
        # 室絶対湿度の計算
        space.xr = space.BRXC / space.BRMX
    # 潜熱負荷の計算
    space.Lcl = space.Ghum * conra
    # 当面は放射空調の潜熱は0
    space.Lrl = 0.0
    # 室相対湿度の計算
    space.RH = rhtx(space.Tr, space.xr)

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
def calcTfun(space, calc_time_interval):
    if space.Capfun > 0.0:
        space.Tfun = ((space.Capfun / calc_time_interval * space.oldTfun \
                + space.Cfun * space.Tr + space.Qsolfun) \
                / (space.Capfun / calc_time_interval + space.Cfun))
        space.Qfuns = space.Cfun * (space.Tr - space.Tfun)
    # if self.name == "主たる居室":
    #     print(self.name, self.oldTfun, self.Tfun, self.Capfun, self.Cfun, self.Qsolfun)
    return space.Tfun

# 家具類の湿度を計算する
def calcxf(space, calc_time_interval):
    space.xf = (space.Gf / calc_time_interval * space.oldxf + space.Cx * space.xr) / (space.Gf / calc_time_interval + space.Cx)
    space.Qfunl = space.Cx * (space.xr - space.xf)
    # if self.name == "主たる居室":
    #     print(self.name, self.oldTfun, self.Tfun, self.Capfun, self.Cfun, self.Qsolfun)
    return space.xf