import numpy as np
from apdx10_oblique_incidence_characteristics import get_CID

"""
付録11．窓の透過日射熱取得の計算
"""


# 透過日射量[W]、吸収日射量[W]の計算 式(90)
def calc_Qgt(CosT: np.ndarray, incident_angle_characteristics, Id: np.ndarray, Fsdw: np.ndarray, Isky: np.ndarray, Ir: np.ndarray, area, T, Cd):

    # 直達日射の入射角特性の計算
    CID = get_CID(CosT, incident_angle_characteristics)

    # 直達成分
    Qgtd = get_QGTD(T, Id, CID, Fsdw)

    # 拡散成分
    Qgts = get_QGTS(T, Cd, Isky, Ir)

    # 透過日射量の計算
    Qgt = (Qgtd + Qgts) * area

    return Qgt


# 透過日射熱取得（直達成分）[W/m2]の計算
def get_QGTD(T, Id: np.ndarray, CID: np.ndarray, Fsdw: np.ndarray) -> np.ndarray:
    """
    :param Id: 傾斜面入射直達日射量[W/m2]
    :param CID: 直達日射の入射角特性
    :param Fsdw: 日よけ等による日影面積率
    :return: 透過日射熱取得（直達成分）[W/m2]
    """
    # 透過日射熱取得（直達成分）[W/m2]の計算
    QGTD = T * (1.0 - Fsdw) * CID * Id

    return QGTD


# 透過日射熱取得（拡散成分）[W/m2]の計算
def get_QGTS(T: float, Cd: np.ndarray, Isk: np.ndarray, Ir: np.ndarray) -> np.ndarray:
    """
    :param Isk: 傾斜面入射天空日射量[W/m2]
    :param Ir: 傾斜面入射反射日射量[W/m2]
    :return: 透過日射熱取得（拡散成分）[W/m2]
    """
    QGTS = T * Cd * (Isk + Ir)
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
                        surface.Fsdw = calc_shading_area_ratio(surface, solar_position)
                    Qgt[item] += calc_Qgt(surface)

            item += 1
        nnow += 1
    return Qgt """