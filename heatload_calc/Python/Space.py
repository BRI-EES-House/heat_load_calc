
# coding: utf-8

# In[1]:


import nbimporter
import numpy as np
import datetime
import Weather
from Weather import enmWeatherComponent

# In[2]:


import SolarPosision
from SolarPosision import SolarPosision


# In[3]:


import Weather


# In[4]:


import Schedule


# In[5]:


import WallMng
from WallMng import WallMng


# In[6]:


import ExsrfMng
from ExsrfMng import ExsrfMng


# In[7]:


import WindowMng
from WindowMng import WindowMng


# In[8]:


import Sunbrk
from Sunbrk import *


# In[9]:


import SeasonalValue
from SeasonalValue import SeasonalValue

from common import conca, conrowa

# # 室温・熱負荷を計算するクラス

# ## １）室内部位に関連するクラス

# 室内部位に関する情報を保持します。
# 
# - skin:      外皮フラグ, 外皮の場合True
# - boundary:  方位・隣室名, string
# - unsteady:  非定常フラグ, 非定常壁体の場合True
# - name:      壁体・開口部名称, string
# - area:      面積, m2
# - sunbreak:  ひさし名称, string
# - flr:       放射暖房吸収比率, －
# - fot:       人体に対する形態係数, －

# In[10]:


