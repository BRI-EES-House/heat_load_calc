
# coding: utf-8

# In[1]:


import nbimporter


# In[2]:


import Exsrf
from Exsrf import Exsrf


# # 複数の外表面情報を保持するクラス

# - 外表面に関する入力情報を辞書型で受け取り、外表面関連情報を保持するクラスをインスタンス化します。
# - 複数の外表面情報を配列で保持します。
# 
# ### Constructor parameters
# ```
# d = {
#     'Surface': [
#         {
#             'Name'              : # 名称
#             'DirectionAngle'    : # 方位角
#             'InclinationAngle'  : # 傾斜角
#             'GroundReflectRate' : # 地面反射率
#             'TempDifferFactor'  : # 温度差係数
#         }
#     ]
# }
# ```
# ### Class Definition

# In[3]:


class ExsrfMng:
    
    # 初期化
    def __init__(self, d):
        
        # 外表面情報インスタンスの配列を作成
        self.__objExsrf = []
        for d_surface in d['Surface']:
            IsOuterSkin = True if abs(d_surface['TempDifferFactor']) < 0.000001 else False
            #print(IsOuterSkin)
            surface = Exsrf( d_surface['Name'], d_surface['DirectionAngle'], d_surface['InclinationAngle'], d_surface['GroundReflectRate'], d_surface['TempDifferFactor'], IsOuterSkin )
            self.__objExsrf.append(surface)
            
        # 壁体登録数
        self.__lngNExsrf = len( self.__objExsrf )
        
        # 外表面名称から外表面番号を変換する
        self.__dicExsrfName = {}
        for lngI, x in enumerate(self.__objExsrf):
            self.__dicExsrfName[x.Name()] = lngI
    
    # 傾斜面日射量の計算
    def CalcSlopSol(self, solpos, dblIdn, dblIsky):
        # solpos  : 太陽位置の情報を保持するクラス'defSolpos'
        # dblIdn  : 法線面直達日射量[W/m2]
        # dblIsky : 水平面天空日射量[W/m2]
        for obj in self.__objExsrf:
            obj.CalcSlopSol(solpos, dblIdn, dblIsky)
    
    # 名称から外表面情報を取得
    def ExsrfobjByName(self, strName):
        return self.__objExsrf[self.__dicExsrfName[strName]]
    
    # インデックスから外表面情報を取得
    def ExsrfobjByIndex(self, lngExsrf):
        return self.__objExsrf[lngExsrf]
    
    # 外表面の定義数を取得
    def N(self):
        return self.__lngNExsrf
    
    # 傾斜面日射量
    def Iwi(self, lngExsrf):
        Iwi = -999#
        if lngExsrf <= self.__lngNExsrf:
            Iwi = self.__objExsrf[lngExsrf].Iw()
        return Iwi
    
    # 傾斜面直達日射量
    def Idi(self, lngExsrf):
        Idi = -999#
        if lngExsrf <= self.__lngNExsrf:
            Idi = self.__objExsrf[lngExsrf].Id()
        return Idi
    
    # 傾斜面天空日射量
    def Iski(self, lngExsrf):
        Iski = -999#
        if lngExsrf <= self.__lngNExsrf:
            Iski = self.__objExsrf[lngExsrf].Isk()
        return Iski
    
    # 傾斜面反射日射量
    def Iri(self, lngExsrf):
        Iri = -999#
        if lngExsrf <= self.__lngNExsrf:
            Iri = self.__objExsrf[lngExsrf].Ir()
        return Iri


# # ### Example

# # In[4]:


# d = {
#     'Surface': [
#         {
#             'Name'              : 'North',
#             'DirectionAngle'    : 180,
#             'InclinationAngle'  : 90,
#             'GroundReflectRate' : 0.1,
#             'TempDifferFactor'  : 0.0
#         }
#     ]
# }

# exsrfmng = ExsrfMng( d )


# # ### Example
# # #### 外表面の各情報の取得

# # In[5]:


# print('名称：', exsrfmng.ExsrfobjByIndex(0).Name() )
# print('傾斜面方位角：', exsrfmng.ExsrfobjByIndex(0).Wa() )
# print('天空の形態係数：', exsrfmng.ExsrfobjByIndex(0).Fs() )
# print('外皮かどうか：', exsrfmng.ExsrfobjByIndex(0).Skin() )


# # #### 外表面の定義数を取得

# # In[6]:


# exsrfmng.N()


# # #### 傾斜面日射量を取得

# # In[7]:


# #exsrfmng.Iwi(0)

