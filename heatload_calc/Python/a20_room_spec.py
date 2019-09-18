"""
付録20．空間の定義
"""


# 室気積[m3]
def read_volume(d_room):
    return d_room['volume']


# 計画換気量
def read_vent(d_room):
    return d_room['vent']


def read_natural_vent_time(d_room):
    return d_room['natural_vent_time']
