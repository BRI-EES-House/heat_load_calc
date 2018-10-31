
# coding: utf-8

# In[1]:


import datetime


# # 汎用処理を行う関数群

# ## 当該日の通日を計算する関数
# - 日付（datetime型）を引数とし、1月1日から通して数えた日数（通日）を返す
# 
# ### Function

# In[2]:


# 当該日の通日を計算する
def Nday(dtmDate):
    dtmNewYear = datetime.date(dtmDate.year, 1, 1)
    dtmTemp = datetime.date(dtmDate.year, dtmDate.month, dtmDate.day)
    Nday = (dtmTemp - dtmNewYear).days + 1
    return Nday


# # ### Example

# # In[3]:


# Nday(datetime.datetime.strptime('2017/01/02 12:00:00', '%Y/%m/%d %H:%M:%S'))


# # In[4]:


# Nday(datetime.datetime.strptime('08月02日', '%m月%d日'))

