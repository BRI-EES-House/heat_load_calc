import math
from SolarPosision import defSolpos

# 水平庇の物理的な長さを保持するクラス
class SunbrkType:
    def __init__(self, d_sun_break):
        """
        :param Name: 日除け名称
        :param D: 庇の出巾[m]
        :param WI1: 向かって左側の庇のでっぱり[m]
        :param WI2: 向かって右側の庇のでっぱり[m]
        :param hi: 窓上端と庇までの距離[m]
        :param WR: 開口部巾[m]
        :param WH: 開口部高さ[m]
        """
        # 日除けの有無（True:あり）
        self.existance = d_sun_break['existence']

        # 日除けがある場合のみ
        if self.existance:
            # 入力方法
            self.__input_method = d_sun_break['input_method']

            # 簡易入力の場合
            if self.__input_method == 'simple':
                # 出幅
                self.__depth = d_sun_break['depth']
                # 窓の高さ
                self.__d_h = d_sun_break['d_h']
                # 窓の上端から庇までの距離
                self.__d_e = d_sun_break['d_e']
            # 詳細入力の場合
            elif self.__input_method == 'detailed':
                #庇水平方向の出（左）
                self.__x1 = d_sun_break['x1']
                #窓幅
                self.__x2 = d_sun_break['x2']
                #庇水平方向の出（右）
                self.__x3 = d_sun_break['x3']
                #上部庇の窓上端からの距離
                self.__y1 = d_sun_break['y1']
                #窓高さ
                self.__y2 = d_sun_break['y2']
                #下部庇の窓下端からの距離
                self.__y3 = d_sun_break['y3']
                #側壁右の出幅
                self.__z_x_pls = d_sun_break['z_x_pls']
                #上部庇の出幅
                self.__z_y_pls = d_sun_break['z_y_pls']
                #下部庇の出幅
                self.__z_y_mns = d_sun_break['z_y_mns']

    # 日除けの影面積を計算する（当面、簡易入力のみに対応）
    def get_Fsdw(self, defSolpos: defSolpos, Wa: float):
        """
        :param defSolpos: 太陽位置
        :param Wa: 庇の設置してある窓の傾斜面方位角[rad]
        :return: 日除けの影面積
        """
        # γの計算[rad]
        gamma = defSolpos.A - Wa
        # tan(プロファイル角)の計算
        tan_fai = math.tan(defSolpos.h) / math.cos(gamma)

        # 日が出ているときだけ計算する
        if defSolpos.h > 0.0:
            # DPの計算[m]
            dblDP = self.__depth * tan_fai
            # DH'の計算[m]
            dblDHd = dblDP - self.__d_e
            #DHの計算[m]
            dblDH = min(max(0.0, dblDHd), self.__d_h)

            # 日影面積率の計算
            dblFsdw = dblDH / self.__d_h
        else:
            dblFsdw = 0.0

        return dblFsdw
