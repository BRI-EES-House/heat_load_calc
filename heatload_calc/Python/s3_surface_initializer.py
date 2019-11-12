from collections import namedtuple
from typing import List
import numpy as np

import x_07_inclined_surface_solar_radiation as x_07
import x_19_external_boundaries_direction as x_19

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


Initialized_Surface = namedtuple('Initialized_Surface', [
    'N_surf_i',
    'boundary_type',
    'is_sun_striked_outside',
    'is_solar_absorbed_inside',
    'a_i_k',
    'A_i_k',
    'Rnext_i_k',
    'U',
    # ----- 以上はデータを参照用に保持 ----
    # ----- 以下は計算した結果の保存用 ----
    'Teolist',
    'hi_i_k_n',
    'ho_i_k_n',
    'RFT0',
    'RFA0',
    'RFT1',
    'RFA1',
    'Row',
    'Nroot',
    'gp_idx',
    'ib'
])


IntegratedBoundaries = namedtuple('IntegratedBoundaries', [
    'name_i_iks',
    'sub_name_i_iks',
    'boundary_type_i_iks',
    'a_i_iks',
    'is_sun_striked_outside_i_iks',
    'h_i_iks',
    'next_room_type_i_iks',
    'is_solar_absorbed_inside_i_ks',
    'h_i_i_iks',
    't_e_o_group'
])


def init_surface(
        boundaries: List[Boundary],
        i_dn_ns: np.ndarray, i_sky_ns: np.ndarray, r_n_ns: np.ndarray, theta_o_ns: np.ndarray,
        h_sun_ns: np.ndarray, a_sun_ns: np.ndarray) -> Initialized_Surface:

    # 集約化可能な境界には同じIDを振り、境界ごとにそのIDを取得する。
    # boundaries の数のIDを持つndarray
    # 例
    # [ 0  1  2  3  4  5  0  1  4  5  6  7  8  0  1  4  5  6  9  0  1  2 10  4  5 11]
    gp_idxs = a34.get_group_indices(boundaries)

    # 先頭のインデックスのリスト
    first_idx = np.array([np.where(gp_idxs == k)[0][0] for k in np.unique(gp_idxs)], dtype=np.int)

    # 室iの境界kの名前
    name_i_ks = np.array([b.name for b in boundaries])

    # 室iの境界kの種類 * k
    boundary_type_i_ks = np.array([b.boundary_type for b in boundaries])

    # 室iの境界kの面積, m2
    a_i_ks = np.array([b.area for b in boundaries])

    # 室iの境界kの日射の有無 * k
    is_sun_striked_outside_i_ks = np.array([b.is_sun_striked_outside for b in boundaries])

    # 室iの境界kの温度差係数 * k
    h_i_ks = np.array([b.temp_dif_coef for b in boundaries])

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

    # 室iの境界kの隣室タイプ * k
    next_room_type_i_ks = np.array([b.next_room_type for b in boundaries])
    next_room_type_i_ks = np.vectorize(convert_from_next_room_name_to_id)(next_room_type_i_ks)

    # 室iの境界kの床室内侵入日射吸収の有無 * k
    is_solar_absorbed_inside_i_ks = np.array([b.is_solar_absorbed_inside for b in boundaries])

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

    # 室iの境界kの室外側熱伝達抵抗, m2K/W
    # 地盤以外（間仕切り・外皮_一般部位・外皮_透明な開口部・外皮_不透明な開口部）で定義される。
    def get_r_o_i_ks(b):
        if type(b.spec) is InternalPartSpec:
            return b.spec.outside_heat_transfer_resistance
        elif type(b.spec) is GeneralPartSpec:
            return b.spec.outside_heat_transfer_resistance
        elif type(b.spec) is TransparentOpeningPartSpec:
            return b.spec.outside_heat_transfer_resistance
        elif type(b.spec) is OpaqueOpeningPartSpec:
            return b.spec.outside_heat_transfer_resistance
        elif type(b.spec) is GroundSpec:
            return None   # 地盤の場合は逆側が年間一定温度とする温度境界のため熱伝達抵抗の定義がない。
        else:
            raise TypeError

    r_o_i_ks = np.array([get_r_o_i_ks(b) for b in boundaries])

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


    # 室内側表面総合熱伝達率 [W/m2K] 式(122)
    h_i_i_ks = a23.get_h_i_i_ks(r_i_i_ks)

