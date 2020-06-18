import numpy as np

import x_35_occupants as x_35

def get_x_hum_i_n(theta_r_is_n: np.ndarray, n_hum_i_n: np.ndarray) -> np.ndarray:
    """人体発湿を計算する。

    Args:
        theta_r_is_n: ステップnにおける室iの空気温度, degree C, [i]
        n_hum_i_n: ステップnの室iにおける在室人数, [i]

    Returns:
        ステップnの室iにおける人体発湿, kg/s, [i]
    """

    # ステップnの室iにおける1人あたりの人体発湿, kg/s, [i]
    x_hum_psn_i_n = x_35.get_x_hum_psn_is_n(theta_r_is_n)

    # ステップnの室iにおける人体潜熱, kg/s, [i]
    return n_hum_i_n * x_hum_psn_i_n





