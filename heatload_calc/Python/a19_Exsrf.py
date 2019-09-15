import math
import numpy as np

# 傾斜面に関する変数であり、式(73)
def get_slope_angle_intermediate_variables(Wa, Wb):
    # 太陽入射角の方向余弦cosθ　計算用パラメータ
    Wz = np.cos(Wb)
    Ww = np.sin(Wb) * np.sin(Wa)
    Ws = np.sin(Wb) * np.cos(Wa)

    return Wz, Ww, Ws


# 方向名称から方位角、傾斜角の計算 表11 方位と方位角、傾斜角の対応
def get_slope_angle(direction_string: np.ndarray) -> tuple:
    direction_angle = np.array([-999.0] * len(direction_string))
    inclination_angle = np.array([-999.0] * len(direction_string))

    # direction_string == 's'
    direction_angle[direction_string == 's'] = 0.0
    inclination_angle[direction_string == 's'] = 90.0

    # direction_string == 'sw'
    direction_angle[direction_string == 'sw'] = 45.0
    inclination_angle[direction_string == 'sw'] = 90.0

    # direction_string == 'w'
    direction_angle[direction_string == 'w'] = 90.0
    inclination_angle[direction_string == 'w'] = 90.0

    # direction_string == 'nw'
    direction_angle[direction_string == 'nw'] = 135.0
    inclination_angle[direction_string == 'nw'] = 90.0

    # direction_string == 'n'
    direction_angle[direction_string == 'n'] = 180.0
    inclination_angle[direction_string == 'n'] = 90.0

    # direction_string == 'ne':
    direction_angle[direction_string == 'ne'] = -135.0
    inclination_angle[direction_string == 'ne'] = 90.0

    # direction_string == 'e'
    direction_angle[direction_string == 'e'] = -90.0
    inclination_angle[direction_string == 'e'] = 90.0

    # direction_string == 'se'
    direction_angle[direction_string == 'se'] = -45.0
    inclination_angle[direction_string == 'se'] = 90.0

    # direction_string == 'top'
    direction_angle[direction_string == 'top'] = 0.0
    inclination_angle[direction_string == 'top'] = 0.0

    # direction_string == 'bottom'
    direction_angle[direction_string == 'bottom'] = 0.0
    inclination_angle[direction_string == 'bottom'] = 180.0
    
    return np.radians(direction_angle), np.radians(inclination_angle)


# 傾斜面の地面に対する形態係数 式(119)
def get_Phi_G_i_k(PhiS_i_k):
    return 1.0 - PhiS_i_k


# 傾斜面の天空に対する形態係数の計算 式(120)
def get_Phi_S_i_k(Wz):
    return (1.0 + Wz) / 2.0

