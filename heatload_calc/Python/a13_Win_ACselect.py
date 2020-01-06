import numpy as np
from typing import Dict
from scipy.optimize import newton

from a39_global_parameters import ACMode, OperationMode
import a35_PMV as a35

"""
付録13．窓の開閉と空調発停の切り替え
"""


# 当該時刻の窓開閉、空調発停を判定する
def mode_select(
        ac_demand_i_n: bool, operation_mode_i_n_mns: OperationMode,
        is_radiative_heating, p_a_i_n, theta_ot_i_n, theta_r_i_n, h_hum_i_n
) -> (OperationMode, float, float):
    """

    Args:
        ac_demand_i_n: ステップnの室iにおける空調需要
        now_pmv:
        operation_mode_i_n_mns:

    Returns:

    """

    theta_cl11_i_n = a35.get_t_cl_i_n(clo_i_n=1.1, ot_i_n=theta_ot_i_n, h_a_i_n=h_hum_i_n)
    theta_cl07_i_n = a35.get_t_cl_i_n(clo_i_n=0.7, ot_i_n=theta_ot_i_n, h_a_i_n=h_hum_i_n)
    theta_cl03_i_n = a35.get_t_cl_i_n(clo_i_n=0.3, ot_i_n=theta_ot_i_n, h_a_i_n=h_hum_i_n)

    pmv11_i_n = a35.get_pmv(t_a=theta_r_i_n, t_cl=theta_cl11_i_n, clo_value=1.1, p_a=p_a_i_n, h=h_hum_i_n, ot=theta_ot_i_n)
    pmv07_i_n = a35.get_pmv(t_a=theta_r_i_n, t_cl=theta_cl07_i_n, clo_value=0.7, p_a=p_a_i_n, h=h_hum_i_n, ot=theta_ot_i_n)
    pmv03_i_n = a35.get_pmv(t_a=theta_r_i_n, t_cl=theta_cl03_i_n, clo_value=0.3, p_a=p_a_i_n, h=h_hum_i_n, ot=theta_ot_i_n)

    if ac_demand_i_n:  # 空調需要がある場合

        if operation_mode_i_n_mns == OperationMode.HEATING:

            if pmv11_i_n <= 0.7:
                operation_mode = OperationMode.HEATING
            elif pmv03_i_n >= 0.7:
                operation_mode = OperationMode.COOLING
            else:
                operation_mode = OperationMode.STOP_CLOSE

        elif operation_mode_i_n_mns == OperationMode.COOLING:

            if pmv03_i_n >= -0.7:
                operation_mode = OperationMode.COOLING
            elif pmv11_i_n <= -0.7:
                operation_mode = OperationMode.HEATING
            else:
                operation_mode = OperationMode.STOP_CLOSE

        elif operation_mode_i_n_mns == OperationMode.STOP_OPEN:

            if pmv03_i_n >= 0.7:
                operation_mode = OperationMode.COOLING
            elif pmv11_i_n <= -0.7:
                operation_mode = OperationMode.HEATING
            elif pmv07_i_n <= 0.0:
                operation_mode = OperationMode.STOP_CLOSE
            else:
                operation_mode = OperationMode.STOP_OPEN

        elif operation_mode_i_n_mns == OperationMode.STOP_CLOSE:

            if pmv03_i_n >= 0.7:
                operation_mode = OperationMode.COOLING
            elif pmv11_i_n <= -0.7:
                operation_mode = OperationMode.HEATING
            elif pmv07_i_n >= 0.0:
                operation_mode = OperationMode.STOP_OPEN
            else:
                operation_mode = OperationMode.STOP_CLOSE

        else:
            raise ValueError()

    # 空調需要がない場合（窓閉鎖、空調停止）
    else:

        operation_mode = OperationMode.STOP_CLOSE

    clo_i_n = {
        OperationMode.HEATING: 1.1,
        OperationMode.COOLING: 0.3,
        OperationMode.STOP_OPEN: 0.7,
        OperationMode.STOP_CLOSE: 0.7
    }[operation_mode]

    # 前時刻の相対湿度を用い、PMV目標値を満たすような目標作用温度を求める
    if operation_mode == OperationMode.HEATING:
        target_pmv = -0.5
        theta_ot_target = newton(lambda OT: a35.get_pmv(t_a=OT, t_cl=theta_cl11_i_n, clo_value=clo_i_n, p_a=p_a_i_n, h=h_hum_i_n, ot=OT) - target_pmv, 0.001)
    elif operation_mode == OperationMode.COOLING:
        target_pmv = 0.5
        theta_ot_target = newton(lambda OT: a35.get_pmv(t_a=OT, t_cl=theta_cl03_i_n, clo_value=clo_i_n, p_a=p_a_i_n, h=h_hum_i_n, ot=OT) - target_pmv, 0.001)
    else:
        theta_ot_target = 0.0

    return operation_mode, clo_i_n, theta_ot_target


# 最終の空調信号の計算（空調停止はこのルーチンに入らない）
def reset_SW(ac_mode: int, Lcs: float, Lr: float, isRadiantHeater: bool, Lrcap: float) -> int:

    # 「冷房時の暖房」、「暖房時の冷房」判定
    if Lcs + Lr < 0.0:
        return ACMode.STOP

    # 放射暖房の過負荷状態
    elif isRadiantHeater and Lrcap > 0.0 and Lr > Lrcap:
        return 3

    # 放射暖房の過負荷状態
    elif isRadiantHeater and Lrcap <= 0.0:
        return 4

    else:
        return ACMode.HEATING


# 窓開放時の通風量 式(102)
def get_NV(is_now_window_open: bool, v_ntrl_vent_i: float) -> float:
    """

    Args:
        is_now_window_open:
        v_room_cap_i: 室iの容積, m3
        n_ntrl_vent_i: 室iの自然風利用時の換気回数, 1/h
        v_ntrl_vent_i: 室iの自然風利用時の換気量, m3/s

    Returns:

    """
    if is_now_window_open:
        return v_ntrl_vent_i
    else:
        return 0.0


