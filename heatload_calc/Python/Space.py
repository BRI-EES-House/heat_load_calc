
from typing import List
import Weather
from Weather import enmWeatherComponent, WeaData, SolPosList, get_datetime_list
import math
import numpy as np
from Surface import Surface
from NextVent import NextVent
from common import conca, conrowa, Sgm, conra, get_nday
import datetime

import s4_1_sensible_heat as s41

import a1_calculation_surface_temperature as a1
import apdx6_direction_cos_incident_angle as a6
import a7_inclined_surface_solar_radiation as a7
import a8_shading as a8
import a9_rear_surface_equivalent_temperature as a9
import a11_opening_transmission_solar_radiation as a11
import a14_furniture as a14
import a15_air_flow_rate_rac as a15
import a12_indoor_radiative_heat_transfer as a12
import a13_Win_ACselect as a13
import a23_surface_heat_transfer_coefficient as a23
import a29_local_vent_schedule as a29
import a30_internal_heat_schedule as a30
import a31_lighting_schedule as a31
import a32_resident_schedule as a32
import a34_building_part_summarize as a34

from Psychrometrics import xtrh

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
    def __init__(self, calc_time_interval, d_room, weather, solar_position):
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
        self.Lrs = 0.0
        self.Lrl = 0.0
        self.Lcl = 0.0
        self.Lcl = 0.0
        self.Ls = None
        self.Tr = 15.0                              # 室温の初期化
        self.oldTr = 15.0                         # 前時刻の室温の初期化
        self.Tfun = 15.0                            # 家具の温度[℃]
        self.oldTfun = 15.0                       # 前時刻の家具の温度[℃]
        self.rsolfun = 0.5                        # 透過日射の内家具が吸収する割合[－]
        # self.rsolfun = 0.0
        self.kc = s41.calc_kc()  #式(12)
                                                    # 人体表面の熱伝達率の対流成分比率
        self.kr = s41.calc_kr()  #式(13)
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

        self.Ghum = 0.0

        # 暖房設備仕様の読み込み
        heating_equipment_read(self, d_room['heating_equipment'])
        # 冷房設備仕様の読み込み
        cooling_equipment_read(self, d_room['cooling_equipment'])
        
        self.volume = d_room['volume']            # 室気積[m3]
        self.Ga = self.volume * conrowa         # 室空気の質量[kg]

        # 家具の熱容量、湿気容量の計算
        # Capfun:家具熱容量[J/K]、Cfun:家具と室空気間の熱コンダクタンス[W/K]
        # Gf:湿気容量[kg/(kg/kg(DA))]、Cx:湿気コンダクタンス[kg/(s･kg/kg(DA))]
        self.Capfun  = a14.get_Capfun(self.volume)
        self.Cfun = a14.get_Cfun(self.Capfun)
        self.Gf = a14.get_Gf(self.volume)
        self.Cx = a14.get_Cx(self.Gf)

        self.xr = xtrh(20.0, 40.0)                  # 室の絶対湿度[kg/kg(DA)]
        self.oldxr = self.xr                      # 室内絶対湿度の初期値
        self.xf = self.xr                           # 家具類の絶対湿度
        self.oldxf = self.xr                      # 家具類の絶対湿度の初期値
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

        # ********** 計算準備14 局所換気スケジュール、機器発熱スケジュール、
        # 照明発熱スケジュール、人体発熱スケジュールの読み込み **********

        # 局所換気スケジュールの読み込み
        self.local_vent_amount_schedule = a29.read_local_vent_schedules_from_json(d_room)

        # 機器発熱スケジュールの読み込み
        self.heat_generation_appliances_schedule, \
        self.heat_generation_cooking_schedule, \
        self.vapor_generation_cooking_schedule = a30.read_internal_heat_schedules_from_json(d_room)

        # 照明発熱スケジュールの読み込み
        self.heat_generation_lighting_schedule = a31.read_lighting_schedules_from_json(d_room)

        # 在室人数スケジュールの読み込み
        self.number_of_people_schedule  = a32.read_resident_schedules_from_json(d_room)

        # 空調スケジュールの読み込み
        self.is_upper_temp_limit_set_schedule, \
        self.is_lower_temp_limit_set_schedule, \
        self.pmv_upper_limit_schedule, \
        self.pmv_lower_limit_schedule = a13.read_air_conditioning_schedules_from_json(d_room)

        # ********** 計算準備6 隣室間換気の読み込み **********

        # 室間換気量クラスの構築
        self.RoomtoRoomVent = \
            [NextVent(room_vent['upstream_room_type'], room_vent['volume']) for room_vent in d_room['next_vent']]

        # 部位の読み込み
        self.input_surfaces = \
            [Surface(d_surface, calc_time_interval) for d_surface in d_room['boundaries']]

        # 透過日射熱取得の計算（部位を集約するので最初に8760時間分計算しておく）
        # 透過日射熱取得収録配列の初期化とメモリ確保
        self.Qgt = np.zeros(int(8760.0 * 3600.0 / float(calc_time_interval)))


        dtlist = get_datetime_list(calc_time_interval)
        Idn = np.zeros(len(dtlist))
        Isky = np.zeros(len(dtlist))
        RN = np.zeros(len(dtlist))
        Ta = np.zeros(len(dtlist))

        for item, dtmNow in enumerate(dtlist):
            # 傾斜面日射量の計算
            Idn[item] = WeaData(weather, enmWeatherComponent.Idn, dtmNow, solar_position, item)
            Isky[item] = WeaData(weather, enmWeatherComponent.Isky, dtmNow, solar_position, item)
            # 夜間放射量
            RN[item] = WeaData(weather, enmWeatherComponent.RN, dtmNow, solar_position, item)
            # 外気温度
            Ta[item] = WeaData(weather, enmWeatherComponent.Ta, dtmNow, solar_position, item)

        for surface in self.input_surfaces:
            # 外表面に日射が当たる場合
            if surface.is_sun_striked_outside:

                if 'external' in surface.backside_boundary_condition.Type:

                    # 入射角の方向余弦
                    surface.backside_boundary_condition.CosT = a6.calc_cos_incident_angle(
                        sin_h_s=solar_position.sin_h_s,
                        cos_h_s=solar_position.cos_h_s,
                        sin_a_s=solar_position.sin_a_s,
                        cos_a_s=solar_position.cos_a_s,
                        wa=surface.backside_boundary_condition.Wa,
                        wb= surface.backside_boundary_condition.Wb
                    )

                    # 傾斜面日射量
                    surface.Id, surface.Isky, surface.Ir, surface.Iw = a7.calc_slope_sol(
                        i_sun_dir=Idn,
                        i_sun_sky=Isky,
                        sin_h_s=solar_position.sin_h_s,
                        cos_phi=surface.backside_boundary_condition.CosT,
                        phi_evlp_sky=surface.backside_boundary_condition.Fs,
                        phi_evlp_grd=surface.backside_boundary_condition.dblFg,
                        rho_grd=surface.backside_boundary_condition.Rg
                    )
                else:
                    # 0を入れておく
                    surface.backside_boundary_condition.CosT = np.zeros(len(dtlist))
                    surface.Id = np.zeros(len(dtlist))
                    surface.Isky = np.zeros(len(dtlist))
                    surface.Ir = np.zeros(len(dtlist))
                    surface.Iw = np.zeros(len(dtlist))

                # 一般部位、不透明な開口部の場合
                if surface.boundary_type == "external_general_part" or surface.boundary_type == "external_opaque_part":
                    # 傾斜面の相当外気温度の計算
                    surface.Teolist = a9.get_Te(
                        Fs=surface.backside_boundary_condition.Fs,
                        Iw=surface.Iw,
                        _as=surface.outside_solar_absorption,
                        ho=surface.ho,
                        e=surface.Eo,
                        Ta=Ta,
                        RN=RN
                    )
                # 透明開口部の場合
                elif surface.boundary_type == "external_transparent_part":
                    # 日除けの日影面積率の計算
                    if surface.sunbrk.existance:
                        surface.Fsdw = a8.calc_shading_area_ratio(
                            depth=surface.sunbrk.depth,
                            d_e=surface.sunbrk.d_e,
                            d_h=surface.sunbrk.d_h,
                            a_s=solar_position.a_s,
                            h_s=solar_position.h_s,
                            Wa=surface.backside_boundary_condition.Wa
                        )
                    else:
                        surface.Fsdw = np.zeros_like(dtlist, dtype=np.float)

                    # 透過日射熱取得の集約
                    self.Qgt += a11.calc_Qgt(
                        CosT=surface.backside_boundary_condition.CosT,
                        incident_angle_characteristics=surface.transparent_opening.incident_angle_characteristics,
                        Id=surface.Id,
                        Fsdw=surface.Fsdw,
                        Isky=surface.Isky,
                        Ir=surface.Ir,
                        area=surface.area,
                        T=surface.transparent_opening.T,
                        Cd=surface.transparent_opening.Cd
                    )

                    # 相当外気温度の集約
                    surface.Teolist = - surface.Eo * surface.backside_boundary_condition.Fs * RN / surface.ho + Ta

            # 地面の場合は、年平均気温とする
            elif surface.boundary_type == "ground":
                surface.Teo = np.array([weather.AnnualTave]*len(dtlist))

        # 部位の集約
        self.input_surfaces = a34.summarize_building_part(self.input_surfaces)

        # 部位の面数
        self.Nsurf = len(self.input_surfaces)

        # 配列の準備
        area = np.array([x.area for x in self.input_surfaces])
        is_solar_absorbed_inside = np.array([x.is_solar_absorbed_inside for x in self.input_surfaces])
        Ei = np.array([x.Ei for x in self.input_surfaces])
        hi = np.array([x.hi for x in self.input_surfaces])
        RFA0 = np.array([x.RFA0 for x in self.input_surfaces])
        V_nxt = np.array([x.volume for x in self.RoomtoRoomVent])

        # 部位の人体に対する形態係数を計算
        fot = a12.calc_form_factor_for_human_body(area, is_solar_absorbed_inside)

        if abs(np.sum(fot) - 1.0) > 0.001:
            print(self.name, 'total_Fot=', np.sum(fot))

        # 合計面積の計算
        self.Atotal = np.sum(area)

        # 合計床面積の計算
        self.TotalAF = np.sum(area * is_solar_absorbed_inside)

        # ルームエアコンの仕様の設定
        self.qrtd_c = a15.get_qrtd_c(self.TotalAF)
        self.qmax_c = a15.get_qmax_c(self.qrtd_c)
        self.qmin_c = a15.get_qmin_c()
        self.Vmax = a15.get_Vmax(self.qrtd_c)
        self.Vmin = a15.get_Vmin(self.Vmax)

        # 放射暖房の発熱部位の設定（とりあえず床発熱）
        flr = (area / self.TotalAF) * self.is_radiative_heating * is_solar_absorbed_inside

        # 微小点に対する室内部位の形態係数の計算（永田先生の方法）
        FF, a = a12.calc_form_factor_of_microbodies(self.name, area)

        # 表面熱伝達率の計算
        hir, hic = a23.calc_surface_transfer_coefficient(Ei, FF, hi)

        # 平均放射温度計算時の各部位表面温度の重み計算 式(101)
        Fmrt = a12.get_mrt_weight(area, hir)

        # 日射吸収比率の計算
        self.rsolfun, SolR = a12.calc_absorption_ratio_of_transmitted_solar_radiation(self.name, self.TotalAF, self.rsolfun, is_solar_absorbed_inside, area)

        # 結果保持
        for i, surface in enumerate(self.input_surfaces):
            surface.a = a[i]
            surface.FF = FF[i]
            surface.hir = hir[i]
            surface.hic = hic[i]
            surface.Fmrt = Fmrt[i]
            surface.SolR = SolR[i]
            surface.fot = fot[i]
            surface.flr = flr[i]


        # *********** 室内表面熱収支計算のための行列作成 ***********

        # matFIAの作成 式(26)
        matFIA = a1.get_FIA(RFA0, hic)

        # FLB=φA0×flr×(1-Beta) 式(26)
        matFLB = a1.get_FLB(RFA0, flr, self.Beta, area)

        # 行列AX 式(25)
        self.matAX = a1.get_AX(RFA0, hir, Fmrt, hi, self.Nsurf)

        # {WSR}の計算 式(24)
        self.matWSR = a1.get_WSR(self.matAX, matFIA)

        # {WSB}の計算 式(24)
        self.matWSB = a1.get_WSB(self.matAX, matFLB)

        # ****************************************************

        # BRMの計算 式(5)
        self.BRM = s41.get_BRM(
            Hcap=self.Hcap, 
            calc_time_interval=calc_time_interval, 
            matWSR=self.matWSR, 
            Capfun=self.Capfun,
            Cfun=self.Cfun, 
            Vent=self.Vent, 
            local_vent_amount_schedule=self.local_vent_amount_schedule,
            area=area,
            hic=hic,
            V_nxt=V_nxt
        )

        # BRLの計算 式(7)
        self.BRL = s41.get_BRL(
            Beta=self.Beta,
            matWSB=self.matWSB,
            area=area,
            hic=hic
        )



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



def create_spaces(calc_time_interval, rooms, weather, solar_position):
    objSpace = {}
    for room in rooms:
        space = Space(calc_time_interval, room, weather, solar_position)
        objSpace[room['name']] = space
    return objSpace