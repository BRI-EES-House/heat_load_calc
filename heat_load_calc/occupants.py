import numpy as np

from heat_load_calc.global_number import get_l_wtr


def get_x_hum_psn_is_n(theta_r_is_n: np.ndarray) -> np.ndarray:
    """Calculate the moisture generated from one occupant in room i at step n.

    Args:
        theta_r_is_n: room temperature of room i at step n, degree C, [I, 1]

    Returns:
        moisture generated from one occupant in room i at step n, kg/s, [I, 1]
    """

    # latent heat of vaporization of water, J/kg
    l_wtr = get_l_wtr()

    # sensitive heat generated from one occupant in room i at step n, W, [I, 1]
    q_hum_psn_is_n = get_q_hum_psn_is_n(theta_r_is_n=theta_r_is_n)

    return (119.0 - q_hum_psn_is_n) / l_wtr


def get_q_hum_psn_is_n(theta_r_is_n: np.ndarray) -> np.ndarray:
    """Calculate the sensitive heat generated from one occupant in room i at step n.

    Args:
        theta_r_is_n: room temperature of room i at step n, degree C, [I, 1]

    Returns:
        sensitive heat generated from one occupant in room i at step n, W, [I, 1]
    """

    return np.minimum(63.0 - 4.0 * (theta_r_is_n - 24.0), 119.0)


def get_clo_heavy() -> float:
    """厚着をした場合の在室者のclo値を取得する。

    Returns:
        厚着をした場合の在室者のclo値
    """

    return 1.1


def get_clo_middle() -> float:
    """中間着をした場合の在室者のclo値を取得する。

    Returns:
        中間着をした場合の在室者のclo値
    """

    return 0.7


def get_clo_light() -> float:
    """薄着をした場合の在室者のclo値を取得する。

    Returns:
        薄着をした場合の在室者のclo値
    """

    return 0.3


