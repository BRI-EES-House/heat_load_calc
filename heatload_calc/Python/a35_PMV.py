import math
import numpy as np
from numba import jit
from typing import Union

from a39_global_parameters import OperationMode


def get_v_hum_is_n(operation_mode_is_n, is_radiative_heating_is, is_radiative_cooling_is):

    return np.vectorize(get_v_hum_i_n_pls)(operation_mode_is_n, is_radiative_heating_is, is_radiative_cooling_is)


def get_v_hum_i_n_pls(operation_mode_i_n, is_radiative_heating, is_radiative_cooling):

    if operation_mode_i_n == OperationMode.HEATING:
        if is_radiative_heating:
            return 0.0
        else:
            return 0.2
    elif operation_mode_i_n == OperationMode.COOLING:
        if is_radiative_cooling:
            return 0.0
        else:
            return 0.2
    elif operation_mode_i_n == OperationMode.STOP_CLOSE:
        return 0.0
    elif operation_mode_i_n == OperationMode.STOP_OPEN:
        return 0.1
    else:
        raise ValueError()


@jit('f8[:](f8[:],f8[:])', nopython=True)
def get_h_hum_is_n(
        h_hum_r_is_n: np.ndarray,
        h_hum_c_is_n: np.ndarray
) -> np.ndarray:
    """人体周りの総合熱伝達率を計算する。

    Args:
        h_hum_r_is_n: ステップnにおける室iの人体周りの放射熱伝達率, W/m2K, [i]
        h_hum_c_is_n: ステップnにおける室iの人体周りの対流熱伝達率, W/m2K, [i]

    Returns:
        ステップnにおける室iの人体周りの総合熱伝達率, W/m2K, [i]
    """

    return h_hum_r_is_n + h_hum_c_is_n


@jit('f8[:](f8[:],f8[:],f8[:],f8[:],f8[:])', nopython=True)
def get_theta_ot_is_n(
        h_hum_c_is_n: np.ndarray,
        h_hum_r_is_n: np.ndarray,
        h_hum_is_n: np.ndarray,
        theta_r_is_n: np.ndarray,
        theta_mrt_is_n: np.ndarray
) -> np.ndarray:
    """在室者の作用温度を計算する。

    Args:
        h_hum_c_is_n: ステップnにおける室iの人体周りの対流熱伝達率, W/m2K, [i]
        h_hum_r_is_n: ステップnにおける室iの人体周りの放射熱伝達率, W/m2K, [i]
        h_hum_is_n: ステップnにおける室iの人体周りの総合熱伝達率, W/m2K, [i]
        theta_r_is_n: ステップnにおける室iの室温, degree C, [i]
        theta_mrt_is_n: ステップnにおける室iの平均放射温度, degree C, [i]

    Returns:
        ステップnにおける室iの在室者の作用温度, degree C, [i]
    """

    return (h_hum_r_is_n * theta_mrt_is_n + h_hum_c_is_n * theta_r_is_n) / h_hum_is_n


def get_theta_cl_heavy_is_n(theta_ot_is_n: np.ndarray, h_hum_is_n: np.ndarray) -> np.ndarray:
    """厚着をした場合の在室者の着衣温度を計算する。

    Args:
        theta_ot_is_n: ステップnにおける室iの在室者の作用温度, degree C, [i]
        h_hum_is_n: ステップnにおける室iの人体周りの総合熱伝達率, W/m2K, [i]

    Returns:
        ステップnにおける室iの厚着をした場合の在室者の着衣温度, degree C, [i]
    """

    # 厚着時のClo値
    clo_heavy = get_clo_heavy()

    # 厚着をした場合の在室者の着衣温度, degree C, [i]
    theta_cl_heavy_is_n = get_theta_cl_is_n(clo_is_n=clo_heavy, theta_ot_is_n=theta_ot_is_n, h_hum_is_n=h_hum_is_n)

    return theta_cl_heavy_is_n


