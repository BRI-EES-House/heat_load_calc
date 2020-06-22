# 空気の比熱[J/kg K]
def get_c_air() -> float:
    return 1005.0


# 空気の密度[kg/m3]
def get_rho_air() -> float:
    return 1.2


# 蒸発潜熱[J/kg]
def get_conra() -> float:
    return 2501000.0


# ステファンボルツマン定数
def get_Sgm() -> float:
    return 5.67e-8


def get_delta_t():
    return 900


# TODO: 仕様書では固定値で記述されているが、
# 実際には JSONファイル内の`outside_solar_absorption`を使用している
# def get_as():
#    return 0.8



def get_eps():
    return 0.9