###########################################################################

    itg_bs = []

    for i in np.unique(gp_idxs):
        r_i_i_iks = r_i_i_ks[first_idx[i]]
        r_o_i_iks = r_o_i_ks[first_idx[i]]
        h_i_i_ik = h_i_i_ks[first_idx[i]]
        itg_bs.append(IntegratedBoundaries(
            name_i_iks='integrated_boundary' + str(i),
            sub_name_i_iks='+'.join(name_i_ks[gp_idxs == i]),
            boundary_type_i_iks=boundary_type_i_ks[first_idx[i]],
            a_i_iks=sum(a_i_ks[gp_idxs == i]),
            is_sun_striked_outside_i_iks=is_sun_striked_outside_i_ks[first_idx[i]],
            h_i_iks=h_i_ks[first_idx[i]],
            next_room_type_i_iks=next_room_type_i_ks[first_idx[i]],
            is_solar_absorbed_inside_i_ks=is_solar_absorbed_inside_i_ks[first_idx[i]],
            h_i_i_iks=h_i_i_ik,
            t_e_o_group=None
        ))

    # 室iの統合された境界ikの名称
    itg_name_i_iks = [itg_b.name_i_iks for itg_b in itg_bs]

    # 室iの統合された境界ikの副名称（統合する前の境界の名前を'+'記号でつなげたもの）
    itg_sub_name_i_iks = [itg_b.sub_name_i_iks for itg_b in itg_bs]

    # 室iの統合された境界ikの種類
    itg_boundary_type_i_iks = [itg_b.boundary_type_i_iks for itg_b in itg_bs]

    # 室iの統合された境界ikの面積
    itg_a_i_iks = np.array([itg_b.a_i_iks for itg_b in itg_bs])

    # 室iの統合された境界ikの日射の有無
    itg_is_sun_striked_outside_i_iks = np.array([itg_b.is_sun_striked_outside_i_iks for itg_b in itg_bs])

    # 室iの統合された境界ikの温度差係数
    itg_h_i_iks = np.array([itg_b.h_i_iks for itg_b in itg_bs])

    # 室iの境界kの隣室タイプ * k
    itg_next_room_type_i_iks = np.array([itg_b.next_room_type_i_iks for itg_b in itg_bs])

    # 室iの境界kの床室内侵入日射吸収の有無 * k
    itg_is_solar_absorbed_inside_i_ks = np.array([itg_b.is_solar_absorbed_inside_i_ks for itg_b in itg_bs])

    h_i_i_iks = np.array([itg_b.h_i_i_iks for itg_b in itg_bs])







    # ========== 初期計算 ==========

    # 以下、計算結果格納用

    N_surf_i = len(boundaries)

    Uso = np.zeros(N_surf_i)

    # 応答係数
    # ※応答係数の次数は最大12として確保しておく
    RFT0, RFA0, RFT1, RFA1, Row, Nroot = \
        np.zeros(N_surf_i), np.zeros(N_surf_i), np.zeros((N_surf_i, 12)), np.zeros(
            (N_surf_i, 12)), \
        np.zeros((N_surf_i, 12)), np.zeros(N_surf_i, dtype=np.int64)

    # 室外側表面総合熱伝達率 [W/m2K] 式(121)
    ho_i_k_n = np.array([a23.get_ho_i_k_n(r_o_i_k) if r_o_i_k is not None else None for r_o_i_k in r_o_i_ks])

    # ********** 応答係数 **********

    # 1) 非一般部位
    f = np.logical_not((boundary_type_i_ks == "external_general_part")
                       | (boundary_type_i_ks == "internal")
                       | (boundary_type_i_ks == "ground"))

    # 開口部の室内表面から屋外までの熱貫流率[W / (m2･K)] 式(124)
    Uso[f] = a25.get_Uso(u_i_ks[f], r_i_i_ks[f])

    RFT0[f], RFA0[f], RFT1[f], RFA1[f], Row[f], Nroot[f] = \
        1.0, 1.0 / Uso[f], np.zeros(12), np.zeros(12), np.zeros(12), 0

    # 2) 一般部位
    for k in range(N_surf_i):
        if boundary_type_i_ks[k] in ["external_general_part", "internal", "ground"]:
            is_ground = boundary_type_i_ks[k] == "ground"

            # 応答係数
            RFT0[k], RFA0[k], RFT1[k], RFA1[k], Row[k], Nroot[k] = \
                a2.calc_response_factor(is_ground, c_layer_i_k_ls[k], r_layer_i_k_ls[k])

    # 傾斜面の相当外気温度の計算
    Teolist = np.array([
        get_eot(boundary=b, theta_o_ns=theta_o_ns, i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, r_n_ns=r_n_ns, a_sun_ns=a_sun_ns,
                h_sun_ns=h_sun_ns)
        for b in boundaries])

    t_e_o_group = get_grouped_t_e_o(Teolist, a_i_ks, gp_idxs)

    ib = IntegratedBoundaries(
        name_i_iks=itg_name_i_iks,
        sub_name_i_iks=itg_sub_name_i_iks,
        boundary_type_i_iks=itg_boundary_type_i_iks,
        a_i_iks=itg_a_i_iks,
        is_sun_striked_outside_i_iks=itg_is_sun_striked_outside_i_iks,
        h_i_iks=itg_h_i_iks,
        next_room_type_i_iks=itg_next_room_type_i_iks,
        is_solar_absorbed_inside_i_ks=itg_is_solar_absorbed_inside_i_ks,
        h_i_i_iks=h_i_i_iks,
        t_e_o_group=t_e_o_group
    )

    return Initialized_Surface(
        N_surf_i=N_surf_i,
        boundary_type=boundary_type_i_ks,
        is_sun_striked_outside=is_sun_striked_outside_i_ks,
        is_solar_absorbed_inside=is_solar_absorbed_inside_i_ks,
        a_i_k=h_i_ks,
        A_i_k=a_i_ks,
#        Rnext_i_k=np.vectorize(convert_from_next_room_name_to_id)(next_room_type_i_ks),
        Rnext_i_k=next_room_type_i_ks,
        U=u_i_ks,
        Teolist=Teolist,
        hi_i_k_n=h_i_i_ks,
        ho_i_k_n=ho_i_k_n,
        RFT0=RFT0,
        RFA0=RFA0,
        RFT1=RFT1,
        RFA1=RFA1,
        Row=Row,
        Nroot=Nroot,
        gp_idx=gp_idxs,
        ib=ib
    )


