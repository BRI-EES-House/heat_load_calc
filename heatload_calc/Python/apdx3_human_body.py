import numpy as np

import a39_global_parameters as a39


def get_alpha_hm_c() -> float:
    """
    Returns:
        人体表面の対流熱伝達率, W/m2K
    """

    return 4.9


def get_alpha_hm_r() -> float:
    """
    Returns:
        人体表面の放射熱伝達率, W/m2K
    """

    return 4.9


def get_x_hum_psn_i_n(theta_r_i_n: np.ndarray) -> np.ndarray:
    """1人あたりの人体発湿を計算する。

    Args:
        theta_r_i_n: ステップnの室iにおける室温, degree C, [i]

    Returns:
        ステップnの室iにおける1人あたりの人体発湿, kg/s, [i]
    """

    # 水の蒸発潜熱, J/kg
    l_wtr = a39.get_l_wtr()

    # ステップnの室iにおける1人あたりの人体発熱, W, [i]
    q_hum_psn_i_n = get_q_hum_psn_i_n(theta_r_i_n=theta_r_i_n)

    return (119.0 - q_hum_psn_i_n) / l_wtr


def get_q_hum_psn_i_n(theta_r_i_n: np.ndarray) -> np.ndarray:
    """1人あたりの人体発湿を計算する。

    Args:
        theta_r_i_n: ステップnの室iにおける室温, degree C, [i]

    Returns:
        ステップnの室iにおける1人あたりの人体発熱, W, [i]
    """

    return np.minimum(63.0 - 4.0 * (theta_r_i_n - 24.0), 119.0)


def get_q_hum_i_n(theta_r_is_n: np.ndarray, n_hum_i_n: np.ndarray) -> np.ndarray:
    """人体発熱を計算する。

    Args:
        theta_r_is_n: ステップnにおける室iの空気温度, degree C, [i]
        n_hum_i_n: ステップnの室iにおける在室人数, [i]

    Returns:
        ステップnの室iにおける人体発熱, W, [i]
    """

    # ステップnの室iにおける1人あたりの人体発熱, W, [i]
    q_hum_psn_i_n = get_q_hum_psn_i_n(theta_r_i_n=theta_r_is_n)

    # ステップnの室iにおける人体発熱, W, [i]
    return n_hum_i_n * q_hum_psn_i_n


def get_x_hum_i_n(theta_r_is_n: np.ndarray, n_hum_i_n: np.ndarray) -> np.ndarray:
    """人体発湿を計算する。

    Args:
        theta_r_is_n: ステップnにおける室iの空気温度, degree C, [i]
        n_hum_i_n: ステップnの室iにおける在室人数, [i]

    Returns:
        ステップnの室iにおける人体発湿, kg/s, [i]
    """

    # ステップnの室iにおける1人あたりの人体発湿, kg/s, [i]
    x_hum_psn_i_n = get_x_hum_psn_i_n(theta_r_is_n)

    # ステップnの室iにおける人体潜熱, kg/s, [i]
    return n_hum_i_n * x_hum_psn_i_n

