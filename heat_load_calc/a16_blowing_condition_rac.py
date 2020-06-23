from heat_load_calc.core.operation_mode import OperationMode
from heat_load_calc.external import psychrometrics as psy
from heat_load_calc.external.psychrometrics import get_p_vs, get_x
from heat_load_calc.external.global_number import get_c_air, get_rho_air


# エアコンの熱交換部飽和絶対湿度の計算
def calcVac_xeout(Lcs, Vmin, Vmax, qmin_c, qmax_c, Tr, operation_mode):
    """
    :param nowAC: 当該時刻の空調運転状態（0：なし、正：暖房、負：冷房）
    :return:
    """

    BF = get_BF()

    # Lcsは加熱が正
    # 加熱時は除湿ゼロ
    Qs = get_Qs(Lcs)

    if operation_mode in [OperationMode.STOP_OPEN, OperationMode.STOP_CLOSE] or Qs <= 1.0e-3:
        Vac = 0.0
        xeout = 0.0
    else:

        # --- 熱交換器温度　Teoutを求める ---

        # 風量[m3/s]の計算（線形補間）
        Vac = get_Vac(Qs, Vmin, Vmax, qmin_c, qmax_c)

        # 熱交換器温度＝熱交換器部分吹出温度 式(113)
        Teout = get_Teout(Qs=Qs, Tr=Tr, Vac=Vac, BF=BF)

        # 熱交換器吹出部分は飽和状態 式(115)-(118)
        xeout = get_x(get_p_vs(Teout))

    # 風量[m3/s]の計算（線形補間）

    return Vac*(1.0 - BF), xeout


def get_Qs(Lcs):
    return - Lcs


def get_Vac(Qs, Vmin, Vmax, qmin_c, qmax_c):
    return ((Vmin + (Vmax - Vmin)
             / (qmax_c - qmin_c) * (Qs - qmin_c)) / 60.0)


# 熱交換器温度＝熱交換器部分吹出温度 式(113)
def get_Teout(Qs, Tr, Vac, BF):
    rhoa = get_rho_air()
    ca = get_c_air()
    return Tr - Qs / (ca * rhoa * Vac * (1.0 - BF))


# バイパスファクターBF 式(114)
def get_BF():
    return 0.2

