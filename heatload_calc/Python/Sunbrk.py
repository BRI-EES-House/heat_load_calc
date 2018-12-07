import math
from SolarPosision import defSolpos


# 水平庇の物理的な長さを保持するクラス
class SunbrkType:
    def __init__(self, Name, D, WI1, WI2, hi, WR, WH):
        """
        :param Name: 日除け名称
        :param D: 庇の出巾[m]
        :param WI1: 向かって左側の庇のでっぱり[m]
        :param WI2: 向かって右側の庇のでっぱり[m]
        :param hi: 窓上端と庇までの距離[m]
        :param WR: 開口部巾[m]
        :param WH: 開口部高さ[m]
        """
        self.Name = Name  # 日除け名称
        self.D = float(D)  # 庇の出巾
        self.WI1 = float(WI1)  # 向かって左側の庇のでっぱり
        self.WI2 = float(WI2)  # 向かって右側の庇のでっぱり
        self.hi = float(hi)  # 窓上端から庇までの距離
        self.WR = float(WR)  # 開口部巾
        self.WH = float(WH)  # 開口部高さ
        self.A = self.WR * self.WH  # 開口部面積

    # 日除けの影面積を計算する
    def get_Fsdw(self, defSolpos: defSolpos, Wa: float):
        """
        :param defSolpos: 太陽位置
        :param Wa: 庇の設置してある窓の傾斜面方位角[rad]
        :return: 日除けの影面積
        """
        # γの計算[rad]
        dblGamma = defSolpos.A - Wa
        # tan(プロファイル角)の計算
        dblTanFai = math.tan(defSolpos.h / math.cos(dblGamma))

        # 日が出ているときだけ計算する
        if defSolpos.h > 0.0:
            # DPの計算[m]
            dblDP = self.D * dblTanFai

            # DAの計算
            dblDA = self.D * math.tan(dblGamma)
            dblABSDA = abs(dblDA)

            # WIの計算
            if dblDA > 0.:
                dblWI = self.WI1
            else:
                dblWI = self.WI2

            # DHAの計算
            dblDHA = min([max([0., dblWI * dblDP / max([dblWI, dblABSDA]) - self.hi]), self.WH])

            # DHBの計算
            dblDHB = min([max([0., (dblWI + self.WR) * dblDP \
                               / max([dblWI + self.WR, dblABSDA]) - self.hi]), self.WH])

            # DWAの計算
            if dblDP <= self.hi:
                dblDWA = 0.
            else:
                dblDWA = min([max([0., (dblWI + self.WR) - self.hi * dblABSDA / dblDP]), self.WR])

            # DWBの計算
            dblDWB = min([max([0., (dblWI + self.WR) - (self.hi + self.WH) * dblABSDA / \
                               max([self.hi + self.WH, dblDP])]), self.WR])

            # 日影面積の計算
            dblASDW = dblDWA * dblDHA + 0.5 * (dblDWA + dblDWB) * (dblDHB - dblDHA)

            # 日影面積率の計算
            dblFsdw = dblASDW / self.A
        else:
            dblFsdw = 0.0

        return dblFsdw


def create_sunbrks(d):
    dic = {}
    for d_sunbrk in d:
        name = d_sunbrk['Name']
        dic[name] = SunbrkType(**d_sunbrk)
    return dic
