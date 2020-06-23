from psychrometrics import get_p_vs, get_x
import a18_initial_value_constants as a18
from a39_global_parameters import OperationMode


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
    rhoa = a18.get_rho_air()
    ca = a18.get_c_air()
    return Tr - Qs / (ca * rhoa * Vac * (1.0 - BF))


# バイパスファクターBF 式(114)
def get_BF():
    return 0.2

# 式(20)のうちの一部
def get_RhoVac(Vac: float):

    rhoa = a18.get_rho_air()
    return rhoa * Vac