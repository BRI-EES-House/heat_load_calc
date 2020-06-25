from collections import namedtuple
from typing import List
import numpy as np

import heat_load_calc.a2_response_factor as a2
import heat_load_calc.a9_rear_surface_equivalent_temperature as a9
import heat_load_calc.a11_opening_transmission_solar_radiation as a11
import heat_load_calc.a23_surface_heat_transfer_coefficient as a23
import heat_load_calc.a34_building_part_summarize as a34
from heat_load_calc.s3_surface_loader import Boundary
from heat_load_calc.s3_surface_loader import InternalPartSpec
from heat_load_calc.s3_surface_loader import GeneralPartSpec
from heat_load_calc.s3_surface_loader import TransparentOpeningPartSpec
from heat_load_calc.s3_surface_loader import OpaqueOpeningPartSpec
from heat_load_calc.s3_surface_loader import GroundSpec
from heat_load_calc.a39_global_parameters import BoundaryType


IntegratedBoundaries = namedtuple('IntegratedBoundaries', [
    'name_i_jstrs',
    'sub_name_i_jstrs',
    'boundary_type_i_jstrs',
    'a_i_jstrs',
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

    # 室iの境界jの室内侵入日射吸収の有無, [j]
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

    # 室iの境界kの日除けの仕様 * k
    solar_shading_part_i_ks = [b.solar_shading_part for b in boundaries]

    # 室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [8760*4]
    theta_o_sol_i_js_ns = np.array([
        a9.get_theta_o_sol_i_j_ns(
            boundary_i_j=b,
            theta_o_ns=theta_o_ns,
            i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, r_n_ns=r_n_ns, a_sun_ns=a_sun_ns, h_sun_ns=h_sun_ns)
        for b in boundaries])

    rfs = [a2.get_response_factors(b) for b in boundaries]

    RFT0 = np.array([rf.rft0 for rf in rfs])
    RFA0 = np.array([rf.rfa0 for rf in rfs])
    RFT1 = np.array([rf.rft1 for rf in rfs])
    RFA1 = np.array([rf.rfa1 for rf in rfs])
    Row = np.array([rf.row for rf in rfs])
    n_root_i_js = np.array([rf.n_root for rf in rfs])

    # 室iの統合された境界j*の名称, [j*]
    name_i_jstrs = np.array(['integrated_boundary' + str(i) for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の副名称（統合する前の境界の名前を'+'記号でつなげたもの）, [j*]
    sub_name_i_jstrs = np.array(['+'.join(name_i_js[gp_idxs == i]) for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の種類, [j*]
    boundary_type_i_jstrs = np.array([boundary_type_i_js[first_idx[i]] for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の面積, [j*]
    a_i_jstrs = np.array([np.sum(a_i_js[gp_idxs == i]) for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の温度差係数, [j*]
    h_i_jstrs = np.array([h_i_js[first_idx[i]] for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の隣室タイプ, [j*]
    next_room_type_i_jstrs = np.array([next_room_type_i_js[first_idx[i]] for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の室内侵入日射吸収の有無, [j*]
    is_solar_absorbed_inside_i_jstrs = np.array([is_solar_absorbed_inside_i_js[first_idx[i]] for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の室内側表面総合熱伝達率, W/m2K, [j*]
    h_i_i_jstrs = np.array([h_i_i_js[first_idx[i]] for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の傾斜面のステップnにおける相当外気温度, ℃, [j*, 8760*4]
    theta_o_sol_i_jstrs_ns = np.array([
        get_area_weighted_averaged_values_two_dimension(v=theta_o_sol_i_js_ns[gp_idxs == i], a=a_i_js[gp_idxs == i])
        for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の応答係数法（項別公比法）における根の数, [j*]
    n_root_i_jstrs = np.array([n_root_i_js[first_idx[i]] for i in np.unique(gp_idxs)])

    Rows = np.array([Row[first_idx[i]] for i in np.unique(gp_idxs)])

    RFT0s = np.array([
        get_area_weighted_averaged_values_one_dimension(v=RFT0[gp_idxs == i], a=a_i_js[gp_idxs == i])
        for i in np.unique(gp_idxs)
    ])

    RFA0s = np.array([
        get_area_weighted_averaged_values_one_dimension(v=RFA0[gp_idxs == i], a=a_i_js[gp_idxs == i])
        for i in np.unique(gp_idxs)
    ])

    RFT1s = np.array([
        get_area_weighted_averaged_values_two_dimension(v=RFT1[gp_idxs == i], a=a_i_js[gp_idxs == i]) for i in np.unique(gp_idxs)
    ])

    RFA1s = np.array([
        get_area_weighted_averaged_values_two_dimension(v=RFA1[gp_idxs == i], a=a_i_js[gp_idxs == i]) for i in np.unique(gp_idxs)
    ])

    NsurfG_i = len(np.unique(gp_idxs))

    return IntegratedBoundaries(
        name_i_jstrs=name_i_jstrs,
        sub_name_i_jstrs=sub_name_i_jstrs,
        boundary_type_i_jstrs=boundary_type_i_jstrs,
        a_i_jstrs=a_i_jstrs,
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


def get_area_weighted_averaged_values_one_dimension(v: np.ndarray, a: np.ndarray) -> np.ndarray:
    """
    あるデータを面積荷重平均する。
    Args:
        v: ベクトル（1次元）, [m] (m=境界の数）
        a: 面積, m2, [m] (m=境界の数）

    Returns:
        面積荷重平均化された値
    """
    return np.sum(v * a / np.sum(a))


def get_area_weighted_averaged_values_two_dimension(v: np.ndarray, a: np.ndarray) -> np.ndarray:
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


def get_transmitted_solar_radiation(boundaries: List[Boundary], i_dn_ns, i_sky_ns, h_sun_ns, a_sun_ns):

    bs = [b for b in boundaries if is_solar_radiation_transmitted(b)]

    q = a11.test(boundaries=bs, i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, h_sun_ns=h_sun_ns, a_sun_ns=a_sun_ns)

    return q


def is_solar_radiation_transmitted(boundary: Boundary):

    if boundary.boundary_type == BoundaryType.ExternalTransparentPart:

        if boundary.is_sun_striked_outside:

            return True

        else:

            return False
    else:

        return False



