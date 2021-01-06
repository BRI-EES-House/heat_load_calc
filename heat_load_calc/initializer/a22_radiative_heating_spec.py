"""
付録22．	室供給熱量の最大能力の定義
"""


# 放射暖房の有無
def read_is_radiative_heating(d_room):
    return d_room['heating_equipment']['equipment_type'] == 'radiative'


# 放射冷房の有無
def read_is_radiative_cooling(d_room):
    return d_room['cooling_equipment']['equipment_type'] == 'radiative'


# 放射冷房最大能力 [W/m2]
def read_radiative_cooling_max_capacity(d_room):
    if read_is_radiative_cooling(d_room):
        return d_room['cooling_equipment']['radiative_cooling']['max_capacity'] * \
               d_room['cooling_equipment']['radiative_cooling']['area']


# 定格冷房能力[W] (対流式の場合)
def read_convective_cooling_rtd_capacity(d_room):
    if not read_is_radiative_cooling(d_room):
        return d_room['cooling_equipment']['convective_cooling']['max_capacity']
