from collections import namedtuple

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
from s3_surface_loader import DSurface

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
    'Nroot'
])


def init_surface(
        data: DSurface,
        I_DN_n: np.ndarray, I_sky_n: np.ndarray, RN_n: np.ndarray, To_n: np.ndarray,
        h_s_n: np.ndarray, a_s_n: np.ndarray) -> Initialized_Surface:

    sin_a_s = np.where(h_s_n > 0.0, np.sin(a_s_n), 0.0)
    cos_a_s = np.where(h_s_n > 0.0, np.cos(a_s_n), 0.0)

    Sh_n = np.where(h_s_n > 0.0, np.sin(h_s_n), 0.0)
    cos_h_s = np.where(h_s_n > 0.0, np.cos(h_s_n), 1.0)

    # ========== 初期計算 ==========

    # 以下、計算結果格納用

    QGT_i_k_n = np.zeros((data.N_surf_i, 24 * 365 * 4))
    Teolist = np.zeros((data.N_surf_i, 24 * 365 * 4))
    cos_Theta_i_k_n = np.zeros((data.N_surf_i, 24 * 365 * 4))
    hi_i_k_n = np.zeros((data.N_surf_i, 24 * 365 * 4))
    ho_i_k_n = np.zeros((data.N_surf_i, 24 * 365 * 4))
    Cd_i_k = np.zeros(data.N_surf_i)

    RhoG_l = np.zeros(data.N_surf_i)
    w_alpha_i_k = np.zeros(data.N_surf_i)
    w_beta_i_k = np.zeros(data.N_surf_i)
    Wz_i_k = np.zeros(data.N_surf_i)
    Ww_i_k = np.zeros(data.N_surf_i)
    Ws_i_k = np.zeros(data.N_surf_i)
    PhiS_i_k = np.zeros(data.N_surf_i)
    PhiG_i_k = np.zeros(data.N_surf_i)
    Uso = np.zeros(data.N_surf_i)

    # 応答係数
    # ※応答係数の次数は最大12として確保しておく
    RFT0, RFA0, RFT1, RFA1, Row, Nroot = \
        np.zeros(data.N_surf_i), np.zeros(data.N_surf_i), np.zeros((data.N_surf_i, 12)), np.zeros(
            (data.N_surf_i, 12)), \
        np.zeros((data.N_surf_i, 12)), np.zeros(data.N_surf_i, dtype=np.int64)

    def get_bi(b):
        return np.array(b)[np.newaxis, :]

    # *********** 外壁傾斜面の計算 ***********

    f = (data.boundary_type_i_ks == "external_general_part") \
        | (data.boundary_type_i_ks == "external_transparent_part") \
        | (data.boundary_type_i_ks == "external_opaque_part")

    # 方位角、傾斜面方位角 [rad]
    w_alpha_i_k[f], w_beta_i_k[f] = a19.get_slope_angle(data.direction_i_ks[f])

    # 傾斜面に関する変数であり、式(73)
    Wz_i_k[f], Ww_i_k[f], Ws_i_k[f] = \
        a19.get_slope_angle_intermediate_variables(w_alpha_i_k[f], w_beta_i_k[f])

    # 傾斜面の天空に対する形態係数の計算 式(120)
    PhiS_i_k[f] = a19.get_Phi_S_i_k(Wz_i_k[f])

    # 傾斜面の地面に対する形態係数 式(119)
    PhiG_i_k[f] = a19.get_Phi_G_i_k(PhiS_i_k[f])

    # 温度差係数
    # h_i_ks[f] = data.h_i_ks[f]

    # 地面反射率[-]
    RhoG_l[f] = a18.get_RhoG()

    # 拡散日射の入射角特性
    Cd_i_k = a10.get_Cd(data.IAC_i_k)

    # 室外側表面総合熱伝達率 [W/m2K] 式(121)
    ho_i_k_n = a23.get_ho_i_k_n(data.Ro_i_k_n)

    # 室内側表面総合熱伝達率 [W/m2K] 式(122)
    hi_i_k_n = a23.get_hi_i_k_n(data.Ri_i_k_n)

    # 開口部の室内表面から屋外までの熱貫流率[W / (m2･K)] 式(124)
    f = np.logical_not((data.boundary_type_i_ks == "external_general_part")
                       | (data.boundary_type_i_ks == "internal")
                       | (data.boundary_type_i_ks == "ground"))

    Uso[f] = a25.get_Uso(data.U[f], data.Ri_i_k_n[f])

    # ********** 応答係数 **********

    # 1) 非一般部位
    f = np.logical_not((data.boundary_type_i_ks == "external_general_part")
                       | (data.boundary_type_i_ks == "internal")
                       | (data.boundary_type_i_ks == "ground"))

    RFT0[f], RFA0[f], RFT1[f], RFA1[f], Row[f], Nroot[f] = \
        1.0, 1.0 / Uso[f], np.zeros(12), np.zeros(12), np.zeros(12), 0

    # 2) 一般部位
    for k in range(data.N_surf_i):
        if data.boundary_type_i_ks[k] in ["external_general_part", "internal", "ground"]:
            is_ground = data.boundary_type_i_ks[k] == "ground"

            # 応答係数
            RFT0[k], RFA0[k], RFT1[k], RFA1[k], Row[k], Nroot[k] = \
                a2.calc_response_factor(is_ground, data.C_i_k_p[k], data.R_i_k_p[k])

    # ********** 入射角の方向余弦および傾斜面日射量の計算(外壁のみ) **********

    # 入射角の方向余弦
    f = (data.boundary_type_i_ks == "external_general_part") \
        | (data.boundary_type_i_ks == "external_transparent_part") \
        | (data.boundary_type_i_ks == "external_opaque_part")

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
    f = (data.boundary_type_i_ks == "external_general_part") \
        | (data.boundary_type_i_ks == "external_transparent_part") \
        | (data.boundary_type_i_ks == "external_opaque_part")

    Iw_i_k_n = np.zeros((data.N_surf_i, 24 * 365 * 4))
    I_D_i_k_n = np.zeros((data.N_surf_i, 24 * 365 * 4))
    I_S_i_k_n = np.zeros((data.N_surf_i, 24 * 365 * 4))
    I_R_i_k_n = np.zeros((data.N_surf_i, 24 * 365 * 4))

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
    f_sun = get_bi(np.array([d if d is not None else False for d in data.is_sun_striked_outside_i_ks]))

    # 1-1) 一般部位、不透明な開口部の場合
    f = tuple(f_sun &
              ((data.boundary_type_i_ks == "external_general_part") | (data.boundary_type_i_ks == "external_opaque_part")))

    Teolist[f] = a9.get_Te_n_1(
        To_n=To_n,
        as_i_k=data.as_i_k[f],
        I_w_i_k_n=Iw_i_k_n[f],
        eps_i_k=data.eps_i_k[f],
        PhiS_i_k=PhiS_i_k[f],
        RN_n=RN_n,
        ho_i_k_n=ho_i_k_n[f]
    )

    # 1-2) 透明開口部の場合
    f = tuple(f_sun & (data.boundary_type_i_ks == "external_transparent_part"))

    Teolist[f] = a9.get_Te_n_2(
        To_n=To_n,
        eps_i_k=data.eps_i_k[f],
        PhiS_i_k=PhiS_i_k[f],
        RN_n=RN_n,
        ho_i_k_n=ho_i_k_n[f]
    )

    # 2) 日射が当たらない場合

    # 2-1) 地面の場合は、年平均気温とする
    f = tuple((f_sun == False) & (data.boundary_type_i_ks == "ground"))
    Teolist[f] = np.full(24 * 365 * 4, np.average(To_n))

    # 2-2) 日の当たらない一般部位と内壁
    f = tuple(
        (f_sun == False) & ((data.boundary_type_i_ks == "external_general_part") | (data.boundary_type_i_ks == "internal")))
    Teolist[f] = np.zeros(24 * 365 * 4)

    # ********** 日除けの日影面積率の計算 **********

    # 外表面に日射が当たる場合
    FSDW_i_k_n = np.zeros((data.N_surf_i, 24 * 365 * 4))

    for k in range(data.N_surf_i):

        if data.is_sun_striked_outside_i_ks[k]:

            # 透明開口部の場合
            if data.boundary_type_i_ks[k] == "external_transparent_part":
                # 日除けの日影面積率の計算
                if data.sunbrk[k]['existance']:
                    if data.sunbrk[k]['input_method'] == 'simple':
