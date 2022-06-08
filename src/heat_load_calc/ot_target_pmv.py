import numpy as np
from functools import partial

from heat_load_calc.operation_mode import OperationMode
from heat_load_calc import pmv


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


def make_get_theta_target_is_n_function(
        is_radiative_heating_is: np.ndarray,
        is_radiative_cooling_is: np.ndarray,
        met_is: np.ndarray
):
    return partial(
        _get_theta_target,
        is_radiative_heating_is=is_radiative_heating_is,
        is_radiative_cooling_is=is_radiative_cooling_is,
        method='constant',
        met_is=met_is
    )


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
    v_hum_is_n_mns = get_v_hum_is_n(
        operation_mode_is_n=operation_mode_is_n_mns,
        is_radiative_heating_is=is_radiative_heating_is,
        is_radiative_cooling_is=is_radiative_cooling_is
    )

    # 厚着時のClo値
    clo_heavy = get_clo_heavy()

    # 中間着時のClo値
    clo_middle = get_clo_middle()

    # 薄着時のClo値
    clo_light = get_clo_light()

    met_is = np.full_like(theta_r_is_n, fill_value=1.0, dtype=float)

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


def _get_theta_target(
        is_radiative_cooling_is: np.ndarray,
        is_radiative_heating_is: np.ndarray,
        method: str,
        operation_mode_is_n: np.ndarray,
        p_v_r_is_n: np.ndarray,
        theta_mrt_hum_is_n: np.ndarray,
        theta_r_is_n: np.ndarray,
        met_is: np.ndarray
):

    # ステップnの室iにおけるClo値, [i, 1]
    clo_is_n = get_clo_is_n(operation_mode_is_n=operation_mode_is_n)

    # ステップnにおける室iの在室者周りの風速, m/s, [i, 1]
    v_hum_is_n = get_v_hum_is_n(
        operation_mode_is_n=operation_mode_is_n,
        is_radiative_heating_is=is_radiative_heating_is,
        is_radiative_cooling_is=is_radiative_cooling_is
    )

    # ステップnの室iにおける目標PMV, [i, 1]
    pmv_target_is_n = get_pmv_target_is_n(operation_mode_is_n)

    # ステップnにおける室iの目標作用温度, degree C, [i, 1]
    theta_ot_target_is_n = np.zeros_like(operation_mode_is_n, dtype=float)

    # 目標作用温度を計算する必要の有無（必要あり = True, 必要なし = False)
    # 計算する必要がない場合は、0.0（初期値）とする。
    # 計算する必要がある場合は、上書きする。
    f = (operation_mode_is_n == OperationMode.HEATING) | (operation_mode_is_n == OperationMode.COOLING)

    # (1) ステップ n における室 i の在室者周りの対流熱伝達率, W/m2K, [i, 1]
    # (2) ステップ n における室 i の在室者周りの放射熱伝達率, W/m2K, [i, 1]
    # (3) ステップ n における室 i の在室者周りの総合熱伝達率, W/m2K, [i, 1]
    h_hum_c_is_n, h_hum_r_is_n, h_hum_is_n = pmv.get_h_hum(
        theta_mrt_is_n=theta_mrt_hum_is_n,
        theta_r_is_n=theta_r_is_n,
        clo_is_n=clo_is_n,
        v_hum_is_n=v_hum_is_n,
        method=method,
        met_is=met_is
    )

    theta_ot_target_dsh_is_n = pmv.get_theta_ot_target(
        clo_is_n=clo_is_n,
        p_a_is_n=p_v_r_is_n,
        h_hum_is_n=h_hum_is_n,
        met_is=met_is,
        pmv_target_is_n=pmv_target_is_n
    )

    theta_ot_target_is_n[f] = theta_ot_target_dsh_is_n[f]

    theta_lower_target_is_n = np.zeros_like(operation_mode_is_n, dtype=float)
    theta_lower_target_is_n[operation_mode_is_n == OperationMode.HEATING] \
        = theta_ot_target_is_n[operation_mode_is_n == OperationMode.HEATING]
    theta_upper_target_is_n = np.zeros_like(operation_mode_is_n, dtype=float)
    theta_upper_target_is_n[operation_mode_is_n == OperationMode.COOLING] \
        = theta_ot_target_is_n[operation_mode_is_n == OperationMode.COOLING]

    return theta_lower_target_is_n, theta_upper_target_is_n, h_hum_c_is_n, h_hum_r_is_n, v_hum_is_n, clo_is_n




# region 本モジュール内でのみ参照される関数


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


def get_clo_is_n(
        operation_mode_is_n: np.ndarray
) -> np.ndarray:
    """運転モードに応じた在室者のClo値を決定する。

    Args:
        operation_mode_is_n: ステップnにおける室iの運転状態, [i, 1]

    Returns:
        ステップnにおける室iの在室者のClo値, [i, 1]
    """

    # ステップnにおける室iの在室者のClo値, [i, 1]
    clo_is_n = np.zeros_like(operation_mode_is_n, dtype=float)

    # 運転方法に応じてclo値の設定を決定する。

    # 暖房運転時の場合は厚着とする。
    clo_is_n[operation_mode_is_n == OperationMode.HEATING] = get_clo_heavy()

    # 冷房運転時の場合は薄着とする。
    clo_is_n[operation_mode_is_n == OperationMode.COOLING] = get_clo_light()

    # 暖冷房停止時は、窓の開閉によらず中間着とする。
    clo_is_n[operation_mode_is_n == OperationMode.STOP_OPEN] = get_clo_middle()
    clo_is_n[operation_mode_is_n == OperationMode.STOP_CLOSE] = get_clo_middle()

    return clo_is_n


def get_pmv_target_is_n(
        operation_mode_is_n: np.ndarray
) -> np.ndarray:
    """運転モードから目標とするPMVを決定する。

    Args:
        operation_mode_is_n: ステップnの室iにおける運転状況, [i, 1]

    Returns:
        ステップnの室iにおける目標PMV, [i, 1]
    """

    pmv_target_is_n = np.zeros_like(operation_mode_is_n, dtype=float)

    pmv_target_is_n[operation_mode_is_n == OperationMode.HEATING] = -0.5
    pmv_target_is_n[operation_mode_is_n == OperationMode.COOLING] = 0.5
    pmv_target_is_n[operation_mode_is_n == OperationMode.STOP_OPEN] = 0.0
    pmv_target_is_n[operation_mode_is_n == OperationMode.STOP_CLOSE] = 0.0

    return pmv_target_is_n


# endregion
