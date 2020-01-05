import math
import numpy as np


def get_t_cl_i_n(clo_i_n, h_c_i_n, h_r_i_n, ot_i_n):
    """着衣温度を計算する。
    
    Args:
        clo_i_n: ステップnの室iにおけるClo値
        h_c_i_n: ステップnの室iにおける人体周りの対流熱伝達率, W/m2K
        h_r_i_n: ステップnの室iにおける人体周りの放射熱伝達率, W/m2K
        ot_i_n: ステップnの室iにおける作用温度, degree C

    Returns:
        ステップnの室iにおける着衣温度, degree C
    """

    # 着衣抵抗, m2K/W
    i_cl = convert_clo_to_m2kw(clo_i_n)

    # 着衣面積率
    f_cl = get_f_cl(i_cl)

    # 代謝量（人体内部発熱量）, W/m2
    m = get_met()

    # ステップnの室iにおける人体周りの総合熱伝達率, W/m2K
    h_a_i_n = h_c_i_n + h_r_i_n

    # ステップnの室iにおける着衣温度, degree C
    t_cl_i_n = (35.7 - 0.028 * m - ot_i_n) / (1 + i_cl * f_cl * h_a_i_n) + ot_i_n

    return t_cl_i_n


def get_h_hum_r_is_n(theta_cl_is_n: np.ndarray, theta_mrt_is_n: np.ndarray) -> np.ndarray:
    """人体周りの放射熱伝達率を計算する。
    
    Args:
        theta_cl_is_n: ステップnの室iにおける着衣温度, degree C, [i]
        theta_mrt_is_n: ステップnの室iにおける平均放射温度, degree C, [i]

    Returns:
        ステップnの室iにおける人体周りの放射熱伝達率, W/m2K, [i]
    """

    # ステップnの室iにおける着衣温度, K, [i]
    t_cl_is_n = theta_cl_is_n + 273.0

    # ステップnの室iにおける平均放射温度, K, [i]
    t_mrt_is_n = theta_mrt_is_n + 273.0

    return 3.96 * 10 ** (-8) * (t_cl_is_n ** 3.0 + t_cl_is_n ** 2.0 * t_mrt_is_n + t_cl_is_n * t_mrt_is_n ** 2.0 + t_mrt_is_n)


def get_h_hum_c_is_n(theta_r_is_n: np.ndarray, t_cl_is_n: np.ndarray, v_hum_is_n: np.ndarray) -> np.ndarray:
    """人体周りの対流熱伝達率を計算する。

    Args:
        theta_r_is_n: ステップnの室iにおける室温, degree C, [i]
        t_cl_is_n: ステップnの室iにおける着衣温度, degree C, [i]
        v_hum_is_n: ステップnの室iにおける人体周りの風速, m/s, [i]

    Returns:
        ステップnの室iにおける人体周りの対流熱伝達率, W/m2K
    """

    return np.maximum(12.1 * np.sqrt(v_hum_is_n), 2.38 * np.abs(t_cl_is_n - theta_r_is_n) ** 0.25)


def get_h_hum_is_n(h_hum_r_is_n: np.ndarray, h_hum_c_is_n: np.ndarray) -> np.ndarray:
    """人体周りの対流熱伝達率を計算する。

    Args:
        h_hum_r_is_n: ステップnの室iにおける人体周りの放射熱伝達率, W/m2K, [i]
        h_hum_c_is_n: ステップnの室iにおける人体周りの対流熱伝達率, W/m2K, [i]

    Returns:
        ステップnの室iにおける人体周りの総合熱伝達率, W/m2K, [i]
    """

    return h_hum_r_is_n + h_hum_c_is_n


def get_pmv(h_c, t_a, t_cl, t_r_bar, clo_value, h_r, p_a, h, ot):
    """PMVを計算する

    Args:
        h_c: 対流熱伝達率, W/m2K
        t_a: 乾球温度, degree C
        t_cl: 着衣温度, degree C
        t_r_bar: 放射温度, degree C
        clo_value: Clo値
        h_r: 放射熱伝達率, W/m2K
        p_a:　水蒸気圧, Pa

    Returns:
        PMV: PMV

    Notes:
        ISOで定める計算方法ではなく、前の時刻に求めた人体周りの熱伝達率、着衣温度を使用して収束計算が生じないようにしている。

    """

    # 着衣抵抗, m2K/W
    i_cl = convert_clo_to_m2kw(clo_value)

    # 代謝量（人体内部発熱量）, W/m2
    m = get_met()

    # 着衣面積率
    f_cl = get_f_cl(i_cl)

    ot = (h_r * t_r_bar + h_c * t_a)/h

    return (0.303 * math.exp(-0.036 * m) + 0.028) * (
            m  # 活動量, W/m2
            - 3.05 * 10 ** (-3) * (5733.0 - 6.99 * m - p_a)  # 皮膚からの潜熱損失, W/m2
            - max(0.42 * (m - 58.15), 0.0)  # 発汗熱損失, W/m2
            - 1.7 * 10 ** (-5) * m * (5867.0 - p_a)  # 呼吸に伴う潜熱損失, W/m2
            - 0.0014 * m * (34.0 - t_a)  # 呼吸に伴う顕熱損失, W/m2 ( = 呼吸量, (g/s)/m2 ✕ (34.0 - 室温)
            - f_cl * h * (t_cl - ot))  # 着衣からの熱損失


def convert_clo_to_m2kw(clo):
    """convert the unit of clo to m2K/W

    Args:
        clo: value, clo

    Returns:
        value, m2K/W

    Notes:
        1 clo = 0.155 m2K/W
    """

    return clo * 0.155


def get_met():
    """代謝量を得る。

    Returns:
        代謝量, W/m2

    Notes:
        代謝量は1.0 met に固定とする。
        1.0 met は、ISOにおける、Resting - Seated, quiet に相当
        1 met = 58.15 W/m2
    """

    return 58.15


def get_f_cl(i_cl: float) -> float:
    """着衣面積率を計算する。

    Args:
        i_cl: 着衣抵抗, m2K/W

    Returns:
        着衣面積率

    Notes:
        equation (4)
    """

    if i_cl <= 0.078:
        return 1.00 + 1.290 * i_cl
    else:
        return 1.05 + 0.645 * i_cl

