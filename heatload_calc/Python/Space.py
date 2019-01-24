import numpy as np
from typing import List
from Weather import enmWeatherComponent
import math

import Surface
from Surface import *
import NextVent
from NextVent import *

import SeasonalValue
from SeasonalValue import SeasonalValue
from Psychrometrics import Pws, x, xtrh, rhtx
from common import conca, conrowa, Sgm, conra
from PMV import *
from Win_ACselect import *

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
# - RadHeat:       放射暖房対象室フラグ, True
# - Betat:         放射暖房対流比率, －
# - RoomtoRoomVents:      室間換気量（list型、暖房・中間期・冷房、風上室名称）, m3/h
# - d:             室内部位に関連するクラス, Surface

# 空間に関する情報の保持
class Space:
    FsolFlr = 0.5  # 床の日射吸収比率

    # 初期化
    def __init__(self, Gdata, roomname,
                 HeatCcap, HeatRcap, CoolCcap, Vol, Fnt, Vent, Inf, CrossVentRoom,
                 RadHeat, Beta, RoomtoRoomVents, Surfaces: List[dict]):
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
        :param RadHeat:
        :param Beta:
        :param RoomtoRoomVents:
        :param Surfaces:
        """
        self.name = roomname  # 室用途（主たる居室、その他居室、非居室）
        self.__AnnualLoadcC = 0.0  # 年間冷房熱負荷（対流成分）
        self.__AnnualLoadcH = 0.0  # 年間暖房熱負荷（対流成分）
        self.__AnnualLoadrC = 0.0  # 年間冷房熱負荷（放射成分）
        self.__AnnualLoadrH = 0.0  # 年間暖房熱負荷（放射成分）
        self.Tr = 15.0  # 室温の初期化
        self.__oldTr = 15.0  # 前時刻の室温の初期化
        self.Tfun = 15.0  # 家具の温度[℃]
        self.__oldTfun = 15.0   # 前時刻の家具の温度[℃]
        self.__rsolfun = 0.5    # 透過日射の内家具が吸収する割合[－]
        self.__kc = 0.5  # 人体表面の熱伝達率の対流成分比率
        self.__kr = 0.5  # 人体表面の熱伝達率の放射成分比率
        self.demAC = 0                          # 当該時刻の空調需要（0：なし、1：あり）
        self.preAC = 0                          # 前時刻の空調運転状態（0：停止、正：暖房、負：冷房）
        self.preWin = 0                         # 前時刻の窓状態（0：閉鎖、1：開放）
        self.nowAC = 0                          # 当該時刻の空調運転状態（0：なし、正：暖房、負：冷房）
        self.nowWin = 0                         # 当該時刻の窓状態（0：閉鎖、1：開放）
        # PMVの計算条件
        self.Met = 1.0                          # 代謝量[Met]
        self.Wme = 0.0                          # 外部仕事[Met]
        self.Vel = 0.1                          # 相対風速[m/s]
        self.Clo = 1.0                          # 着衣量[Clo]
        self.OTset = 0.0
        self.__HeatCcap = 0.0
        if HeatCcap is not None:
            self.__HeatCcap = float(HeatCcap)  # 最大暖房能力（対流）
        self.__HeatRcap = 0.0
        if HeatRcap is not None:
            self.__HeatRcap = float(HeatRcap)  # 最大暖房能力（放射）
        self.__CoolCcap = 0.0
        if CoolCcap is not None:
            self.__CoolCcap = float(CoolCcap)  # 最大冷房能力（対流）
        # self.__CoolRcap = CoolRcap                #最大冷房能力（放射）
        self.__Vol = float(Vol)  # 室気積
        self.__Ga = self.__Vol * conrowa                # 室空気の質量[kg]
        self.__Capfun = self.__Vol * float(Fnt) * 1000.  # 家具熱容量[J/K]
        self.__Cfun = 0.00022 * self.__Capfun       # 家具と空気間の熱コンダクタンス[W/K]
        self.__Gf = 16.8 * self.__Vol               # 家具類の湿気容量[kg]
        self.__Cx = 0.0018 * self.__Gf              # 室空気と家具類間の湿気コンダクタンス[kg/(s･kg/kg(DA))]
        self.xr = xtrh(20.0, 40.0)
        self.__oldxr = self.xr                    # 室内絶対湿度の初期値
        self.xf = self.xr                       
        self.__oldxf = self.xr                    # 家具類の絶対湿度の初期値
        self.__BF = 0.2                             # バイパスファクター
        self.__xeout = 0.0                          # エアコン熱交換部の飽和絶対湿度[kg/kg(DA)]
        self.Vac = 0.0                            # エアコンの風量[m3/s]
        self.RH = 50.0                               # 室相対湿度[%]
        self.__Vcrossvent = self.__Vol * 20.0       # 窓開放時通風量：とりあえず5回/h
        # 室空気の熱容量
        self.__Hcap = self.__Vol * conrowa * conca
        # print(self.__Hcap)
        self.__Vent = SeasonalValue(Vent['winter'], Vent['inter'], Vent['summer'])
        # self.__Vent = Vent                        #計画換気量
        # print(self.__Vent)
        # self.__Inf = Inf                          #すきま風量
        self.__Inf = SeasonalValue(Inf['winter'], Inf['inter'], Inf['summer'])
        self.__CrossVentRoom = CrossVentRoom  # 通風対象室フラグ
        self.__isRadiantHeater = RadHeat  # 放射暖房設置フラグ
        if Beta is None:
            self.__Beta = 0.0 
        else:
            self.__Beta = float(Beta)  # 放射暖房対流比率
        # self.__oldNextRoom = []
        # self.__NextVent = []

        # 内部発熱の初期化
        # 機器顕熱
        self.__Appls = 0.0
        # 照明
        self.__Light = 0.0
        # 人体顕熱
        self.__Humans = 0.0
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
        for room_vent in RoomtoRoomVents:
            self.__RoomtoRoomVent.append(NextVent(room_vent['Windward_roomname'], \
                                                  room_vent['winter'], room_vent['inter'], room_vent['summer']))
        self.__Nsurf = 0  # 部位の数
        self.surfaces = []

        for d_surface in Surfaces:
            # print(d_surface['name'])
            self.surfaces.append(Surface(d_surface, Gdata))
        
        # 部位の人体に対する形態係数の計算
        total_Aex_floor = 0.0
        total_A_floor = 0.0
        # 設定合計値もチェック
        total_Fot = 0.0
        # 床と床以外の合計面積を計算
        for surface in self.surfaces:
            # 下向き部位（床）
            if surface.Floor:
                total_A_floor += surface.area
            # 床以外
            else:
                total_Aex_floor += surface.area
        
        # 上向き、下向き、垂直部位の合計面積をチェックし人体に対する形態係数の割合を基準化
        fot_floor = 0.45
        fot_exfloor = 1.0 - fot_floor

        # 人体に対する部位の形態係数の計算
        for surface in self.surfaces:
            # 下向き部位（床）
            if surface.Floor:
                surface.fot = surface.area / total_A_floor * fot_floor
            # 床以外
            else:
                surface.fot = surface.area / total_Aex_floor * fot_exfloor
            total_Fot += surface.fot
            # print(surface.name, surface.fot)

        if abs(total_Fot - 1.0) > 0.001:
            print(self.name, 'total_Fot=', total_Fot)

        self.__Nsurf = len(self.surfaces)

        # 面対面の形態係数の計算
        self.__Atotal = 0.0
        self.__TotalAF = 0.0

        # print('合計面積1=', self.__Atotal)
        # 合計面積の計算
        for surface in self.surfaces:
            self.__Atotal += surface.area
            # 合計床面積の計算
            if surface.Floor == True:
                self.__TotalAF += surface.area
        
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
        for surface in self.surfaces:
            surface.a = surface.area / self.__Atotal
            max_a = max(max_a, surface.a)
        
        # 室のパラメータの計算（ニュートン法）
        # 初期値を設定
        fbd = max_a * 4.0 + 0.1
        # 収束判定
        isConverge = False
        for i in range(50):
            L = -1.0
            Ld = 0.0
            for surface in self.surfaces:
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
        # print('合計表面積=', self.__Atotal)
        # 形態係数の計算（永田の方式）
        # 総和のチェック
        TotalFF = 0.0
        for surface in self.surfaces:
            FF = 0.5 * (1.0 - math.sqrt(1.0 - 4.0 * surface.a / fb))
            TotalFF += FF
            # print(self.name, surface.name, FF)
            surface.setFF(FF)
        
        # 室内側表面熱伝達率の計算
        for surface in self.surfaces:
            surface.hir = surface.Ei / (1.0 - surface.Ei * surface.FF()) \
                    * 4.0 * Sgm * (20.0 + 273.15) ** 3.0
            surface.hic = max(0.0, surface.hi - surface.hir)
            # print(surface.name, surface.hic, surface.hir, surface.hi)
        
        # print(TotalFF)
        # 透過日射の室内部位表面吸収比率の計算
        # 50%を床、50%を家具に吸収させる
        # 床が複数の部位の場合は面積比で案分する
        FsolFlr = 0.5
        # 家具の吸収比率で初期化
        TotalR = self.__rsolfun

        for surface in self.surfaces:
            SolR = 0.0
            # 床の室内部位表面吸収比率の設定
            if surface.Floor == True:
                SolR = FsolFlr * surface.area / self.__TotalAF
            surface.SolR = SolR
            # 室内部位表面吸収比率の合計値（チェック用）
            TotalR += SolR
        # 日射吸収率の合計値のチェック
        if abs(TotalR - 1.0) > 0.00001:
            print(self.name, '日射吸収比率合計値エラー', TotalR)

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
        for surface in self.surfaces:
            # matFIAの作成
            self.__matFIA[i][0] = surface.RFA0 * surface.hic
            # print('i=', i, 'FIA=', self.__matFIA[i][0])
            # FLB=φA0×flr×(1-Beta)
            self.__matFLB[i][0] = surface.RFA0 * surface.flr * (1. - self.__Beta) / surface.area

            # 放射計算のマトリックス作成
            for j in range(self.__Nsurf):
                # print('i=', i, 'j=', j)
                # print('FIA=', self.__matFIA[0][i])
                # print('FF=', surface.FF(j))
                # 対角要素
                if i == j:
                    self.__matAXd[i][j] = 1. + surface.RFA0 * surface.hi \
                                          - surface.RFA0 * surface.hir * surface.FF()
                # 対角要素以外
                else:
                    self.__matAXd[i][j] = - surface.RFA0 * surface.hir * surface.FF()
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

    # 室温、熱負荷の計算
    def calcHload(self, Gdata, spaces, dtmNow, defSolpos, Schedule, Weather):
        # 室間換気の風上室温をアップデート
        for roomvent in self.__RoomtoRoomVent:
            windward_roomname = roomvent.Windward_roomname
            oldTr = spaces[windward_roomname].oldTr
            oldxr = spaces[windward_roomname].oldxr
            roomvent.update_oldstate(oldTr, oldxr)

        # 外皮の傾斜面日射量の計算
        Idn = Weather.WeaData(enmWeatherComponent.Idn, dtmNow)
        Isky = Weather.WeaData(enmWeatherComponent.Isky, dtmNow)
        for surface in self.surfaces:
            if surface.is_skin:
                surface.update_slope_sol(defSolpos, Idn, Isky)

        # 庇の日影面積率計算
        for surface in self.surfaces:
            # 庇がある場合のみ
            if surface.has_sunbrk:
                # 日影面積率の計算
                surface.update_Fsdw(defSolpos)
                # print(surface.Fsdw)

        # 透過日射熱取得の計算
        self.Qgt = 0.0
        for surface in self.surfaces:
            if surface.is_window and surface.is_skin:
                surface.update_Qgt_Qga()
                self.Qgt += surface.Qgt

        # 相当外気温度の計算
        Ta = Weather.WeaData(enmWeatherComponent.Ta, dtmNow)
        RN = Weather.WeaData(enmWeatherComponent.RN, dtmNow)
        AnnualTave = Weather.AnnualTave()
        for surface in self.surfaces:
            surface.calcTeo(Ta, RN, self.__oldTr, AnnualTave, spaces)
            # print(surface.name, Ta, RN, self.__oldTr, surface.Teo)

        # 内部発熱の計算（すべて対流成分とする）
        self.__Appls = Schedule.Appl(self.name, '顕熱', dtmNow)
        self.__Appll = Schedule.Appl(self.name, '潜熱', dtmNow)
        self.__Light = Schedule.Light(self.name, dtmNow)
        Nresi = Schedule.Nresi(self.name, dtmNow)
        self.__Humans = Nresi \
                       * (63.0 - 4.0 * (self.__oldTr - 24.0))
        # 人体潜熱
        self.__Humanl = max(Nresi * 119.0 - self.__Humans, 0.0)
        self.__Hn = self.__Appls + self.__Light + self.__Humans

        # 内部発湿[kg/s]
        self.Lin = (self.__Appll + self.__Humanl) / conra
        # print(self.name, self.__Appls, self.__Light, self.__Humans)

        # 室内表面の吸収日射量
        for surface in self.surfaces:
            surface.update_RSsol(self.Qgt)
        # 家具の吸収日射量
        self.__Qsolfun = self.Qgt * self.__rsolfun

        # 流入外気風量の計算
        # 計画換気・すきま風量
        season = Schedule.Season(dtmNow)
        if season == '暖房':
            self.__Ventset = self.__Vent.winter
            self.__Infset = self.__Inf.winter
        elif season == '中間':
            self.__Ventset = self.__Vent.inter
            self.__Infset = self.__Inf.inter
        elif season == '冷房':
            self.__Ventset = self.__Vent.summer
            self.__Infset = self.__Inf.summer
        # 局所換気量
        self.__LocalVent = Schedule.LocalVent(self.name, dtmNow)

        # 空調設定温度の取得
        Tset = Schedule.ACSet(self.name, '温度', dtmNow)
        # 空調需要の設定
        if Nresi > 0:
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
        for surface in self.surfaces:
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
               (self.__Ventset + self.__Infset + self.__LocalVent) / 3600.0
        self.__BRM += temp
        # 室間換気
        for room_vent in self.__RoomtoRoomVent:
            nextvent = room_vent.next_vent(season)
            temp = conca * conrowa * nextvent / 3600.0
            self.__BRM += temp

        # 家具からの熱取得
        self.__BRM += 1. / (Gdata.DTime / self.__Capfun + 1. / self.__Cfun)

        # 定数項の計算
        self.__BRC = 0.0
        # {WSC}、{CRX}の初期化
        self.__matWSC = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]
        self.__matCRX = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]

        # {CRX}の作成
        i = 0
        for surface in self.surfaces:
            self.__matCRX[i][0] = surface.RFT0 * surface.Teo \
                                  + surface.RSsol * surface.RFA0
            i += 1

        # {WSC}=[XA]*{CRX}
        self.__matWSC = np.dot(self.__matAX, self.__matCRX)
        # {BRC}の計算
        i = 0
        for surface in self.surfaces:
            NowQw = self.__matWSC[i][0] * surface.area * surface.hic
            self.__BRC += NowQw
            i += 1

        # 外気流入風（換気＋すきま風）
        temp = conca * conrowa * \
               (self.__Ventset + self.__Infset + self.__LocalVent) \
               * Weather.WeaData(enmWeatherComponent.Ta, dtmNow) / 3600.0
        self.__BRC += temp

        # 室間換気流入風
        for room_vent in self.__RoomtoRoomVent:
            nextvent = room_vent.next_vent(season)
            temp = conca * conrowa * nextvent \
                   * room_vent.oldTr / 3600.0
            # print(self.name, room_vent.Windward_roomname(), nextvent, room_vent.oldTr())
            self.__BRC += temp
        # RM/Δt*oldTrの項
        temp = self.__Hcap / Gdata.DTime * self.__oldTr
        self.__BRC += temp

        # 家具からの熱取得の項
        self.__BRC += (self.__Capfun / Gdata.DTime * self.__oldTfun + self.__Qsolfun) \
                / (self.__Capfun / (Gdata.DTime * self.__Cfun) + 1.)

        # {WSV}、{CVL}の初期化
        self.__matWSV = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]
        self.__matCVL = [[0.0 for i in range(1)] for j in range(self.__Nsurf)]

        # 畳み込み演算
        i = 0
        for surface in self.surfaces:
            self.__matCVL[i][0] = surface.convolution()
            i += 1

        # {WSV}=[XA]*{CVL}
        self.__matWSV = np.dot(self.__matAX, self.__matCVL)
        # 畳み込み後の室内表面温度の計算
        i = 0
        for surface in self.surfaces:
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
        for surface in self.surfaces:
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
        self.__OT, self.Lcs, self.Lr = self.calcTrLs(0, self.__isRadiantHeater, self.__BRCot, self.__BRMot,
                                                        self.__BRLot, 0, 0, 0.0)

        # 窓開閉と空調発停の判定をする
        self.nowWin, self.nowAC = mode_select(self.demAC, self.preAC, self.preWin, self.__OT)
        # if self.nowAC == 1 and self.__isRadiantHeater:
        #     self.nowAC = 4

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
        for surface in self.surfaces:
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
        self.OTset, self.Met, self.Clo, self.Vel = calcOTset(self.nowAC, self.__isRadiantHeater, self.RH)

        # 仮の室温、熱負荷の計算
        self.__OT, self.Lcs, self.Lr = self.calcTrLs(self.nowAC,
                                                        self.__isRadiantHeater, self.__BRCot, self.__BRMot,
                                                        self.__BRLot, 0, 0, self.OTset)
        # 室温を計算
        self.Tr = self.__Xot * self.__OT - self.__XLr * self.Lr - self.__XC

        # 最終的な運転フラグの設定（空調時のみ）
        self.finalAC = self.nowAC
        if self.nowAC != 0:
            if self.nowAC > 0:
                Hcap = self.__HeatCcap
            else:
                Hcap = self.__CoolCcap
            self.finalAC = reset_SW(self.nowAC, self.Lcs, self.Lr, self.__isRadiantHeater, Hcap, self.__HeatRcap)

        # 機器容量を再設定
        if self.finalAC > 0:
            Hcap = self.__HeatCcap
        elif self.finalAC < 0:
            Hcap = self.__CoolCcap
        else:
            Hcap = 0.0

        # 最終室温・熱負荷の再計算
        self.__OT, self.Lcs, self.Lr = self.calcTrLs(self.finalAC,
                                                        self.__isRadiantHeater, self.__BRCot, self.__BRMot,
                                                        self.__BRLot, Hcap, self.__HeatRcap, self.OTset)
        # 室温を計算
        self.Tr = self.__Xot * self.__OT \
                    - self.__XLr * self.Lr - self.__XC

        # 放射暖房最大能力が設定されている場合にはもう１度チェックする
        if self.finalAC == 3 and self.Lcs > Hcap and Hcap > 0.0:
            self.finalAC = 5
            self.__OT, self.Lcs, self.Lr = self.calcTrLs(self.finalAC, \
                                                            self.__isRadiantHeater, self.__BRCot, self.__BRMot, \
                                                            self.__BRLot, Hcap, self.__HeatRcap, self.OTset)
            # 室温を計算
            self.Tr = self.__Xot * self.__OT - self.__XLr * self.Lr - self.__XC

        # 年間熱負荷の積算
        # 助走計算以外の時だけ積算
        if Gdata.FlgOrig(dtmNow) == True:
            # 対流式空調の積算
            if self.Lcs > 0.0:
                self.__AnnualLoadcH += self.Lcs * Gdata.DTime * 0.000000001
            else:
                self.__AnnualLoadcC += self.Lcs * Gdata.DTime * 0.000000001

            # 放射式空調の積算
            if self.Lr > 0.0:
                self.__AnnualLoadrH += self.Lr * Gdata.DTime * 0.000000001
            else:
                self.__AnnualLoadrC += self.Lr * Gdata.DTime * 0.000000001

        # 表面温度の計算
        self.MRT = 0.0
        self.AST = 0.0
        i = 0
        for surface in self.surfaces:
            Ts = self.__matWSR[i][0] * self.Tr \
                 + self.__matWSC[i][0] + self.__matWSV[i][0] \
                 + self.__matWSB[i][0] * self.Lr
            surface.Ts = Ts

            # 人体に対する放射温度：MRT、面積荷重平均温度：ASTの計算
            self.MRT += surface.fot * surface.Ts
            self.AST += surface.area * surface.Ts / self.__Atotal
            i += 1

        # 室内側等価温度の計算
        for surface in self.surfaces:
            Tsx = 0.0

            j = 0
            # 形態係数加重平均表面温度の計算
            for nxtsurface in self.surfaces:
                Tsx += nxtsurface.Ts * nxtsurface.FF()
                j += 1

            # 室内側等価温度の計算
            surface.update_Tei(self.Tr, Tsx, self.Lr, self.__Beta)
            # 室内表面熱流の計算
            surface.update_qi(self.Tr, Tsx, self.Lr, self.__Beta)

        # 湿度の計算
        xo = Weather.WeaData(enmWeatherComponent.x, dtmNow) / 1000.
        self.Voin = (self.__Ventset + self.__Infset + self.__LocalVent) / 3600.
        Ff = self.__Gf * self.__Cx / (self.__Gf + Gdata.DTime * self.__Cx)
        Vd = self.__Vol / Gdata.DTime
        self.__BRMX = conrowa * (Vd + self.Voin) + Ff
        self.__BRXC = conrowa * (self.__Vol / Gdata.DTime * self.__oldxr + self.Voin * xo) \
                + Ff * self.__oldxf + self.Lin
        
        # if self.name == '主たる居室':
        #     print(self.Voin, Ff, Vd)
        # 室間換気流入風
        for room_vent in self.__RoomtoRoomVent:
            nextvent = room_vent.next_vent(season)
            self.__BRMX += conrowa * nextvent / 3600.0
            self.__BRXC += conrowa * nextvent * room_vent.oldxr / 3600.0
        # 空調の熱交換部飽和絶対湿度の計算
        self.calcVac_xeout(self.nowAC)
        # 空調機除湿の項
        RhoVac = conrowa * self.Vac * (1.0 - self.__BF)
        self.__BRMX += RhoVac
        self.__BRXC += RhoVac * self.__xeout
        # 室絶対湿度の計算
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
        self.Ll = self.Ghum * conra
        # 室相対湿度の計算
        self.RH = rhtx(self.Tr, self.xr)
        # 家具の温度を計算
        self.Tfun = self.calcTfun(Gdata)
        self.xf = self.calcxf(Gdata)

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
    def calcTrLs(self, nowAC, RadHeat, BRC, BRM, BRL, Hcap, Lrcap, Tset):
        Lcs = 0.0
        Lr = 0.0
        Tr = 0.0
        # 非空調時の計算
        if nowAC == 0:
            Tr = BRC / BRM
        # 熱負荷計算（最大能力無制限）
        elif nowAC == 1 or nowAC == -1 or nowAC == 4:
            # 対流式空調の場合
            if RadHeat != True or RadHeat and nowAC < 0:
                Lcs = BRM * Tset - BRC
            # 放射式空調
            else:
                Lr = (BRM * Tset - BRC) / BRL
            # 室温の計算
            Tr = (BRC + Lcs + BRL * Lr) / BRM
        # 対流空調最大能力運転
        elif (nowAC == 2 and Hcap > 0.0) or (nowAC == -2 and Hcap < 0.0):
            Lcs = Hcap
            Tr = (BRC + Hcap) / BRM
        # 放射暖房最大能力運転（当面は暖房のみ）
        elif nowAC == 3 and Lrcap > 0.0:
            Lr = Lrcap
            # 室温は対流式で維持する
            Lcs = BRM * Tset - BRC - Lr * BRL
            # 室温の計算
            Tr = (BRC + Lcs + BRL * Lr) / BRM
        # 放射空調も対流空調も最大能力運転
        elif nowAC == 5:
            # 放射暖房、対流暖房ともに最大能力
            Lr = Lrcap
            Lcs = Hcap
            # 室温を計算する
            Tr = (BRC + Lcs + BRL * Lr) / BRM

        # 室温、対流空調熱負荷、放射空調熱負荷を返す
        return (Tr, Lcs, Lr)

    

    # 平均放射温度の計算
    def update_Tsx(self):
        self.__Tsx = 0.0
        i = 0
        for surface in self.surfaces:
            self.__Tsx += surface.Ts.Ts() * surface.FF(i)
            i += 1

    # 表面温度の出力
    def surftemp_print(self):
        for surface in self.surfaces:
            print('{0:.2f}'.format(surface.Ts()), "", end="")

    # 家具の温度を計算する
    def calcTfun(self, Gdata):
        self.Tfun = ((self.__Capfun / Gdata.DTime * self.__oldTfun \
                + self.__Cfun * self.Tr + self.__Qsolfun) \
                / (self.__Capfun / Gdata.DTime + self.__Cfun))
        # if self.name == "主たる居室":
        #     print(self.name, self.__oldTfun, self.Tfun, self.__Capfun, self.__Cfun, self.__Qsolfun)
        return self.Tfun

    # 家具類の湿度を計算する
    def calcxf(self, Gdata):
        self.xf = (self.__Gf / Gdata.DTime * self.__oldxf + self.__Cx * self.xr) / (self.__Gf / Gdata.DTime + self.__Cx)
        # if self.name == "主たる居室":
        #     print(self.name, self.__oldTfun, self.Tfun, self.__Capfun, self.__Cfun, self.__Qsolfun)
        return self.xf

    # エアコンの熱交換部飽和絶対湿度の計算
    def calcVac_xeout(self, nowAC):
        # Lcsは加熱が正
        # 加熱時は除湿ゼロ
        Qs = - self.Lcs
        if nowAC == 0 or Qs <= 1.0e-3:
            self.Vac = 0.0
            self.Ghum = 0.0
            self.Ll = 0.0
            return
        else:
            # 風量[m3/s]の計算（線形補間）
            self.Vac = (self.__Vmin + (self.__Vmax - self.__Vmin) \
                    / (self.__qmax_c - self.__qmin_c) * (Qs - self.__qmin_c)) / 60.0
            # 熱交換器温度＝熱交換器部分吹出温度
            self.__Teout = self.Tr - Qs / (conca * conrowa * self.Vac * (1.0 - self.__BF))
            # 熱交換器吹出部分は飽和状態
            self.__xeout = x(Pws(self.__Teout))

def create_spaces(Gdata, rooms):
    objSpace = {}
    for room in rooms:
        HeatCcap = None
        if 'HeatCcap' in room:
            HeatCcap = room['HeatCcap']
        HeatRcap = None
        if 'HeatRcap' in room:
            HeatRcap = room['HeatRcap']
        CoolCcap = None
        if 'CoolCcap' in room:
            CoolCcap = room['CoolCcap']
        RadHeat = None
        if 'RadHeat' in room:
            RadHeat = room['RadHeat']
        CrossVentRoom = None
        if 'CrossVentRoom' in room:
            CrossVentRoom = room['CrossVentRoom']
        Beta = None
        if 'Beta' in room:
            Beta = room['Beta']
        Fnt = 12.6
        if 'Fnt' in room:
            Fnt = room['Fnt']
        space = Space(Gdata, room['roomname'], \
                      HeatCcap, HeatRcap, CoolCcap, room['Vol'], \
                      Fnt, room['Vent'], room['Inf'], \
                      CrossVentRoom, RadHeat, Beta, room['NextVent'],
                      room['Surface'])
        objSpace[room['roomname']] = space
    return objSpace