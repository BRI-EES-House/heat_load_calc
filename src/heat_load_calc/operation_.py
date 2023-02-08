import numpy as np
from functools import partial
from enum import Enum
from typing import Dict, Tuple, Callable

from heat_load_calc import pmv, occupants
from heat_load_calc.operation_mode import OperationMode
from heat_load_calc import psychrometrics as psy


class ACMethod(Enum):

    # PMV 制御
    PMV = 'pmv'
    # OT制御と同じ　互換性を保つために残しているがOTを使用することを推奨する
    SIMPLE = 'simple'
    # OT制御
    OT = 'ot'
    # 空気温度制御
    AIR_TEMPERATURE = 'air_temperature'


class Operation:

    def __init__(
            self,
            ac_method: ACMethod,
            ac_config: Dict,
            lower_target_is_ns: np.ndarray,
            upper_target_is_ns: np.ndarray,
            ac_demand_is_ns: np.ndarray,
            n_rm
    ):
        self._ac_method = ac_method
        self._ac_config = ac_config
        self._lower_target_is_ns = lower_target_is_ns
        self._upper_target_is_ns = upper_target_is_ns
        self._ac_demand_is_ns = ac_demand_is_ns
        self._n_rm = n_rm

    @classmethod
    def make_operation(cls, d: Dict, ac_setting_is_ns: np.ndarray, ac_demand_is_ns: np.ndarray, n_rm: int):

        ac_method = ACMethod(d['ac_method'])

        if 'ac_config' in d:
            ac_config = d['ac_config']
        else:
            if ac_method in [ACMethod.AIR_TEMPERATURE, ACMethod.SIMPLE, ACMethod.OT]:
                ac_config = [
                    {'mode': 1, 'lower': 20.0, 'upper': 27.0},
                    {'mode': 2, 'lower': 20.0, 'upper': 27.0}
                ]
            elif ac_method == ACMethod.PMV:
                ac_config = [
                    {'mode': 1, 'lower': -0.5, 'upper': 0.5},
                    {'mode': 2, 'lower': -0.5, 'upper': 0.5}
                ]
            else:
                raise Exception()

        lower_target_is_ns = np.full_like(ac_setting_is_ns, fill_value=np.nan, dtype=float)
        upper_target_is_ns = np.full_like(ac_setting_is_ns, fill_value=np.nan, dtype=float)

        for conf in ac_config:
            lower_target_is_ns[ac_setting_is_ns == conf['mode']] = conf['lower']
            upper_target_is_ns[ac_setting_is_ns == conf['mode']] = conf['upper']

        return Operation(
            ac_method=ac_method,
            ac_config=ac_config,
            lower_target_is_ns=lower_target_is_ns,
            upper_target_is_ns=upper_target_is_ns,
            ac_demand_is_ns=ac_demand_is_ns,
            n_rm=n_rm
        )

    @property
    def ac_method(self):
        return self._ac_method

    @property
    def ac_config(self):
        return self._ac_config

    def get_operation_mode_is_n(
            self,
            n: int,
            is_radiative_heating_is: np.ndarray,
            is_radiative_cooling_is: np.ndarray,
            met_is: np.ndarray,
            theta_r_ot_ntr_non_nv_is_n_pls: np.ndarray,
            theta_r_ot_ntr_nv_is_n_pls: np.ndarray,
            theta_r_ntr_non_nv_is_n_pls: np.ndarray,
            theta_r_ntr_nv_is_n_pls: np.ndarray,
            theta_mrt_hum_ntr_non_nv_is_n_pls: np.ndarray,
            theta_mrt_hum_ntr_nv_is_n_pls: np.ndarray,
            x_r_ntr_non_nv_is_n_pls: np.ndarray,
            x_r_ntr_nv_is_n_pls: np.ndarray
    ):
        """

        Args:
            operation_mode_is_n_mns:
            n:
            is_radiative_heating_is:
            is_radiative_cooling_is:
            met_is:
            theta_r_ot_ntr_non_nv_is_n_pls: ステップn+1における自然風非利用時の自然作用温度, degree C, [i, 1]
            theta_r_ot_ntr_nv_is_n_pls: ステップn+1における自然風利用時の自然作用温度, degree C, [i, 1]
            theta_r_ntr_non_nv_is_n_pls:
            theta_r_ntr_nv_is_n_pls:
            theta_mrt_hum_ntr_non_nv_is_n_pls:
            theta_mrt_hum_ntr_nv_is_n_pls:
            x_r_ntr_non_nv_is_n_pls:
            x_r_ntr_nv_is_n_pls:
        Returns:

        """

        upper_target_is_n = self._upper_target_is_ns[:, n].reshape(-1, 1)
        lower_target_is_n = self._lower_target_is_ns[:, n].reshape(-1, 1)
        ac_demand_is_n = self._ac_demand_is_ns[:, n].reshape(-1, 1)

        if self.ac_method in [ACMethod.AIR_TEMPERATURE, ACMethod.SIMPLE, ACMethod.OT]:

            x_cooling_is_n_pls, x_window_open_is_n_pls, x_heating_is_n_pls = _get_operation_mode_simple_is_n(
                theta_r_ot_ntr_non_nv_is_n_pls=theta_r_ot_ntr_non_nv_is_n_pls,
                theta_r_ot_ntr_nv_is_n_pls=theta_r_ot_ntr_nv_is_n_pls,
            )

        elif self.ac_method == ACMethod.PMV:

            x_cooling_is_n_pls, x_window_open_is_n_pls, x_heating_is_n_pls = _get_operation_mode_pmv_is_n(
                is_radiative_cooling_is=is_radiative_cooling_is,
                is_radiative_heating_is=is_radiative_heating_is,
                method='constant',
                met_is=met_is,
                theta_r_ntr_non_nv_is_n_pls=theta_r_ntr_non_nv_is_n_pls,
                theta_r_ntr_nv_is_n_pls=theta_r_ntr_nv_is_n_pls,
                theta_mrt_hum_ntr_non_nv_is_n_pls=theta_mrt_hum_ntr_non_nv_is_n_pls,
                theta_mrt_hum_ntr_nv_is_n_pls=theta_mrt_hum_ntr_nv_is_n_pls,
                x_r_ntr_non_nv_is_n_pls=x_r_ntr_non_nv_is_n_pls,
                x_r_ntr_nv_is_n_pls=x_r_ntr_nv_is_n_pls
            )

        else:
            raise Exception()

        v = np.full((self._n_rm, 1), OperationMode.STOP_CLOSE)

        is_op = ac_demand_is_n > 0

        v[is_op & (x_cooling_is_n_pls > upper_target_is_n) & (x_window_open_is_n_pls > upper_target_is_n)] \
            = OperationMode.COOLING
        v[is_op & (x_cooling_is_n_pls > upper_target_is_n) & (x_window_open_is_n_pls <= upper_target_is_n)] \
            = OperationMode.STOP_OPEN
        v[is_op & (x_heating_is_n_pls < lower_target_is_n)] = OperationMode.HEATING

        return v

    def get_theta_target_is_n(
            self,
            p_v_r_is_n: np.ndarray,
            operation_mode_is_n: np.ndarray,
            theta_r_is_n: np.ndarray,
            theta_mrt_hum_is_n: np.ndarray,
            n: int,
            is_radiative_heating_is: np.ndarray,
            is_radiative_cooling_is: np.ndarray,
            met_is: np.ndarray
    ):

        if self.ac_method in [ACMethod.AIR_TEMPERATURE, ACMethod.SIMPLE, ACMethod.OT]:

            return _get_theta_target_simple(
                p_v_r_is_n=p_v_r_is_n,
                operation_mode_is_n=operation_mode_is_n,
                theta_r_is_n=theta_r_is_n,
                theta_mrt_hum_is_n=theta_mrt_hum_is_n,
                theta_lower_target_is_ns=self._lower_target_is_ns,
                theta_upper_target_is_ns=self._upper_target_is_ns,
                n=n,
                is_radiative_heating_is=is_radiative_heating_is,
                is_radiative_cooling_is=is_radiative_cooling_is
            )

        elif self.ac_method == ACMethod.PMV:

            return _get_theta_target(
                is_radiative_heating_is=is_radiative_heating_is,
                is_radiative_cooling_is=is_radiative_cooling_is,
                method='constant',
                operation_mode_is_n=operation_mode_is_n,
                p_v_r_is_n=p_v_r_is_n,
                theta_mrt_hum_is_n=theta_mrt_hum_is_n,
                theta_r_is_n=theta_r_is_n,
                met_is=met_is,
                n=n,
                theta_lower_target_is_ns=self._lower_target_is_ns,
                theta_upper_target_is_ns=self._upper_target_is_ns
            )

        else:

            raise Exception()


    def get_k_is(self) -> Tuple[np.ndarray, np.ndarray]:
        """

        Returns:
            ステップ n における室 i の人体表面の対流熱伝達率が総合熱伝達率に占める割合, -, [i, 1]
            ステップ n における室 i の人体表面の放射熱伝達率が総合熱伝達率に占める割合, -, [i, 1]
        """

        if self.ac_method == ACMethod.AIR_TEMPERATURE:
            k_c_is = np.full((self._n_rm, 1), 1.0, dtype=float)
            k_r_is = np.full((self._n_rm, 1), 0.0, dtype=float)
        elif self.ac_method in [ACMethod.OT, ACMethod.PMV, ACMethod.SIMPLE]:
            k_c_is = np.full((self._n_rm, 1), 0.5, dtype=float)
            k_r_is = np.full((self._n_rm, 1), 0.5, dtype=float)
        else:
            raise Exception

        return k_c_is, k_r_is


