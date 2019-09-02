import datetime
# import Weather
from Weather import Solpos, WeaData, enmWeatherComponent
from common import get_nday
from apdx10_oblique_incidence_characteristics import get_CID
from inclined_surface_solar_radiation import calc_slope_sol
from Sunbrk import calc_shading_area_ratio, get_shading_area_ratio
from apdx6_direction_cos_incident_angle import calc_cos_incident_angle

# 透過日射量[W]、吸収日射量[W]の計算
def calc_Qgt(surface):
    # 直達成分
    Qgtd = get_QGTD(surface.transparent_opening, surface.Id, \
        surface.backside_boundary_condition.CosT, surface.Fsdw, surface.transparent_opening.incident_angle_characteristics) * surface.area

    # 拡散成分
    Qgts = get_QGTS(surface.transparent_opening, surface.Isky, surface.Ir) * surface.area

    # 透過日射量の計算
    return Qgtd + Qgts

# 透過日射熱取得（直達成分）[W/m2]の計算
def get_QGTD(transparent_opening, Id: float, CosT: float, Fsdw: float, incident_angle_characteristics: str) -> float:
    """
    :param Id: 傾斜面入射直達日射量[W/m2]
    :param CosT: 入射角の方向余弦
    :param Fsdw: 日よけ等による日影面積率
    :return: 透過日射熱取得（直達成分）[W/m2]
    """
    # 直達日射の入射角特性の計算
    CID = get_CID(CosT, incident_angle_characteristics)

    # 透過日射熱取得（直達成分）[W/m2]の計算
    QGTD = transparent_opening.T * (1.0 - Fsdw) * CID * Id

    return QGTD

# 透過日射熱取得（拡散成分）[W/m2]の計算
def get_QGTS(window, Isk: float, Ir: float) -> float:
    """
    :param Isk: 傾斜面入射天空日射量[W/m2]
    :param Ir: 傾斜面入射反射日射量[W/m2]
    :return: 透過日射熱取得（拡散成分）[W/m2]
    """
    QGTS = window.T * window.Cd * (Isk + Ir)
    return QGTS

# 透過日射を集約する
""" def summarize_transparent_solar_radiation(surfaces, calc_time_interval, weather):
    # 透過日射熱取得収録配列の初期化とメモリ確保
    Qgt = []
    Qgt = [0.0 for j in range(int(8760.0 * 3600.0 / float(calc_time_interval)))]

    ntime = int(24 * 3600 / calc_time_interval)
    nnow = 0
    item = 0
    start_date = datetime.datetime(1989, 1, 1)
    for nday in range(get_nday(1, 1), get_nday(12, 31) + 1):
        for tloop in range(ntime):
            dtime = datetime.timedelta(days=nnow + float(tloop) / float(ntime))
            dtmNow = dtime + start_date

            # 太陽位置の計算
            solar_position = Solpos(weather, dtmNow)
            # 傾斜面日射量の計算
            Idn = WeaData(weather, enmWeatherComponent.Idn, dtmNow, solar_position)
            Isky = WeaData(weather, enmWeatherComponent.Isky, dtmNow, solar_position)
            for surface in surfaces:
                # 外表面に日射が当たる場合
                if surface.is_sun_striked_outside and surface.boundary_type == "external_transparent_part":
                    sin_h_s = solar_position.sin_h_s
                    cos_h_s = solar_position.cos_h_s
                    sin_a_s = solar_position.sin_a_s
                    cos_a_s = solar_position.cos_a_s
                    wa = surface.backside_boundary_condition.Wa
                    wb = surface.backside_boundary_condition.Wb

                    if 'external' in surface.backside_boundary_condition.Type and surface.backside_boundary_condition.is_sun_striked_outside:
                        cos_t = calc_cos_incident_angle(sin_h_s, cos_h_s, sin_a_s, cos_a_s, wa, wb)
                        surface.backside_boundary_condition.CosT = cos_t
                        Fs = surface.backside_boundary_condition.Fs
                        dblFg = surface.backside_boundary_condition.dblFg
                        Rg = surface.backside_boundary_condition.Rg
                        surface.Id, surface.Isky, surface.Ir, surface.Iw = calc_slope_sol(
                            Idn, Isky, sin_h_s, cos_t, Fs, dblFg, Rg)
                    else:
                        surface.backside_boundary_condition.CosT = 0.0
                        surface.Id, surface.Isky, surface.Ir, surface.Iw = 0.0, 0.0, 0.0, 0.0


                    # 日除けの日影面積率の計算
                    if surface.sunbrk.existance:
                        surface.Fsdw = get_shading_area_ratio(surface, solar_position)
                    Qgt[item] += calc_Qgt(surface)

            item += 1
        nnow += 1
    return Qgt """