import numpy as np
from typing import List
import Weather
from Weather import enmWeatherComponent, Solpos, WeaData
import math
# import Surface
from Surface import Surface, create_surface, boundary_comp, calc_slope_sol, get_shading_area_ratio, calc_Qgt, calcTeo, calc_RSsol, calc_qi, calc_Tei, convolution
import NextVent
from NextVent import NextVent, update_oldstate
from Psychrometrics import Pws, x, xtrh, rhtx
from common import conca, conrowa, Sgm, conra, \
    funiture_sensible_capacity, funiture_latent_capacity, bypass_factor_rac, get_nday
from PMV import calcPMV, calcOTset, get_OT
from Win_ACselect import reset_SW, mode_select
import datetime
from Gdata import FlgOrig

# # 室温・熱負荷を計算するクラス

# ## １）室内部位に関連するクラス

# 室内部位に関する情報を保持します。
# 
# - is_skin:      外皮フラグ, 外皮の場合True
# - boundary:  方位・隣室名, string
# - unsteady:  非定常フラグ, 非定常壁体の場合True
# - name:      壁体・開口部名称, string
# - area:      面積, m2
# - sunbreak:  ひさし名称, string
# - flr:       放射暖房吸収比率, －
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

# 空間に関する情報の保持
class Space:
    FsolFlr = 0.5  # 床の日射吸収比率

    # 初期化
    def __init__(self, Gdata, d_room, weather):
        """
        :param Gdata:
        :param ExsrfMng:
        :param SunbrkMng:
        :param roomname: 室用途（主たる居室、その他居室、非居室）
        :param HeatCcap:
        :param HeatRcap:
        :param CoolCcap:
        :param Vol:
        :param Fnt:
        :param Vent:
        :param Inf:
        :param CrossVentRoom:
        :param is_radiative_heating:
        :param Beta:
        :param RoomtoRoomVents:
        :param input_surfaces:
        """
        self.name = d_room['name']                  # 室名称
        if Gdata.is_residential:
            self.room_type = d_room['room_type']      # 室用途（1:主たる居室、2:その他居室、3:非居室）
        self.AnnualLoadcCs = 0.0                  # 年間顕熱冷房熱負荷（主暖房）
        self.AnnualLoadcHs = 0.0                  # 年間顕熱暖房熱負荷（対流成分）
        self.AnnualLoadcCl = 0.0                  # 年間潜熱冷房熱負荷（対流成分）
        self.AnnualLoadcHl = 0.0                  # 年間潜熱暖房熱負荷（対流成分）
        self.AnnualLoadrCs = 0.0                  # 年間顕熱冷房熱負荷（放射成分）
        self.AnnualLoadrHs = 0.0                  # 年間顕熱暖房熱負荷（放射成分）
        self.AnnualLoadrCl = 0.0                  # 年間潜熱冷房熱負荷（放射成分）
        self.AnnualLoadrHl = 0.0                  # 年間潜熱暖房熱負荷（放射成分）
        self.Lrs = self.Lrl = self.Lcl = self.Lcl = 0.0
        self.Tr = 15.0                              # 室温の初期化
        self.oldTr = 15.0                         # 前時刻の室温の初期化
        self.Tfun = 15.0                            # 家具の温度[℃]
        self.oldTfun = 15.0                       # 前時刻の家具の温度[℃]
        self.rsolfun = 0.5                        # 透過日射の内家具が吸収する割合[－]
        # self.rsolfun = 0.0
        self.kc = 0.5                             # 人体表面の熱伝達率の対流成分比率
        self.kr = 0.5                             # 人体表面の熱伝達率の放射成分比率
        self.demAC = 0                              # 当該時刻の空調需要（0：なし、1：あり）
        self.preAC = 0                              # 前時刻の空調運転状態（0：停止、正：暖房、負：冷房）
        self.preWin = 0                             # 前時刻の窓状態（0：閉鎖、1：開放）
        self.nowAC = 0                              # 当該時刻の空調運転状態（0：なし、正：暖房、負：冷房）
        self.nowWin = 0                             # 当該時刻の窓状態（0：閉鎖、1：開放）
        # PMVの計算条件
        self.Met = 1.0                              # 代謝量[Met]
        self.Wme = 0.0                              # 外部仕事[Met]
        self.Vel = 0.1                              # 相対風速[m/s]
        self.Clo = 1.0                              # 着衣量[Clo]
        self.OTset = 0.0                            # 設定作用温度[℃]
        self.is_radiative_heating = False
        self.radiative_heating_max_capacity = 0.0
        if Gdata.is_residential:
            heating_equipment_read(self, d_room['heating_equipment'])
                                                    # 暖房設備仕様の読み込み
            cooling_equipment_read(self, d_room['cooling_equipment'])
        
        self.volume = d_room['volume']            # 室気積[m3]
        self.Ga = self.volume * conrowa         # 室空気の質量[kg]
        self.Capfun = self.volume * funiture_sensible_capacity * 1000.
                                                    # 家具熱容量[J/K]
        # self.Capfun = 0.0
        self.Cfun = 0.00022 * self.Capfun       # 家具と空気間の熱コンダクタンス[W/K]
        self.Gf = funiture_latent_capacity * self.volume
                                                    # 家具類の湿気容量[kg]
        self.Cx = 0.0018 * self.Gf              # 室空気と家具類間の湿気コンダクタンス[kg/(s･kg/kg(DA))]
        self.xr = xtrh(20.0, 40.0)                  # 室の絶対湿度[kg/kg(DA)]
        self.oldxr = self.xr                      # 室内絶対湿度の初期値
        self.xf = self.xr                           # 家具類の絶対湿度
        self.oldxf = self.xr                      # 家具類の絶対湿度の初期値
        self.bypass_factor_rac = bypass_factor_rac               # バイパスファクター
        self.xeout = 0.0                          # エアコン熱交換部の飽和絶対湿度[kg/kg(DA)]
        self.Vac = 0.0                              # エアコンの風量[m3/s]
        self.RH = 50.0                              # 室相対湿度[%]
        if Gdata.is_residential:
            self.Vcrossvent = self.volume * d_room['natural_vent_time']
                                                    # 窓開放時通風量
        # 室空気の熱容量
        self.Hcap = self.volume * conrowa * conca
        # print(self.Hcap)
        self.Vent = d_room['vent']                #計画換気量
        self.Inf = 0.0                            #すきま風量（暫定値）
        self.Beta = 0.0                           # 放射暖房対流比率

        # スケジュールの読み込み
        read_schedules(self, d_room, Gdata)
        
        # 内部発熱合計
        self.Hn = 0.0

        # 室透過日射熱取得の初期化
        # self.Qgt = [0.0 for j in range(8760 * 3600 / int(Gdata.DTime)]

        # 室間換気量クラスの構築
        self.RoomtoRoomVent = []
        # prevroomname = ''
        # winter_vent = 0.0
        # inter_vent = 0.0
        # summer_vent = 0.0
        if Gdata.is_residential:
            for room_vent in d_room['next_vent']:
                self.RoomtoRoomVent.append(NextVent(room_vent['upstream_room_type'], room_vent['volume']))
        self.Nsurf = 0  # 部位の数
        self.input_surfaces = []

        # 部位の読み込み
        for d_surface in d_room['boundaries']:
            # print(d_surface['name'])
            self.input_surfaces.append(Surface(d = d_surface, Gdata = Gdata))
        
        # 透過日射熱取得の計算（部位を集約するので最初に8760時間分計算しておく）
        self.Qgt = summarize_transparent_solar_radiation(self.input_surfaces, Gdata, weather)
        
        # 部位の集約
        self.input_surfaces = summarize_building_part(self.input_surfaces)
            
        # 部位の人体に対する形態係数を計算
        calc_form_factor_for_human_body(self)

        # 部位の面数
        self.Nsurf = len(self.input_surfaces)

        # 各種合計面積の計算
        self.Atotal = 0.0
        self.TotalAF = 0.0

        # print('合計面積1=', self.Atotal)
        # 合計面積の計算
        for surface in self.input_surfaces:
            self.Atotal += surface.area

            # 合計床面積の計算
            if surface.is_solar_absorbed_inside == True:
                self.TotalAF += surface.area
        
        # ルームエアコンの仕様の設定
        set_rac_spec(self)

        # 放射暖房の発熱部位の設定（とりあえず床発熱）
        if Gdata.is_residential:
            if self.is_radiative_heating:
                for surface in self.input_surfaces:
                    if surface.is_solar_absorbed_inside:
                        surface.flr = surface.area / self.TotalAF

        # 微小点に対する室内部位の形態係数の計算（永田先生の方法）
        calc_form_factor_of_microbodies(self.name, self.input_surfaces)
        
        #　室内表面対流・放射熱伝達率の計算
        calc_surface_heat_transfer_coefficient(self.input_surfaces)

        # 平均放射温度計算時の各部位表面温度の重み計算
        calc_mrt_weight(self.input_surfaces)

        # 日射吸収比率の計算
        self.rsolfun = calc_absorption_ratio_of_transmitted_solar_radiation(self.name, self.TotalAF, self.rsolfun, self.input_surfaces)

        # 室内表面熱収支計算のための行列作成
        make_matrix_for_surface_heat_balance(self)

    # 室温、熱負荷の計算
    def calcHload(self, Gdata, spaces, dtmNow, defSolpos, Ta, xo, Idn, Isky, RN, annual_average_temperature):
        # 室間換気の風上室温をアップデート
        for roomvent in self.RoomtoRoomVent:
            windward_roomname = roomvent.windward_roomname
            update_oldstate(roomvent, spaces[windward_roomname].oldTr, spaces[windward_roomname].oldxr)

        # 外皮の傾斜面日射量の計算
        for surface in self.input_surfaces:
            if surface.is_sun_striked_outside:
                surface.Id, surface.Isky, surface.Ir, surface.Iw = calc_slope_sol(surface, defSolpos, Idn, Isky)

        # 相当外気温度の計算
        for surface in self.input_surfaces:
            calcTeo(surface, Ta, RN, self.oldTr, annual_average_temperature, spaces)

        # 当該時刻の内部発熱・発湿・局所換気量の読み込み（顕熱はすべて対流成分とする）
        create_hourly_schedules(self, dtmNow, Gdata.is_residential)

        # 室内表面の吸収日射量
        sequence_number = int((get_nday(dtmNow.month, dtmNow.day) - 1) * 24 * 4 + dtmNow.hour * 4 + float(dtmNow.minute) / 60.0 * 3600 / Gdata.DTime)
        for surface in self.input_surfaces:
            surface.RSsol = calc_RSsol(surface, self.Qgt[sequence_number])
        # 家具の吸収日射量
        self.Qsolfun = self.Qgt[sequence_number] * self.rsolfun

        # 流入外気風量の計算
        # 計画換気・すきま風量
        self.Ventset = self.Vent

        # すきま風量未実装につき、とりあえず０とする
        self.Infset = 0.0

        # 空調設定温度の取得
        # 空調需要の設定
        if self.number_of_people > 0:
            self.demAC = 1
        else:
            self.demAC = 0
        
        # 自然室温計算時窓開閉条件の設定
        # 空調需要がなければ窓閉鎖、空調需要がある場合は前時刻の窓開閉状態
        self.nowWin = 0
        if self.demAC == 1:
            self.nowWin = self.preWin

        # 室温・熱負荷計算のための係数BRM、BRLの計算
        self.BRM, self.BRL = calc_BRM_BRL(self, Gdata.DTime)

        # 室温・熱負荷計算のための定数項BRCの計算
        self.BRC = calc_BRC(self, Gdata.DTime, Ta)

        # 窓開閉、空調発停判定のための自然室温計算
        # 通風なしでの係数を控えておく
        self.BRMnoncv = self.BRM
        self.BRCnoncv = self.BRC
        # 通風計算用に係数を補正（前時刻が通風状態の場合は非空調作用温度を通府状態で計算する）
        if self.nowWin == 1:
            temp = conca * conrowa * self.Vcrossvent / 3600.0
            self.BRM += temp
            self.BRC += temp * Ta

        # OT計算用の係数補正
        self.BRMot, self.BRLot, self.BRCot, self.Xot, self.XLr, self.XC = convert_coefficient_for_operative_temperature(self)
        
        # 自然作用温度の計算（住宅用）
        if Gdata.is_residential:
            # 自然作用温度の計算
            self.OT, self.Lcs, self.Lrs = calc_Tr_Ls(0, self.is_radiative_heating, self.BRCot, self.BRMot,
                                                        self.BRLot, 0, 0.0)
            # 窓開閉と空調発停の判定をする
            self.nowWin, self.nowAC = mode_select(self.demAC, self.preAC, self.preWin, self.OT)
            # 最終計算のための係数整備
            self.BRC = self.BRCnoncv
            self.BRM = self.BRMnoncv
            # 通風なら通風量を設定
            if self.nowWin == 1:
                temp = conca * conrowa * self.Vcrossvent / 3600.0
                self.BRM += temp
                self.BRC += temp * Ta
            
            # OT計算用の係数補正
            self.BRMot, self.BRLot, self.BRCot, self.Xot, self.XLr, self.XC = convert_coefficient_for_operative_temperature(self)
            
            # 目標作用温度、代謝量、着衣量、風速の計算
            self.OTset, self.Met, self.Clo, self.Vel = calcOTset(self.nowAC, self.is_radiative_heating, self.RH)

            # 仮の作用温度、熱負荷の計算
            self.OT, self.Lcs, self.Lrs = calc_Tr_Ls(self.nowAC,
                                                            self.is_radiative_heating, self.BRCot, self.BRMot,
                                                            self.BRLot, 0, self.OTset)

            # 放射空調の過負荷状態をチェックする
            self.finalAC = reset_SW(self.nowAC, self.Lcs, self.Lrs, self.is_radiative_heating, self.radiative_heating_max_capacity)

            # 最終作用温度・熱負荷の再計算
            self.OT, self.Lcs, self.Lrs = calc_Tr_Ls(self.finalAC,
                                                            self.is_radiative_heating, self.BRCot, self.BRMot,
                                                            self.BRLot, self.radiative_heating_max_capacity, self.OTset)
            # 室温を計算
            self.Tr = self.Xot * self.OT - self.XLr * self.Lrs - self.XC
        # 自然室温の計算（非住宅用）
        else:
            # 自然室温の計算
            self.Tr, self.Lcs, self.Lrs = calc_Tr_Ls(0, self.is_radiative_heating, self.BRC, self.BRM,
                                                        self.BRL, 0, 0.0)
            # 空調停止で初期化
            self.finalAC = 0
            # 窓閉鎖
            self.nowWin = 0
            # 設定温度
            temp_set = 0.0
            # 上限温度を超える場合は冷房
            if self.is_upper_temp_limit_set and self.Tr > self.temperature_upper_limit:
                self.finalAC = -1
                temp_set = self.temperature_upper_limit
            # 下限温度を下回る場合は暖房
            elif self.is_lower_temp_limit_set and self.Tr < self.temperature_lower_limit:
                self.finalAC = 1
                temp_set = self.temperature_lower_limit
            # print("item=", item, "Tr=", self.Tr, "finalAC=", self.finalAC, "temp_set=", temp_set, \
            #     self.is_upper_temp_limit_set[item], self.temperature_upper_limit[item])
            # 室温、熱負荷の計算
            self.Tr, self.Lcs, self.Lrs = calc_Tr_Ls(self.finalAC, self.is_radiative_heating, self.BRC, self.BRM, \
                self.BRL, 0, temp_set)

        # 表面温度、MRT、AST、平均放射温度の計算
        calc_surface_temperature_MRT_AST(self)
        
        # 非住宅の場合の作用温度を計算する
        self.OT = self.kc * self.Tr + self.kr * self.MRT

        # 室内側等価温度・熱流の計算
        for surface in self.input_surfaces:
            # 室内側等価温度の計算
            surface.Tei = calc_Tei(surface, self.Tr, self.Tsx, self.Lrs, self.Beta)
            # 室内表面熱流の計算
            calc_qi(surface, self.Tr, self.Tsx, self.Lrs, self.Beta)

        # ここから潜熱の計算
        self.BRMX, self.BRXC = calc_BRMX_BRXC(self, Gdata.DTime, xo)
        
        # 住宅の場合
        if Gdata.is_residential:
            calc_xr_Ll_residential(self)
        # 非住宅の場合
        else:
            calc_xr_Ll_non_residential(self)

        # 家具の温度を計算
        self.Tfun = calcTfun(self, Gdata)
        self.xf = calcxf(self, Gdata)

        # 年間熱負荷の積算
        # 助走計算以外の時だけ積算
        if FlgOrig(Gdata, dtmNow) == True:
            calc_annual_heat_load(self, Gdata.DTime)

        # PMVの計算
        self.PMV = calcPMV(self.Tr, self.MRT, self.RH, self.Vel, self.Met, self.Wme, self.Clo)

        # 当該時刻の空調状態、窓開閉状態を控える
        self.preAC = self.nowAC
        self.preWin = self.nowWin

        return 0

