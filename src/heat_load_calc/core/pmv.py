import math
from typing import Tuple
from scipy.optimize import newton
from collections import namedtuple
import numpy as np


def get_pmv_ppd(
        met_value: float, p_eff: np.array, t_a: np.array, t_r_bar: np.array,
        clo_value: np.array, v_ar: np.array, rh: np.array
) -> Tuple[np.array, np.array]:
    """calculate PMV & PPD

    Args:
        t_a: the air temperature, degree C
        t_r_bar: the mean radiant temperature, degree C
        rh: the relative humidity, %
        v_ar: the relative air velocity, m/s
        met_value: the metabolic rate, met
        p_eff: the effective mechanical power, met
        clo_value: the clothing insulation, clo

    Returns:
        tuple:
            PMV
            PPD

    Notes:
        Reference: ISO 7730, 1994, 2005
    """

    # the water vapour partial pressure, Pa
    p_a = get_p_a(rh, t_a)

    # the clothing insulation, m2K/W
    i_cl = convert_clo_to_m2kw(clo_value)

    # the metabolic rate, W/m2
    m = convert_met_to_wm2(met_value)

    # the effective mechanical power, W/m2
    w = convert_met_to_wm2(p_eff)

    # the clothing surface area factor
    f_cl = get_f_cl(i_cl)

    # the clothing surface temperature, degree C
    i = 0
    t_cl = np.zeros(f_cl.shape[0])
    for (fcld, icld, tad, vard, trbard) in zip(f_cl, i_cl, t_a, v_ar, t_r_bar):
        t_cl[i] = newton(lambda t: get_t_cl(fcld, icld, tad, t, vard, trbard, m, w) - t, 0.001)
        i += 1

    # the convective heat transfer coefficient, W/m2K
    h_c = get_h_c(t_a, t_cl, v_ar)

    # PMV, PPD
    pmv, ppd = get_pmv(f_cl, h_c, m, p_a, t_a, t_cl, t_r_bar, w)

    return pmv, ppd


def get_h_c(t_a: np.array, t_cl: np.array, v_ar: np.array) -> np.array:
    """

    Args:
        t_a: the air temperature, degree C
        t_cl: the clothing surface temperature, degree C
        v_ar: the relative air velocity, m/s

    Returns:
        the convective heat transfer coefficient, W/m2K
    """

    return np.maximum(12.1 * np.sqrt(v_ar), 2.38 * np.fabs(t_cl - t_a) ** 0.25)


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

    h_c = get_h_c(t_a, t_cl, v_ar)

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


def convert_clo_to_m2kw(clo:np.array) -> np.array:
    """convert the unit of clo to m2K/W

    Args:
        clo: value, clo

    Returns:
        value, m2K/W
    """
    return clo * 0.155


def convert_met_to_wm2(met: float):
    """convert the unit of met to W/m2

    Args:
        met: value, met

    Returns:
        value, W/m2
    """

    return met * 58.15


def get_f_cl(i_cl: np.ndarray) -> np.ndarray:
    """calculate clothing surface area factor

    Args:
        i_cl: the clothing insulation, m2K/W

    Returns:
        the clothing surface area factor

    Notes:
        equation (4)
    """

    return np.where(i_cl <= 0.078, 1.00 + 1.290 * i_cl, 1.05 + 0.645 * i_cl)


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


if __name__ == '__main__':

    pmv1 = get_pmv_ppd(met_value=1.1, p_eff=0.0, t_a=22.0, t_r_bar=22.0, clo_value=0.5, v_ar=0.1, rh=60.0)
    print(pmv1)

    pmv2 = get_pmv_ppd(met_value=1.1, p_eff=0.0, t_a=27.0, t_r_bar=27.0, clo_value=0.5, v_ar=0.1, rh=60.0)
    print(pmv2)

    pmv3 = get_pmv_ppd(met_value=1.1, p_eff=0.0, t_a=23.5, t_r_bar=25.5, clo_value=0.5, v_ar=0.1, rh=60.0)
    print(pmv3)

    pmv4 = get_pmv_ppd(met_value=1.1, p_eff=0.0, t_a=19.0, t_r_bar=19.0, clo_value=1.0, v_ar=0.1, rh=40.0)
    print(pmv4)

    pmv5 = get_pmv_ppd(met_value=1.1, p_eff=0.0, t_a=27.0, t_r_bar=27.0, clo_value=0.5, v_ar=0.3, rh=60.0)
    print(pmv5)

