
# coding: utf-8

# In[1]:


import nbimporter


# In[2]:


import Wall
from Wall import Layer, Wall, ResponseFactor


# # 複数の壁体情報を保持するクラス
# - 壁体に関する入力情報を辞書型で受け取り、壁体関連情報を保持するクラスをインスタンス化します。
# - 複数の壁体情報を配列で保持します。
# 
# ### Constructor parameters
# ```
# d = {
#     'Common': {
#         'Region'               : # 地域の区分 1 ~ 8 の整数
#         'TimeInterval'         : # 計算時間間隔[s]
#         'ResponseFactorCalculationHours': 応答係数を作成する時間数[h]
#     },
#     'Walls': [
#         {
#             'Name'             : # 壁体名称
#             'Layers' : [
#                 {
#                     'Name'     : # 部材名称　string値
#                     'Thick'    : # 厚さ[m]
#                     'Cond'     : # 熱伝導率[W/(m・K)]
#                     'SpecH'    : # 容積比熱[kJ/(m3・K)]
#                 }
#             ] # 層構成の情報
#             #室外側総合熱伝達率は壁体構成設定時に読み込むように仕様変更2018/8/24
#             ######'OutHeatTrans'     : # 室外側熱伝達率[W/(m2・K)]
#             'OutEmissiv'       : # 室外側放射率[-]
#             'OutSolarAbs'      : # 室外側日射吸収率[-]
#             'InConHeatTrans'   : # 室内対流熱伝達率[W/(m2･K)
#             'InRadHeatTrans'   : # 内放射熱伝達率[W/(m2･K)]
#         }
#     ]
# }
# ```
# ### Class Definition

# In[3]:


class WallMng:
    #@classmethod
    # 初期化
    def __init__( self, d ):
        #print('WallMng')
        #print(d)
        # 登録壁体インスタンスを設定
        self.__objWall = []
        self.WalldataRead( d )
        
        # 壁体登録数
        self.__lngNWall = len( self.__objWall ) - 1
        
        # 壁体名称→登録番号変換
        self.__dicWallname = {}
        for lngI, x in enumerate(self.__objWall):
            self.__dicWallname[x.Wall().Name()] = lngI

    # 壁体構成データの読み込みと応答係数の作成
    def WalldataRead( self, d ):
        
        # 時間間隔(s)
        #print('TimeInterval=', d['Common']['TimeInterval'])
        dblDTime = d['Common']['TimeInterval']

        # 応答係数を作成する時間数(h)
        dblNcalTime = d['Common']['ResponseFactorCalculationHours']
        
        #print('Dtime=', dblDTime)
        # 登録壁体インスタンスの配列を作成
        for d_wall in d['Walls']:
            #print('Walls Name=', d_wall['Name'])
            #print(d_wall)
            #print('wallname=', d_wall['Name'])
            # 壁体構成部材の情報を保持するクラスをインスタンス化
            layers = []
            for d_layers in d_wall['Layers']:
                #print('Layer Name=', d_layers['Name'])
                layer = Layer( d_layers['Name'], d_layers['Cond'], d_layers['SpecH'], d_layers['Thick'] )
                layers.append(layer)
            
            # 壁体情報を保持するクラスをインスタンス化
            wall = Wall( d_wall['Name'], d_wall['OutEmissiv'], d_wall['OutSolarAbs'], d_wall['InConHeatTrans'], d_wall['InRadHeatTrans'], layers )
            
            # 応答係数を保持するクラスをインスタンス化し、配列に格納
            rf = ResponseFactor( 'wall' , dblDTime, dblNcalTime, wall )
            self.__objWall.append(rf)
        #print('Walldata')
        #print(self.__objWall)
    
    # 壁体名称から二等辺三角波励振の貫流応答係数を返す
    def RFT(self, strWallname):
        return self.__objWall[self.__dicWallname[strWallname]].RFT()
    
    # 壁体名称から二等辺三角波励振の吸熱応答係数を返す
    def RFA(self, strWallname):
        return self.__objWall[self.__dicWallname[strWallname]].RFA()
    
    # 壁体名称から公比を返す
    def Row(self, strWallname):
        return self.__objWall[self.__dicWallname[strWallname]].Row()
    
    # 壁体名称から指数項別貫流応答係数を返す
    def RFT1(self, strWallname):
        return self.__objWall[self.__dicWallname[strWallname]].RFT1()
    
    # 壁体名称から指数項別吸熱応答係数を返す
    def RFA1(self, strWallname):
        return self.__objWall[self.__dicWallname[strWallname]].RFA1()

    # 壁体名称から貫流応答係数の初項を返す
    def RFT0(self, strWallname):
        return self.__objWall[self.__dicWallname[strWallname]].RFT0()
    
    # 壁体名称から吸熱応答係数の初項を返す
    def RFA0(self, strWallname):
        return self.__objWall[self.__dicWallname[strWallname]].RFA0()

    # 壁体名称から根の数を返す
    def Nroot(self, strWallname):
        return len(self.__objWall[self.__dicWallname[strWallname]].Alp())

    # 室内側熱伝達率
    def hi(self, strWallname):
        return self.__objWall[self.__dicWallname[strWallname]].Wall().hi()

    # 室内側対流熱伝達率
    def hic(self, strWallname):
        return self.__objWall[self.__dicWallname[strWallname]].Wall().hic()

    # 室内側放射熱伝達率
    def hir(self, strWallname):
        return self.__objWall[self.__dicWallname[strWallname]].Wall().hir()
    
    # 室外側熱伝達率
    def ho(self, strWallname):
        return self.__objWall[self.__dicWallname[strWallname]].Wall().ho()
    
    # 室外側放射率
    def Eo(self, strWallname):
        return self.__objWall[self.__dicWallname[strWallname]].Wall().Eo()
    
    # 室外側日射吸収率
    def Solas(self, strWallname):
        return self.__objWall[self.__dicWallname[strWallname]].Wall().Solas()


