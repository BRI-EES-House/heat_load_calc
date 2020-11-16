"""
付録12．	室内表面の吸収日射量、形態係数、放射暖房放射成分吸収比率
"""


# 放射暖房放射成分吸収比率 表7
def get_flr(A_i_g, A_fs_i, is_radiative_heating, is_solar_absorbed_inside):
    return (A_i_g / A_fs_i) * is_radiative_heating * is_solar_absorbed_inside


