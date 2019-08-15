from apdx6_direction_cos_incident_angle import calc_cos_incident_angle
from apdx5_solar_position import defSolpos

# 傾斜面日射量を計算する
def calc_slope_sol(backside_boundary_condition, Solpos: defSolpos, Idn, Isky):
        Id = Is = Ir = Iw = backside_boundary_condition.CosT = Ihol = 0.0
        if 'external' in backside_boundary_condition.Type and backside_boundary_condition.is_sun_striked_outside:
                Ihol = Solpos.sin_h_s * Idn + Isky  # 水平面全天日射量

                # 入射角の計算
                sin_h_s = Solpos.sin_h_s
                cos_h_s = Solpos.cos_h_s
                sin_a_s = Solpos.sin_a_s
                cos_a_s = Solpos.cos_a_s
                wa = backside_boundary_condition.Wa
                wb = backside_boundary_condition.Wb

                backside_boundary_condition.CosT = calc_cos_incident_angle(sin_h_s, cos_h_s, sin_a_s, cos_a_s, wa, wb)

                # 直達日射量
                Id = backside_boundary_condition.CosT * Idn

                # 天空日射量
                Is = backside_boundary_condition.Fs * Isky

                # 反射日射量
                Ir = backside_boundary_condition.dblFg * backside_boundary_condition.Rg * Ihol

                # 全天日射量
                Iw = Id + Is + Ir

        return (Id, Is, Ir, Iw)