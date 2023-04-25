from typing import Tuple
from scipy.optimize import newton
import numpy as np


def get_pmv_is_n(
    p_a_is_n: np.ndarray,
    theta_r_is_n: np.ndarray,
    theta_mrt_is_n: np.ndarray,
    clo_is_n: np.ndarray,
    v_hum_is_n: np.ndarray,
    met_is: np.ndarray,
    method: str = "convergence"
) -> np.ndarray:
    """PMVを計算する。
    人体周りの熱伝達率を着衣温度との収束計算をした上でPMVを計算する。

    Args:
        p_a_is_n:　ステップnにおける室iの水蒸気圧, Pa, [i, 1]
        theta_r_is_n: ステップ n における室 i の空気温度, degree C, [i, 1]
        theta_mrt_is_n: ステップ n における室 i の在室者の平均放射温度, degree C, [i, 1]
        clo_is_n: ステップ n における室 i のClo値, [i, 1]
        v_hum_is_n: ステップ n における室 i の在室者周りの風速, m/s, [i, 1]
        met_is: 室 i の在室者のMet値, [i, 1]
        method: PMV計算時の熱伝達率計算に収束計算を行うか固定値を使用するか
    Returns:
        ステップ n における室 i の在室者のPMV, [i, 1]
    """

    # (1) ステップ n における室 i の在室者周りの対流熱伝達率, W/m2K, [i, 1]
    # (2) ステップ n における室 i の在室者周りの放射熱伝達率, W/m2K, [i, 1]
    # (3) ステップ n における室 i の在室者周りの総合熱伝達率, W/m2K, [i, 1]
    h_hum_c_is_n, h_hum_r_is_n, h_hum_is_n = get_h_hum(
        theta_mrt_is_n=theta_mrt_is_n,
        theta_r_is_n=theta_r_is_n,
        clo_is_n=clo_is_n,
        v_hum_is_n=v_hum_is_n,
        method=method,
        met_is=met_is
    )

    # ステップnにおける室iの在室者の作用温度, degree C, [i, 1]
    theta_ot_is_n = _get_theta_ot_is_n(h_hum_r_is_n=h_hum_r_is_n, theta_mrt_is_n=theta_mrt_is_n, h_hum_c_is_n=h_hum_c_is_n, theta_r_is_n=theta_r_is_n)

    # ステップ n における室 i の在室者の着衣抵抗, m2K/W, [i, 1]
    i_cl_is_n = _get_i_cl_is_n(clo_is_n=clo_is_n)

    # ステップ n における室 i の在室者の着衣面積率, [i, 1]
    f_cl_is_n = _get_f_cl_is_n(i_cl_is_n=i_cl_is_n)

    m_is = _get_m_is(met_is=met_is)

    # ステップnにおける室iの在室者の厚着時のPMV, [i, 1]
    pmv_is_n = _get_pmv_is_n(
        theta_r_is_n=theta_r_is_n,
        p_a_is_n=p_a_is_n,
        h_hum_is_n=h_hum_is_n,
        theta_ot_is_n=theta_ot_is_n,
        i_cl_is_n=i_cl_is_n,
        f_cl_is_n=f_cl_is_n,
        m_is=m_is
    )

    return pmv_is_n


def get_ppd_is_n(pmv_is_n: np.array) -> np.array:
    """PPDを計算する。
    Calculate the PPD of a ocupant.
    Args:
        pmv_is_n: ステップ n における室 i の在室者のPMV, [i, 1]
    Returns:
        ステップ n における室 i の在室者のPPD, [i, 1]
    Note:
        eq.(2)
    """

    return 100.0 - 95.0 * np.exp(-0.03353 * pmv_is_n ** 4.0 - 0.2179 * pmv_is_n ** 2.0)