# 室内部位に関連するクラス
class Surface:
    
    # 初期化
    def __init__(self, ExsrfMng, WallMng, WindowMng, SunbrkMng, skin, boundary,                  unsteady, name, area, sunbreak, flr, fot):
        self.__skin = skin            #外皮フラグ
        self.__boundary = boundary    #方位・隣室名
        
        # 外皮の場合は方位クラスを取得する
        if self.__skin == True :
            self.__objExsrf = ExsrfMng.ExsrfobjByName(self.__boundary)
        
        self.__unsteady = unsteady    #非定常フラグ
        self.__name = name            #壁体名称
        
        if '床' in self.__name :      #床フラグ
            self.__floor = True
        else:
            self.__floor = False
            
        self.__area = area            #面積
        self.__sunbreakname = sunbreak    #ひさし名称
        self.__flr = flr              #放射暖房吸収比率
        self.__fot = fot              #人体に対する形態係数
        #self.__floor = floor          #床フラグ
        
        #形態係数収録用リストの定義
        self.__FF = []
        
        #透過日射の室内部位表面吸収日射量の初期化
        self.__RSsol = 0.0

        #庇フラグの初期化
        self.__sunbrkflg = False
        #窓フラグの初期化
        self.__windowflg = False
        #開口部透過日射量、吸収日射量の初期化
        self.__Qgt = 0.0
        self.__Qga = 0.0
        #相当外気温度の初期化
        self.__Teo = 15.0
        self.__oldTeo = 15.0

        self.__Nroot = 0

        self.__Qt = 0.0
        self.__oldTeo = 15.0                         #前時刻の室外側温度
        self.__oldqi = 0.0                          #前時刻の室内側表面熱流
        #print(self.__unsteady)
        # 壁体の初期化
        if self.__unsteady == True :
            #print(self.__name)
            
            self.__Row = WallMng.Row(self.__name)        #公比の取得
            self.__Nroot = WallMng.Nroot(self.__name)    #根の数
            self.__RFT0 = WallMng.RFT0(self.__name)      #貫流応答の初項
            self.__RFA0 = WallMng.RFA0(self.__name)      #吸熱応答の初項
            self.__RFT1 = WallMng.RFT1(self.__name)      #指数項別貫流応答の初項
            self.__RFA1 = WallMng.RFA1(self.__name)      #指数項別吸熱応答の初項
            self.__oldTsd_a = []
            self.__oldTsd_t = []
            self.__oldTsd_a = [ [ 0.0 for i in range(1) ] for j in range(self.__Nroot) ]
            self.__oldTsd_t = [ [ 0.0 for i in range(1) ] for j in range(self.__Nroot) ]
            # self.__oldTsd_t = range(0, self.__Nroot-1)   #貫流応答の表面温度の履歴
            # self.__oldTsd_a = range(0, self.__Nroot-1)   #吸熱応答の表面温度の履歴
            self.__hi = WallMng.hi(self.__name)          #室内側表面総合熱伝達率
            self.__hic = WallMng.hic(self.__name)        #室内側表面対流熱伝達率
            self.__hir = WallMng.hir(self.__name)        #室内側表面放射熱伝達率
            self.__ho = WallMng.ho(self.__name)          #室外側表面総合熱伝達率
            self.__as = WallMng.Solas(self.__name)       #室側側日射吸収率
            self.__Eo = WallMng.Eo(self.__name)          #室内側表面総合熱伝達率
            #print('RFT0=', self.__RFT0)
            #print('RFA0=', self.__RFA0)
            #print('hi=', self.__hi)
        # 定常部位の初期化
        else:
            self.__objWindow = WindowMng.Window(self.__name)
            objWindow = WindowMng.Window(self.__name)    #Windowオブジェクトの取得
            self.__windowflg = True
            self.__tau = objWindow.T()        #日射透過率
            self.__B = objWindow.B()          #吸収日射取得率
            self.__Uso = objWindow.Uso()      #熱貫流率（表面熱伝達抵抗除く）
            self.__RFA0 = 1.0 / self.__Uso                 #吸熱応答係数の初項
            self.__RFT0 = 1.0                              #貫流応答係数の初項
            self.__hi = objWindow.hi()        #室内側表面総合熱伝達率
            self.__hic = objWindow.hic()      #室内側表面対流熱伝達率
            self.__hir = objWindow.hir()      #室内側表面放射熱伝達率
            self.__ho = objWindow.ho()        #室外側表面総合熱伝達率
            self.__U = 1.0 / (1.0 / self.__Uso + 1.0 / self.__hi)   #熱貫流率（表面熱伝達抵抗含む）
            self.__Eo = objWindow.Eo()        #室内側表面総合熱伝達率
            self.__sunbrkflg = len(self.__sunbreakname) > 0  #庇がついているかのフラグ
            if self.__sunbrkflg:
                self.__sunbkr = SunbrkMng.Sunbrk(self.__sunbreakname)
    
    #畳み込み演算のためのメモリ確保
    # def Tsd_malloc(self):
    #     self.__oldTsd_a = [ [ 0.0 for i in range(1) ] for j in range(self.__Nroot) ]
    #     self.__oldTsd_t = [ [ 0.0 for i in range(1) ] for j in range(self.__Nroot) ]

    #畳み込み積分
    def convolution(self):
        sumTsd = 0.0
        for i in range(self.__Nroot):
            self.__oldTsd_t[i][0] = self.__oldTeo * self.__RFT1[i] \
                    + self.__Row[i] * self.__oldTsd_t[i][0]
            self.__oldTsd_a[i][0] = self.__oldqi * self.__RFA1[i] \
                    + self.__Row[i] * self.__oldTsd_a[i][0]
            sumTsd += self.__oldTsd_t[i][0] + self.__oldTsd_a[i][0]
        
        return sumTsd

    #人体に対する当該部位の形態係数の取得
    def fot(self):
        return self.__fot
    #表面温度の計算
    def setTs(self, Ts):
        self.__Ts = Ts
    #表面温度の取得
    def Ts(self):
        return self.__Ts
    #室内等価温度の計算
    def calcTei(self, Tr, Tsx, Lr, Beta):
        self.__Tei = Tr * self.__hic / self.__hi \
                + Tsx * self.__hir / self.__hi \
                + self.__RSsol / self.__hi \
                + self.__flr * Lr * (1.0 - Beta) / self.__hi / self.__area
    
    #前時刻の室内表面熱流の取得
    def oldqi(self):
        return self.__oldqi
    #室内表面熱流の計算
    def calcqi(self, Tr, Tsx, Lr, Beta):
        #前時刻熱流の保持
        self.__oldqi = self.__Qt / self.__area

        #対流成分
        self.__Qc = self.__hic * self.__area * (Tr - self.__Ts)
        #放射成分
        self.__Qr = self.__hir * self.__area * (Tsx - self.__Ts)
        #短波長熱取得成分
        self.__RS = self.__RSsol * self.__area
        #放射暖房成分
        self.__Lr = self.__flr * Lr * (1.0 - Beta)
        #表面熱流合計
        self.__Qt = self.__Qc + self.__Qr + self.__Lr + self.__RS

    #透過日射の室内部位表面吸収日射量の初期化
    def calcRSsol(self, TotalQgt):
        self.__RSsol = TotalQgt * self.__SolR / self.__area
        # print(self.__boundary, self.__RSsol)

    #透過日射の室内部位表面吸収日射の取得
    def RSsol(self):
        return self.__RSsol

    #透過日射の室内部位表面吸収比率の設定
    def setSolR(self, SolR):
        self.__SolR = SolR

    #境界条件
    def boundary(self):
        return self.__boundary

    #相当外気温度の計算
    def calcTeo(self, Ta, RN, oldTr, spaces):
        self.__oldTeo = self.__Teo
        #非定常部位の場合
        if self.__unsteady:
            #外皮の場合（相当外気温度もしくは隣室温度差係数から計算）
            if self.__skin:
                self.__Teo = self.__objExsrf.Te(self.__as, self.__ho, \
                        self.__Eo, Ta, RN, oldTr)
            #内壁の場合（前時刻の室温）
            else:
                self.__Teo = spaces.oldTr2(self.__boundary)
        #定常部位（窓）の場合
        else:
            #外皮の場合
            if self.__skin:
                self.__Teo = self.__Qga / self.__area / self.__U \
                        - self.__Eo * self.__objExsrf.Fs() * RN / self.__ho \
                        + Ta
            #内壁の場合（前時刻の室温）
            else:
                self.__Teo = spaces.oldTr2(self.__boundary)

    #相当外気温度の取得
    def Teo(self):
        return self.__Teo
    #前時刻の相当外気温度の取得
    def oldTeo(self):
        return self.__oldTeo
    
    #非定常フラグの取得
    def unstrady(self):
        return self.__unsteady

    #地面反射率の取得
    def rg(self):
        return self.__objExsrf.Rg()

    #透過日射量、吸収日射量の計算
    def calcQgt_Qga(self):
        #直達成分
        Qgtd = self.__objWindow.QGTD(self.__Id, self.__objExsrf.CosT(), self.__Fsdw) * self.__area
        #拡散成分
        Qgts = self.__objWindow.QGTS(self.__Isky, self.__Ir) * self.__area
        #透過日射量の計算
        self.__Qgt = Qgtd + Qgts
        #吸収日射量
        self.__Qga = self.__objWindow.QGA(self.__Id, self.__Isky, \
                self.__Ir, self.__objExsrf.CosT(), self.__Fsdw) * self.__area
    #透過日射量の取得
    def Qgt(self):
        return self.__Qgt
    #吸収日射量の取得
    def Qga(self):
        return self.__Qga
    #庇名称の取得
    def sunbrkname(self):
        return self.__sunbreakname

    #庇の有無フラグ
    def sunbrkflg(self):
        return self.__sunbrkflg

    #窓フラグ
    def windowflg(self):
        return self.__windowflg

    #日影面積率の計算
    def calcFsdw(self, Solpos):
        self.__Fsdw = self.__sunbkr.FSDW(Solpos, self.__objExsrf.Wa())

    #日影面積を取得
    def Fsdw(self, Solpos):
        return self.__sunbkr.FSDW(Solpos)

    #日影面積をセット
    def setFsdw(self, Fsdw):
        self.__Fsdw = Fsdw

    #床フラグの取得
    def Floor(self):
        return self.__floor
    
    #部位面積の取得
    def area(self):
        return self.__area
    
    #応答係数の初項の取得
    def RFA0(self):
        return self.__RFA0
    def RFT0(self):
        return self.__RFT0
    
    #指数項別応答係数
    def RFA1(self):
        return self.__RFA1
    def RFT1(self):
        return self.__RFT1
    
    #公比の取得
    def Row(self):
        if self.__unsteady == True:
            return self.__Row
        else:
            return 0
    
    #室内側表面総合熱伝達率
    def hi(self):
        return self.__hi
    
    #放射暖房吸収比率の取得
    def flr(self):
        return self.__flr
    
    #放射熱伝達率の取得
    def hir(self):
        return self.__hir
    
    #対流熱伝達率の取得
    def hic(self):
        return self.__hic
    
    #形態係数収録用メモリの確保
    #def FF_alloc(self, Nsurf):
    #    self.__FF = [0:Nsurf-1]
    #    #self.__FF = range(0, Nsurf-1)
    #    print('FFの要素数=', len(self.__FF))
    
    #傾斜面日射量を計算する
    def update_slope_sol(self):
        #直達日射量
        self.__Id = self.__objExsrf.Id()
        #天空日射量
        self.__Isky = self.__objExsrf.Isk()
        #反射日射量
        self.__Ir = self.__objExsrf.Ir()
        #全天日射量
        self.__Iw = self.__Id + self.__Isky + self.__Ir
    
    #傾斜面日射量の出力
    def print_slope_sol(self):
        print(self.__boundary, self.__name)
        print('直達日射量[W/m2]：', self.__Id)
        print('天空日射量[W/m2]：', self.__Isky)
        print('反射日射量[W/m2]：', self.__Ir)
        print('全天日射量[W/m2]：', self.__Iw)
    
    #部位の情報出力
    def print_surface(self):
        print(self.__boundary, self.__name)
        print('面積[m2]', self.__area)
    
    #外皮フラグを返す
    def skin(self):
        return self.__skin
    
    #形態係数の設定
    def setFF(self, FFd):
        self.__FF.append(FFd)
    #形態係数の取得
    def FF(self, i):
        return self.__FF[i]

