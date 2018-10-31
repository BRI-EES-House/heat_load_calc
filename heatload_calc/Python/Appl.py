
# coding: utf-8

# In[1]:


import csv


# # 機器発熱スケジュールを保持するクラス
# - csvファイルから毎時の機器発熱スケジュールを読み込み、辞書型として保持します。
# - メソッド'Appl'は、「室名」、「室分類」、「機器発熱分類（'顕熱' or '潜熱'）」、「曜日（'平日' or '休日'）」および「時刻」を与えると、指定した時刻の機器発熱量を返します。
# - 顕熱発熱量の単位は[W], 潜熱発熱量の単位は[g/h]です。

# In[2]:


# 機器発熱スケジュールデータ
class Appl:

    # 機器発熱スケジュールデータの取得
    def __init__(self):
        
        # 機器発熱スケジュールの読み込み
        with open('appliances.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            
            # 機器発熱
            self.__dicAppl={}
            
            for row in reader:
                strRoomName = row[0] # 室名
                strRoomDiv = row[1]  # 室分類
                strSHLH = row[2]     # 機器発熱分類（'顕熱' or '潜熱'）
                strWeek =row[3]      # 曜日（'平日' or '休日'）
                
                # 毎時スケジュールのリストを設定
                dblHourly=[]         
                for hour in range(24):
                    dblHourly.append(float(row[hour + 4]))
                
                # 機器発熱をセット
                # 顕熱の単位は[W], 潜熱の単位は[g/h]
                key = strRoomName + ',' + strRoomDiv + ',' + strWeek + ',' + strSHLH
                self.__dicAppl[key] = dblHourly
                

    # 機器発熱
    def dicAppl(self):
        return self.__dicAppl
        
    # 指定した時刻の機器発熱量の取得
    def Appl(self, strRoomName, strRoomDiv, strWeek, strSHLH, lngTime):
        key = strRoomName + ',' + strRoomDiv + ',' + strWeek + ',' + strSHLH
        vntHourly=self.__dicAppl[key] 
        return vntHourly[lngTime]


# # ## Example

# # In[3]:


# ap=Appl()


# # ### keyの取得

# # In[4]:


# ap.dicAppl().keys()


# # ### Itemの取得

# # In[5]:


# ap.dicAppl()['主たる居室,,平日,顕熱']


# # ### 指定した時刻の機器発熱量を取得

# # In[6]:


# ap.Appl('主たる居室','','平日','顕熱',23)

