import math
import numpy as np
from numba import jit


def get_theta_cl_heavy_middle_light_is_n(
        theta_ot_is_n: np.ndarray, h_hum_is_n: np.ndarray) -> (np.ndarray, np.ndarray, np.ndarray):
    """厚着・中間着・薄着をした場合の着衣温度をそれぞれ計算する。

    Args:
        theta_ot_is_n: ステップnの室iにおける作用温度, degree C, [i]
        h_hum_is_n: ステップnの室iにおける人体周りの総合熱伝達率, W/m2K, [i]

    Returns:
        以下の3つの変数
            ステップnの室iにおける厚着をした場合の着衣温度, degree C, [i]
            ステップnの室iにおける中間着をした場合の着衣温度, degree C, [i]
            ステップnの室iにおける薄着をした場合の着衣温度, degree C, [i]
    """

    # 厚着・中間着・薄着をした場合のClo値
    clo_heavy, clo_middle, clo_light = get_clo()

    # 厚着・中間着・薄着をした場合の着衣温度, degree C, [i]
    theta_cl_heavy_is_n = get_theta_cl_is_n(clo=clo_heavy, theta_ot_is_n=theta_ot_is_n, h_hum_is_n=h_hum_is_n)
    theta_cl_middle_is_n = get_theta_cl_is_n(clo=clo_middle, theta_ot_is_n=theta_ot_is_n, h_hum_is_n=h_hum_is_n)
    theta_cl_light_is_n = get_theta_cl_is_n(clo=clo_light, theta_ot_is_n=theta_ot_is_n, h_hum_is_n=h_hum_is_n)

    return theta_cl_heavy_is_n, theta_cl_middle_is_n, theta_cl_light_is_n


def get_theta_cl_is_n(clo: float, theta_ot_is_n: np.ndarray, h_hum_is_n: np.ndarray) -> np.ndarray:
    """着衣温度を計算する。

    Args:
        clo: ステップnの室iにおけるClo値
        theta_ot_is_n: ステップnの室iにおける作用温度, degree C
        h_hum_is_n: ステップnの室iにおける人体周りの総合熱伝達率, W/m2K

    Returns:
        ステップnの室iにおける着衣温度, degree C
    """

    # 着衣抵抗, m2K/W
    i_cl = get_i_cl(clo)

    # 着衣面積率
    f_cl = get_f_cl(i_cl)

    # 代謝量（人体内部発熱量）, W/m2
    m = get_m()

    # ステップnの室iにおける着衣温度, degree C
    t_cl_i_n = (35.7 - 0.028 * m - theta_ot_is_n) / (1 + i_cl * f_cl * h_hum_is_n) + theta_ot_is_n

    return t_cl_i_n


def get_t_cl_i_n(clo_i_n, ot_i_n, h_a_i_n):
    """着衣温度を計算する。
    
    Args:
        clo_i_n: ステップnの室iにおけるClo値
        ot_i_n: ステップnの室iにおける作用温度, degree C
        h_a_i_n: ステップnの室iにおける人体周りの総合熱伝達率, W/m2K

    Returns:
        ステップnの室iにおける着衣温度, degree C
    """

    # 着衣抵抗, m2K/W
    i_cl = get_i_cl(clo_i_n)

    # 着衣面積率
    f_cl = get_f_cl(i_cl)

    # 代謝量（人体内部発熱量）, W/m2
    m = get_m()

    # ステップnの室iにおける着衣温度, degree C
    t_cl_i_n = (35.7 - 0.028 * m - ot_i_n) / (1 + i_cl * f_cl * h_a_i_n) + ot_i_n

    return t_cl_i_n


@jit('f8[:](f8[:], f8[:])', nopython=True)
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


@jit('f8[:](f8[:], f8[:], f8[:])', nopython=True)
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


