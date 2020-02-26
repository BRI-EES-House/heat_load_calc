import math
import numpy as np
from numba import jit

def get_h(p_v: np.ndarray, p_vs: np.ndarray) -> np.ndarray:
    """相対湿度を計算する。

    Args:
        p_v: 水蒸気圧, Pa
        p_vs: 飽和水蒸気圧, Pa

    Returns:
        相対湿度, %

    Notes:
        省エネ基準第11章「その他」第5節「湿り空気」式(1)
    """

    return p_v / p_vs * 100.0


def get_x(p_v: float) -> float:
    """水蒸気圧から絶対湿度を計算する。

    Args:
        p_v: 水蒸気圧, Pa

    Returns:
        絶対湿度, kg/kgDA

    Notes:
        省エネ基準第11章「その他」第5節「湿り空気」式(2)
        ただし、省エネ基準の式は一部間違っていると考えられる。(2020/1/5時点)
    """

    # 大気圧, Pa
    f = get_f()

    return 0.622 * p_v / (f - p_v)


def get_p_v_r_is_n(x_r_is_n: np.ndarray) -> np.ndarray:
    """絶対湿度から水蒸気圧を求める。

    Args:
        x_r_is_n: ステップnにおける室iの絶対湿度, kg/kgDA, [i]
    Returns:
        ステップnにおける室iの水蒸気圧, Pa, [i]

    Notes:
        省エネ基準第11章「その他」第5節「湿り空気」式(4)
        ただし、省エネ基準の式は絶対湿度の単位として(g/kg(DA))を使用しているが、
        ここでは、kg/kg(DA)に統一した。
    """

    # 大気圧, Pa
    f = get_f()

    return f * x_r_is_n / (x_r_is_n + 0.62198)


def get_p_vs_is(theta_is: np.ndarray) -> np.ndarray:

    return np.vectorize(get_p_vs)(theta_is)


def get_p_vs(theta: float) -> float:
    """飽和水蒸気圧を計算する。

    Args:
        theta: 空気温度, degree C

    Returns:
        飽和水蒸気圧, Pa

    Notes:
        省エネ基準
    """

    t = theta + 273.15  # 絶対温度の計算

    a_1 = -6096.9385
    a_2 = 21.2409642
    a_3 = -0.02711193
    a_4 = 0.00001673952
    a_5 = 2.433502
    b_1 = -6024.5282
    b_2 = 29.32707
    b_3 = 0.010613863
    b_4 = -0.000013198825
    b_5 = -0.49382577

    if theta >= 0.0:
        return math.exp(a_1 / t + a_2 + a_3 * t + a_4 * t ** 2 + a_5 * math.log(t))
    else:
        return math.exp(b_1 / t + b_2 + b_3 * t + b_4 * t ** 2 + b_5 * math.log(t))


def get_f() -> float:
    """大気圧を求める。

    Returns:
        大気圧, Pa
    """

    return 101325
