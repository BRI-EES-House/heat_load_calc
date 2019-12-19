import datetime

#蒸発潜熱[J/kg]
conra = 2501000.0
#空気の比熱[J/kg K]
conca = 1005.0
#空気の密度[kg/m3]
conrowa = 1.2
#ステファンボルツマン定数
Sgm = 5.67e-8

#大気圧[kPa]
P = 101.325

#室の家具の顕熱容量[kJ/m3 K]
#funiture_sensible_capacity = 12.6
funiture_sensible_capacity = 40/2.6
#funiture_sensible_capacity = 80/2.6
#funiture_sensible_capacity = 0.1/2.6
#室の家具の潜熱容量[kg/(m3 kg/kg(DA))]
#funiture_latent_capacity = 16.8
funiture_latent_capacity = 80*(10**6)/conra/2.6
#funiture_latent_capacity = 160*(10**6)/conra/2.6
#funiture_latent_capacity = 0.1*(10**6)/conra/2.6

#ルームエアコンのバイパスファクター
bypass_factor_rac = 0.2

# 通日を計算
def get_nday(mo, day):
    """
    :param mo: 月
    :param day: 日
    :return: 1月1日からの通日
    """
    new_year = datetime.datetime(2017, 1, 1)
    that_day = datetime.datetime(2017, mo, day)
    ndays = that_day - new_year

    return (ndays.days + 1)

# # 汎用処理を行う関数群

# ## 当該日の通日を計算する関数
# - 日付（datetime型）を引数とし、1月1日から通して数えた日数（通日）を返す
#
# ### Function

# 当該日の通日を計算する
def Nday(dtmDate):
    new_year = datetime.date(dtmDate.year, 1, 1)
    that_day = datetime.date(dtmDate.year, dtmDate.month, dtmDate.day)
    ndays = (that_day - new_year).days + 1
    return ndays
