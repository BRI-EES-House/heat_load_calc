
# coding: utf-8

# In[1]:


import csv


# # 暖冷房設定温湿度のスケジュールを保持するクラス
# - csvファイルから毎時の暖冷房設定温湿度スケジュールを読み込み、辞書型として保持します。
# - メソッド'ACSet'は、「室名」、「室分類」、「運転モード（'冷房' or '暖房'）」、「設定分類（'温度' or '湿度'）」、「曜日（'平日' or '休日'）」および「時刻」を与えると、指定した時刻の暖冷房設定温湿度を返します。
# - 設定温度の単位は[℃], 設定湿度の単位は[%]です。

# In[2]:


# 暖冷房設定温湿度スケジュールデータ
class ACSet:

    # 暖冷房設定温湿度スケジュールデータの取得
    def __init__(self):
        
        # 暖冷房設定温湿度スケジュールデータの読み込み
        with open('ACschedule.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            
            # 暖冷房設定温湿度
            self.__dicACSet={}
            
            for row in reader:
                strRoomName = row[0] # 室名
                strRoomDiv = row[1]  # 室分類
                strMode = row[2]     # 運転モード（'冷房' or '暖房'）
                strTH = row[3]       # 設定分類（'温度' or '湿度'）
                strWeek =row[4]      # 曜日（'平日' or '休日'）
                
                # 毎時の設定温湿度スケジュールのリストを設定
                dblHourly=[]         
                for hour in range(24):
                    dblHourly.append(float(row[hour + 5]))
                
                # 暖冷房設定温湿度をセット
                # 温度の単位は[℃], 湿度の単位は[%]
                key = strRoomName + ',' + strRoomDiv + ',' + strMode + ',' + strTH + ',' + strWeek
                self.__dicACSet[key] = dblHourly
                

    # 暖冷房設定温湿度
    def dicACSet(self):
        return self.__dicACSet
        
    # 指定した時刻の設定温湿度の取得
    def ACSet(self, strRoomName, strRoomDiv, strMode, strWeek, strTH, lngTime):
        key = strRoomName + ',' + strRoomDiv + ',' + strMode + ',' + strTH + ',' + strWeek
        vntHourly = self.__dicACSet[key] # 指定されたkeyがないときのエラー処理が必要
        return vntHourly[lngTime] 


# # ## Example

# # In[3]:


# ac=ACSet()


# # ### keyの取得

# # In[4]:


# ac.dicACSet().keys()


# # ### 毎時の設定温湿度スケジュールを取得

# # In[5]:


# ac.ACSet('主たる居室','','冷房','平日','温度', 23)

