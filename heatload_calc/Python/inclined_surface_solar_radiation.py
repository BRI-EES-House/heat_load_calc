

def calc_slope_sol(
    i_sun_dir: float, i_sun_sky: float, sin_h_s: float, cos_phi: float,
    phi_evlp_sky: float, phi_evlp_grd: float, rho_grd: float) ->(float, float, float, float):
    """
    Args:
        i_sun_dir: 法線面直達日射量, W/m2K
        i_sun_sky: 水平面天空日射量, W/m2K
        sin_h_s: 太陽高度の正弦
        cos_phi: 外表面における入射角の正弦
        phi_evlp_sky: 外表面における天空に対する形態係数
        phi_evlp_grd: 外表面における地面に対する形態係数
        rho_grd: 地面日射反射率
    Returns:
        傾斜面直達日射量, W/m2K
        傾斜面天空日射量, W/m2K
        傾斜面反射日射量, W/m2K
        傾斜面日射量の合計, W/m2K
    """

    # 直達日射量
    i_evlp_dir = cos_phi * i_sun_dir

    # 天空日射量
    i_evlp_sky = phi_evlp_sky * i_sun_sky

    # 反射日射量
    i_sun_hrz = sin_h_s * i_sun_dir + i_sun_sky  # 水平面全天日射量
    i_evlp_ref = phi_evlp_grd * rho_grd * i_sun_hrz

    # 日射量の合計
    i_evlp = i_evlp_dir + i_evlp_sky + i_evlp_ref

    return i_evlp_dir, i_evlp_sky, i_evlp_ref, i_evlp