# ## Example

# In[4]:


# d = {
#     'Common': {
#         'Region': 6,
#         'TimeInterval': 3600,
#         'ResponseFactorCalculationHours': 50
#     },
#     'Walls': [
#         {
#             'Name': 'Ceiling',
#             'Layers': [
#                 {'Name': 'GW16K', 'Cond': 0.045, 'Thick': 0.0, 'SpecH': 13.0},
#                 {'Name': 'GPB', 'Cond': 0.22, 'Thick': 0.0095, 'SpecH': 830.0}
#             ],
# #            'OutHeatTrans' : 25.0,
#             'OutEmissiv' : 0.90,
#             'OutSolarAbs' : 0.80,
#             'InConHeatTrans' : 6.10,
#             'InRadHeatTrans' : 5.00
#         },
#         {
#             'Name': 'Wall_SW',
#             'Layers': [
#                 {'Name': 'GW16K', 'Cond': 0.045, 'Thick': 0.0, 'SpecH': 13.0},
#                 {'Name': 'GPB', 'Cond': 0.22, 'Thick': 0.0095, 'SpecH': 830.0}
#             ],
# #            'OutHeatTrans' : 25.0,
#             'OutEmissiv' : 0.90,
#             'OutSolarAbs' : 0.80,
#             'InConHeatTrans' : 4.10,
#             'InRadHeatTrans' : 5.00
#         }
#     ]
# }

# wallmng = WallMng( d )


# # ### 二等辺三角波励振の応答係数の取得

# # In[5]:


# print('二等辺三角波励振の貫流応答係数(12項まで)：', wallmng.RFT('Wall_SW')[:12] )
# print('二等辺三角波励振の吸熱応答係数(12項まで)：', wallmng.RFA('Wall_SW')[:12] )


# # ### 公比の取得

# # In[6]:


# wallmng.Row('Wall_SW')


# # ### 指数項別応答係数の取得

# # In[7]:


# print('指数項別貫流応答係数：', wallmng.RFT1('Wall_SW') )
# print('指数項別吸熱応答係数：', wallmng.RFA1('Wall_SW') )


# # ### 応答係数の初項の取得

# # In[8]:


# print('貫流応答の初項：', wallmng.RFT0('Wall_SW') )
# print('吸熱応答の初項：', wallmng.RFA0('Wall_SW') )


# # ### 根の数の取得

# # In[9]:


# wallmng.Nroot('Wall_SW')


# # ### 熱伝達率等の取得

# # In[10]:


# print('室内側熱伝達率　　：', wallmng.hi('Wall_SW') )
# print('室内側対流熱伝達率：', wallmng.hic('Wall_SW') )
# print('室内側放射熱伝達率：', wallmng.hir('Wall_SW') )
# print('室外側熱伝達率　　：', wallmng.ho('Wall_SW') )
# print('室外側放射率　　　：', wallmng.Eo('Wall_SW') )
# print('室外側日射吸収率　：', wallmng.Solas('Wall_SW') )

