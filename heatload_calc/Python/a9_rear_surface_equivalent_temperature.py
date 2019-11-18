from typing import List
import numpy as np

import x_07_inclined_surface_solar_radiation as x_07
import x_19_external_boundaries_direction as x_19

import s3_space_initializer
import a23_surface_heat_transfer_coefficient as a23

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


def get_theta_o_sol_i_j_n(boundary_i_j, theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, a_sun_ns, h_sun_ns):
    """
    相当外気温度を計算する。

    Args:
        boundary_i_j: 室iの境界j
        theta_o_ns: ステップnにおける外気温度, ℃, [8760 * 4]
        i_dn_ns: ステップnにおける法線面直達日射量, W/m2, [8760 * 4]
        i_sky_ns: ステップnにおける水平面天空日射量, W/m2, [8760 * 4]
        r_n_ns: ステップnにおける夜間放射量, W/m2, [8760 * 4]
        a_sun_ns: ステップnにおける太陽高度, deg, [8760*4]
        h_sun_ns: ステップnにおける太陽方位, deg, [8760*4]

    Returns:
        室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [8760*4]
    """

    # 間仕切りの場合
    if boundary_i_j.boundary_type == 'internal':

        # この値は使用しないのでNoneでもよいはず
        # 集約化する際にNoneだと変な挙動を示すかも知れないのでとりあえずゼロにしておく。
        return np.zeros(24 * 365 * 4)

    # 一般部位・透明な開口部・不透明な開口部の場合
    elif (boundary_i_j.boundary_type == 'external_general_part') \
            or (boundary_i_j.boundary_type == 'external_opaque_part') \
            or (boundary_i_j.boundary_type == 'external_transparent_part'):

        # 日射が当たる場合
        if boundary_i_j.is_sun_striked_outside:

            # 室iの境界jの傾斜面の方位角, rad
            # 室iの境界jの傾斜面の傾斜角, rad
            w_alpha_i_j, w_beta_i_j = x_19.get_w_alpha_i_j_w_beta_i_j(direction_i_j=boundary_i_j.direction)

            # ステップnにおける室iの境界jにおける傾斜面の夜間放射量, W/m2, [8760 * 4]
            r_n_is_i_j_ns = x_07.get_r_n_is_i_j_ns(r_n_ns=r_n_ns, w_beta_i_j=w_beta_i_j)

            if (boundary_i_j.boundary_type == 'external_general_part') \
                    or (boundary_i_j.boundary_type == 'external_opaque_part'):

                # ステップnにおける室iの境界jにおける傾斜面の日射量のうち直達成分, W/m2K [8760*4]
                # ステップnにおける室iの境界jにおける傾斜面の日射量のうち天空成分, W/m2K [8760*4]
                # ステップnにおける室iの境界jにおける傾斜面の日射量のうち地盤反射成分, W/m2K [8760*4]
                i_is_d_i_j_ns, i_is_sky_i_j_ns, i_is_ref_i_j_ns = x_07.get_i_is_i_j_ns(
                    i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, h_sun_ns=h_sun_ns, a_sun_ns=a_sun_ns,
                    w_alpha_i_j=w_alpha_i_j, w_beta_i_j=w_beta_i_j)

                # 室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [8760*4]
                # 一般部位・不透明な開口部の場合、日射・長波長放射を考慮する。
                return get_theta_o_sol_i_j_n_1(
                    theta_o_ns=theta_o_ns,
                    a_s_i_j=boundary_i_j.spec.outside_solar_absorption,
                    eps_r_i_j=boundary_i_j.spec.outside_emissivity,
                    i_is_d_i_j_ns=i_is_d_i_j_ns, i_is_sky_i_j_ns=i_is_sky_i_j_ns, i_is_ref_i_j_ns=i_is_ref_i_j_ns,
                    r_n_is_i_j_ns=r_n_is_i_j_ns,
                    r_surf_o_i_j=boundary_i_j.spec.outside_heat_transfer_resistance
                )

            # 透明な開口部の場合
            elif boundary_i_j.boundary_type == 'external_transparent_part':

                # 室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [8760*4]
                # 透明な開口部の場合、日射はガラス面への透過・吸収の項で扱うため、ここでは長波長放射のみ考慮する。
                return get_theta_o_sol_i_j_n_2(
                    theta_o_ns=theta_o_ns,
                    eps_r_i_j=boundary_i_j.spec.outside_emissivity,
                    r_n_is_i_j_ns=r_n_is_i_j_ns,
                    r_surf_o_i_j=boundary_i_j.spec.outside_heat_transfer_resistance
                )

        # 日射が当たらない場合
        else:

            return theta_o_ns

    # 地盤の場合
    elif boundary_i_j.boundary_type == 'ground':

        return np.full(24 * 365 * 4, np.average(theta_o_ns))

    else:

        raise ValueError()


#get_theta_o_sol_i_j_n
# 傾斜面の相当外気温度の計算
# 日射の当たる外皮_一般部位, 日射の当たる外皮_不透明な開口部
def get_theta_o_sol_i_j_n_1(theta_o_ns: np.ndarray, a_s_i_j: float, eps_r_i_j: float,
                            i_is_d_i_j_ns, i_is_sky_i_j_ns, i_is_ref_i_j_ns, r_n_is_i_j_ns, r_surf_o_i_j) -> np.ndarray:
    """
    :param a_s_i_j: 日射吸収率 [-]
    :param ho_i_k_n: 外表面の総合熱伝達率[W/m2K]
    :param eps_r_i_j: 外表面の放射率[-]
    :param theta_o_ns: 外気温度[℃]
    :param RN_n: 夜間放射量[W/m2]
    :return: 傾斜面の相当外気温度 [℃]
    """

    Te_n = theta_o_ns + (a_s_i_j * (i_is_d_i_j_ns + i_is_sky_i_j_ns + i_is_ref_i_j_ns) - eps_r_i_j * r_n_is_i_j_ns) * r_surf_o_i_j

    return Te_n

# 傾斜面の相当外気温度の計算
# 外皮_透明な開口部
def get_theta_o_sol_i_j_n_2(theta_o_ns: np.ndarray, eps_r_i_j: float,
                            r_n_is_i_j_ns, r_surf_o_i_j) -> np.ndarray:
    """
    :param ho_i_k_n: 外表面の総合熱伝達率[W/m2K]
    :param eps_r_i_j: 外表面の放射率[-]
    :param theta_o_ns: 外気温度[℃]
    :param RN_n: 夜間放射量[W/m2]
    :return: 傾斜面の相当外気温度 [℃]
    """
    Te_n = theta_o_ns + (- eps_r_i_j * r_n_is_i_j_ns) * r_surf_o_i_j

    return Te_n


# 温度差係数を設定した隣室温度 ( 日射が当たらない外皮_一般部位 )
def get_NextRoom_fromR(a_i_k: float, Ta: float, Tr: float) -> float:
    Te = a_i_k * Ta + (1.0 - a_i_k) * Tr
    return Te


# 前時刻の隣室温度の場合
def get_oldNextRoom(nextroomname: str, spaces: List['s3_space_initializer'], sequence_number: int) -> float:
    Te = spaces[nextroomname].Tr_i_n[sequence_number - 1]
    return Te
