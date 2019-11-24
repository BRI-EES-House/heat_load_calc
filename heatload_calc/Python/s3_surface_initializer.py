from collections import namedtuple
from typing import List
import numpy as np

import a11_opening_transmission_solar_radiation as a11
import a23_surface_heat_transfer_coefficient as a23
import a25_window as a25
import a2_response_factor as a2
import a9_rear_surface_equivalent_temperature as a9
from s3_surface_loader import Boundary
from s3_surface_loader import InternalPartSpec
from s3_surface_loader import GeneralPartSpec
from s3_surface_loader import TransparentOpeningPartSpec
from s3_surface_loader import OpaqueOpeningPartSpec
from s3_surface_loader import GroundSpec
import a34_building_part_summarize as a34


IntegratedBoundaries = namedtuple('IntegratedBoundaries', [
    'name_i_jstrs',
    'sub_name_i_jstrs',
    'boundary_type_i_jstrs',
    'a_i_jstrs',
    'is_sun_striked_outside_i_jstrs',
    'h_i_jstrs',
    'next_room_type_i_jstrs',
    'is_solar_absorbed_inside_i_jstrs',
    'h_i_i_jstrs',
    'theta_o_sol_i_jstrs_ns',
    'n_root_i_jstrs',
    'Rows',
    'RFT0s',
    'RFA0s',
    'RFT1s',
    'RFA1s',
    'NsurfG_i'
])


