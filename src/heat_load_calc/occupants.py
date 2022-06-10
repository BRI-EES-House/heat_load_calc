import numpy as np

from heat_load_calc.global_number import get_l_wtr


def get_x_hum_psn_is_n(theta_r_is_n: np.ndarray) -> np.ndarray:
    """1人あたりの人体発湿を計算する。

    Args:
        theta_r_is_n: ステップnの室iにおける室温, degree C, [i, 1]

    Returns:
        ステップnの室iにおける1人あたりの人体発湿, kg/s, [i, 1]
    """

    # 水の蒸発潜熱, J/kg
    l_wtr = get_l_wtr()

    # ステップnの室iにおける1人あたりの人体発熱, W, [i]
    q_hum_psn_is_n = get_q_hum_psn_is_n(theta_r_is_n=theta_r_is_n)

    return (119.0 - q_hum_psn_is_n) / l_wtr


def get_q_hum_psn_is_n(theta_r_is_n: np.ndarray) -> np.ndarray:
    """1人あたりの人体発湿を計算する。

    Args:
        theta_r_is_n: ステップnの室iにおける室温, degree C, [i, 1]

    Returns:
        ステップnの室iにおける1人あたりの人体発熱, W, [i, 1]
    """

    return np.minimum(63.0 - 4.0 * (theta_r_is_n - 24.0), 119.0)
