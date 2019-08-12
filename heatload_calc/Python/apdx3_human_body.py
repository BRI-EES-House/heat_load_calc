import common


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


def get_q_hum_and_x_hum(theta_r: float) -> (float, float):
    """
    Args:
        theta_r: 室温, ℃
    Returns:
        1人あたりの人体発熱, W
        1人あたりの人体発湿, kg/s
    """

    # 水の蒸発潜熱, J/kg
    l_wtr = common.get_l_wtr()

    q_hum = min(63.0 - 4.0 * (theta_r - 24.0), 119.0)
    x_hum = (119.0 - q_hum) / l_wtr

    return q_hum, x_hum
