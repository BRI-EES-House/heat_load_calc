import numpy as np

from heat_load_calc.core.operation_mode import OperationMode
from heat_load_calc.external.psychrometrics import get_p_vs, get_x, get_p_vs_is2
from heat_load_calc.external.global_number import get_c_air, get_rho_air


def get_vac_xeout_is(lcs_is_n, theta_r_is_npls, operation_mode_is_n, rac_spec):
    # Lcsは加熱が正で表される。
    # 加熱時は除湿しない。
    # 以下の取り扱いを簡単にするため（冷房負荷を正とするため）、正負を反転させる
    qs_is_n = -lcs_is_n

    does_dehumidify1_is_n = np.logical_and(operation_mode_is_n == OperationMode.COOLING,
                                           qs_is_n > 1.0e-3)
    does_dehumidify2_is_n = np.logical_and(operation_mode_is_n == OperationMode.HEATING,
                                           qs_is_n > 1.0e-3)
    dh = np.logical_or(does_dehumidify1_is_n, does_dehumidify2_is_n)

    vac_is_n = np.zeros_like(operation_mode_is_n)
    vac_is_n[dh] = (
            (rac_spec['v_min'][dh] + (rac_spec['v_max'][dh] - rac_spec['v_min'][dh]) / (
                        rac_spec['q_max'][dh] - rac_spec['q_min'][dh]) * (qs_is_n[dh] - rac_spec['q_min'][dh])) / 60.0)

    BF = 0.2

    Teout_is = np.zeros_like(operation_mode_is_n, dtype=float)
    # 熱交換器温度＝熱交換器部分吹出温度 式(113)
    Teout_is[dh] = theta_r_is_npls[dh] - qs_is_n[dh] / (get_c_air() * get_rho_air() * vac_is_n[dh] * (1.0 - BF))

    xeout_is_n = np.zeros_like(operation_mode_is_n, dtype=float)

    xeout_is_n[dh] = get_x(get_p_vs_is2(Teout_is[dh]))

    vac_is_n = vac_is_n * (1 - BF)

    return np.array(vac_is_n), np.array(xeout_is_n)