# ## ２）室間換気量に関するクラス

# 室間換気量に関する情報を保持します。
# 
# - roomname:      流入室名称
# - winter:        暖房期の流入量, m3/h
# - inter:         中間期の流入量, m3/h
# - summer:        冷房期の流入量, m3/h

# In[11]:


class NextVent:
    def __init__(self, Windward_roomname, Windward_roomdiv, Leeward_roomname, Leeward_roomdiv, Season, VentVolume):
        #風上室用途
        self.__Windward_roomname = Windward_roomname
        #風上室名
        self.__Windward_roomdiv = Windward_roomdiv
        
        #風下室用途
        self.__Leeward_roomname = Leeward_roomname
        self.__Leeward_roomdiv = Leeward_roomdiv
        #季節の設定
        self.__Season = Season
        #室間換気量
        self.__VentVolume = VentVolume

        # self.__SeasonalValue = SeasonalValue(winter, inter, summer)
        
        #風上室の室温を初期化
        self.__oldTr = 15.0
        
#        self.__winter = winter                     #暖房期の流入量
#        self.__inter = inter                       #中間期の流入量
#        self.__summer = summer                     #冷房期の流入量
    
    #風上室の室温を更新
    def update_oldTr(self, oldTr):
        self.__oldTr = oldTr
    
    #風上室の室用途を返す
    def Windward_roomname(self):
        return self.__Windward_roomname
    #風上室の室名称を返す
    def Windward_roomdiv(self):
        return self.__Windward_roomdiv
    
    #風下室の室用途を返す
    def Leeward_roomname(self):
        return self.__Leeward_roomname
    #風下室の室名称を返す
    def Leeward_roomdiv(self):
        return self.__Leeward_roomdiv
    
    #季節名称を返す
    def Season(self):
        return self.__Season

    #風量を返す
    def next_vent(self) :
        return self.__VentVolume
    
    #前時刻の隣室温度を返す
    def oldTr(self):
        return self.__oldTr


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

# In[12]:


# 空間に関する情報の保持
class Space:
    FsolFlr = 0.5                                 #床の日射吸収比率
    # 初期化
    def __init__(self, Gdata, ExsrfMng, WallMng, WindowMng, SunbrkMng, roomname, roomdiv,\
            HeatCcap, HeatRcap, CoolCcap, Vol, Fnt, Vent, Inf, CrossVentRoom,\
            RadHeat, Beta, RoomtoRoomVents, Surfaces):
        self.__roomname = roomname                #室用途（主たる居室、その他居室、非居室）
        self.__roomdiv = roomdiv                  #室名称（主寝室、子供室1、子供室2、和室）
        self.__AnnualLoadcC = 0.0                 #年間冷房熱負荷（対流成分）
        self.__AnnualLoadcH = 0.0                 #年間暖房熱負荷（対流成分）
        self.__AnnualLoadrC = 0.0                 #年間冷房熱負荷（放射成分）
        self.__AnnualLoadrH = 0.0                 #年間暖房熱負荷（放射成分）
        self.__Tr = 15.0                          #室温の初期化
        self.__oldTr = 15.0                       #前時刻の室温の初期化
        self.__kc = 0.5                           #人体表面の熱伝達率の対流成分比率
        self.__kr = 0.5                           #人体表面の熱伝達率の放射成分比率
        self.__HeatCcap = HeatCcap                #最大暖房能力（対流）
        self.__HeatRcap = HeatRcap                #最大暖房能力（放射）
        self.__CoolCcap = CoolCcap                #最大冷房能力（対流）
        #self.__CoolRcap = CoolRcap                #最大冷房能力（放射）
        self.__Vol = Vol                          #室気積
        self.__Fnt = Fnt                          #家具熱容量
        #print(self.__Vol, self.__Fnt)
        #print(self.__Vol * 1.2 * 1005.0)
        #print(self.__Vol * self.__Fnt * 1000.0)
        #print('aaaaa')
        #print('Hcap=', self.__Hcap)
        # 室空気の熱容量（家具を含む）
        self.__Hcap = self.__Vol * 1.2 * 1005.0 + self.__Vol * self.__Fnt * 1000.0
        #print(self.__Hcap)
        self.__Vent = SeasonalValue(Vent.winter(), Vent.inter(), Vent.summer())
        #self.__Vent = Vent                        #計画換気量
        #print(self.__Vent)
        #self.__Inf = Inf                          #すきま風量
        self.__Inf = SeasonalValue(Inf.winter(), Inf.inter(), Inf.summer())
        self.__CrossVentRoom = CrossVentRoom      #通風対象室フラグ
        self.__RadHeat = RadHeat                  #放射暖房設置フラグ
        self.__Beta = Beta                        #放射暖房対流比率
        #self.__oldNextRoom = []
        #self.__NextVent = []

        #内部発熱の初期化
        #機器顕熱
        self.__Appl = 0.0
        #照明
        self.__Light = 0.0
        #人体顕熱
        self.__Human = 0.0
        #内部発熱合計
        self.__Hn = 0.0
        
        #室透過日射熱取得の初期化
        self.__Qgt = 0.0

        #室間換気量クラスの構築
        self.__RoomtoRoomVent = []
        prevroomname = ''
        prevroomdiv = ''
        # winter_vent = 0.0
        # inter_vent = 0.0
        # summer_vent = 0.0
        for room_vent in RoomtoRoomVents:
            #if room_vent['Windward_roomname'] != prevroomname and room_vent['Windward_roomdiv'] != prevroomdiv:
            self.__RoomtoRoomVent.append(NextVent(prevroomname, prevroomdiv, self.__roomname, self.__roomdiv,\
                    room_vent['Season'], room_vent['VentVolume']))
            # winter_vent = 0.0
            # inter_vent = 0.0
            # summer_vent = 0.0
            
            # prevroomname = room_vent['Windward_roomname']
            # prevroomdiv = room_vent['Windward_roomdiv']
            # if room_vent['Season'] == '冬期':
            #     winter_vent = room_vent['VentVolume']
            # elif room_vent['Season'] == '中間期':
            #     inter_vent = room_vent['VentVolume']
            # elif room_vent['Season'] == '夏期':
            #     summer_vent = room_vent['VentVolume']
            # else:
            #     print('RoomtoRoomVent.csv 未定義の季節', room_vent['Season'])
        #残ったバッファを吐き出し
        # if winter_vent > 0. or inter_vent > 0. or summer_vent > 0.:
        #     self.__RoomtoRoomVent.append(NextVent(prevroomname, prevroomdiv, self.__roomname, self.__roomdiv, \
        #             winter_vent, inter_vent, summer_vent))
        
        #print(self.__RoomtoRoomVent)
        
        #self.__RoomtoRoomVent = RoomtoRoomVents
        #print(self.__RoomtoRoomVent)
        #for i in range(1, 3):
        #    for j in range(0, len(NextVent)):
        #        self.__NextVent[i][j] = NextVent[i][j]    #室間換気量
        #        self.__oldNextRoom[j] = 15.0              #風上室の前時刻の温度
        self.__Nsurf = 0                           #部位の数
        self.__Surface = []
        #def __init__(self, ExsrfMng, WallMng, WindowMng, SunbrkMng, skin, boundary, \
        #         unsteady, name, area, sunbreak, flr, fot):
        
        #部位表面
        for d_surface in Surfaces:
            self.__Surface.append(Surface(ExsrfMng, WallMng, WindowMng, SunbrkMng, \
                    d_surface['skin'], d_surface['boundary'], d_surface['unsteady'], d_surface['name'],\
                    d_surface['area'], d_surface['sunbrk'], d_surface['flr'], d_surface['fot']))
            
        #print('self.__Surfaceの型：', type(self.__Surface))
        #print(Surfaces)
        #for d_surface in Surfaces:
        #    print(d_surface['name'])
        #    self.__Surface.append(Surface(WallMng, d_surface['skin'], d_surface['boundary'], d_surface['unsteady'], \
        #                                  d_surface['name'], d_surface['area'], d_surface['sunbreak'], \
        #                                  d_surface['flr'], d_surface['fot']))
        #    self.__Nsurf += 1                         #定義部位数をインクリメント
        #部位表面数
        #self.__Nsurf = 5
        self.__Nsurf = len(self.__Surface)
        #print(self.__Nsurf)
        
        #面対面の形態係数の計算
        self.__Atotal = 0.0
        self.__TotalAF = 0.0
        
        #print('合計面積1=', self.__Atotal)
        #合計面積の計算
        for surface in self.__Surface:
            self.__Atotal += surface.area()
            #合計床面積の計算
            if surface.Floor() == True:
                self.__TotalAF += surface.area()
        
        #print('合計表面積=', self.__Atotal)
        #形態係数の計算（面積比）
        i = 0
        for surface in self.__Surface:
            j = 0
            #形態係数収録用メモリの確保
            #surface.FF_alloc(self.__Nsurf)
            for nxtsurface in self.__Surface:
                surface.setFF(nxtsurface.area() / self.__Atotal)
                #print(i, j, surface.FF(j))
                j += 1
            i += 1
        
        #透過日射の室内部位表面吸収比率の計算
        #床に集中的に吸収させ、残りは表面積で案分
        #床の1次入射比率
        FsolFlr = Gdata.FsolFlr()
        TotalR = 0.0
        #床を除いた室内合計表面積の計算
        temp = self.__Atotal - self.__TotalAF

        for surface in self.__Surface:
            #床の室内部位表面吸収比率の設定
            if surface.Floor() == True:
                SolR = FsolFlr * surface.area() / self.__TotalAF
            #床以外は面積案分
            else:
                #室に床がある場合
                if self.__TotalAF > 0.0:
                    SolR = surface.area() / temp * (1. - FsolFlr)
                #床がない場合
                else:
                    SolR = surface.area() / temp
            surface.setSolR(SolR)
            #室内部位表面吸収比率の合計値（チェック用）
            TotalR += SolR
        #日射吸収率の合計値のチェック
        if abs(TotalR - 1.0) > 0.00001:
            print(self.__roomdiv, '日射吸収比率合計値エラー', TotalR)

        #畳み込み演算のためのメモリー確保
        # for surface in self.__Surface:
        #     surface.Tsd_malloc()

        #放射収支計算のための行列準備
        #行列の準備と初期化
        #[AX]
        self.__matAXd = [ [ 0.0 for i in range(self.__Nsurf) ] for j in range(self.__Nsurf) ]
        #{FIA}
        self.__matFIA = [ [ 0.0 for i in range(1) ] for j in range(self.__Nsurf) ]
        #{CRX}
        self.__matCRX = [ [ 0.0 for i in range(1) ] for j in range(self.__Nsurf) ]
        #{CVL}
        self.__matCVL = [ [ 0.0 for i in range(1) ] for j in range(self.__Nsurf) ]
        #{FLB}
        self.__matFLB = [ [ 0.0 for i in range(1) ] for j in range(self.__Nsurf) ]
        #{WSC}
        self.__matWSC = [ [ 0.0 for i in range(1) ] for j in range(self.__Nsurf) ]
        #{WSR}
        #self.__matWSR = [ [ 0.0 for i in range(1) ] for j in range(self.__Nsurf) ]
        #{WSV}
        self.__matWSV = [ [ 0.0 for i in range(1) ] for j in range(self.__Nsurf) ]
        #{WSB}
        #self.__matWSB = [ [ 0.0 for i in range(1) ] for j in range(self.__Nsurf) ]
        
        #print('FIA[len]=', len(self.__matFIA))
        i = 0
        for surface in self.__Surface:
            #matFIAの作成
            #print('RFA0=', surface.RFA0(), 'hi=', surface.hi())
            self.__matFIA[i][0] = surface.RFA0() * surface.hic()
            #print('i=', i, 'FIA=', self.__matFIA[i][0])
            #FLB=φA0×flr×(1-Beta)
            self.__matFLB[i][0] = surface.RFA0() * surface.flr()                         * (1. - self.__Beta) / surface.area()
            
            #放射計算のマトリックス作成
            for j in range(self.__Nsurf):
                #print('i=', i, 'j=', j)
                #print('FIA=', self.__matFIA[0][i])
                #print('FF=', surface.FF(j))
                #対角要素
                if i == j:
                    self.__matAXd[i][j] = 1. + surface.RFA0() * surface.hi()\
                            - surface.RFA0() * surface.hir() * surface.FF(j)
                #対角要素以外
                else:
                    self.__matAXd[i][j] = - surface.RFA0() * surface.hir() * surface.FF(j)
            #print('放射計算マトリックス作成完了')
            i += 1
        
        #print('[Matrix AXd]')
        #print(self.__matAXd)
        
        #逆行列の計算
        self.__matAX = np.linalg.inv(self.__matAXd)
        #print('[Matrix AX  inverse Matrix AXd]')
        #print(self.__matAX)
        #{WSR}の計算
        self.__matWSR = np.dot(self.__matAX, self.__matFIA)
        #print('[Matrix FIA]')
        #print(self.__matFIA)
        #print('[Matrix WSR]')
        #print(self.__matWSR)
        #{WSB}の計算
        self.__matWSB = np.dot(self.__matAX, self.__matFLB)
        #print('[Matrix FLB]')
        #print(self.__matFLB)
        #print('[Matrix WSB]')
        #print(self.__matWSB)
    
    #室用途を返す
    def name(self):
        return self.__roomname
    
    #室名を返す
    def roomdiv(self):
        return self.__roomdiv
    
    #室温を返す
    def oldTr(self):
        return self.__oldTr
    
    #室温、熱負荷の計算
    def calcHload(self, Gdata, spaces, dtmNow, defSolpos, Schedule, Weather, SunbrkMng):
        #室間換気の風上室温をアップデート
        for roomvent in self.__RoomtoRoomVent:
            roomvent.update_oldTr(spaces.oldTr(roomvent['Windward_roomname'], roomvent['Windward_roomdiv']))
            #print(roomvent.oldTr())
        
        #外皮の傾斜面日射量の計算
        for surface in self.__Surface:
            #surface.print_surface()
            #print(surface.skin())
            if surface.skin() == True:
                surface.update_slope_sol()
                #surface.print_slope_sol()
        
        #庇の日影面積率計算
        for surface in self.__Surface:
            if surface.sunbrkflg() == True:
                #Sunbrk = SunbrkMng.Sunbrk(surface.sunbrkname())
                #print(type(Sunbrk))
                #print('Name=', surface.sunbrkname())
                #日影面積率の計算
                surface.calcFsdw(defSolpos)
                #print('Name=', surface.sunbrkname(), 'Fsdw=', surface.Fsdw())
        
        #透過日射熱取得の初期化
        self.__Qgt = 0.0

        #透過日射吸収日射の計算
        for surface in self.__Surface:
            if surface.windowflg() == True:
                # print('透過日射量、吸収日射量の計算')
                # Idn = Weather.WeaData(enmWeatherComponent.Idn, dtmNow)
                # Isky = Weather.WeaData(enmWeatherComponent.Isky, dtmNow)
                # Ihol = Idn * math.sin(Weather.WeaData(enmWeatherComponent.h, dtmNow)) + Isky
                # Ir = Ihol * surface.rg()
                surface.calcQgt_Qga()
                # print(dtmNow, surface.Qgt(), surface.Qga())
                #透過日射熱取得の積算
                self.__Qgt += surface.Qgt()
        
        #相当外気温度の計算
        Ta = Weather.WeaData(enmWeatherComponent.Ta, dtmNow)
        RN = Weather.WeaData(enmWeatherComponent.RN, dtmNow)
        for surface in self.__Surface:
            surface.calcTeo(Ta, RN, self.__oldTr, spaces)
            # print(surface.boundary(), surface.Teo())

        #内部発熱の計算（すべて対流成分とする）
        self.__Appl = Schedule.Appl(self.__roomname, self.__roomdiv, \
                '顕熱', dtmNow)
        self.__Light = Schedule.Light(self.__roomname, self.__roomdiv, dtmNow)
        self.__Human = Schedule.Nresi(self.__roomname, self.__roomdiv, dtmNow) \
                * (63.0 - 4.0 * (self.__oldTr - 24.0))
        self.__Hn = self.__Appl + self.__Light + self.__Human

        #室内表面の吸収日射量
        for surface in self.__Surface:
            surface.calcRSsol(self.__Qgt)

        #流入外気風量の計算
        #計画換気・すきま風量
        season = Schedule.Season(dtmNow)
        if season == '暖房':
            self.__Ventset = self.__Vent.winter()
            self.__Infset = self.__Inf.winter()
        elif season == '中間':
            self.__Ventset = self.__Vent.inter()
            self.__Infset = self.__Inf.inter()
        elif season == '冷房':
            self.__Ventset = self.__Vent.summer()
            self.__Infset = self.__Inf.summer()
        #局所換気量
        self.__LocalVent = Schedule.LocalVent(self.__roomname, self.__roomdiv, dtmNow)

        #空調設定温度の取得
        self.__Tset = Schedule.ACSet(self.__roomname, self.__roomdiv, '温度', dtmNow)
        #空調発停信号
        self.__SW = 0
        if season == '暖房' and self.__Tset > 0.0:
            self.__SW = 1
        elif season == '冷房' and self.__Tset > 0.0:
            self.__SW = -1
        
        #室温・熱負荷計算のための係数の計算
        #BRM・BRLの初期化
        self.__BRM = 0.0
        self.__BRL = self.__Beta
        RMdT = self.__Hcap / Gdata.DTime()
        self.__BRM += RMdT
        #BRLの計算
        i = 0
        for surface in self.__Surface:
            #室内対流熱伝達率×面積[W/K]
            AF0 = surface.area() * surface.hic()
            temp = AF0 * (1.0 - self.__matWSR[i][0])
            #hc×A×(1-WSR)の積算
            self.__BRM += temp
            #BRLの計算
            self.__BRL += AF0 * self.__matWSB[i][0]
            i += 1
        
        #外気導入項の計算
        temp = conca * conrowa * \
                (self.__Ventset + self.__Infset + self.__LocalVent) / 3600.0
        self.__BRM += temp
        #室間換気
        for room_vent in self.__RoomtoRoomVent:
            if room_vent.Season() == season:
                temp = conca * conrowa * room_vent.next_vent() / 3600.0
                self.__BRM += temp
        
        #定数項の計算
        self.__BRC = 0.0
        #{WSC}、{CRX}の初期化
        self.__matWSC = [ [ 0.0 for i in range(1) ] for j in range(self.__Nsurf) ]
        self.__matCRX = [ [ 0.0 for i in range(1) ] for j in range(self.__Nsurf) ]
        
        #{CRX}の作成
        i = 0
        for surface in self.__Surface:
            self.__matCRX[i][0] = surface.RFT0() * surface.Teo() \
                    + surface.RSsol() * surface.RFA0()
            i += 1
        
        #{WSC}=[XA]*{CRX}
        self.__matWSC = np.dot(self.__matAX, self.__matCRX)
        #{BRC}の計算
        i = 0
        for surface in self.__Surface:
            NowQw = self.__matWSC[i][0] * surface.area() * surface.hic()
            self.__BRC += NowQw
            i += 1
        
        #外気流入風（換気＋すきま風）
        temp = conca * conrowa * \
                (self.__Ventset + self.__Infset + self.__LocalVent) \
                * Weather.WeaData(enmWeatherComponent.Ta, dtmNow) / 3600.0
        self.__BRC += temp
        
        #室間換気流入風
        for room_vent in self.__RoomtoRoomVent:
            if room_vent.Season() == season:
                temp = conca * conrowa * room_vent.next_vent() \
                        * room_vent.oldTr() / 3600.0
                self.__BRC += temp
        #RM/Δt*oldTrの項
        temp = self.__Hcap / Gdata.DTime() * self.__oldTr
        self.__BRC += temp

        #{WSV}、{CVL}の初期化
        self.__matWSV = [ [ 0.0 for i in range(1) ] for j in range(self.__Nsurf) ]
        self.__matCVL = [ [ 0.0 for i in range(1) ] for j in range(self.__Nsurf) ]
        
        #畳み込み演算
        i = 0
        for surface in self.__Surface:
            self.__matCVL[i][0] = surface.convolution()
            i += 1
        
        #{WSV}=[XA]*{CVL}
        self.__matWSV = np.dot(self.__matAX, self.__matCVL)
        #畳み込み後の室内表面温度の計算
        i = 0
        for surface in self.__Surface:
            temp = surface.area() * surface.hic() * self.__matWSV[i][0]
    
            self.__BRC += temp
            i += 1
        
        #定数項への内部発熱の加算
        self.__BRC += self.__Hn

        #OT制御の換算係数の計算
        if Gdata.OTset() == True:
            self.__Xot = 0.0
            self.__XLr = 0.0
            self.__XC = 0.0
            temp = 0.0
            XLr = 0.0
            XC = 0.0
            i = 0
            for surface in self.__Surface:
                temp += surface.fot() * self.__matWSR[i][0]
                XLr += surface.fot() * self.__matWSB[i][0]
                XC += surface.fot() * (self.__matWSC[i][0] + self.__matWSV[i][0])
                i += 1

            temp = self.__kc + self.__kr * temp
            self.__Xot = 1.0 / temp
            self.__XLr = self.__kr * XLr / temp
            self.__XC = self.__kr * XC / temp
            self.__BRMot = self.__BRM * self.__Xot
            self.__BRCot = self.__BRC + self.__BRM * self.__XC
            self.__BRLot = self.__BRL + self.__BRM * self.__XLr
        
        #### 通風計算はここに入れる（今回は未実装）

        #室温・熱負荷の計算
        Hcap = 0.0
        if self.__SW > 0:
            Hcap = self.__HeatCcap
        elif self.__SW < 0:
            Hcap = self.__CoolCcap
        
        #仮の室温、熱負荷の計算
        #室温設定の場合
        if Gdata.OTset() == False:
            self.__Tr, self.__Lcs, self.__Lr = self.calcTrLs(self.__SW, \
                    self.__RadHeat, self.__BRC, self.__BRM, \
                    self.__BRL, 0, 0, self.__Tset)
        #OT設定の場合
        else:
            self.__OT, self.__Lcs, self.__Lr = self.calcTrLs(self.__SW, \
                    self.__RadHeat, self.__BRCot, self.__BRMot, \
                    self.__BRLot, 0, 0, self.__Tset)
            #室温を計算
            self.__Tr = self.__Xot * self.__OT \
                    - self.__XLr * self.__Lr - self.__XC
        
        #最終的な運転フラグの設定
        self.__SW = self.resetSW(Hcap, self.__HeatRcap)

        #機器容量を再設定
        Hcap = 0.0
        if self.__SW > 0:
            Hcap = self.__HeatCcap
        elif self.__SW < 0:
            Hcap = self.__CoolCcap
        
        #最終室温・熱負荷の再計算
        if Gdata.OTset() == False:
            self.__Tr, self.__Lcs, self.__Lr = self.calcTrLs(self.__SW, \
                    self.__RadHeat, self.__BRC, self.__BRM, \
                    self.__BRL, Hcap, self.__HeatRcap, self.__Tset)
        #OT設定の場合
        else:
            self.__OT, self.__Lcs, self.__Lr = self.calcTrLs(self.__SW, \
                    self.__RadHeat, self.__BRCot, self.__BRMot, \
                    self.__BRLot, Hcap, self.__HeatRcap, self.__Tset)
            #室温を計算
            self.__Tr = self.__Xot * self.__OT \
                    - self.__XLr * self.__Lr - self.__XC
        
        #放射暖房最大能力が設定されている場合にはもう１度チェックする
        if self.__SW == 3 and self.__Lcs > Hcap and Hcap > 0.0:
            self.__SW = 5
            if Gdata.OTset() == False:
                self.__Tr, self.__Lcs, self.__Lr = self.calcTrLs(self.__SW, \
                        self.__RadHeat, self.__BRC, self.__BRM, \
                        self.__BRL, Hcap, self.__HeatRcap, self.__Tset)
            #OT設定の場合
            else:
                self.__OT, self.__Lcs, self.__Lr = self.calcTrLs(self.__SW, \
                        self.__RadHeat, self.__BRCot, self.__BRMot, \
                        self.__BRLot, Hcap, self.__HeatRcap, self.__Tset)
                #室温を計算
                self.__Tr = self.__Xot * self.__OT \
                        - self.__XLr * self.__Lr - self.__XC
            
        #年間熱負荷の積算
        #助走計算以外の時だけ積算
        if Gdata.FlgOrig(dtmNow) == True:
            #対流式空調の積算
            if self.__Lcs > 0.0:
                self.__AnnualLoadcH += self.__Lcs * Gdata.DTime() \
                        * 0.000000001
            else:
                self.__AnnualLoadcC += self.__Lcs * Gdata.DTime() \
                        * 0.000000001
            
            #放射式空調の積算
            if self.__Lcs > 0.0:
                self.__AnnualLoadrH += self.__Lr * Gdata.DTime() \
                        * 0.000000001
            else:
                self.__AnnualLoadrC += self.__Lr * Gdata.DTime() \
                        * 0.000000001
        #表面温度の計算
        self.__MRT = 0.0
        self.__AST = 0.0
        i = 0
        for surface in self.__Surface:
            Ts = self.__matWSR[i][0] * self.__Tr \
                    + self.__matWSC[i][0] + self.__matWSV[i][0] \
                    + self.__matWSB[i][0] * self.__Lr
            surface.setTs(Ts)
            print (Ts, "", end="")

            #人体に対する放射温度：MRT、面積荷重平均温度：ASTの計算
            self.__MRT += surface.fot() * surface.Ts()
            self.__AST += surface.area() * surface.Ts() / self.__Atotal
            i += 1
        print('')
        #室内側等価温度の計算
        for surface in self.__Surface:
            Tsx = 0.0

            j = 0
            #形態係数加重平均表面温度の計算
            for nxtsurface in self.__Surface:
                Tsx += nxtsurface.Ts() * nxtsurface.FF(j)
                j += 1

            #室内側等価温度の計算
            surface.calcTei(self.__Tr, Tsx, self.__Lr, self.__Beta)
            #室内表面熱流の計算
            surface.calcqi(self.__Tr, Tsx, self.__Lr, self.__Beta)

        #前時刻の室温の更新
        self.__oldTr = self.__Tr

        # print(dtmNow, self.__SW, self.__Qgt, self.__Tr, self.__Lcs)
        
        return 0

    #室温・熱負荷の計算ルーティン
    def calcTrLs(self, SW, RadHeat, BRC, BRM, BRL, \
            Hcap, Lrcap, Tset):
        Lcs = 0.0
        Lr = 0.0
        Tr = 0.0
        #非空調時の計算
        if SW == 0:
            Tr = BRC / BRM
        #熱負荷計算（最大能力無制限）
        elif SW == 1 or SW == -1 or SW == 4:
            #対流式空調の場合
            if RadHeat != True:
                Lcs = BRM * Tset - BRC
            #放射式空調
            else:
                Lr = (BRM * Tset - BRC) / BRL
            #室温の計算
            Tr = (BRC + Lcs + BRL * Lr) / BRM
        #対流空調最大能力運転
        elif (SW == 2 and Hcap > 0.0) or (SW == -2 and Hcap < 0.0):
            Lcs = Hcap
            Tr = (BRC + Hcap) / BRM
        #放射暖房最大能力運転（当面は暖房のみ）
        elif SW == 3 and Lrcap > 0.0:
            Lr = Lrcap
            #室温は対流式で維持する
            Lcs = BRM * Tset - BRC - Lr * BRL
            #室温の計算
            Tr = (BRC + Lcs + BRL * Lr) / BRM
        #放射空調も対流空調も最大能力運転
        elif SW == 5:
            #放射暖房、対流暖房ともに最大能力
            Lr = Lrcap
            Lcs = Hcap
            #室温を計算する
            Tr = (BRC + Lcs + BRL * Lr) / BRM
        
        #室温、対流空調熱負荷、放射空調熱負荷を返す
        return (Tr, Lcs, Lr)

    #最終の空調信号の計算
    def resetSW(self, Hcap, Lrcap):
        temp = self.__SW
    
        # 「冷房時の暖房」、「暖房時の冷房」判定
        if float(self.__SW) * (self.__Lcs + self.__Lr) < 0.0:
            temp = 0
        # 暖房の過負荷状態
        elif not self.__RadHeat and self.__SW == 1 and Hcap > 0.0 \
                and self.__Lcs > Hcap:
            temp = 2
        # 冷房の過負荷状態
        elif self.__SW == -1 and Hcap < 0.0 and self.__Lcs < Hcap:
            temp = -2
        # 放射暖房の過負荷状態
        elif self.__RadHeat and self.__SW == 1 and Lrcap > 0.0 \
                and self.__Lr > Lrcap:
            temp = 3
        # 放射暖房の過熱状態
        elif self.__RadHeat and self.__SW == 1 and Lrcap <= 0.0:
            temp = 4

        return temp

    #平均放射温度の計算
    def calcTsx(self):
        self.__Tsx = 0.0
        i = 0
        for surface in self.__Surface:
            self.__Tsx += surface.Ts() * surface.FF(i)
            i += 1