def _get_operation_mode_simple_is_n(
        theta_r_ot_ntr_non_nv_is_n_pls: np.ndarray,
        theta_r_ot_ntr_nv_is_n_pls: np.ndarray,
):

    x_cooling_is_n_pls = theta_r_ot_ntr_nv_is_n_pls
    x_window_open_is_n_pls = theta_r_ot_ntr_non_nv_is_n_pls
    x_heating_is_n_pls = theta_r_ot_ntr_nv_is_n_pls

    return x_cooling_is_n_pls, x_window_open_is_n_pls, x_heating_is_n_pls


def _get_operation_mode_pmv_is_n(
        is_radiative_cooling_is: np.ndarray,
        is_radiative_heating_is: np.ndarray,
        method: str,
        met_is: np.ndarray,
        theta_r_ntr_non_nv_is_n_pls: np.ndarray,
        theta_r_ntr_nv_is_n_pls: np.ndarray,
        theta_mrt_hum_ntr_non_nv_is_n_pls: np.ndarray,
        theta_mrt_hum_ntr_nv_is_n_pls: np.ndarray,
        x_r_ntr_non_nv_is_n_pls: np.ndarray,
        x_r_ntr_nv_is_n_pls: np.ndarray
):

    # ステップnにおける室iの水蒸気圧, Pa, [i, 1]
    p_v_r_ntr_non_nv_is_n_pls = psy.get_p_v_r_is_n(x_r_is_n=x_r_ntr_non_nv_is_n_pls)
    p_v_r_ntr_nv_is_n_pls = psy.get_p_v_r_is_n(x_r_is_n=x_r_ntr_nv_is_n_pls)

    # 薄着時のClo値
    clo_light = occupants.get_clo_light()

    # 厚着時のClo値
    clo_heavy = occupants.get_clo_heavy()

    ### 冷房判定用（窓開け時）のPMV計算

    # 窓を開けている時の風速を 0.1 m/s とする
    v_hum_window_open_is_n = 0.1

    # 冷房判定用（窓開け時）のPMV
    pmv_window_open_is_n = pmv.get_pmv_is_n(
        p_a_is_n=p_v_r_ntr_nv_is_n_pls,
        theta_r_is_n=theta_r_ntr_nv_is_n_pls,
        theta_mrt_is_n=theta_mrt_hum_ntr_nv_is_n_pls,
        clo_is_n=clo_light,
        v_hum_is_n=v_hum_window_open_is_n,
        met_is=met_is,
        method=method
    )

    # 冷房判定用（窓閉め時）のPMV計算

    # 冷房時の風速を対流冷房時0.2m/s・放射冷房時0.0m/sに設定する。
    v_hum_cooling_is_n = np.where(is_radiative_cooling_is, 0.0, 0.2)

    # 冷房判定用（窓閉め時）のPMV
    pmv_cooling_is_n = pmv.get_pmv_is_n(
        p_a_is_n=p_v_r_ntr_non_nv_is_n_pls,
        theta_r_is_n=theta_r_ntr_non_nv_is_n_pls,
        theta_mrt_is_n=theta_mrt_hum_ntr_non_nv_is_n_pls,
        clo_is_n=clo_light,
        v_hum_is_n=v_hum_cooling_is_n,
        met_is=met_is,
        method=method
    )

    # 暖房判定用のPMV計算

    # 暖房時の風速を対流暖房時0.2m/s・放射暖房時0.0m/sに設定する。
    v_hum_heating_is_n = np.where(is_radiative_heating_is, 0.0, 0.2)

    # 暖房判定用のPMV
    pmv_heating_is_n = pmv.get_pmv_is_n(
        p_a_is_n=p_v_r_ntr_non_nv_is_n_pls,
        theta_r_is_n=theta_r_ntr_non_nv_is_n_pls,
        theta_mrt_is_n=theta_mrt_hum_ntr_non_nv_is_n_pls,
        clo_is_n=clo_heavy,
        v_hum_is_n=v_hum_heating_is_n,
        met_is=met_is,
        method=method
    )

    x_cooling_is_n_pls = pmv_cooling_is_n
    x_window_open_is_n_pls = pmv_window_open_is_n
    x_heating_is_n_pls = pmv_heating_is_n

    return x_cooling_is_n_pls, x_window_open_is_n_pls, x_heating_is_n_pls


