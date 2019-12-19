import numpy as np
from typing import List
from Weather import enmWeatherComponent
import math
import Surface
from Surface import Surface
import NextVent
from NextVent import NextVent
from Psychrometrics import Pws, x, xtrh, rhtx
from common import conca, conrowa, Sgm, conra, \
    funiture_sensible_capacity, funiture_latent_capacity, bypass_factor_rac, get_nday
from PMV import calcPMV, calcOTset
from Win_ACselect import reset_SW, mode_select

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
# - __is_radiative_heating:       放射暖房対象室フラグ, True
# - Betat:         放射暖房対流比率, －
# - RoomtoRoomVents:      室間換気量（list型、暖房・中間期・冷房、風上室名称）, m3/h
# - d:             室内部位に関連するクラス, Surface

# 空間に関する情報の保持
class Space:
    FsolFlr = 0.5  # 床の日射吸収比率

    # 初期化
    def __init__(self, Gdata, d_room):
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
        :param __is_radiative_heating:
        :param Beta:
        :param RoomtoRoomVents:
        :param input_surfaces:
        """
        self.name = d_room['name']                  # 室名称
        if Gdata.is_residential:
            self.__room_type = d_room['room_type']      # 室用途（1:主たる居室、2:その他居室、3:非居室）
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
        self.__oldTr = 15.0                         # 前時刻の室温の初期化
        self.Tfun = 15.0                            # 家具の温度[℃]
        self.__oldTfun = 15.0                       # 前時刻の家具の温度[℃]
        self.__rsolfun = 0.5                        # 透過日射の内家具が吸収する割合[－]
        # self.__rsolfun = 0.0
        self.__kc = 0.5                             # 人体表面の熱伝達率の対流成分比率
        self.__kr = 0.5                             # 人体表面の熱伝達率の放射成分比率
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
            self.__heating_equipment_read(d_room['heating_equipment'])
                                                    # 暖房設備仕様の読み込み
            self.__cooling_equipment_read(d_room['cooling_equipment'])
        
        self.__volume = d_room['volume']            # 室気積[m3]
        self.__Ga = self.__volume * conrowa         # 室空気の質量[kg]
        self.__Capfun = self.__volume * funiture_sensible_capacity * 1000.
                                                    # 家具熱容量[J/K]
        # self.__Capfun = 0.0
        self.__Cfun = 0.00022 * self.__Capfun       # 家具と空気間の熱コンダクタンス[W/K]
        self.__Gf = funiture_latent_capacity * self.__volume
                                                    # 家具類の湿気容量[kg]
        self.__Cx = 0.0018 * self.__Gf              # 室空気と家具類間の湿気コンダクタンス[kg/(s･kg/kg(DA))]
        self.xr = xtrh(20.0, 40.0)                  # 室の絶対湿度[kg/kg(DA)]
        self.__oldxr = self.xr                      # 室内絶対湿度の初期値
        self.xf = self.xr                           # 家具類の絶対湿度
        self.__oldxf = self.xr                      # 家具類の絶対湿度の初期値
        self.__BF = bypass_factor_rac               # バイパスファクター
        self.__xeout = 0.0                          # エアコン熱交換部の飽和絶対湿度[kg/kg(DA)]
        self.Vac = 0.0                              # エアコンの風量[m3/s]
        self.RH = 50.0                              # 室相対湿度[%]
        if Gdata.is_residential:
            self.__Vcrossvent = self.__volume * d_room['natural_vent_time']
                                                    # 窓開放時通風量
        # 室空気の熱容量
        self.__Hcap = self.__volume * conrowa * conca
        # print(self.__Hcap)
        self.__Vent = d_room['vent']                #計画換気量
        self.__Inf = 0.0                            #すきま風量（暫定値）
        self.__Beta = 0.0                           # 放射暖房対流比率

        # 空調スケジュールの読み込み
        # 設定温度／PMV上限値の設定
        if 'is_upper_temp_limit_set' in d_room['schedule']:
            self.__is_upper_temp_limit_set = d_room['schedule']['is_upper_temp_limit_set']
        # 設定温度／PMV下限値の設定
        if 'is_lower_temp_limit_set' in d_room['schedule']:
            self.__is_lower_temp_limit_set = d_room['schedule']['is_lower_temp_limit_set']
        # 非住宅の場合
        if not Gdata.is_residential:
            # 室温上限値
            self.__temperature_upper_limit = d_room['schedule']['temperature_upper_limit']
            # 室温下限値
            self.__temperature_lower_limit = d_room['schedule']['temperature_lower_limit']
            # 相対湿度上限値の設定
            self.__is_upper_humidity_limit_set = d_room['schedule']['is_upper_humidity_limit_set']
            # 相対湿度下限値の設定
            self.__is_lower_humidity_limit_set = d_room['schedule']['is_lower_humidity_limit_set']
            # 相対湿度上限値
            self.__relative_humidity_upper_limit = d_room['schedule']['relative_humidity_upper_limit']
            # 相対湿度下限値
            self.__relative_humidity_lower_limit = d_room['schedule']['relative_humidity_lower_limit']
        # 住宅の場合
        else:
            # PMV上限値
            if 'pmv_upper_limit' in d_room['schedule']:
                self.__pmv_upper_limit = d_room['schedule']['pmv_upper_limit']
            # PMV下限値
            if 'pmv_lower_limit' in d_room['schedule']:
                self.__pmv_lower_limit = d_room['schedule']['pmv_lower_limit']
        # 内部発熱の初期化
        # 機器顕熱
        self.__Appls_schedule = d_room['schedule']['heat_generation_appliances']
        # 調理顕熱
        self.__cooking_s_schedule = d_room['schedule']['heat_generation_cooking']
        # 調理潜熱
        self.__cooking_l_schedule = d_room['schedule']['vapor_generation_cooking']
        
        # 照明
        self.__Light_schedule = d_room['schedule']['heat_generation_lighting']
        # 人体顕熱
        self.__number_of_people_schedule = d_room['schedule']['number_of_people']

        # 局所換気
        self.__LocalVent_schedule = d_room['schedule']['local_vent_amount']
        # 内部発熱合計
        self.__Hn = 0.0

        # 室透過日射熱取得の初期化
        self.Qgt = 0.0

        # 室間換気量クラスの構築
        self.__RoomtoRoomVent = []
        # prevroomname = ''
        # winter_vent = 0.0
        # inter_vent = 0.0
        # summer_vent = 0.0
        if Gdata.is_residential:
            for room_vent in d_room['next_vent']:
                self.__RoomtoRoomVent.append(NextVent(room_vent['upstream_room_type'], room_vent['volume']))
        self.__Nsurf = 0  # 部位の数
        self.input_surfaces = []

        # 部位の読み込み
        for d_surface in d_room['boundaries']:
            # print(d_surface['name'])
            self.input_surfaces.append(Surface(d = d_surface, Gdata = Gdata))
        
        """         
        # 部位のグループ化
        group_number = 0
        for surface in self.input_surfaces:
            # 最初の部位は最も若いグループ番号にする
            if not surface.is_grouping:
                # グループ化済みにする
                surface.is_grouping = True
                surface.group_number = group_number

                # 同じ境界条件の部位を探す
                for comp_surface in self.input_surfaces:
                    # 境界条件が同じかどうかチェックする
                    # グループ化していない部位だけを対象とする
                    if not comp_surface.is_grouping:
                        if surface.boundary_comp(comp_surface):
                            comp_surface.is_grouping = True
                            comp_surface.group_number = group_number
                # グループ番号を増やす
                group_number += 1 """
        
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

        self.__Nsurf = len(self.input_surfaces)

        # 面対面の形態係数の計算
        self.__Atotal = 0.0
        self.__TotalAF = 0.0

        # print('合計面積1=', self.__Atotal)
        # 合計面積の計算
        for surface in self.input_surfaces:
            self.__Atotal += surface.area
            # 合計床面積の計算
            if surface.is_solar_absorbed_inside == True:
                self.__TotalAF += surface.area
        
        # 放射暖房の発熱部位の設定（とりあえず床発熱）
        if Gdata.is_residential:
            if self.__is_radiative_heating:
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
        
        for surface in self.input_surfaces:
            surface.a = surface.area / self.__Atotal

        # 面積比の計算
        # 面積比の最大値も同時に計算（ニュートン法の初期値計算用）
        # 初期値を設定
        m = 1.0e-5  # 式(99)
        n = 100.0
        m_n = (m + n) / 2.0
        
        # 収束判定
        isConverge = False
        for i in range(50):
            L_m = -1.0  # 式(96)の一部
            L_n = -1.0
            L_m_n = -1.0
            for surface in self.input_surfaces:
                L_m += self.get_L(surface.a, m)  # 式(96)の一部
                L_n += self.get_L(surface.a, n)
                L_m_n += self.get_L(surface.a, m_n)
            # print(i, 'm=', m, 'L_m=', L_m, 'n=', n, 'L_n=', L_n, 'm_n=', m_n, 'L_m_n=', L_m_n)
            # 収束判定
            if abs(L_m_n) < 1.e-4:  # 式(100)
                isConverge = True
                break

            if np.sign(L_m_n) == np.sign(L_m):
                m = m_n
            else:
                n = m_n
            m_n = (m + n) / 2.0
        fb = m_n
        
        # 収束しないときには警告を表示
        if not isConverge:
            print(self.name, '形態係数パラメータが収束しませんでした。')
        # print('合計表面積=', self.__Atotal)
        # 形態係数の計算（永田の方式）
        # 総和のチェック
        TotalFF = 0.0
        for surface in self.input_surfaces:
            FF = 0.5 * (1.0 - np.sign(1.0 - 4.0 * surface.a / fb) * np.sqrt(abs(1.0 - 4.0 * surface.a / fb)))
            TotalFF += FF
            # print(self.name, surface.name, FF)
            surface.setFF(FF)
            # surface.setFF(surface.a)
        
        # 室内側表面熱伝達率の計算
        for surface in self.input_surfaces:
            surface.hir = surface.Ei / (1.0 - surface.Ei * surface.FF()) \
                    * 4.0 * Sgm * (20.0 + 273.15) ** 3.0
            # surface.hir = 5.0
            surface.hic = max(0.0, surface.hi - surface.hir)
            # print(surface.name, surface.hic, surface.hir, surface.hi)
            # surface.hir = 4.5 / 0.86
            # surface.hic = surface.hi - surface.hir
        
        # 平均放射温度計算のための各部位の比率計算
        total_area_hir = 0.0
        for surface in self.input_surfaces:
            total_area_hir += surface.area * surface.hir
        for surface in self.input_surfaces:
            surface.Fmrt = surface.area * surface.hir / total_area_hir

        # print(TotalFF)
        # 透過日射の室内部位表面吸収比率の計算
        # 50%を床、50%を家具に吸収させる
        # 床が複数の部位の場合は面積比で案分する
        FsolFlr = 0.5
        # FsolFlr = 1.0
        # 家具の吸収比率で初期化
        TotalR = self.__rsolfun

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
            self.__rsolfun += max(1.0 - TotalR, 0)

        # 放射収支計算のための行列準備
        # 行列の準備と初期化
        # [AX]
        self.__matAXd = [[0.0 for i in range(self.__Nsurf)] for j in range(self.__Nsurf)]
        # {FIA}
        self.__matFIA = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]
        # {CRX}
        self.__matCRX = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]
        # {CVL}
        self.__matCVL = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]
        # {FLB}
        self.__matFLB = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]
        # {WSC}
        self.__matWSC = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]
        # {WSR}
        # self.__matWSR = [ [ 0.0 for i in range(1) ] for j in range(self.__Nsurf) ]
        # {WSV}
        self.__matWSV = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]
        # {WSB}
        # self.__matWSB = [ [ 0.0 for i in range(1) ] for j in range(self.__Nsurf) ]

        # print('FIA[len]=', len(self.__matFIA))
        i = 0
        for surface in self.input_surfaces:
            # matFIAの作成
            self.__matFIA[i][0] = surface.RFA0 * surface.hic
            # print('i=', i, 'FIA=', self.__matFIA[i][0])
            # FLB=φA0×flr×(1-Beta)
            self.__matFLB[i][0] = surface.RFA0 * surface.flr * (1. - self.__Beta) / surface.area

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
        self.__matAX = np.linalg.inv(self.__matAXd)
        # print('[Matrix AX  inverse Matrix AXd]')
        # print(self.__matAX)
        # {WSR}の計算
        self.__matWSR = np.dot(self.__matAX, self.__matFIA)
        # print('[Matrix FIA]')
        # print(self.__matFIA)
        # print('[Matrix WSR]')
        # print(self.__matWSR)
        # {WSB}の計算
        self.__matWSB = np.dot(self.__matAX, self.__matFLB)
        # print('[Matrix FLB]')
        # print(self.__matFLB)
        # print('[Matrix WSB]')
        # print(self.__matWSB)

    # 前時刻の室温を返す
    @property
    def oldTr(self):
        return self.__oldTr
    # 前時刻の絶対湿度を返す
    @property
    def oldxr(self):
        return self.__oldxr
    
    def get_L(self, a: float, fbd: float) -> float:
        return 0.5 * (1.0 - np.sign(1.0 - 4.0 * a / fbd) * math.sqrt(abs(1.0 - 4.0 * a / fbd)))

    # 室温、熱負荷の計算
    def calcHload(self, Gdata, spaces, dtmNow, defSolpos, Weather):
        # 室間換気の風上室温をアップデート
        for roomvent in self.__RoomtoRoomVent:
            windward_roomname = roomvent.Windward_roomname
            oldTr = spaces[windward_roomname].oldTr
            oldxr = spaces[windward_roomname].oldxr
            roomvent.update_oldstate(oldTr, oldxr)

        # 外皮の傾斜面日射量の計算
        Idn = Weather.WeaData(enmWeatherComponent.Idn, dtmNow)
        Isky = Weather.WeaData(enmWeatherComponent.Isky, dtmNow)
        # print(Idn, Isky)
        for surface in self.input_surfaces:
            if surface.is_sun_striked_outside:
                surface.update_slope_sol(defSolpos, Idn, Isky)

        # 庇の日影面積率計算
        for surface in self.input_surfaces:
            # 庇がある場合のみ
            if surface.is_sun_striked_outside and surface.sunbrk.existance:
                # 日影面積率の計算
                surface.update_Fsdw(defSolpos)
                # print(surface.Fsdw)

        # 透過日射熱取得の計算
        self.Qgt = 0.0
        for surface in self.input_surfaces:
            if surface.boundary_type == "external_transparent_part" and surface.is_sun_striked_outside:
                # print('name=', surface.name)
                surface.update_Qgt_Qga()
                self.Qgt += surface.Qgt
                # print("name=", surface.name, "QGT=", surface.Qgt)

        # 相当外気温度の計算
        Ta = Weather.WeaData(enmWeatherComponent.Ta, dtmNow)
        RN = Weather.WeaData(enmWeatherComponent.RN, dtmNow)
        AnnualTave = Weather.AnnualTave()
        for surface in self.input_surfaces:
            surface.calcTeo(Ta, RN, self.__oldTr, AnnualTave, spaces)
            # print(surface.name, Ta, RN, self.__oldTr, surface.Teo)

        # 内部発熱の計算（すべて対流成分とする）
        # スケジュールのリスト番号の計算
        item = (get_nday(dtmNow.month, dtmNow.day) - 1) * 24 + dtmNow.hour
        # 機器顕熱[W]
        self.heat_generation_appliances = self.__Appls_schedule[item]
        # 調理顕熱[W]
        self.__heat_generation_cooking = self.__cooking_s_schedule[item]
        # 調理潜熱[g/h]
        self.__vapor_generation_cooking = self.__cooking_l_schedule[item]
        # 照明発熱[W]
        self.heat_generation_lighting = self.__Light_schedule[item]
        # 在室人員[人]
        self.__number_of_people = self.__number_of_people_schedule[item]
        # 人体顕熱[W]
        self.Humans = self.__number_of_people \
                       * (63.0 - 4.0 * (self.__oldTr - 24.0))
        # 人体潜熱[W]
        self.Humanl = max(self.__number_of_people * 119.0 - self.Humans, 0.0)
        self.__Hn = self.heat_generation_appliances + self.heat_generation_lighting + self.Humans + self.__heat_generation_cooking

        # 内部発湿[kg/s]
        self.Lin = self.__vapor_generation_cooking / 1000.0 / 3600.0 + self.Humanl / conra
        # print(self.name, self.heat_generation_appliances, self.heat_generation_lighting, self.Humans)

        # 室内表面の吸収日射量
        for surface in self.input_surfaces:
            surface.update_RSsol(self.Qgt)
        # 家具の吸収日射量
        self.Qsolfun = self.Qgt * self.__rsolfun

        # 流入外気風量の計算
        # 計画換気・すきま風量
        # season = Schedule.Season(dtmNow)
        self.__Ventset = self.__Vent

        # すきま風量未実装につき、とりあえず０とする
        self.__Infset = 0.0
        # self.__Infset = self.__Inf
        # 局所換気量
        self.__LocalVentset = self.__LocalVent_schedule[item]

        # 空調設定温度の取得
        # Tset = Schedule.ACSet(self.name, '温度', dtmNow)
        # 空調需要の設定
        if self.__number_of_people > 0:
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
        self.__BRM = 0.0
        self.__BRL = self.__Beta
        RMdT = self.__Hcap / Gdata.DTime
        self.__BRM += RMdT
        # BRLの計算
        i = 0
        for surface in self.input_surfaces:
            # 室内対流熱伝達率×面積[W/K]
            AF0 = surface.area * surface.hic
            temp = AF0 * (1.0 - self.__matWSR[i][0])
            # hc×A×(1-WSR)の積算
            self.__BRM += temp
            # BRLの計算
            self.__BRL += AF0 * self.__matWSB[i][0]
            i += 1

        # 外気導入項の計算
        temp = conca * conrowa * \
               (self.__Ventset + self.__Infset + self.__LocalVentset) / 3600.0
        self.__BRM += temp
        # 室間換気
        for room_vent in self.__RoomtoRoomVent:
            nextvent = room_vent.next_vent()
            temp = conca * conrowa * nextvent / 3600.0
            self.__BRM += temp

        # 家具からの熱取得
        if self.__Capfun > 0.0:
            self.__BRM += 1. / (Gdata.DTime / self.__Capfun + 1. / self.__Cfun)

        # 定数項の計算
        self.__BRC = 0.0
        # {WSC}、{CRX}の初期化
        self.__matWSC = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]
        self.__matCRX = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]

        # {CRX}の作成
        i = 0
        for surface in self.input_surfaces:
            self.__matCRX[i][0] = surface.RFT0 * surface.Teo \
                                  + surface.RSsol * surface.RFA0
            i += 1

        # print('matCRX')
        # print(self.__matCRX)
        # {WSC}=[XA]*{CRX}
        self.__matWSC = np.dot(self.__matAX, self.__matCRX)
        
        # print('matWSC')
        # print(self.__matWSC)
        # {BRC}の計算
        i = 0
        for surface in self.input_surfaces:
            NowQw = self.__matWSC[i][0] * surface.area * surface.hic
            self.__BRC += NowQw
            i += 1

        # 外気流入風（換気＋すきま風）
        temp = conca * conrowa * \
               (self.__Ventset + self.__Infset + self.__LocalVentset) \
               * Weather.WeaData(enmWeatherComponent.Ta, dtmNow) / 3600.0
        self.__BRC += temp

        # 室間換気流入風
        for room_vent in self.__RoomtoRoomVent:
            nextvent = room_vent.next_vent()
            temp = conca * conrowa * nextvent \
                   * room_vent.oldTr / 3600.0
            # print(self.name, room_vent.Windward_roomname(), nextvent, room_vent.oldTr())
            self.__BRC += temp
        # RM/Δt*oldTrの項
        temp = self.__Hcap / Gdata.DTime * self.__oldTr
        self.__BRC += temp

        # 家具からの熱取得の項
        if self.__Capfun > 0.0:
            self.__BRC += (self.__Capfun / Gdata.DTime * self.__oldTfun + self.Qsolfun) \
                    / (self.__Capfun / (Gdata.DTime * self.__Cfun) + 1.)

        # {WSV}、{CVL}の初期化
        self.__matWSV = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]
        self.__matCVL = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]

        # 畳み込み演算
        i = 0
        for surface in self.input_surfaces:
            self.__matCVL[i][0] = surface.convolution()
            i += 1

        # {WSV}=[XA]*{CVL}
        self.__matWSV = np.dot(self.__matAX, self.__matCVL)
        # 畳み込み後の室内表面温度の計算
        i = 0
        for surface in self.input_surfaces:
            temp = surface.area * surface.hic * self.__matWSV[i][0]

            self.__BRC += temp
            i += 1

        # 定数項への内部発熱の加算
        self.__BRC += self.__Hn

        # 窓開閉、空調発停判定のための自然室温計算
        # 通風なしでの係数を控えておく
        self.__BRMnoncv = self.__BRM
        self.__BRCnoncv = self.__BRC
        if self.nowWin == 1:
            temp = conca * conrowa * self.__Vcrossvent / 3600.0
            self.__BRM += temp
            self.__BRC += temp * Ta

        # OT計算用の係数補正
        self.__Xot = 0.0
        self.__XLr = 0.0
        self.__XC = 0.0
        temp = 0.0
        XLr = 0.0
        XC = 0.0
        i = 0
        for surface in self.input_surfaces:
            temp += (surface.fot * self.__matWSR[i][0])
            XLr += surface.fot * self.__matWSB[i][0]
            XC += surface.fot * (self.__matWSC[i][0] + self.__matWSV[i][0])
            i += 1

        temp = self.__kc + self.__kr * temp
        self.__Xot = 1.0 / temp
        self.__XLr = self.__kr * XLr / temp
        self.__XC = self.__kr * XC / temp
        self.__BRMot = self.__BRM * self.__Xot
        self.__BRCot = self.__BRC + self.__BRM * self.__XC
        self.__BRLot = self.__BRL + self.__BRM * self.__XLr
        # 自然室温でOTを計算する
        is_radiative_heating = False
        if Gdata.is_residential:
            is_radiative_heating = self.__is_radiative_heating
        
        # 自然作用温度の計算（住宅用）
        if Gdata.is_residential:
            self.OT, self.Lcs, self.Lrs = self.calcTrLs(0, is_radiative_heating, self.__BRCot, self.__BRMot,
                                                        self.__BRLot, 0, 0.0)
            # 窓開閉と空調発停の判定をする
            self.nowWin, self.nowAC = mode_select(self.demAC, self.preAC, self.preWin, self.OT)
            # 最終計算のための係数整備
            self.__BRC = self.__BRCnoncv
            self.__BRM = self.__BRMnoncv
            # 通風なら通風量を設定
            if self.nowWin == 1:
                temp = conca * conrowa * self.__Vcrossvent / 3600.0
                self.__BRM += temp
                self.__BRC += temp * Ta
            
            # OT計算用の係数補正
            self.__Xot = 0.0
            self.__XLr = 0.0
            self.__XC = 0.0
            temp = 0.0
            XLr = 0.0
            XC = 0.0
            i = 0
            for surface in self.input_surfaces:
                temp += (surface.fot * self.__matWSR[i][0])
                XLr += surface.fot * self.__matWSB[i][0]
                XC += surface.fot * (self.__matWSC[i][0] + self.__matWSV[i][0])
                i += 1

            temp = self.__kc + self.__kr * temp
            self.__Xot = 1.0 / temp
            self.__XLr = self.__kr * XLr / temp
            self.__XC = self.__kr * XC / temp
            self.__BRMot = self.__BRM * self.__Xot
            self.__BRCot = self.__BRC + self.__BRM * self.__XC
            self.__BRLot = self.__BRL + self.__BRM * self.__XLr
            
            # 設定温度の計算
            self.OTset, self.Met, self.Clo, self.Vel = calcOTset(self.nowAC, self.__is_radiative_heating, self.RH)

            # 仮の室温、熱負荷の計算
            self.OT, self.Lcs, self.Lrs = self.calcTrLs(self.nowAC,
                                                            self.__is_radiative_heating, self.__BRCot, self.__BRMot,
                                                            self.__BRLot, 0, self.OTset)
            # 室温を計算
            self.Tr = self.__Xot * self.OT - self.__XLr * self.Lrs - self.__XC

            # 最終的な運転フラグの設定（空調時のみ）
            self.finalAC = reset_SW(self.nowAC, self.Lcs, self.Lrs, self.__is_radiative_heating, self.__radiative_heating_max_capacity)

            # 最終室温・熱負荷の再計算
            self.OT, self.Lcs, self.Lrs = self.calcTrLs(self.finalAC,
                                                            self.__is_radiative_heating, self.__BRCot, self.__BRMot,
                                                            self.__BRLot, self.__radiative_heating_max_capacity, self.OTset)
            # 室温を計算
            self.Tr = self.__Xot * self.OT \
                        - self.__XLr * self.Lrs - self.__XC
        # 自然室温の計算（非住宅用）
        else:
            self.Tr, self.Lcs, self.Lrs = self.calcTrLs(0, is_radiative_heating, self.__BRC, self.__BRM,
                                                        self.__BRL, 0, 0.0)
            # 空調停止で初期化
            self.finalAC = 0
            # 窓閉鎖
            self.nowWin = 0
            # 設定温度
            temp_set = 0.0
            # 上限温度を超える場合は冷房
            if self.__is_upper_temp_limit_set[item] and self.Tr > self.__temperature_upper_limit[item]:
                self.finalAC = -1
                temp_set = self.__temperature_upper_limit[item]
            # 下限温度を下回る場合は暖房
            elif self.__is_lower_temp_limit_set[item] and self.Tr < self.__temperature_lower_limit[item]:
                self.finalAC = 1
                temp_set = self.__temperature_lower_limit[item]
            # print("item=", item, "Tr=", self.Tr, "finalAC=", self.finalAC, "temp_set=", temp_set, \
            #     self.__is_upper_temp_limit_set[item], self.__temperature_upper_limit[item])
            # 室温、熱負荷の計算
            self.Tr, self.Lcs, self.Lrs = self.calcTrLs(self.finalAC, is_radiative_heating, self.__BRC, self.__BRM, \
                self.__BRL, 0, temp_set)

        # 表面温度の計算
        self.MRT = 0.0
        self.AST = 0.0
        i = 0
        for surface in self.input_surfaces:
            Ts = self.__matWSR[i][0] * self.Tr \
                 + self.__matWSC[i][0] + self.__matWSV[i][0] \
                 + self.__matWSB[i][0] * self.Lrs
            surface.Ts = Ts

            # 人体に対する放射温度：MRT、面積荷重平均温度：ASTの計算
            self.MRT += surface.fot * surface.Ts
            self.AST += surface.area * surface.Ts / self.__Atotal
            i += 1
        # 非住宅の場合の作用温度を計算する
        self.OT = self.__kc * self.Tr + self.__kr * self.MRT

        # 室内側等価温度の計算
        for surface in self.input_surfaces:
            surface.Tsx = 0.0

            j = 0
            # 形態係数加重平均表面温度の計算
            for nxtsurface in self.input_surfaces:
                surface.Tsx += nxtsurface.Ts * nxtsurface.Fmrt
                j += 1

            # 室内側等価温度の計算
            surface.update_Tei(self.Tr, surface.Tsx, self.Lrs, self.__Beta)
            # 室内表面熱流の計算
            surface.update_qi(self.Tr, surface.Tsx, self.Lrs, self.__Beta)

        # 湿度の計算
        xo = Weather.WeaData(enmWeatherComponent.x, dtmNow) / 1000.
        self.Voin = (self.__Ventset + self.__Infset + self.__LocalVentset) / 3600.
        Ff = self.__Gf * self.__Cx / (self.__Gf + Gdata.DTime * self.__Cx)
        Vd = self.__volume / Gdata.DTime
        self.__BRMX = conrowa * (Vd + self.Voin) + Ff
        self.__BRXC = conrowa * (self.__volume / Gdata.DTime * self.__oldxr + self.Voin * xo) \
                + Ff * self.__oldxf + self.Lin
        
        # if self.name == '主たる居室':
        #     print(self.Voin, Ff, Vd)
        # 室間換気流入風
        for room_vent in self.__RoomtoRoomVent:
            nextvent = room_vent.next_vent()
            self.__BRMX += conrowa * nextvent / 3600.0
            self.__BRXC += conrowa * nextvent * room_vent.oldxr / 3600.0
        
        # 住宅の場合
        if Gdata.is_residential:
            # 空調の熱交換部飽和絶対湿度の計算
            self.calcVac_xeout(self.nowAC)
            # 空調機除湿の項
            RhoVac = conrowa * self.Vac * (1.0 - self.__BF)
            self.__BRMX += RhoVac
            self.__BRXC += RhoVac * self.__xeout
            # 室絶対湿度[kg/kg(DA)]の計算
            self.xr = self.__BRXC / self.__BRMX
            # 加湿量の計算
            self.Ghum = RhoVac * (self.__xeout - self.xr)
            if self.Ghum > 0.0:
                self.Ghum = 0.0
                # 空調機除湿の項の再計算（除湿なしで計算）
                self.__BRMX -= RhoVac
                self.__BRXC -= RhoVac * self.__xeout
                self.Va = 0.0
                # 室絶対湿度の計算
                self.xr = self.__BRXC / self.__BRMX
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
            self.xr = self.__BRXC / self.__BRMX
            # 相対湿度の計算
            self.RH = rhtx(self.Tr, self.xr)
            # 潜熱計算運転状態
            self.nowACx = 0
            # 潜熱負荷の初期化
            self.Lcl = 0.0
            # 上限湿度を超える場合は除湿
            if self.__is_upper_humidity_limit_set[item] and self.RH > self.__relative_humidity_upper_limit[item]:
                self.nowACx = -1
                RH_set = self.__relative_humidity_upper_limit[item]
                
            # 下限湿度を下回る場合は加湿
            elif self.__is_lower_humidity_limit_set[item] and self.RH < self.__relative_humidity_lower_limit[item]:
                self.nowACx = 1
                RH_set = self.__relative_humidity_lower_limit[item]

            # 設定絶対湿度の計算（潜熱運転のときだけ）
            if self.nowACx != 0:
                self.xr = xtrh(self.Tr, RH_set)
                self.RH = RH_set
                self.Lcl = - conra * (self.__BRXC - self.__BRMX * self.xr)

        # 家具の温度を計算
        self.Tfun = self.calcTfun(Gdata)
        self.xf = self.calcxf(Gdata)

        # 年間熱負荷の積算
        # 助走計算以外の時だけ積算
        if Gdata.FlgOrig(dtmNow) == True:
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
                self.AnnualLoadcCl += self.Lcl * Gdata.DTime * 0.000000001

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
        self.__oldTr = self.Tr
        self.__oldTfun = self.Tfun
        self.__oldxr = self.xr
        self.__oldxf = self.xf

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
        if self.__Capfun > 0.0:
            self.Tfun = ((self.__Capfun / Gdata.DTime * self.__oldTfun \
                    + self.__Cfun * self.Tr + self.Qsolfun) \
                    / (self.__Capfun / Gdata.DTime + self.__Cfun))
            self.Qfuns = self.__Cfun * (self.Tr - self.Tfun)
        # if self.name == "主たる居室":
        #     print(self.name, self.__oldTfun, self.Tfun, self.__Capfun, self.__Cfun, self.Qsolfun)
        return self.Tfun

    # 家具類の湿度を計算する
    def calcxf(self, Gdata):
        self.xf = (self.__Gf / Gdata.DTime * self.__oldxf + self.__Cx * self.xr) / (self.__Gf / Gdata.DTime + self.__Cx)
        self.Qfunl = self.__Cx * (self.xr - self.xf)
        # if self.name == "主たる居室":
        #     print(self.name, self.__oldTfun, self.Tfun, self.__Capfun, self.__Cfun, self.Qsolfun)
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
            self.__Teout = self.Tr - Qs / (conca * conrowa * self.Vac * (1.0 - self.__BF))
            # 熱交換器吹出部分は飽和状態
            self.__xeout = x(Pws(self.__Teout))

    # 暖房設備仕様の読み込み
    def __heating_equipment_read(self, dheqp):
        # 放射暖房有無（Trueなら放射暖房あり）
        self.__is_radiative_heating = dheqp['is_radiative_heating']
        # 放射暖房最大能力[W]
        self.__radiative_heating_max_capacity = 0.0
        if self.__is_radiative_heating:
            self.__radiative_heating_max_capacity = dheqp['radiative_heating']['max_capacity'] * dheqp['radiative_heating']['area']

    # 冷房設備仕様の読み込み
    def __cooling_equipment_read(self, dceqp):
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

    # 機器仕様の読み込み
    def __equipment_read(self, deqp):
        # 主冷房
        self.__main_type_c, \
        self.__main_q_rtd_c, \
        self.__main_q_max_c, \
        self.__main_cop_rtd_c, \
        self.__main_construct_floor_c = self.__equip_alalysis(deqp['cooling']['main'])
        # 補助冷房
        self.__sub_type_c, \
        self.__sub_q_rtd_c, \
        self.__sub_q_max_c, \
        self.__sub_cop_rtd_c, \
        self.__sub_construct_floor_c = self.__equip_alalysis(deqp['cooling']['sub'])
        # 主暖房
        self.__main_type_h, \
        self.__main_q_rtd_h, \
        self.__main_q_max_h, \
        self.__main_cop_rtd_h, \
        self.__main_construct_floor_h = self.__equip_alalysis(deqp['heating']['main'])
        # 補助冷房
        self.__sub_type_h, \
        self.__sub_q_rtd_h, \
        self.__sub_q_max_h, \
        self.__sub_cop_rtd_h, \
        self.__sub_construct_floor_h = self.__equip_alalysis(deqp['heating']['sub'])

        return 0

    # 機器仕様Dictionaryを解析する
    def __equip_alalysis(self, eqp):
        type = None
        q_rtd = 0.0
        q_max = 0.0
        cop_rtd = 0.0
        construct_area = 0.0
        if len(eqp) > 0:
            type = eqp['type']
            if type == 'room_air_conditioner':
                q_rtd = float(eqp['q_rtd'])
                q_max = float(eqp['q_max'])
                cop_rtd = float(eqp['cop_rtd'])
            elif type == 'floor_heating':
                construct_area = float(eqp['construct_area'])

        return type, q_rtd, q_max, cop_rtd, construct_area

def create_spaces(Gdata, rooms):
    objSpace = {}
    for room in rooms:
        space = Space(Gdata, room)
        objSpace[room['name']] = space
    return objSpace