@jit('f8[:](f8[:],f8[:])', nopython=True)
def get_h_hum_is_n(h_hum_r_is_n: np.ndarray, h_hum_c_is_n: np.ndarray) -> np.ndarray:
    """人体周りの対流熱伝達率を計算する。

    Args:
        h_hum_r_is_n: ステップnの室iにおける人体周りの放射熱伝達率, W/m2K, [i]
        h_hum_c_is_n: ステップnの室iにおける人体周りの対流熱伝達率, W/m2K, [i]

    Returns:
        ステップnの室iにおける人体周りの総合熱伝達率, W/m2K, [i]
    """

    return h_hum_r_is_n + h_hum_c_is_n


def get_pmv_heavy_middle_light_is_n(
        theta_r_is_n: np.ndarray,
        theta_cl_heavy_is_n: np.ndarray, theta_cl_middle_is_n: np.ndarray, theta_cl_light_is_n: np.ndarray,
        p_a_is_n: np.ndarray, h_hum_is_n: np.ndarray,
        theta_ot_is_n: np.ndarray) -> (np.ndarray, np.ndarray, np.ndarray):
    """PMVを計算する

    Args:
        theta_r_is_n: ステップnの室iにおける室温, degree C, [i]
        theta_cl_heavy_is_n: ステップnの室iにおける厚着の場合の着衣温度, degree C, [i]
        theta_cl_middle_is_n: ステップnの室iにおける中間着の場合の着衣温度, degree C, [i]
        theta_cl_light_is_n: ステップnの室iにおける薄着の場合の着衣温度, degree C, [i]
        p_a_is_n:　ステップnの室iにおける水蒸気圧, Pa, [i]
        h_hum_is_n: ステップnの室iにおける人体周りの総合熱伝達率, W/m2K, [i]
        theta_ot_is_n: ステップnの室iにおける作用温度, degree C, [i]

    Returns:
        以下の3つの値
            ステップnの室iにおける厚着をした場合のPMV, [i]
            ステップnの室iにおける中間着をした場合のPMV, [i]
            ステップnの室iにおける薄着をした場合のPMV, [i]
    """

    # 厚着・中間着・薄着をした場合のClo値
    clo_heavy, clo_middle, clo_light = get_clo()

    pmv_heavy_is_n = get_pmv_is_n(
        theta_r_is_n=theta_r_is_n, theta_cl_is_n=theta_cl_heavy_is_n, clo=clo_heavy, p_a_is_n=p_a_is_n,
        h_hum_is_n=h_hum_is_n, theta_ot_is_n=theta_ot_is_n)
    pmv_middle_is_n = get_pmv_is_n(
        theta_r_is_n=theta_r_is_n, theta_cl_is_n=theta_cl_middle_is_n, clo=clo_middle, p_a_is_n=p_a_is_n,
        h_hum_is_n=h_hum_is_n, theta_ot_is_n=theta_ot_is_n)
    pmv_light_is_n = get_pmv_is_n(
        theta_r_is_n=theta_r_is_n, theta_cl_is_n=theta_cl_light_is_n, clo=clo_light, p_a_is_n=p_a_is_n,
        h_hum_is_n=h_hum_is_n, theta_ot_is_n=theta_ot_is_n)

    return pmv_heavy_is_n, pmv_middle_is_n, pmv_light_is_n


