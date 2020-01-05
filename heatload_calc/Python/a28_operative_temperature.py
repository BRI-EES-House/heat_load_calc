import a35_PMV as a35
from scipy.optimize import fsolve
from scipy.optimize import newton
from a39_global_parameters import OperationMode

"""
付録28．暖冷房設定温度
"""


def get_OTset(RH: float, Clo: float, PMV_set: float, h_c_i_n, t_cl_i_n, h_r, p_a) -> float:
    """ 作用温度の計算
    指定条件(met, velocity, RH, Clo)条件下で指定PMVになる作用温度OTを求める

    :param RH: 室相対湿度[%]
    :param Clo: 着衣量 [Clo]
    :param PMV_set: 目標PMV
    :return: 作用温度 [℃]
    """
    # 定数部分があるので、ラムダ式で関数を包む
    # 右辺が0になるように式を変形する

    OTset = newton(lambda OT: a35.get_pmv(h_c=h_c_i_n, t_a=OT, t_cl=t_cl_i_n, t_r_bar=OT, clo_value=Clo, h_r=h_r, p_a=p_a) - PMV_set, 0.001)

    return OTset


# PMV_i_n=0条件から目標作用温度を計算する
def calc_OTset(isRadiantHeater: bool, RH: float, PMV_set: float, h_c_i_n, t_cl_i_n, h_r, operation_mode_i_n, p_a, Clo) -> float:
    """

    :param isRadiantHeater: 放射式空調時はTrue
    :param RH: 室相対湿度[%]
    :param PMV_set: 目標PMV
    :return: 目標作用温度 [℃]
    """
    if operation_mode_i_n in [OperationMode.HEATING, OperationMode.COOLING]:
        # 放射式空調時
        if isRadiantHeater:
            # 代謝量1.0Met、風速0.0m/sを想定
            OTset = get_OTset(RH, Clo, PMV_set, h_c_i_n, t_cl_i_n, h_r, p_a)
        # 対流式空調時
        else:
            # 代謝量1.0Met、風速0.2m/sを想定
            OTset = get_OTset(RH, Clo, PMV_set, h_c_i_n, t_cl_i_n, h_r, p_a)
    else:
        OTset = 0.0

    return OTset