# ### Constructor parameters
# ```
# d = {
#     'Space': [
#         {
#             'roomname'             : # 室区分
#             'roomdiv'              : # 室名称
#             'HeatCcap'             : # 最大暖房能力（対流）[W]
#             'HeatRcap'             : # 最大暖房能力（放射）[W]
#             'CoolCcap'             : # 最大冷房能力（対流）[W]
#             'CoolRcap'             : # 最大冷房能力（放射）[W]
#             'Vol'                  : # 室気積, m3
#             'Fnt'                  : # 家具熱容量, kJ/m3K
#             'Vent': {              : # 計画換気量, m3/h
#                 'winter',
#                 'inter',
#                 'summer'
#             }
#             'Inf' : {
#                 'winter'           : #冬期のすきま風量, m3/h
#                 'inter'            : #中間期のすきま風量, m3/h
#                 'summer'           : #夏期のすきま風量, m3/h
#             }                      : # すきま風量[Season]（list型、暖房・中間期・冷房の順）, m3/h
#             'CrossVentRoom'        : # 通風計算対象室, False
#             'RadHeat'              : # 放射暖房対象室フラグ, True
#             'Beta'                 : # 放射暖房対流比率, －
#             'NextVent' : [         : # 室間換気量, m3/h
#                 {
#                     'name'         : #室名称
#                     'winter'       : #冬期のすきま風量, m3/h
#                     'inter'        : #中間期のすきま風量, m3/h
#                     'summer'       : #夏期のすきま風量, m3/h
#                 }
#             ]
#             'Surface' : [          : # 室内部位に関連するクラス, Surface
#                 {
#                     'skin'         : # 外皮フラグ, 外皮の場合True
#                     'boundary'     : # 方位・隣室名, string
#                     'unsteady'     : # 非定常フラグ, 非定常壁体の場合True
#                     'name'         : # 壁体・開口部名称, string
#                     'area'         : # 面積, m2
#                     'sunbreak'     : # ひさし名称, string
#                     'flr'          : # 放射暖房吸収比率, －
#                     'fot'          : # 人体に対する形態係数, －
#                     'floor'        : # 床フラグ, 床の場合True（日射が多く当たる）
#                 }
#             ]
#         }
#     ]
# }
# ```

