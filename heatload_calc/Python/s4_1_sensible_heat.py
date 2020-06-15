import numpy as np

import a18_initial_value_constants as a18
from a39_global_parameters import OperationMode


# ********** （1）式から作用温度、室除去熱量を計算する方法 **********

# TODO: 空調運転モード3,4については未定義


# 自然室温を計算 式(14)
def get_Tr_i_n(OT, Lrs, Xot, XLr, XC):
    return Xot * OT - XLr * Lrs - XC


# 家具の温度 式(15)
def get_Tfun_i_n(Capfun, Tfun_i_n_m1, Cfun, Tr, Qsolfun):
    """

    :param Capfun: i室の家具の熱容量（付録14．による） [J/K]
    :param Tfun_i_n_m1: i室の家具の15分前の温度 [℃]
    :param Cfun: i室の家具と室空気間の熱コンダクタンス（付録14．による）
    :param Tr: 室温 [℃]
    :param Qsolfun: i室のn時点における家具の日射吸収熱量 [W]
    :return: 家具の温度 [℃]
    """

    delta_t = a18.get_delta_t()

#    if Capfun > 0.0:
#        return (Capfun / delta_t * Tfun_i_n_m1 + Cfun * Tr + Qsolfun) / (Capfun / delta_t + Cfun)
#    else:
#        return 0.0
    return np.where(Capfun > 0.0, (Capfun / delta_t * Tfun_i_n_m1 + Cfun * Tr + Qsolfun) / (Capfun / delta_t + Cfun), 0.0)


def get_Qfuns(Cfun, Tr, Tfun):
    """

    :param Cfun: i室の家具と室空気間の熱コンダクタンス（付録14．による）
    :param Tr:
    :param Tfun: i室の家具の温度 [℃]
    :return:
    """
    return Cfun[:, np.newaxis] * (Tr - Tfun)


def calc_next_temp_and_load(
        is_radiative_heating_is, brc_ot_is_n, brm_ot_is_is_n, brl_ot_is_is_n, theta_ot_target_is_n, lrcap_is, operation_mode_is_n):

    # 室の配列の形, i ✕ 1　の行列
    room_shape = theta_ot_target_is_n.shape

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

    # TODO: ここの処理は後でどうにかしないといけない
    is_radiative_cooling_is = np.full(room_shape, False)

    # 室温指定を表す係数, [i, 1], int型
    # 指定する = 0, 指定しない = 1
    # 室温を指定しない場合は、 operation_mode が STOP_CLOSE or STOP_OPEN の場合である。
    # 後で再計算する際に、負荷が機器容量を超えている場合は、最大暖房／冷房負荷で処理されることになるため、
    # 室温を指定しない場合は、この限りではない。
    nt = np.zeros(room_shape, dtype=int)
    nt[operation_mode_is_n == OperationMode.STOP_CLOSE] = 1
    nt[operation_mode_is_n == OperationMode.STOP_OPEN] = 1

    # nt = 0 （室温を指定する） に対応する要素に、ターゲットとなるOTを代入する。
    # nt = 1 （室温を指定しない）場合は、theta_set は 0 にしなければならない。
    theta_set = np.zeros(room_shape, dtype=float)
    theta_set[nt == 0] = theta_ot_target_is_n[nt == 0]

    # 対流空調指定を表す係数, [i, 1], int型
    # 指定する = 0, 指定しない = 1
    # 対流空調を指定しない場合は、対流空調をしている場合に相当するので、
    #   operation_mode が　HEATING でかつ、 is_radiative_heating_is が false の場合か、
    #   operation_mode が COOLING でかつ、 is_radiative_cooling_is が false の場合
    # のどちらかである。
    c = np.zeros(room_shape, dtype=int)
    c[(operation_mode_is_n == OperationMode.HEATING) & (np.logical_not(is_radiative_heating_is))] = 1
    c[(operation_mode_is_n == OperationMode.COOLING) & (np.logical_not(is_radiative_cooling_is))] = 1

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
    r[(operation_mode_is_n == OperationMode.HEATING) & is_radiative_heating_is] = 1
    r[(operation_mode_is_n == OperationMode.COOLING) & is_radiative_cooling_is] = 1

    # r = 0 （放射空調を指定する）に対応する要素に、0.0 を代入する。
    # 放射空調を指定する場合は空調をしていないことに相当するため。ただし、後述する、最大能力で動く場合は、その値を代入することになる。
    # 放射空調を指定しない場合は、 lr_set には 0.0 を入れなければならない。
    # 結果として、ここでは、あらゆるケースで 0.0 が代入される。
    lr_set = np.zeros(room_shape, dtype=float)

    # theta 温度, degree C, [i, 1]
    # lc 対流空調負荷, W, [i, 1]
    # lr 放射空調負荷, W, [i, 1]
    theta, lc, lr = get_load_and_temp(kt, kc, kr, k, nt, theta_set, c, lc_set, r, lr_set)

    # TODO: 放射暖房負荷が最大能力を超えたときの措置を記載していない。

    return theta, lc, lr


def get_load_and_temp(kt, kc, kr, k, nt, theta_set, c, lc_set, r, lr_set) -> (np.ndarray, np.ndarray, np.ndarray):
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