def _get_theta_target_simple(
        p_v_r_is_n: np.ndarray,
        operation_mode_is_n: np.ndarray,
        theta_r_is_n: np.ndarray,
        theta_mrt_hum_is_n: np.ndarray,
        theta_lower_target_is_ns: np.ndarray,
        theta_upper_target_is_ns: np.ndarray,
        n: int,
        is_radiative_heating_is: np.ndarray,
        is_radiative_cooling_is: np.ndarray,
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
        n: int,
        theta_lower_target_is_ns: np.ndarray,
        theta_upper_target_is_ns: np.ndarray
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


def get_v_hum_is_n(
        operation_mode_is: np.ndarray,
        is_radiative_cooling_is: np.ndarray,
        is_radiative_heating_is: np.ndarray
) -> np.ndarray:
    """在室者周りの風速を求める。

    Args:
        operation_mode_is:
        is_radiative_cooling_is:
        is_radiative_heating_is:

    Returns:
        ステップnにおける室iの在室者周りの風速, m/s, [i, 1]
    """

    # 在室者周りの風速はデフォルトで 0.0 m/s とおく
    v_hum_is_n = np.zeros_like(operation_mode_is, dtype=float)

    # 対流暖房時の風速を 0.2 m/s とする
    v_hum_is_n[(operation_mode_is == OperationMode.HEATING) & np.logical_not(is_radiative_heating_is)] = 0.2
    # 放射暖房時の風速を 0.0 m/s とする
    v_hum_is_n[(operation_mode_is == OperationMode.HEATING) & (is_radiative_heating_is)] = 0.0

    # 対流冷房時の風速を 0.2 m/s とする
    v_hum_is_n[(operation_mode_is == OperationMode.COOLING) & np.logical_not(is_radiative_cooling_is)] = 0.2
    # 放射冷房時の風速を 0.0 m/s とする
    v_hum_is_n[(operation_mode_is == OperationMode.COOLING) & (is_radiative_cooling_is)] = 0.0

    # 暖冷房をせずに窓を開けている時の風速を 0.1 m/s とする
    # 対流暖房・冷房時と窓を開けている時は同時には起こらないことを期待しているが
    # もし同時にTrueの場合は窓を開けている時の風速が優先される（上書きわれる）
    v_hum_is_n[operation_mode_is == OperationMode.STOP_OPEN] = 0.1

    # 上記に当てはまらない場合の風速は 0.0 m/s のままである。

    return v_hum_is_n


def get_clo_is_ns(operation_mode_is: np.ndarray):

    clo_is_ns = np.zeros_like(operation_mode_is, dtype=float)

    # 暖房時は厚着とする。
    clo_is_ns[operation_mode_is == OperationMode.HEATING] = occupants.get_clo_heavy()

    # 冷房時は薄着とする。
    clo_is_ns[operation_mode_is == OperationMode.COOLING] = occupants.get_clo_light()

    # 運転停止（窓開）時は薄着とする。
    clo_is_ns[operation_mode_is == OperationMode.STOP_OPEN] = occupants.get_clo_light()

    # 運転停止（窓閉）時は薄着とする。
    clo_is_ns[operation_mode_is == OperationMode.STOP_CLOSE] = occupants.get_clo_middle()

    return clo_is_ns
