"""
付録15．	ルームエアコンの定格能力、風量の計算
"""


# 最大風量[m3/min]の計算 式(107)
def get_Vmax(qrtd_c):
    """
    :param qrtd_c: 定格冷房能力[W]
    :return:
    """
    Vmax = 11.076 * (qrtd_c / 1000.0) ** 0.3432
    return Vmax


# 最小風量[m3/min]の計算 式(108)
def get_Vmin(Vmax):
    """
    :param Vmax: 最大風量[m3/min]
    :return:
    """
    Vmin = Vmax * 0.55
    return Vmin


# 定格冷房能力[W]の計算（除湿量計算用）式(109)
def get_qrtd_c(TotalAF):
    """
    :param TotalAF: 合計床面積
    :return:
    """
    qrtd_c = 190.5 * TotalAF + 45.6
    return qrtd_c


# 冷房最大能力[W]の計算 式(110)
def get_qmax_c(qrtd_c):
    """
    :param qrtd_c: 定格冷房能力[W]
    :return:
    """
    qmax_c = 0.8462 * qrtd_c + 1205.9
    return qmax_c


# 冷房最小能力[W]の計算（とりあえず500Wで固定） 式(101)
def get_qmin_c():
    return 500.0
