
# ルームエアコンの仕様の設定
# とりあえず、建研仕様書の手法を実装
def set_rac_spec(space):
    # 定格冷房能力[W]の計算（除湿量計算用）
    space.qrtd_c = 190.5 * space.TotalAF + 45.6
    # 冷房最大能力[W]の計算
    space.qmax_c = 0.8462 * space.qrtd_c + 1205.9
    # 冷房最小能力[W]の計算（とりあえず500Wで固定）
    space.qmin_c = 500.0
    # 最大風量[m3/min]、最小風量[m3/min]の計算
    space.Vmax = 11.076 * (space.qrtd_c / 1000.0) ** 0.3432
    space.Vmin = space.Vmax * 0.55
