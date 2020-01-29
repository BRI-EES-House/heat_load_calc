import numpy as np

from a39_global_parameters import OperationMode
import a35_PMV as a35


def get_theta_ot_target_is_n(
        p_a_is_n: np.ndarray, h_hum_is_n: np.ndarray,
        operation_mode_is_n: np.ndarray, clo_is_n: np.ndarray, theta_cl_is_n: np.ndarray
) -> np.ndarray:
    """目標作用温度を計算する。

    Args:
        p_a_is_n: ステップnの室iにおける水蒸気圧, Pa
        h_hum_is_n: ステップnの室iにおける人体周りの総合熱伝達率, W/m2K, [i]
        operation_mode_is_n: ステップnの室iにおける運転モード, [i]
        clo_is_n: ステップnの室iにおけるClo値, [i]
        theta_cl_is_n: ステップnの室iにおける着衣温度, degree C [i]

    Returns:
        ステップnの室iにおける目標作用温度, degree C, [i]
    """

    # ステップnの室iにおける目標PMV, [i]
    pmv_target_is_n = np.vectorize(get_pmv_target_i_n)(operation_mode_is_n)

    return np.where(
        (operation_mode_is_n == OperationMode.HEATING) | (operation_mode_is_n == OperationMode.COOLING),
        a35.get_theta_ot_target(
            theta_cl_is_n=theta_cl_is_n,
            clo_is_n=clo_is_n,
            p_a_is_n=p_a_is_n,
            h_hum_is_n=h_hum_is_n,
            pmv_target_is_n=pmv_target_is_n
        ),
        0.0
    )


def get_pmv_target_i_n(operation_mode_i_n):
    """運転モードから目標とするPMVを決定する。

    Args:
        operation_mode_i_n: ステップnの室iにおける運転モード


    Returns:
        ステップnの室iにおける目標PMV
    """

    return {
        OperationMode.HEATING: -0.5,
        OperationMode.COOLING: 0.5,
        OperationMode.STOP_OPEN: 0.0,
        OperationMode.STOP_CLOSE: 0.0
    }[operation_mode_i_n]


def get_theta_cl_is_n(
        operation_mode_is_n: np.ndarray,
        theta_cl_heavy_is_n: np.ndarray, theta_cl_middle_is_n: np.ndarray, theta_cl_light_is_n: np.ndarray
) -> np.ndarray:
    """運転モードから着衣温度を決定する。

    Args:
        operation_mode_is_n: ステップnの室iにおける運転モード, [i]
        theta_cl_heavy_is_n: ステップnの室iにおける厚着の場合の着衣温度, degree C, [i]
        theta_cl_middle_is_n: ステップnの室iにおける中間着の場合の着衣温度, degree C , [i]
        theta_cl_light_is_n: ステップnの室iにおける薄着の場合の着衣温度, degree C, [i]

    Returns:
        ステップnの室iにおける着衣温度, degree C, [i]
    """

    return np.vectorize(get_theta_cl_i_n)(
        operation_mode_is_n, theta_cl_heavy_is_n, theta_cl_middle_is_n, theta_cl_light_is_n)


def get_theta_cl_i_n(
        operation_mode_i_n: OperationMode,
        theta_cl_heavy_i_n: float, theta_cl_middle_i_n: float, theta_cl_light_i_n: float
) -> float:
    """運転モードから着衣温度を決定する。

    Args:
        operation_mode_i_n: ステップnの室iにおける運転モード
        theta_cl_heavy_i_n: ステップnの室iにおける厚着の場合の着衣温度, degree C
        theta_cl_middle_i_n: ステップnの室iにおける中間着の場合の着衣温度, degree C
        theta_cl_light_i_n: ステップnの室iにおける薄着の場合の着衣温度, degree C

    Returns:
        ステップnの室iにおける着衣温度, degree C
    """

    return {
        OperationMode.HEATING: theta_cl_heavy_i_n,
        OperationMode.COOLING: theta_cl_light_i_n,
        OperationMode.STOP_OPEN: theta_cl_middle_i_n,
        OperationMode.STOP_CLOSE: theta_cl_middle_i_n
    }[operation_mode_i_n]


