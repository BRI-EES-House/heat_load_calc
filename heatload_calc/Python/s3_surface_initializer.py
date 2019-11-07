from collections import namedtuple
from typing import List

import numpy as np

import a11_opening_transmission_solar_radiation as a11
import a18_initial_value_constants as a18
import a19_external_surfaces as a19
import a23_surface_heat_transfer_coefficient as a23
import a25_window as a25
import a2_response_factor as a2
import a7_inclined_surface_solar_radiation as a7
import a8_shading as a8
import a9_rear_surface_equivalent_temperature as a9
import apdx10_oblique_incidence_characteristics as a10
import apdx6_direction_cos_incident_angle as a6
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


Initialized_Surface = namedtuple('Initialized_Surface', [
    'N_surf_i',
    'direction',
    'boundary_type',
    'is_sun_striked_outside',
    'is_solar_absorbed_inside',
    'a_i_k',
    'eps_i_k',
    'as_i_k',
    'A_i_k',
    'Rnext_i_k',
    'U',
    # ----- 以上はデータを参照用に保持 ----
    # ----- 以下は計算した結果の保存用 ----
    'QGT_i_k_n',
    'Teolist',
    'cos_Theta_i_k_n',
    'hi_i_k_n',
    'ho_i_k_n',
    'Cd_i_k',
    'RhoG_l',
    'w_alpha_i_k',
    'w_beta_i_k',
    'Wz_i_k',
    'Ww_i_k',
    'Ws_i_k',
    'PhiS_i_k',
    'PhiG_i_k',
    'Uso',
    'RFT0',
    'RFA0',
    'RFT1',
    'RFA1',
    'Row',
    'Nroot',
    'gpi'
])


