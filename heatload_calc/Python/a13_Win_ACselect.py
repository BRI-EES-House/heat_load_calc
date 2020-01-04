import numpy as np
from typing import Dict

from a39_global_parameters import ACMode, OperationMode

"""
付録13．窓の開閉と空調発停の切り替え
"""


# 当該時刻の窓開閉、空調発停を判定する
def mode_select(ac_demand: bool, now_pmv: float, operation_mode_i_n_mns) -> tuple:

    # 窓の開閉、空調の発停を決定する
    # 冷房開始PMV
    occu_cooling_pmv = 0.84
    # 暖房開始PMV
    occu_heating_pmv = -0.84
    # 窓を開放するときのPMV
    occu_window_open_pmv = 0.49
    # 窓を閉鎖するときのPMV
    occu_window_close_pmv = -0.49

    # 空調需要がある場合は、前の窓開閉状態で自然室温を計算
    if ac_demand:

        if operation_mode_i_n_mns == OperationMode.HEATING:  # 前時刻が暖房の場合

            if now_pmv >= occu_cooling_pmv:  # 冷房生起PMV以上の場合は冷房
                return False, ACMode.COOLING, OperationMode.COOLING

            elif now_pmv >= occu_window_open_pmv:  # 窓開放生起温度以上の場合は通風
                return True, ACMode.STOP, OperationMode.STOP_OPEN

            else:
                return False, ACMode.HEATING, OperationMode.HEATING

        elif operation_mode_i_n_mns == OperationMode.COOLING:  # 前時刻が冷房の場合

            if now_pmv >= occu_heating_pmv:  # 暖房生起PMV以上の場合は冷房
                return False, ACMode.COOLING, OperationMode.COOLING

            else:  # 暖房生起PMV未満の場合は暖房
                return False, ACMode.HEATING, OperationMode.HEATING

        elif operation_mode_i_n_mns in [OperationMode.STOP_OPEN, OperationMode.STOP_CLOSE]:  # 前の時刻が空調停止の場合

            if now_pmv >= occu_cooling_pmv:  # 冷房生起PMV以上の場合は冷房
                return False, ACMode.COOLING, OperationMode.COOLING

            elif now_pmv <= occu_heating_pmv:  # 暖房生起PMV以下の場合は暖房
                return False, ACMode.HEATING, OperationMode.HEATING

            else:

                if operation_mode_i_n_mns == OperationMode.STOP_OPEN:

                    if now_pmv <= occu_window_close_pmv:
                        return False, ACMode.STOP, OperationMode.STOP_CLOSE

                    else:
                        return True, ACMode.STOP, OperationMode.STOP_OPEN

                else:

                    # 窓を開放する
                    if now_pmv >= occu_window_open_pmv:
                        return True, ACMode.STOP, OperationMode.STOP_OPEN

                    else:
                        return False, ACMode.STOP, OperationMode.STOP_CLOSE

        else:
            raise ValueError()

    # 空調需要がない場合（窓閉鎖、空調停止）
    else:
        return False, ACMode.STOP, OperationMode.STOP_CLOSE


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


