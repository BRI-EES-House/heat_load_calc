from Psychrometrics import Pws, x
import a18_initial_value_constants as a18

"""
付録16．	ルームエアコン吹出絶対湿度の計算
"""


# エアコンの熱交換部飽和絶対湿度の計算
def calcVac_xeout(Lcs, Vmin, Vmax, qmin_c, qmax_c, Tr, BF, nowAC: bool):
    """
    :param nowAC: 当該時刻の空調運転状態（0：なし、正：暖房、負：冷房）
    :return:
    """
    # Lcsは加熱が正
    # 加熱時は除湿ゼロ
    Qs = get_Qs(Lcs)

    if nowAC == 0 or Qs <= 1.0e-3:
        Vac = 0.0
        xeout = 0.0
    else:

        # --- 熱交換器温度　Teoutを求める ---

        # 風量[m3/s]の計算（線形補間）
        Vac = get_Vac(Qs, Vmin, Vmax, qmin_c, qmax_c)

        # 熱交換器温度＝熱交換器部分吹出温度 式(113)
        Teout = get_Teout(Qs=Qs, Tr=Tr, Vac=Vac, BF=BF)

        # 熱交換器吹出部分は飽和状態 式(115)-(118)
        xeout = x(Pws(Teout))

    # 風量[m3/s]の計算（線形補間）

    return Vac, xeout


def get_Qs(Lcs):
    return - Lcs


def get_Vac(Qs, Vmin, Vmax, qmin_c, qmax_c):
    return ((Vmin + (Vmax - Vmin)
             / (qmax_c - qmin_c) * (Qs - qmin_c)) / 60.0)


# 熱交換器温度＝熱交換器部分吹出温度 式(113)
def get_Teout(Qs, Tr, Vac, BF):
    rhoa = a18.get_rho_air()
    ca = a18.get_c_air()
    return Tr - Qs / (ca * rhoa * Vac * (1.0 - BF))


# バイパスファクターBF 式(114)
def get_BF():
    return 0.2