# 室内表面熱収支計算のための行列作成
def make_matrix_for_surface_heat_balance(space):
    # 行列の準備と初期化
    # [AX]
    space.matAXd = [[0.0 for i in range(space.Nsurf)] for j in range(space.Nsurf)]
    # {FIA}
    space.matFIA = [0.0 for j in range(space.Nsurf)]
    # {CRX}
    space.matCRX = [0.0 for j in range(space.Nsurf)]
    # {CVL}
    space.matCVL = [0.0 for j in range(space.Nsurf)]
    # {FLB}
    space.matFLB = [0.0 for j in range(space.Nsurf)]
    # {WSC}
    space.matWSC = [0.0 for j in range(space.Nsurf)]
    # {WSV}
    space.matWSV = [0.0 for j in range(space.Nsurf)]

    i = 0
    for surface in space.input_surfaces:
        # matFIAの作成
        space.matFIA[i] = surface.RFA0 * surface.hic
        # FLB=φA0×flr×(1-Beta)
        space.matFLB[i] = surface.RFA0 * surface.flr * (1. - space.Beta) / surface.area

        # 放射計算のマトリックス作成
        j = 0
        for nxtsurface in space.input_surfaces:
            # 対角要素
            if i == j:
                space.matAXd[i][j] = 1. + surface.RFA0 * surface.hi \
                                        - surface.RFA0 * surface.hir * nxtsurface.Fmrt
            # 対角要素以外
            else:
                space.matAXd[i][j] = - surface.RFA0 * surface.hir * nxtsurface.Fmrt
            j += 1
        # print('放射計算マトリックス作成完了')
        i += 1

    # 逆行列の計算
    space.matAX = np.linalg.inv(space.matAXd)
    # {WSR}の計算
    space.matWSR = np.dot(space.matAX, space.matFIA)
    # {WSB}の計算
    space.matWSB = np.dot(space.matAX, space.matFLB)

