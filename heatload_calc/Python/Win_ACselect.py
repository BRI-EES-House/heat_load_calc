
# 窓の開閉、空調の発停を決定する
# 冷房開始PMV
occu_cooling_pmv = 0.84
# 暖房開始PMV
occu_heating_pmv = -0.84
# 窓を開放するときのPMV
occu_window_open_pmv = 0.49
# 窓を閉鎖するときのPMV
occu_window_close_pmv = -0.49

# 当該時刻の窓開閉、空調発停を判定する
def mode_select(air_conditioning_demand, prev_air_conditioning_mode, is_prev_window_open, now_pmv):
    # 空調需要がない場合（窓閉鎖、空調停止）
    if air_conditioning_demand == False:
        is_now_window_open = False
        now_air_conditioning_mode = 0
    # 空調需要がある場合は、前の窓開閉状態で自然室温を計算
    else:
        # 前時刻が暖房の場合
        if prev_air_conditioning_mode > 0:
            is_now_window_open = is_prev_window_open
            now_air_conditioning_mode = prev_air_conditioning_mode
            # 冷房生起PMV以上の場合は冷房
            if now_pmv >= occu_cooling_pmv:
                is_now_window_open = False
                now_air_conditioning_mode = -1
            # 窓開放生起温度以上の場合は通風
            elif now_pmv >= occu_window_open_pmv:
                is_now_window_open = True
                now_air_conditioning_mode = 0
        # 前時刻が冷房の場合
        elif prev_air_conditioning_mode < 0:
            # 暖房生起PMV以上の場合は冷房
            if now_pmv >= occu_heating_pmv:
                is_now_window_open = False
                now_air_conditioning_mode = -1
            # 暖房生起PMV未満の場合は暖房
            else:
                is_now_window_open = False
                now_air_conditioning_mode = 1
        # 前の時刻が空調停止の場合
        else:
            # 冷房生起PMV以上の場合は冷房
            if now_pmv >= occu_cooling_pmv:
                is_now_window_open = False
                now_air_conditioning_mode = -1
            # 暖房生起PMV以下の場合は暖房
            elif now_pmv <= occu_heating_pmv:
                is_now_window_open = False
                now_air_conditioning_mode = 1
            # 空調は停止し、now_PMVが窓開放生起PMVをまたぐまでは前の状態を維持
            else:
                now_air_conditioning_mode = 0
                is_now_window_open = is_prev_window_open
                # 窓を開放する
                if is_prev_window_open == 0 and now_pmv >= occu_window_open_pmv:
                    is_now_window_open = True
                # 窓を閉鎖する
                elif is_prev_window_open == 1 and now_pmv <= occu_window_close_pmv:
                    is_now_window_open = False
    
    return (is_now_window_open, now_air_conditioning_mode)

# 最終の空調信号の計算（空調停止はこのルーチンに入らない）
def reset_SW(now_air_conditioning_mode, Lcs, Lr, isRadiantHeater, Lrcap):
    temp = now_air_conditioning_mode

    # 「冷房時の暖房」、「暖房時の冷房」判定
    if float(now_air_conditioning_mode) * (Lcs + Lr) < 0.0:
        temp = 0
    # 放射暖房の過負荷状態
    elif isRadiantHeater and now_air_conditioning_mode == 1 and Lrcap > 0.0 \
            and Lr > Lrcap:
        temp = 3
    # 放射暖房の過負荷状態
    elif isRadiantHeater and now_air_conditioning_mode == 1 and Lrcap <= 0.0:
        temp = 4

    return temp