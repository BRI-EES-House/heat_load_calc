import math

def calcPMV(Ta, MRT, RH, V, Met, Wme, Clo):
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
        
        if abs(XN - XF) < EPS:
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
    HL5 = 3.96 * fcl * (XN **4.0 - (MRTa / 100.0) ** 4.0)
    HL6 = fcl * Hc * (Tcl - Ta)

    TS = 0.303 * math.exp(-0.036 * M) + 0.028
    PMV = TS * (MW - HL1 - HL2 - HL3 - HL4 - HL5 - HL6)
    
    if PMV > 3.0:
        PMV = 999#
    elif PMV < -3.0:
        PMV = -999.0
    
    return PMV

# PPDを計算する
def calcPPD(PMV):
    PPD = -9999.0
    if abs(PMV) > 3.0:
        PPD = -9999.0
    else:
        PPD = 100.0 - 95.0 * math.exp(-0.03353 * PMV **4.0 - 0.2179 * PMV **2.0)
    return PPD

# 飽和水蒸気圧[kPa]の計算（ASHRAE Standard 55-2013）
def FNPS(T):
    return math.exp(16.6536 - 4030.183 / (T + 235.0))

# print(calcPMV(23.9, 23.9, 66, 0.1, 1.1, 0.0, 1.0))

# PMV=0条件から設定作用温度を計算する
def calcOTset(nowAC, isRadiantHeater, RH):
    OTset = 0.0
    Met = 1.0
    Clo = 0.7
    Vel = 0.1
    # 冷房時
    if nowAC < 0:
        # 着衣量0.4clo、代謝量1.0Met、風速0.2m/sを想定
        OTset = - 0.021 * RH + 28.6
        Met = 1.0
        Clo = 0.4
        Vel = 0.2
    # 対流暖房時
    elif nowAC > 0 and not isRadiantHeater:
        # 着衣量1.0clo、代謝量1.0Met、風速0.2m/sを想定
        OTset = - 0.027 * RH + 25.2
        Met = 1.0
        Clo = 1.0
        Vel = 0.2
    # 放射暖房時
    elif nowAC > 0 and isRadiantHeater:
        # 着衣量1.0clo、代謝量1.0Met、風速0.0m/sを想定
        OTset = - 0.030 * RH + 24.5
        Met = 1.0
        Clo = 1.0
        Vel = 0.0

    return OTset, Met, Clo, Vel
