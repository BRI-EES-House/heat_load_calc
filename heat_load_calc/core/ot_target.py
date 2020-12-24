from typing import Tuple, Callable
import numpy as np

from heat_load_calc.core.operation_mode import OperationMode
from heat_load_calc.core import occupants


def make_get_ot_target_and_h_hum_function(
        is_radiative_heating_is: np.ndarray,
        is_radiative_cooling_is: np.ndarray
) -> Callable[[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray], Tuple]:
    """
    作用温度と人体まわりの熱伝達率を計算する関数を取得する。
    Args:
        is_radiative_heating_is: 放射暖房を行うか否か, [i, 1]
        is_radiative_cooling_is: 放射冷房を行うか否か, [i, 1]
    Returns:
        作用温度と人体まわりの熱伝達率を計算する関数
    Notes:
        この関数は以下の引数と戻り値を持つ。
            Args：
                theta_r_is_n: ステップnにおける室iの空気温度, degree C, [i, 1]
                theta_mrt_is_n: ステップnにおける室iの在室者の平均放射温度, degree C, [i, 1]
                x_r_is_n: ステップnにおける室iの絶対湿度, kg/kgDA, [i, 1]
                operation_mode_is_n_mns: ステップn-1における室iの運転状態, [i, 1]
                ac_demand_is_n: ステップnにおける室iの空調需要の有無, 0.0～1.0, [i, 1]
            Returns:
                ステップnにおける室iの在室者周りの対流熱伝達率, W/m2K, [i, 1]
                ステップnにおける室iの在室者周りの放射熱伝達率, W/m2K, [i, 1]
                ステップnの室iにおける運転モード, [i, 1]
                ステップnの室iにおける目標作用温度下限値, degree C, [i]
                ステップnの室iにおける目標作用温度上限値, degree C, [i]
                その他の備考情報を含むタプル（何の情報が含まれるかは関数の種類による。）
    """

    def get_ot_target_and_h_hum(
            theta_r_is_n: np.ndarray,
            theta_mrt_hum_is_n: np.ndarray,
            x_r_is_n: np.ndarray,
            operation_mode_is_n_mns: np.ndarray,
            ac_demand_is_n: np.ndarray
    ):
        h_hum_c_is_n, h_hum_r_is_n, operation_mode_is_n, theta_ot_target_is_n, remarks_n = \
            occupants._get_ot_target_and_h_hum_with_pmv(
                x_r_is_n=x_r_is_n,
                operation_mode_is_n_mns=operation_mode_is_n_mns,
                is_radiative_heating_is=np.array(is_radiative_heating_is).reshape(-1, 1),
                is_radiative_cooling_is=np.array(is_radiative_cooling_is).reshape(-1, 1),
                theta_r_is_n=theta_r_is_n,
                theta_mrt_is_n=theta_mrt_hum_is_n,
                ac_demand_is_n=ac_demand_is_n,
                method='constant'
            )

        theta_lower_target_is_n = np.zeros_like(operation_mode_is_n, dtype=float)
        theta_lower_target_is_n[operation_mode_is_n == OperationMode.HEATING] \
            = theta_ot_target_is_n[operation_mode_is_n == OperationMode.HEATING]

        theta_upper_target_is_n = np.zeros_like(operation_mode_is_n, dtype=float)
        theta_upper_target_is_n[operation_mode_is_n == OperationMode.COOLING] \
            = theta_ot_target_is_n[operation_mode_is_n == OperationMode.COOLING]

        return h_hum_c_is_n, h_hum_r_is_n, operation_mode_is_n, theta_lower_target_is_n, theta_upper_target_is_n,\
            remarks_n

    return get_ot_target_and_h_hum


