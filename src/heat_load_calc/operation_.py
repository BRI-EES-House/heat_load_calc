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
            operation_mode_is_n_mns: np.ndarray,
            x_r_is_n: np.ndarray,
            theta_mrt_hum_is_n: np.ndarray,
            theta_r_is_n: np.ndarray,
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
            x_r_is_n:
            theta_mrt_hum_is_n:
            theta_r_is_n:
            n:
            is_radiative_heating_is:
            is_radiative_cooling_is:
            met_is:
            theta_r_ot_ntr_non_nv_is_n_pls: ステップn+1における自然風非利用時の自然作用温度, degree C, [i, 1]
            theta_r_ot_ntr_nv_is_n_pls: ステップn+1における自然風利用時の自然作用温度, degree C, [i, 1]

        Returns:

        """

        upper_target_is_n = self._upper_target_is_ns[:, n].reshape(-1, 1)
        lower_target_is_n = self._lower_target_is_ns[:, n].reshape(-1, 1)
        ac_demand_is_n = self._ac_demand_is_ns[:, n].reshape(-1, 1)

        if self.ac_method in [ACMethod.AIR_TEMPERATURE, ACMethod.SIMPLE, ACMethod.OT]:

            return _get_operation_mode_simple_is_n(
                n_rm=self._n_rm,
                theta_r_ot_ntr_non_nv_is_n_pls=theta_r_ot_ntr_non_nv_is_n_pls,
                theta_r_ot_ntr_nv_is_n_pls=theta_r_ot_ntr_nv_is_n_pls,
                upper_target_is_n=upper_target_is_n,
                lower_target_is_n=lower_target_is_n,
                ac_demand_is_n=ac_demand_is_n
            )

        elif self.ac_method == ACMethod.PMV:

            # ステップnにおける室iの水蒸気圧, Pa, [i, 1]
            p_v_r_is_n = psy.get_p_v_r_is_n(x_r_is_n=x_r_ntr_non_nv_is_n_pls)

            return _get_operation_mode_pmv_is_n(
                is_radiative_cooling_is=is_radiative_cooling_is,
                is_radiative_heating_is=is_radiative_heating_is,
                method='constant',
                operation_mode_is_n_mns=operation_mode_is_n_mns,
                p_v_r_is_n=p_v_r_is_n,
                theta_mrt_hum_is_n=theta_mrt_hum_ntr_non_nv_is_n_pls,
                theta_r_is_n=theta_r_ot_ntr_non_nv_is_n_pls,
                met_is=met_is,
                n=n,
                upper_target_is_n=upper_target_is_n,
                lower_target_is_n=lower_target_is_n,
                ac_demand_is_n=ac_demand_is_n,
                theta_r_ot_ntr_non_nv_is_n_pls=theta_r_ot_ntr_non_nv_is_n_pls,
                theta_r_ot_ntr_nv_is_n_pls=theta_r_ot_ntr_nv_is_n_pls,
                theta_r_ntr_non_nv_is_n_pls=theta_r_ntr_non_nv_is_n_pls,
                theta_r_ntr_nv_is_n_pls=theta_r_ntr_nv_is_n_pls,
                theta_mrt_hum_ntr_non_nv_is_n_pls=theta_mrt_hum_ntr_non_nv_is_n_pls,
                theta_mrt_hum_ntr_nv_is_n_pls=theta_mrt_hum_ntr_nv_is_n_pls,
                x_r_ntr_non_nv_is_n_pls=x_r_ntr_non_nv_is_n_pls,
                x_r_ntr_nv_is_n_pls=x_r_ntr_nv_is_n_pls
            )


    def make_get_theta_target_is_n_function(
            self,
            is_radiative_heating_is: np.ndarray,
            is_radiative_cooling_is: np.ndarray,
            met_is: np.ndarray,
            ac_setting_is_ns: np.ndarray
    ) -> Callable[[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:

        if self.ac_method in [ACMethod.AIR_TEMPERATURE, ACMethod.SIMPLE, ACMethod.OT]:

            return partial(
                _get_theta_target_simple,
                theta_lower_target_is_ns=self._lower_target_is_ns,
                theta_upper_target_is_ns=self._upper_target_is_ns
            )

        elif self.ac_method == ACMethod.PMV:
            return partial(
                _get_theta_target,
                is_radiative_heating_is=is_radiative_heating_is,
                is_radiative_cooling_is=is_radiative_cooling_is,
                method='constant',
                met_is=met_is
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
        n_rm,
        theta_r_ot_ntr_non_nv_is_n_pls,
        theta_r_ot_ntr_nv_is_n_pls,
        upper_target_is_n,
        lower_target_is_n,
        ac_demand_is_n
):

    v = np.full((n_rm, 1), OperationMode.STOP_CLOSE)

    is_op = ac_demand_is_n > 0

    v[is_op & (theta_r_ot_ntr_non_nv_is_n_pls > upper_target_is_n) & (theta_r_ot_ntr_nv_is_n_pls > upper_target_is_n)] = OperationMode.COOLING
    v[is_op & (theta_r_ot_ntr_non_nv_is_n_pls > upper_target_is_n) & (theta_r_ot_ntr_nv_is_n_pls <= upper_target_is_n)] = OperationMode.STOP_OPEN
    v[is_op & (theta_r_ot_ntr_non_nv_is_n_pls < lower_target_is_n)] = OperationMode.HEATING

    return v


def _get_operation_mode_pmv_is_n(
        is_radiative_cooling_is: np.ndarray,
        is_radiative_heating_is: np.ndarray,
        method: str,
        operation_mode_is_n_mns: np.ndarray,
        p_v_r_is_n: np.ndarray,
        theta_mrt_hum_is_n: np.ndarray,
        theta_r_is_n: np.ndarray,
        met_is: np.ndarray,
        n: int,
        upper_target_is_n: np.ndarray,
        lower_target_is_n: np.ndarray,
        ac_demand_is_n: np.ndarray,
        theta_r_ot_ntr_non_nv_is_n_pls: np.ndarray,
        theta_r_ot_ntr_nv_is_n_pls: np.ndarray,
        theta_r_ntr_non_nv_is_n_pls: np.ndarray,
        theta_r_ntr_nv_is_n_pls: np.ndarray,
        theta_mrt_hum_ntr_non_nv_is_n_pls: np.ndarray,
        theta_mrt_hum_ntr_nv_is_n_pls: np.ndarray,
        x_r_ntr_non_nv_is_n_pls: np.ndarray,
        x_r_ntr_nv_is_n_pls: np.ndarray

):

    is_window_open_is_n = OperationMode.u_is_window_open(oms=operation_mode_is_n_mns)
    is_convective_ac_is_n = OperationMode.u_is_convective_ac(oms=operation_mode_is_n_mns, is_radiative_heating_is=is_radiative_heating_is, is_radiative_cooling_is=is_radiative_cooling_is)

    # ステップnにおける室iの在室者周りの風速, m/s, [i, 1]
    v_hum_is_n_mns = occupants.get_v_hum_is_n(
        is_window_open_is_n=is_window_open_is_n,
        is_convective_ac_is_n=is_convective_ac_is_n
    )

    # 厚着時のClo値
    clo_heavy = occupants.get_clo_heavy()

    # 中間着時のClo値
    clo_middle = occupants.get_clo_middle()

    # 薄着時のClo値
    clo_light = occupants.get_clo_light()

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