def get_theta_cl_middle_is_n(theta_ot_is_n: np.ndarray, h_hum_is_n: np.ndarray) -> np.ndarray:
    """中間着をした場合の在室者の着衣温度を計算する。

    Args:
        theta_ot_is_n: ステップnにおける室iの在室者の作用温度, degree C, [i]
        h_hum_is_n: ステップnにおける室iの人体周りの総合熱伝達率, W/m2K, [i]

    Returns:
        ステップnにおける室iの中間着をした場合の在室者の着衣温度, degree C, [i]
    """

    # 中間着時のClo値
    clo_middle = get_clo_middle()

    # 中間着をした場合の在室者の着衣温度, degree C, [i]
    theta_cl_middle_is_n = get_theta_cl_is_n(clo_is_n=clo_middle, theta_ot_is_n=theta_ot_is_n, h_hum_is_n=h_hum_is_n)

    return theta_cl_middle_is_n


def get_theta_cl_light_is_n(theta_ot_is_n: np.ndarray, h_hum_is_n: np.ndarray) -> np.ndarray:
    """薄着をした場合の在室者の着衣温度を計算する。

    Args:
        theta_ot_is_n: ステップnにおける室iの在室者の作用温度, degree C, [i]
        h_hum_is_n: ステップnにおける室iの人体周りの総合熱伝達率, W/m2K, [i]

    Returns:
        ステップnにおける室iの薄着をした場合の在室者の着衣温度, degree C, [i]
    """

    # 薄着時のClo値
    clo_light = get_clo_light()

    # 薄着をした場合の在室者の着衣温度, degree C, [i]
    theta_cl_light_is_n = get_theta_cl_is_n(clo_is_n=clo_light, theta_ot_is_n=theta_ot_is_n, h_hum_is_n=h_hum_is_n)

    return theta_cl_light_is_n


def get_theta_cl_is_n(
        clo_is_n: Union[np.ndarray, float],
        theta_ot_is_n: np.ndarray,
        h_hum_is_n: np.ndarray
) -> np.ndarray:
    """着衣温度を計算する。

    Args:
        clo_is_n: ステップnにおける室iの在室者のClo値, [i]　又は、（厚着・中間着・薄着時の）Clo値（定数）
        theta_ot_is_n: ステップnにおける室iの在室者の作用温度, degree C, [i]
        h_hum_is_n: ステップnにおける室iの人体周りの総合熱伝達率, W/m2K, [i]

    Returns:
        ステップnにおける室iの着衣温度, degree C, [i]
    """

    # ステップnにおける室iの着衣抵抗, m2K/W, [i]
    i_cl_is_n = get_i_cl_is_n(clo_is_n=clo_is_n)

    # ステップnにおける室iの着衣面積率, [i]
    f_cl_is_n = get_f_cl_is_n(i_cl_is_n=i_cl_is_n)

    # 代謝量（人体内部発熱量）, W/m2
    m = get_m()

    # ステップnの室iにおける着衣温度, degree C
    t_cl_i_n = (35.7 - 0.028 * m - theta_ot_is_n) / (1 + i_cl_is_n * f_cl_is_n * h_hum_is_n) + theta_ot_is_n

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
def get_h_hum_c_is_n(theta_r_is_n: np.ndarray, theta_cl_is_n: np.ndarray, v_hum_is_n: np.ndarray) -> np.ndarray:
    """人体周りの対流熱伝達率を計算する。

    Args:
        theta_r_is_n: ステップnの室iにおける室温, degree C, [i]
        theta_cl_is_n: ステップnの室iにおける着衣温度, degree C, [i]
        v_hum_is_n: ステップnの室iにおける人体周りの風速, m/s, [i]

    Returns:
        ステップnの室iにおける人体周りの対流熱伝達率, W/m2K
    """

    return np.maximum(12.1 * np.sqrt(v_hum_is_n), 2.38 * np.abs(theta_cl_is_n - theta_r_is_n) ** 0.25)


