import math
from SolarPosision import defSolpos


# 外表面の情報を保持するクラス
class Exsrf:
    """外表面の基本情報（方位角、傾斜角、地面反射率、温度差係数等）を保持するクラスを定義します。"""

    # 初期化
    def __init__(self, name: str, DirectionAngle: float, InclinationAngle: float, GroundReflectRate: float,
                 TempDifferFactor: float, IsOuterSkin: bool):
        """
        :param name: 名称
        :param DirectionAngle: 方位角[゜]
        :param InclinationAngle: 傾斜角[゜]
        :param GroundReflectRate: 地面反射率[-]
        :param TempDifferFactor: 温度差係数[-]
        :param IsOuterSkin: 外皮かどうか
        """
        self.name = name  # 開口部名称, string値
        self.__Rg = GroundReflectRate  # 地面反射率[-]
        self.__R = TempDifferFactor  # 温度差係数[-]
        self.__Skin = IsOuterSkin  # 外皮かどうか, bool値

        if self.__Skin:
            self.Wa = math.radians(DirectionAngle)  # 傾斜面方位角 [rad]
            # 入射角計算のためのパラメータの計算
            self.__Wb = math.radians(InclinationAngle)  # 傾斜角[rad]
            self.__Wz = math.cos(self.__Wb)
            self.__Ww = math.sin(self.__Wb) * math.sin(self.Wa)
            self.__Ws = math.sin(self.__Wb) * math.cos(self.Wa)
            self.Fs = (1.0 + self.__Wz) / 2.0  # 傾斜面の天空に対する形態係数の計算
            self.__dblFg = 1.0 - self.Fs  # 傾斜面の地面に対する形態係数
        else:
            self.CosT = None  # 入射角
            self.Wa = None  # 傾斜面方位角 [rad]
            self.Id = 0.0  # 傾斜面入射直達日射量
            self.Is = 0.0  # 傾斜面入射天空日射量
            self.Ir = 0.0  # 傾斜面入射地面反射日射量
            self.Iw = 0.0  # 傾斜面入射全日射量
            self.Fs = None  # 傾斜面の天空に対する形態係数
            self.__dblFg = 0.0  # 傾斜面の地面に対する形態係数

    # 傾斜面日射量の計算
    # ※注意※　太陽位置の情報を保持するクラス'defSolpos'の定義に従って以下の処理を修正する必要があります
    def update_slop_sol(self, solpos: defSolpos, Idn: float, Isky: float):
        """
        :param solpos: 太陽位置の情報
        :param Idn: 法線面直達日射量[W/m2]
        :param Isky: 水平面天空日射量[W/m2]
        """
        # 外皮の場合
        if self.__Skin == True:
            # 入射角の計算
            self.CosT = max(solpos.Sh * self.__Wz + solpos.Sw * self.__Ww + solpos.Ss * self.__Ws, 0.0)
            Ihol = solpos.Sh * Idn + Isky  # 水平面全天日射量
            self.Id = self.CosT * Idn  # 傾斜面直達日射量
            self.Is = self.Fs * Isky  # 傾斜面天空日射量
            self.Ir = self.__dblFg * self.__Rg * Ihol  # 傾斜面地面反射日射量
            self.Iw = self.Id + self.Is + self.Ir  # 傾斜面全日射量

    # 傾斜面の相当外気温度の計算
    def get_Te(self, _as, ho, e, Ta, RN, Tr):
        """
        :param _as: 日射吸収率 [-]
        :param ho: 外表面の総合熱伝達率[W/m2K]
        :param e: 外表面の放射率[-]
        :param Ta: 外気温度[℃]
        :param RN: 夜間放射量[W/m2]
        :param Tr: 前時刻の自室室温[℃]（隣室温度計算用）
        :return: 傾斜面の相当外気温度 [℃]
        """
        if self.__Skin:
            Te = Ta + (_as * self.Iw - self.Fs * e * RN) / ho
        else:
            Te = self.__R * Ta + (1.0 - self.__R) * Tr

        return Te


# 外表面情報インスタンスの辞書を作成
def create_exsurfaces(d):
    dic = {}
    for d_surface in d:
        name = d_surface['Name']
        dic[name] = Exsrf(
            name=name,
            DirectionAngle=d_surface['DirectionAngle'],
            InclinationAngle=d_surface['InclinationAngle'],
            GroundReflectRate=d_surface['GroundReflectRate'],
            TempDifferFactor=d_surface['TempDifferFactor'],
            IsOuterSkin=d_surface['TempDifferFactor'] is None
        )
    return dic
