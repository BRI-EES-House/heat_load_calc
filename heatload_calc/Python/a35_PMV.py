import math
from scipy.optimize import fsolve
from scipy.optimize import newton
from line_profiler import LineProfiler


def calc_PMV(t_a, t_r_bar, clo_value, v_ar, rh):
    """PMVを計算する。

    Args:
        t_a: 乾球温度, degree C
        t_r_bar: 放射温度, degree C
        rh: 相対湿度, %
        v_ar: 相対気流速度, m/s
        clo_value: 着衣量, clo

    Returns:
        PMV

    Notes:
        参考: ISO 7730, 1994, 2005
        機械的仕事量は 0.0 W/m2 としたため、ISO中の'W'は省略してある。
    """

    # 水蒸気分圧, Pa
    p_a = get_p_a(rh, t_a)

    # 着衣抵抗, m2K/W
    i_cl = convert_clo_to_m2kw(clo_value)

    # 代謝量（人体内部発熱量）, W/m2
    m = get_met()

    # 着衣面積率
    f_cl = get_f_cl(i_cl)

    t_cl = get_t_cl(clo_value, t_a, v_ar, t_r_bar)

    h_c = get_h_c(t_a, t_cl, v_ar)

    pmv = get_pmv(f_cl, h_c, m, p_a, t_a, t_cl, t_r_bar)

    return pmv


def get_t_cl(clo, t_a, v_ar, t_r_bar):

    # 着衣抵抗, m2K/W
    i_cl = convert_clo_to_m2kw(clo)

    # 着衣面積率
    f_cl = get_f_cl(i_cl)

    # 代謝量（人体内部発熱量）, W/m2
    m = get_met()

    def f(t):

        h_c = get_h_c(t_a, t, v_ar)

        return 35.7 - 0.028 * m \
            - i_cl * (
                3.96 * 10 ** (-8) * f_cl * ((t + 273.0) ** 4.0 - (t_r_bar + 273.0) ** 4.0) + f_cl * h_c * (t - t_a)
            )

    t_cl = newton(lambda t: f(t) - t, 0.001)

    return t_cl


def get_h_c(t_a, t_cl, v_ar):
    return max(12.1 * math.sqrt(v_ar), 2.38 * abs(t_cl - t_a) ** 0.25)


def get_pmv(f_cl, h_c, m, p_a, t_a, t_cl, t_r_bar):
    """

    Args:
        f_cl: 着衣面積率
        h_c: 対流熱伝達率, W/m2K
        m: 活動量, W/m2
        p_a: 水蒸気分圧, Pa
        t_a: 乾球温度, degree C
        t_cl: 着衣温度, degree C
        t_r_bar: 放射温度, degree C

    Returns:
        PMV

    Notes:
        equation (1)
    """

    return (0.303 * math.exp(-0.036 * m) + 0.028) * (
            m  # 活動量, W/m2
            - 3.05 * 10 ** (-3) * (5733.0 - 6.99 * m - p_a)  # 皮膚からの潜熱損失, W/m2
            - max(0.42 * (m - 58.15), 0.0)  # 発汗熱損失, W/m2
            - 1.7 * 10 ** (-5) * m * (5867.0 - p_a)  # 呼吸に伴う潜熱損失, W/m2
            - 0.0014 * m * (34.0 - t_a)  # 呼吸に伴う顕熱損失, W/m2 ( = 呼吸量, (g/s)/m2 ✕ (34.0 - 室温)
            - 3.96 * 10 ** (-8) * f_cl * ((t_cl + 273) ** 4.0 - (t_r_bar + 273.0) ** 4.0)  # 着衣からの放射熱損失
            - f_cl * h_c * (t_cl - t_a))  # 着衣からの対流熱損失


def get_p_a(rh: float, t_a: float) -> float:
    """

    Args:
        rh: 相対湿度, %
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

