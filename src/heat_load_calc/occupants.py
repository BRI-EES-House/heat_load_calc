import numpy as np

from heat_load_calc.global_number import get_l_wtr
from heat_load_calc.operation_mode import OperationMode


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


def get_v_hum_is_n(
        operation_mode_is_n: np.ndarray,
        is_radiative_heating_is: np.ndarray,
        is_radiative_cooling_is: np.ndarray
) -> np.ndarray:
    """在室者周りの風速を求める。

    Args:
        operation_mode_is_n: ステップnにおける室iの運転状態, [i, 1]
        is_radiative_heating_is: 放射暖房の有無, [i, 1]
        is_radiative_cooling_is: 放射冷房の有無, [i, 1]

    Returns:
        ステップnにおける室iの在室者周りの風速, m/s, [i, 1]
    """

    # 在室者周りの風速はデフォルトで 0.0 m/s とおく
    v_hum_is_n = np.zeros_like(operation_mode_is_n, dtype=float)

    # 暖房をしてかつそれが放射暖房ではない場合の風速を 0.2 m/s とする
    v_hum_is_n[(operation_mode_is_n == OperationMode.HEATING) & np.logical_not(is_radiative_heating_is)] = 0.2

    # 冷房をしてかつそれが放射冷房ではない場合の風速を 0.2 m/s とする
    v_hum_is_n[(operation_mode_is_n == OperationMode.COOLING) & np.logical_not(is_radiative_cooling_is)] = 0.2

    # 暖冷房をせずに窓を開けている時の風速を 0.1 m/s とする
    v_hum_is_n[operation_mode_is_n == OperationMode.STOP_OPEN] = 0.1

    # 上記に当てはまらない場合の風速は 0.0 m/s のままである。

    return v_hum_is_n


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


