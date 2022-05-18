from typing import Callable, Tuple
import numpy as np
from functools import partial

from heat_load_calc.core.operation_mode import OperationMode


def make_get_next_temp_and_load_function(
        ac_demand_is_ns: np.ndarray,
        is_radiative_heating_is: np.ndarray,
        is_radiative_cooling_is: np.ndarray,
        lr_h_max_cap_is: np.ndarray,
        lr_cs_max_cap_is: np.ndarray
) -> Callable[[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray, np.ndarray]]:

    return partial(
        get_next_temp_and_load,
        ac_demand_is_ns=ac_demand_is_ns,
        is_radiative_heating_is=is_radiative_heating_is,
        is_radiative_cooling_is=is_radiative_cooling_is,
        lr_h_max_cap_is=lr_h_max_cap_is,
        lr_cs_max_cap_is=lr_cs_max_cap_is
    )


def get_next_temp_and_load(
        ac_demand_is_ns: np.ndarray,
        brc_ot_is_n: np.ndarray,
        brm_ot_is_is_n: np.ndarray,
        brl_ot_is_is_n: np.ndarray,
        theta_lower_target_is_n: np.ndarray,
        theta_upper_target_is_n: np.ndarray,
        operation_mode_is_n: np.ndarray,
        is_radiative_heating_is: np.ndarray,
        is_radiative_cooling_is: np.ndarray,
        lr_h_max_cap_is: np.ndarray,
        lr_cs_max_cap_is: np.ndarray,
        theta_natural_is_n: np.ndarray,
        is_heating_is_n: np.ndarray,
        is_cooling_is_n: np.ndarray,
        n: int
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:

    ac_demand_is_n = ac_demand_is_ns[:, n].reshape(-1, 1)

    # 室の配列の形, i✕1　の行列 を表すタプル
    room_shape = operation_mode_is_n.shape

    # 室の数
    n_room = room_shape[0]

    # 係数　kt, W / K, [i, i], float型
    kt = brm_ot_is_is_n

    # 係数 kc, [i, i], float型
    kc = np.identity(n_room, dtype=float)

    # 係数 kr, [i, i], float型
    kr = brl_ot_is_is_n

    # 係数 k, W, [i, 1], float型
    k = brc_ot_is_n

    # 実際に暖房が行われるかどうか。
#    is_heating = (operation_mode_is_n == OperationMode.HEATING) & (theta_natural_is_n < theta_lower_target_is_n)
#    is_cooling = (operation_mode_is_n == OperationMode.COOLING) & (theta_upper_target_is_n < theta_natural_is_n)
    is_heating = is_heating_is_n
    is_cooling = is_cooling_is_n

    # 室温指定を表す係数, [i, 1], int型
    # 指定する = 0, 指定しない = 1
    # 室温を指定しない場合は、 operation_mode が STOP_CLOSE or STOP_OPEN の場合である。
    # 後で再計算する際に、負荷が機器容量を超えている場合は、最大暖房／冷房負荷で処理されることになるため、
    # 室温を指定しない場合は、この限りではない。
#    nt = np.zeros(room_shape, dtype=int)
#    nt[operation_mode_is_n == OperationMode.STOP_CLOSE] = 1
#    nt[operation_mode_is_n == OperationMode.STOP_OPEN] = 1
    nt = np.full(room_shape, 1, dtype=int)
    nt[is_heating] = 0
    nt[is_cooling] = 0

    # nt = 0 （室温を指定する） に対応する要素に、ターゲットとなるOTを代入する。
    # nt = 1 （室温を指定しない）場合は、theta_set は 0 にしなければならない。
    theta_set = np.zeros(room_shape, dtype=float)
    theta_set[is_heating] = theta_lower_target_is_n[is_heating] * ac_demand_is_n[is_heating] \
        + theta_natural_is_n[is_heating] * (1.0 - ac_demand_is_n[is_heating])
    theta_set[is_cooling] = theta_upper_target_is_n[is_cooling] * ac_demand_is_n[is_cooling] \
        + theta_natural_is_n[is_cooling] * (1.0 - ac_demand_is_n[is_cooling])

    # 対流空調指定を表す係数, [i, 1], int型
    # 指定する = 0, 指定しない = 1
    # 対流空調を指定しない場合は、対流空調をしている場合に相当するので、
    #   operation_mode が　HEATING でかつ、 is_radiative_heating_is が false の場合か、
    #   operation_mode が COOLING でかつ、 is_radiative_cooling_is が false の場合
    # のどちらかである。
    c = np.zeros(room_shape, dtype=int)
#    c[(operation_mode_is_n == OperationMode.HEATING) & (np.logical_not(is_radiative_heating_is))] = 1
#    c[(operation_mode_is_n == OperationMode.COOLING) & (np.logical_not(is_radiative_cooling_is))] = 1
    c[is_heating & (np.logical_not(is_radiative_heating_is))] = 1
    c[is_cooling & (np.logical_not(is_radiative_cooling_is))] = 1

    # c = 0 （対流空調を指定する）に対応する要素に、0.0 を代入する。
    # 対流空調を指定する場合は空調をしていないことに相当するため。ただし、後述する、最大能力で動く場合は、その値を代入することになる。
    # 対流空調を指定しない場合は、 lc_set には 0.0 を入れなければならない。
    # 結果として、ここでは、あらゆるケースで 0.0 が代入される。
    lc_set = np.zeros(room_shape, dtype=float)

    # 放射空調指定を表す係数, [i, 1], int型
    # 指定する = 0, 指定しない = 1
    # 放射空調を指定しない場合は、放射空調をしている場合に相当するので、
    #   operation_mode が　HEATING でかつ、 is_radiative_heating_is が true の場合か、
    #   operation_mode が COOLING でかつ、 is_radiative_cooling_is が true の場合
    # のどちらかである。
    r = np.zeros(room_shape, dtype=int)
#    r[(operation_mode_is_n == OperationMode.HEATING) & is_radiative_heating_is] = 1
#    r[(operation_mode_is_n == OperationMode.COOLING) & is_radiative_cooling_is] = 1
    r[is_heating & is_radiative_heating_is] = 1
    r[is_cooling & is_radiative_cooling_is] = 1

    # r = 0 （放射空調を指定する）に対応する要素に、0.0 を代入する。
    # 放射空調を指定する場合は空調をしていないことに相当するため。ただし、後述する、最大能力で動く場合は、その値を代入することになる。
    # 放射空調を指定しない場合は、 lr_set には 0.0 を入れなければならない。
    # 結果として、ここでは、あらゆるケースで 0.0 が代入される。
    lr_set = np.zeros(room_shape, dtype=float)

    # theta 温度, degree C, [i, 1]
    # lc 対流空調負荷, W, [i, 1]
    # lr 放射空調負荷, W, [i, 1]
    theta, lc, lr = get_load_and_temp(kt, kc, kr, k, nt, theta_set, c, lc_set, r, lr_set)

    # 計算された放射空調負荷が最大放熱量を上回る場合は、放熱量を最大放熱量に固定して、対流空調負荷を未知数として再計算する。
    over_lr = lr > lr_h_max_cap_is

    # 対流負荷を未知数とする。
    c[over_lr] = 1

    # 放射負荷を最大放熱量に指定する。
    r[over_lr] = 0
    lr_set[over_lr] = lr_h_max_cap_is[over_lr]

    # 計算された放射空調負荷が最大放熱量を下回る場合は、放熱量を最大放熱量に固定して、対流空調負荷を未知数として再計算する。
    # 注意：冷房の最大放熱量は正の値で指定される。一方、計算される負荷（lr）は、冷房の場合、負の値で指定される。
    under_lr = lr < -lr_cs_max_cap_is

    # 対流負荷を未知数とする。
    c[under_lr] = 1

    # 放射負荷を最大放熱量に指定する。
    r[under_lr] = 0
    lr_set[under_lr] = -lr_cs_max_cap_is[under_lr]

    # 放射暖房を最大放熱量に指定して再計算する。
    theta, lc, lr = get_load_and_temp(kt, kc, kr, k, nt, theta_set, c, lc_set, r, lr_set)

    return theta, lc, lr


def get_load_and_temp(
    kt: np.ndarray,
    kc: np.ndarray,
    kr: np.ndarray,
    k: np.ndarray,
    nt: np.ndarray,
    theta_set: np.ndarray,
    c: np.ndarray,
    lc_set: np.ndarray,
    r: np.ndarray,
    lr_set: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """

    Args:
        kt: 係数 kt, W/K, [i, i], float型
        kc: 係数 kc, [i, i], float型
        kr: 係数 kr, [i, i], float型
        k: 係数 k, W, [i, 1], float型
        nt: 室温指定を表す係数, [i, 1], int型
        theta_set: 室温を指定する場合の室温, degree C, [i, 1], float型
        c: 対流空調指定を表す係数, [i, 1], int型
        lc_set: 対流空調を指定する場合の放熱量, W, [i, 1], float型
        r: 放射空調指定を表す係数, [i, 1], int型
        lr_set: 放射空調を指定する場合の放熱量, W, [i, 1], float型

    Returns:
        温度, degree C, [i, 1]
        対流空調負荷, W, [i, 1]
        放射空調負荷, W, [i, 1]

    Notes:
        各係数によって、
        kt theta = kc Lc + kr Lr + k
        が維持される。

        室温・対流空調・放射空調 を指定する場合は、指定しない = 1, 指定する = 0 とする。
        theta_set, lc_set, lr_set について、指定しない場合は必ず 0.0 とする。
    """

    # 室温を指定しない場合 nt = 1
    # 室温を指定しない場合 theta_set は 0.0 とする。
    theta_set[nt == 1] = 0.0

    # 対流空調負荷を指定しない場合 c = 1
    # 対流空調負荷を指定しない場合 lc_set = 0.0 とする。
    lc_set[c == 1] = 0.0

    # 放射空調負荷を指定しない場合 r = 1
    # 放射空調負荷を指定しない場合 lr_set = 0.0 とする。
    lr_set[r == 1] = 0.0

    # 左辺を未知数、右辺を既知数とし
    # X1 (theta + Lc + Lr) = X2
    # とした時の　係数 X1 と 係数 X2 を求める。
    # X1, X2 は、[i, i] のベクトル、 theta, Lc, Lr は、[i, 1] の縦ベクトル。
    x1 = kt * nt.T - kc * c.T - kr * r.T
    x2 = -np.dot(kt, theta_set) + np.dot(kc, lc_set) + np.dot(kr, lr_set) + k

    # V = theta + Lc + Lr
    # とすると、
    # X1 V = X2
    # V = X1^-1 X2
    # となる。 V は [i, 1] の縦ベクトル。
    v = np.dot(np.linalg.inv(x1), x2)

    # 求めるべき数値
    # nt, c, r それぞれ、1の場合（値を指定しない場合）は、vで表される値が入る。
    # 反対に、 0 の場合（値を指定する場合）、は、それぞれ、theta_set, lc_set, lr_set の値が入る。
    theta_rq = v * nt + theta_set * (1 - nt)
    lc_rq = v * c + lc_set * (1 - c)
    lr_rq = v * r + lr_set * (1 - r)

    return theta_rq, lc_rq, lr_rq
