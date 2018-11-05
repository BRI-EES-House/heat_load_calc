
# coding: utf-8

# In[1]:


import math
import datetime


# # 太陽位置を計算するクラス

# ## 1) 太陽位置を保持するクラス

# 太陽位置を保持するクラスを定義します。
# 
# - dbSh=sin(h)
# - dblSw=cos(h)*sin(A)
# - dblSs=cos(h)*cos(A)
# - dblh=太陽高度[rad]
# - dblA=太陽方位角[rad]

# In[2]:


# 太陽位置
# VBA では、mdlDefine モジュールにあったものを、モジュール　SolarPosision で記述することにした。
class defSolpos:
    
    def __init__(self, dblSh, dblSw, dblSs, dblh, dblA):
        
        # sin h
        self.dblSh = dblSh
        
        # cos h sin A
        self.dblSw = dblSw

        # cos h cos A
        self.dblSs = dblSs

        # 太陽高度
        self.dblh = dblh
        
        # 太陽方位角
        self.dblA = dblA
    
    # def dblh(self):
    #     return(self.dblh)
    # def dblA(self):
    #     return(self.dblA)
    # def dblSh(self):
    #     return(self.dblSh)
    # def dblSw(self):
    #     return(self.dblSw)
    # def dblSs(self):
    #     return(self.dblSs)


# ## 2) 太陽位置を計算するクラス
# - 太陽位置を計算します
# 
# ### Constructor parameters
# ```
# 'Lat'      ：緯度[゜]
# 'Lon'     ：経度[゜]
# 'Ls'       ：標準子午線[゜]
# ```
# 
# ### Class Definition

# In[3]:


class SolarPosision:
    
    # 冬至の日赤緯
    mconDelta0 = -23.4393
    
    # 
    lngN=1989-1968
    # 赤緯の正弦
    dblSinD=0.0
    # 赤緯の余弦
    dblCosD=0.0
    # 太陽位置収録クラス
    Solpos=defSolpos
    
    # 緯度経度を読み込み計算準備
    # 緯度、経度、標準子午線を引数として初期化する
    def __init__(self, Lat, Lon, Ls):
        
        # 緯度
        dblLat = math.radians(Lat)
        # 経度
        dblLon = math.radians(Lon)
        # 標準子午線
        dblLs = math.radians(Ls)
        
        #太陽位置クラスの初期化
        self.Solpos = defSolpos(0.0, 0.0, 0.0, 0.0, 0.0)

        # 地域情報の初期化
        self.__dblCosPhi = math.cos(dblLat)
        self.__dblSinPhi = math.sin(dblLat)
        self.__dblLLs = dblLon - dblLs
        self.__dblSinD0 = math.sin(math.radians(self.mconDelta0))
        self.__dblCoeff = 360.0 / 365.2596
        
    
    # 平均軌道上の近日点通過日（暦表時による1968年1月1日正午基準日差）
    def Calcd0(self):
        return 3.71 + 0.2596 * self.lngN - int((self.lngN + 3.0) / 4.0)
    # 均時差の計算
    def CalcEt(self,dtmDate):
        # 通日の計算
        lngNowNday=self.__Nday(dtmDate.month,dtmDate.day)
        
        # 平均近点離角Mの計算
        dblM = self.__dblCoeff * (lngNowNday-self.Calcd0())
        # 近日点と冬至点の角度
        dble=12.3901 + 0.0172 * (self.lngN + dblM / 360.0)
        # 真近点離角の計算
        dblV=dblM + 1.914 * math.sin(math.radians(dblM))                 + 0.02 * math.sin(math.radians(dblM * 2.0))
        
        dblRad2VE = math.radians(dblV + dble)
        # 赤緯の正弦
        self.dblSinD = math.cos(dblRad2VE) * self.__dblSinD0
        # 赤緯の余弦
        self.dblCosD = math.sqrt(1.0 - self.dblSinD * self.dblSinD)
        
        # 中心差による時差
        dblEt1 = dblM - dblV
        # 太陽赤経と太陽黄経の差
        dblRad2VE = dblRad2VE * 2.0
        dblEt2 = math.degrees(math.atan(0.043 * math.sin(dblRad2VE)                 / (1.0 - 0.043 * math.cos(dblRad2VE))))
        return dblEt1-dblEt2
    # 太陽位置を計算する
    def CalcSolpos(self, dtmDate):
        # dtmDate: Datetime型
        
        # 標準時の計算
        dblTm = dtmDate.hour + dtmDate.minute / 60.0 + dtmDate.second / 3600.0
        # 通日の計算
        lngNowNday = self.__Nday(dtmDate.month,dtmDate.day)
        # 均時差の計算
        dblEt=self.CalcEt(dtmDate)
        # 時角の計算
        dblT = math.radians(15.0 * (dblTm - 12.0) + math.degrees(self.__dblLLs) + dblEt)
        # print('Tm=',dblTm,'Et=',dblEt,'T=',dblT)
        # 太陽位置の計算
        self.Solpos.dblSh= max(self.__dblSinPhi * self.dblSinD             + self.__dblCosPhi * self.dblCosD * math.cos(dblT),0.0)
        # print('SinPhi=',self.__dblSinPhi,'SinD=',self.dblSinD,'CosPhi=',self.__dblCosPhi,'CosD=',self.dblCosD,'Sh=',self.Solpos.dblSh)
        # 太陽高度
        self.Solpos.dblh=math.asin(self.Solpos.dblSh)
        if self.Solpos.dblSh>0.:
            dblCosh=math.sqrt(1.0-self.Solpos.dblSh*self.Solpos.dblSh)
            dblSinA = self.dblCosD * math.sin(dblT) / dblCosh
            dblCosA = (self.Solpos.dblSh * self.__dblSinPhi - self.dblSinD)                 / (dblCosh * self.__dblCosPhi)
            dblTemp=1.0
            if dblT<0.0:
                dblTemp=-1.0
            self.Solpos.dblA = dblTemp * math.acos(dblCosA)
            self.Solpos.dblSs = dblCosh * dblCosA
            self.Solpos.dblSw = dblCosh * dblSinA
        else:
            self.Solpos.dblSs = 0.0
            self.Solpos.dblSw = 0.0
            self.Solpos.dblA = 0.0
        
        # print('h=',self.Solpos.dblh,'A=',self.Solpos.dblA)
        return(self.Solpos)
    #通日を計算するモジュール
    def __Nday(self,Mo,Day):
        NewYear = datetime.datetime(2017,1,1)
        ThatDay = datetime.datetime(2017,Mo,Day)
        Ndays = ThatDay - NewYear
        return (Ndays.days + 1)


# ### Initialize Example
# - 緯度：34.6583333333333[゜]
# - 経度：133.918333333333[゜]
# - 標準子午線：135[゜]

# In[4]:


# s = SolarPosision(34.6583333333333, 133.918333333333, 135)


# # ### Calculate Example
# # - 1989年2月1日12:00の太陽位置を計算する

# # In[5]:


# CalcDate=datetime.datetime(1989,2,1,12,0,0)
# print(CalcDate)
# sp=s.CalcSolpos(CalcDate)
# print('h=',sp.dblh,'A=',sp.dblA)