# 表面温度、MRT、AST、平均放射温度の計算
def calc_surface_temperature_MRT_AST(space):
    # 表面温度の計算
    for (matWSR, matWSV, matWSC, matWSB, surface) in zip(space.matWSR, space.matWSV, space.matWSC, space.matWSB, space.input_surfaces):
        surface.Ts = matWSR * space.Tr + matWSC + matWSV + matWSB * space.Lrs

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
def calc_BRC(space, Dtime, Ta):
    # 定数項の計算
    BRC = 0.0
    # {WSC}、{CRX}の初期化
    space.matWSC = [0.0 for j in range(space.Nsurf)]
    space.matCRX = [0.0 for j in range(space.Nsurf)]

    # {CRX}の作成
    i = 0
    for surface in space.input_surfaces:
        space.matCRX[i] = surface.RFT0 * surface.Teo \
                                + surface.RSsol * surface.RFA0
        i += 1

    # {WSC}=[XA]*{CRX}
    space.matWSC = np.dot(space.matAX, space.matCRX)
    
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

    # {WSV}、{CVL}の初期化
    space.matWSV = [0.0 for j in range(space.Nsurf)]
    space.matCVL = [0.0 for j in range(space.Nsurf)]

    # 畳み込み演算
    i = 0
    for surface in space.input_surfaces:
        space.matCVL[i] = convolution(surface)
        i += 1

    # {WSV}=[XA]*{CVL}
    space.matWSV = np.dot(space.matAX, space.matCVL)
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
    # Vd = self.volume / Gdata.DTime
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

