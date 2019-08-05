# 傾斜面への入射角の方向余弦を計算する

def calc_cos_incident_angle(exterior_surface, solar_position):
    return max(solar_position.Sh * exterior_surface.Wz + solar_position.Sw * exterior_surface.Ww + solar_position.Ss * exterior_surface.Ws, 0.0)