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
        ac_demand_i_n: bool, operation_mode_i_n_mns,
        is_radiative_heating, h_hum_c_i_n, h_hum_r_i_n, p_a_i_n, clo_i_n, theta_ot_i_n, theta_r_i_n
) -> (OperationMode, float, float):
    """

    Args:
        ac_demand_i_n: ステップnの室iにおける空調需要
        now_pmv:
        operation_mode_i_n_mns:

    Returns:

    """

    h_hum_i_n = h_hum_c_i_n + h_hum_r_i_n

    theta_cl_i_n = a35.get_t_cl_i_n(clo_i_n=clo_i_n, h_c_i_n=h_hum_c_i_n, h_r_i_n=h_hum_r_i_n, ot_i_n=theta_ot_i_n, h_a_i_n=h_hum_i_n)

    pmv_i_n = a35.get_pmv(t_a=theta_r_i_n, t_cl=theta_cl_i_n, clo_value=clo_i_n, p_a=p_a_i_n, h=h_hum_i_n, ot=theta_ot_i_n)

    # 窓の開閉、空調の発停を決定する
    # 冷房開始PMV
    occu_cooling_pmv = 0.84
    # 暖房開始PMV
    occu_heating_pmv = -0.84
    # 窓を開放するときのPMV
    occu_window_open_pmv = 0.49
    # 窓を閉鎖するときのPMV
    occu_window_close_pmv = -0.49

    if ac_demand_i_n:  # 空調需要がある場合

        if operation_mode_i_n_mns == OperationMode.HEATING:  # 前時刻が暖房の場合
            if pmv_i_n >= occu_cooling_pmv:  # 冷房生起PMV以上の場合は冷房
                operation_mode, pmv_set, clo_i_n = OperationMode.COOLING, 0.5, 0.3

            elif pmv_i_n >= occu_window_open_pmv:  # 窓開放生起温度以上の場合は通風
                operation_mode, pmv_set, clo_i_n = OperationMode.STOP_OPEN, None, 0.7

            else:
                operation_mode, pmv_set, clo_i_n = OperationMode.HEATING, -0.5, 1.1

        elif operation_mode_i_n_mns == OperationMode.COOLING:  # 前時刻が冷房の場合

            if pmv_i_n >= occu_heating_pmv:  # 暖房生起PMV以上の場合は冷房
                operation_mode, pmv_set, clo_i_n = OperationMode.COOLING, 0.5, 0.3

            else:  # 暖房生起PMV未満の場合は暖房
                operation_mode, pmv_set, clo_i_n = OperationMode.HEATING, -0.5, 1.1

        elif operation_mode_i_n_mns in [OperationMode.STOP_OPEN, OperationMode.STOP_CLOSE]:  # 前の時刻が空調停止の場合

            if pmv_i_n >= occu_cooling_pmv:  # 冷房生起PMV以上の場合は冷房
                operation_mode, pmv_set, clo_i_n = OperationMode.COOLING, 0.5, 0.3

            elif pmv_i_n <= occu_heating_pmv:  # 暖房生起PMV以下の場合は暖房
                operation_mode, pmv_set, clo_i_n = OperationMode.HEATING, -0.5, 1.1

            else:

                if operation_mode_i_n_mns == OperationMode.STOP_OPEN:

                    if pmv_i_n <= occu_window_close_pmv:
                        operation_mode, pmv_set, clo_i_n = OperationMode.STOP_CLOSE, None, 0.7

                    else:
                        operation_mode, pmv_set, clo_i_n = OperationMode.STOP_OPEN, None, 0.7

                else:

                    # 窓を開放する
                    if pmv_i_n >= occu_window_open_pmv:
                        operation_mode, pmv_set, clo_i_n = OperationMode.STOP_OPEN, None, 0.7

                    else:
                        operation_mode, pmv_set, clo_i_n = OperationMode.STOP_CLOSE, None, 0.7

        else:
            raise ValueError()

    # 空調需要がない場合（窓閉鎖、空調停止）
    else:

        operation_mode, pmv_set, clo_i_n = OperationMode.STOP_CLOSE, None, 0.7

    # 前時刻の相対湿度を用い、PMV目標値を満たすような目標作用温度を求める
    if operation_mode in [OperationMode.HEATING, OperationMode.COOLING]:
        OTset = newton(lambda OT: a35.get_pmv(t_a=OT, t_cl=theta_cl_i_n, clo_value=clo_i_n, p_a=p_a_i_n, h=h_hum_i_n, ot=OT) - pmv_set, 0.001)
    else:
        OTset = 0.0

    return operation_mode, clo_i_n, OTset

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


