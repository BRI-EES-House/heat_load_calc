# 傾斜面日射量の計算
def calc_inclined_surface_solar_radiation(Idn, Isky, exterior_surface, solar_position):
    Ihol = solar_position.Sh * Idn + Isky  # 水平面全天日射量
    Id = exterior_surface.CosT * Idn  # 傾斜面直達日射量
    Is = exterior_surface.Fs * Isky  # 傾斜面天空日射量
    Ir = exterior_surface.dblFg * exterior_surface.Rg * Ihol  # 傾斜面地面反射日射量
    Iw = Id + Is + Ir  # 傾斜面全日射量

    return Id, Is, Ir, Iw

# 傾斜面日射量を計算する
def calc_slope_sol(suraface, Solpos, Idn, Isky):
    if 'external' in suraface.backside_boundary_condition.Type and suraface.is_sun_striked_outside:
        # 傾斜面日射量を計算
        suraface.backside_boundary_condition.update_slop_sol(Solpos, Idn, Isky)
        # 直達日射量
        Id = suraface.backside_boundary_condition.Id

        # 天空日射量
        Isky = suraface.backside_boundary_condition.Is

        # 反射日射量
        Ir = suraface.backside_boundary_condition.Ir

        # 全天日射量
        Iw = Id + Isky + Ir

        return Id, Isky, Ir, Iw