# スケジュールの読み込み
def create_hourly_schedules(space, dtmNow, is_residential):
    # スケジュールのリスト番号の計算
    item = (get_nday(dtmNow.month, dtmNow.day) - 1) * 24 + dtmNow.hour
    # 機器顕熱[W]
    space.heat_generation_appliances = space.heat_generation_appliances_schedule[item]
    # 調理顕熱[W]
    space.heat_generation_cooking = space.heat_generation_cooking_schedule[item]
    # 調理潜熱[g/h]
    space.vapor_generation_cooking = space.vapor_generation_cooking_schedule[item]
    # 照明発熱[W]
    space.heat_generation_lighting = space.heat_generation_lighting_schedule[item]
    # 在室人員[人]
    space.number_of_people = space.number_of_people_schedule[item]
    # 人体顕熱[W]
    space.Humans = space.number_of_people \
                    * min(63.0 - 4.0 * (space.oldTr - 24.0), 119.0)
    # 人体潜熱[W]
    space.Humanl = max(space.number_of_people * 119.0 - space.Humans, 0.0)
    space.Hn = space.heat_generation_appliances + space.heat_generation_lighting + space.Humans + space.heat_generation_cooking

    # 内部発湿[kg/s]
    space.Lin = space.vapor_generation_cooking / 1000.0 / 3600.0 + space.Humanl / conra
    
    # 局所換気量
    space.LocalVentset = space.local_vent_amount_schedule[item]

    # 非住宅の室温、湿度の上下限値関連スケジュールの読み込み
    if not is_residential:
        # 上限温度設定フラグ
        space.is_upper_temp_limit_set = space.is_upper_temp_limit_set_schedule[item]
        # 設定上限温度
        space.temperature_upper_limit = space.temperature_upper_limit_schedule[item]
        # 下限温度設定フラグ
        space.is_lower_temp_limit_set = space.is_lower_temp_limit_set_schedule[item]
        # 設定下限温度
        space.temperature_lower_limit = space.temperature_lower_limit_schedule[item]

        # 上限湿度設定フラグ
        space.is_upper_humidity_limit_set = space.is_upper_humidity_limit_set_schedule[item]
        # 設定上限湿度
        space.relative_humidity_upper_limit = space.relative_humidity_upper_limit_schedule[item]
        # 下限湿度設定フラグ
        space.is_lower_humidity_limit_set = space.is_lower_humidity_limit_set_schedule[item]
        # 設定下限湿度
        space.relative_humidity_lower_limit = space.relative_humidity_lower_limit_schedule[item]