def get_theta_ot_target(
        clo_is_n: np.ndarray,
        p_a_is_n: np.ndarray,
        h_hum_is_n: np.ndarray,
        met_is: np.ndarray,
        pmv_target_is_n: np.ndarray
) -> np.ndarray:
    """指定したPMVを満たすOTを計算する

    Args:
        clo_is_n: ステップnにおける室iの在室者のClo値, [i, 1]
        p_a_is_n: ステップnにおける室iの水蒸気圧, Pa, [i, 1]
        h_hum_is_n: ステップnにおける室iの在室者周りの総合熱伝達率, W/m2K, [i, 1]
        met_is: 室 i における在室者のMet, [i, 1]
        pmv_target_is_n: ステップnにおける室iの在室者の目標PMV, [i, 1]

    Returns:
        ステップnにおける室iの在室者の目標OT, [i, 1]

    Notes:
        ISOで定める計算方法ではなく、前の時刻に求めた人体周りの熱伝達率、着衣温度を使用して収束計算が生じないようにしている。

    """

    # 着衣抵抗, m2K/W, [i, 1]
    i_cl_is_n = _get_i_cl_is_n(clo_is_n=clo_is_n)

    # 代謝量（人体内部発熱量）, W/m2
    m_is = _get_m_is(met_is=met_is)

    # ステップnにおける室iの着衣面積率, [i, 1]
    f_cl_is_n = _get_f_cl_is_n(i_cl_is_n=i_cl_is_n)

    return _get_theta_ot_target_is_n(p_a_is_n, h_hum_is_n, pmv_target_is_n, i_cl_is_n, m_is, f_cl_is_n)


