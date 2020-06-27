from heat_load_calc.core.operation_mode import OperationMode
from heat_load_calc.external.psychrometrics import get_p_vs, get_x
from heat_load_calc.external.global_number import get_c_air, get_rho_air


# エアコンの熱交換部飽和絶対湿度の計算
def calcVac_xeout(Lcs, Tr, operation_mode, Vac):
    """
    :param nowAC: 当該時刻の空調運転状態（0：なし、正：暖房、負：冷房）
    :return:
    """

    # バイパスファクター
    # バイパスファクターは　0.2 とする。
    BF = 0.2

    # Lcsは加熱が正
    # 加熱時は除湿ゼロ
    # 正負を反転させる
    Qs = - Lcs

    if operation_mode in [OperationMode.STOP_OPEN, OperationMode.STOP_CLOSE] or Qs <= 1.0e-3:
        xeout = 0.0
    else:

        # --- 熱交換器温度　Teoutを求める ---

        # 熱交換器温度＝熱交換器部分吹出温度 式(113)
        Teout = Tr - Qs / (get_c_air() * get_rho_air() * Vac * (1.0 - BF))

        # 熱交換器吹出部分は飽和状態 式(115)-(118)
        xeout = get_x(get_p_vs(Teout))

    # 風量[m3/s]の計算（線形補間）

    return Vac*(1.0 - BF), xeout

