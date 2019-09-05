
from typing import List
import Weather
from Weather import enmWeatherComponent, WeaData, Solpos
import math
import numpy as np
from Surface import Surface
from NextVent import NextVent
from common import conca, conrowa, Sgm, conra, bypass_factor_rac, get_nday
import datetime
from calculation_surface_temperature import make_matrix_for_surface_heat_balance
from apdx3_human_body import get_alpha_hm_c, get_alpha_hm_r
# from opening_transmission_solar_radiation import summarize_transparent_solar_radiation
from furniture import calc_furniture
from air_flow_rate_rac import set_rac_spec
from indoor_radiative_heat_transfer import calc_form_factor_of_microbodies, calc_mrt_weight, calc_absorption_ratio_of_transmitted_solar_radiation, \
    calc_form_factor_for_human_body
from Psychrometrics import xtrh
from surface_heat_transfer_coefficient import calc_surface_heat_transfer_coefficient
from building_part_summarize import summarize_building_part
from local_vent_schedule import read_local_vent_schedules_from_json
from internal_heat_schedule import read_internal_heat_schedules_from_json
from lighting_schedule import read_lighting_schedules_from_json
from resident_schedule import read_resident_schedules_from_json
from Win_ACselect import read_air_conditioning_schedules_from_json
from apdx6_direction_cos_incident_angle import calc_cos_incident_angle
from inclined_surface_solar_radiation import calc_slope_sol
from rear_surface_equivalent_temperature import get_Te
from opening_transmission_solar_radiation import calc_Qgt
from Sunbrk import get_shading_area_ratio

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
    def __init__(self, calc_time_interval, d_room, weather):
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
        self.kc = get_alpha_hm_c() / (get_alpha_hm_r() + get_alpha_hm_c())
                                                    # 人体表面の熱伝達率の対流成分比率
        self.kr = get_alpha_hm_r() / (get_alpha_hm_r() + get_alpha_hm_c())
                                                    # 人体表面の熱伝達率の放射成分比率
        self.air_conditioning_demand = False        # 当該時刻の空調需要（0：なし、1：あり）
        self.prev_air_conditioning_mode = 0         # 前時刻の空調運転状態（0：停止、正：暖房、負：冷房）
        self.is_prev_window_open = False            # 前時刻の窓状態（0：閉鎖、1：開放）
        self.now_air_conditioning_mode = 0          # 当該時刻の空調運転状態（0：なし、正：暖房、負：冷房）
        self.is_now_window_open = False             # 当該時刻の窓状態（0：閉鎖、1：開放）
        # PMVの計算条件
        self.Met = 1.0                              # 代謝量[Met]
        self.Wme = 0.0                              # 外部仕事[Met]
        self.Vel = 0.1                              # 相対風速[m/s]
        self.Clo = 1.0                              # 着衣量[Clo]
        self.OTset = 0.0                            # 設定作用温度[℃]
        self.is_radiative_heating = False
        self.radiative_heating_max_capacity = 0.0

        # 暖房設備仕様の読み込み
        heating_equipment_read(self, d_room['heating_equipment'])
        # 冷房設備仕様の読み込み
        cooling_equipment_read(self, d_room['cooling_equipment'])
        
        self.volume = d_room['volume']            # 室気積[m3]
        self.Ga = self.volume * conrowa         # 室空気の質量[kg]

        # 家具の熱容量、湿気容量の計算
        # Capfun:家具熱容量[J/K]、Cfun:家具と室空気間の熱コンダクタンス[W/K]
        # Gf:湿気容量[kg/(kg/kg(DA))]、Cx:湿気コンダクタンス[kg/(s･kg/kg(DA))]
        self.Capfun, self.Cfun, self.Gf, self.Cx = calc_furniture(self)

        self.xr = xtrh(20.0, 40.0)                  # 室の絶対湿度[kg/kg(DA)]
        self.oldxr = self.xr                      # 室内絶対湿度の初期値
        self.xf = self.xr                           # 家具類の絶対湿度
        self.oldxf = self.xr                      # 家具類の絶対湿度の初期値
        self.bypass_factor_rac = bypass_factor_rac               # バイパスファクター
        self.xeout = 0.0                          # エアコン熱交換部の飽和絶対湿度[kg/kg(DA)]
        self.Vac = 0.0                              # エアコンの風量[m3/s]
        self.RH = 50.0                              # 室相対湿度[%]
        self.Vcrossvent = self.volume * d_room['natural_vent_time']
                                                    # 窓開放時通風量
        # 室空気の熱容量
        self.Hcap = self.volume * conrowa * conca
        # print(self.Hcap)
        self.Vent = d_room['vent']                #計画換気量
        self.Inf = 0.0                            #すきま風量（暫定値）
        self.Beta = 0.0                           # 放射暖房対流比率

        # 局所換気スケジュールの読み込み
        read_local_vent_schedules_from_json(self, d_room)
        # 機器発熱スケジュールの読み込み
        read_internal_heat_schedules_from_json(self, d_room)
        # 照明発熱スケジュールの読み込み
        read_lighting_schedules_from_json(self, d_room)
        # 在室人数スケジュールの読み込み
        read_resident_schedules_from_json(self, d_room)
        # 空調スケジュールの読み込み
        read_air_conditioning_schedules_from_json(self, d_room)

        # 室間換気量クラスの構築
        self.RoomtoRoomVent = []
        for room_vent in d_room['next_vent']:
            self.RoomtoRoomVent.append(NextVent(room_vent['upstream_room_type'], room_vent['volume']))
        self.Nsurf = 0  # 部位の数
        self.input_surfaces = []

        # 部位の読み込み
        for d_surface in d_room['boundaries']:
            # print(d_surface['name'])
            self.input_surfaces.append(Surface(d = d_surface, calc_time_interval = calc_time_interval))
        
        # 透過日射熱取得の計算（部位を集約するので最初に8760時間分計算しておく）
        # 透過日射熱取得収録配列の初期化とメモリ確保
        self.Qgt = [0.0 for j in range(int(8760.0 * 3600.0 / float(calc_time_interval)))]

        ntime = int(24 * 3600 / calc_time_interval)
        nnow = 0
        item = 0
        start_date = datetime.datetime(1989, 1, 1)
        for nday in range(get_nday(1, 1), get_nday(12, 31) + 1):
            for tloop in range(ntime):
                dtime = datetime.timedelta(days=nnow + float(tloop) / float(ntime))
                dtmNow = dtime + start_date
                sequence_number = int((get_nday(dtmNow.month, dtmNow.day) - 1) * 24 * 4 + dtmNow.hour * 4 + float(dtmNow.minute) / 60.0 * 3600 / calc_time_interval)

                # 太陽位置の計算
                solar_position = Solpos(weather, dtmNow)
                # 傾斜面日射量の計算
                Idn = WeaData(weather, enmWeatherComponent.Idn, dtmNow, solar_position)
                Isky = WeaData(weather, enmWeatherComponent.Isky, dtmNow, solar_position)
                # 夜間放射量
                RN = WeaData(weather, enmWeatherComponent.RN, dtmNow, solar_position)
                # 外気温度
                Ta = WeaData(weather, enmWeatherComponent.Ta, dtmNow, solar_position)
                for surface in self.input_surfaces:
                    # 外表面に日射が当たる場合
                    if surface.is_sun_striked_outside:
                        sin_h_s = solar_position.sin_h_s
                        cos_h_s = solar_position.cos_h_s
                        sin_a_s = solar_position.sin_a_s
                        cos_a_s = solar_position.cos_a_s
                        wa = surface.backside_boundary_condition.Wa
                        wb = surface.backside_boundary_condition.Wb

                        if 'external' in surface.backside_boundary_condition.Type:
                            cos_t = calc_cos_incident_angle(sin_h_s, cos_h_s, sin_a_s, cos_a_s, wa, wb)
                            surface.backside_boundary_condition.CosT = cos_t
                            Fs = surface.backside_boundary_condition.Fs
                            dblFg = surface.backside_boundary_condition.dblFg
                            Rg = surface.backside_boundary_condition.Rg
                            surface.Id, surface.Isky, surface.Ir, surface.Iw = calc_slope_sol(
                                Idn, Isky, sin_h_s, cos_t, Fs, dblFg, Rg)
                        else:
                            surface.backside_boundary_condition.CosT = 0.0
                            surface.Id, surface.Isky, surface.Ir, surface.Iw = 0.0, 0.0, 0.0, 0.0

                        # 一般部位、不透明な開口部の場合
                        if surface.boundary_type == "external_general_part" or surface.boundary_type == "external_opaque_part":
                            surface.Teolist[item] = get_Te(surface.backside_boundary_condition, \
                                surface.Iw, surface.outside_solar_absorption, surface.ho, surface.Eo, Ta, RN)
                        # 透明開口部の場合
                        elif surface.boundary_type == "external_transparent_part":
                            # 日除けの日影面積率の計算
                            if surface.sunbrk.existance:
                                surface.Fsdw = get_shading_area_ratio(surface, solar_position)
                            # 透過日射熱取得の集約
                            self.Qgt[item] += calc_Qgt(surface)

                            # 相当外気温度の集約
                            surface.Teolist[item] = - surface.Eo * surface.backside_boundary_condition.Fs * RN / surface.ho + Ta
                    # 地面の場合は、年平均気温とする
                    elif surface.boundary_type == "ground":
                        surface.Teo = weather.AnnualTave
                item += 1
            nnow += 1
        
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
        self.qrtd_c, self.qmax_c, self.qmin_c, self.Vmax, self.Vmin = set_rac_spec(self)

        # 放射暖房の発熱部位の設定（とりあえず床発熱）
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
        self.matAX, self.matWSR, self.matWSB = make_matrix_for_surface_heat_balance(self)

        # ** BRMを計算する 式(5) **

        # BRM - 初期値
        BRM_0 = self.Hcap / calc_time_interval

        # BRM - 何と書けばよいのだろう
        for (matWSR, surface) in zip(self.matWSR, self.input_surfaces):
            BRM_0 += surface.area * surface.hic * (1.0 - matWSR)

        # BRM - 室間換気
        for room_vent in self.RoomtoRoomVent:
            BRM_0 += conca * conrowa * room_vent.volume / 3600.0
            
        # BRM - 家具からの熱取得
        if self.Capfun > 0.0:
            BRM_0 += 1. / (calc_time_interval / self.Capfun + 1. / self.Cfun)

        # BRM - 外気導入項の計算（3項目の0.0はすきま風量）
        self.BRM = BRM_0 + conca * conrowa * (self.Vent + 0.0 + np.repeat(self.local_vent_amount_schedule, 4)) / 3600.0

        # ** BRLを計算する 式(7) **

        # BRL - 初期値
        BRL_0 = self.Beta

        # BRL - 何と書けばよいのだろう
        for (matWSB, surface) in zip(self.matWSB, self.input_surfaces):
            BRL_0 += surface.area * surface.hic * matWSB

        self.BRL = np.repeat([BRL_0], 8760 * 4)


# 前時刻の室温を現在時刻の室温、家具温度に置換
def update_space_oldstate(space):
    space.oldTr = space.Tr
    space.oldTfun = space.Tfun
    space.oldxr = space.xr
    space.oldxf = space.xf

# 暖房設備仕様の読み込み
def heating_equipment_read(space, dheqp):
    # 放射暖房有無（Trueなら放射暖房あり）
    space.is_radiative_heating = dheqp['is_radiative_heating']
    # 放射暖房最大能力[W]
    space.radiative_heating_max_capacity = 0.0
    if space.is_radiative_heating:
        space.radiative_heating_max_capacity = dheqp['radiative_heating']['max_capacity'] * dheqp['radiative_heating']['area']

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



def create_spaces(calc_time_interval, rooms, weather):
    objSpace = {}
    for room in rooms:
        space = Space(calc_time_interval, room, weather)
        objSpace[room['name']] = space
    return objSpace