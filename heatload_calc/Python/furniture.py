"""
付録14．	家具の熱容量・熱コンダクタンスと備品等の湿気容量・湿気コンダクタンスの計算
"""


# 家具熱容量[J/K] 式(103)
def get_Capfun(Vol):
    """

    :param Vol: 室気積
    :return:
    """
    # 室の家具の顕熱容量[kJ/m3 K]
    funiture_sensible_capacity = 12.6

    # 家具熱容量[J/K]
    Capfan = funiture_sensible_capacity * Vol * 1000.

    return Capfan


# 家具類の湿気容量[kg]  式(104)
def get_Gf(Vol):
    """

    :param Vol: 室気積
    :return:
    """
    # 室の家具の潜熱容量[kg/(m3 kg/kg(DA))]
    funiture_latent_capacity = 16.8

    # 家具類の湿気容量[kg]
    Gf = funiture_latent_capacity * Vol

    return Gf



# 家具と空気間の熱コンダクタンス[W/K] 式(105)
def get_Cfun(Capfun):
    return 0.00022 * Capfun


# 室空気と家具類間の湿気コンダクタンス[kg/(s･kg/kg(DA))]  式(106)
def get_Cx(Gf):
    return 0.0018 * Gf