# 部位の人体に対する形態係数の計算
def calc_form_factor_for_human_body(space):
    # 部位の人体に対する形態係数の計算
    total_Aex_floor = 0.0
    total_A_floor = 0.0
    # 設定合計値もチェック
    total_Fot = 0.0
    # 床と床以外の合計面積を計算
    for surface in space.input_surfaces:
        # 下向き部位（床）
        if surface.is_solar_absorbed_inside:
            total_A_floor += surface.area
        # 床以外
        else:
            total_Aex_floor += surface.area
    
    # 上向き、下向き、垂直部位の合計面積をチェックし人体に対する形態係数の割合を基準化
    fot_floor = 0.45
    fot_exfloor = 1.0 - fot_floor

    # 人体に対する部位の形態係数の計算
    for surface in space.input_surfaces:
        # 下向き部位（床）
        if surface.is_solar_absorbed_inside:
            surface.fot = surface.area / total_A_floor * fot_floor
        # 床以外
        else:
            surface.fot = surface.area / total_Aex_floor * fot_exfloor
        total_Fot += surface.fot
        # print(surface.name, surface.fot)

    if abs(total_Fot - 1.0) > 0.001:
        print(space.name, 'total_Fot=', total_Fot)

# JSONファイルから各種スケジュールを読み込む
def read_schedules(space, d_room, Gdata):
    # 空調スケジュールの読み込み
    # 設定温度／PMV上限値の設定
    if 'is_upper_temp_limit_set' in d_room['schedule']:
        space.is_upper_temp_limit_set_schedule = d_room['schedule']['is_upper_temp_limit_set']
    # 設定温度／PMV下限値の設定
    if 'is_lower_temp_limit_set' in d_room['schedule']:
        space.is_lower_temp_limit_set_schedule = d_room['schedule']['is_lower_temp_limit_set']
    # 非住宅の場合
    if not Gdata.is_residential:
        # 室温上限値
        space.temperature_upper_limit_schedule = d_room['schedule']['temperature_upper_limit']
        # 室温下限値
        space.temperature_lower_limit_schedule = d_room['schedule']['temperature_lower_limit']
        # 相対湿度上限値の設定
        space.is_upper_humidity_limit_set_schedule = d_room['schedule']['is_upper_humidity_limit_set']
        # 相対湿度下限値の設定
        space.is_lower_humidity_limit_set_schedule = d_room['schedule']['is_lower_humidity_limit_set']
        # 相対湿度上限値
        space.relative_humidity_upper_limit_schedule = d_room['schedule']['relative_humidity_upper_limit']
        # 相対湿度下限値
        space.relative_humidity_lower_limit_schedule = d_room['schedule']['relative_humidity_lower_limit']
    # 住宅の場合
    else:
        # PMV上限値
        if 'pmv_upper_limit' in d_room['schedule']:
            space.pmv_upper_limit_schedule = d_room['schedule']['pmv_upper_limit']
        # PMV下限値
        if 'pmv_lower_limit' in d_room['schedule']:
            space.pmv_lower_limit_schedule = d_room['schedule']['pmv_lower_limit']
    # 内部発熱の初期化
    # 機器顕熱
    space.heat_generation_appliances_schedule = d_room['schedule']['heat_generation_appliances']
    # 調理顕熱
    space.heat_generation_cooking_schedule = d_room['schedule']['heat_generation_cooking']
    # 調理潜熱
    space.vapor_generation_cooking_schedule = d_room['schedule']['vapor_generation_cooking']
    
    # 照明
    space.heat_generation_lighting_schedule = d_room['schedule']['heat_generation_lighting']
    # 人体顕熱
    space.number_of_people_schedule = d_room['schedule']['number_of_people']

    # 局所換気
    space.local_vent_amount_schedule = d_room['schedule']['local_vent_amount']

