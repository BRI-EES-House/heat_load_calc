
# coding: utf-8

# # 開口部透明部位の情報を保持するクラス

# ## 1) １つの開口部透明部位の情報を保持するクラス
# - 開口部透明部位の基本情報（開口部名称、日射熱取得率、熱貫流率等）を保持するクラスを定義します。
# 
# ### Constructor parameters
# ```
# 'Name'           : # 開口部名称
# 'Eta'            : # 日射熱取得率[-]
# 'SolarTrans'     : # 日射透過率[-]
# 'SolarAbsorp'    : # 吸収日射取得率[-]
# 'Uw'             : # 開口部熱貫流率[W/m2K]
# 'OutHeatTrans'   : # 室外側熱伝達率[W/(m2・K)]
# 'OutEmissiv'     : # 室外側放射率[-]
# 'InConHeatTrans' : # 室内対流熱伝達率[W/(m2･K)]
# 'InRadHeatTrans' : # 室内放射熱伝達率[W/(m2･K)]
# ```
# ### Class Definition

# In[1]:


class Window:
    
    # 初期化
    def __init__(self, Name, Eta, SolarTrans, SolarAbsorp, Uw, OutHeatTrans, OutEmissiv, InConHeatTrans, InRadHeatTrans ):
        self.__strName = Name           # 開口部名称, string値
        self.__dblEta = float(Eta)             # 日射熱取得率[-]
        self.__dblT = float(SolarTrans)        # 日射透過率[-]
        self.__dblB = float(SolarAbsorp)       # 吸収日射取得率[-]
        self.__dblUw = float(Uw)               # 開口部熱貫流率[W/m2K]
        self.__dblho = float(OutHeatTrans)     # 室外側熱伝達率[W/m2K]
        self.__dblEo = float(OutEmissiv)       # 室外側放射率[-]
        self.__dblhic = float(InConHeatTrans)  # 室内対流熱伝達率[W/(m2･K)]
        self.__dblhir = float(InRadHeatTrans)  # 室内放射熱伝達率[W/(m2･K)]
        
        # 室内総合熱伝達率[W/(m2･K)]
        self.__dblhi = self.__dblhic + self.__dblhir   

        # 窓部材熱抵抗[m2K/W]
        self.__dblRw = 1.0 / self.__dblUw - 1.0 / self.__dblhi - 1.0 / self.__dblho
        
        # 開口部の室内表面から屋外までの熱貫流率[W/(m2･K)]
        self.__dblUso = 1.0 / ( self.__dblRw + 1.0 / self.__dblho)
        
        # 拡散日射に対する入射角特性
        self.__condblCd = 0.92         
    
    # 名前の取得
    def Name(self):
        return self.__strName
    
    # 開口部の室内表面から屋外までの熱貫流率の取得
    def Uso(self):
        return self.__dblUso
    
    # 日射透過率の取得
    def T(self):
        return self.__dblT
    
    # 吸収日射取得率の取得
    def B(self):
        return self.__dblB
    
    # 室外側熱伝達率の取得
    def ho(self):
        return self.__dblho
    
    # 室内側熱伝達率の取得
    def hi(self):
        return self.__dblhi
    
    # 室内側対流熱伝達率の取得
    def hic(self):
        return self.__dblhic
    
    # 室内側放射熱伝達率の取得
    def hir(self):
        return self.__dblhir
    
    # 室外側放射率の取得
    def Eo(self):
        return self.__dblEo
    
    # 直達日射の入射角特性の計算
    def CID(self, dblCosT):
        return (2.392 * dblCosT - 3.8636 * dblCosT ** 3.0 + 3.7568 * dblCosT ** 5.0 - 1.3965 * dblCosT ** 7.0) / 0.88

    # 吸収日射熱取得[W/m2]の計算
    def QGA(self, dblId, dblIsk, dblIr, dblCosT, dblFsdw):
        # dblId   : 傾斜面入射直達日射量[W/m2]
        # dblIsk  : 傾斜面入射天空日射量[W/m2]
        # dblIr   : 傾斜面入射反射日射量[W/m2]
        # dblCosT : 入射角の方向余弦
        # dblFsdw : 日よけ等による日影面積率
        dblCID = self.CID(dblCosT)
        return self.__dblB * ((1.0 - dblFsdw) * dblCID * dblId + self.__condblCd * (dblIsk + dblIr))
    
    
    # 透過日射熱取得（直達成分）[W/m2]の計算
    def QGTD(self, dblId, dblCosT, dblFsdw):  
        # dblId   : 傾斜面入射直達日射量[W/m2]
        # dblCosT : 入射角の方向余弦
        # dblFsdw : 日よけ等による日影面積率
        return self.__dblT * (1.0 - dblFsdw) * self.CID(dblCosT) * dblId

    # 透過日射熱取得（拡散成分）[W/m2]の計算
    def QGTS(self, dblIsk, dblIr):
        # dblIsk:傾斜面入射天空日射量[W/m2]
        # dblIr:傾斜面入射反射日射量[W/m2]
        return self.__dblT * self.__condblCd * (dblIsk + dblIr)
                                                          
    # 透過日射熱取得[W/m2]の計算
    def QGT(self, dblId, dblIsk, dblIr, dblCosT, dblFsdw):
        # dblId   : 傾斜面入射直達日射量[W/m2]
        # dblIsk  : 傾斜面入射天空日射量[W/m2]
        # dblIr   : 傾斜面入射反射日射量[W/m2]
        # dblCosT : 入射角の方向余弦
        # dblFsdw : 日よけ等による日影面積率
        return self.QGTD(dblId, dblCosT, dblFsdw) + self.QGTS(dblIsk, dblIr)


