import numpy as np
from functools import partial

from heat_load_calc import pmv, occupants
from heat_load_calc.operation_mode import OperationMode


def make_get_operation_mode_is_n_function(
        ac_method: str,
        ac_demand_is_ns: np.ndarray,
        is_radiative_heating_is: np.ndarray,
        is_radiative_cooling_is: np.ndarray,
        met_is: float
):
    if ac_method == 'simple':

        return partial(
            _get_operation_mode_simple_is_n,
            ac_demand_is_ns=ac_demand_is_ns
        )

    elif ac_method == 'pmv':

        return partial(
            _get_operation_mode_pmv_is_n,
            ac_demand_is_ns=ac_demand_is_ns,
            is_radiative_heating_is=is_radiative_heating_is,
            is_radiative_cooling_is=is_radiative_cooling_is,
            method='constant',
            met_is=met_is
        )

    else:

        raise Exception()


def _get_operation_mode_simple_is_n(
        ac_demand_is_ns: np.ndarray,
        operation_mode_is_n_mns: np.ndarray,
        p_v_r_is_n: np.ndarray,
        theta_mrt_hum_is_n: np.ndarray,
        theta_r_is_n: np.ndarray,
        n: int
):

    ac_demand_is_n = ac_demand_is_ns[:, n].reshape(-1, 1)

    v = np.full_like(operation_mode_is_n_mns, OperationMode.STOP_CLOSE)

    v[ac_demand_is_n > 0] = OperationMode.HEATING_AND_COOLING

    return v


def _get_operation_mode_pmv_is_n(
        ac_demand_is_ns: np.ndarray,
        is_radiative_cooling_is: np.ndarray,
        is_radiative_heating_is: np.ndarray,
        method: str,
        operation_mode_is_n_mns: np.ndarray,
        p_v_r_is_n: np.ndarray,
        theta_mrt_hum_is_n: np.ndarray,
        theta_r_is_n: np.ndarray,
        met_is: np.ndarray,
        n: int
):

    # ステップnにおける室iの在室者周りの風速, m/s, [i, 1]
    v_hum_is_n_mns = occupants.get_v_hum_is_n(
        operation_mode_is_n=operation_mode_is_n_mns,
        is_radiative_heating_is=is_radiative_heating_is,
        is_radiative_cooling_is=is_radiative_cooling_is
    )

    # 厚着時のClo値
    clo_heavy = occupants.get_clo_heavy()

    # 中間着時のClo値
    clo_middle = occupants.get_clo_middle()

    # 薄着時のClo値
    clo_light = occupants.get_clo_light()

    # met_is = np.full_like(theta_r_is_n, fill_value=1.0, dtype=float)

    pmv_heavy_is_n = pmv.get_pmv_is_n(
        p_a_is_n=p_v_r_is_n,
        theta_r_is_n=theta_r_is_n,
        theta_mrt_is_n=theta_mrt_hum_is_n,
        clo_is_n=clo_heavy,
        v_hum_is_n=v_hum_is_n_mns,
        met_is=met_is,
        method=method
    )

    pmv_middle_is_n = pmv.get_pmv_is_n(
        p_a_is_n=p_v_r_is_n,
        theta_r_is_n=theta_r_is_n,
        theta_mrt_is_n=theta_mrt_hum_is_n,
        clo_is_n=clo_middle,
        v_hum_is_n=v_hum_is_n_mns,
        met_is=met_is,
        method=method
    )

    pmv_light_is_n = pmv.get_pmv_is_n(
        p_a_is_n=p_v_r_is_n,
        theta_r_is_n=theta_r_is_n,
        theta_mrt_is_n=theta_mrt_hum_is_n,
        clo_is_n=clo_light,
        v_hum_is_n=v_hum_is_n_mns,
        met_is=met_is,
        method=method
    )

    ac_demand_is_n = ac_demand_is_ns[:, n].reshape(-1, 1)

    # ステップnにおける室iの運転状態, [i, 1]
    operation_mode_is_n = get_operation_mode_is_n(
        ac_demand_is_n=ac_demand_is_n,
        operation_mode_is_n_mns=operation_mode_is_n_mns,
        pmv_heavy_is_n=pmv_heavy_is_n,
        pmv_middle_is_n=pmv_middle_is_n,
        pmv_light_is_n=pmv_light_is_n
    )

    return operation_mode_is_n


def get_operation_mode_is_n(
        ac_demand_is_n: np.ndarray,
        operation_mode_is_n_mns: np.ndarray,
        pmv_heavy_is_n: np.ndarray,
        pmv_middle_is_n: np.ndarray,
        pmv_light_is_n: np.ndarray
) -> np.ndarray:
    """運転モードを決定する。

    Args:
        ac_demand_is_n: ステップnにおける室iの空調需要の有無, 0.0~1.0, [i, 1]
        operation_mode_is_n_mns: ステップn-1における室iの運転状態, [i, 1]
        pmv_heavy_is_n: ステップnにおける室iの厚着時のPMV, [i, 1]
        pmv_middle_is_n: ステップnにおける室iの中間着時のPMV, [i, 1]
        pmv_light_is_n: ステップnにおける室iの薄着時のPMV, [i, 1]

    Returns:
        ステップnの室iにおける運転状態, [i, 1]
    """

    return np.vectorize(get_operation_mode_i_n)(
        ac_demand_is_n, operation_mode_is_n_mns, pmv_heavy_is_n, pmv_middle_is_n, pmv_light_is_n)


def get_operation_mode_i_n(
        ac_demand_i_n: float,
        operation_mode_i_n_mns: OperationMode,
        pmv_heavy_i_n: float,
        pmv_middle_i_n: float,
        pmv_light_i_n: float
) -> OperationMode:
    """運転モードを決定する。

    Args:
        ac_demand_i_n: ステップnにおける室iの空調需要の有無, 0.0～1.0
        operation_mode_i_n_mns: ステップn-1における室iの運転状態
        pmv_heavy_i_n: ステップnにおける室iの厚着時のPMV
        pmv_middle_i_n: ステップnにおける室iの中間着時のPMV
        pmv_light_i_n: ステップnにおける室iの薄着時のPMV

    Returns:
        ステップnにおける室iの運転状態
    """

    if ac_demand_i_n > 0.0:  # 空調需要がある場合

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

