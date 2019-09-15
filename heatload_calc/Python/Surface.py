import numpy as np
import a2_ResponseFactor as a2
import apdx6_direction_cos_incident_angle as a6
import a7_inclined_surface_solar_radiation as a7
import a8_shading as a8
import a9_rear_surface_equivalent_temperature as a9
import a11_opening_transmission_solar_radiation as a11
import a19_Exsrf as a19
import a23_surface_heat_transfer_coefficient as a23
import a24_wall_layer as a24
import a25_window as a25

"""
付録23．表面熱伝達率
"""

class GroupedSurface:
    def __init__(self):
        pass

# 室内部位に関連するクラス
class Surface:

    # 初期化
    def __init__(self, surfaces, solar_position, I_DN_n, I_sky_n, RN_n, To_n, AnnualTave):

        # ========== JSONからの読み出し ==========

        # 部位数
        self.N_surf_i = len(surfaces)

        def read_to_array(key):
            return np.array([d[key] if key in d else None for d in surfaces])

        # True:外表面に日射が当たる
        self.is_sun_striked_outside = read_to_array('is_sun_striked_outside')

        # 境界条件タイプ
        self.boundary_type = read_to_array('boundary_type')

        # 隣室温度差係数
        self.a_i_k =read_to_array('temp_dif_coef')

        # 隣接室
        self.Rnext_i_k = read_to_array('next_room_type')

        # 方位
        self.direction = read_to_array('direction')

        # 床フラグ（透過日射の吸収部位）
        self.is_solar_absorbed_inside = read_to_array('is_solar_absorbed_inside')

        # 面積
        self.A_i_k = read_to_array('area')

        # 屋外に日射が当たる場合はひさしの情報を読み込む
        sunbrk = read_to_array('solar_shading_part')

        # 壁体の種別
        is_general_part = [(self.boundary_type[k] in ["external_general_part", "internal", "ground"]) for k in range(self.N_surf_i)]
        is_transparent_part = [self.boundary_type[k] in ["external_transparent_part"] for k in range(self.N_surf_i)]
        is_opaque_part = [self.boundary_type[k] in ["external_opaque_part"] for k in range(self.N_surf_i)]
        is_ground = [self.boundary_type[k] == "ground" for k in range(self.N_surf_i)]     # 壁体に土壌が含まれる場合True

        # 読みだし元位置決定
        part_key_name = [{
            "external_general_part":     "general_part_spec",
            "internal":                  "general_part_spec",
            "ground":                    "ground_spec",
            "external_transparent_part": "transparent_opening_part_spec",
            "external_opaque_part":      "opaque_opening_part_spec"
        }[self.boundary_type[k]] for k in range(self.N_surf_i)]

        # 読み出し
        datalist = [s[k] for (s,k) in zip(surfaces, part_key_name)]

        # 透過率・拡散日射の入射角特性
        self.tau_i_k = np.array([float(data['eta_value']) if 'eta_value' in data else 0.0 for data in datalist])
        self.IAC_i_k = np.array([data['incident_angle_characteristics'] if 'incident_angle_characteristics' in data else None for data in datalist])

        # 室外側日射吸収率
        self.as_i_k = np.array([data['outside_solar_absorption'] if 'outside_solar_absorption' in data else 0.0 for data in datalist])

        # 室外側放射率[-]
        self.eps_i_k = np.array([float(data['outside_emissivity']) if 'outside_emissivity' in data else 0.0 for data in datalist])


        # 室外側熱伝達率
        Ro_i_k_n = np.array([float(data['outside_heat_transfer_resistance']) if 'outside_heat_transfer_resistance' in data else 0.0 for data in datalist])

        # 室内側熱伝達抵抗・室内側表面総合熱伝達率
        Ri_i_k_n = np.array([data['inside_heat_transfer_resistance'] for data in datalist])        # 室内側熱伝達抵抗

        # 開口部熱貫流率[W/m2K]
        self.U = np.array([data['u_value'] if 'u_value' in data else 0.0 for data in datalist])



        # ========== 初期計算 ==========

        def get_bi(b):
            return np.array(b)[np.newaxis, :]


        # *********** 外壁傾斜面の計算 ***********

        f = (self.boundary_type == "external_general_part") | (self.boundary_type == "external_transparent_part") | (self.boundary_type == "external_opaque_part")

        self.RhoG_l = np.zeros(self.N_surf_i)
        self.w_alpha_i_k = np.zeros(self.N_surf_i)
        self.w_beta_i_k = np.zeros(self.N_surf_i)
        self.Wz_i_k = np.zeros(self.N_surf_i)
        self.Ww_i_k = np.zeros(self.N_surf_i)
        self.Ws_i_k = np.zeros(self.N_surf_i)
        self.PhiS_i_k = np.zeros(self.N_surf_i)
        self.PhiG_i_k = np.zeros(self.N_surf_i)

        # 方位角、傾斜面方位角 [rad]
        self.w_alpha_i_k[f], self.w_beta_i_k[f] = a19.get_slope_angle(self.direction[f])

        # 傾斜面に関する変数であり、式(73)
        self.Wz_i_k[f], self.Ww_i_k[f], self.Ws_i_k[f] = \
            a19.get_slope_angle_intermediate_variables(self.w_alpha_i_k[f], self.w_beta_i_k[f])

        # 傾斜面の天空に対する形態係数の計算 式(120)
        self.PhiS_i_k[f] = a19.get_Phi_S_i_k(self.Wz_i_k[f])

        # 傾斜面の地面に対する形態係数 式(119)
        self.PhiG_i_k[f] = a19.get_Phi_G_i_k(self.PhiS_i_k[f])

        # 温度差係数
        self.a_i_k[f] = self.a_i_k[f]

        # 地面反射率[-]
        self.RhoG_l[f] = 0.1

        # ********** 拡散日射の入射角特性の計算 **********
        f = tuple(get_bi(is_transparent_part))
        self.Cd_i_k = np.zeros(self.N_surf_i)
        self.Cd_i_k[f] = a25.get_Cd(self.IAC_i_k[f])

        # 室外側熱伝達率
        self.ho_i_k_n = np.zeros(self.N_surf_i)
        for k, data in enumerate(datalist):
            if self.boundary_type[k] == 'external_general_part' or is_transparent_part[k] or is_opaque_part[k]:
                self.ho_i_k_n[k] = a23.get_ho_i_k_n(Ro_i_k_n[k])          # 室外側熱伝達率[W/m2K]

        # 室内側熱伝達抵抗・室内側表面総合熱伝達率
        self.hi_i_k_n = a23.get_hi_i_k_n(Ri_i_k_n)              # 室内側表面総合熱伝達率 式(122)

        # 開口部熱貫流率・開口部の室内表面から屋外までの熱貫流率
        self.Uso = np.zeros(self.N_surf_i)
        f = tuple(np.logical_not(get_bi(is_general_part)))
        self.Uso[f] = a25.get_Uso(self.U[f], Ri_i_k_n[f])            # 開口部の室内表面から屋外までの熱貫流率[W/(m2･K)] 式(124)

        # 応答係数
        self.RFT0, self.RFA0, self.RFT1, self.RFA1, self.Row, self.Nroot = \
            np.zeros(self.N_surf_i), np.zeros(self.N_surf_i), np.zeros((self.N_surf_i, 12)), np.zeros((self.N_surf_i, 12)), \
            np.zeros((self.N_surf_i, 12)), np.zeros(self.N_surf_i, dtype=np.int64)
        for k, data in enumerate(datalist):
            if is_general_part[k] == False:
                self.RFT0[k], self.RFA0[k], self.RFT1[k], self.RFA1[k], self.Row[k], self.Nroot[k] = \
                    1.0, 1.0/self.Uso[k], np.zeros(12), np.zeros(12), np.zeros(12), 0
            else:
                layers = a24.get_layers(data, is_ground[k])

                # 応答係数
                self.RFT0[k], self.RFA0[k], self.RFT1[k], self.RFA1[k], self.Row[k], self.Nroot[k] = \
                    a2.calc_response_factor(is_ground[k], layers[:, 1] * 1000.0, layers[:, 0])

        # ********** 入射角の方向余弦および傾斜面日射量の計算(外壁のみ) **********

        # 入射角の方向余弦
        f = (self.boundary_type == "external_general_part") | (self.boundary_type == "external_transparent_part") | (self.boundary_type == "external_opaque_part")
        self.cos_Theta_i_k_n = np.zeros((self.N_surf_i, 24 * 365 * 4))
        self.cos_Theta_i_k_n[f] = a6.calc_cos_incident_angle(
            h_sun_sin_n=solar_position["Sh_n"],
            h_sun_cos_n=solar_position["cos_h_s"],
            a_sun_sin_n=solar_position["sin_a_s"],
            a_sun_cos_n=solar_position["cos_a_s"],
            w_alpha_k=self.w_alpha_i_k[f],
            w_beta_k=self.w_beta_i_k[f]
        )

        # 傾斜面日射量
        f = (self.boundary_type == "external_general_part") | (self.boundary_type == "external_transparent_part") | (self.boundary_type == "external_opaque_part")
        Iw_i_k_n = np.zeros((self.N_surf_i, 24 * 365 * 4))
        I_D_i_k_n = np.zeros((self.N_surf_i, 24 * 365 * 4))
        I_S_i_k_n = np.zeros((self.N_surf_i, 24 * 365 * 4))
        I_R_i_k_n = np.zeros((self.N_surf_i, 24 * 365 * 4))
        Iw_i_k_n[f], I_D_i_k_n[f], I_S_i_k_n[f], I_R_i_k_n[f] = a7.calc_slope_sol(
            I_DN_n=I_DN_n,
            I_sky_n=I_sky_n,
            Sh_n=solar_position["Sh_n"],
            cos_Theta_i_k_n=self.cos_Theta_i_k_n[f],
            PhiS_i_k=self.PhiS_i_k[f],
            PhiG_i_k=self.PhiG_i_k[f],
            RhoG_l=self.RhoG_l[f]
        )

        # ********** 傾斜面の相当外気温度の計算 **********

        self.Teolist = np.zeros((self.N_surf_i, 24 * 365 * 4))

        # 1) 日射が当たる場合
        f_sun = get_bi(self.is_sun_striked_outside)

        # 1-1) 一般部位、不透明な開口部の場合
        f = tuple(f_sun & ((self.boundary_type == "external_general_part") | (self.boundary_type == "external_opaque_part")))

        self.Teolist[f] = a9.get_Te_n_1(
            To_n=To_n,
            as_i_k=self.as_i_k[f],
            I_w_i_k_n=Iw_i_k_n[f],
            eps_i_k=self.eps_i_k[f],
            PhiS_i_k=self.PhiS_i_k[f],
            RN_n=RN_n,
            ho_i_k_n=self.ho_i_k_n[f]
        )

        # 1-2) 透明開口部の場合
        f = tuple(f_sun & (self.boundary_type == "external_transparent_part"))

        self.Teolist[f] = a9.get_Te_n_2(
            To_n=To_n,
            eps_i_k=self.eps_i_k[f],
            PhiS_i_k=self.PhiS_i_k[f],
            RN_n=RN_n,
            ho_i_k_n=self.ho_i_k_n[f]
        )

        # 2) 日射が当たらない場合

        # 2-1) 地面の場合は、年平均気温とする
        f = tuple((f_sun == False) & (self.boundary_type == "ground"))
        self.Teolist[f] = [AnnualTave] * (24*365*4)

        # 2-2) 日の当たらない一般部位と内壁
        f = tuple((f_sun == False) & ((self.boundary_type == "external_general_part") | (self.boundary_type == "internal")))
        self.Teolist[f] = [0.0] * (24*365*4)

        # ********** 日除けの日影面積率の計算 **********

        # 外表面に日射が当たる場合
        FSDW_i_k_n = np.zeros((self.N_surf_i, 24 * 365 * 4))
        for k in range(self.N_surf_i):
            if self.is_sun_striked_outside[k]:

                # 透明開口部の場合
                if self.boundary_type[k] == "external_transparent_part":
                    # 日除けの日影面積率の計算
                    if sunbrk[k]['existance']:
                        if sunbrk[k]['input_method'] == 'simple':
                            FSDW_i_k_n[k] = a8.calc_F_SDW_i_k_n(
                                D_i_k=sunbrk[k]['depth'],  # 出幅
                                d_e=sunbrk[k]['d_e'],      # 窓の上端から庇までの距離
                                d_h=sunbrk[k]['d_h'],      # 窓の高さ
                                a_s_n=solar_position['a_s'],
                                h_s_n=solar_position['h_s'],
                                Wa_i_k=self.w_alpha_i_k[k]
                            )
                        elif sunbrk[k].input_method == 'detailed':
                            raise ValueError
                        else:
                            raise ValueError

        # ********** 透過日射熱取得の計算 **********

        self.QGT_i_k_n = np.zeros((self.N_surf_i, 24 * 365 * 4))
        f = tuple(f_sun & (self.boundary_type == "external_transparent_part"))
        self.QGT_i_k_n[f] = a11.calc_QGT_i_k_n(
            cos_Theta_i_k_n=self.cos_Theta_i_k_n[f],
            IAC_i_k=self.IAC_i_k[f],
            I_D_i_k_n=I_D_i_k_n[f],
            FSDW_i_k_n=FSDW_i_k_n[f],
            I_S_i_k_n=I_S_i_k_n[f],
            I_R_i_k_n=I_R_i_k_n[f],
            A_i_k=self.A_i_k[f],
            tau_i_k=self.tau_i_k[f],
            Cd_i_k=self.Cd_i_k[f]
        )
