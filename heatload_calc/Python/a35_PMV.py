import math

"""
付録35．PMVの計算方法
"""


# PMVを計算する
def calc_PMV(Ta, MRT, RH, V, Met, Wme, Clo):
    # 水蒸気分圧[Pa]の計算
    Pa = RH / 100. * FNPS(Ta) * 1000.0
    # 着衣の熱抵抗[m2K/W]の計算
    Icl = 0.155 * Clo
    # 代謝量[W/m2]、外部仕事[W/m2]の計算
    M = Met * 58.15
    W = Wme * 58.15
    # 人体内部での熱生産量[W/m2]
    MW = M - W
    # 着衣面積率
    if Icl < 0.078:
        fcl = 1.0 + 1.29 * Icl
    else:
        fcl = 1.05 + 0.645 * Icl
    # 強制対流熱伝達率の計算
    Hcf = 12.1 * math.sqrt(V)
    # 室温、MRTの絶対温度換算
    Taa = Ta + 273.0
    MRTa = MRT + 273.0

    Tcla = Taa + (35.5 - Ta) / (3.5 * (6.45 * Icl + 0.1))
    P1 = Icl * fcl
    P2 = P1 * 3.96
    P3 = P1 * 100.0
    P4 = P1 * Taa
    P5 = 308.7 - 0.028 * MW + P2 * (MRTa / 100.0) ** 4.0
    XN = Tcla / 100.0
    XF = XN
    # N = 0
    EPS = 0.00015
    PMV = 99999.0
    # 着衣の表面温度収束計算
    for i in range(150):
        XF = (XF + XN) / 2.0
        # 自然対流熱伝達率
        Hcn = 2.38 * abs(100.0 * XF - Taa) ** 0.25
        Hc = max(Hcf, Hcn)
        XN = (P5 + P4 * Hc - P2 * XF ** 4.0) / (100.0 + P3 * Hc)

        if abs(XN - XF) < EPS:  # 式(138)
            break
    # 着衣の表面温度[℃]
    Tcl = 100.0 * XN - 273.0

    HL1 = 3.05 * (5733.0 - 6.99 * MW - Pa) / 1000.0
    if MW > 58.15:
        HL2 = 0.42 * (MW - 58.15)
    else:
        HL2 = 0.0

    HL3 = 1.7 * M * (5867.0 - Pa) / 100000.0
    HL4 = 14.0 * M * (34.0 - Ta) / 10000.0
    HL5 = 3.96 * fcl * (XN ** 4.0 - (MRTa / 100.0) ** 4.0)
    HL6 = fcl * Hc * (Tcl - Ta)

    TS = 0.303 * math.exp(-0.036 * M) + 0.028
    PMV = TS * (MW - HL1 - HL2 - HL3 - HL4 - HL5 - HL6)

    return PMV


# PPDを計算する
# PPD（Predicted Percentage of Dissatisfied,予測不快者率（その温熱環境に不満足・不快さを感じる人の割合）)
# ref: https://www.jsrae.or.jp/annai/yougo/66.html
def get_PPD(PMV: float) -> float:
    if abs(PMV) > 3.0:
        # TODO: -9999.0 の扱いは要検討
        return -9999.0
    else:
        return 100.0 - 95.0 * math.exp(-0.03353 * PMV ** 4.0 - 0.2179 * PMV ** 2.0)


# 飽和水蒸気圧[kPa]の計算（ASHRAE Standard 55-2013）
def FNPS(T: float) -> float:
    return math.exp(16.6536 - 4030.183 / (T + 235.0))


# 着衣量 [clo] の計算（作用温度から求める） 式(128)
def get_I_cl(OT: float) -> float:
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



