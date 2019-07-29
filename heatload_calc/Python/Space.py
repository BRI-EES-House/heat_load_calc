import numpy as np
from typing import List
import Weather
from Weather import enmWeatherComponent, Solpos, WeaData
import math
import Surface
from Surface import Surface, create_surface, boundary_comp, calc_slope_sol, calc_Fsdw, calc_Qgt, calcTeo, calc_RSsol, update_qi, calc_Tei, convolution
import NextVent
from NextVent import NextVent
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
        self.Annual_un_LoadcCs = 0.0              # 年間未処理顕熱冷房熱負荷（対流成分）
        self.Annual_un_LoadcHs = 0.0              # 年間未処理顕熱暖房熱負荷（対流成分）
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
        if Gdata.is_residential:
            self.heating_equipment_read(d_room['heating_equipment'])
                                                    # 暖房設備仕様の読み込み
            self.cooling_equipment_read(d_room['cooling_equipment'])
        
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

        # 空調スケジュールの読み込み
        # 設定温度／PMV上限値の設定
        if 'is_upper_temp_limit_set' in d_room['schedule']:
            self.is_upper_temp_limit_set_schedule = d_room['schedule']['is_upper_temp_limit_set']
        # 設定温度／PMV下限値の設定
        if 'is_lower_temp_limit_set' in d_room['schedule']:
            self.is_lower_temp_limit_set_schedule = d_room['schedule']['is_lower_temp_limit_set']
        # 非住宅の場合
        if not Gdata.is_residential:
            # 室温上限値
            self.temperature_upper_limit_schedule = d_room['schedule']['temperature_upper_limit']
            # 室温下限値
            self.temperature_lower_limit_schedule = d_room['schedule']['temperature_lower_limit']
            # 相対湿度上限値の設定
            self.is_upper_humidity_limit_set_schedule = d_room['schedule']['is_upper_humidity_limit_set']
            # 相対湿度下限値の設定
            self.is_lower_humidity_limit_set_schedule = d_room['schedule']['is_lower_humidity_limit_set']
            # 相対湿度上限値
            self.relative_humidity_upper_limit_schedule = d_room['schedule']['relative_humidity_upper_limit']
            # 相対湿度下限値
            self.relative_humidity_lower_limit_schedule = d_room['schedule']['relative_humidity_lower_limit']
        # 住宅の場合
        else:
            # PMV上限値
            if 'pmv_upper_limit' in d_room['schedule']:
                self.pmv_upper_limit_schedule = d_room['schedule']['pmv_upper_limit']
            # PMV下限値
            if 'pmv_lower_limit' in d_room['schedule']:
                self.pmv_lower_limit_schedule = d_room['schedule']['pmv_lower_limit']
        # 内部発熱の初期化
        # 機器顕熱
        self.heat_generation_appliances_schedule = d_room['schedule']['heat_generation_appliances']
        # 調理顕熱
        self.heat_generation_cooking_schedule = d_room['schedule']['heat_generation_cooking']
        # 調理潜熱
        self.vapor_generation_cooking_schedule = d_room['schedule']['vapor_generation_cooking']
        
        # 照明
        self.heat_generation_lighting_schedule = d_room['schedule']['heat_generation_lighting']
        # 人体顕熱
        self.number_of_people_schedule = d_room['schedule']['number_of_people']

        # 局所換気
        self.local_vent_amount_schedule = d_room['schedule']['local_vent_amount']
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
        
        # 透過日射熱取得の計算
        self.Qgt = summarize_transparent_solar_radiation(self.input_surfaces, Gdata, weather)
        
        # 部位の集約
        self.input_surfaces = summarize_building_part(self.input_surfaces)

        # print("集約後")
        # for surface in self.input_surfaces:
            # print('name=', surface.name, 'area=', surface.area, 'group=', surface.group_number)
        
        # 部位のグループ化
        # self.surfaces = []
        # for group in range(group_number):
        #     for surface in self.input_surfaces:

        # グループ化の結果の表示
        # for surface in self.input_surfaces:
        #     print(surface.boundary_type, surface.is_grouping, surface.group_number)

            
        # 部位の人体に対する形態係数の計算
        total_Aex_floor = 0.0
        total_A_floor = 0.0
        # 設定合計値もチェック
        total_Fot = 0.0
        # 床と床以外の合計面積を計算
        for surface in self.input_surfaces:
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
        for surface in self.input_surfaces:
            # 下向き部位（床）
            if surface.is_solar_absorbed_inside:
                surface.fot = surface.area / total_A_floor * fot_floor
            # 床以外
            else:
                surface.fot = surface.area / total_Aex_floor * fot_exfloor
            total_Fot += surface.fot
            # print(surface.name, surface.fot)

        if abs(total_Fot - 1.0) > 0.001:
            print(self.name, 'total_Fot=', total_Fot)

        self.Nsurf = len(self.input_surfaces)

        # 面対面の形態係数の計算
        self.Atotal = 0.0
        self.__TotalAF = 0.0

        # print('合計面積1=', self.Atotal)
        # 合計面積の計算
        for surface in self.input_surfaces:
            self.Atotal += surface.area
            # 合計床面積の計算
            if surface.is_solar_absorbed_inside == True:
                self.__TotalAF += surface.area
        
        # 放射暖房の発熱部位の設定（とりあえず床発熱）
        if Gdata.is_residential:
            if self.is_radiative_heating:
                for surface in self.input_surfaces:
                    if surface.is_solar_absorbed_inside:
                        surface.flr = surface.area / self.__TotalAF

        # 定格冷房能力[W]の計算（除湿量計算用）
        self.__qrtd_c = 190.5 * self.__TotalAF + 45.6
        # 冷房最大能力[W]の計算
        self.__qmax_c = 0.8462 * self.__qrtd_c + 1205.9
        # 冷房最小能力[W]の計算（とりあえず500Wで固定）
        self.__qmin_c = 500.0
        # 最大風量[m3/min]、最小風量[m3/min]の計算
        self.__Vmax = 11.076 * (self.__qrtd_c / 1000.0) ** 0.3432
        self.__Vmin = self.__Vmax * 0.55

        # 面積比の計算
        # 面積比の最大値も同時に計算（ニュートン法の初期値計算用）
        max_a = 0.0
        for surface in self.input_surfaces:
            surface.a = surface.area / self.Atotal
            max_a = max(max_a, surface.a)
        
        # 室のパラメータの計算（ニュートン法）
        # 初期値を設定
        fbd = max_a * 4.0 + 1.e-4
        # 収束判定
        isConverge = False
        for i in range(50):
            L = -1.0
            Ld = 0.0
            for surface in self.input_surfaces:
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
            print(self.name, '形態係数パラメータが収束しませんでした。')
        # print('合計表面積=', self.Atotal)
        # 形態係数の計算（永田の方式）
        # 総和のチェック
        TotalFF = 0.0
        for surface in self.input_surfaces:
            FF = 0.5 * (1.0 - math.sqrt(1.0 - 4.0 * surface.a / fb))
            TotalFF += FF
            # 形態係数の設定（面の微小球に対する形態係数）
            surface.FF = FF
        
        # 室内側表面熱伝達率の計算
        for surface in self.input_surfaces:
            surface.hir = surface.Ei / (1.0 - surface.Ei * surface.FF) \
                    * 4.0 * Sgm * (20.0 + 273.15) ** 3.0
            # surface.hir = 5.0
            surface.hic = max(0.0, surface.hi - surface.hir)
            # print(surface.name, surface.hic, surface.hir, surface.hi)
        
        # 平均放射温度計算のための各部位の比率計算
        total_area_hir = 0.0
        for surface in self.input_surfaces:
            total_area_hir += surface.area * surface.hir
        for surface in self.input_surfaces:
            if total_area_hir > 0.0:
                surface.Fmrt = surface.area * surface.hir / total_area_hir
            else:
                # テスト用（室内放射計算をキャンセルしたときの対応）
                surface.Fmrt = surface.a

        # print(TotalFF)
        # 透過日射の室内部位表面吸収比率の計算
        # 50%を床、50%を家具に吸収させる
        # 床が複数の部位の場合は面積比で案分する
        FsolFlr = 0.5
        # FsolFlr = 1.0
        # 家具の吸収比率で初期化
        TotalR = self.rsolfun

        for surface in self.input_surfaces:
            SolR = 0.0
            # 床の室内部位表面吸収比率の設定
            if surface.is_solar_absorbed_inside == True:
                SolR = FsolFlr * surface.area / self.__TotalAF
            surface.SolR = SolR
            # 室内部位表面吸収比率の合計値（チェック用）
            TotalR += SolR
        # 日射吸収率の合計値のチェック
        if abs(TotalR - 1.0) > 0.00001:
            print(self.name, '日射吸収比率合計値エラー', TotalR)
            print("残りは家具に吸収させます")
            self.rsolfun += max(1.0 - TotalR, 0)

        # 放射収支計算のための行列準備
        # 行列の準備と初期化
        # [AX]
        self.__matAXd = [[0.0 for i in range(self.Nsurf)] for j in range(self.Nsurf)]
        # {FIA}
        self.__matFIA = [[0.0 for i in range(1)] for j in range(self.Nsurf)]
        # {CRX}
        self.matCRX = [[0.0 for i in range(1)] for j in range(self.Nsurf)]
        # {CVL}
        self.matCVL = [[0.0 for i in range(1)] for j in range(self.Nsurf)]
        # {FLB}
        self.__matFLB = [[0.0 for i in range(1)] for j in range(self.Nsurf)]
        # {WSC}
        self.matWSC = [[0.0 for i in range(1)] for j in range(self.Nsurf)]
        # {WSR}
        # self.matWSR = [ [ 0.0 for i in range(1) ] for j in range(self.Nsurf) ]
        # {WSV}
        self.matWSV = [[0.0 for i in range(1)] for j in range(self.Nsurf)]
        # {WSB}
        # self.matWSB = [ [ 0.0 for i in range(1) ] for j in range(self.Nsurf) ]

        # print('FIA[len]=', len(self.__matFIA))
        i = 0
        for surface in self.input_surfaces:
            # matFIAの作成
            self.__matFIA[i] = surface.RFA0 * surface.hic
            # print('i=', i, 'FIA=', self.__matFIA[i])
            # FLB=φA0×flr×(1-Beta)
            self.__matFLB[i] = surface.RFA0 * surface.flr * (1. - self.Beta) / surface.area

            # 放射計算のマトリックス作成
            j = 0
            for nxtsurface in self.input_surfaces:
                # print('i=', i, 'j=', j)
                # print('FIA=', self.__matFIA[0][i])
                # print('FF=', surface.FF(j))
                # 対角要素
                if i == j:
                    self.__matAXd[i][j] = 1. + surface.RFA0 * surface.hi \
                                          - surface.RFA0 * surface.hir * nxtsurface.Fmrt
                # 対角要素以外
                else:
                    self.__matAXd[i][j] = - surface.RFA0 * surface.hir * nxtsurface.Fmrt
                j += 1
            # print('放射計算マトリックス作成完了')
            i += 1

        # print('[Matrix AXd]')
        # print(self.__matAXd)

        # 逆行列の計算
        self.matAX = np.linalg.inv(self.__matAXd)
        # print('[Matrix AX  inverse Matrix AXd]')
        # print(self.matAX)
        # {WSR}の計算
        self.matWSR = np.dot(self.matAX, self.__matFIA)
        # print('[Matrix FIA]')
        # print(self.__matFIA)
        # print('[Matrix WSR]')
        # print(self.matWSR)
        # {WSB}の計算
        self.matWSB = np.dot(self.matAX, self.__matFLB)
        # print('[Matrix FLB]')
        # print(self.__matFLB)
        # print('[Matrix WSB]')
        # print(self.matWSB)

    # 室温、熱負荷の計算
    def calcHload(self, Gdata, spaces, dtmNow, defSolpos, Weather):
        # 室間換気の風上室温をアップデート
        for roomvent in self.RoomtoRoomVent:
            windward_roomname = roomvent.windward_roomname
            oldTr = spaces[windward_roomname].oldTr
            oldxr = spaces[windward_roomname].oldxr
            roomvent.update_oldstate(oldTr, oldxr)

        # 外皮の傾斜面日射量の計算
        Idn = WeaData(Weather, enmWeatherComponent.Idn, dtmNow)
        Isky = WeaData(Weather, enmWeatherComponent.Isky, dtmNow)
        # print(Idn, Isky)
        for surface in self.input_surfaces:
            if surface.is_sun_striked_outside:
                surface.Id, surface.Isky, surface.Ir, surface.Iw = calc_slope_sol(surface, defSolpos, Idn, Isky)

        """ # 庇の日影面積率計算
        for surface in self.input_surfaces:
            # 庇がある場合のみ
            if surface.is_sun_striked_outside and surface.sunbrk.existance:
                # 日影面積率の計算
                surface.Fsdw = surface.calc_Fsdw(defSolpos)
                # print(surface.Fsdw)

        # 透過日射熱取得の計算
        self.Qgt = 0.0
        for surface in self.input_surfaces:
            if surface.boundary_type == "external_transparent_part" and surface.is_sun_striked_outside:
                # print('name=', surface.name)
                surface.Qgt = surface.calc_Qgt()
                self.Qgt += surface.Qgt
                # print("name=", surface.name, "QGT=", surface.Qgt) """

        # 相当外気温度の計算
        Ta = WeaData(Weather, enmWeatherComponent.Ta, dtmNow)
        RN = WeaData(Weather, enmWeatherComponent.RN, dtmNow)
        for surface in self.input_surfaces:
            calcTeo(surface, Ta, RN, self.oldTr, Weather.AnnualTave, spaces)
            # print(surface.name, Ta, RN, self.oldTr, surface.Teo)

        # 内部発熱の計算（すべて対流成分とする）
        # スケジュールのリスト番号の計算
        item = (get_nday(dtmNow.month, dtmNow.day) - 1) * 24 + dtmNow.hour
        # 機器顕熱[W]
        self.heat_generation_appliances = self.heat_generation_appliances_schedule[item]
        # 調理顕熱[W]
        self.heat_generation_cooking = self.heat_generation_cooking_schedule[item]
        # 調理潜熱[g/h]
        self.vapor_generation_cooking = self.vapor_generation_cooking_schedule[item]
        # 照明発熱[W]
        self.heat_generation_lighting = self.heat_generation_lighting_schedule[item]
        # 在室人員[人]
        self.number_of_people = self.number_of_people_schedule[item]
        # 人体顕熱[W]
        self.Humans = self.number_of_people \
                       * (63.0 - 4.0 * (self.oldTr - 24.0))
        # 人体潜熱[W]
        self.Humanl = max(self.number_of_people * 119.0 - self.Humans, 0.0)
        self.Hn = self.heat_generation_appliances + self.heat_generation_lighting + self.Humans + self.heat_generation_cooking

        # 内部発湿[kg/s]
        self.Lin = self.vapor_generation_cooking / 1000.0 / 3600.0 + self.Humanl / conra
        # print(self.name, self.heat_generation_appliances, self.heat_generation_lighting, self.Humans)

        # 室内表面の吸収日射量
        sequence_number = int((get_nday(dtmNow.month, dtmNow.day) - 1) * 24 * 4 + dtmNow.hour * 4 + float(dtmNow.minute) / 60.0 * 3600 / Gdata.DTime)
        for surface in self.input_surfaces:
            surface.RSsol = calc_RSsol(surface, self.Qgt[sequence_number])
        # 家具の吸収日射量
        self.Qsolfun = self.Qgt[sequence_number] * self.rsolfun

        # 流入外気風量の計算
        # 計画換気・すきま風量
        # season = Schedule.Season(dtmNow)
        self.Ventset = self.Vent

        # すきま風量未実装につき、とりあえず０とする
        self.Infset = 0.0
        # self.Infset = self.Inf
        # 局所換気量
        self.LocalVentset = self.local_vent_amount_schedule[item]

        # 空調設定温度の取得
        # Tset = Schedule.ACSet(self.name, '温度', dtmNow)
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

        # 室温・熱負荷計算のための係数の計算
        # BRM・BRLの初期化
        self.BRM = 0.0
        self.BRL = self.Beta
        RMdT = self.Hcap / Gdata.DTime
        self.BRM += RMdT
        # BRLの計算
        i = 0
        for surface in self.input_surfaces:
            # 室内対流熱伝達率×面積[W/K]
            AF0 = surface.area * surface.hic
            temp = AF0 * (1.0 - self.matWSR[i])
            # hc×A×(1-WSR)の積算
            self.BRM += temp
            # BRLの計算
            self.BRL += AF0 * self.matWSB[i]
            i += 1

        # 外気導入項の計算
        temp = conca * conrowa * \
               (self.Ventset + self.Infset + self.LocalVentset) / 3600.0
        self.BRM += temp
        # 室間換気
        for room_vent in self.RoomtoRoomVent:
            nextvent = room_vent.volume
            temp = conca * conrowa * nextvent / 3600.0
            self.BRM += temp

        # 家具からの熱取得
        if self.Capfun > 0.0:
            self.BRM += 1. / (Gdata.DTime / self.Capfun + 1. / self.Cfun)

        # 定数項の計算
        self.BRC = 0.0
        # {WSC}、{CRX}の初期化
        self.matWSC = [0.0 for j in range(self.Nsurf)]
        self.matCRX = [0.0 for j in range(self.Nsurf)]

        # {CRX}の作成
        i = 0
        for surface in self.input_surfaces:
            self.matCRX[i] = surface.RFT0 * surface.Teo \
                                  + surface.RSsol * surface.RFA0
            i += 1

        # print('matCRX')
        # print(self.matCRX)
        # {WSC}=[XA]*{CRX}
        self.matWSC = np.dot(self.matAX, self.matCRX)
        
        # print('matWSC')
        # print(self.matWSC)
        # {BRC}の計算
        i = 0
        for surface in self.input_surfaces:
            NowQw = self.matWSC[i] * surface.area * surface.hic
            self.BRC += NowQw
            i += 1

        # 外気流入風（換気＋すきま風）
        temp = conca * conrowa * \
               (self.Ventset + self.Infset + self.LocalVentset) \
               * WeaData(Weather, enmWeatherComponent.Ta, dtmNow) / 3600.0
        self.BRC += temp

        # 室間換気流入風
        for room_vent in self.RoomtoRoomVent:
            nextvent = room_vent.volume
            temp = conca * conrowa * nextvent \
                   * room_vent.oldTr / 3600.0
            # print(self.name, room_vent.Windward_roomname(), nextvent, room_vent.oldTr())
            self.BRC += temp
        # RM/Δt*oldTrの項
        temp = self.Hcap / Gdata.DTime * self.oldTr
        self.BRC += temp

        # 家具からの熱取得の項
        if self.Capfun > 0.0:
            self.BRC += (self.Capfun / Gdata.DTime * self.oldTfun + self.Qsolfun) \
                    / (self.Capfun / (Gdata.DTime * self.Cfun) + 1.)

        # {WSV}、{CVL}の初期化
        self.matWSV = [0.0 for j in range(self.Nsurf)]
        self.matCVL = [0.0 for j in range(self.Nsurf)]

        # 畳み込み演算
        i = 0
        for surface in self.input_surfaces:
            self.matCVL[i] = convolution(surface)
            i += 1

        # {WSV}=[XA]*{CVL}
        self.matWSV = np.dot(self.matAX, self.matCVL)
        # 畳み込み後の室内表面温度の計算
        i = 0
        for surface in self.input_surfaces:
            temp = surface.area * surface.hic * self.matWSV[i]

            self.BRC += temp
            i += 1

        # 定数項への内部発熱の加算
        self.BRC += self.Hn

        # 窓開閉、空調発停判定のための自然室温計算
        # 通風なしでの係数を控えておく
        self.BRMnoncv = self.BRM
        self.BRCnoncv = self.BRC
        if self.nowWin == 1:
            temp = conca * conrowa * self.Vcrossvent / 3600.0
            self.BRM += temp
            self.BRC += temp * Ta

        # OT計算用の係数補正
        self.Xot = 0.0
        self.XLr = 0.0
        self.XC = 0.0
        temp = 0.0
        XLr = 0.0
        XC = 0.0
        i = 0
        for surface in self.input_surfaces:
            temp += (surface.fot * self.matWSR[i])
            XLr += surface.fot * self.matWSB[i]
            XC += surface.fot * (self.matWSC[i] + self.matWSV[i])
            i += 1

        temp = self.kc + self.kr * temp
        self.Xot = 1.0 / temp
        self.XLr = self.kr * XLr / temp
        self.XC = self.kr * XC / temp
        self.BRMot = self.BRM * self.Xot
        self.BRCot = self.BRC + self.BRM * self.XC
        self.BRLot = self.BRL + self.BRM * self.XLr
        # 自然室温でOTを計算する
        is_radiative_heating = False
        if Gdata.is_residential:
            is_radiative_heating = self.is_radiative_heating
        
        # 自然作用温度の計算（住宅用）
        if Gdata.is_residential:
            self.OT, self.Lcs, self.Lrs = self.calcTrLs(0, is_radiative_heating, self.BRCot, self.BRMot,
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
            self.Xot = 0.0
            self.XLr = 0.0
            self.XC = 0.0
            temp = 0.0
            XLr = 0.0
            XC = 0.0
            i = 0
            for surface in self.input_surfaces:
                temp += (surface.fot * self.matWSR[i])
                XLr += surface.fot * self.matWSB[i]
                XC += surface.fot * (self.matWSC[i] + self.matWSV[i])
                i += 1

            temp = self.kc + self.kr * temp
            self.Xot = 1.0 / temp
            self.XLr = self.kr * XLr / temp
            self.XC = self.kr * XC / temp
            self.BRMot = self.BRM * self.Xot
            self.BRCot = self.BRC + self.BRM * self.XC
            self.BRLot = self.BRL + self.BRM * self.XLr
            
            # 設定温度の計算
            self.OTset, self.Met, self.Clo, self.Vel = calcOTset(self.nowAC, self.is_radiative_heating, self.RH)

            # 仮の室温、熱負荷の計算
            self.OT, self.Lcs, self.Lrs = self.calcTrLs(self.nowAC,
                                                            self.is_radiative_heating, self.BRCot, self.BRMot,
                                                            self.BRLot, 0, self.OTset)
            # 室温を計算
            self.Tr = self.Xot * self.OT - self.XLr * self.Lrs - self.XC

            # 最終的な運転フラグの設定（空調時のみ）
            self.finalAC = reset_SW(self.nowAC, self.Lcs, self.Lrs, self.is_radiative_heating, self.radiative_heating_max_capacity)

            # 最終室温・熱負荷の再計算
            self.OT, self.Lcs, self.Lrs = self.calcTrLs(self.finalAC,
                                                            self.is_radiative_heating, self.BRCot, self.BRMot,
                                                            self.BRLot, self.radiative_heating_max_capacity, self.OTset)
            # 室温を計算
            self.Tr = self.Xot * self.OT \
                        - self.XLr * self.Lrs - self.XC
        # 自然室温の計算（非住宅用）
        else:
            self.Tr, self.Lcs, self.Lrs = self.calcTrLs(0, is_radiative_heating, self.BRC, self.BRM,
                                                        self.BRL, 0, 0.0)
            # 空調停止で初期化
            self.finalAC = 0
            # 窓閉鎖
            self.nowWin = 0
            # 設定温度
            temp_set = 0.0
            # 上限温度を超える場合は冷房
            if self.is_upper_temp_limit_set_schedule[item] and self.Tr > self.temperature_upper_limit_schedule[item]:
                self.finalAC = -1
                temp_set = self.temperature_upper_limit_schedule[item]
            # 下限温度を下回る場合は暖房
            elif self.is_lower_temp_limit_set_schedule[item] and self.Tr < self.temperature_lower_limit_schedule[item]:
                self.finalAC = 1
                temp_set = self.temperature_lower_limit_schedule[item]
            # print("item=", item, "Tr=", self.Tr, "finalAC=", self.finalAC, "temp_set=", temp_set, \
            #     self.is_upper_temp_limit_set[item], self.temperature_upper_limit[item])
            # 室温、熱負荷の計算
            self.Tr, self.Lcs, self.Lrs = self.calcTrLs(self.finalAC, is_radiative_heating, self.BRC, self.BRM, \
                self.BRL, 0, temp_set)

        # 表面温度の計算
        self.MRT = 0.0
        self.AST = 0.0
        i = 0
        for surface in self.input_surfaces:
            Ts = self.matWSR[i] * self.Tr \
                 + self.matWSC[i] + self.matWSV[i] \
                 + self.matWSB[i] * self.Lrs
            surface.Ts = Ts

            # 人体に対する放射温度：MRT、面積荷重平均温度：ASTの計算
            self.MRT += surface.fot * surface.Ts
            self.AST += surface.area * surface.Ts / self.Atotal
            i += 1
        # 非住宅の場合の作用温度を計算する
        self.OT = self.kc * self.Tr + self.kr * self.MRT

        # 室内側等価温度の計算
        for surface in self.input_surfaces:
            surface.Tsx = 0.0

            j = 0
            # 形態係数加重平均表面温度の計算
            for nxtsurface in self.input_surfaces:
                surface.Tsx += nxtsurface.Ts * nxtsurface.Fmrt
                j += 1

            # 室内側等価温度の計算
            surface.Tei = calc_Tei(surface, self.Tr, surface.Tsx, self.Lrs, self.Beta)
            # 室内表面熱流の計算
            update_qi(surface, self.Tr, surface.Tsx, self.Lrs, self.Beta)

        # 湿度の計算
        xo = WeaData(Weather, enmWeatherComponent.x, dtmNow) / 1000.
        self.Voin = (self.Ventset + self.Infset + self.LocalVentset) / 3600.
        Ff = self.Gf * self.Cx / (self.Gf + Gdata.DTime * self.Cx)
        Vd = self.volume / Gdata.DTime
        self.BRMX = conrowa * (Vd + self.Voin) + Ff
        self.BRXC = conrowa * (self.volume / Gdata.DTime * self.oldxr + self.Voin * xo) \
                + Ff * self.oldxf + self.Lin
        
        # if self.name == '主たる居室':
        #     print(self.Voin, Ff, Vd)
        # 室間換気流入風
        for room_vent in self.RoomtoRoomVent:
            nextvent = room_vent.volume
            self.BRMX += conrowa * nextvent / 3600.0
            self.BRXC += conrowa * nextvent * room_vent.oldxr / 3600.0
        
        # 住宅の場合
        if Gdata.is_residential:
            # 空調の熱交換部飽和絶対湿度の計算
            self.calcVac_xeout(self.nowAC)
            # 空調機除湿の項
            RhoVac = conrowa * self.Vac * (1.0 - self.bypass_factor_rac)
            self.BRMX += RhoVac
            self.BRXC += RhoVac * self.xeout
            # 室絶対湿度[kg/kg(DA)]の計算
            self.xr = self.BRXC / self.BRMX
            # 加湿量の計算
            self.Ghum = RhoVac * (self.xeout - self.xr)
            if self.Ghum > 0.0:
                self.Ghum = 0.0
                # 空調機除湿の項の再計算（除湿なしで計算）
                self.BRMX -= RhoVac
                self.BRXC -= RhoVac * self.xeout
                self.Va = 0.0
                # 室絶対湿度の計算
                self.xr = self.BRXC / self.BRMX
            # 潜熱負荷の計算
            self.Lcl = self.Ghum * conra
            # 当面は放射空調の潜熱は0
            self.Lrl = 0.0
            # 室相対湿度の計算
            self.RH = rhtx(self.Tr, self.xr)
        # 非住宅の場合
        else:
            # 自然湿度の計算
            # 室絶対湿度[kg/kg(DA)]の計算
            self.xr = self.BRXC / self.BRMX
            # 相対湿度の計算
            self.RH = rhtx(self.Tr, self.xr)
            # 潜熱計算運転状態
            self.nowACx = 0
            # 潜熱負荷の初期化
            self.Lcl = 0.0
            # 上限湿度を超える場合は除湿
            if self.is_upper_humidity_limit_set_schedule[item] and self.RH > self.relative_humidity_upper_limit_schedule[item]:
                self.nowACx = -1
                RH_set = self.relative_humidity_upper_limit_schedule[item]
                
            # 下限湿度を下回る場合は加湿
            elif self.is_lower_humidity_limit_set_schedule[item] and self.RH < self.relative_humidity_lower_limit_schedule[item]:
                self.nowACx = 1
                RH_set = self.relative_humidity_lower_limit_schedule[item]

            # 設定絶対湿度の計算（潜熱運転のときだけ）
            if self.nowACx != 0:
                self.xr = xtrh(self.Tr, RH_set)
                self.RH = RH_set
                self.Lcl = - conra * (self.BRXC - self.BRMX * self.xr)

        # 家具の温度を計算
        self.Tfun = self.calcTfun(Gdata)
        self.xf = self.calcxf(Gdata)

        # 年間熱負荷の積算
        # 助走計算以外の時だけ積算
        if FlgOrig(Gdata, dtmNow) == True:
            # 対流式空調（顕熱）の積算
            if self.Lcs > 0.0:
                self.AnnualLoadcHs += self.Lcs * Gdata.DTime * 0.000000001
            else:
                self.AnnualLoadcCs += self.Lcs * Gdata.DTime * 0.000000001
            
            # 当面未処理負荷は0
            self.un_Lcs = 0.0
            # 対流式空調（顕熱未処理）の積算
            if self.un_Lcs > 0.0:
                self.Annual_un_LoadcHs += self.un_Lcs * Gdata.DTime * 0.000000001
            else:
                self.Annual_un_LoadcCs += self.un_Lcs * Gdata.DTime * 0.000000001
            
            # 対流式空調（潜熱）の積算
            if self.Lcl > 0.0:
                self.AnnualLoadcHl += self.Lcl * Gdata.DTime * 0.000000001
            else:
                self.AnnualLoadcCs += self.Lcl * Gdata.DTime * 0.000000001

            # 放射式空調（顕熱）の積算
            if self.Lrs > 0.0:
                self.AnnualLoadrHs += self.Lrs * Gdata.DTime * 0.000000001
            else:
                self.AnnualLoadrCs += self.Lrs * Gdata.DTime * 0.000000001

            # 放射式空調（潜熱）の積算
            if self.Lrl > 0.0:
                self.AnnualLoadrHl += self.Lrl * Gdata.DTime * 0.000000001
            else:
                self.AnnualLoadrCl += self.Lrl * Gdata.DTime * 0.000000001

        # PMVの計算
        self.PMV = calcPMV(self.Tr, self.MRT, self.RH, self.Vel, self.Met, self.Wme, self.Clo)

        # 当該時刻の空調状態、窓開閉状態を控える
        self.preAC = self.nowAC
        self.preWin = self.nowWin

        return 0

    # 前時刻の室温を現在時刻の室温、家具温度に置換
    def update_oldstate(self):
        self.oldTr = self.Tr
        self.oldTfun = self.Tfun
        self.oldxr = self.xr
        self.oldxf = self.xf

    # 室温・熱負荷の計算ルーティン
    def calcTrLs(self, nowAC, is_radiative_heating, BRC, BRM, BRL, Lrcap, Tset):
        Lcs = 0.0
        Lrs = 0.0
        Tr = 0.0
        # 非空調時の計算
        if nowAC == 0:
            Tr = BRC / BRM
        # 熱負荷計算（最大能力無制限）
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

    # 平均放射温度の計算
    def update_Tsx(self):
        self.__Tsx = 0.0
        i = 0
        for surface in self.input_surfaces:
            self.__Tsx += surface.Ts.Ts() * surface.FF(i)
            i += 1

    # 表面温度の出力
    def surftemp_print(self):
        for surface in self.input_surfaces:
            print('{0:.2f}'.format(surface.Ts()), "", end="")

    # 家具の温度を計算する
    def calcTfun(self, Gdata):
        if self.Capfun > 0.0:
            self.Tfun = ((self.Capfun / Gdata.DTime * self.oldTfun \
                    + self.Cfun * self.Tr + self.Qsolfun) \
                    / (self.Capfun / Gdata.DTime + self.Cfun))
            self.Qfuns = self.Cfun * (self.Tr - self.Tfun)
        # if self.name == "主たる居室":
        #     print(self.name, self.oldTfun, self.Tfun, self.Capfun, self.Cfun, self.Qsolfun)
        return self.Tfun

    # 家具類の湿度を計算する
    def calcxf(self, Gdata):
        self.xf = (self.Gf / Gdata.DTime * self.oldxf + self.Cx * self.xr) / (self.Gf / Gdata.DTime + self.Cx)
        self.Qfunl = self.Cx * (self.xr - self.xf)
        # if self.name == "主たる居室":
        #     print(self.name, self.oldTfun, self.Tfun, self.Capfun, self.Cfun, self.Qsolfun)
        return self.xf

    # エアコンの熱交換部飽和絶対湿度の計算
    def calcVac_xeout(self, nowAC):
        # Lcsは加熱が正
        # 加熱時は除湿ゼロ
        Qs = - self.Lcs
        if nowAC == 0 or Qs <= 1.0e-3:
            self.Vac = 0.0
            self.Ghum = 0.0
            self.Lcl = 0.0
            return
        else:
            # 風量[m3/s]の計算（線形補間）
            self.Vac = (self.__Vmin + (self.__Vmax - self.__Vmin) \
                    / (self.__qmax_c - self.__qmin_c) * (Qs - self.__qmin_c)) / 60.0
            # 熱交換器温度＝熱交換器部分吹出温度
            self.__Teout = self.Tr - Qs / (conca * conrowa * self.Vac * (1.0 - self.bypass_factor_rac))
            # 熱交換器吹出部分は飽和状態
            self.xeout = x(Pws(self.__Teout))

    # 暖房設備仕様の読み込み
    def heating_equipment_read(self, dheqp):
        # 放射暖房有無（Trueなら放射暖房あり）
        self.is_radiative_heating = dheqp['is_radiative_heating']
        # 放射暖房最大能力[W]
        self.radiative_heating_max_capacity = 0.0
        if self.is_radiative_heating:
            self.radiative_heating_max_capacity = dheqp['radiative_heating']['max_capacity'] * dheqp['radiative_heating']['area']

    # 冷房設備仕様の読み込み
    def cooling_equipment_read(self, dceqp):
        # 放射冷房有無（Trueなら放射冷房あり）
        self.__is_radiative_cooling = dceqp['is_radiative_cooling']
        # 放射冷房最大能力[W]
        self.__radiative_cooling_max_capacity = 0.0
        if self.__is_radiative_cooling:
            self.__radiative_cooling_max_capacity = dceqp['radiative_cooling']['max_capacity'] * dceqp['radiative_cooling']['area']
        # 対流式の場合
        else:
            # 熱交換器種類
            self.__heat_exchanger_type = dceqp['convective_cooling']['heat_exchanger_type']
            # 定格冷房能力[W]
            self.__convective_cooling_rtd_capacity = dceqp['convective_cooling']['max_capacity']

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
            Idn = WeaData(weather, enmWeatherComponent.Idn, dtmNow)
            Isky = WeaData(weather, enmWeatherComponent.Isky, dtmNow)
            for surface in surfaces:
                # 外表面に日射が当たる場合
                if surface.is_sun_striked_outside and surface.boundary_type == "external_transparent_part":
                    surface.Id, surface.Isky, surface.Ir, surface.Iw = calc_slope_sol(surface, solar_position, Idn, Isky)

                    # 日除けの日影面積率の計算
                    if surface.sunbrk.existance:
                        surface.Fsdw = calc_Fsdw(surface, solar_position)
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