# 前時刻の室温を現在時刻の室温、家具温度に置換
def update_space_oldstate(space):
    space.oldTr = space.Tr
    space.oldTfun = space.Tfun
    space.oldxr = space.xr
    space.oldxf = space.xf

# 湿度・潜熱負荷の計算ルーチン（住宅）
def calc_xr_Ll_residential(space):
    # 空調の熱交換部飽和絶対湿度の計算
    calcVac_xeout(space, space.nowAC)
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

# 室温・顕熱熱負荷の計算ルーティン
def calc_Tr_Ls(nowAC, is_radiative_heating, BRC, BRM, BRL, Lrcap, Tset):
    Lcs = 0.0
    Lrs = 0.0
    Tr = 0.0
    # 非空調時の計算
    if nowAC == 0:
        Tr = BRC / BRM
    # 熱負荷計算（能力無制限）
    elif nowAC == 1 or nowAC == -1 or nowAC == 4:
        # 対流式空調の場合
        if is_radiative_heating != True or is_radiative_heating and nowAC < 0:
            Lcs = BRM * Tset - BRC
        # 放射式空調
        else:
            Lrs = (BRM * Tset - BRC) / BRL
        # 室温の計算
        Tr = (BRC + Lcs + BRL * Lrs) / BRM
    # 放射暖房最大能力運転（当面は暖房のみ）
    elif nowAC == 3 and Lrcap > 0.0:
        Lrs = Lrcap
        # 室温は対流式で維持する
        Lcs = BRM * Tset - BRC - Lrs * BRL
        # 室温の計算
        Tr = (BRC + Lcs + BRL * Lrs) / BRM

    # 室温、対流空調熱負荷、放射空調熱負荷を返す
    return (Tr, Lcs, Lrs)

# 家具の温度を計算する
def calcTfun(space, Gdata):
    if space.Capfun > 0.0:
        space.Tfun = ((space.Capfun / Gdata.DTime * space.oldTfun \
                + space.Cfun * space.Tr + space.Qsolfun) \
                / (space.Capfun / Gdata.DTime + space.Cfun))
        space.Qfuns = space.Cfun * (space.Tr - space.Tfun)
    # if self.name == "主たる居室":
    #     print(self.name, self.oldTfun, self.Tfun, self.Capfun, self.Cfun, self.Qsolfun)
    return space.Tfun

# 家具類の湿度を計算する
def calcxf(space, Gdata):
    space.xf = (space.Gf / Gdata.DTime * space.oldxf + space.Cx * space.xr) / (space.Gf / Gdata.DTime + space.Cx)
    space.Qfunl = space.Cx * (space.xr - space.xf)
    # if self.name == "主たる居室":
    #     print(self.name, self.oldTfun, self.Tfun, self.Capfun, self.Cfun, self.Qsolfun)
    return space.xf

