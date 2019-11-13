
# 窓の開閉、空調の発停を決定する
# 冷房開始OT
occuCoolOT = 29.1
occuHeatOT = 19.3
occuOpenOT = 24.8

# 当該時刻の窓開閉、空調発停を判定する
def mode_select(demAC, preAC, preWin, nowOT):
    # 空調需要がない場合（窓閉鎖、空調停止）
    if demAC == 0:
        nowWin = 0
        nowAC = 0
    # 空調需要がある場合は、前の窓開閉状態で自然室温を計算
    else:
        # 前時刻が暖房の場合
        if preAC > 0:
            nowWin = preWin
            nowAC = preAC
            # 冷房生起温度以上の場合は冷房
            if nowOT >= occuCoolOT:
                nowWin = 0
                nowAC = -1
            # 窓開放生起温度以上の場合は通風
            elif nowOT >= occuOpenOT + 2.0:
                nowWin = 1
                nowAC = 0
        # 前時刻が冷房の場合
        elif preAC < 0:
            # 暖房生起温度以上の場合は冷房
            if nowOT >= occuHeatOT:
                nowWin = 0
                nowAC = -1
            # 暖房生起温度未満の場合は暖房
            else:
                nowWin = 0
                nowAC = 1
        # 前の時刻が空調停止の場合
        else:
            # 冷房生起温度以上の場合は冷房
            if nowOT >= occuCoolOT:
                nowWin = 0
                nowAC = -1
            # 暖房生起温度以下の場合は暖房
            elif nowOT <= occuHeatOT:
                nowWin = 0
                nowAC = 1
            # 空調は停止し、nowOTが窓開放生起温度をまたぐまでは前の状態を維持
            else:
                nowAC = 0
                nowWin = preWin
                if preWin == 0 and nowOT >= occuOpenOT + 2.0:
                    nowWin = 1
                elif preWin == 1 and nowOT <= occuOpenOT - 2.0:
                    nowWin = 0
    
    return (nowWin, nowAC)

# 最終の空調信号の計算（空調停止はこのルーチンに入らない）
def reset_SW(nowAC, Lcs, Lr, isRadiantHeater, Lrcap):
    temp = nowAC

    # 「冷房時の暖房」、「暖房時の冷房」判定
    if float(nowAC) * (Lcs + Lr) < 0.0:
        temp = 0
    # 放射暖房の過負荷状態
    elif isRadiantHeater and nowAC == 1 and Lrcap > 0.0 \
            and Lr > Lrcap:
        temp = 3
    # 放射暖房の過負荷状態
    elif isRadiantHeater and nowAC == 1 and Lrcap <= 0.0:
        temp = 4

    return temp