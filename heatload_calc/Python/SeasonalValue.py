
# coding: utf-8

# # 季節ごとの特性値を保持するクラス
# 
# 室ごとの季節別換気量を保持します。

# In[1]:


class SeasonalValue:
    # 初期化
    def __init__(self, winter, inter, summer):
        self.__winter = winter                            # 冬期特性値
        self.__inter = inter                              # 中間期特性値
        self.__summer = summer                            # 夏期特性値
    
    # 冬期の特性値
    def winter(self):
        return self.__winter
    
    # 中間期の特性値
    def inter(self):
        return self.__inter
    
    # 夏期の特性値
    def summer(self):
        return self.__summer

