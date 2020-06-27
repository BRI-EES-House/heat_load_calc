from heat_load_calc.core.operation_mode import OperationMode
from heat_load_calc.external.psychrometrics import get_p_vs, get_x
from heat_load_calc.external.global_number import get_c_air, get_rho_air


# エアコンの熱交換部飽和絶対湿度の計算
def calcVac_xeout(theta_r_i_npls, operation_mode_i_n, vac_i_n, qs_i_n):
    """
    :param nowAC: 当該時刻の空調運転状態（0：なし、正：暖房、負：冷房）
    :return:
    """

    # バイパスファクター
    # バイパスファクターは　0.2 とする。
    BF = 0.2

    if operation_mode_i_n in [OperationMode.STOP_OPEN, OperationMode.STOP_CLOSE] or qs_i_n <= 1.0e-3:
        xeout = 0.0
    else:

        # --- 熱交換器温度　Teoutを求める ---

        # 熱交換器温度＝熱交換器部分吹出温度 式(113)
        Teout = theta_r_i_npls - qs_i_n / (get_c_air() * get_rho_air() * vac_i_n * (1.0 - BF))

        # 熱交換器吹出部分は飽和状態 式(115)-(118)
        xeout = get_x(get_p_vs(Teout))

    # 風量[m3/s]の計算（線形補間）

    return vac_i_n * (1.0 - BF), xeout

