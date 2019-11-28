import math
from scipy.optimize import fsolve
from scipy.optimize import newton
from line_profiler import LineProfiler


def calc_PMV(t_a, t_r_bar, clo_value, v_ar, rh):
    """calculate PMV

    Args:
        t_a: the air temperature, degree C
        t_r_bar: the mean radiant temperature, degree C
        rh: the relative humidity, %
        v_ar: the relative air velocity, m/s
        p_eff: the effective mechanical power, met
        clo_value: the clothing insulation, clo

    Returns:
        PMV

    Notes:
        参考: ISO 7730, 1994, 2005
        機械的仕事量は 0.0 W/m2 としたため、ISO中の'W'は省略してある。
    """

    # the water vapour partial pressure, Pa
    p_a = get_p_a(rh, t_a)

    # the clothing insulation, m2K/W
    i_cl = convert_clo_to_m2kw(clo_value)

    # 代謝量（人体内部発熱量）, W/m2
    mw = get_met()

    # the clothing surface area factor
    f_cl = get_f_cl(i_cl)

    t_cl = newton(lambda t: get_t_cl(f_cl, i_cl, mw, t_a, t, v_ar, t_r_bar) - t, 0.001)

    h_c = max(12.1 * math.sqrt(v_ar), 2.38 * abs(t_cl - t_a) ** 0.25)

    pmv = get_pmv(f_cl, h_c, mw, p_a, t_a, t_cl, t_r_bar)

    return pmv


def get_t_cl(f_cl, i_cl, mw, t_a, t_cl, v_ar, t_r_bar):

    h_c = max(12.1 * math.sqrt(v_ar), 2.38 * abs(t_cl - t_a) ** 0.25)

    return 35.7 - 0.028 * mw - i_cl * (
                3.96 * 10 ** (-8) * f_cl * ((t_cl + 273.0) ** 4.0 - (t_r_bar + 273.0) ** 4.0)
                + f_cl * h_c * (t_cl - t_a)
    )


def get_pmv(f_cl, h_c, m, p_a, t_a, t_cl, t_r_bar):
    """

    Args:
        f_cl: the clothing insulation, m2K/W
        h_c: the convective heat transfer coefficient, W/m2K
        m: the metabolic rate, W/m2
        p_a: the water vapour partial pressure, Pa
        t_a: the air temperature, degree C
        t_cl: the clothing surface temperature, degree C
        t_r_bar: the mean radiant temperature, degree C

    Returns:
        PMV

    Notes:
        equation (1)
    """

    return (0.303 * math.exp(-0.036 * m) + 0.028) * (
            m
            - 3.05 * 10 ** (-3) * (5733.0 - 6.99 * m - p_a)
            - max(0.42 * (m - 58.15), 0.0)
            - 1.7 * 10 ** (-5) * m * (5867.0 - p_a)
            - 0.0014 * m * (34.0 - t_a)
            - 3.96 * 10 ** (-8) * f_cl * ((t_cl + 273) ** 4.0 - (t_r_bar + 273.0) ** 4.0)
            - f_cl * h_c * (t_cl - t_a))


def get_p_a(rh: float, t_a: float) -> float:
    """

    Args:
        rh: relative humidity, %
        t_a: the air temperature, degree C

    Returns:
        the water vapour partial pressure, Pa

    """

    # TODO 飽和水蒸気圧の計算方法は省エネ基準で採用している方法（WMO?）に揃えた方が良い。
    return rh / 100. * FNPS(t_a) * 1000.0


def convert_clo_to_m2kw(clo):
    """convert the unit of clo to m2K/W

    Args:
        clo: value, clo

    Returns:
        value, m2K/W
    """
    return clo * 0.155


def get_met():
    """代謝量を得る。

    Returns:
        代謝量, W/m2
    """

    # 代謝量は1.0 met に固定とする。
    met = 1.0

    return met * 58.15


def get_f_cl(i_cl: float) -> float:
    """calculate clothing surface area factor

    Args:
        i_cl: the clothing insulation, m2K/W

    Returns:
        the clothing surface area factor

    Notes:
        equation (4)
    """

    if i_cl <= 0.078:
        return 1.00 + 1.290 * i_cl
    else:
        return 1.05 + 0.645 * i_cl


# 飽和水蒸気圧[kPa]の計算（ASHRAE Standard 55-2013）
def FNPS(T: float) -> float:
    return math.exp(16.6536 - 4030.183 / (T + 235.0))


# 着衣量 [clo] の計算（作用温度から求める） 式(128)
def get_I_cl(OT: float) -> float:
    # 冷房時の着衣量
    if OT > 29.1:
        clothing = 0.3
    # 暖房時の着衣量
    elif OT < 19.4:
        clothing = 1.1
    # 非空調時の着衣量（作用温度と線形関係で調節する）
    else:
        clothing = 1.1 + (0.3 - 1.1) / (29.1 - 19.4) * (OT - 19.4)

    return clothing


if __name__ == '__main__':

    pmv1 = calc_PMV(t_a=22.0, t_r_bar=22.0, clo_value=0.5, v_ar=0.1, rh=60.0)
    print(pmv1)

    pmv2 = calc_PMV(t_a=27.0, t_r_bar=27.0, clo_value=0.5, v_ar=0.1, rh=60.0)
    print(pmv2)

    pmv3 = calc_PMV(t_a=23.5, t_r_bar=25.5, clo_value=0.5, v_ar=0.1, rh=60.0)
    print(pmv3)

    pmv4 = calc_PMV(t_a=19.0, t_r_bar=19.0, clo_value=1.0, v_ar=0.1, rh=40.0)
    print(pmv4)

    pmv5 = calc_PMV(t_a=27.0, t_r_bar=27.0, clo_value=0.5, v_ar=0.3, rh=60.0)
    print(pmv5)

    def test():
        return calc_PMV(t_a=22.0, t_r_bar=22.0, clo_value=0.5, v_ar=0.1, rh=60.0)

    prf = LineProfiler()
    prf.add_function(calc_PMV)
    prf.runcall(test)
    prf.print_stats()
