from collections import namedtuple
from typing import List
import numpy as np

import heat_load_calc.a2_response_factor as a2
import heat_load_calc.a9_rear_surface_equivalent_temperature as a9
import heat_load_calc.a11_opening_transmission_solar_radiation as a11
import heat_load_calc.a34_building_part_summarize as a34
from heat_load_calc.s3_surface_loader import Boundary
from heat_load_calc.s3_surface_loader import InternalPartSpec
from heat_load_calc.s3_surface_loader import GeneralPartSpec
from heat_load_calc.s3_surface_loader import TransparentOpeningPartSpec
from heat_load_calc.s3_surface_loader import OpaqueOpeningPartSpec
from heat_load_calc.s3_surface_loader import GroundSpec
from heat_load_calc.initializer.boundary_type import BoundaryType
from heat_load_calc.initializer.boundary_simple import BoundarySimple
import heat_load_calc.s3_surface_loader as s3_loader


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
    'NsurfG_i',
    'q_trs_i_jstrs_ns'
])


def get_boundary_simple(theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, a_sun_ns, h_sun_ns, b):

    # 名前
    name = b['name']
    sub_name = ''

    # 境界の種類
    # 'internal': 間仕切り
    # 'external_general_part': 外皮_一般部位
    # 'external_transparent_part': 外皮_透明な開口部
    # 'external_opaque_part': 外皮_不透明な開口部
    # 'ground': 地盤
    # boundary_type = b['boundary_type']
    boundary_type = {
        'internal': BoundaryType.Internal,
        'external_general_part': BoundaryType.ExternalGeneralPart,
        'external_transparent_part': BoundaryType.ExternalTransparentPart,
        'external_opaque_part': BoundaryType.ExternalOpaquePart,
        'ground': BoundaryType.Ground
    }[b['boundary_type']]

    # 面積, m2
    area = float(b['area'])

    # 温度差係数
    # 境界の種類が'external_general_part', 'external_transparent_part', 'external_opaque_part'の場合に定義される。
    if b['boundary_type'] in ['external_general_part', 'external_transparent_part', 'external_opaque_part']:
        h_td = float(b['temp_dif_coef'])
    else:
        h_td = 0.0

    # 隣室タイプ
    # 境界の種類が'internal'の場合に定義される。
    # 隣室タイプにひもづけて隣室のIDを取得している。
    # 本来であれば、IDで直接指定する方が望ましい。
    # TODO: ID指定に変更する。
    next_room_type = {
        'main_occupant_room': 0,
        'other_occupant_room': 1,
        'non_occupant_room': 2,
        'underfloor': 3
    }[b['next_room_type']] if b['boundary_type'] == 'internal' else -1

    # 室内侵入日射吸収の有無
    # True: 吸収する
    # False: 吸収しない
    is_solar_absorbed_inside = bool(b['is_solar_absorbed_inside'])

    # 日射の有無
    # True: 当たる
    # False: 当たらない
    # 境界の種類が'external_general_part', 'external_transparent_part', 'external_opaque_part'の場合に定義される。
    if b['boundary_type'] in ['external_general_part', 'external_transparent_part', 'external_opaque_part']:
        is_sun_striked_outside = bool(b['is_sun_striked_outside'])
    else:
        is_sun_striked_outside = None

    # 方位
    # 's', 'sw', 'w', 'nw', 'n', 'ne', 'e', 'se', 'top', 'bottom'
    # 日射の有無が定義されている場合でかつその値がTrueの場合のみ定義される。
    if 'is_sun_striked_outside' in b:
        if b['is_sun_striked_outside']:
            direction = b['direction']
        else:
            direction = None
    else:
        direction = None

    # 室内側熱伝達抵抗, m2K/W
    r_i = b['inside_heat_transfer_resistance']

    # 室内側表面総合熱伝達率, W/m2K
    h_i = 1.0 / r_i

    # ===============================

    b = s3_loader.get_boundary(b)

    # 相当外気温度, degree C, [8760 * 4]
    theta_o_sol = a9.get_theta_o_sol_i_j_ns(
        boundary_i_j=b,
        theta_o_ns=theta_o_ns,
        i_dn_ns=i_dn_ns,
        i_sky_ns=i_sky_ns,
        r_n_ns=r_n_ns,
        a_sun_ns=a_sun_ns,
        h_sun_ns=h_sun_ns
    )

    # 透過日射量, W, [8760*4]
    if is_solar_radiation_transmitted(b):
        q_trs_sol = a11.get_qgt(a_sun_ns=a_sun_ns, b=b, h_sun_ns=h_sun_ns, i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns)
    else:
        q_trs_sol = np.zeros(8760*4, dtype=float)

    # 応答係数
    rfs = a2.get_response_factors(b)

    return BoundarySimple(
        name=name,
        sub_name=sub_name,
        boundary_type=boundary_type,
        area=area,
        h_td=h_td,
        next_room_type=next_room_type,
        is_solar_absorbed_inside=is_solar_absorbed_inside,
        is_sun_striked_outside=is_sun_striked_outside,
        direction=direction,
        h_i=h_i,
        theta_o_sol=theta_o_sol,
        q_trs_sol=q_trs_sol,
        n_root=rfs.n_root,
        row=rfs.row,
        rfa0=rfs.rfa0,
        rfa1=rfs.rfa1,
        rft0=rfs.rft0,
        rft1=rfs.rft1
    )