# ## 2) 複数の開口部透明部位の情報を保持するクラス
# - 開口部透明部位に関する入力情報を辞書型で受け取り、開口部透明部位の情報を保持するクラスをインスタンス化します。
# - 複数の開口部透明部位の情報を配列で保持します。
# 
# ### Constructor parameters
# ```
# d = {
#     'Windows': [
#         {
#             'Name'           : # 開口部名称
#             'Eta'            : # 日射熱取得率[-]
#             'SolarTrans'     : # 日射透過率[-]
#             'SolarAbsorp'    : # 吸収日射取得率[-]
#             'Uw'             : # 開口部熱貫流率[W/m2K]
#             'OutHeatTrans'   : # 室外側熱伝達率[W/(m2・K)]
#             'OutEmissiv'     : # 室外側放射率[-]
#             'InConHeatTrans' : # 室内対流熱伝達率[W/(m2･K)]
#             'InRadHeatTrans' : # 室内放射熱伝達率[W/(m2･K)]
#         }
#     ]
# }
# ```
# ### Class Definition

# In[2]:


class WindowMng:
    
    # 初期化
    def __init__( self, d ):
        
        # 開口部透明部位インスタンスの配列を作成
        self.__objWindow = []
        for d_window in d['Windows']:
            window = Window( d_window['Name'], d_window['Eta'], d_window['SolarTrans'], d_window['SolarAbsorp'], d_window['Uw'], d_window['OutHeatTrans'], d_window['OutEmissiv'], d_window['InConHeatTrans'], d_window['InRadHeatTrans'] )
            self.__objWindow.append(window)
            
        # 開口部登録数
        # self.__lngNWindow = len( self.__objWindow ) - 1
        
        # 開口部名称→登録番号変換
        self.__dicWindowName = {}
        for lngI, x in enumerate(self.__objWindow):
            self.__dicWindowName[x.Name()] = lngI
            
    # 開口部透明部位情報の取得
    def Window(self, strName):
        #print('WindowName=', strName)
        return self.__objWindow[self.__dicWindowName[strName]]
    
    #日射透過率
    def T(self, strName):
        window_type = self.__objWindow[self.__dicWindowName[strName]]
        return window_type.T()


# ### Example

# In[3]:


# d = {
#     'Windows': [
#         {
#             'Name'           : 'Window_NW',
#             'Eta'            : 0.729,
#             'SolarTrans'     : 0.738,
#             'SolarAbsorp'    : 0.054,
#             'Uw'             : 4.65,
#             'OutHeatTrans'   : 25.0,
#             'OutEmissiv'     : 0.90,
#             'InConHeatTrans' : 4.1,
#             'InRadHeatTrans' : 5.0
#         }
#     ]
# }

# windowsmng = WindowMng( d )

# print(windowsmng.T('Window_NW'))


# # #### 開口部不透明部位の各種情報の取得

# # In[4]:


# print('開口部の室内表面から屋外までの熱貫流率 :', windowsmng.Window('Window_NW').Uso() )
# print('日射透過率 :', windowsmng.Window('Window_NW').T() )
# print('吸収日射取得率 :', windowsmng.Window('Window_NW').B() )
# print('室外側熱伝達率 :', windowsmng.Window('Window_NW').ho() )
# print('室内側熱伝達率 :', windowsmng.Window('Window_NW').hi() )
# print('室内側対流熱伝達率 :', windowsmng.Window('Window_NW').hic() )
# print('室内側放射熱伝達率 :', windowsmng.Window('Window_NW').hir() )
# print('室外側放射率 :', windowsmng.Window('Window_NW').Eo() )


# # #### 吸収日射熱取得[W/m2]の計算

# # In[5]:


# windowsmng.Window('Window_NW').QGA(425.1, 56.9, 15.4, 0.69, 0)


# # #### 透過日射熱取得[W/m2]の計算

# # In[6]:


# windowsmng.Window('Window_NW').QGT(425.1, 56.9, 15.4, 0.69, 0)

