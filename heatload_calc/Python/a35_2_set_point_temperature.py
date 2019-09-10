from a35_1_PMV import calcPMV
from scipy.optimize import fsolve

"""
付録35．	PMVの計算方法
"""

# 着衣量の計算（作用温度から求める） 式(128)
def calc_clothing(OT):
    # 冷房時の着衣量
    if OT > 29.1:
        clothing = 0.3
    # 暖房時の着衣量
    elif OT < 19.4:
        clothing = 1.1
    # 非空調時の着衣量（作用温度と線形関係で調節する）
    else:
        clothing = 1.1 + (0.3 - 1.1) / (29.1 - 19.4) * (OT - 19.4)
    
    return clothing

def get_OT(met, velocity, RH, Clo, PMV_set):
    # 定数部分があるので、ラムダ式で関数を包む
    # 右辺が0になるように式を変形する
    # 初期値は適当に0にした
    ot_set = fsolve(lambda OT: calcPMV(OT, OT, RH, velocity, met, 0.0, Clo) - PMV_set, 0.0)

    # 着衣量と設定作用温度を返す
    return ot_set[0]

# for i in range(18, 32):
#     ot_set, clo = get_OT(1.0, 0.2, 50.0, i / 10.0)
#     print(i / 10.0, ot_set, clo)

# PMV=0条件から設定作用温度を計算する
def calcOTset(now_air_conditioning_mode, isRadiantHeater, RH, pmv_set_point):
    ot_set = 0.0
    Met = 1.0
    Clo = 0.7
    Vel = 0.1
    # 対流式空調
    if now_air_conditioning_mode != 0 and not isRadiantHeater:
        # 代謝量1.0Met、風速0.2m/sを想定
        Met = 1.0
        Vel = 0.2
        Clo = 1.1 if now_air_conditioning_mode > 0 else 0.3
        ot_set = get_OT(Met, Vel, RH, Clo, pmv_set_point)
    # 放射式空調時
    elif now_air_conditioning_mode != 0 and isRadiantHeater:
        # 代謝量1.0Met、風速0.0m/sを想定
        Met = 1.0
        Vel = 0.0
        Clo = 1.1 if now_air_conditioning_mode > 0 else 0.3
        ot_set = get_OT(Met, Vel, RH, Clo, pmv_set_point)

    return ot_set, Met, Clo, Vel