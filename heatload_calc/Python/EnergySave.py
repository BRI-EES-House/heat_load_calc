
# coding: utf-8

# # 省エネ手法の情報を保持するクラス

# - 省エネ手法に関する入力情報を辞書型で受け取り、省エネ手法の情報を保持するクラスをインスタンス化します。
# 
# ### Constructor parameters
# ```
# d = {
#     'EnergySave': {
#             'IsUseVentilation' : # 通風を利用するかどうか, bool値
#             'AirChangeRate'    : # 換気回数[回/h]
#             'IsUseHeatStorage' : # 蓄熱を利用するかどうか, bool値
#             'IsUseHEXVent'     : # 熱交換換気を利用するかどうか, bool値
#     }
# }
# ```
# ### Class Definition

# In[1]:


class EnergySave:
    
    # 初期化
    def __init__(self, d):
        # 通風の利用有無
        self.__blnCrossVent = d['EnergySave']['IsUseVentilation']
        # 通風の換気回数
        self.__dblVentRate = d['EnergySave']['AirChangeRate']
        # 蓄熱の有無
        self.__blnStorage = d['EnergySave']['IsUseHeatStorage']
        # 熱交換換気有無
        self.__blnHexVent = d['EnergySave']['IsUseHEXVent']
        
    # 通風の換気回数を取得
    def VentRate(self):
        return self.__dblVentRate if self.__blnCrossVent == True else 0.0
    
    # 蓄熱の有無を取得
    def Storage(self):
        return self.__blnStorage
    
    # 熱交換換気有無を取得
    def HexVent(self):
        return self.__blnHexVent


# ### Example

# In[2]:


# d = {
#     'EnergySave': {
#         'IsUseVentilation' : True,
#         'AirChangeRate'    : 5.0,
#         'IsUseHeatStorage' : False,
#         'IsUseHEXVent'     : True
#     }
# }
# energysave = EnergySave( d )


# # #### 通風の換気回数を取得

# # In[3]:


# energysave.VentRate()


# # #### 蓄熱の有無を取得

# # In[4]:


# energysave.Storage()


# # #### 熱交換換気有無を取得

# # In[5]:


# energysave.HexVent()