def get_clo_is_n(
        operation_mode_is_n: np.ndarray, clo_heavy_is_n: np.ndarray, clo_middle_is_n: np.ndarray, clo_light_is_n: np.ndarray
) -> np.ndarray:
    """運転モードに応じたClo値を決定する。

    Args:
        operation_mode_is_n: ステップnの室iにおける運転モード, [i]

    Returns:
        ステップnの室iにおけるClo値, [i]
    """

    return np.vectorize(get_clo_i_n)(operation_mode_is_n, clo_heavy_is_n, clo_middle_is_n, clo_light_is_n)


def get_clo_i_n(
        operation_mode_i_n: OperationMode, clo_heavy_is_n: float, clo_middle_is_n: float, clo_light_is_n: float
) -> float:
    """運転モードに応じたClo値を決定する。

    Args:
        operation_mode_i_n: ステップnの室iにおける運転モード

    Returns:
        ステップnの室iにおけるClo値
    """

    return {
        OperationMode.HEATING: clo_heavy_is_n,
        OperationMode.COOLING: clo_light_is_n,
        OperationMode.STOP_OPEN: clo_middle_is_n,
        OperationMode.STOP_CLOSE: clo_middle_is_n
    }[operation_mode_i_n]


def get_operation_mode_is_n(
        ac_demand_is_n: np.ndarray,
        operation_mode_is_n_mns: np.ndarray,
        pmv_heavy_is_n: np.ndarray,
        pmv_middle_is_n: np.ndarray,
        pmv_light_is_n: np.ndarray
) -> np.ndarray:
    """運転モードを決定する。

    Args:
        ac_demand_is_n: ステップnの室iにおける空調需要の有無, [i]
        operation_mode_is_n_mns: ステップn-1の室iにおける運転モード, [i]
        pmv_heavy_is_n: ステップnの室iにおける厚着をした場合のPMV, [i]
        pmv_middle_is_n: ステップnの室iにおける中間着をした場合のPMV, [i]
        pmv_light_is_n: ステップnの室iにおける薄着をした場合のPMV, [i]

    Returns:
        ステップnの室iにおける運転モード, [i]
    """

    return np.vectorize(get_operation_mode_i_n)(
        ac_demand_is_n, operation_mode_is_n_mns, pmv_heavy_is_n, pmv_middle_is_n, pmv_light_is_n)


def get_operation_mode_i_n(
        ac_demand_i_n: bool, operation_mode_i_n_mns: OperationMode,
        pmv_heavy_i_n: float, pmv_middle_i_n: float, pmv_light_i_n: float) -> OperationMode:
    """運転モードを決定する。

    Args:
        ac_demand_i_n: ステップnの室iにおける空調需要の有無
        operation_mode_i_n_mns: ステップn-1の室iにおける運転モード
        pmv_heavy_i_n: ステップnの室iにおける厚着をした場合のPMV
        pmv_middle_i_n: ステップnの室iにおける中間着をした場合のPMV
        pmv_light_i_n: ステップnの室iにおける薄着をした場合のPMV

    Returns:
        ステップnの室iにおける運転モード
    """

    if ac_demand_i_n:  # 空調需要がある場合

        if operation_mode_i_n_mns == OperationMode.HEATING:

            if pmv_heavy_i_n <= 0.7:
                return OperationMode.HEATING
            elif pmv_light_i_n >= 0.7:
                return OperationMode.COOLING
            else:
                return OperationMode.STOP_CLOSE

        elif operation_mode_i_n_mns == OperationMode.COOLING:

            if pmv_light_i_n >= -0.7:
                return OperationMode.COOLING
            elif pmv_heavy_i_n <= -0.7:
                return OperationMode.HEATING
            else:
                return OperationMode.STOP_CLOSE

        elif operation_mode_i_n_mns == OperationMode.STOP_OPEN:

            if pmv_light_i_n >= 0.7:
                return OperationMode.COOLING
            elif pmv_heavy_i_n <= -0.7:
                return OperationMode.HEATING
            elif pmv_middle_i_n <= 0.0:
                return OperationMode.STOP_CLOSE
            else:
                return OperationMode.STOP_OPEN

        elif operation_mode_i_n_mns == OperationMode.STOP_CLOSE:

            if pmv_light_i_n >= 0.7:
                return OperationMode.COOLING
            elif pmv_heavy_i_n <= -0.7:
                return OperationMode.HEATING
            elif pmv_middle_i_n >= 0.0:
                return OperationMode.STOP_OPEN
            else:
                return OperationMode.STOP_CLOSE

        else:
            raise ValueError()

    # 空調需要がない場合（窓閉鎖、空調停止）
    else:
        return OperationMode.STOP_CLOSE

