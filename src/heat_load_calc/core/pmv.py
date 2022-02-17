import math
from typing import Tuple
from scipy.optimize import newton
from collections import namedtuple
import numpy as np

from heat_load_calc.core import ot_target_pmv


def get_pmv_ppd(
        t_a: np.ndarray, t_r_bar: np.ndarray,
        v_ar: np.ndarray, rh: np.ndarray,
        clo_is_n: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """calculate PMV & PPD

    Args:
        t_a: the air temperature, degree C
        t_r_bar: the mean radiant temperature, degree C
        rh: the relative humidity, %
        v_ar: the relative air velocity, m/s
        clo_is_n: ステップ n における室 i の居住者のClo値, [i, 1]

    Returns:
        tuple:
            PMV
            PPD

    Notes:
        Reference: ISO 7730, 1994, 2005
    """

    # Met値
    # 取り急ぎ、1.0に固定するが、ot_target_pmv.py
    met_value = 1.0

    # the effective mechanical power, met
    p_eff = 0.0

    # the water vapour partial pressure, Pa
    p_a = get_p_a(rh, t_a)

    # ステップ n における室 i の在室者の着衣抵抗, m2K/W, [i, 1]
    i_cl = get_i_cl_is_n(clo_is_n=clo_is_n)

    # the metabolic rate, W/m2
    m = convert_met_to_wm2(met_value)

    # the effective mechanical power, W/m2
    w = convert_met_to_wm2(p_eff)

    # the clothing surface area factor
    f_cl = get_f_cl_is_n(i_cl_is_n=i_cl)

    def f(t):

        i_cl = get_i_cl_is_n(clo_is_n=clo_is_n)
        f_cl = get_f_cl_is_n(i_cl_is_n=i_cl)
        return get_t_cl(f_cl=f_cl, i_cl=i_cl, t_a=t_a, t_cl=t, v_ar=v_ar, t_r_bar=t_r_bar, m=m, w=w)

    # the clothing surface temperature, degree C
#    i = 0
#    t_cl = np.zeros(f_cl.shape[0])
#    for (fcld, icld, tad, vard, trbard) in zip(f_cl, i_cl, t_a, v_ar, t_r_bar):
#        t_cl[i] = newton(lambda t: get_t_cl(fcld, icld, tad, t, vard, trbard, m, w) - t, 0.001)
#        i += 1

    t_cl = newton(f, np.zeros_like(t_a, dtype=float))

    # the convective heat transfer coefficient, W/m2K
    h_c = get_h_hum_c_is_n(t_a, t_cl, v_ar)

    # PMV, PPD
    pmv, ppd = get_pmv(f_cl, h_c, m, p_a, t_a, t_cl, t_r_bar, w)

    return pmv, ppd


def get_h_hum_c_is_n(theta_r_is_n: np.array, theta_cl_is_n: np.array, v_hum_is_n: np.array) -> np.array:
    """人体周りの対流熱伝達率を計算する。

    Args:
        theta_r_is_n: ステップ n における室 i の空気温度, degree C, [i, 1]
        theta_cl_is_n: ステップ n における室 i の在室者の着衣温度, degree C, [i, 1]
        v_hum_is_n: ステップ n における室 i の在室者周りの風速, m/s, [i, 1]

    Returns:
        ステップnの室iにおける在室者周りの対流熱伝達率, W/m2K, [i, 1]

    """

    return np.maximum(12.1 * np.sqrt(v_hum_is_n), 2.38 * np.fabs(theta_cl_is_n - theta_r_is_n) ** 0.25)


def get_h_hum_r_is_n(
        theta_cl_is_n: np.ndarray,
        theta_mrt_is_n: np.ndarray
) -> np.ndarray:
    """在室者周りの放射熱伝達率を計算する。

    Args:
        theta_cl_is_n: ステップnにおける室iの在室者の着衣温度, degree C, [i, 1]
        theta_mrt_is_n: ステップnにおける室iの在室者の平均放射温度, degree C, [i, 1]

    Returns:
        ステップnにおける室iの在室者周りの放射熱伝達率, W/m2K, [i, 1]
    """

    # ステップnにおける室iの在室者の着衣温度, K, [i, 1]
    t_cl_is_n = theta_cl_is_n + 273.0

    # ステップnにおける室iの在室者の平均放射温度, K, [i, 1]
    t_mrt_is_n = theta_mrt_is_n + 273.0

    return 3.96 * 10 ** (-8) * (
                t_cl_is_n ** 3.0 + t_cl_is_n ** 2.0 * t_mrt_is_n + t_cl_is_n * t_mrt_is_n ** 2.0 + t_mrt_is_n ** 3.0)


def get_t_cl(f_cl: np.array, i_cl: np.array, t_a: np.array, t_cl: np.array, v_ar: np.array, t_r_bar: np.array, m:float, w:float) -> np.array:
    """

    Args:
        f_cl: the clothing surface area factor
        i_cl: the clothing insulation, m2K/W
        t_a: the air temperature, degree C
        t_cl: the clothing surface temperature, degree C
        v_ar: the relative air velocity, m/s
        t_r_bar: the mean radiant temperature, degree C
        m: the metabolic rate, W/m2
        w: the effective mechanical power, W/m2

    Returns:
        the clothing surface temperature, degree C
    """

    h_c = get_h_hum_c_is_n(t_a, t_cl, v_ar)

    return get_skin_temperature(m, w) - i_cl * (
            get_radiative_heat_loss_from_clothing(f_cl, t_cl, t_r_bar)
            + get_convective_heat_loss_from_clothing(f_cl, h_c, t_a, t_cl)
    )


def get_skin_temperature(m: float, w: float) -> float:
    """

    Args:
        m: the metabolic rate, W/m2
        w: the effective mechanical power, W/m2

    Returns:
        the skin temperature, degree C
    """

    return 35.7 - 0.028 * (m - w)


def get_radiative_heat_loss_from_clothing(f_cl: np.array, t_cl: np.array, t_r_bar: np.array) -> np.array:
    """

    Args:
        f_cl: the clothing surface area factor
        t_cl: the clothing surface temperature, degree C
        t_r_bar: the mean radiant temperature, degree C

    Returns:
        the radiative heat loss from clothing, W/m2
    """

    return 3.96 * 10 ** (-8) * f_cl * ((t_cl + 273.0) ** 4.0 - (t_r_bar + 273.0) ** 4.0)


def get_pmv(f_cl: np.ndarray, h_c: np.ndarray, m: np.ndarray, p_a: np.ndarray, t_a: np.ndarray, t_cl: np.ndarray, t_r_bar: np.ndarray, w: float) -> Tuple[np.ndarray, np.ndarray]:
    """

    Args:
        f_cl: the clothing surface area factor
        h_c: the convective heat transfer coefficient, W/m2K
        m: the metabolic rate, W/m2
        p_a: the water vapour partial pressure, Pa
        t_a: the air temperature, degree C
        t_cl: the clothing surface temperature, degree C
        t_r_bar: the mean radiant temperature, degree C
        w: the effective mechanical power, W/m2

    Returns:
        PMV

    Notes:
        equation (1)
    """

    pmv = np.minimum(np.maximum((0.303 * np.exp(-0.036 * m) + 0.028) * (
            (m - w)
            - get_latent_heat_loss_from_skin(m, p_a, w)
            - get_the_sweating_heat_loss(m, w)
            - get_latent_heat_loss_with_breathing(m, p_a)
            - get_sensible_heat_loss_with_breathing(m, t_a)
            - get_radiative_heat_loss_from_clothing(f_cl, t_cl, t_r_bar)
            - get_convective_heat_loss_from_clothing(f_cl, h_c, t_a, t_cl)), -3.0), 3.0)

    ppd = get_ppd(pmv=pmv)

    return pmv, ppd


def get_latent_heat_loss_from_skin(m: float, p_a: np.array, w: float) -> np.array:
    """

    Args:
        m: the metabolic rate, W/m2
        p_a: the water vapour partial pressure, Pa
        w: the effective mechanical power, W/m2

    Returns:
        the latent heat loss from skin, W/m2
    """
    return 3.05 * 10 ** (-3) * (5733.0 - 6.99 * (m - w) - p_a)


def get_latent_heat_loss_with_breathing(m: float, p_a: np.array) -> np.array:
    """

    Args:
        m: the metabolic rate, W/m2
        p_a: the water vapour partial pressure, Pa

    Returns:
        the latent heat loss with breathing, W/m2
    """

    return 1.7 * 10 ** (-5) * m * (5867.0 - p_a)


def get_sensible_heat_loss_with_breathing(m: float, t_a: np.array) -> np.array:
    """

    Args:
        m: the metabolic rate, W/m2
        t_a: the air temperature, degree C

    Returns:
        the sensible heat loss with breathing, W/m2
    """
    return 0.0014 * m * (34.0 - t_a)


def get_convective_heat_loss_from_clothing(f_cl: np.array, h_c: np.array, t_a: np.array, t_cl: np.array) -> np.array:
    """

    Args:
        f_cl: the clothing surface area factor
        h_c: the convective heat transfer coefficient, W/m2K
        t_a: the air temperature, degree C
        t_cl: the clothing surface temperature, degree C

    Returns:
        the convective heat loss from clothing, W/m2
    """

    return f_cl * h_c * (t_cl - t_a)


def get_the_sweating_heat_loss(m: float, w: float) -> float:
    """

    Args:
        m: the metabolic rate, W/m2
        w: the effective mechanical power, W/m2

    Returns:
        the sweating heat loss, W/m2
    """

    return max(0.42 * ((m - w) - 58.15), 0.0)


def get_p_a(rh: np.array, t_a: np.array) -> np.array:
    """get the water vapour partial pressure.

    Args:
        rh: relative humidity, %
        t_a: the air temperature, degree C

    Returns:
        the water vapour partial pressure, Pa

    """

    # the saturated vapour pressure, Pa
    p_sat = saturated_vapor_pressure_SONNTAG(status='water', t=t_a + 273.15)[0]

    return rh / 100.0 * p_sat


def get_i_cl_is_n(clo_is_n: np.array) -> np.array:
    """Clo値から着衣抵抗を計算する。

    Args:
        clo_is_n: ステップ n における室 i の在室者のClo値, [i, 1]

    Returns:
        ステップ n における室 i の在室者の着衣抵抗, m2K/W, [i, 1]

    Notes:
        1 clo = 0.155 m2K/W

    """

    return clo_is_n * 0.155


def get_f_cl_is_n(i_cl_is_n: np.ndarray) -> np.ndarray:
    """着衣面積率を計算する。

    Args:
        i_cl_is_n: ステップ n における室 i の在室者の着衣抵抗, m2K/W, [i, 1]

    Returns:
        ステップ n における室 i の在室者の着衣面積率, [i, 1]
    """

    return np.where(i_cl_is_n <= 0.078, 1.00 + 1.290 * i_cl_is_n, 1.05 + 0.645 * i_cl_is_n)


def get_ppd(pmv: np.array) -> np.array:
    """calculate PPD

    Args:
        pmv: PMV

    Returns:
        PPD

    Notes:
        PPD is Predicted Percentage of Dissatisfied.
    """

    return 100.0 - 95.0 * np.exp(-0.03353 * pmv ** 4.0 - 0.2179 * pmv ** 2.0)


def saturated_vapor_pressure_SONNTAG(status: str, t: np.array) -> Tuple[np.array, np.array]:
    """calculate the saturated vapor pressure and its differential

    Args:
        status: 'water' or 'ice'
        t: temperature, K

    Returns:
        2 parameters:
            (1) saturated vapor pressure, Pa
            (2) differential of saturated vapor pressure, Pa/K
    """

    Coeff = namedtuple('Coeff', ('a1', 'a2', 'a3', 'a4', 'a5'))

    c = {
        'water': Coeff(-6096.9385, 21.2409642, -0.02711193, 0.00001673952, 2.433502),
        'ice': Coeff(-6024.5282, 29.32707, 0.010613863, -0.000013198825, -0.49382577)
    }[status]

    k = c.a1 / t + c.a2 + c.a3 * t + c.a4 * t ** 2 + c.a5 * np.log(t)

    pvs = np.exp(k)

    dpvs_dt = pvs * (- c.a1 / (t ** 2) + c.a3 + 2 * c.a4 * t + c.a5 / t)

    return pvs, dpvs_dt


def get_h_hum(
        theta_mrt_is_n: np.ndarray,
        theta_r_is_n: np.ndarray,
        clo_is_n: np.ndarray,
        v_hum_is_n: np.ndarray,
        method: str
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """ 在室者周りの熱伝達率を計算する。

    Args:
        theta_mrt_is_n: ステップnにおける室iの在室者の平均放射温度, degree C, [i, 1]
        theta_r_is_n: ステップnにおける室iの空気温度, degree C, [i, 1]
        clo_is_n: CLO値, [i, 1]
        v_hum_is_n: ステップnにおける室iの在室者周りの風速, m/s, [i, 1]

    Returns:
        (1) ステップ n における室 i の在室者周りの対流熱伝達率, W/m2K, [i, 1]
        (2) ステップ n における室 i の在室者周りの放射熱伝達率, W/m2K, [i, 1]
        (3) ステップ n における室 i の在室者周りの総合熱伝達率, W/m2K, [i, 1]

    """

    def f(t):

        # ステップnにおける室iの在室者周りの対流熱伝達率, W/m2K, [i, 1]
        h_hum_c = get_h_hum_c_is_n(theta_r_is_n=theta_r_is_n, theta_cl_is_n=t, v_hum_is_n=v_hum_is_n)

        # ステップnにおける室iの在室者周りの放射熱伝達率, W/m2K, [i, 1]
        h_hum_r = get_h_hum_r_is_n(theta_cl_is_n=t, theta_mrt_is_n=theta_mrt_is_n)

        # ステップnにおける室iの在室者周りの総合熱伝達率, W/m2K, [i, 1]
        h_hum = h_hum_r + h_hum_c

        # ステップnにおける室iの在室者の作用温度, degree C, [i, 1]
        theta_ot_is_n = (h_hum_r * theta_mrt_is_n + h_hum_c * theta_r_is_n) / h_hum

        return _get_theta_cl_is_n(clo_is_n=clo_is_n, theta_ot_is_n=theta_ot_is_n, h_hum_is_n=h_hum)

    if method == 'convergence':
        # ステップnにおける室iの在室者の着衣温度, degree C, [i, 1]
        theta_cl_is_n = newton(lambda t: f(t) - t, np.zeros_like(theta_r_is_n, dtype=float))

        # ステップnにおける室iの在室者周りの対流熱伝達率, W/m2K, [i, 1]
        h_hum_c_is_n = get_h_hum_c_is_n(theta_r_is_n=theta_r_is_n, theta_cl_is_n=theta_cl_is_n, v_hum_is_n=v_hum_is_n)

        # ステップnにおける室iの在室者周りの放射熱伝達率, W/m2K, [i, 1]
        h_hum_r_is_n = get_h_hum_r_is_n(theta_cl_is_n=theta_cl_is_n, theta_mrt_is_n=theta_mrt_is_n)

    elif method == 'constant':

        h_hum_c_is_n = np.full_like(theta_r_is_n, 4.0)
        h_hum_r_is_n = np.full_like(theta_r_is_n, 4 * 3.96 * 10 ** (-8) * (20.0 + 273.15) ** 3.0)

    else:

        raise Exception

    h_hum_is_n = h_hum_c_is_n + h_hum_r_is_n

    return h_hum_c_is_n, h_hum_r_is_n, h_hum_is_n


def _get_theta_cl_is_n(
        clo_is_n: np.ndarray,
        theta_ot_is_n: np.ndarray,
        h_hum_is_n: np.ndarray
) -> np.ndarray:
    """着衣温度を計算する。

    Args:
        clo_is_n: ステップnにおける室iの在室者のClo値, [i, 1]　又は、（厚着・中間着・薄着時の）Clo値（定数）
        theta_ot_is_n: ステップnにおける室iの在室者の作用温度, degree C, [i, 1]
        h_hum_is_n: ステップnにおける室iの在室者周りの総合熱伝達率, W/m2K, [i, 1]

    Returns:
        ステップnにおける室iの着衣温度, degree C, [i, 1]
    """

    # ステップnにおける室iの在室者の着衣抵抗, m2K/W, [i, 1]
    i_cl_is_n = get_i_cl_is_n(clo_is_n=clo_is_n)

    # ステップnにおける室iの在室者の着衣面積率, [i]
    f_cl_is_n = get_f_cl_is_n(i_cl_is_n=i_cl_is_n)

    # 室 i の在室者の代謝量（人体内部発熱量）, W/m2
    m = get_m_is(met=np.full_like(clo_is_n, fill_value=1.0, dtype=float))

    # ステップnにおける室iの在室者の着衣温度, degree C
    t_cl_i_n = (35.7 - 0.028 * m - theta_ot_is_n) / (1 + i_cl_is_n * f_cl_is_n * h_hum_is_n) + theta_ot_is_n

    return t_cl_i_n


def get_m_is(met: np.ndarray) -> np.ndarray:
    """代謝量を得る。

    Args:
        met: Met, [i, 1]

    Returns:
        代謝量, W/m2, [i, 1]

    Notes:
        代謝量は1.0 met に固定とする。
        1.0 met は、ISOにおける、Resting - Seated, quiet に相当
        1 met = 58.15 W/m2
    """

    return met * 58.15


def convert_met_to_wm2(met: float):
    """convert the unit of met to W/m2

    Args:
        met: value, met

    Returns:
        value, W/m2
    """

    return met * 58.15


def _get_h_hum_and_pmv(
    p_a_is_n: np.ndarray,
    theta_r_is_n: np.ndarray,
    theta_mrt_is_n: np.ndarray,
    clo_is_n: np.ndarray,
    v_hum_is_n: np.ndarray,
    method : str = "convergence"
) -> np.ndarray:
    """

    Args:
        p_a_is_n:　ステップnにおける室iの水蒸気圧, Pa, [i, 1]
        theta_r_is_n: ステップnにおける室iの空気温度, degree C, [i, 1]
        theta_mrt_is_n: ステップnにおける室iの在室者の平均放射温度, degree C, [i, 1]
        clo_is_n:
        v_hum_is_n: ステップnにおける室iの在室者周りの風速, m/s, [i, 1]
        method: PMV計算時の熱伝達率計算に収束計算を行うか固定値を使用するか
    Returns:
        ステップnにおける室iの在室者のPMV, [i, 1]
    """

    # 室 i の在室者のMet値, [i, 1]
    met_is = np.full_like(clo_is_n, fill_value=1.0, dtype=float)

    # 室 i の在室者の代謝量（人体内部発熱量）, W/m2
    m_is = get_m_is(met=met_is)

    # (1) ステップ n における室 i の在室者周りの対流熱伝達率, W/m2K, [i, 1]
    # (2) ステップ n における室 i の在室者周りの放射熱伝達率, W/m2K, [i, 1]
    # (3) ステップ n における室 i の在室者周りの総合熱伝達率, W/m2K, [i, 1]
    h_hum_c_is_n, h_hum_r_is_n, h_hum_is_n = get_h_hum(
        theta_mrt_is_n=theta_mrt_is_n, theta_r_is_n=theta_r_is_n, clo_is_n=clo_is_n, v_hum_is_n=v_hum_is_n, method=method)

    # ステップnにおける室iの在室者の作用温度, degree C, [i, 1]
    theta_ot_is_n = (h_hum_r_is_n * theta_mrt_is_n + h_hum_c_is_n * theta_r_is_n) / h_hum_is_n

    # ステップ n における室 i の在室者の着衣抵抗, m2K/W, [i, 1]
    i_cl_is_n = get_i_cl_is_n(clo_is_n=clo_is_n)

    # ステップ n における室 i の在室者の着衣面積率, [i, 1]
    f_cl_is_n = get_f_cl_is_n(i_cl_is_n=i_cl_is_n)

    # ステップnにおける室iの在室者の厚着時のPMV, [i, 1]
    pmv_is_n = get_pmv_is_n(
        theta_r_is_n=theta_r_is_n,
        p_a_is_n=p_a_is_n,
        h_hum_is_n=h_hum_is_n,
        theta_ot_is_n=theta_ot_is_n,
        i_cl_is_n=i_cl_is_n,
        m_is=m_is,
        f_cl_is_n=f_cl_is_n
    )

    return pmv_is_n


def get_pmv_is_n(
        theta_r_is_n: np.ndarray,
        p_a_is_n: np.ndarray,
        h_hum_is_n: np.ndarray,
        theta_ot_is_n: np.ndarray,
        i_cl_is_n: np.ndarray,
        m_is: np.ndarray,
        f_cl_is_n: np.ndarray
) -> np.ndarray:
    """PMVを計算する

    Args:
        theta_r_is_n: ステップnにおける室iの空気温度, degree C, [i, 1]
        p_a_is_n:　ステップnにおける室iの水蒸気圧, Pa, [i, 1]
        h_hum_is_n: ステップnにおける室iの在室者周りの総合熱伝達率, W/m2K, [i, 1]
        theta_ot_is_n: ステップnにおける室iの在室者の作用温度, degree C, [i, 1]
        i_cl_is_n: ステップ n における室 i の在室者の着衣抵抗, m2K/W, [i, 1]
        m_is: 室 i の在室者の代謝量（人体内部発熱量）, W/m2
        f_cl_is_n: ステップnにおける室iの在室者の着衣面積率, [i, 1]

    Returns:
        ステップnにおける室iの在室者のPMV, [i, 1]

    Notes:
        ISOで定める計算方法ではなく、前の時刻に求めた人体周りの熱伝達率、着衣温度を使用して収束計算が生じないようにしている。

    """

    return (0.303 * np.exp(-0.036 * m_is) + 0.028) * (
            m_is  # 活動量, W/m2
            - 3.05 * 10 ** (-3) * (5733.0 - 6.99 * m_is - p_a_is_n)  # 皮膚からの潜熱損失, W/m2
            - np.maximum(0.42 * (m_is - 58.15), 0.0)  # 発汗熱損失, W/m2
            - 1.7 * 10 ** (-5) * m_is * (5867.0 - p_a_is_n)  # 呼吸に伴う潜熱損失, W/m2
            - 0.0014 * m_is * (34.0 - theta_r_is_n)  # 呼吸に伴う顕熱損失, W/m2 ( = 呼吸量, (g/s)/m2 ✕ (34.0 - 室温)
            - f_cl_is_n * h_hum_is_n * (35.7 - 0.028 * m_is - theta_ot_is_n) / (1 + i_cl_is_n * f_cl_is_n * h_hum_is_n))  # 着衣からの熱損失


def get_theta_ot_target(
        clo_is_n: np.ndarray,
        p_a_is_n: np.ndarray,
        h_hum_is_n: np.ndarray,
        pmv_target_is_n: np.ndarray
) -> np.ndarray:
    """指定したPMVを満たすOTを計算する

    Args:
        clo_is_n: ステップnにおける室iの在室者のClo値, [i, 1]
        p_a_is_n:　ステップnにおける室iの水蒸気圧, Pa, [i, 1]
        h_hum_is_n: ステップnにおける室iの在室者周りの総合熱伝達率, W/m2K, [i, 1]
        pmv_target_is_n: ステップnにおける室iの在室者の目標PMV, [i, 1]

    Returns:
        ステップnにおける室iの在室者の目標OT, [i, 1]

    Notes:
        ISOで定める計算方法ではなく、前の時刻に求めた人体周りの熱伝達率、着衣温度を使用して収束計算が生じないようにしている。

    """

    # 着衣抵抗, m2K/W, [i, 1]
    i_cl_is_n = get_i_cl_is_n(clo_is_n=clo_is_n)

    # 室 i の在室者のMet値, [i, 1]
    met_is = np.full_like(clo_is_n, fill_value=1.0, dtype=float)

    # 代謝量（人体内部発熱量）, W/m2
    m_is = get_m_is(met=met_is)

    # ステップnにおける室iの着衣面積率, [i, 1]
    f_cl_is_n = get_f_cl_is_n(i_cl_is_n=i_cl_is_n)

    return (pmv_target_is_n / (0.303 * np.exp(-0.036 * m_is) + 0.028) - m_is
            + 3.05 * 10 ** (-3) * (5733.0 - 6.99 * m_is - p_a_is_n)
            + np.maximum(0.42 * (m_is - 58.15), 0.0)
            + 1.7 * 10 ** (-5) * m_is * (5867.0 - p_a_is_n)
            + 0.0014 * m_is * 34.0
            + f_cl_is_n * h_hum_is_n * (35.7 - 0.028 * m_is) / (1 + i_cl_is_n * f_cl_is_n * h_hum_is_n)
            )/(0.0014 * m_is + f_cl_is_n * h_hum_is_n / (1 + i_cl_is_n * f_cl_is_n * h_hum_is_n))