###################################################################################
                        h_s = np.where(h_s_n > 0.0, h_s_n, 0.0)
                        a_s = np.where(h_s_n > 0.0, a_s_n, 0.0)

                        FSDW_i_k_n[k] = a8.calc_F_SDW_i_k_n(
                            D_i_k=data.sunbrk[k]['depth'],  # 出幅
                            d_e=data.sunbrk[k]['d_e'],  # 窓の上端から庇までの距離
                            d_h=data.sunbrk[k]['d_h'],  # 窓の高さ
                            a_s_n=a_s,
                            h_s_n=h_s,
                            Wa_i_k=w_alpha_i_k[k]
                        )
                    elif data.sunbrk[k].input_method == 'detailed':
                        raise ValueError
                    else:
                        raise ValueError

    # ********** 透過日射熱取得の計算 **********

    f = tuple(f_sun & (data.boundary_type_i_ks == "external_transparent_part"))

    QGT_i_k_n[f] = a11.calc_QGT_i_k_n(
        cos_Theta_i_k_n=cos_Theta_i_k_n[f],
        IAC_i_k=data.IAC_i_k[f],
        I_D_i_k_n=I_D_i_k_n[f],
        FSDW_i_k_n=FSDW_i_k_n[f],
        I_S_i_k_n=I_S_i_k_n[f],
        I_R_i_k_n=I_R_i_k_n[f],
        A_i_k=data.a_i_ks[f],
        tau_i_k=data.tau_i_k[f],
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
        N_surf_i=data.N_surf_i,
        direction=data.direction_i_ks,
        boundary_type=data.boundary_type_i_ks,
        is_sun_striked_outside=data.is_sun_striked_outside_i_ks,
        is_solar_absorbed_inside=data.is_solar_absorbed_inside,
        a_i_k=data.h_i_ks,
        eps_i_k=data.eps_i_k,
        as_i_k=data.as_i_k,
        A_i_k=data.a_i_ks,
        Rnext_i_k=np.vectorize(convert_from_next_room_name_to_id)(data.next_room_type_i_ks),
#        Rnext_i_k=data.next_room_type_i_ks,
        U=data.U,
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
        Nroot=Nroot
    )
