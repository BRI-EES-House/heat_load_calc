from typing import List
import s3_space_initializer
import numpy as np

"""
付録9．	裏面相当温度
"""


# 裏面の相当温度を計算する 表.4
def calc_Teo(surfG_i, To_n: float, oldTr: float, spaces: List['s3_space_initializer'], sequence_number: int):
    Teo_i_k_n = np.zeros(surfG_i.NsurfG_i)

    for g in range(surfG_i.NsurfG_i):
        # 日射の当たる一般部位または不透明部位の場合
        if surfG_i.boundary_type[g] == "external_general_part" or surfG_i.boundary_type[g] == "external_opaque_part":
            # 室外側に日射が当たる場合
            if surfG_i.is_sun_striked_outside[g]:
                Teo_i_k_n[g] = surfG_i.Teolist[g][sequence_number]
            # 室外側に日射が当たらない場合
            else:
                Teo_i_k_n[g] = get_NextRoom_fromR(surfG_i.a_i_g[g], To_n, oldTr)

    # 窓,土壌の場合
    for g in range(surfG_i.NsurfG_i):
        if surfG_i.boundary_type[g] == "external_transparent_part" or surfG_i.boundary_type[g] == "ground":
            Teo_i_k_n[g] = surfG_i.Teolist[g][sequence_number]

    for g in range(surfG_i.NsurfG_i):
        # 内壁の場合（前時刻の室温）
        if surfG_i.boundary_type[g] == "internal":
            Teo_i_k_n[g] = spaces[surfG_i.Rnext_i_g[g]].Tr_i_n[sequence_number - 1]

    return Teo_i_k_n


# 傾斜面の相当外気温度の計算
# 日射の当たる外皮_一般部位, 日射の当たる外皮_不透明な開口部
def get_Te_n_1(To_n: np.ndarray, as_i_k: float, eps_i_k: float,
               ho_i_k_n: float, i_inc_d, i_inc_sky, i_inc_ref, r_n_is_i_j_n) -> np.ndarray:
    """
    :param as_i_k: 日射吸収率 [-]
    :param ho_i_k_n: 外表面の総合熱伝達率[W/m2K]
    :param eps_i_k: 外表面の放射率[-]
    :param To_n: 外気温度[℃]
    :param RN_n: 夜間放射量[W/m2]
    :return: 傾斜面の相当外気温度 [℃]
    """

    Te_n = To_n + (as_i_k * (i_inc_d + i_inc_sky + i_inc_ref) - eps_i_k * r_n_is_i_j_n) / ho_i_k_n

    return Te_n

# 傾斜面の相当外気温度の計算
# 外皮_透明な開口部
def get_Te_n_2(To_n: np.ndarray, eps_i_k: float,
               ho_i_k_n: float, r_n_is_i_j_n) -> np.ndarray:
    """
    :param ho_i_k_n: 外表面の総合熱伝達率[W/m2K]
    :param eps_i_k: 外表面の放射率[-]
    :param To_n: 外気温度[℃]
    :param RN_n: 夜間放射量[W/m2]
    :return: 傾斜面の相当外気温度 [℃]
    """
    Te_n = To_n + (- eps_i_k * r_n_is_i_j_n) / ho_i_k_n

    return Te_n


# 温度差係数を設定した隣室温度 ( 日射が当たらない外皮_一般部位 )
def get_NextRoom_fromR(a_i_k: float, Ta: float, Tr: float) -> float:
    Te = a_i_k * Ta + (1.0 - a_i_k) * Tr
    return Te


# 前時刻の隣室温度の場合
def get_oldNextRoom(nextroomname: str, spaces: List['s3_space_initializer'], sequence_number: int) -> float:
    Te = spaces[nextroomname].Tr_i_n[sequence_number - 1]
    return Te
