
# coding: utf-8

# In[1]:


import math
import datetime
import nbimporter
import Exsrf
from Exsrf import Exsrf
import SolarPosision
from SolarPosision import defSolpos


# # 水平庇の影面積を計算する
# 
# ## 1) 庇の物理長さを保持するクラス
# - Name    ：日除け名称
# - D       ：庇の出巾[m]
# - WI1     ：向かって左側の庇のでっぱり[m]
# - WI2     ：向かって右側の庇のでっぱり[m]
# - hi      ：窓上端と庇までの距離[m]
# - WR      ：開口部巾[m]
# - WH      ：開口部高さ[m]
# - ########Wa      ：庇の設置してある窓の方位角[rad]

# In[2]:


# 水平庇の物理的な長さを保持するクラス

class SunbrkType:
    def __init__(self, Name, D, WI1, WI2, hi, WR, WH):
        # 日除け名称
        self.__Name = Name
        
        # 庇の出巾
        self.__D = float(D)
        
        # 向かって左側の庇のでっぱり
        self.__WI1 = float(WI1)
        # 向かって右側の庇のでっぱり
        self.__WI2 = float(WI2)
        
        # 窓上端から庇までの距離
        self.__hi = float(hi)
        
        # 開口部巾
        self.__WR = float(WR)
        # 開口部高さ
        self.__WH = float(WH)
        
        # 窓の方位角
#        self.__Wa = Wa
        
        # 開口部面積
        self.__A = self.__WR * self.__WH
    
    def Exsrf(self, Exsrf):
        self.__Wa = Exsrf.Wa()
    def Name(self):
        return self.__Name
    def D(self):
        return self.__D
    def WI1(self):
        return self.__WI1
    def WI2(self):
        return self.__WI2
    def hi(self):
        return self.__hi
    def WR(self):
        return self.__WR
    def WH(self):
        return self.__WH
    def Wa(self):
        return self.__Wa
    def A(self):
        return self.__A

    # 日除けの影面積を計算する
    def FSDW(self, defSolpos, Wa):
        # γの計算[rad]
        dblGamma = defSolpos.dblA - Wa
        # tan(プロファイル角)の計算
        dblTanFai = math.tan(defSolpos.dblh / math.cos(dblGamma))
        # print(defSolpos.dblh)
        # 日が出ているときだけ計算する
        if defSolpos.dblh > 0.0:
            # DPの計算[m]
            dblDP = self.__D * dblTanFai

            # DAの計算
            dblDA = self.__D * math.tan(dblGamma)
            dblABSDA = abs(dblDA)

            # WIの計算
            if dblDA > 0.:
                dblWI = self.__WI1
            else:
                dblWI = self.__WI2

            # DHAの計算
            dblDHA = min([max([0., dblWI * dblDP / max([dblWI, dblABSDA]) - self.__hi]), self.__WH])

            # DHBの計算
            dblDHB = min([max([0., (dblWI + self.__WR) * dblDP \
                    / max([dblWI + self.__WR, dblABSDA]) - self.__hi]), self.__WH])

            # DWAの計算
            if dblDP <= self.__hi:
                dblDWA = 0.
            else:
                dblDWA = min([max([0., (dblWI + self.__WR) - self.__hi * dblABSDA / dblDP]), self.__WR])

            # DWBの計算
            dblDWB = min([max([0., (dblWI + self.__WR) - (self.__hi + self.__WH) * dblABSDA /\
                    max([self.__hi + self.__WH, dblDP])]), self.__WR])

            # 日影面積の計算
            dblASDW = dblDWA * dblDHA + 0.5 * (dblDWA + dblDWB) * (dblDHB - dblDHA)

            # 日影面積率の計算
            dblFsdw = dblASDW / self.__A
        else:
            dblFsdw = 0.0
        return dblFsdw


# ## 2) 影面積を計算する
# 
# ### Constructor parameters
# ```
# d = {
#     'Sunbrk': [
#         {
#             'Name'           : # 開口部名称
#             'D'              : # 庇の出巾[m]
#             'WI1'            : # 向かって左側の庇のでっぱり[m]
#             'WI2'            : # 向かって右側の庇のでっぱり[m]
#             'hi'             : # 窓上端と庇までの距離[m]
#             'WR'             : # 窓の幅[m]
#             'WH'             : # 窓の高さ[m]
#             'Wa'             : # 設置方位角[rad]
#         }
#     ]
# }
# ```

# ### Class Definition

# In[3]:


class SunbrkMng:
    # 初期化
    def __init__(self, d):
        
        # 水平庇のインスタンスの配列を作成
        self.__objSunbrk=[]
        for d_sunbrk in d['Sunbrk']:
            sunbrk = SunbrkType(d_sunbrk['Name'], d_sunbrk['D'],                               d_sunbrk['WI1'], d_sunbrk['WI2'],                               d_sunbrk['hi'], d_sunbrk['WR'], d_sunbrk['WH'])
            self.__objSunbrk.append(sunbrk)
        # 庇の登録数を加算
        # self.__lngNSunbrk = len(self.__objSunbrk) - 1
        
        # 水平庇名称と登録番号の返還
        self.__dicSunbrkName = {}
        for lngI, x in enumerate(self.__objSunbrk):
            self.__dicSunbrkName[x.Name()] = lngI
    
    # 水平庇の部位情報の取得
    def Sunbrk(self, Name):
        objSunbrk = self.__objSunbrk[self.__dicSunbrkName[Name]]
        return objSunbrk


# ### Example

# In[4]:


# d = {
#     'Sunbrk': [
#         {
#             'Name'           : 'sunbrk_sample',
#             'D'              : 0.91,
#             'WI1'            : 0.29,
#             'WI2'            : 0.05,
#             'hi'             : 0.48,
#             'WR'             : 3.3,
#             'WH'             : 2.1,
# #            'Wa'             : 0.0
#         }
#     ]
# }


# # In[5]:


# sunbrk_mng = SunbrkMng(d)
# sunbrk = sunbrk_mng.Sunbrk('sunbrk_sample')
# print('Name=', sunbrk.Name())
# print('D=', sunbrk.D())
# print('WI1=', sunbrk.WI1())
# print('WI2=', sunbrk.WI2())
# print('hi=', sunbrk.hi())
# print('WR=', sunbrk.WR())
# print('WH=', sunbrk.WH())
# #print('Wa=', sunbrk.Wa())

