import numpy as np
from functools import partial
from enum import Enum

from heat_load_calc.operation_mode import OperationMode
from heat_load_calc import pmv
from heat_load_calc import occupants
from heat_load_calc import operation_


class ACMethod(Enum):

    # PMV 制御
    PMV = 'pmv'
    # OT制御と同じ　互換性を保つために残しているがOTを使用することを推奨する
    SIMPLE = 'simple'
    # OT制御
    OT = 'ot'
    # 空気温度制御
    AIR_TEMPERATURE = 'air_temperature'


def make_get_theta_target_is_n_function(
        ac_method: str,
        is_radiative_heating_is: np.ndarray,
        is_radiative_cooling_is: np.ndarray,
        met_is: np.ndarray,
        ac_setting_is_ns: np.ndarray,
        ac_config: dict
):

    if ac_method in ['air_temperature', 'simple', 'ot']:

        theta_lower_target_is_ns = np.full_like(ac_setting_is_ns, fill_value=np.nan, dtype=float)
        theta_upper_target_is_ns = np.full_like(ac_setting_is_ns, fill_value=np.nan, dtype=float)

        for conf in ac_config:
            theta_lower_target_is_ns[ac_setting_is_ns == conf['mode']] = conf['lower']
            theta_upper_target_is_ns[ac_setting_is_ns == conf['mode']] = conf['upper']

        return partial(
            _get_theta_target_simple,
            theta_lower_target_is_ns=theta_lower_target_is_ns,
            theta_upper_target_is_ns=theta_upper_target_is_ns
        )

    elif ac_method == 'pmv':
        return partial(
            _get_theta_target,
            is_radiative_heating_is=is_radiative_heating_is,
            is_radiative_cooling_is=is_radiative_cooling_is,
            method='constant',
            met_is=met_is
        )
    else:
        raise Exception()


def _get_theta_target_simple(
        p_v_r_is_n: np.ndarray,
        operation_mode_is_n: np.ndarray,
        theta_r_is_n: np.ndarray,
        theta_mrt_hum_is_n: np.ndarray,
        theta_lower_target_is_ns: np.ndarray,
        theta_upper_target_is_ns: np.ndarray,
        n: int
):

    # ステップnの室iにおけるClo値, [i, 1]
    clo_is_n = np.full_like(theta_r_is_n, fill_value=occupants.get_clo_light(), dtype=float)

    # ステップnにおける室iの在室者周りの風速, m/s, [i, 1]
    v_hum_is_n = np.zeros_like(theta_r_is_n, dtype=float)

    h_hum_c_is_n = np.full_like(theta_r_is_n, fill_value=1.0, dtype=float)
    h_hum_r_is_n = np.full_like(theta_r_is_n, fill_value=1.0, dtype=float)

    theta_lower_target_is_n = theta_lower_target_is_ns[:, n].reshape(-1, 1)
    theta_upper_target_is_n = theta_upper_target_is_ns[:, n].reshape(-1, 1)

    return theta_lower_target_is_n, theta_upper_target_is_n, h_hum_c_is_n, h_hum_r_is_n, v_hum_is_n, clo_is_n


def _get_theta_target(
        is_radiative_cooling_is: np.ndarray,
        is_radiative_heating_is: np.ndarray,
        method: str,
        operation_mode_is_n: np.ndarray,
        p_v_r_is_n: np.ndarray,
        theta_mrt_hum_is_n: np.ndarray,
        theta_r_is_n: np.ndarray,
        met_is: np.ndarray,
        n: int
):

    # ステップnの室iにおけるClo値, [i, 1]
    clo_is_n = _get_clo_is_n(operation_mode_is_n=operation_mode_is_n)

    # is_window_open_is_n = operation_mode_is_n == OperationMode.STOP_OPEN
    is_window_open_is_n = OperationMode.u_is_window_open(oms=operation_mode_is_n)
    is_convective_ac_is_n = ((operation_mode_is_n == OperationMode.HEATING) & np.logical_not(is_radiative_heating_is)) | (
                (operation_mode_is_n == OperationMode.COOLING) & np.logical_not(is_radiative_cooling_is))
    is_convective_ac_is_n = OperationMode.u_is_convective_ac(oms=operation_mode_is_n, is_radiative_heating_is=is_radiative_heating_is, is_radiative_cooling_is=is_radiative_cooling_is)

    # ステップnにおける室iの在室者周りの風速, m/s, [i, 1]
    v_hum_is_n = occupants.get_v_hum_is_n(
        is_window_open_is_n=is_window_open_is_n,
        is_convective_ac_is_n=is_convective_ac_is_n
    )

    # ステップnの室iにおける目標PMV, [i, 1]
    pmv_target_is_n = _get_pmv_target_is_n(operation_mode_is_n)

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


def _get_clo_is_n(operation_mode_is_n: np.ndarray) -> np.ndarray:
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
    clo_is_n[operation_mode_is_n == OperationMode.HEATING] = occupants.get_clo_heavy()

    # 冷房運転時の場合は薄着とする。
    clo_is_n[operation_mode_is_n == OperationMode.COOLING] = occupants.get_clo_light()

    # 暖冷房停止時は、窓の開閉によらず中間着とする。
    clo_is_n[operation_mode_is_n == OperationMode.STOP_OPEN] = occupants.get_clo_middle()
    clo_is_n[operation_mode_is_n == OperationMode.STOP_CLOSE] = occupants.get_clo_middle()

    return clo_is_n


def _get_pmv_target_is_n(operation_mode_is_n: np.ndarray) -> np.ndarray:
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


def get_h_hum_is_n_simple(
        operation_mode_is_n: np.ndarray,
        theta_r_is_n: np.ndarray,
        theta_mrt_hum_is_n: np.ndarray
):

    # ステップnの室iにおけるClo値, [i, 1]
    clo_is_n = np.full_like(theta_r_is_n, fill_value=occupants.get_clo_light(), dtype=float)

    # ステップnにおける室iの在室者周りの風速, m/s, [i, 1]
    v_hum_is_n = np.zeros_like(theta_r_is_n, dtype=float)

    h_hum_c_is_n = np.full_like(theta_r_is_n, fill_value=1.0, dtype=float)
    h_hum_r_is_n = np.full_like(theta_r_is_n, fill_value=1.0, dtype=float)

    return h_hum_c_is_n, h_hum_r_is_n


def get_h_hum_is_n_pmv(
        is_radiative_cooling_is: np.ndarray,
        is_radiative_heating_is: np.ndarray,
        method: str,
        operation_mode_is_n: np.ndarray,
        theta_mrt_hum_is_n: np.ndarray,
        theta_r_is_n: np.ndarray,
        met_is: np.ndarray
):

    # ステップnの室iにおけるClo値, [i, 1]
    clo_is_n = _get_clo_is_n(operation_mode_is_n=operation_mode_is_n)

    is_window_open_is_n = OperationMode.u_is_window_open(oms=operation_mode_is_n)
    is_convective_ac_is_n = OperationMode.u_is_convective_ac(oms=operation_mode_is_n, is_radiative_heating_is=is_radiative_heating_is, is_radiative_cooling_is=is_radiative_cooling_is)

    # ステップnにおける室iの在室者周りの風速, m/s, [i, 1]
    v_hum_is_n = occupants.get_v_hum_is_n(
        is_window_open_is_n=is_window_open_is_n,
        is_convective_ac_is_n=is_convective_ac_is_n
    )

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

    return h_hum_c_is_n, h_hum_r_is_n