def init_surface(bss: List[BoundarySimple]) -> IntegratedBoundaries:

    bss = np.array(bss)

    # 集約化可能な境界には同じIDを振り、境界ごとにそのIDを取得する。
    # boundaries の数のIDを持つndarray
    # 例
    # [ 0  1  2  3  4  5  0  1  4  5  6  7  8  0  1  4  5  6  9  0  1  2 10  4  5 11]
    gp_idxs = a34.get_group_indices(bss=bss)

    # 先頭のインデックスのリスト
    first_idx = np.array([np.where(gp_idxs == k)[0][0] for k in np.unique(gp_idxs)], dtype=np.int)

    # 室iの統合された境界j*の名称, [j*]
    name_i_jstrs = np.array(['integrated_boundary' + str(i) for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の副名称（統合する前の境界の名前を'+'記号でつなげたもの）, [j*]
    sub_name_i_jstrs = np.array(['+'.join([bs.name for bs in bss[gp_idxs == i]]) for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の種類, [j*]
    boundary_type_i_jstrs = np.array([bss[first_idx[i]].boundary_type for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の面積, [j*]
    a_i_jstrs = np.array([np.sum([bs.area for bs in bss[gp_idxs == i]]) for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の温度差係数, [j*]
    h_i_jstrs = np.array([bss[first_idx[i]].h_td for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の隣室タイプ, [j*]
    next_room_type_i_jstrs = np.array([bss[first_idx[i]].next_room_type for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の室内侵入日射吸収の有無, [j*]
    is_solar_absorbed_inside_i_jstrs = np.array([bss[first_idx[i]].is_solar_absorbed_inside for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の室内側表面総合熱伝達率, W/m2K, [j*]
    h_i_i_jstrs = np.array([bss[first_idx[i]].h_i for i in np.unique(gp_idxs)])

    # 室iの統合された境界j*の傾斜面のステップnにおける相当外気温度, ℃, [j*, 8760*4]
    theta_o_sol_i_jstrs_ns = np.array([
        get_area_weighted_averaged_values_two_dimension(
            v=np.array([bs.theta_o_sol for bs in bss[gp_idxs == i]]),
            a=np.array([bs.area for bs in bss[gp_idxs == i]])
        )
        for i in np.unique(gp_idxs)])

    q_trs_sol_i_jstrs_ns = np.array([
        np.sum([bs.q_trs_sol for bs in bss[gp_idxs == i]], axis=0)
        for i in np.unique(gp_idxs)
    ])

    # 室iの統合された境界j*の応答係数法（項別公比法）における根の数, [j*]
    n_root_i_jstrs = np.array([bss[first_idx[i]].n_root for i in np.unique(gp_idxs)])

    Rows = np.array([bss[first_idx[i]].row for i in np.unique(gp_idxs)])

    RFT0s = np.array([
        get_area_weighted_averaged_values_one_dimension(
            v=np.array([bs.rft0 for bs in bss[gp_idxs == i]]),
            a=np.array([bs.area for bs in bss[gp_idxs == i]])
        )
        for i in np.unique(gp_idxs)
    ])

    RFA0s = np.array([
        get_area_weighted_averaged_values_one_dimension(
            v=np.array([bs.rfa0 for bs in bss[gp_idxs == i]]),
            a=np.array([bs.area for bs in bss[gp_idxs == i]])
        )
        for i in np.unique(gp_idxs)
    ])

    RFT1s = np.array([
        get_area_weighted_averaged_values_two_dimension(
            v=np.array([bs.rft1 for bs in bss[gp_idxs == i]]),
            a=np.array([bs.area for bs in bss[gp_idxs == i]])
        )
        for i in np.unique(gp_idxs)
    ])

    RFA1s = np.array([
        get_area_weighted_averaged_values_two_dimension(
            v=np.array([bs.rfa1 for bs in bss[gp_idxs == i]]),
            a=np.array([bs.area for bs in bss[gp_idxs == i]])
        )
        for i in np.unique(gp_idxs)
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
        NsurfG_i=NsurfG_i,
        q_trs_i_jstrs_ns=q_trs_sol_i_jstrs_ns
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



