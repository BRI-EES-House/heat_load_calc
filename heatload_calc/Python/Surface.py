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
    def __init__(self, d, solar_position, I_DN_n, I_sky_n, RN_n, To_n, AnnualTave):
        self.is_sun_striked_outside = d['is_sun_striked_outside']
                                                        # True:外表面に日射が当たる
        # 境界条件タイプ
        self.boundary_type = d['boundary_type']

        # 隣室温度差係数
        if self.boundary_type in ["external_general_part", "external_transparent_part", "external_opaque_part"]:
            self.a_i_k = d['temp_dif_coef']

        if self.boundary_type in ["internal"]:
            self.next_room_type = d['next_room_type']

        # 外皮の場合
        if self.boundary_type in ["external_general_part", "external_transparent_part", "external_opaque_part"]:
            self.direction = None
            if self.is_sun_striked_outside:
                self.direction = d['direction']

            self.Type = "external"  # 境界条件タイプ
            self.nextroomname = ""

            # 地面反射率[-]
            self.RhoG_l = 0.1

            self.direction = self.direction

            # 方位角、傾斜面方位角 [rad]
            self.Wa, self.Wb = a19.get_slope_angle(self.direction)

            # 傾斜面に関する変数であり、式(73)
            self.Wz, self.WW, self.Ws = a19.get_Wz_Ww_Ws(self.Wa, self.Wb)

            # 傾斜面の天空に対する形態係数の計算 式(120)
            self.PhiS_i_k = a19.get_Phi_S_i_k(self.Wz)

            # 傾斜面の地面に対する形態係数 式(119)
            self.PhiG_i_k = a19.get_Phi_G_i_k(self.PhiS_i_k)

            # 温度差係数
            self.a_i_k = self.a_i_k

        # 内壁の場合
        elif self.boundary_type in ["internal"]:
            # 隣室の場合
            self.Type = "internal"
            self.nextroomname = self.next_room_type  # 隣室名称

        # 土壌の場合
        elif self.boundary_type in ["ground"]:
            self.Type = "ground"  # 土壌の場合
            self.nextroomname = ""

        # 例外
        else:
            print("境界Typeが見つかりません。 name=", d['name'], "boundary_type=", self.boundary_type)

        # 部位のタイプ
        self.is_solar_absorbed_inside = d['is_solar_absorbed_inside']      #床フラグ（透過日射の吸収部位）

        self.A_i_k = float(d['area'])               # 面積

        # 屋外に日射が当たる場合はひさしの情報を読み込む
        if self.is_sun_striked_outside:
            self.sunbrk = d['solar_shading_part']         # ひさし

        # 壁体の種別
        is_general_part = self.boundary_type in ["external_general_part", "internal", "ground"]
        is_transparent_part = self.boundary_type in ["external_transparent_part"]
        is_opaque_part = self.boundary_type in ["external_opaque_part"]
        is_ground = self.boundary_type == "ground"     # 壁体に土壌が含まれる場合True

        # 読みだし元位置決定
        part_key_name = {
            "external_general_part":     "general_part_spec",
            "internal":                  "general_part_spec",
            "ground":                    "ground_spec",
            "external_transparent_part": "transparent_opening_part_spec",
            "external_opaque_part":      "opaque_opening_part_spec"
        }[self.boundary_type]

        # 読み出し
        data = d[part_key_name]

        # 透過率・拡散日射の入射角特性
        if is_transparent_part:
            self.tau = float(data['eta_value'])
            self.incident_angle_characteristics = data['incident_angle_characteristics']
            self.Cd = a25.get_Cd(self.incident_angle_characteristics)

        # 室外側日射吸収率・室外側放射率
        if self.is_sun_striked_outside:
            self.as_i_k = data['outside_solar_absorption']        # 室外側日射吸収率
            self.eps_i_k = float(data['outside_emissivity'])      # 室外側放射率[-]
        else:
            self.as_i_k = 0.0
            self.eps_i_k = 0.0

        # 室外側熱伝達率
        if self.boundary_type == 'external_general_part' or is_transparent_part or is_opaque_part:
            Ro_i_k_n = data['outside_heat_transfer_resistance']   # 室外側熱伝達抵抗
            self.ho_i_k_n = a23.get_ho_i_k_n(Ro_i_k_n)          # 室外側熱伝達率[W/m2K]
        else:
            self.ho_i_k_n = 0.0

        # 室内側熱伝達抵抗・室内側表面総合熱伝達率
        Ri_i_k_n = data['inside_heat_transfer_resistance']        # 室内側熱伝達抵抗
        self.hi_i_k_n = a23.get_hi_i_k_n(Ri_i_k_n)              # 室内側表面総合熱伝達率 式(122)

        # 開口部熱貫流率・開口部の室内表面から屋外までの熱貫流率
        if is_general_part == False:
            self.U = float(data['u_value'])                       # 開口部熱貫流率[W/m2K]
            self.Uso = a25.get_Uso(self.U, Ri_i_k_n)            # 開口部の室内表面から屋外までの熱貫流率[W/(m2･K)] 式(124)
        else:
            self.U = 0.0
            self.Uso = 0.0

        # 応答係数
        if is_general_part == False:
            self.RFT0, self.RFA0, self.RFT1, self.RFA1, self.Row, self.Nroot = 1.0, 1.0/self.Uso, np.zeros(0), np.zeros(0), None, 0
        else:
            layers = a24.get_layers(data, is_ground)

            # 応答係数
            self.RFT0, self.RFA0, self.RFT1, self.RFA1, self.Row, self.Nroot = \
                a2.calc_response_factor(is_ground, layers[:, 1] * 1000.0, layers[:, 0])

        # 外表面に日射が当たる場合
        surface = self

        if 'external' in surface.Type:

            # 入射角の方向余弦
            surface.cos_Theta_i_k_n = a6.calc_cos_incident_angle(
                h_sun_sin_n=solar_position["Sh_n"],
                h_sun_cos_n=solar_position["cos_h_s"],
                a_sun_sin_n=solar_position["sin_a_s"],
                a_sun_cos_n=solar_position["cos_a_s"],
                w_alpha=surface.Wa,
                w_beta=surface.Wb
            )

            # 傾斜面日射量
            surface.Iw_i_k_n, surface.I_D_i_k_n, surface.I_S_i_k_n, surface.I_R_i_k_n = a7.calc_slope_sol(
                I_DN_n=I_DN_n,
                I_sky_n=I_sky_n,
                Sh_n=solar_position["Sh_n"],
                cos_Theta_i_k_n=surface.cos_Theta_i_k_n,
                PhiS_i_k=surface.PhiS_i_k,
                PhiG_i_k=surface.PhiG_i_k,
                RhoG_l=surface.RhoG_l
            )
        else:
            # 0を入れておく
            surface.cos_Theta_i_k_n = np.zeros(24 * 365 * 4)
            surface.Iw_i_k_n = np.zeros(24 * 365 * 4)
            surface.I_D_i_k_n = np.zeros(24 * 365 * 4)
            surface.I_S_i_k_n = np.zeros(24 * 365 * 4)
            surface.I_R_i_k_n = np.zeros(24 * 365 * 4)


        # 外表面に日射が当たる場合
        if surface.is_sun_striked_outside:

            # 一般部位、不透明な開口部の場合
            if surface.boundary_type in ["external_general_part", "external_opaque_part"]:
                # 傾斜面の相当外気温度の計算
                surface.Teolist = a9.get_Te_n_1(
                    To_n=To_n,
                    as_i_k=surface.as_i_k,
                    I_w_i_k_n=surface.Iw_i_k_n,
                    eps_i_k=surface.eps_i_k,
                    PhiS_i_k=surface.PhiS_i_k,
                    RN_n=RN_n,
                    ho_i_k_n=surface.ho_i_k_n
                )

            # 透明開口部の場合
            elif surface.boundary_type == "external_transparent_part":
                # 相当外気温度の集約
                surface.Teolist = a9.get_Te_n_2(
                    To_n=To_n,
                    eps_i_k=surface.eps_i_k,
                    PhiS_i_k=surface.PhiS_i_k,
                    RN_n=RN_n,
                    ho_i_k_n=surface.ho_i_k_n
                )

            else:
                raise ValueError()

        # 地面の場合は、年平均気温とする
        elif surface.boundary_type == "ground":
            surface.Teolist = [AnnualTave] * (24*365*5)

        elif surface.boundary_type in ["external_general_part", "internal"]:
            surface.Teolist = [0.0] * (24*365*5)

        else:
            raise ValueError(surface.boundary_type)


        # 外表面に日射が当たる場合
        if surface.is_sun_striked_outside:

            # 透明開口部の場合
            if surface.boundary_type == "external_transparent_part":
                # 日除けの日影面積率の計算
                if surface.sunbrk['existance']:
                    if surface.sunbrk['input_method'] == 'simple':
                        surface.F_SDW_i_k = a8.calc_F_SDW_i_k(
                            D_i_k=surface.sunbrk['depth'],  # 出幅
                            d_e=surface.sunbrk['d_e'],      # 窓の上端から庇までの距離
                            d_h=surface.sunbrk['d_h'],      # 窓の高さ
                            a_s_n=solar_position['a_s'],
                            h_s_n=solar_position['h_s'],
                            Wa_i_k=surface.Wa
                        )
                    elif surface.sunbrk.input_method == 'detailed':
                        raise ValueError
                    else:
                        raise ValueError
                else:
                    surface.F_SDW_i_k = np.zeros(24*365*4, dtype=np.float)

                # 透過日射熱取得
                self.QGT_i_n = a11.calc_QGT_i_n(
                    cos_Theta_i_k_n=surface.cos_Theta_i_k_n,
                    incident_angle_characteristics=surface.incident_angle_characteristics,
                    I_D_i_k_n=surface.I_D_i_k_n,
                    F_SDW_i_k=surface.F_SDW_i_k,
                    I_S_i_k_n=surface.I_S_i_k_n,
                    I_R_i_k_n=surface.I_R_i_k_n,
                    A_i_k=surface.A_i_k,
                    T=surface.tau,
                    Cd=surface.Cd
                )

            else:
                self.QGT_i_n = np.zeros(24*365*4)
        else:
            self.QGT_i_n = np.zeros(24 * 365 * 4)
