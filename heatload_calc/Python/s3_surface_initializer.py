from collections import namedtuple
from typing import List

import numpy as np

import a11_opening_transmission_solar_radiation as a11
import a18_initial_value_constants as a18
import x_19_external_boundaries_direction as a19
import a23_surface_heat_transfer_coefficient as a23
import a25_window as a25
import a2_response_factor as a2
import a7_inclined_surface_solar_radiation as a7
import a8_shading as a8
import a9_rear_surface_equivalent_temperature as a9
import apdx10_oblique_incidence_characteristics as a10
from s3_surface_loader import Boundary
from s3_surface_loader import InternalPartSpec
from s3_surface_loader import InternalPartSpecLayers
from s3_surface_loader import GeneralPartSpec
from s3_surface_loader import GeneralPartSpecLayers
from s3_surface_loader import TransparentOpeningPartSpec
from s3_surface_loader import OpaqueOpeningPartSpec
from s3_surface_loader import GroundSpec
from s3_surface_loader import GroundSpecLayers
from s3_surface_loader import SolarShadingPart
import a34_building_part_summarize as a34

from x_19_external_boundaries_direction import get_w_alpha_i_k_w_beta_i_k as x_19_get_w_alpha_i_k_w_beta_i_k


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
    'h_i_i_iks'
])

def init_surface(
        boundaries: List[Boundary],
        I_DN_n: np.ndarray, I_sky_n: np.ndarray, RN_n: np.ndarray, To_n: np.ndarray,
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
            h_i_i_iks=h_i_i_ik
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

    ib = IntegratedBoundaries(
        name_i_iks=itg_name_i_iks,
        sub_name_i_iks=itg_sub_name_i_iks,
        boundary_type_i_iks=itg_boundary_type_i_iks,
        a_i_iks=itg_a_i_iks,
        is_sun_striked_outside_i_iks=itg_is_sun_striked_outside_i_iks,
        h_i_iks=itg_h_i_iks,
        next_room_type_i_iks=itg_next_room_type_i_iks,
        is_solar_absorbed_inside_i_ks=itg_is_solar_absorbed_inside_i_ks,
        h_i_i_iks=h_i_i_iks
    )






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

    def get_bi(b):
        return np.array(b)[np.newaxis, :]

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

    # *********** 外壁傾斜面の計算 ***********

    f_sun = get_bi(np.array([d if d is not None else False for d in is_sun_striked_outside_i_ks]))

    # 1-1) 一般部位、不透明な開口部の場合
    f = tuple(f_sun &
              ((boundary_type_i_ks == "external_general_part")
               | (boundary_type_i_ks == "external_transparent_part")
               | (boundary_type_i_ks == "external_opaque_part"))
              )

    f_sky_i_k = np.zeros(N_surf_i)
    i_inc_i_k_n_all = np.zeros((N_surf_i, 24 * 365 * 4))

    f_skys = []
    i_inc_i_k_n_alls =[]

    for b in boundaries:

        if (b.boundary_type == 'external_general_part') \
            or (b.boundary_type == 'external_transparent_part') \
                or (b.boundary_type == 'external_opaque_part'):

            if b.is_sun_striked_outside:

                # 室iの境界kの傾斜面の方位角, rad
                # 室iの境界kの傾斜面の傾斜角, rad
                w_alpha, w_beta = x_19_get_w_alpha_i_k_w_beta_i_k(b.direction)

                # ステップnの室iの境界kにおける傾斜面に入射する太陽の入射角* 365 * 24 * 4
                theta_aoi = a7.get_cos_theta_aoi_i_k_n(w_alpha, w_beta, h_sun_ns, a_sun_ns)

                # 室iの境界kの傾斜面の天空に対する形態係数
                f_sky = a7.get_f_sky_i_k(w_beta)

                # 室iの境界kの傾斜面の地面に対する形態係数
                f_gnd = a7.get_f_gnd_i_k(f_sky)

                # 地面の日射に対する反射率（アルベド）
                rho_gnd = a7.get_rho_gnd()

                # ステップnにおける室iの境界kにおける傾斜面の日射量, W / m2K
                # ステップnにおける室iの境界kにおける傾斜面の日射量のうち直達成分, W / m2K
                # ステップnにおける室iの境界kにおける傾斜面の日射量のうち天空成分, W / m2K
                # ステップnにおける室iの境界kにおける傾斜面の日射量のうち地盤反射成分, W / m2K
                i_inc_all, i_inc_d, i_inc_sky, i_inc_ref = a7.get_i_inc_i_k_n(
                    i_dn_ns=I_DN_n,
                    i_sky_ns=I_sky_n,
                    theta_aoi_i_k_n=theta_aoi,
                    f_sky_i_k=f_sky,
                    f_gnd_i_k=f_gnd,
                    rho_gnd_i_k=rho_gnd,
                    h_sun_ns=h_sun_ns
                )

                f_skys.append(f_sky)
                i_inc_i_k_n_alls.append(i_inc_all)


    f_sky_i_k[f] = f_skys
    i_inc_i_k_n_all[f] = i_inc_i_k_n_alls

    # ********** 傾斜面の相当外気温度の計算 **********

    Ts = []

    for i, b in enumerate(boundaries):

        if b.boundary_type == 'internal':
            T = np.zeros(24 * 365 * 4)
            Ts.append(T)

        elif (b.boundary_type == 'external_general_part') or (b.boundary_type == 'external_opaque_part'):

            if b.is_sun_striked_outside:

                T = a9.get_Te_n_1(
                    To_n=To_n,
                    as_i_k=b.spec.outside_solar_absorption,
                    I_w_i_k_n=i_inc_i_k_n_all[i],
                    eps_i_k=b.spec.outside_emissivity,
                    PhiS_i_k=f_sky_i_k[i],
                    RN_n=RN_n,
                    ho_i_k_n=a23.get_ho_i_k_n(b.spec.outside_heat_transfer_resistance)
                )
                Ts.append(T)

            else:

                T = np.zeros(24 * 365 * 4)
                Ts.append(T)

        elif b.boundary_type == 'external_transparent_part':

            T = a9.get_Te_n_2(
                To_n=To_n,
                eps_i_k=b.spec.outside_emissivity,
                PhiS_i_k=f_sky_i_k[i],
                RN_n=RN_n,
                ho_i_k_n=a23.get_ho_i_k_n(b.spec.outside_heat_transfer_resistance)
            )

            Ts.append(T)

        elif b.boundary_type == 'ground':
            T = np.full(24 * 365 * 4, np.average(To_n))
            Ts.append(T)

        else:
            raise ValueError()

    Teolist = Ts

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


def is_solar_radiation_transmitted(boundary: Boundary):

    if boundary.boundary_type == 'external_transparent_part':

        if boundary.is_sun_striked_outside:

            return True

        else:

            return False
    else:

        return False


def get_transmitted_solar_radiation(
        boundaries: List[Boundary], I_DN_n, I_sky_n, h_sun_ns, a_sun_ns):

    bs = [b for b in boundaries if is_solar_radiation_transmitted(b)]

    q = a11.test(boundaries=bs, I_DN_n=I_DN_n, I_sky_n=I_sky_n, h_sun_ns=h_sun_ns, a_sun_ns=a_sun_ns)

    return q



