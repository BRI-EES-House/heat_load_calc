import math
import datetime
import common


# 太陽位置を計算するクラス
class defSolpos:
    """VBA では、mdlDefine モジュールにあったものを、モジュール　SolarPosision で記述することにした。"""

    def __init__(self, Sh, Sw, Ss, h, A):
        """
        :param Sh: sin(h)
        :param Sw: cos(h)*sin(A)
        :param Ss: cos(h)*cos(A)
        :param h: 太陽高度[rad]
        :param A: 太陽方位角[rad]
        """
        self.Sh = Sh  # sin h
        self.Sw = Sw  # cos h sin A
        self.Ss = Ss  # cos h cos A
        self.h = h  # 太陽高度
        self.A = A  # 太陽方位角


def get_d0(lngN):
    return 3.71 + 0.2596 * lngN - int((lngN + 3.0) / 4.0)


# 均時差の計算
def get_Et(dtmDate, coeff, d0, SinD0, lngN):
    # 通日の計算
    nday = common.get_nday(dtmDate.month, dtmDate.day)

    # 平均近点離角Mの計算
    M = coeff * (nday - d0)

    # 近日点と冬至点の角度
    dble = 12.3901 + 0.0172 * (lngN + M / 360.0)

    # 真近点離角の計算
    dblV = M + 1.914 * math.sin(math.radians(M)) + 0.02 * math.sin(math.radians(M * 2.0))

    dblRad2VE = math.radians(dblV + dble)

    # 赤緯の正弦
    dblSinD = math.cos(dblRad2VE) * SinD0

    # 赤緯の余弦
    dblCosD = math.sqrt(1.0 - dblSinD * dblSinD)

    # 中心差による時差
    dblEt1 = M - dblV

    # 太陽赤経と太陽黄経の差
    dblRad2VE = dblRad2VE * 2.0
    dblEt2 = math.degrees(math.atan(0.043 * math.sin(dblRad2VE) / (1.0 - 0.043 * math.cos(dblRad2VE))))

    return dblSinD, dblCosD, dblEt1 - dblEt2


# 太陽位置を計算する
def get_solpos(dtmDate, coeff, d0, SinD0, CosPhi, SinPhi, LLs, lngN) -> defSolpos:
    # 標準時の計算
    dblTm = dtmDate.hour + dtmDate.minute / 60.0 + dtmDate.second / 3600.0

    # 均時差の計算
    dblSinD, dblCosD, dblEt = get_Et(dtmDate, coeff, d0, SinD0, lngN)

    # 時角の計算
    dblT = math.radians(15.0 * (dblTm - 12.0) + math.degrees(LLs) + dblEt)

    # 太陽位置の計算
    dblSh = max(SinPhi * dblSinD + CosPhi * dblCosD * math.cos(dblT), 0.0)

    # print('Sh', dblSh)

    # 太陽高度
    dblh = math.asin(dblSh)
    if dblSh > 0.:
        dblCosh = math.sqrt(1.0 - dblSh * dblSh)
        dblSinA = dblCosD * math.sin(dblT) / dblCosh
        dblCosA = (dblSh * SinPhi - dblSinD) / (dblCosh * CosPhi)
        dblTemp = 1.0
        if dblT < 0.0:
            dblTemp = -1.0
        dblA = dblTemp * math.acos(dblCosA)
        dblSs = dblCosh * dblCosA
        dblSw = dblCosh * dblSinA
        # print(dtmDate, 'h=', dblh, 'A=', dblA)
    else:
        dblSs = 0.0
        dblSw = 0.0
        dblA = 0.0

    return defSolpos(dblSh, dblSw, dblSs, dblh, dblA)


class SolarPosision:
    ___mconDelta0 = -23.4393  # 冬至の日赤緯
    __lngN = 1989 - 1968

    # 緯度経度を読み込み計算準備
    # 緯度、経度、標準子午線を引数として初期化する
    def __init__(self, Lat, Lon, Ls):
        """
        :param Lat: 緯度(°)
        :param Lon: 経度(°)
        :param Ls: 標準子午線(°)
        """
        dblLat = math.radians(Lat)  # 緯度
        dblLon = math.radians(Lon)  # 経度
        dblLs = math.radians(Ls)  # 標準子午線

        # 地域情報の初期化
        self.__dblCosPhi = math.cos(dblLat)
        self.__dblSinPhi = math.sin(dblLat)
        self.__dblLLs = dblLon - dblLs
        self.__dblSinD0 = math.sin(math.radians(self.___mconDelta0))
        self.__dblCoeff = 360.0 / 365.2596

        # 平均軌道上の近日点通過日（暦表時による1968年1月1日正午基準日差）
        self.__d0 = get_d0(self.__lngN)

    # 太陽位置を計算する
    def get_solpos(self, dtmDate) -> defSolpos:
        return get_solpos(dtmDate, self.__dblCoeff, self.__d0, self.__dblSinD0, self.__dblCosPhi, self.__dblSinPhi,
                          self.__dblLLs, self.__lngN)
