from typing import List
import Surface
import Space
import a19_Exsrf
import numpy as np

"""
付録9．	裏面相当温度
"""


# 裏面の相当温度を計算する 表.4
def calc_Teo(surface: Surface, To_n: float, oldTr: float, spaces: List['Space'], sequence_number: int):
    # 日射の当たる一般部位または不透明部位の場合
    if surface.boundary_type == "external_general_part" or surface.boundary_type == "external_opaque_part":
        # 室外側に日射が当たる場合
        if surface.is_sun_striked_outside:
            return surface.Teolist[sequence_number]
        # 室外側に日射が当たらない場合
        else:
            return get_NextRoom_fromR(surface.a_i_k, To_n, oldTr)
    # 窓,土壌の場合
    elif surface.boundary_type == "external_transparent_part" or surface.boundary_type == "ground":
        return surface.Teolist[sequence_number]
    # 内壁の場合（前時刻の室温）
    elif surface.boundary_type == "internal":
        return get_oldNextRoom(surface.nextroomname, spaces)
    # 例外
    else:
        print("境界条件が見つかりません。 name=", surface.boundary_type)


# 傾斜面の相当外気温度の計算
# 日射の当たる外皮_一般部位, 日射の当たる外皮_不透明な開口部
def get_Te_n_1(To_n: np.ndarray, as_i_k: float, I_w_i_k_n: np.ndarray, eps_i_k: float, PhiS_i_k: float, RN_n: np.ndarray,
               ho_i_k_n: float) -> np.ndarray:
    """
    :param as_i_k: 日射吸収率 [-]
    :param ho_i_k_n: 外表面の総合熱伝達率[W/m2K]
    :param eps_i_k: 外表面の放射率[-]
    :param To_n: 外気温度[℃]
    :param RN_n: 夜間放射量[W/m2]
    :return: 傾斜面の相当外気温度 [℃]
    """
    Te_n = To_n + (as_i_k * I_w_i_k_n - eps_i_k * PhiS_i_k * RN_n) / ho_i_k_n

    return Te_n

# 傾斜面の相当外気温度の計算
# 外皮_透明な開口部
def get_Te_n_2(To_n: np.ndarray, eps_i_k: float, PhiS_i_k: float, RN_n: np.ndarray,
               ho_i_k_n: float) -> np.ndarray:
    """
    :param ho_i_k_n: 外表面の総合熱伝達率[W/m2K]
    :param eps_i_k: 外表面の放射率[-]
    :param To_n: 外気温度[℃]
    :param RN_n: 夜間放射量[W/m2]
    :return: 傾斜面の相当外気温度 [℃]
    """
    Te_n = To_n + (- eps_i_k * PhiS_i_k * RN_n) / ho_i_k_n

    return Te_n


# 温度差係数を設定した隣室温度 ( 日射が当たらない外皮_一般部位 )
def get_NextRoom_fromR(a_i_k: float, Ta: float, Tr: float) -> float:
    Te = a_i_k * Ta + (1.0 - a_i_k) * Tr
    return Te


# 前時刻の隣室温度の場合
def get_oldNextRoom(nextroomname: str, spaces: List['Space']) -> float:
    Te = spaces[nextroomname].oldTr
    return Te

""" # 相当外気温度の計算
def precalcTeo(space: Space, To: float, I_DN: float, I_sky: float, RN: float, annual_average_ta: float, defSolpos: defSolpos, sequence_number: int):
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
                surface.backside_boundary_condition.cos_Theta_i_k_n = cos_t
                Fs = surface.backside_boundary_condition.Fs
                dblFg = surface.backside_boundary_condition.dblFg
                Rg = surface.backside_boundary_condition.Rg

                surface.I_D_i_k_n, surface.I_sky, surface.I_R_i_k_n, surface.Iw_i_k_n = calc_slope_sol(I_DN, I_sky, sin_h_s, cos_t, Fs, dblFg, Rg)
            else:
                surface.backside_boundary_condition.cos_Theta_i_k_n = 0.0
                surface.I_D_i_k_n, surface.I_sky, surface.I_R_i_k_n, surface.Iw_i_k_n = 0.0, 0.0, 0.0, 0.0
        elif surface.boundary_type == "ground":
            surface.Teo = annual_average_ta

    # 相当外気温度の計算
    for surface in space.input_surfaces:
        if surface.is_sun_striked_outside:
            # 外皮_一般部位もしくは外皮_不透明部位の場合
            if surface.boundary_type == "external_general_part" or surface.boundary_type == "external_opaque_part":
                surface.Teolist[sequence_number] = get_Te_n_1(surface.backside_boundary_condition, \
                    surface.Iw_i_k_n, surface.as_i_k, surface.ho_i_k_n, surface.eps_i_k, To, RN)
            # 外皮_透明部位の場合
            else:
                surface.Teolist[sequence_number] = - surface.eps_i_k * surface.backside_boundary_condition.Fs * RN / surface.ho_i_k_n + To """