# エアコンの熱交換部飽和絶対湿度の計算
def calcVac_xeout(space, nowAC):
    # Lcsは加熱が正
    # 加熱時は除湿ゼロ
    Qs = - space.Lcs
    if nowAC == 0 or Qs <= 1.0e-3:
        space.Vac = 0.0
        space.Ghum = 0.0
        space.Lcl = 0.0
        return
    else:
        # 風量[m3/s]の計算（線形補間）
        space.Vac = (space.Vmin + (space.Vmax - space.Vmin) \
                / (space.qmax_c - space.qmin_c) * (Qs - space.qmin_c)) / 60.0
        # 熱交換器温度＝熱交換器部分吹出温度
        space.Teout = space.Tr - Qs / (conca * conrowa * space.Vac * (1.0 - space.bypass_factor_rac))
        # 熱交換器吹出部分は飽和状態
        space.xeout = x(Pws(space.Teout))

# 暖房設備仕様の読み込み
def heating_equipment_read(space, dheqp):
    # 放射暖房有無（Trueなら放射暖房あり）
    space.is_radiative_heating = dheqp['is_radiative_heating']
    # 放射暖房最大能力[W]
    space.radiative_heating_max_capacity = 0.0
    if space.is_radiative_heating:
        space.radiative_heating_max_capacity = dheqp['radiative_heating']['max_capacity'] * dheqp['radiative_heating']['area']

# 透過日射の吸収比率を設定する（家具の吸収比率を返す）
def calc_absorption_ratio_of_transmitted_solar_radiation(room_name, tolal_floor_area, furniture_ratio, surfaces):
    # 部位の日射吸収比率の計算

    # 透過日射の室内部位表面吸収比率の計算
    # 50%を床、50%を家具に吸収させる
    # 床が複数の部位の場合は面積比で案分する
    FsolFlr = 0.5
    # 家具の吸収比率で初期化
    TotalR = furniture_ratio
    modify_furniture_ratio = furniture_ratio

    for surface in surfaces:
        SolR = 0.0
        # 床の室内部位表面吸収比率の設定
        if surface.is_solar_absorbed_inside == True:
            SolR = FsolFlr * surface.area / tolal_floor_area
        surface.SolR = SolR
        # 室内部位表面吸収比率の合計値（チェック用）
        TotalR += SolR
    # 日射吸収率の合計値のチェック
    if abs(TotalR - 1.0) > 0.00001:
        print(room_name, '日射吸収比率合計値エラー', TotalR)
        print("残りは家具に吸収させます")
        # 修正家具の日射吸収比率の計算
        modify_furniture_ratio = furniture_ratio + max(1.0 - TotalR, 0)
    
    return modify_furniture_ratio

# 表面対流・放射熱伝達率の計算
def calc_surface_heat_transfer_coefficient(surfaces):
    # 室内側表面熱伝達率の計算
    for surface in surfaces:
        surface.hir = surface.Ei / (1.0 - surface.Ei * surface.FF) \
                * 4.0 * Sgm * (20.0 + 273.15) ** 3.0
        # surface.hir = 5.0
        surface.hic = max(0.0, surface.hi - surface.hir)
        # print(surface.name, surface.hic, surface.hir, surface.hi)

# 平均放射温度計算時の各部位表面温度の重み計算
def calc_mrt_weight(surfaces):
    # 各部位表面温度の重み=面積×放射熱伝達率の比率
    total_area_hir = 0.0
    for surface in surfaces:
        total_area_hir += surface.area * surface.hir
    
    for surface in surfaces:
        surface.Fmrt = surface.area * surface.hir / total_area_hir

# 微小体に対する部位の形態係数の計算
def calc_form_factor_of_microbodies(space_name, surfaces):
    # 面積比の計算
    # 面積比の最大値も同時に計算（ニュートン法の初期値計算用）
    max_a = 0.0
    Atotal = 0.0
    for surface in surfaces:
        Atotal += surface.area
    for surface in surfaces:
        surface.a = surface.area / Atotal
        max_a = max(max_a, surface.a)
    
    # 室のパラメータの計算（ニュートン法）
    # 初期値を設定
    fbd = max_a * 4.0 + 1.e-4
    # 収束判定
    isConverge = False
    for i in range(50):
        L = -1.0
        Ld = 0.0
        for surface in surfaces:
            temp = math.sqrt(1.0 - 4.0 * surface.a / fbd)
            L += 0.5 * (1.0 - temp)
            Ld += surface.a / ((fbd ** 2.0) * temp)
            # print(surface.name, 'a=', surface.a, 'L=', 0.5 * (1.0 - math.sqrt(temp)), 'Ld=', -0.25 * (1.0 + 4.0 * surface.a / fbd ** (2.0)) / temp)
        fb = fbd + L / Ld
        # print(i, 'fb=', fb, 'fbd=', fbd)
        # 収束判定
        if abs(fb - fbd) < 1.e-4:
            isConverge = True
            break
        fbd = fb
    
    # 収束しないときには警告を表示
    if not isConverge:
        print(space_name, '形態係数パラメータが収束しませんでした。')
    # print('合計表面積=', self.Atotal)
    # 形態係数の計算（永田の方式）
    # 総和のチェック
    TotalFF = 0.0
    for surface in surfaces:
        FF = 0.5 * (1.0 - math.sqrt(1.0 - 4.0 * surface.a / fb))
        TotalFF += FF
        # 形態係数の設定（面の微小球に対する形態係数）
        surface.FF = FF
    
    if abs(TotalFF - 1.0) > 1.0e-3:
        print('形態係数の合計値が不正 name=', space_name, 'TotalFF=', TotalFF)