def init_surface(
        boundaries: List[Boundary],
        I_DN_n: np.ndarray, I_sky_n: np.ndarray, RN_n: np.ndarray, To_n: np.ndarray,
        h_s_n: np.ndarray, a_s_n: np.ndarray) -> Initialized_Surface:

    gpi = a34.get_group_indices(boundaries)

    N_surf_i = len(boundaries)

    # 室iの境界kの名称 * k
    name_i_ks = np.array([b.name for b in boundaries])

    # 室iの境界kの種類 * k
    boundary_type_i_ks = np.array([b.boundary_type for b in boundaries])

    # 室iの境界kの面積, m2
    a_i_ks = np.array([b.area for b in boundaries])

    # 室iの境界kの日射の有無 * k
    is_sun_striked_outside_i_ks = np.array([b.is_sun_striked_outside for b in boundaries])

    # 室iの境界kの温度差係数 * k
    h_i_ks = np.array([b.temp_dif_coef for b in boundaries])

    # 室iの境界kの方位 * k
    direction_i_ks = np.array([b.direction for b in boundaries])

    # 室iの境界kの隣室タイプ * k
    next_room_type_i_ks = np.array([b.next_room_type for b in boundaries])

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

    # 室iの境界kの室外側長波長放射率
    # 間仕切り・地盤では定義されない。
    def get_epsilon_o_i_ks(b):
        if type(b.spec) is InternalPartSpec:
            return None  # 本計算では室内側の長波長放射率の値は固定値で実施しているため、間仕切りの場合は定義しない。
        elif type(b.spec) is GeneralPartSpec:
            return b.spec.outside_emissivity
        elif type(b.spec) is TransparentOpeningPartSpec:
            return b.spec.outside_emissivity
        elif type(b.spec) is OpaqueOpeningPartSpec:
            return b.spec.outside_emissivity
        elif type(b.spec) is GroundSpec:
            return None   # 地盤の場合は逆側が年間一定温度とする温度境界のため熱伝達抵抗の定義がない。
        else:
            raise TypeError

    epsilon_o_i_ks = np.array([get_epsilon_o_i_ks(b) for b in boundaries])

    # 室iの境界kの室外側日射吸収率
    # 一般部位・不透明な開口部で定義される。
    # 間仕切り・地盤では定義されない。
    # 透明な開口部も吸収および再放熱と透過成分のどちらも考慮した日射吸収率として定義される。
    def get_a_sun_i_ks(b):
        if type(b.spec) is InternalPartSpec:
            return None  # 間仕切りの場合は定義しない。
        elif type(b.spec) is GeneralPartSpec:
            return b.spec.outside_solar_absorption
        elif type(b.spec) is TransparentOpeningPartSpec:
            return None  # 日射熱取得率の中に含まれるため定義しない。
        elif type(b.spec) is OpaqueOpeningPartSpec:
            return b.spec.outside_solar_absorption
        elif type(b.spec) is GroundSpec:
            return None  # 地盤の場合は定義しない。
        else:
            raise TypeError

    a_sun_i_ks = np.array([get_a_sun_i_ks(b) for b in boundaries])

    # 室iの境界kの日射熱取得率
    # 透明な開口部のみで定義される。
    def get_eta_w_i_ks(b):
        if type(b.spec) is InternalPartSpec:
            return None
        elif type(b.spec) is GeneralPartSpec:
            return None
        elif type(b.spec) is TransparentOpeningPartSpec:
            return b.spec.eta_value
        elif type(b.spec) is OpaqueOpeningPartSpec:
            return None
        elif type(b.spec) is GroundSpec:
            return None
        else:
            raise TypeError

    eta_w_i_k = np.array([get_eta_w_i_ks(b) for b in boundaries])

    # 室iの境界kのガラスの入射角特性タイプ
    # 透明な開口部のみで定義される。
    def get_incident_angle_characteristics_i_ks(b):
        if type(b.spec) is InternalPartSpec:
            return None
        elif type(b.spec) is GeneralPartSpec:
            return None
        elif type(b.spec) is TransparentOpeningPartSpec:
            return b.spec.incident_angle_characteristics
        elif type(b.spec) is OpaqueOpeningPartSpec:
            return None
        elif type(b.spec) is GroundSpec:
            return None
        else:
            raise TypeError

    incident_angle_characteristics_i_ks = np.array([get_incident_angle_characteristics_i_ks(b) for b in boundaries])

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

    sin_a_s = np.where(h_s_n > 0.0, np.sin(a_s_n), 0.0)
    cos_a_s = np.where(h_s_n > 0.0, np.cos(a_s_n), 0.0)

    Sh_n = np.where(h_s_n > 0.0, np.sin(h_s_n), 0.0)
    cos_h_s = np.where(h_s_n > 0.0, np.cos(h_s_n), 1.0)

    # ========== 初期計算 ==========

    # 以下、計算結果格納用

    QGT_i_k_n = np.zeros((N_surf_i, 24 * 365 * 4))
    Teolist = np.zeros((N_surf_i, 24 * 365 * 4))
    cos_Theta_i_k_n = np.zeros((N_surf_i, 24 * 365 * 4))
    hi_i_k_n = np.zeros((N_surf_i, 24 * 365 * 4))
    ho_i_k_n = np.zeros((N_surf_i, 24 * 365 * 4))
    Cd_i_k = np.zeros(N_surf_i)

    RhoG_l = np.zeros(N_surf_i)
    w_alpha_i_k = np.zeros(N_surf_i)
    w_beta_i_k = np.zeros(N_surf_i)
    Wz_i_k = np.zeros(N_surf_i)
    Ww_i_k = np.zeros(N_surf_i)
    Ws_i_k = np.zeros(N_surf_i)
    PhiS_i_k = np.zeros(N_surf_i)
    PhiG_i_k = np.zeros(N_surf_i)
    Uso = np.zeros(N_surf_i)

    # 応答係数
    # ※応答係数の次数は最大12として確保しておく
    RFT0, RFA0, RFT1, RFA1, Row, Nroot = \
        np.zeros(N_surf_i), np.zeros(N_surf_i), np.zeros((N_surf_i, 12)), np.zeros(
            (N_surf_i, 12)), \
        np.zeros((N_surf_i, 12)), np.zeros(N_surf_i, dtype=np.int64)

    def get_bi(b):
        return np.array(b)[np.newaxis, :]

    # *********** 外壁傾斜面の計算 ***********

    f = (boundary_type_i_ks == "external_general_part") \
        | (boundary_type_i_ks == "external_transparent_part") \
        | (boundary_type_i_ks == "external_opaque_part")

    # 方位角、傾斜面方位角 [rad]
    w_alpha_i_k[f], w_beta_i_k[f] = a19.get_slope_angle(direction_i_ks[f])

    # 傾斜面に関する変数であり、式(73)
    Wz_i_k[f], Ww_i_k[f], Ws_i_k[f] = \
        a19.get_slope_angle_intermediate_variables(w_alpha_i_k[f], w_beta_i_k[f])

    # 傾斜面の天空に対する形態係数の計算 式(120)
    PhiS_i_k[f] = a19.get_Phi_S_i_k(Wz_i_k[f])

    # 傾斜面の地面に対する形態係数 式(119)
    PhiG_i_k[f] = a19.get_Phi_G_i_k(PhiS_i_k[f])

    # 地面反射率[-]
    RhoG_l[f] = a18.get_RhoG()

    # 拡散日射の入射角特性
    Cd_i_k = a10.get_Cd(incident_angle_characteristics_i_ks)

    # 室外側表面総合熱伝達率 [W/m2K] 式(121)
    ho_i_k_n = np.array([a23.get_ho_i_k_n(r_o_i_k) if r_o_i_k is not None else None for r_o_i_k in r_o_i_ks])

    # 室内側表面総合熱伝達率 [W/m2K] 式(122)
    hi_i_k_n = a23.get_hi_i_k_n(r_i_i_ks)

    # 開口部の室内表面から屋外までの熱貫流率[W / (m2･K)] 式(124)
    f = np.logical_not((boundary_type_i_ks == "external_general_part")
                       | (boundary_type_i_ks == "internal")
                       | (boundary_type_i_ks == "ground"))

    Uso[f] = a25.get_Uso(u_i_ks[f], r_i_i_ks[f])

    # ********** 応答係数 **********

    # 1) 非一般部位
    f = np.logical_not((boundary_type_i_ks == "external_general_part")
                       | (boundary_type_i_ks == "internal")
                       | (boundary_type_i_ks == "ground"))

    RFT0[f], RFA0[f], RFT1[f], RFA1[f], Row[f], Nroot[f] = \
        1.0, 1.0 / Uso[f], np.zeros(12), np.zeros(12), np.zeros(12), 0

    # 2) 一般部位
    for k in range(N_surf_i):
        if boundary_type_i_ks[k] in ["external_general_part", "internal", "ground"]:
            is_ground = boundary_type_i_ks[k] == "ground"

            # 応答係数
            RFT0[k], RFA0[k], RFT1[k], RFA1[k], Row[k], Nroot[k] = \
                a2.calc_response_factor(is_ground, c_layer_i_k_ls[k], r_layer_i_k_ls[k])

    # ********** 入射角の方向余弦および傾斜面日射量の計算(外壁のみ) **********

    # 入射角の方向余弦
    f = (boundary_type_i_ks == "external_general_part") \
        | (boundary_type_i_ks == "external_transparent_part") \
        | (boundary_type_i_ks == "external_opaque_part")

