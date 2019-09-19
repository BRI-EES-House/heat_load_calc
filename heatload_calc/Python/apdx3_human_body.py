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


def get_q_hum_and_x_hum(theta_r: float) -> (float, float):
    """
    Args:
        theta_r: 室温, ℃
    Returns:
        1人あたりの人体発熱, W
        1人あたりの人体発湿, kg/s
    """

    # 水の蒸発潜熱, J/kg
    l_wtr = a18.get_l_wtr()

    q_hum = min(63.0 - 4.0 * (theta_r - 24.0), 119.0)
    x_hum = (119.0 - q_hum) / l_wtr

    return q_hum, x_hum


def calc_Hhums_and_Hhuml(Tr: float, Nresi: int) -> (float, float):
    # 1人あたりの人体発熱(W)・発湿(kg/s)
    q_hum, x_hum = get_q_hum_and_x_hum(Tr)

    # 人体顕熱[W]
    Hhums = Nresi * q_hum

    # 人体潜熱[kg/s]
    Hhuml = Nresi * x_hum

    return Hhums, Hhuml