def get_pmv_is_n(
        theta_r_is_n: np.ndarray,
        theta_cl_is_n: np.ndarray,
        clo_is_n: np.ndarray,
        p_a_is_n: np.ndarray,
        h_hum_is_n: np.ndarray,
        theta_ot_is_n: np.ndarray
) -> np.ndarray:
    """PMVを計算する

    Args:
        theta_r_is_n: ステップnの室iにおける室温, degree C, [i]
        theta_cl_is_n: ステップnの室iにおける着衣温度, degree C, [i]
        clo_is_n: ステップnの室iにおけるClo値, [i]
        p_a_is_n:　ステップnの室iにおける水蒸気圧, Pa, [i]
        h_hum_is_n: ステップnの室iにおける人体周りの総合熱伝達率, W/m2K, [i]
        theta_ot_is_n: ステップnの室iにおける作用温度, degree C, [i]

    Returns:
        ステップnの室iにおけるPMV, [i]

    Notes:
        ISOで定める計算方法ではなく、前の時刻に求めた人体周りの熱伝達率、着衣温度を使用して収束計算が生じないようにしている。

    """

    # 着衣抵抗, m2K/W
    i_cl = get_i_cl_is_n(clo_is_n=clo_is_n)

    # 代謝量（人体内部発熱量）, W/m2
    m = get_m()

    # ステップnにおける室iの着衣面積率, [i]
    f_cl = get_f_cl_is_n(i_cl_is_n=i_cl)

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
    i_cl = get_i_cl_is_n(clo_is_n=clo_is_n)

    # 代謝量（人体内部発熱量）, W/m2
    m = get_m()

    # ステップnにおける室iの着衣面積率, [i]
    f_cl = get_f_cl_is_n(i_cl_is_n=i_cl)

    return (pmv_target_is_n / (0.303 * math.exp(-0.036 * m) + 0.028) - m
            + 3.05 * 10 ** (-3) * (5733.0 - 6.99 * m - p_a_is_n)
            + max(0.42 * (m - 58.15), 0.0)
            + 1.7 * 10 ** (-5) * m * (5867.0 - p_a_is_n)
            + 0.0014 * m * 34.0
            + f_cl * h_hum_is_n * theta_cl_is_n
            )/(0.0014 * m + f_cl * h_hum_is_n)


@jit('f8()', nopython=True)
def get_clo_heavy() -> float:
    """厚着をした場合の在室者のclo値を取得する。

    Returns:
        厚着をした場合の在室者のclo値
    """

    return 1.1


@jit('f8()', nopython=True)
def get_clo_middle() -> float:
    """中間着をした場合の在室者のclo値を取得する。

    Returns:
        中間着をした場合の在室者のclo値
    """

    return 0.7


@jit('f8()', nopython=True)
def get_clo_light() -> float:
    """薄着をした場合の在室者のclo値を取得する。

    Returns:
        薄着をした場合の在室者のclo値
    """

    return 0.3


# region 本モジュール内でのみ参照される関数

def get_f_cl_is_n(i_cl_is_n: np.ndarray) -> np.ndarray:
    """着衣面積率を計算する。

    Args:
        i_cl_is_n: ステップnにおける室iの着衣抵抗, m2K/W, [i]

    Returns:
        ステップnにおける室iの着衣面積率, [i]

    """

    return np.where(i_cl_is_n <= 0.078, 1.00 + 1.290 * i_cl_is_n, 1.05 + 0.645 * i_cl_is_n)


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


def get_i_cl_is_n(clo_is_n: np.ndarray) -> np.ndarray:
    """Clo値から着衣抵抗を計算する。

    Args:
        clo_is_n: ステップnの室iにおけるClo値, [i]

    Returns:
        ステップnの室iにおける着衣抵抗, m2K/W, [i]

    Notes:
        1 clo = 0.155 m2K/W
    """

    return clo_is_n * 0.155


# endregion
