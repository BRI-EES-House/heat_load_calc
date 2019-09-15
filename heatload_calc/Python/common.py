import datetime

#蒸発潜熱[J/kg]
conra = 2501000.0

def get_l_wtr() -> float:
    """
    Returns:
         水の蒸発潜熱, J/kg
    """
    return 2501000.0

#空気の比熱[J/kg K]
ca = 1005.0
#空気の密度[kg/m3]
rhoa = 1.2
#ステファンボルツマン定数
Sgm = 5.67e-8

#大気圧[kPa]
P = 101.325

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

# 実数型の一致比較
def is_float_equal(a, b, eps):
    return abs(a - b < eps)