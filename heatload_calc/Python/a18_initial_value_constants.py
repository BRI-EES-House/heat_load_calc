import Psychrometrics as psy

"""
付録18．初期値と定数
"""


# ********** 表8 各種変数の初期値 **********


def get_theta_r_initial() -> float:
    return 15.0

def get_theta_dsh_srf_a_initial() -> float:
    """
    指数項mの吸熱応答の項別成分に初期値を与える。

    Returns:
        ステップnの統合された境界j*における指数項mの吸熱応答の項別成分, degree C
    """

    # 初期値を0.0℃とする。
    return 0.0


def get_theta_dsh_srf_t_initial() -> float:
    # TODO: 仕様書は15.0になっているが、実装は0.0相当だった
    return 0.0


def get_Teo_initial() -> float:
    return 15.0


def get_q_initial() -> float:
    return 0.0


def get_Tfun_initial() -> float:
    return 15.0


def get_xr_initial() -> float:

    p_v = psy.get_p_vs(theta=20.0) * 0.4

    return psy.get_x(p_v)


def get_xf_initial() -> float:

    p_v = psy.get_p_vs(theta=20.0) * 0.4

    return psy.get_x(p_v)


# ********** 表9 各種定数値 **********

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


def get_l_wtr() -> float:
    """
    Returns:
         水の蒸発潜熱, J/kg
    """
    return 2501000.0


def get_delta_t():
    return 900


# TODO: 仕様書では固定値で記述されているが、
# 実際には JSONファイル内の`outside_solar_absorption`を使用している
# def get_as():
#    return 0.8



def get_eps():
    return 0.9
