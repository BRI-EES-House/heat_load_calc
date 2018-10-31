
# coding: utf-8

# In[1]:


import nbimporter
import math
import datetime


# In[2]:


from SolarPosision import defSolpos, SolarPosision


# # 外表面の情報を保持するクラス

# ## 1) １つの外表面の情報を保持するクラス
# - 外表面の基本情報（方位角、傾斜角、地面反射率、温度差係数等）を保持するクラスを定義します。
# 
# ### Constructor parameters
# ```
# 'Name'           　 : # 名称
# 'DirectionAngle' 　 : # 方位角[゜]
# 'InclinationAngle'  : # 傾斜角[゜]
# 'GroundReflectRate' : # 地面反射率[-]
# 'TempDifferFactor'  : # 温度差係数[-]
# 'IsOuterSkin': # 外皮かどうか, bool値
# ```
# ### Class Definition

# In[3]:


class Exsrf:
    
    # 初期化
    def __init__(self, Name, DirectionAngle, InclinationAngle, GroundReflectRate, TempDifferFactor, IsOuterSkin ):
        self.__strName = Name                         # 開口部名称, string値
        self.__dblWa = math.radians(DirectionAngle)   # 方位角[rad]
        self.__dblWb = math.radians(InclinationAngle) # 傾斜角[rad]
        self.__dblRg = GroundReflectRate              # 地面反射率[-]
        self.__dblR = TempDifferFactor                # 温度差係数[-]
        self.__blnSkin = IsOuterSkin                  # 外皮かどうか, bool値
        
        if self.__blnSkin == True:
            # 入射角計算のためのパラメータの計算
            self.__dblWz = math.cos(self.__dblWb)
            self.__dblWw = math.sin(self.__dblWb) * math.sin(self.__dblWa)
            self.__dblWs = math.sin(self.__dblWb) * math.cos(self.__dblWa)
            # 傾斜面の天空に対する形態係数の計算
            self.__dblFs = ( 1.0 + self.__dblWz ) / 2.0
            # 傾斜面の地面に対する形態係数
            self.__dblFg = 1.0 - self.__dblFs
            
    # 傾斜面日射量の計算
    # ※注意※　太陽位置の情報を保持するクラス'defSolpos'の定義に従って以下の処理を修正する必要があります
    def CalcSlopSol(self, solpos, dblIdn, dblIsky):
        # solpos  : 太陽位置の情報を保持するクラス'defSolpos'
        # dblIdn  : 法線面直達日射量[W/m2]
        # dblIsky : 水平面天空日射量[W/m2]
    
        # 外皮の場合
        if self.__blnSkin == True:
            # 入射角の計算
            self.__dblCosT = max( solpos.dblSh * self.__dblWz + solpos.dblSw * self.__dblWw + solpos.dblSs * self.__dblWs, 0.0 )    
            # 水平面全天日射量の計算
            dblIhol = solpos.dblSh * dblIdn + dblIsky
            # 傾斜面入射直達日射量の計算
            self.__dblId = self.__dblCosT * dblIdn
            # 傾斜面入射天空日射量の計算
            self.__dblIs = self.__dblFs * dblIsky
            # 傾斜面入射地面反射日射量の計算
            self.__dblIr = self.__dblFg * self.__dblRg * dblIhol
            # 傾斜面入射全日射量の計算
            self.__dblIw = self.__dblId + self.__dblIs + self.__dblIr
            
    # 傾斜面の相当外気温度の計算
    def Te(self, dblas, dblho, dble, dblTa, dblRN, dblTr):
        # dblas : 日射吸収率
        # dblho : 外表面の総合熱伝達率[W/m2K]
        # dble  : 外表面の放射率[-]
        # dblTa : 外気温度[℃]
        # dblRN : 夜間放射量[W/m2]
        # dblTr : 前時刻の自室室温[℃]（隣室温度計算用）

        if self.__blnSkin == True:
            te = dblTa + (dblas * self.__dblIw - self.__dblFs * dble * dblRN) / dblho
        else:
            te = self.__dblR * dblTa + (1.0 - self.__dblR) * dblTr
        
        return te
    
    # 傾斜面入射直達日射量の取得
    def Id(self):
        if self.__blnSkin:
            return self.__dblId
        else:
            return 0.

    # 傾斜面入射天空日射量の取得
    def Isk(self):
        if self.__blnSkin:
            return self.__dblIs
        else:
            return 0.

    # 傾斜面入射地面反射日射量の取得
    def Ir(self):
        if self.__blnSkin:
            return self.__dblIr
        else:
            return 0.
    
    # 傾斜面入射全天日射量の取得
    def Iw(self):
        if self.__blnSkin:
            return self.__dblIw
        else:
            return 0.

    # 入射角の方向余弦の取得
    def CosT(self):
        if self.__blnSkin:
            return self.__dblCosT
        else:
            return 0.

    # 傾斜面方位角
    def Wa(self):
        if self.__blnSkin:
            return self.__dblWa
        else:
            return -999.

    # 天空の形態係数
    def Fs(self):
        if self.__blnSkin:
            return self.__dblFs
        else:
            return -999.

    # 外皮かどうか
    def Skin(self):
        return self.__blnSkin

    # 外表面名称
    def Name(self):
        return self.__strName


# ### Example
# #### 外表面の各情報の取得

# In[4]:


# exsrf = Exsrf('North', 180, 90, 0.0, 0.0, True)
# print('名称：', exsrf.Name() )
# print('傾斜面方位角：', exsrf.Wa() )
# print('天空の形態係数：', exsrf.Fs() )
# print('外皮かどうか：', exsrf.Skin() )


# # In[5]:


# s = SolarPosision(34.6583333333333, 133.918333333333, 135)
# sp = s.CalcSolpos(datetime.datetime(2017,1,2,12,0,0))
# print(sp.dblSh,sp.dblSs,sp.dblSw)
# exsrf.CalcSlopSol(sp, 500, 100)
# print(exsrf.Iw())