##########################################################################
    cos_Theta_i_k_n[f] = a6.calc_cos_incident_angle(
        h_sun_sin_n=Sh_n,
        h_sun_cos_n=cos_h_s,
        a_sun_sin_n=sin_a_s,
        a_sun_cos_n=cos_a_s,
        w_alpha_k=w_alpha_i_k[f],
        w_beta_k=w_beta_i_k[f]
    )

    # 傾斜面日射量
    f = (boundary_type_i_ks == "external_general_part") \
        | (boundary_type_i_ks == "external_transparent_part") \
        | (boundary_type_i_ks == "external_opaque_part")

    Iw_i_k_n = np.zeros((N_surf_i, 24 * 365 * 4))
    I_D_i_k_n = np.zeros((N_surf_i, 24 * 365 * 4))
    I_S_i_k_n = np.zeros((N_surf_i, 24 * 365 * 4))
    I_R_i_k_n = np.zeros((N_surf_i, 24 * 365 * 4))

#####################################################################
    Iw_i_k_n[f], I_D_i_k_n[f], I_S_i_k_n[f], I_R_i_k_n[f] = a7.calc_slope_sol(
        I_DN_n=I_DN_n,
        I_sky_n=I_sky_n,
        Sh_n=Sh_n,
        cos_Theta_i_k_n=cos_Theta_i_k_n[f],
        PhiS_i_k=PhiS_i_k[f],
        PhiG_i_k=PhiG_i_k[f],
        RhoG_l=RhoG_l[f]
    )

    # ********** 傾斜面の相当外気温度の計算 **********

    # 1) 日射が当たる場合
    f_sun = get_bi(np.array([d if d is not None else False for d in is_sun_striked_outside_i_ks]))

    # 1-1) 一般部位、不透明な開口部の場合
    f = tuple(f_sun &
              ((boundary_type_i_ks == "external_general_part") | (boundary_type_i_ks == "external_opaque_part")))

    Teolist[f] = a9.get_Te_n_1(
        To_n=To_n,
        as_i_k=a_sun_i_ks[f],
        I_w_i_k_n=Iw_i_k_n[f],
        eps_i_k=epsilon_o_i_ks[f],
        PhiS_i_k=PhiS_i_k[f],
        RN_n=RN_n,
        ho_i_k_n=ho_i_k_n[f]
    )

    # 1-2) 透明開口部の場合
    f = tuple(f_sun & (boundary_type_i_ks == "external_transparent_part"))

    Teolist[f] = a9.get_Te_n_2(
        To_n=To_n,
        eps_i_k=epsilon_o_i_ks[f],
        PhiS_i_k=PhiS_i_k[f],
        RN_n=RN_n,
        ho_i_k_n=ho_i_k_n[f]
    )

    # 2) 日射が当たらない場合

    # 2-1) 地面の場合は、年平均気温とする
    f = tuple((f_sun == False) & (boundary_type_i_ks == "ground"))
    Teolist[f] = np.full(24 * 365 * 4, np.average(To_n))

    # 2-2) 日の当たらない一般部位と内壁
    f = tuple(
        (f_sun == False) & ((boundary_type_i_ks == "external_general_part") | (boundary_type_i_ks == "internal")))
    Teolist[f] = np.zeros(24 * 365 * 4)

    # ********** 日除けの日影面積率の計算 **********

    # 外表面に日射が当たる場合
    FSDW_i_k_n = np.zeros((N_surf_i, 24 * 365 * 4))

    for k in range(N_surf_i):

        if is_sun_striked_outside_i_ks[k]:

            # 透明開口部の場合
            if boundary_type_i_ks[k] == "external_transparent_part":
                # 日除けの日影面積率の計算
                if solar_shading_part_i_ks[k].existence:
                    if solar_shading_part_i_ks[k].input_method == 'simple':