def get_h_hum(
        theta_mrt_is_n: np.ndarray,
        theta_r_is_n: np.ndarray,
        clo_is_n: np.ndarray,
        v_hum_is_n: np.ndarray,
        method: str,
        met_is: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """ 在室者周りの熱伝達率を計算する。

    Args:
        theta_mrt_is_n: ステップnにおける室iの在室者の平均放射温度, degree C, [i, 1]
        theta_r_is_n: ステップnにおける室iの空気温度, degree C, [i, 1]
        clo_is_n: CLO値, [i, 1]
        v_hum_is_n: ステップnにおける室iの在室者周りの風速, m/s, [i, 1]
        method: 在室者周りの熱伝達率を求める際に収束計算を行うかどうか
        met_is: 室 i の在室者のMet値, [i, 1]
    Returns:
        (1) ステップ n における室 i の在室者周りの対流熱伝達率, W/m2K, [i, 1]
        (2) ステップ n における室 i の在室者周りの放射熱伝達率, W/m2K, [i, 1]
        (3) ステップ n における室 i の在室者周りの総合熱伝達率, W/m2K, [i, 1]

    """

    m_is = _get_m_is(met_is=met_is)

    # def f(t):

    #     # ステップnにおける室iの在室者周りの対流熱伝達率, W/m2K, [i, 1]
    #     h_hum_c = _get_h_hum_c_is_n(theta_r_is_n=theta_r_is_n, theta_cl_is_n=t, v_hum_is_n=v_hum_is_n)

    #     # ステップnにおける室iの在室者周りの放射熱伝達率, W/m2K, [i, 1]
    #     h_hum_r = _get_h_hum_r_is_n(theta_cl_is_n=t, theta_mrt_is_n=theta_mrt_is_n)

    #     # ステップnにおける室iの在室者周りの総合熱伝達率, W/m2K, [i, 1]
    #     h_hum = h_hum_r + h_hum_c

    #     # ステップnにおける室iの在室者の作用温度, degree C, [i, 1]
    #     theta_ot_is_n = (h_hum_r * theta_mrt_is_n + h_hum_c * theta_r_is_n) / h_hum

    #     return _get_theta_cl_is_n(clo_is_n=clo_is_n, theta_ot_is_n=theta_ot_is_n, h_hum_is_n=h_hum, m_is=m_is)

    # if method == 'convergence':
    #     # ステップnにおける室iの在室者の着衣温度, degree C, [i, 1]
    #     theta_cl_is_n: np.ndarray = newton(lambda t: f(t) - t, np.zeros_like(theta_r_is_n, dtype=float))

    #     # ステップnにおける室iの在室者周りの対流熱伝達率, W/m2K, [i, 1]
    #     h_hum_c_is_n = _get_h_hum_c_is_n(theta_r_is_n=theta_r_is_n, theta_cl_is_n=theta_cl_is_n, v_hum_is_n=v_hum_is_n)

    #     # ステップnにおける室iの在室者周りの放射熱伝達率, W/m2K, [i, 1]
    #     h_hum_r_is_n = _get_h_hum_r_is_n(theta_cl_is_n=theta_cl_is_n, theta_mrt_is_n=theta_mrt_is_n)

    # elif method == 'constant':

    #     h_hum_c_is_n = np.full_like(theta_r_is_n, 4.0)
    #     h_hum_r_is_n = np.full_like(theta_r_is_n, 4 * 3.96 * 10 ** (-8) * (20.0 + 273.15) ** 3.0)

    # else:

    #     raise Exception

    h_hum_c_is_n, h_hum_r_is_n = _get_h_hum_c_is_n_and_h_hum_r_is_n(
        theta_mrt_is_n=theta_mrt_is_n,
        theta_r_is_n=theta_r_is_n,
        clo_is_n=clo_is_n,
        v_hum_is_n=v_hum_is_n,
        method=method,
        m_is=m_is
    )

    h_hum_is_n = _get_h_hum_is_n(h_hum_c_is_n=h_hum_c_is_n, h_hum_r_is_n=h_hum_r_is_n)

    return h_hum_c_is_n, h_hum_r_is_n, h_hum_is_n

def _get_h_hum_is_n(h_hum_c_is_n: np.ndarray, h_hum_r_is_n: np.ndarray) -> np.ndarray:
    """在室者周りの総合熱伝達率を計算する。
    calculate the integrated heat transfere coefficient around the ocupant.
    Args:
        h_hum_c_is_n: ステップ n における室 i の在室者周りの対流熱伝達率, W/m2K, [i, 1]
        h_hum_r_is_n: ステップ n における室 i の在室者周りの放射熱伝達率, W/m2K, [i, 1]
    Returns:
        ステップ n における室 i の在室者周りの総合熱伝達率, W/m2K, [i, 1]
    Note:
        eq.(4)
    """

    return h_hum_c_is_n + h_hum_r_is_n


def _get_h_hum_c_is_n_and_h_hum_r_is_n(
        theta_mrt_is_n: np.ndarray,
        theta_r_is_n: np.ndarray,
        clo_is_n: np.ndarray,
        v_hum_is_n: np.ndarray,
        method: str,
        m_is: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """ 在室者周りの熱伝達率を計算する。

    Args:
        theta_mrt_is_n: ステップ n における室 i の平均放射温度, degree C, [i, 1]
        theta_r_is_n: ステップ n における室 i の空気温度, degree C, [i, 1]
        clo_is_n: 室 i の在室者のClo値, [i, 1]
        v_hum_is_n: ステップ n における室 i の在室者周りの風速, m/s, [i, 1]
        method: 在室者周りの熱伝達率を求める際に収束計算を行うかどうか
        m_is: 室 i の在室者の代謝量, W/m2, [i, 1]
    Returns:
        (1) ステップ n における室 i の在室者周りの対流熱伝達率, W/m2K, [i, 1]
        (2) ステップ n における室 i の在室者周りの放射熱伝達率, W/m2K, [i, 1]
        (3) ステップ n における室 i の在室者周りの総合熱伝達率, W/m2K, [i, 1]

    """

    def f(t):

        # ステップnにおける室iの在室者周りの対流熱伝達率, W/m2K, [i, 1]
        h_hum_c = _get_h_hum_c_is_n(theta_r_is_n=theta_r_is_n, theta_cl_is_n=t, v_hum_is_n=v_hum_is_n)

        # ステップnにおける室iの在室者周りの放射熱伝達率, W/m2K, [i, 1]
        h_hum_r = _get_h_hum_r_is_n(theta_cl_is_n=t, theta_mrt_is_n=theta_mrt_is_n)

        # ステップnにおける室iの在室者周りの総合熱伝達率, W/m2K, [i, 1]
        h_hum = h_hum_r + h_hum_c

        # ステップnにおける室iの在室者の作用温度, degree C, [i, 1]
        theta_ot_is_n = _get_theta_ot_is_n(h_hum_r_is_n=h_hum_r, theta_mrt_is_n=theta_mrt_is_n, h_hum_c_is_n=h_hum_c, theta_r_is_n=theta_r_is_n)

        return _get_theta_cl_is_n(clo_is_n=clo_is_n, theta_ot_is_n=theta_ot_is_n, h_hum_is_n=h_hum, m_is=m_is)

    # 収束計算による方法
    if method == 'convergence':
    
        # ステップnにおける室iの在室者の着衣温度, degree C, [i, 1]
        theta_cl_is_n: np.ndarray = newton(lambda t: f(t) - t, np.zeros_like(theta_r_is_n, dtype=float))

        # ステップnにおける室iの在室者周りの対流熱伝達率, W/m2K, [i, 1]
        h_hum_c_is_n = _get_h_hum_c_is_n(theta_r_is_n=theta_r_is_n, theta_cl_is_n=theta_cl_is_n, v_hum_is_n=v_hum_is_n)

        # ステップnにおける室iの在室者周りの放射熱伝達率, W/m2K, [i, 1]
        h_hum_r_is_n = _get_h_hum_r_is_n(theta_cl_is_n=theta_cl_is_n, theta_mrt_is_n=theta_mrt_is_n)

    # 収束計算によらない方法
    elif method == 'constant':

        h_hum_c_is_n = np.full_like(theta_r_is_n, 4.0)
        h_hum_r_is_n = np.full_like(theta_r_is_n, 4 * 3.96 * 10 ** (-8) * (20.0 + 273.15) ** 3.0)

    else:

        raise Exception

    return h_hum_c_is_n, h_hum_r_is_n


def _get_pmv_is_n(
        theta_r_is_n: np.ndarray,
        p_a_is_n: np.ndarray,
        h_hum_is_n: np.ndarray,
        theta_ot_is_n: np.ndarray,
        i_cl_is_n: np.ndarray,
        f_cl_is_n: np.ndarray,
        m_is: np.ndarray
) -> np.ndarray:
    """PMVを計算する
    Calculate the PMV of a occupant.
    Args:
        theta_r_is_n: ステップ n における室 i の空気温度, degree C, [i, 1]
        p_a_is_n: ステップ n における室 i の水蒸気圧, Pa, [i, 1]
        h_hum_is_n: ステップ n における室 i の在室者周りの総合熱伝達率, W/m2K, [i, 1]
        theta_ot_is_n: ステップ n における室 i の在室者の作用温度, degree C, [i, 1]
        i_cl_is_n: ステップ n における室 i の在室者の着衣抵抗, m2K/W, [i, 1]
        f_cl_is_n: ステップ n における室 i の在室者の着衣面積率, [i, 1]
        m_is: 室 i の在室者の代謝量, W/m2, [i, 1]
    Returns:
        ステップ n における室 i の在室者のPMV, [i, 1]
    Notes:
        eq.(1)
    """

    return (0.303 * np.exp(-0.036 * m_is) + 0.028) * (
            m_is  # 活動量, W/m2
            - 3.05 * 10 ** (-3) * (5733.0 - 6.99 * m_is - p_a_is_n)  # 皮膚からの潜熱損失, W/m2
            - np.maximum(0.42 * (m_is - 58.15), 0.0)  # 発汗熱損失, W/m2
            - 1.7 * 10 ** (-5) * m_is * (5867.0 - p_a_is_n)  # 呼吸に伴う潜熱損失, W/m2
            - 0.0014 * m_is * (34.0 - theta_r_is_n)  # 呼吸に伴う顕熱損失, W/m2 ( = 呼吸量, (g/s)/m2 ✕ (34.0 - 室温)
            - f_cl_is_n * h_hum_is_n * (35.7 - 0.028 * m_is - theta_ot_is_n) / (1 + i_cl_is_n * f_cl_is_n * h_hum_is_n))  # 着衣からの熱損失


def _get_theta_ot_target_is_n(p_a_is_n: np.ndarray, h_hum_is_n: np.ndarray, pmv_target_is_n: np.ndarray, i_cl_is_n: np.ndarray, m_is, f_cl_is_n: np.ndarray) -> np.ndarray:
    """目標作用温度を計算する。
    Calculate the target operative temperature.
    Args:
        p_a_is_n: ステップ n における室 i の水蒸気圧, Pa, [i, 1]
        h_hum_is_n: ステップ n における室 i の在室者周りの総合熱伝達率, W/m2K, [i, 1]
        pmv_target_is_n: ステップ n における室 i の在室者の目標PMV, [i, 1]
        i_cl_is_n: ステップ n における室 i の在室者の着衣抵抗, m2K/W, [i, 1]
        m_is: 室 i の在室者の代謝量, W/m2, [i, 1]
        f_cl_is_n: ステップ n における室 i の在室者の着衣面積率, [i, 1]
    Returns:
        ステップ n における室 i の在室者の目標作用温度, degree C, [i, 1]
    NOte:
        eq.(3)
    """
    
    return (pmv_target_is_n / (0.303 * np.exp(-0.036 * m_is) + 0.028) - m_is
            + 3.05 * 10 ** (-3) * (5733.0 - 6.99 * m_is - p_a_is_n)
            + np.maximum(0.42 * (m_is - 58.15), 0.0)
            + 1.7 * 10 ** (-5) * m_is * (5867.0 - p_a_is_n)
            + 0.0014 * m_is * 34.0
            + f_cl_is_n * h_hum_is_n * (35.7 - 0.028 * m_is) / (1 + i_cl_is_n * f_cl_is_n * h_hum_is_n)
            )/(0.0014 * m_is + f_cl_is_n * h_hum_is_n / (1 + i_cl_is_n * f_cl_is_n * h_hum_is_n))


def _get_theta_ot_is_n(h_hum_r_is_n: np.ndarray, theta_mrt_is_n: np.ndarray, h_hum_c_is_n: np.ndarray, theta_r_is_n: np.ndarray) -> np.ndarray:
    """在室者の作用温度を計算する。
    Calculate the operative temperature of the occupant.
    Args:
        h_hum_r_is_n: ステップ n における室 i の在室者周りの放射熱伝達率, W/m2K, [i, 1]
        theta_mrt_is_n: ステップ n における室 i の在室者の平均放射温度, degree C, [i, 1]
        h_hum_c_is_n: ステップ n における室 i の在室者周りの対流熱伝達率, W/m2K, [i, 1]
        theta_r_is_n: ステップ n における室 i の空気温度, degree C, [i, 1]
    Returns:
        ステップ n における室 i の在室者の作用温度, degree C, [i, 1]
    Notes:
        eq.(5)
    """

    return (h_hum_r_is_n * theta_mrt_is_n + h_hum_c_is_n * theta_r_is_n) / (h_hum_r_is_n + h_hum_c_is_n)


def _get_h_hum_c_is_n(theta_r_is_n: np.array, theta_cl_is_n: np.array, v_hum_is_n: np.array) -> np.array:
    """人体周りの対流熱伝達率を計算する。

    Args:
        theta_r_is_n: ステップ n における室 i の空気温度, degree C, [i, 1]
        theta_cl_is_n: ステップ n における室 i の在室者の着衣温度, degree C, [i, 1]
        v_hum_is_n: ステップ n における室 i の在室者周りの風速, m/s, [i, 1]

    Returns:
        ステップ n の室 i における在室者周りの対流熱伝達率, W/m2K, [i, 1]

    """

    return np.maximum(12.1 * np.sqrt(v_hum_is_n), 2.38 * np.fabs(theta_cl_is_n - theta_r_is_n) ** 0.25)


def _get_h_hum_r_is_n(
        theta_cl_is_n: np.ndarray,
        theta_mrt_is_n: np.ndarray
) -> np.ndarray:
    """在室者周りの放射熱伝達率を計算する。

    Args:
        theta_cl_is_n: ステップ n における室 i の在室者の着衣温度, degree C, [i, 1]
        theta_mrt_is_n: ステップ n における室 i の在室者の平均放射温度, degree C, [i, 1]

    Returns:
        ステップ n における室 i の在室者周りの放射熱伝達率, W/m2K, [i, 1]
    """

    # ステップ n における室 i の在室者の着衣温度, K, [i, 1]
    t_cl_is_n = theta_cl_is_n + 273.0

    # ステップ n における室 i の在室者の平均放射温度, K, [i, 1]
    t_mrt_is_n = theta_mrt_is_n + 273.0

    return 3.96 * 10 ** (-8) * (
                t_cl_is_n ** 3.0 + t_cl_is_n ** 2.0 * t_mrt_is_n + t_cl_is_n * t_mrt_is_n ** 2.0 + t_mrt_is_n ** 3.0)


def _get_theta_cl_is_n(
        clo_is_n: np.ndarray,
        theta_ot_is_n: np.ndarray,
        h_hum_is_n: np.ndarray,
        m_is: np.ndarray
) -> np.ndarray:
    """着衣温度を計算する。

    Args:
        clo_is_n: ステップnにおける室iの在室者のClo値, [i, 1]　又は、（厚着・中間着・薄着時の）Clo値（定数）
        theta_ot_is_n: ステップnにおける室iの在室者の作用温度, degree C, [i, 1]
        h_hum_is_n: ステップnにおける室iの在室者周りの総合熱伝達率, W/m2K, [i, 1]
        m_is: 室 i の在室者の代謝量（人体内部発熱量）, W/m2

    Returns:
        ステップnにおける室iの着衣温度, degree C, [i, 1]
    """

    # ステップnにおける室iの在室者の着衣抵抗, m2K/W, [i, 1]
    i_cl_is_n = _get_i_cl_is_n(clo_is_n=clo_is_n)

    # ステップnにおける室iの在室者の着衣面積率, [i]
    f_cl_is_n = _get_f_cl_is_n(i_cl_is_n=i_cl_is_n)

    # ステップnにおける室iの在室者の着衣温度, degree C
    t_cl_i_n = (35.7 - 0.028 * m_is - theta_ot_is_n) / (1 + i_cl_is_n * f_cl_is_n * h_hum_is_n) + theta_ot_is_n

    return t_cl_i_n


def _get_m_is(met_is: np.ndarray) -> np.ndarray:
    """代謝量を得る。

    Args:
        met_is: 居室 i の在室者のMet値, [i, 1]

    Returns:
        居室 i の在室者の代謝量, W/m2, [i, 1]

    Notes:
        代謝量は1.0 met に固定とする。
        1.0 met は、ISOにおける、Resting - Seated, quiet に相当
        1 met = 58.15 W/m2
    """

    return met_is * 58.15


def _get_f_cl_is_n(i_cl_is_n: np.ndarray) -> np.ndarray:
    """着衣面積率を計算する。

    Args:
        i_cl_is_n: ステップ n における室 i の在室者の着衣抵抗, m2K/W, [i, 1]

    Returns:
        ステップ n における室 i の在室者の着衣面積率, [i, 1]
    """

    return np.where(i_cl_is_n <= 0.078, 1.00 + 1.290 * i_cl_is_n, 1.05 + 0.645 * i_cl_is_n)


def _get_i_cl_is_n(clo_is_n: np.array) -> np.array:
    """Clo値から着衣抵抗を計算する。

    Args:
        clo_is_n: ステップ n における室 i の在室者のClo値, [i, 1]

    Returns:
        ステップ n における室 i の在室者の着衣抵抗, m2K/W, [i, 1]

    Notes:
        1 clo = 0.155 m2K/W

    """

    return clo_is_n * 0.155


