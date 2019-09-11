import numpy as np
import a2_ResponseFactor as a2
import a19_Exsrf as a19
import a23_surface_heat_transfer_coefficient as a23
import a24_wall_layer as a24
import a25_window as a25

"""
付録23．表面熱伝達率
"""

# 室内部位に関連するクラス
class Surface:

    # 初期化
    def __init__(self, d = None):
        self.oldTsd_a = np.zeros(0)
        self.oldTsd_t = np.zeros(0)

        if d != None :
            self.is_sun_striked_outside = d['is_sun_striked_outside']
                                                            # True:外表面に日射が当たる
            # 境界条件タイプ
            self.boundary_type = d['boundary_type']

            # 境界条件クラスの初期化
            self.backside_boundary_condition = a19.Exsrf()

            self.name = d['name']                           # 壁体名称

            # 裏面相当外気温度をListで保持していない
            self.is_Teo_list = False
            # 外皮の場合
            if "external" in self.boundary_type:
                self.direction = None
                if self.is_sun_striked_outside:
                    self.direction = d['direction']
                    self.Teolist = [15.0 for j in range(8760 * 4)]
                    self.is_Teo_list = True
                # 隣室温度差係数
                self.temp_dif_coef = d['temp_dif_coef']
                # 境界条件の初期化
                self.backside_boundary_condition = a19.external_init(self.direction, \
                    self.is_sun_striked_outside, self.temp_dif_coef)
            # 内壁の場合
            elif self.boundary_type == "internal":
                self.next_room_type = d['next_room_type']
                self.backside_boundary_condition = a19.internal_init(self.next_room_type)
            # 土壌の場合
            elif self.boundary_type == "ground":
                self.backside_boundary_condition = a19.ground_init()
            # 例外
            else:
                print("境界Typeが見つかりません。 name=", self.name, "boundary_type=", self.boundary_type)

            # 部位のタイプ
            self.is_solar_absorbed_inside = d['is_solar_absorbed_inside']      #床フラグ（透過日射の吸収部位）

            # 面積
            self.A_i_k = float(d['area'])

            # 屋外に日射が当たる場合はひさしの情報を読み込む
            if self.is_sun_striked_outside:
                self.sunbrk = d['solar_shading_part']         # ひさし

            self.is_ground = self.boundary_type == "ground"     # 壁体に土壌が含まれる場合True

            # 相当外気温度の初期化
            self.Teo = 15.0
            self.oldTeo = 15.0

            self.Qt = 0.0
            self.Qc = 0.0  # 対流成分
            self.Qr = 0.0  # 放射成分
            self.RS = 0.0  # 短波長熱取得成分
            self.Lr = 0.0  # 放射暖房成分

            self.oldTeo = 15.0  # 前時刻の室外側温度
            self.oldqi = 0.0  # 前時刻の室内側表面熱流

            # 一般部位の初期化
            # 透明部位の初期化
            # 不透明な開口部の初期化

            if is_general_part(self.boundary_type):
                part_key_name = 'ground_spec' if self.boundary_type == "ground" else 'general_part_spec'
                _d = d[part_key_name]
            elif is_transparent_part(self.boundary_type):
                _d = d['transparent_opening_part_spec']
            else:
                _d = d['opaque_opening_part_spec']

            # 透過率＝日射熱取得率とするか0
            if is_transparent_part(self.boundary_type):
                self.tau = float(_d['eta_value'])
            else:
                self.tau = 0.0

            if self.boundary_type == 'external_general_part' or  is_transparent_part(self.boundary_type) or is_opaque_part(self.boundary_type):
                # 室外側熱伝達抵抗
                Ro_i_k_n = _d['outside_heat_transfer_resistance']

                # 室外側熱伝達率[W/m2K]
                self.ho = 1.0 / float(Ro_i_k_n)
            else:
                self.ho = 0.0

            # 室側側日射吸収率
            if self.is_sun_striked_outside:
                self.as_i_k = _d['outside_solar_absorption']
            else:
                self.as_i_k = None

            # 室外側放射率[-]
            if self.is_sun_striked_outside:
                self.eps_i_k = float(_d['outside_emissivity'])
            else:
                self.eps_i_k = None  # 室外側表面放射率

            # 室内側放射率[－]
            self.Ei = 0.9

            # 室内側熱伝達抵抗
            self.Ri_i_k_n = _d['inside_heat_transfer_resistance']

            # 室内側表面総合熱伝達率 式(122)
            self.hi = a23.get_hi_i_k_n(self.Ri_i_k_n)

            # 開口部熱貫流率[W/m2K]
            if is_general_part(self.boundary_type) == False:
                self.U = float(_d['u_value'])
            else:
                self.U = None

            # 開口部の室内表面から屋外までの熱貫流率[W/(m2･K)] 式(124)
            if is_general_part(self.boundary_type) == False:
                self.Uso = a25.get_Uso(self.U, self.Ri_i_k_n)
            else:
                self.Uso = None

            # 応答係数
            # 吸熱応答係数の初項 RFA0
            # 貫流応答係数の初項 RFT0
            # 指数項別貫流応答の初項 RFT1
            # 指数項別吸熱応答の初項 RFA1
            if is_general_part(self.boundary_type) == False:
                self.RFT0, self.RFA0, self.RFT1, self.RFA1, self.Row, self.Nroot = 1.0, 1.0/self.Uso, None, None, None, 0
            else:
                layers = a24.get_layers(_d, self.is_ground)

                # 応答係数
                self.RFT0, self.RFA0, self.RFT1, self.RFA1, self.Row, self.Nroot = a2.calc_response_factor(
                    is_ground=self.is_ground,
                    NcalTime=50,
                    C=layers[:, 1] * 1000.0,
                    R=layers[:, 0]
                )

            # 入射角特性番号
            if is_transparent_part(self.boundary_type):
                self.incident_angle_characteristics = _d['incident_angle_characteristics']
            else:
                self.incident_angle_characteristics = None

            # 拡散日射に対する入射角特性
            self.Cd = (a25.get_Cd(self.incident_angle_characteristics)
                if is_transparent_part(self.boundary_type)
                else None)


            self.oldTsd_a = np.zeros(self.Nroot)
            self.oldTsd_t = np.zeros(self.Nroot)

            # 部位のグループ化に関する変数
            # グループ番号
            self.group_number = -999
            # グループ化済み変数
            self.is_grouping = False


def is_general_part(boundary_type:str):
    return boundary_type == "external_general_part" or boundary_type == "internal" or boundary_type == "ground"


def is_transparent_part(boundary_type:str):
    return boundary_type == "external_transparent_part"


def is_opaque_part(boundary_type:str):
    return boundary_type == "external_opaque_part"
