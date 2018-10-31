
# coding: utf-8

# In[1]:


import csv


# # 局所換気スケジュールを保持するクラス
# - csvファイルから毎時の局所換気スケジュールを読み込み、辞書型として保持します。
# - メソッド'Vent'は、「室名」、「室分類」、「曜日（'平日' or '休日'）」および「時刻」を与えると、指定した時刻の局所換気量を返します。
# - 局所換気量の単位は[m3/h]です。

# In[2]:


# 局所換気スケジュールデータ
class LocalVent:

    # 局所換気スケジュールデータの取得
    def __init__(self):
        
        # 局所換気スケジュールの読み込み
        with open('LocalVentSchedule.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            
            # 局所換気
            self.__dicVent={}
            
            for row in reader:
                strRoomName = row[0] # 室名
                strRoomDiv = row[1]  # 室分類
                strWeek =row[2]      # 曜日（'平日' or '休日'）
                
                # 毎時スケジュールのリストを設定
                dblHourly=[]         
                for hour in range(24):
                    dblHourly.append(float(row[hour + 3]))
                
                # 局所換気をセット
                # 単位は[m3/h]
                key = strRoomName + ',' + strRoomDiv + ',' + strWeek 
                self.__dicVent[key] = dblHourly
                

    # 局所換気
    def dicVent(self):
        return self.__dicVent
        
    # 指定した時刻の局所換気量の取得
    def Vent(self, strRoomName, strRoomDiv, strWeek, lngTime):
        key = strRoomName + ',' + strRoomDiv + ',' + strWeek
        vntHourly=self.__dicVent[key] 
        return vntHourly[lngTime]


# # ## Example

# # In[3]:


# ve=LocalVent()


# # ### keyの取得

# # In[4]:


# ve.dicVent().keys()


# # ### Itemの取得

# # In[5]:


# ve.dicVent()['主たる居室,,平日']


# # ### 指定した時刻の局所換気量を取得

# # In[6]:


# ve.Vent('主たる居室','','平日',23)

