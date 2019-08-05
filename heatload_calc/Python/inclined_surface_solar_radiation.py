from direction_cos_incident_angle import calc_cos_incident_angle

# 傾斜面日射量を計算する
def calc_slope_sol(backside_boundary_condition, Solpos, Idn, Isky):
        Id = Is = Ir = Iw = backside_boundary_condition.CosT = Ihol = 0.0
        if 'external' in backside_boundary_condition.Type and backside_boundary_condition.is_sun_striked_outside:
                Ihol = Solpos.Sh * Idn + Isky  # 水平面全天日射量

                # 入射角の計算
                backside_boundary_condition.CosT = calc_cos_incident_angle(backside_boundary_condition, Solpos)
                # 直達日射量
                Id = backside_boundary_condition.CosT * Idn

                # 天空日射量
                Is = backside_boundary_condition.Fs * Isky

                # 反射日射量
                Ir = backside_boundary_condition.dblFg * backside_boundary_condition.Rg * Ihol

                # 全天日射量
                Iw = Id + Is + Ir

        return (Id, Is, Ir, Iw)