###################################################################################
                        h_s = np.where(h_s_n > 0.0, h_s_n, 0.0)
                        a_s = np.where(h_s_n > 0.0, a_s_n, 0.0)

                        FSDW_i_k_n[k] = a8.calc_F_SDW_i_k_n(
                            D_i_k=solar_shading_part_i_ks[k].depth,  # 出幅
                            d_e=solar_shading_part_i_ks[k].d_e,  # 窓の上端から庇までの距離
                            d_h=solar_shading_part_i_ks[k].d_h,  # 窓の高さ
                            a_s_n=a_s,
                            h_s_n=h_s,
                            Wa_i_k=w_alpha_i_k[k]
                        )
                    elif solar_shading_part_i_ks[k].input_method == 'detailed':
                        raise NotImplementedError()
                    else:
                        raise ValueError

    # ********** 透過日射熱取得の計算 **********

    f = tuple(f_sun & (boundary_type_i_ks == "external_transparent_part"))

    QGT_i_k_n[f] = a11.calc_QGT_i_k_n(
        cos_Theta_i_k_n=cos_Theta_i_k_n[f],
        IAC_i_k=incident_angle_characteristics_i_ks[f],
        I_D_i_k_n=I_D_i_k_n[f],
        FSDW_i_k_n=FSDW_i_k_n[f],
        I_S_i_k_n=I_S_i_k_n[f],
        I_R_i_k_n=I_R_i_k_n[f],
        A_i_k=a_i_ks[f],
        tau_i_k=eta_w_i_k[f],
        Cd_i_k=Cd_i_k[f]
    )

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

    return Initialized_Surface(
        N_surf_i=N_surf_i,
        direction=direction_i_ks,
        boundary_type=boundary_type_i_ks,
        is_sun_striked_outside=is_sun_striked_outside_i_ks,
        is_solar_absorbed_inside=is_solar_absorbed_inside_i_ks,
        a_i_k=h_i_ks,
        eps_i_k=epsilon_o_i_ks,
        as_i_k=a_sun_i_ks,
        A_i_k=a_i_ks,
        Rnext_i_k=np.vectorize(convert_from_next_room_name_to_id)(next_room_type_i_ks),
#        Rnext_i_k=next_room_type_i_ks,
        U=u_i_ks,
        QGT_i_k_n=QGT_i_k_n,
        Teolist=Teolist,
        cos_Theta_i_k_n=cos_Theta_i_k_n,
        hi_i_k_n=hi_i_k_n,
        ho_i_k_n=ho_i_k_n,
        Cd_i_k=Cd_i_k,
        RhoG_l=RhoG_l,
        w_alpha_i_k=w_alpha_i_k,
        w_beta_i_k=w_beta_i_k,
        Wz_i_k=Wz_i_k,
        Ww_i_k=Ww_i_k,
        Ws_i_k=Ws_i_k,
        PhiS_i_k=PhiS_i_k,
        PhiG_i_k=PhiG_i_k,
        Uso=Uso,
        RFT0=RFT0,
        RFA0=RFA0,
        RFT1=RFT1,
        RFA1=RFA1,
        Row=Row,
        Nroot=Nroot,
        gpi=gpi
    )
