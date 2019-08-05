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