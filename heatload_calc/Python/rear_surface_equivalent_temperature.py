from typing import List
import Surface
import Space
import Exsrf
from apdx5_solar_position import defSolpos
from apdx6_direction_cos_incident_angle import calc_cos_incident_angle
from inclined_surface_solar_radiation import calc_slope_sol

# 裏面の相当温度を計算する
def calcTeo(surface: Surface, Ta: float, oldTr: float, AnnualTave: float, spaces: List['Space'], sequence_number: int):
    # 前時刻の相当外気温度を控える
    surface.oldTeo = surface.Teo

    # 日射の当たる一般部位または不透明部位の場合
    if surface.boundary_type == "external_general_part" or surface.boundary_type == "external_opaque_part":
        # 室外側に日射が当たる場合
        if surface.is_sun_striked_outside:
            surface.Teo = surface.Teolist[sequence_number]
        # 室外側に日射が当たらない場合
        else:
            surface.Teo = get_NextRoom_fromR(surface.backside_boundary_condition, Ta, oldTr)
    # 窓の場合
    elif surface.boundary_type == "external_transparent_part":
        surface.Teo = surface.Teolist[sequence_number]
    # 土壌の場合
    elif surface.boundary_type == "ground":
        surface.Teo = AnnualTave
    # 内壁の場合（前時刻の室温）
    elif surface.boundary_type == "internal":
        surface.Teo = get_oldNextRoom(surface.backside_boundary_condition, spaces)
    # 例外
    else:
        print("境界条件が見つかりません。 name=", surface.boundary_type)

# 傾斜面の相当外気温度の計算
def get_Te(exsrf: Exsrf, Iw: float,  _as: float, ho: float, e: float, Ta: float, RN: float) -> float:
    """
    :param _as: 日射吸収率 [-]
    :param ho: 外表面の総合熱伝達率[W/m2K]
    :param e: 外表面の放射率[-]
    :param Ta: 外気温度[℃]
    :param RN: 夜間放射量[W/m2]
    :return: 傾斜面の相当外気温度 [℃]
    """
    Te = Ta + (_as * Iw - exsrf.Fs * e * RN) / ho

    return Te

# 温度差係数を設定した隣室温度
def get_NextRoom_fromR(exsrf: Exsrf, Ta: float, Tr: float) -> float:
    Te = exsrf.R * Ta + (1.0 - exsrf.R) * Tr
    return Te

# 前時刻の隣室温度の場合
def get_oldNextRoom(exsrf: Exsrf, spaces: List['Space']) -> float:
    Te = spaces[exsrf.nextroomname].oldTr
    return Te

# 相当外気温度の計算
def precalcTeo(space: Space, Ta: float, Idn: float, Isky: float, RN: float, defSolpos: defSolpos, sequence_number: int):
    # 外皮の傾斜面日射量の計算
    for surface in space.input_surfaces:
        if surface.is_sun_striked_outside:
            sin_h_s = defSolpos.sin_h_s
            cos_h_s = defSolpos.cos_h_s
            sin_a_s = defSolpos.sin_a_s
            cos_a_s = defSolpos.cos_a_s
            wa = surface.backside_boundary_condition.Wa
            wb = surface.backside_boundary_condition.Wb

            if 'external' in surface.backside_boundary_condition.Type and surface.backside_boundary_condition.is_sun_striked_outside:
                cos_t = calc_cos_incident_angle(sin_h_s, cos_h_s, sin_a_s, cos_a_s, wa, wb)
                surface.backside_boundary_condition.CosT = cos_t
                Fs = surface.backside_boundary_condition.Fs
                dblFg = surface.backside_boundary_condition.dblFg
                Rg = surface.backside_boundary_condition.Rg

                surface.Id, surface.Isky, surface.Ir, surface.Iw = calc_slope_sol(Idn, Isky, sin_h_s, cos_t, Fs, dblFg, Rg)
            else:
                surface.backside_boundary_condition.CosT = 0.0
                surface.Id, surface.Isky, surface.Ir, surface.Iw = 0.0, 0.0, 0.0, 0.0
        

    # 相当外気温度の計算
    for surface in space.input_surfaces:
        if surface.is_sun_striked_outside:
            # 外皮_一般部位もしくは外皮_不透明部位の場合
            if surface.boundary_type == "external_general_part" or surface.boundary_type == "external_opaque_part":
                surface.Teolist[sequence_number] = get_Te(surface.backside_boundary_condition, \
                    surface.Iw, surface.outside_solar_absorption, surface.ho, surface.Eo, Ta, RN)
            # 外皮_透明部位の場合
            else:
                surface.Teolist[sequence_number] = - surface.Eo * surface.backside_boundary_condition.Fs * RN / surface.ho + Ta
