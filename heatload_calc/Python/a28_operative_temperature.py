import a35_PMV as a35
from scipy.optimize import fsolve
from scipy.optimize import newton

"""
付録28．暖冷房設定温度
"""


def get_OTset(RH: float, Clo: float, PMV_set: float, h_c_i_n, t_cl_i_n, h_r) -> float:
    """ 作用温度の計算
    指定条件(met, velocity, RH, Clo)条件下で指定PMVになる作用温度OTを求める

    :param RH: 室相対湿度[%]
    :param Clo: 着衣量 [Clo]
    :param PMV_set: 目標PMV
    :return: 作用温度 [℃]
    """
    # 定数部分があるので、ラムダ式で関数を包む
    # 右辺が0になるように式を変形する

    OTset = newton(lambda OT: a35.get_pmv(h_c=h_c_i_n, t_a=OT, t_cl=t_cl_i_n, t_r_bar=OT, clo_value=Clo, rh=RH, h_r=h_r) - PMV_set, 0.001)

    return OTset


# PMV_i_n=0条件から目標作用温度を計算する
def calc_OTset(now_air_conditioning_mode: int, isRadiantHeater: bool, RH: float, PMV_set: float, h_c_i_n, t_cl_i_n, h_r) -> float:
    """

    :param now_air_conditioning_mode: 空調運転モード(-1:冷房, 0:停止, 1:暖房)
    :param isRadiantHeater: 放射式空調時はTrue
    :param RH: 室相対湿度[%]
    :param PMV_set: 目標PMV
    :return: 目標作用温度 [℃]
    """
    # 対流式空調
    if now_air_conditioning_mode != 0 and not isRadiantHeater:
        # 代謝量1.0Met、風速0.2m/sを想定
        Vel = 0.2
        Clo = 1.1 if now_air_conditioning_mode > 0 else 0.3
        OTset = get_OTset(RH, Clo, PMV_set, h_c_i_n, t_cl_i_n, h_r)
    # 放射式空調時
    elif now_air_conditioning_mode != 0 and isRadiantHeater:
        # 代謝量1.0Met、風速0.0m/sを想定
        Vel = 0.0
        Clo = 1.1 if now_air_conditioning_mode > 0 else 0.3
        OTset = get_OTset(RH, Clo, PMV_set, h_c_i_n, t_cl_i_n, h_r)
    else:
        OTset = 0.0
        Clo = 0.7
        Vel = 0.1

    return OTset, Clo, Vel
