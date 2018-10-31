
# coding: utf-8

# In[1]:


import nbimporter
import datetime


# In[2]:


import ACSet
import AnnualCal
import Appl
import Light
import LocalVent
import Resi
import mdlLibrary


# # 各種スケジュールデータを統括するクラス

# In[3]:


class Schedule:
    
    # 各種スケジュールクラスの初期化
    def __init__(self):
        self.__objACSet = ACSet.ACSet()
        self.__objAnnualCal = AnnualCal.AnnualCal()
        self.__objAppl = Appl.Appl()
        self.__objLight = Light.Light()
        self.__objLocalVent = LocalVent.LocalVent()
        self.__objResi = Resi.Resi()
        
    # 空調設定温湿度の取得
    def ACSet(self, strRoomName, strRooDiv, strTH, dtmDate):
        # strRoomName as string : 室名
        # strRooDiv as string : 室分類
        # strTH as string : 設定分類（'温度' or '湿度'）
        # dtmDate as datetime
        
        # 時刻の取得
        lngTime = dtmDate.hour
        # 曜日（'平日' or '休日'）の取得
        Nday = mdlLibrary.Nday(dtmDate)
        strWeek = self.__objAnnualCal.Week(mdlLibrary.Nday(dtmDate))
        # 運転モード（'冷房' or '暖房'）の取得
        strMode = self.__objAnnualCal.Season(Nday)
        return self.__objACSet.ACSet(strRoomName, strRooDiv, strMode, strWeek, strTH, lngTime)
    
    # 機器発熱スケジュールの取得
    def Appl(self, strRoomName, strRoomDiv, strSHLH, dtmDate):
        # strSHLH as string : # 機器発熱分類（'顕熱' or '潜熱'）
        # 時刻の取得
        lngTime = dtmDate.hour
        # 曜日（'平日' or '休日'）の取得
        strWeek = self.__objAnnualCal.Week(mdlLibrary.Nday(dtmDate))
        return self.__objAppl.Appl(strRoomName, strRoomDiv, strWeek, strSHLH, lngTime)
    
    # 照明発熱スケジュールの取得
    def Light(self, strRoomName, strRoomDiv, dtmDate):
        # 時刻の取得
        lngTime =  dtmDate.hour
        # 曜日（'平日' or '休日'）の取得
        strWeek = self.__objAnnualCal.Week(mdlLibrary.Nday(dtmDate))
        return self.__objLight.Light(strRoomName, strRoomDiv, strWeek, lngTime)
    
    # 局所換気スケジュールの取得
    def LocalVent(self, strRoomName, strRoomDiv, dtmDate):
        # 時刻の取得
        lngTime =  dtmDate.hour
        # 曜日（'平日' or '休日'）の取得
        strWeek = self.__objAnnualCal.Week(mdlLibrary.Nday(dtmDate))
        return self.__objLocalVent.Vent(strRoomName, strRoomDiv, strWeek, lngTime)
    
    # 在室人員スケジュールの取得
    def Nresi(self, strRoomName, strRoomDiv, dtmDate):
        # 時刻の取得
        lngTime =  dtmDate.hour
        # 曜日（'平日' or '休日'）の取得
        strWeek = self.__objAnnualCal.Week(mdlLibrary.Nday(dtmDate))
        return self.__objResi.Nresi(strRoomName, strRoomDiv, strWeek, lngTime)

    # datetime型から曜日を取得する
    def Week(self, dtmDate):
        return self.__objAnnualCal.Week(mdlLibrary.Nday(dtmDate))

    # datetime型から季節を取得する
    def Season(self, dtmDate):
        return self.__objAnnualCal.Season(mdlLibrary.Nday(dtmDate))


# ## Example

# In[4]:


# sc = Schedule()


# # ### 空調設定温湿度の取得

# # In[5]:


# sc.ACSet('主たる居室','', '温度', datetime.datetime.strptime('2017/06/01 12:06', '%Y/%m/%d %H:%M'))  


# # ### 機器発熱スケジュールの取得

# # In[6]:


# sc.Appl('主たる居室', '', '顕熱', datetime.datetime.strptime('2017/02/04 07:00', '%Y/%m/%d %H:%M'))  


# # ### 照明発熱スケジュールの取得

# # In[7]:


# sc.Light('主たる居室', '', datetime.datetime.strptime('2017/07/20 19:00', '%Y/%m/%d %H:%M')) 


# # ### 局所換気スケジュールの取得

# # In[8]:


# sc.LocalVent('主たる居室', '', datetime.datetime.strptime('2017/07/20 19:00', '%Y/%m/%d %H:%M')) 


# # ### 在室人員スケジュールの取得

# # In[9]:


# sc.Nresi('主たる居室', '', datetime.datetime.strptime('2017/07/20 19:00', '%Y/%m/%d %H:%M')) 


# # ### datetime型から曜日（'平日' or '休日'）を取得

# # In[10]:


# sc.Week(datetime.datetime.strptime('2017/07/20 19:00', '%Y/%m/%d %H:%M')) 


# # ### datetime型から季節（'冷房' or '暖房'）を取得

# # In[11]:


# sc.Season(datetime.datetime.strptime('2017/07/20 19:00', '%Y/%m/%d %H:%M')) 

