import math
from SolarPosision import defSolpos

# 外表面の情報を保持するクラス
class Exsrf:
    """外表面の基本情報（方位角、傾斜角、地面反射率、温度差係数等）を保持するクラスを定義します。"""

    # 初期化
    def __init__(self):
        pass
        """
        :param boundary_type: 境界の種類（1:間仕切り、2:外皮、3:地盤）
        :param direction: 向き
        :param is_sun_striked_outside: 日射の有無
        :param temp_dif_coef: 温度差係数
        :param next_room_type: 隣室タイプ
        """
    # 外皮として初期化
    def external_init(self, direction, is_sun_striked_outside, temp_dif_coef):
        self.Type = "external"                      # 境界条件タイプ

        # 外皮の場合
        self.Rg = 0.1                           # 地面反射率[-]
        self.direction = direction
        self.Wa, self.Wb = self.__convert_slope_angle(direction)
                                                # 方位角、傾斜面方位角 [rad]
        # 太陽入射角の方向余弦cosθ　計算用パラメータ
        self.__Wz = math.cos(self.Wb)
        self.__Ww = math.sin(self.Wb) * math.sin(self.Wa)
        self.__Ws = math.sin(self.Wb) * math.cos(self.Wa)
        self.Fs = (1.0 + self.__Wz) / 2.0           # 傾斜面の天空に対する形態係数の計算
        self.__dblFg = 1.0 - self.Fs                # 傾斜面の地面に対する形態係数

        self.R = temp_dif_coef                      # 温度差係数
        self.is_sun_striked_outside = is_sun_striked_outside
        
    def internal_init(self, next_room_type):
        # 隣室の場合
        self.Type = "internal"
        self.nextroomname = next_room_type          # 隣室名称

    def ground_init(self):
        self.Type = "ground"                        # 土壌の場合

    # 傾斜面日射量の計算
    def update_slop_sol(self, solpos: defSolpos, Idn: float, Isky: float):
        """
        :param solpos: 太陽位置の情報
        :param Idn: 法線面直達日射量[W/m2]
        :param Isky: 水平面天空日射量[W/m2]
        """
        self.Id = self.Is = self.Ir = self.Iw = self.CosT = 0.0
        # 外皮の場合　かつ　日射が当たる場合
        if self.Type == "external" and self.is_sun_striked_outside:
            # 入射角の計算
            self.CosT = max(solpos.Sh * self.__Wz + solpos.Sw * self.__Ww + solpos.Ss * self.__Ws, 0.0)
            Ihol = solpos.Sh * Idn + Isky  # 水平面全天日射量
            self.Id = self.CosT * Idn  # 傾斜面直達日射量
            self.Is = self.Fs * Isky  # 傾斜面天空日射量
            self.Ir = self.__dblFg * self.Rg * Ihol  # 傾斜面地面反射日射量
            self.Iw = self.Id + self.Is + self.Ir  # 傾斜面全日射量

    # 傾斜面の相当外気温度の計算
    def get_Te(self, _as, ho, e, Ta, RN):
        """
        :param _as: 日射吸収率 [-]
        :param ho: 外表面の総合熱伝達率[W/m2K]
        :param e: 外表面の放射率[-]
        :param Ta: 外気温度[℃]
        :param RN: 夜間放射量[W/m2]
        :return: 傾斜面の相当外気温度 [℃]
        """
        Te = Ta + (_as * self.Iw - self.Fs * e * RN) / ho

        return Te

    # 温度差係数を設定した隣室温度
    def get_NextRoom_fromR(self, Ta, Tr):
        Te = self.R * Ta + (1.0 - self.R) * Tr
        return Te

    # 前時刻の隣室温度の場合
    def get_oldNextRoom(self, spaces):
        Te = spaces[self.nextroomname].oldTr
        return Te

    # 境界条件が一致するかどうかを判定
    def exsrf_comp(self, comp_exsrf):
        temp = False
        # 境界条件種類が一致
        if self.Type == comp_exsrf.Type:
            # 日射が当たる屋外の場合
            if self.Type == "external" and self.is_sun_striked_outside:
                temp = self.__is_float_equal(self.Rg, comp_exsrf.Rg, 1.e-5) \
                        and self.direction == comp_exsrf.direction \
                        and self.__is_float_equal(self.R, comp_exsrf.R, 1.0e-5)
            # 日射が当たらない屋外の場合
            elif self.Type == "external" and not self.is_sun_striked_outside:
                temp = self.direction == comp_exsrf.direction \
                        and self.__is_float_equal(self.R, comp_exsrf.R, 1.0e-5)
            # 隣室の場合
            elif self.Type == "internal":
                temp = (self.nextroomname == comp_exsrf.nextroomname)
            # 年平均気温の場合は無条件で一致
            elif self.Type == "ground":
                temp = True
        return temp
        
    # 実数型の一致比較
    def __is_float_equal(self, a, b, eps):
        return abs(a - b < eps)

    # 方向名称から方位角、傾斜角の計算
    def __convert_slope_angle(self, direction_string):
        direction_angle = -999.0
        inclination_angle = -999.0
        if direction_string == 's':
            direction_angle = 0.0
            inclination_angle = 90.0
        elif direction_string == 'sw':
            direction_angle = 45.0
            inclination_angle = 90.0
        elif direction_string == 'w':
            direction_angle = 90.0
            inclination_angle = 90.0
        elif direction_string == 'nw':
            direction_angle = 135.0
            inclination_angle = 90.0
        elif direction_string == 'n':
            direction_angle = 180.0
            inclination_angle = 90.0
        elif direction_string == 'ne':
            direction_angle = -135.0
            inclination_angle = 90.0
        elif direction_string == 'e':
            direction_angle = -90.0
            inclination_angle = 90.0
        elif direction_string == 'se':
            direction_angle = -45.0
            inclination_angle = 90.0
        elif direction_string == 'top':
            direction_angle = 0.0
            inclination_angle = 0.0
        elif direction_string == 'bottom':
            direction_angle = 0.0
            inclination_angle = 180.0
        
        return math.radians(direction_angle), math.radians(inclination_angle)

# 外表面情報インスタンスの辞書を作成
# def create_exsurfaces(d):
#     # for d_surface in d:
#     dic = Exsrf(
#         d['boundary_type'],
#         d['direction'],
#         d['is_sun_striked_outside'],
#         d['temp_dif_coef'],
#         d['next_room_type']
#     )
#     return dic
