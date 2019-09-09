from Psychrometrics import Pws, x
from common import conca, conrowa
from Space import Space

"""
付録16．	ルームエアコン吹出絶対湿度の計算
"""

# エアコンの熱交換部飽和絶対湿度の計算
def calcVac_xeout(space: Space, nowAC: bool):
    """
    :param space:
    :param nowAC: 当該時刻の空調運転状態（0：なし、正：暖房、負：冷房）
    :return:
    """
    # Lcsは加熱が正
    # 加熱時は除湿ゼロ
    Qs = get_Qs(space.Lcs)

    if nowAC == 0 or Qs <= 1.0e-3:
        space.Vac = 0.0
        space.Ghum = 0.0
        space.Lcl = 0.0
        return
    else:

        Ghum = space.Ghum
        Lcl = space.Lcl

        # --- 熱交換器温度　Teoutを求める ---

        # 風量[m3/s]の計算（線形補間）
        Vac = get_Vac(Qs, space.Vmin, space.Vmax, space.qmin_c, space.qmax_c)

        # バイパスファクターBF 式(114)
        BF = get_BF()

        # 熱交換器温度＝熱交換器部分吹出温度 式(113)
        Teout = get_Teout(Qs=Qs, Tr=space.Tr, Vac=Vac, BF=BF)

        # 熱交換器吹出部分は飽和状態 式(115)-(118)
        xeout = x(Pws(Teout))

    space.Vac = Vac
    space.Teout = Teout
    space.xeout = xeout
    space.Ghum = Ghum
    space.Lcl = Lcl

    # 風量[m3/s]の計算（線形補間）


def get_Qs(Lcs):
    return - Lcs


def get_Vac(Qs, Vmin, Vmax, qmin_c, qmax_c):
    return ((Vmin + (Vmax - Vmin)
            / (qmax_c - qmin_c) * (Qs - qmin_c)) / 60.0)


# 熱交換器温度＝熱交換器部分吹出温度 式(113)
def get_Teout(Qs, Tr, Vac, BF):
    return Tr - Qs / (conca * conrowa * Vac * (1.0 - BF))


# バイパスファクターBF 式(114)
def get_BF():
    return 0.2