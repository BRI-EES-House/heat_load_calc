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

        self.N_surf_i = len(surfaces)

        self.is_sun_striked_outside = [d['is_sun_striked_outside'] for d in surfaces]
                                                        # True:外表面に日射が当たる
        # 境界条件タイプ
        self.boundary_type = [d['boundary_type'] for d in surfaces]

        # 隣室温度差係数
        self.a_i_k = np.zeros(self.N_surf_i)
        for k, d in enumerate(surfaces):
            if self.boundary_type[k] in ["external_general_part", "external_transparent_part", "external_opaque_part"]:
                self.a_i_k[k] = d['temp_dif_coef']

        self.next_room_type = np.zeros(self.N_surf_i, dtype=np.object)
        for k, d in enumerate(surfaces):
            if self.boundary_type[k] in ["internal"]:
                self.next_room_type[k] = d['next_room_type']

        # 外皮の場合
        self.direction = np.zeros(self.N_surf_i, dtype=np.object)
        self.Type = np.zeros(self.N_surf_i, dtype=np.object)
        self.Rnext_i_k = np.zeros(self.N_surf_i, dtype=np.object)
        self.RhoG_l = np.zeros(self.N_surf_i)
        self.w_alpha_i_k = np.zeros(self.N_surf_i)
        self.w_beta_i_k = np.zeros(self.N_surf_i)
        self.Wz_i_k = np.zeros(self.N_surf_i)
        self.Ww_i_k = np.zeros(self.N_surf_i)
        self.Ws_i_k = np.zeros(self.N_surf_i)
        self.PhiS_i_k = np.zeros(self.N_surf_i)
        self.PhiG_i_k = np.zeros(self.N_surf_i)

        for k, d in enumerate(surfaces):
            if self.boundary_type[k] in ["external_general_part", "external_transparent_part", "external_opaque_part"]:

                if self.is_sun_striked_outside[k]:
                    self.direction[k] = d['direction']

                self.Type[k] = "external"  # 境界条件タイプ
                self.Rnext_i_k[k] = ""
                # 地面反射率[-]
                self.RhoG_l[k] = 0.1

                self.direction[k] = self.direction[k]


                # 方位角、傾斜面方位角 [rad]
                self.w_alpha_i_k[k], self.w_beta_i_k[k] = a19.get_slope_angle(self.direction[k])

                # 傾斜面に関する変数であり、式(73)
                self.Wz_i_k[k], self.Ww_i_k[k], self.Ws_i_k[k] = \
                    a19.get_slope_angle_intermediate_variables(self.w_alpha_i_k[k], self.w_beta_i_k[k])

                # 傾斜面の天空に対する形態係数の計算 式(120)
                self.PhiS_i_k[k] = a19.get_Phi_S_i_k(self.Wz_i_k[k])

                # 傾斜面の地面に対する形態係数 式(119)
                self.PhiG_i_k[k] = a19.get_Phi_G_i_k(self.PhiS_i_k[k])

                # 温度差係数
                self.a_i_k[k] = self.a_i_k[k]

            # 内壁の場合
            elif self.boundary_type[k] in ["internal"]:
                # 隣室の場合
                self.Type[k] = "internal"
                self.Rnext_i_k[k] = self.next_room_type[k] # 隣室名称

            # 土壌の場合
            elif self.boundary_type[k] in ["ground"]:
                self.Type[k] = "ground"  # 土壌の場合
                self.Rnext_i_k[k] = ""

            # 例外
            else:
                print("境界Typeが見つかりません。 name=", surfaces[k]['name'], "boundary_type=", self.boundary_type[k])


        # 部位のタイプ
        self.is_solar_absorbed_inside = [d['is_solar_absorbed_inside'] for d in surfaces]      #床フラグ（透過日射の吸収部位）

        self.A_i_k = np.array([float(d['area']) for d in surfaces])               # 面積

        # 屋外に日射が当たる場合はひさしの情報を読み込む
        self.sunbrk = [None] * self.N_surf_i
        for k, d in enumerate(surfaces):
            if self.is_sun_striked_outside[k]:
                self.sunbrk[k] = d['solar_shading_part']         # ひさし

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
        self.tau_i_k = np.zeros(self.N_surf_i)
        self.IAC_i_k = np.zeros(self.N_surf_i, dtype=np.object)
        self.Cd_i_k = np.zeros(self.N_surf_i)
        for k, data in enumerate(datalist):
            if is_transparent_part[k]:
                self.tau_i_k[k] = float(data['eta_value'])
                self.IAC_i_k[k] = data['incident_angle_characteristics']
                self.Cd_i_k[k] = a25.get_Cd(self.IAC_i_k[k])

        # 室外側日射吸収率・室外側放射率
        self.as_i_k = np.zeros(self.N_surf_i)
        self.eps_i_k = np.zeros(self.N_surf_i)
        for k, data in enumerate(datalist):
            if self.is_sun_striked_outside[k]:
                self.as_i_k[k] = data['outside_solar_absorption']        # 室外側日射吸収率
                self.eps_i_k[k] = float(data['outside_emissivity'])      # 室外側放射率[-]

        # 室外側熱伝達率
        self.ho_i_k_n = np.zeros(self.N_surf_i)
        for k, data in enumerate(datalist):
            if self.boundary_type[k] == 'external_general_part' or is_transparent_part[k] or is_opaque_part[k]:
                Ro_i_k_n = data['outside_heat_transfer_resistance']   # 室外側熱伝達抵抗
                self.ho_i_k_n[k] = a23.get_ho_i_k_n(Ro_i_k_n)          # 室外側熱伝達率[W/m2K]

        # 室内側熱伝達抵抗・室内側表面総合熱伝達率
        self.hi_i_k_n = np.zeros(self.N_surf_i)
        Ri_i_k_n = np.zeros(self.N_surf_i)
        for k, data in enumerate(datalist):
            Ri_i_k_n[k] = data['inside_heat_transfer_resistance']        # 室内側熱伝達抵抗
            self.hi_i_k_n[k] = a23.get_hi_i_k_n(Ri_i_k_n[k])              # 室内側表面総合熱伝達率 式(122)

        # 開口部熱貫流率・開口部の室内表面から屋外までの熱貫流率
        self.U = np.zeros(self.N_surf_i)
        self.Uso = np.zeros(self.N_surf_i)
        for k, data in enumerate(datalist):
            if is_general_part[k] == False:
                self.U[k] = float(data['u_value'])                       # 開口部熱貫流率[W/m2K]
                self.Uso[k] = a25.get_Uso(self.U[k], Ri_i_k_n[k])            # 開口部の室内表面から屋外までの熱貫流率[W/(m2･K)] 式(124)

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

        # 外表面に日射が当たる場合
        self.cos_Theta_i_k_n = np.zeros((self.N_surf_i, 24 * 365 * 4))
        self.Iw_i_k_n = np.zeros((self.N_surf_i, 24 * 365 * 4))
        self.I_D_i_k_n = np.zeros((self.N_surf_i, 24 * 365 * 4))
        self.I_S_i_k_n = np.zeros((self.N_surf_i, 24 * 365 * 4))
        self.I_R_i_k_n = np.zeros((self.N_surf_i, 24 * 365 * 4))
        for k, data in enumerate(datalist):
            if 'external' in self.Type[k]:
                # 入射角の方向余弦
                self.cos_Theta_i_k_n[k] = a6.calc_cos_incident_angle(
                    h_sun_sin_n=solar_position["Sh_n"],
                    h_sun_cos_n=solar_position["cos_h_s"],
                    a_sun_sin_n=solar_position["sin_a_s"],
                    a_sun_cos_n=solar_position["cos_a_s"],
                    w_alpha=self.w_alpha_i_k[k],
                    w_beta=self.w_beta_i_k[k]
                )

                # 傾斜面日射量
                self.Iw_i_k_n[k], self.I_D_i_k_n[k], self.I_S_i_k_n[k], self.I_R_i_k_n[k] = a7.calc_slope_sol(
                    I_DN_n=I_DN_n,
                    I_sky_n=I_sky_n,
                    Sh_n=solar_position["Sh_n"],
                    cos_Theta_i_k_n=self.cos_Theta_i_k_n[k],
                    PhiS_i_k=self.PhiS_i_k[k],
                    PhiG_i_k=self.PhiG_i_k[k],
                    RhoG_l=self.RhoG_l[k]
                )


        # 外表面に日射が当たる場合
        self.Teolist = np.zeros((self.N_surf_i, 24 * 365 * 4))
        for k, data in enumerate(datalist):
            if self.is_sun_striked_outside[k]:

                # 一般部位、不透明な開口部の場合
                if self.boundary_type[k] in ["external_general_part", "external_opaque_part"]:
                    # 傾斜面の相当外気温度の計算
                    self.Teolist[k] = a9.get_Te_n_1(
                        To_n=To_n,
                        as_i_k=self.as_i_k[k],
                        I_w_i_k_n=self.Iw_i_k_n[k],
                        eps_i_k=self.eps_i_k[k],
                        PhiS_i_k=self.PhiS_i_k[k],
                        RN_n=RN_n,
                        ho_i_k_n=self.ho_i_k_n[k]
                    )

                # 透明開口部の場合
                elif self.boundary_type[k] == "external_transparent_part":
                    # 相当外気温度の集約
                    self.Teolist[k] = a9.get_Te_n_2(
                        To_n=To_n,
                        eps_i_k=self.eps_i_k[k],
                        PhiS_i_k=self.PhiS_i_k[k],
                        RN_n=RN_n,
                        ho_i_k_n=self.ho_i_k_n[k]
                    )

                else:
                    raise ValueError()

            # 地面の場合は、年平均気温とする
            elif self.boundary_type[k] == "ground":
                self.Teolist[k] = [AnnualTave] * (24*365*4)

            elif self.boundary_type[k] in ["external_general_part", "internal"]:
                self.Teolist[k] = [0.0] * (24*365*4)

            else:
                raise ValueError(self.boundary_type[k])


        # 外表面に日射が当たる場合
        self.FSDW_i_k_n = np.zeros((self.N_surf_i, 24 * 365 * 4))
        self.QGT_i_k_n = np.zeros((self.N_surf_i, 24 * 365 * 4))
        for k, data in enumerate(datalist):
            if self.is_sun_striked_outside[k]:

                # 透明開口部の場合
                if self.boundary_type[k] == "external_transparent_part":
                    # 日除けの日影面積率の計算
                    if self.sunbrk[k]['existance']:
                        if self.sunbrk[k]['input_method'] == 'simple':
                            self.FSDW_i_k_n[k] = a8.calc_F_SDW_i_k_n(
                                D_i_k=self.sunbrk[k]['depth'],  # 出幅
                                d_e=self.sunbrk[k]['d_e'],      # 窓の上端から庇までの距離
                                d_h=self.sunbrk[k]['d_h'],      # 窓の高さ
                                a_s_n=solar_position['a_s'],
                                h_s_n=solar_position['h_s'],
                                Wa_i_k=self.w_alpha_i_k[k]
                            )
                        elif self.sunbrk[k].input_method == 'detailed':
                            raise ValueError
                        else:
                            raise ValueError
                    else:
                        self.FSDW_i_k_n[k, :] = 0.0

                    # 透過日射熱取得
                    self.QGT_i_k_n[k] = a11.calc_QGT_i_k_n(
                        cos_Theta_i_k_n=self.cos_Theta_i_k_n[k],
                        IAC_i_k=self.IAC_i_k[k],
                        I_D_i_k_n=self.I_D_i_k_n[k],
                        FSDW_i_k_n=self.FSDW_i_k_n[k],
                        I_S_i_k_n=self.I_S_i_k_n[k],
                        I_R_i_k_n=self.I_R_i_k_n[k],
                        A_i_k=self.A_i_k[k],
                        tau_i_k=self.tau_i_k[k],
                        Cd_i_k=self.Cd_i_k[k]
                    )

                else:
                    self.QGT_i_k_n[k] = np.zeros(24*365*4)
            else:
                self.QGT_i_k_n[k] = np.zeros(24 * 365 * 4)