def init_surface(
        boundaries: List[Boundary],
        i_dn_ns: np.ndarray, i_sky_ns: np.ndarray, r_n_ns: np.ndarray, theta_o_ns: np.ndarray,
        h_sun_ns: np.ndarray, a_sun_ns: np.ndarray) -> IntegratedBoundaries:

    # 集約化可能な境界には同じIDを振り、境界ごとにそのIDを取得する。
    # boundaries の数のIDを持つndarray
    # 例
    # [ 0  1  2  3  4  5  0  1  4  5  6  7  8  0  1  4  5  6  9  0  1  2 10  4  5 11]
    gp_idxs = a34.get_group_indices(boundaries)

    # 先頭のインデックスのリスト
    first_idx = np.array([np.where(gp_idxs == k)[0][0] for k in np.unique(gp_idxs)], dtype=np.int)

    # 室iの境界jの名前, [j]
    name_i_js = np.array([b.name for b in boundaries])

    # 室iの境界jの種類, [j]
    boundary_type_i_js = np.array([b.boundary_type for b in boundaries])

    # 室iの境界jの面積, m2, [j]
    a_i_js = np.array([b.area for b in boundaries])

    # 室iの境界jの日射の有無, [j]
    is_sun_striked_outside_i_js = np.array([b.is_sun_striked_outside for b in boundaries])

    # 室iの境界jの温度差係数, [j]
    h_i_js = np.array([b.temp_dif_coef for b in boundaries])

    def convert_from_next_room_name_to_id(name):
        if name is not None:
            return {
                'main_occupant_room': 0,
                'other_occupant_room': 1,
                'non_occupant_room': 2,
                'underfloor': 3
            }[name]
        else:
            return -1

    # 室iの境界jの隣室タイプ, [j]
    next_room_type_i_js = np.array([convert_from_next_room_name_to_id(b.next_room_type) for b in boundaries])

    # 室iの境界jの床室内侵入日射吸収の有無, [j]
    is_solar_absorbed_inside_i_js = np.array([b.is_solar_absorbed_inside for b in boundaries])

    # 室iの境界kの室内側熱伝達抵抗, m2K/W
    # 室内側熱伝達抵抗は全ての part 種類において存在する
    # 従って下記のコードは少し冗長であるがspecの1階層下で定義されているため、念の為かき分けておく。
    def get_r_i_i_ks(b):
        if type(b.spec) is InternalPartSpec:
            return b.spec.inside_heat_transfer_resistance
        elif type(b.spec) is GeneralPartSpec:
            return b.spec.inside_heat_transfer_resistance
        elif type(b.spec) is TransparentOpeningPartSpec:
            return b.spec.inside_heat_transfer_resistance
        elif type(b.spec) is OpaqueOpeningPartSpec:
            return b.spec.inside_heat_transfer_resistance
        elif type(b.spec) is GroundSpec:
            return b.spec.inside_heat_transfer_resistance
        else:
            raise TypeError

    r_i_i_ks = np.array([get_r_i_i_ks(b) for b in boundaries])

    # 室iの境界jの室内側表面総合熱伝達率, W/m2K, [j]
    h_i_i_js = a23.get_h_i_i_ks(r_i_i_ks)

    # 室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [8760*4]
    theta_o_sol_i_js_ns = np.array([
        a9.get_theta_o_sol_i_j_ns(
            boundary_i_j=b,
            theta_o_ns=theta_o_ns,
            i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, r_n_ns=r_n_ns, a_sun_ns=a_sun_ns, h_sun_ns=h_sun_ns)
        for b in boundaries])

    # 室iの境界kの熱貫流率, W/m2K
    # 定常で解く部位、つまり、透明な開口部・不透明な開口部で定義される。
    def get_u_i_ks(b):
        if type(b.spec) is InternalPartSpec:
            return None
        elif type(b.spec) is GeneralPartSpec:
            return None
        elif type(b.spec) is TransparentOpeningPartSpec:
            return b.spec.u_value
        elif type(b.spec) is OpaqueOpeningPartSpec:
            return b.spec.u_value
        elif type(b.spec) is GroundSpec:
            return None
        else:
            raise TypeError

    u_i_ks = np.array([get_u_i_ks(b) for b in boundaries])

    def get_r_layer_i_k_ls(b):
        if type(b.spec) is InternalPartSpec:
            r = [layer.thermal_resistance for layer in b.spec.layers]
            r.append(b.spec.outside_heat_transfer_resistance)
            return np.array(r)
        elif type(b.spec) is GeneralPartSpec:
            r = [layer.thermal_resistance for layer in b.spec.layers]
            r.append(b.spec.outside_heat_transfer_resistance)
            return np.array(r)
        elif type(b.spec) is TransparentOpeningPartSpec:
            return None
        elif type(b.spec) is OpaqueOpeningPartSpec:
            return None
        elif type(b.spec) is GroundSpec:
            r = [layer.thermal_resistance for layer in b.spec.layers]
            r.append(3.0 / 1.0)
            return np.array(r)
        else:
            raise TypeError

    r_layer_i_k_ls = [get_r_layer_i_k_ls(b) for b in boundaries]

    def get_c_layer_i_k_ls(b):
        if type(b.spec) is InternalPartSpec:
            c = [layer.thermal_capacity for layer in b.spec.layers]
            c.append(0.0)
            return np.array(c) * 1000.0
        elif type(b.spec) is GeneralPartSpec:
            c = [layer.thermal_capacity for layer in b.spec.layers]
            c.append(0.0)
            return np.array(c) * 1000.0
        elif type(b.spec) is TransparentOpeningPartSpec:
            return None
        elif type(b.spec) is OpaqueOpeningPartSpec:
            return None
        elif type(b.spec) is GroundSpec:
            c = [layer.thermal_capacity for layer in b.spec.layers]
            c.append(3300.0 * 3.0)
            return np.array(c) * 1000.0
        else:
            raise TypeError

    c_layer_i_k_ls = [get_c_layer_i_k_ls(b) for b in boundaries]

    # 室iの境界kの日除けの仕様 * k
    solar_shading_part_i_ks = [b.solar_shading_part for b in boundaries]











    # ========== 初期計算 ==========

    # 以下、計算結果格納用

    N_surf_i = len(boundaries)

    Uso = np.zeros(N_surf_i)

    # 応答係数
    # ※応答係数の次数は最大12として確保しておく
    RFT0, RFA0, RFT1, RFA1, Row, n_root_i_js = \
        np.zeros(N_surf_i), np.zeros(N_surf_i), np.zeros((N_surf_i, 12)), np.zeros(
            (N_surf_i, 12)), \
        np.zeros((N_surf_i, 12)), np.zeros(N_surf_i, dtype=np.int64)

    # ********** 応答係数 **********

    # 1) 非一般部位
    f = np.logical_not((boundary_type_i_js == "external_general_part")
                       | (boundary_type_i_js == "internal")
                       | (boundary_type_i_js == "ground"))

    # 開口部の室内表面から屋外までの熱貫流率[W / (m2･K)] 式(124)
    Uso[f] = a25.get_Uso(u_i_ks[f], r_i_i_ks[f])

    RFT0[f], RFA0[f], RFT1[f], RFA1[f], Row[f], n_root_i_js[f] = \
        1.0, 1.0 / Uso[f], np.zeros(12), np.zeros(12), np.zeros(12), 0

    # 2) 一般部位
    for k in range(N_surf_i):
        if boundary_type_i_js[k] in ["external_general_part", "internal", "ground"]:
            is_ground = boundary_type_i_js[k] == "ground"

            # 応答係数
            RFT0[k], RFA0[k], RFT1[k], RFA1[k], Row[k], n_root_i_js[k] = \
                a2.calc_response_factor(is_ground, c_layer_i_k_ls[k], r_layer_i_k_ls[k])




    # 室iの統合された境界j*の名称, [j*]
    name_i_jstrs = np.array(['integrated_boundary' + str(i) for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の副名称（統合する前の境界の名前を'+'記号でつなげたもの）, [j*]
    sub_name_i_jstrs = np.array(['+'.join(name_i_js[gp_idxs == i]) for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の種類, [j*]
    boundary_type_i_jstrs = [boundary_type_i_js[first_idx[i]] for i in np.unique(gp_idxs)]

    # 室iの統合された境界j*の面積, [j*]
    a_i_jstrs = np.array([np.sum(a_i_js[gp_idxs == i]) for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の日射の有無, [j*]
    is_sun_striked_outside_i_jstrs = np.array([is_sun_striked_outside_i_js[first_idx[i]] for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の温度差係数, [j*]
    h_i_jstrs = np.array([h_i_js[first_idx[i]] for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の隣室タイプ, [j*]
    next_room_type_i_jstrs = np.array([next_room_type_i_js[first_idx[i]] for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の床室内侵入日射吸収の有無, [j*]
    is_solar_absorbed_inside_i_jstrs = np.array([is_solar_absorbed_inside_i_js[first_idx[i]] for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の室内側表面総合熱伝達率, W/m2K, [j*]
    h_i_i_jstrs = np.array([h_i_i_js[first_idx[i]] for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の傾斜面のステップnにおける相当外気温度, ℃, [j*, 8760*4]
    theta_o_sol_i_jstrs_ns = np.array([
        get_are_weighted_averaged_values(v=theta_o_sol_i_js_ns[gp_idxs == i], a=a_i_js[gp_idxs == i])
        for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の応答係数法（項別公比法）における根の数, [j*]
    n_root_i_jstrs = np.array([n_root_i_js[first_idx[i]] for i in np.unique(gp_idxs)])

    Rows = np.array([Row[first_idx[i]] for i in np.unique(gp_idxs)])

    RFT0s = np.array([
        get_area_weighted_averaged_values_one_dimention(v=RFT0[gp_idxs == i], a=a_i_js[gp_idxs == i])
        for i in np.unique(gp_idxs)
    ])

    RFA0s = np.array([
        get_area_weighted_averaged_values_one_dimention(v=RFA0[gp_idxs == i], a=a_i_js[gp_idxs == i])
        for i in np.unique(gp_idxs)
    ])

    RFT1s = np.array([
        get_are_weighted_averaged_values(v=RFT1[gp_idxs == i], a=a_i_js[gp_idxs == i]) for i in np.unique(gp_idxs)
    ])

    RFA1s = np.array([
        get_are_weighted_averaged_values(v=RFA1[gp_idxs == i], a=a_i_js[gp_idxs == i]) for i in np.unique(gp_idxs)
    ])

    NsurfG_i = len(np.unique(gp_idxs))

    ib = IntegratedBoundaries(
        name_i_jstrs=name_i_jstrs,
        sub_name_i_jstrs=sub_name_i_jstrs,
        boundary_type_i_jstrs=boundary_type_i_jstrs,
        a_i_jstrs=a_i_jstrs,
        is_sun_striked_outside_i_jstrs=is_sun_striked_outside_i_jstrs,
        h_i_jstrs=h_i_jstrs,
        next_room_type_i_jstrs=next_room_type_i_jstrs,
        is_solar_absorbed_inside_i_jstrs=is_solar_absorbed_inside_i_jstrs,
        h_i_i_jstrs=h_i_i_jstrs,
        theta_o_sol_i_jstrs_ns=theta_o_sol_i_jstrs_ns,
        n_root_i_jstrs=n_root_i_jstrs,
        Rows=Rows,
        RFT0s=RFT0s,
        RFA0s=RFA0s,
        RFT1s=RFT1s,
        RFA1s=RFA1s,
        NsurfG_i=NsurfG_i
    )

    return ib

def get_area_weighted_averaged_values_one_dimention(v, a):
    return np.sum(v * a / np.sum(a))

def get_are_weighted_averaged_values(v: np.ndarray, a: np.ndarray) -> np.ndarray:
    """
    時系列データ等複数の値もつ1次元配列のデータを複数もつマトリックスを面積加重平均する。

    Args:
        v: ベクトル（2次元） [m, n] （m=境界の数）
        a: 面積, m2, [境界の数]

    Returns:
        面積荷重平均化された1次元配列の値 [n]
    """

    # 面積割合, [境界の数]　ただし、行列計算可能なように[m,1]の2次元配列としている。
    r = (a / np.sum(a)).reshape(-1, 1)

    result = np.sum(v * r, axis=0)

    return result


def is_solar_radiation_transmitted(boundary: Boundary):

    if boundary.boundary_type == 'external_transparent_part':

        if boundary.is_sun_striked_outside:

            return True

        else:

            return False
    else:

        return False


def get_transmitted_solar_radiation(
        boundaries: List[Boundary], i_dn_ns, i_sky_ns, h_sun_ns, a_sun_ns):

    bs = [b for b in boundaries if is_solar_radiation_transmitted(b)]

    q = a11.test(boundaries=bs, i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, h_sun_ns=h_sun_ns, a_sun_ns=a_sun_ns)

    return q