# ルームエアコンの仕様の設定
# とりあえず、建研仕様書の手法を実装
def set_rac_spec(space):
    # 定格冷房能力[W]の計算（除湿量計算用）
    space.qrtd_c = 190.5 * space.TotalAF + 45.6
    # 冷房最大能力[W]の計算
    space.qmax_c = 0.8462 * space.qrtd_c + 1205.9
    # 冷房最小能力[W]の計算（とりあえず500Wで固定）
    space.qmin_c = 500.0
    # 最大風量[m3/min]、最小風量[m3/min]の計算
    space.Vmax = 11.076 * (space.qrtd_c / 1000.0) ** 0.3432
    space.Vmin = space.Vmax * 0.55

# 冷房設備仕様の読み込み
def cooling_equipment_read(space, dceqp):
    # 放射冷房有無（Trueなら放射冷房あり）
    space.is_radiative_cooling = dceqp['is_radiative_cooling']
    # 放射冷房最大能力[W]
    space.radiative_cooling_max_capacity = 0.0
    if space.is_radiative_cooling:
        space.radiative_cooling_max_capacity = dceqp['radiative_cooling']['max_capacity'] * dceqp['radiative_cooling']['area']
    # 対流式の場合
    else:
        # 熱交換器種類
        space.heat_exchanger_type = dceqp['convective_cooling']['heat_exchanger_type']
        # 定格冷房能力[W]
        space.convective_cooling_rtd_capacity = dceqp['convective_cooling']['max_capacity']

# 部位の集約（同一境界条件の部位を集約する）
def summarize_building_part(surfaces):
    # 部位のグループ化
    group_number = 0
    for surface in surfaces:
        # 最初の部位は最も若いグループ番号にする
        if not surface.is_grouping:
            # グループ化済みにする
            surface.is_grouping = True
            surface.group_number = group_number

            # 同じ境界条件の部位を探す
            for comp_surface in surfaces:
                # 境界条件が同じかどうかチェックする
                # グループ化していない部位だけを対象とする
                if not comp_surface.is_grouping:
                    if boundary_comp(surface, comp_surface):
                        comp_surface.is_grouping = True
                        comp_surface.group_number = group_number
            # グループ番号を増やす
            group_number += 1
    
    # print("集約前")
    # for surface in surfaces:
        # print('name=', surface.name, 'area=', surface.area, 'group=', surface.group_number)

    summarize_surfaces = []
    for i in range(group_number):
        summarize_surfaces.append(create_surface(surfaces, i))

    # for surface in summarize_surfaces:
    #     print(surface.boundary_type, surface.name, surface.group_number)
    return summarize_surfaces

# 透過日射を集約する
def summarize_transparent_solar_radiation(surfaces, Gdata, weather):
    # 透過日射熱取得収録配列の初期化とメモリ確保
    Qgt = []
    Qgt = [0.0 for j in range(int(8760.0 * 3600.0 / float(Gdata.DTime)))]

    ntime = int(24 * 3600 / Gdata.DTime)
    nnow = 0
    item = 0
    start_date = datetime.datetime(1989, 1, 1)
    for nday in range(get_nday(1, 1), get_nday(12, 31) + 1):
        for tloop in range(ntime):
            dtime = datetime.timedelta(days=nnow + float(tloop) / float(ntime))
            dtmNow = dtime + start_date

            # 太陽位置の計算
            solar_position = Solpos(weather, dtmNow)
            # 傾斜面日射量の計算
            Idn = WeaData(weather, enmWeatherComponent.Idn, dtmNow, solar_position)
            Isky = WeaData(weather, enmWeatherComponent.Isky, dtmNow, solar_position)
            for surface in surfaces:
                # 外表面に日射が当たる場合
                if surface.is_sun_striked_outside and surface.boundary_type == "external_transparent_part":
                    surface.Id, surface.Isky, surface.Ir, surface.Iw = calc_slope_sol(surface, solar_position, Idn, Isky)

                    # 日除けの日影面積率の計算
                    if surface.sunbrk.existance:
                        surface.Fsdw = get_shading_area_ratio(surface, solar_position)
                    Qgt[item] += calc_Qgt(surface)

            item += 1
        nnow += 1
    return Qgt

def create_spaces(Gdata, rooms, weather):
    objSpace = {}
    for room in rooms:
        space = Space(Gdata, room, weather)
        objSpace[room['name']] = space
    return objSpace