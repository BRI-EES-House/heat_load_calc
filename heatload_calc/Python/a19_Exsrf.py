import math


# 傾斜面に関する変数であり、式(73)
def get_slope_angle_intermediate_variables(Wa, Wb):
    # 太陽入射角の方向余弦cosθ　計算用パラメータ
    Wz = math.cos(Wb)
    Ww = math.sin(Wb) * math.sin(Wa)
    Ws = math.sin(Wb) * math.cos(Wa)

    return Wz, Ww, Ws


# 方向名称から方位角、傾斜角の計算 表11 方位と方位角、傾斜角の対応
def get_slope_angle(direction_string: str) -> tuple:
    direction_angle = -999.0
    inclination_angle = -999.0
    if direction_string == 's':
        direction_angle = 0.0
        inclination_angle = 90.0
    elif direction_string == 'sw':
        direction_angle = 45.0
        inclination_angle = 90.0
    elif direction_string == 'w':
        direction_angle = 90.0
        inclination_angle = 90.0
    elif direction_string == 'nw':
        direction_angle = 135.0
        inclination_angle = 90.0
    elif direction_string == 'n':
        direction_angle = 180.0
        inclination_angle = 90.0
    elif direction_string == 'ne':
        direction_angle = -135.0
        inclination_angle = 90.0
    elif direction_string == 'e':
        direction_angle = -90.0
        inclination_angle = 90.0
    elif direction_string == 'se':
        direction_angle = -45.0
        inclination_angle = 90.0
    elif direction_string == 'top':
        direction_angle = 0.0
        inclination_angle = 0.0
    elif direction_string == 'bottom':
        direction_angle = 0.0
        inclination_angle = 180.0
    
    return math.radians(direction_angle), math.radians(inclination_angle)


# 傾斜面の地面に対する形態係数 式(119)
def get_Phi_G_i_k(PhiS_i_k):
    return 1.0 - PhiS_i_k


# 傾斜面の天空に対する形態係数の計算 式(120)
def get_Phi_S_i_k(Wz):
    return (1.0 + Wz) / 2.0