# In[13]:


class SpaceMng:
    def __init__(self, Gdata, ExsrfMng, WallMng, WindowMng, SunbrkMng, d):
        #空間定義の配列を作成
        #self.__objSpaces = []
        #print(d)
        self.SpacedataRead(Gdata, ExsrfMng, WallMng, WindowMng, SunbrkMng, d)
        
    def SpacedataRead(self, Gdata, ExsrfMng, WallMng, WindowMng, SunbrkMng, d):
        for d_space in d:
            #print(d_space)
            #部位の情報を保持するクラスをインスタンス化
            Surfaces = []
            for d_surface in d_space['Surface']:
                #skin, boundary, unsteady, name, area, sunbreak, flr, fot, floor
                #surface = Surface(WallMng, WindowMng, SunbrkMng, d_surface['skin'], \
                #                  d_surface['boundary'], d_surface['unsteady'], \
                #                  d_surface['name'], d_surface['area'], \
                #                  d_surface['sunbrk'], \
                #                  d_surface['flr'], d_surface['fot'])
                Surfaces.append(d_surface)
                #print(d_surface['boundary'])
            
            #計画換気の読み込み
            Vent_season = d_space['Vent']
            #Vent_season = []
            #for d_vent in d_scpace['Vent']:
            #    Vent_season.append(d_vent)
            
            #すきま風の読み込み
            Inf_season = d_space['Inf']
            #Inf_season = []
            #for d_inf in d_space['Inf']:
            #    Inf_season.append(d_inf)
            
            #室間換気量の読み込み
            NextVentList = []
            for d_nextvent in d_space['NextVent']:
                next_vent = NextVent(d_nextvent['Windward_roomname'], d_nextvent['Windward_roomdiv'], \
                        d_nextvent['Leeward_roomname'], d_nextvent['Leeward_roomdiv'], \
                        d_nextvent['Season'], d_nextvent['VentVolume'])
                NextVentList.append(next_vent)
            
            self.__objSpace = []
            
            #空間情報を保持するクラスをインスタンス化
            #def __init__(self, ExsrfMng, WallMng, WindowMng, SunbrkMng, roomname, roomdiv, \
            #     HeatCcap, HeatRcap, \
            #     CoolCcap, Vol, Fnt, Vent, Inf, CrossVentRoom, \
            #     RadHeat, Beta, RoomtoRoomVents, Surfaces):
            space = Space(Gdata, ExsrfMng, WallMng, WindowMng, SunbrkMng, d_space['roomname'],\
                    d_space['roomdiv'], d_space['HeatCcap'],\
                    d_space['HeatRcap'], d_space['CoolCcap'], d_space['Vol'],\
                    d_space['Fnt'], d_space['Vent'], Inf_season,\
                    d_space['CrossVentRoom'], d_space['RadHeat'], d_space['Beta'], NextVentList, Surfaces)
            #print(space)
            self.__objSpace.append(space)
        
        #print(self.__objSpace)
        #return objSpace
    
    #前時刻の室温を取得する
    def oldTr(self, roomname, roomdiv):
        Tr = -999.0
        for space in self.__objSpace:
            if space.name() == roomname and space.roomdiv() == roomdiv:
                Tr = space.oldTr()
                break
        return Tr
    
    #室名称と室用途をつなげた名称から前時刻の室温を取得する
    def oldTr2(self, roomname_roomdib):
        Tr = -999.0
        for space in self.__objSpace:
            if space.name() + space.roomdiv() == roomname_roomdib:
                Tr = space.oldTr()
                break
        return Tr

    #室温、熱負荷の計算
    def calcHload(self, Gdata, dtmDate, objWdata, objSchedule, objSunbrk):
        for space in self.__objSpace:
            #def calcHload(self, spaces, SolarPosision, Schedule, Weather):
            space.calcHload(Gdata, self, dtmDate, objWdata.Solpos(dtmDate), objSchedule, objWdata, objSunbrk)

