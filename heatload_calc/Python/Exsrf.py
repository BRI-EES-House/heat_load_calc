import math
from SolarPosision import defSolpos


# 外表面の情報を保持するクラス
class Exsrf:
    """外表面の基本情報（方位角、傾斜角、地面反射率、温度差係数等）を保持するクラスを定義します。"""

    # 初期化
    def __init__(self, d: dict):
        """
        :param name: 名称
        :param DirectionAngle: 方位角[゜]
        :param InclinationAngle: 傾斜角[゜]
        :param GroundReflectRate: 地面反射率[-]
        :param TempDifferFactor: 温度差係数[-]
        :param IsOuterSkin: 外皮かどうか
        """
        self.name = d['Name']       # 境界条件名称, string値
        self.Type = d['Type']     # 境界条件タイプ

        # 日射が当たる屋外の場合
        if self.Type == "Outdoor":
            self.Rg = float(d['GroundReflectRate'])  # 地面反射率[-]        
            self.Wa = math.radians(float(d['DirectionAngle']))  # 傾斜面方位角 [rad]
            # 入射角計算のためのパラメータの計算
            self.Wb = math.radians(float(d['InclinationAngle']))  # 傾斜角[rad]
            self.__Wz = math.cos(self.Wb)
            self.__Ww = math.sin(self.Wb) * math.sin(self.Wa)
            self.__Ws = math.sin(self.Wb) * math.cos(self.Wa)
            self.Fs = (1.0 + self.__Wz) / 2.0           # 傾斜面の天空に対する形態係数の計算
            self.__dblFg = 1.0 - self.Fs                # 傾斜面の地面に対する形態係数
        # 隣室温度差係数の場合
        elif self.Type == "DeltaTCoeff":
            self.R = float(d['TempDifferFactor'])     # 温度差係数
        # 隣室の場合
        elif self.Type == "NextRoom":
            self.nextroomname = d['RoomName']         # 隣室名称
        elif self.Type == "AnnualAverage":            # 年平均気温の場合
            pass                                        # 追加情報はなし

    # 傾斜面日射量の計算
    # ※注意※　太陽位置の情報を保持するクラス'defSolpos'の定義に従って以下の処理を修正する必要があります
    def update_slop_sol(self, solpos: defSolpos, Idn: float, Isky: float):
        """
        :param solpos: 太陽位置の情報
        :param Idn: 法線面直達日射量[W/m2]
        :param Isky: 水平面天空日射量[W/m2]
        """
        # 外皮の場合
        if self.Type == "Outdoor":
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
            if self.Type == "Outdoor":
                temp = is_float_equal(self.Rg, comp_exsrf.Rg, 1.e-5) and is_float_equal(self.Wa, comp_exsrf.Wa, 1.e-5) \
                        and is_float_equal(self.Wb, comp_exsrf.Wb, 1.e-5)
            # 隣室温度差係数の場合
            elif self.Type == "DeltaTCoeff":
                temp = is_float_equal(self.R, comp_exsrf.R, 1.e-5)
            # 隣室の場合
            elif self.Type == "NextRoom":
                temp = (self.nextroomname == comp_exsrf.nextroomname)
            # 年平均気温の場合は無条件で一致
            elif self.Type == "AnnualAverage":
                temp = True
        return temp
        
# 実数型の一致比較
def is_float_equal(a, b, eps):
    return abs(a - b < eps)

# 外表面情報インスタンスの辞書を作成
def create_exsurfaces(d):
    dic = {}
    # for d_surface in d:
    name = d['Name']
    dic[name] = Exsrf(
        name=name,
        DirectionAngle=d['DirectionAngle'],
        InclinationAngle=d['InclinationAngle'],
        GroundReflectRate=d['GroundReflectRate'],
        TempDifferFactor=d['TempDifferFactor'],
        IsOuterSkin=d['TempDifferFactor'] is None
    )
    return dic
