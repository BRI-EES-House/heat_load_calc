import a18_initial_value_constants as a18


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


def get_x_hum_psn_i_n(theta_r_i_n: float) -> float:
    """1人あたりの人体発湿を計算する。

    Args:
        theta_r_i_n: ステップnの室iにおける室温, degree C

    Returns:
        ステップnの室iにおける1人あたりの人体発湿, kg/s
    """

    # 水の蒸発潜熱, J/kg
    l_wtr = a18.get_l_wtr()

    # ステップnの室iにおける1人あたりの人体発熱, W
    q_hum_psn_i_n = get_q_hum_psn_i_n(theta_r_i_n=theta_r_i_n)

    return (119.0 - q_hum_psn_i_n) / l_wtr


def get_q_hum_psn_i_n(theta_r_i_n: float) -> float:
    """1人あたりの人体発湿を計算する。

    Args:
        theta_r_i_n: ステップnの室iにおける室温, degree C

    Returns:
        ステップnの室iにおける1人あたりの人体発熱, W
    """

    return min(63.0 - 4.0 * (theta_r_i_n - 24.0), 119.0)


def get_q_hum_i_n(theta_r_i_n: float, n_hum_i_n: int) -> float:
    """人体発熱を計算する。

    Args:
        theta_r_i_n: ステップnの室iにおける室温, degree C
        n_hum_i_n: ステップnの室iにおける在室人数

    Returns:
        ステップnの室iにおける人体発熱, W
    """

    # ステップnの室iにおける1人あたりの人体発熱, W
    q_hum_psn_i_n = get_q_hum_psn_i_n(theta_r_i_n=theta_r_i_n)

    # ステップnの室iにおける人体発熱, W
    return n_hum_i_n * q_hum_psn_i_n


def get_x_hum_i_n(theta_r_i_n: float, n_hum_i_n: int) -> (float, float):
    """人体発湿を計算する。

    Args:
        theta_r_i_n: ステップnの室iにおける室温, degree C
        n_hum_i_n: ステップnの室iにおける在室人数

    Returns:
        ステップnの室iにおける人体発湿, kg/s
    """

    # ステップnの室iにおける1人あたりの人体発湿, kg/s
    x_hum_psn_i_n = get_x_hum_psn_i_n(theta_r_i_n)

    # ステップnの室iにおける人体潜熱, kg/s
    return n_hum_i_n * x_hum_psn_i_n

