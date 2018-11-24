
# coding: utf-8

# In[1]:


import datetime


# In[2]:


# シミュレーション全体の設定条件
class Gdata:
    
    def __init__(self, Region, dblDTime, lngApproach, SimStMo, SimStDay, SimEnMo, SimEnDay, Latitude, Longitude, StMeridian, strFFcalcMethod, dblFsolFlr, blnOTset):
        # 地域区分
        self.__Region = Region

        # 計算対象年
        self.__conlngYr = 1989
        # 計算時間間隔(s)
        self.__dblDTime = dblDTime
        # 助走計算期間(day)
        self.__lngApproach = lngApproach
        # シミュレーション（本計算）の開始日
        self.__dtmStDate = datetime.datetime(self.__conlngYr, SimStMo, SimStDay)
        # シミュレーション（本計算）終了日
        self.__dtmEnDate = datetime.datetime(self.__conlngYr, SimEnMo, SimEnDay)
        # 開始日が終了日よりも後の月日の場合は、終了日にプラス1年加算する。
        if self.__dtmStDate > self.__dtmEnDate:
            self.__dtmEnDate = self.__dtmEnDate + datetime.timedelta(days=365)
        # 助走計算開始時刻
        self.__dtmApDate = self.__dtmStDate - datetime.timedelta(days=self.__lngApproach)
        # 応答係数の作成時間数(hour)
        # self.__lngNcalTime = lngNcalTime
        # 計算結果の行数
        self.__lngOutputRow = int( ( (self.__dtmEnDate - self.__dtmStDate).days + 1 ) * 24 * 3600 / self.__dblDTime )
        # comment - miura : 3600 / dblDtime が必ずしも整数になるとは限らない。その場合のエラー処理が必要か、そもそもdblDtimeではなくて、1時間の分割数とかで入力させるべき。
        # 詳細出力フラグ
        # self.__blnDetailOut = blnDetailOut
        # 形態係数の計算方法
        self.__strFFcalcMethod = strFFcalcMethod
        # 透過日射の床吸収比率
        self.__dblFsolFlr = dblFsolFlr
        # 作用温度設定フラグ
        self.__blnOTset = blnOTset

        # 緯度
        self.__Lat = Latitude
        # 経度
        self.__Lon = Longitude
        # 標準子午線
        self.__StMeridian = StMeridian
    
    # 計算時間間隔の取得
    def DTime(self):
        return self.__dblDTime
    
    # 助走計算開始時刻の取得
    def ApDate(self):
        return self.__dtmApDate

    # 本計算フラグ
    def FlgOrig(self, dtmDate):
        return (self.__dtmStDate <= dtmDate)
    
    # 計算終了日
    def EnDate(self):
        return self.__dtmEnDate

    # 応答係数の項数
    # def M(self):
    #     return int(self.__lngNcalTime * 3600 / self.__dblDTime + 1)
    
    # 計算結果の行数
    def OutputRow(self):
        return self.__lngOutputRow
    
    # 詳細計算結果出力フラグ
    # def DetailOut(self):
    #     return self.__blnDetailOut
    
    # 形態係数の計算方法
    def FFcalcMethod(self):
        return self.__strFFcalcMethod
    
    # 透過日射の床吸収比率
    def FsolFlr(self):
        return self.__dblFsolFlr
    
    # 作用温度設定フラグ
    def OTset(self):
        return self.__blnOTset
    
    # 緯度
    def Latitude(self):
        return self.__Lat
    # 経度
    def Longitude(self):
        return self.__Lon
    #標準子午線
    def StMeridian(self):
        return self.__StMeridian

# # In[3]:


# g = Gdata(900,20,1,1,12,31,50,True,"面積比",0.5,False)


# # In[4]:


# g.DTime()


# # In[5]:


# g.ApDate()


# # In[7]:


# g.FlgOrig(datetime.datetime(1989,1,15))


# # In[ ]:


# g.EnDate()


# # In[ ]:


# g.M()


# # In[ ]:


# g.OutputRow()


# # In[ ]:


# g.DetailOut()


# # In[ ]:


# g.FFcalcMethod()


# # In[ ]:


# g.FsolFlr()


# # In[ ]:


# g.OTset()