def get_grouped_t_e_o(Teolist, a_i_ks, gp_idxs):
    t_e_o_group = []
    for i in np.unique(gp_idxs):
        t = Teolist[gp_idxs == i]
        r = (a_i_ks[gp_idxs == i] / np.sum(a_i_ks[gp_idxs == i])).reshape(-1, 1)
        result = np.sum(t * r, axis=0)

        t_e_o_group.append(result)

    return np.array(t_e_o_group)


def get_eot(boundary, theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, a_sun_ns, h_sun_ns):

    # 間仕切りの場合
    if boundary.boundary_type == 'internal':

        # この値は使用しないのでNoneでもよいはず
        # 集約化する際にNoneだと変な挙動を示すかも知れないのでとりあえずゼロにしておく。
        return np.zeros(24 * 365 * 4)

    # 外壁・不透明な開口部の場合
    elif (boundary.boundary_type == 'external_general_part') or (boundary.boundary_type == 'external_opaque_part'):

        # 日射が当たる場合
        if boundary.is_sun_striked_outside:

            # 室iの境界jの傾斜面の方位角, rad
            # 室iの境界jの傾斜面の傾斜角, rad
            w_alpha_i_j, w_beta_i_j = x_19.get_w_alpha_i_j_w_beta_i_j(direction_i_j=boundary.direction)

            # ステップnにおける室iの境界kにおける傾斜面の日射量のうち直達成分, W / m2K
            # ステップnにおける室iの境界kにおける傾斜面の日射量のうち天空成分, W / m2K
            # ステップnにおける室iの境界kにおける傾斜面の日射量のうち地盤反射成分, W / m2K
            i_inc_d, i_inc_sky, i_inc_ref = x_07.get_i_is_i_j_n(
                i_dn_ns=i_dn_ns,
                i_sky_ns=i_sky_ns,
                h_sun_ns=h_sun_ns,
                a_sun_ns=a_sun_ns,
                w_alpha_i_j=w_alpha_i_j,
                w_beta_i_j=w_beta_i_j
            )
            r_n_is_i_j_n = x_07.get_r_n_is_i_j_n(r_n_ns=r_n_ns, w_beta_i_j=w_beta_i_j)

            T = a9.get_Te_n_1(
                To_n=theta_o_ns,
                as_i_k=boundary.spec.outside_solar_absorption,
                eps_i_k=boundary.spec.outside_emissivity,
                ho_i_k_n=a23.get_ho_i_k_n(boundary.spec.outside_heat_transfer_resistance),
                i_inc_d=i_inc_d,
                i_inc_sky=i_inc_sky,
                i_inc_ref=i_inc_ref,
                r_n_is_i_j_n=r_n_is_i_j_n
            )

            return T

        # 日射が当たらない場合
        else:

            return np.zeros(24 * 365 * 4)

    # 透明な開口部の場合
    elif boundary.boundary_type == 'external_transparent_part':

        if boundary.is_sun_striked_outside:
            # 室iの境界kの傾斜面の方位角, rad
            # 室iの境界kの傾斜面の傾斜角, rad
            w_alpha_i_j, w_beta_i_j = x_19.get_w_alpha_i_j_w_beta_i_j(direction_i_j=boundary.direction)

            r_n_is_i_j_n = x_07.get_r_n_is_i_j_n(r_n_ns=r_n_ns, w_beta_i_j=w_beta_i_j)

            T = a9.get_Te_n_2(
                To_n=theta_o_ns,
                eps_i_k=boundary.spec.outside_emissivity,
                ho_i_k_n=a23.get_ho_i_k_n(boundary.spec.outside_heat_transfer_resistance),
                r_n_is_i_j_n=r_n_is_i_j_n
            )

            return T

        else:

            # もともとこのケースは考えられていなかった。
            # とりあえず、ゼロにするが、概念的には、外気温の方が正しいと思う。
            return np.zeros(24 * 365 * 4)

    elif boundary.boundary_type == 'ground':

        return np.full(24 * 365 * 4, np.average(theta_o_ns))

    else:

        raise ValueError()


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



