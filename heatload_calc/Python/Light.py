
# coding: utf-8

# In[1]:


import csv


# # 照明発熱スケジュールを保持するクラス
# - csvファイルから毎時の照明発熱スケジュールを読み込み、辞書型として保持します。
# - メソッド'Light'は、「室名」、「室分類」、「曜日（'平日' or '休日'）」および「時刻」を与えると、指定した時刻の照明発熱量を返します。
# - 照明発熱量の単位は[W], ただし蛍光灯の安定器損失20%を含んだ値です。

# In[2]:


# 照明発熱スケジュールデータ
class Light:

    # 照明発熱スケジュールデータの取得
    def __init__(self):
        
        # 照明発熱スケジュールの読み込み
        with open('LightingSchedule.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            
            # 照明発熱
            self.__dicLight={}
            
            for row in reader:
                strRoomName = row[0] # 室名
                strRoomDiv = row[1]  # 室分類
                strWeek =row[2]      # 曜日（'平日' or '休日'）
                
                # 毎時スケジュールのリストを設定
                dblHourly=[]         
                for hour in range(24):
                    dblHourly.append(float(row[hour + 3]))
                
                # 照明発熱をセット
                # 単位は[W], 蛍光灯の安定器損失20%を含む
                key = strRoomName + ',' + strRoomDiv + ',' + strWeek 
                self.__dicLight[key] = dblHourly
                

    # 照明発熱
    def dicLight(self):
        return self.__dicLight
        
    # 指定した時刻の照明発熱量の取得
    def Light(self, strRoomName, strRoomDiv, strWeek, lngTime):
        key = strRoomName + ',' + strRoomDiv + ',' + strWeek
        vntHourly=self.__dicLight[key] 
        return vntHourly[lngTime]


# # ## Example

# # In[3]:


# li=Light()


# # ### keyの取得

# # In[4]:


# li.dicLight().keys()


# # ### Itemの取得

# # In[5]:


# li.dicLight()['非居室,,平日']


# # ### 指定した時刻の照明発熱量を取得

# # In[6]:


# li.Light('非居室','','平日',23)