def get_pmv_is_n(
        theta_r_is_n: np.ndarray, theta_cl_is_n: np.ndarray, clo: float, p_a_is_n: np.ndarray, h_hum_is_n: np.ndarray,
        theta_ot_is_n: np.ndarray):
    """PMVを計算する

    Args:
        theta_r_is_n: ステップnの室iにおける室温, degree C, [i]
        theta_cl_is_n: ステップnの室iにおける着衣温度, degree C, [i]
        clo: Clo値
        p_a_is_n:　ステップnの室iにおける水蒸気圧, Pa, [i]
        h_hum_is_n: ステップnの室iにおける人体周りの総合熱伝達率, W/m2K, [i]
        theta_ot_is_n: ステップnの室iにおける作用温度, degree C, [i]

    Returns:
        ステップnの室iにおけるPMV, [i]

    Notes:
        ISOで定める計算方法ではなく、前の時刻に求めた人体周りの熱伝達率、着衣温度を使用して収束計算が生じないようにしている。

    """

    # 着衣抵抗, m2K/W
    i_cl = get_i_cl(clo)

    # 代謝量（人体内部発熱量）, W/m2
    m = get_m()

    # 着衣面積率
    f_cl = get_f_cl(i_cl)

    return (0.303 * math.exp(-0.036 * m) + 0.028) * (
            m  # 活動量, W/m2
            - 3.05 * 10 ** (-3) * (5733.0 - 6.99 * m - p_a_is_n)  # 皮膚からの潜熱損失, W/m2
            - max(0.42 * (m - 58.15), 0.0)  # 発汗熱損失, W/m2
            - 1.7 * 10 ** (-5) * m * (5867.0 - p_a_is_n)  # 呼吸に伴う潜熱損失, W/m2
            - 0.0014 * m * (34.0 - theta_r_is_n)  # 呼吸に伴う顕熱損失, W/m2 ( = 呼吸量, (g/s)/m2 ✕ (34.0 - 室温)
            - f_cl * h_hum_is_n * (theta_cl_is_n - theta_ot_is_n))  # 着衣からの熱損失


def get_theta_ot_target(
        theta_cl_is_n: np.ndarray, clo_is_n: np.ndarray, p_a_is_n: np.ndarray, h_hum_is_n: np.ndarray,
        pmv_target_is_n: np.ndarray):
    """指定したPMVを満たすOTを計算する

    Args:
        theta_cl_is_n: ステップnの室iにおける着衣温度, degree C, [i]
        clo_is_n: ステップnの室iにおけるClo値, [i]
        p_a_is_n:　ステップnの室iにおける水蒸気圧, Pa
        h_hum_is_n: ステップnの室iにおける人体周りの総合熱伝達率, W/m2K, [i]
        pmv_target_is_n: ステップnの室iにおける目標PMV, [i]

    Returns:
        ステップnの室iにおける目標OT, [i]

    Notes:
        ISOで定める計算方法ではなく、前の時刻に求めた人体周りの熱伝達率、着衣温度を使用して収束計算が生じないようにしている。

    """

    # 着衣抵抗, m2K/W
    i_cl = get_i_cl(clo_is_n)

    # 代謝量（人体内部発熱量）, W/m2
    m = get_m()

    # 着衣面積率
    f_cl = get_f_cl(i_cl)

    return (pmv_target_is_n / (0.303 * math.exp(-0.036 * m) + 0.028) - m
            + 3.05 * 10 ** (-3) * (5733.0 - 6.99 * m - p_a_is_n)
            + max(0.42 * (m - 58.15), 0.0)
            + 1.7 * 10 ** (-5) * m * (5867.0 - p_a_is_n)
            + 0.0014 * m * 34.0
            + f_cl * h_hum_is_n * theta_cl_is_n
            )/(0.0014 * m + f_cl * h_hum_is_n)


def get_i_cl(clo: float) -> float:
    """Clo値から着衣抵抗を計算する。

    Args:
        clo: Clo値

    Returns:
        着衣抵抗, m2K/W

    Notes:
        1 clo = 0.155 m2K/W
    """

    return clo * 0.155


def get_m():
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

#    if i_cl <= 0.078:
#        return 1.00 + 1.290 * i_cl
#    else:
#        return 1.05 + 0.645 * i_cl

    return np.where(i_cl <= 0.078, 1.00 + 1.290 * i_cl, 1.05 + 0.645 * i_cl)


def get_clo() -> (float, float, float):
    """厚着・中間着・薄着をした場合のClo値をそれぞれ取得する。

    Returns:
        Clo値
            厚着をした場合のClo値
            中間着をした場合のClo値
            薄着をした場合のClo値
    """

    return 1.1, 0.7, 0.3


