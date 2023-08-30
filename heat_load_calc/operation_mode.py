﻿import numpy as np
from functools import partial
from enum import Enum
from typing import Dict, Tuple, Callable

from heat_load_calc import pmv, occupants
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


class OperationMode(Enum):

    # 冷房
    COOLING = 1

    # 暖房
    HEATING = 2

    # 暖房・冷房停止で窓「開」
    STOP_OPEN = 3

    # 暖房・冷房停止で窓「閉」
    STOP_CLOSE = 4


class Operation:

    def __init__(
            self,
            ac_method: ACMethod,
            x_lower_target_is_ns: np.ndarray,
            x_upper_target_is_ns: np.ndarray,
            r_ac_demand_is_ns: np.ndarray,
            n_rm
    ):
        """

        Args:
            ac_method: 運転モードの決定方法
            x_lower_target_is_ns: ステップ n における室 i の目標下限値
            x_upper_target_is_ns: ステップ n における室 i の目標上限値
            r_ac_demand_is_ns: ステップ n における室 i の空調需要
            n_rm: 室の数
        """
        
        self._ac_method = ac_method
        self._x_lower_target_is_ns = x_lower_target_is_ns
        self._x_upper_target_is_ns = x_upper_target_is_ns
        self._r_ac_demand_is_ns = r_ac_demand_is_ns
        self._n_rm = n_rm

    @classmethod
    def make_operation(cls, d: Dict, t_ac_mode_is_ns: np.ndarray, r_ac_demand_is_ns: np.ndarray, n_rm: int):
        """Operation クラスを作成する。
        Make Operation Class.
        Args:
            d: 運転モードに関する入力情報
            t_ac_mode_is_ns: ステップ n における室 i の空調モード
            r_ac_demand_is_ns: ステップ n における室 i の空調需要
            n_rm: 室の数
        Returns:
            Operation クラス
        """

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

        x_lower_target_is_ns = np.full_like(t_ac_mode_is_ns, fill_value=np.nan, dtype=float)
        x_upper_target_is_ns = np.full_like(t_ac_mode_is_ns, fill_value=np.nan, dtype=float)

        for conf in ac_config:
            x_lower_target_is_ns[t_ac_mode_is_ns == conf['mode']] = conf['lower']
            x_upper_target_is_ns[t_ac_mode_is_ns == conf['mode']] = conf['upper']

        return Operation(
            ac_method=ac_method,
            x_lower_target_is_ns=x_lower_target_is_ns,
            x_upper_target_is_ns=x_upper_target_is_ns,
            r_ac_demand_is_ns=r_ac_demand_is_ns,
            n_rm=n_rm
        )

    @property
    def ac_method(self):
        return self._ac_method

    def get_t_operation_mode_is_n(
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

        if self.ac_method in [ACMethod.AIR_TEMPERATURE, ACMethod.SIMPLE, ACMethod.OT]:

            x_cooling_is_n_pls, x_window_open_is_n_pls, x_heating_is_n_pls = _get_x_is_n_pls_ot_and_air_temperature_control(
                theta_r_ot_ntr_non_nv_is_n_pls=theta_r_ot_ntr_non_nv_is_n_pls,
                theta_r_ot_ntr_nv_is_n_pls=theta_r_ot_ntr_nv_is_n_pls,
            )

        elif self.ac_method == ACMethod.PMV:

            x_cooling_is_n_pls, x_window_open_is_n_pls, x_heating_is_n_pls = _get_x_is_n_pls_pmv_control(
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

        x_upper_target_is_n = self._x_upper_target_is_ns[:, n].reshape(-1, 1)
        x_lower_target_is_n = self._x_lower_target_is_ns[:, n].reshape(-1, 1)
        r_ac_demand_is_n = self._r_ac_demand_is_ns[:, n].reshape(-1, 1)

        is_op = r_ac_demand_is_n > 0

        # ケース 1, 2-3
        t_operation_mode_is_n = np.full((r_ac_demand_is_n.shape[0], 1), OperationMode.STOP_CLOSE)

        # ケース 2-1
        t_operation_mode_is_n[is_op & (x_heating_is_n_pls < x_lower_target_is_n)] = OperationMode.HEATING

        # ケース 2-2-1
        t_operation_mode_is_n[is_op & (x_cooling_is_n_pls > x_upper_target_is_n) & (x_window_open_is_n_pls > x_upper_target_is_n)] \
            = OperationMode.COOLING

        # ケース 2-2-2
        t_operation_mode_is_n[is_op & (x_cooling_is_n_pls > x_upper_target_is_n) & (x_window_open_is_n_pls <= x_upper_target_is_n)] \
            = OperationMode.STOP_OPEN

        return t_operation_mode_is_n

    def get_theta_target_is_n(
            self,
            operation_mode_is_n: np.ndarray,
            theta_r_is_n: np.ndarray,
            theta_mrt_hum_is_n: np.ndarray,
            x_r_ntr_is_n_pls: np.ndarray,
            n: int,
            is_radiative_heating_is: np.ndarray,
            is_radiative_cooling_is: np.ndarray,
            met_is: np.ndarray
    ):

        lower_target_is_n = self._x_lower_target_is_ns[:, n].reshape(-1, 1)
        upper_target_is_n = self._x_upper_target_is_ns[:, n].reshape(-1, 1)

        # ステップnの室iにおけるClo値, [i, 1]
        clo_is_n = _get_clo_is_ns(operation_mode_is_n=operation_mode_is_n)

        # ステップnにおける室iの在室者周りの風速, m/s, [i, 1]
        v_hum_is_n = _get_v_hum_is_n(
            operation_mode_is=operation_mode_is_n,
            is_radiative_heating_is=is_radiative_heating_is,
            is_radiative_cooling_is=is_radiative_cooling_is
        )

        # (1) ステップ n における室 i の在室者周りの対流熱伝達率, W/m2K, [i, 1]
        # (2) ステップ n における室 i の在室者周りの放射熱伝達率, W/m2K, [i, 1]
        # (3) ステップ n における室 i の在室者周りの総合熱伝達率, W/m2K, [i, 1]
        h_hum_c_is_n, h_hum_r_is_n, h_hum_is_n = pmv.get_h_hum(
            theta_mrt_is_n=theta_mrt_hum_is_n,
            theta_r_is_n=theta_r_is_n,
            clo_is_n=clo_is_n,
            v_hum_is_n=v_hum_is_n,
            method='constant',
            met_is=met_is
        )

        if self.ac_method in [ACMethod.AIR_TEMPERATURE, ACMethod.SIMPLE, ACMethod.OT]:

            return lower_target_is_n, upper_target_is_n, h_hum_c_is_n, h_hum_r_is_n

        elif self.ac_method == ACMethod.PMV:

            # ステップnにおける室iの水蒸気圧, Pa, [i, 1]
            p_v_r_is_n = psy.get_p_v_r_is_n(x_r_is_n=x_r_ntr_is_n_pls)

            lower_target_is_n, upper_target_is_n = _get_theta_target(
                operation_mode_is_n=operation_mode_is_n,
                p_v_r_is_n=p_v_r_is_n,
                met_is=met_is,
                lower_target_is_n=lower_target_is_n,
                upper_target_is_n=upper_target_is_n,
                h_hum_is_n=h_hum_is_n,
                clo_is_n=clo_is_n
            )

            return lower_target_is_n, upper_target_is_n, h_hum_c_is_n, h_hum_r_is_n

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


def _get_x_is_n_pls_ot_and_air_temperature_control(
        theta_r_ot_ntr_non_nv_is_n_pls: np.ndarray,
        theta_r_ot_ntr_nv_is_n_pls: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """作用温度制御・空気温度制御の場合の暖房用参照温度・冷房用参照温度・窓開け用参照温度を計算する。
    Calculate the reference temperature for heating, cooling and window-opening in the case of the operative temperature and air temperature controll.
    Args:
        theta_r_ot_ntr_non_nv_is_n_pls: ステップ n+1 における室 i の自然風非利用時の自然作用温度, ℃
        theta_r_ot_ntr_nv_is_n_pls: ステップ n+1 における室 i の自然風利用時の自然作用温度, ℃
    Returns:
        ステップ n+1 における室 i の暖房用参照温度, ℃
        ステップ n+1 における室 i の冷房用参照温度, ℃
        ステップ n+1 における室 i の窓開け用参照温度, ℃
    Note:
        eq.(1a),(1b),(1c)
    """

    x_cooling_is_n_pls = theta_r_ot_ntr_nv_is_n_pls
    x_window_open_is_n_pls = theta_r_ot_ntr_non_nv_is_n_pls
    x_heating_is_n_pls = theta_r_ot_ntr_nv_is_n_pls

    return x_cooling_is_n_pls, x_window_open_is_n_pls, x_heating_is_n_pls


def _get_x_is_n_pls_pmv_control(
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


def _get_theta_target(
        operation_mode_is_n: np.ndarray,
        p_v_r_is_n: np.ndarray,
        met_is: np.ndarray,
        lower_target_is_n: np.ndarray,
        upper_target_is_n: np.ndarray,
        h_hum_is_n: np.ndarray,
        clo_is_n: np.ndarray
):

    f_h = operation_mode_is_n == OperationMode.HEATING
    f_c = operation_mode_is_n == OperationMode.COOLING

    # ステップnにおける室iの目標作用温度, degree C, [i, 1]

    theta_lower_target_is_n = np.zeros_like(operation_mode_is_n, dtype=float)

    theta_lower_target_is_n[f_h] = pmv.get_theta_ot_target(
        clo_is_n=clo_is_n[f_h],
        p_a_is_n=p_v_r_is_n[f_h],
        h_hum_is_n=h_hum_is_n[f_h],
        met_is=met_is[f_h],
        pmv_target_is_n=lower_target_is_n[f_h]
    )

    theta_upper_target_is_n = np.zeros_like(operation_mode_is_n, dtype=float)

    theta_upper_target_is_n[f_c] = pmv.get_theta_ot_target(
        clo_is_n=clo_is_n[f_c],
        p_a_is_n=p_v_r_is_n[f_c],
        h_hum_is_n=h_hum_is_n[f_c],
        met_is=met_is[f_c],
        pmv_target_is_n=upper_target_is_n[f_c]
    )

    return theta_lower_target_is_n, theta_upper_target_is_n


def _get_v_hum_is_n(
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


def _get_clo_is_ns(operation_mode_is_n: np.ndarray):
    """運転モードに応じた在室者のClo値を決定する。

    Args:
        operation_mode_is_n: ステップnにおける室iの運転状態, [i, 1]

    Returns:
        ステップnにおける室iの在室者のClo値, [i, 1]
    """

    # ステップnにおける室iの在室者のClo値, [i, 1]
    clo_is_ns = np.zeros_like(operation_mode_is_n, dtype=float)

    # 運転方法に応じてclo値の設定を決定する。

    # 暖房時は厚着とする。
    clo_is_ns[operation_mode_is_n == OperationMode.HEATING] = occupants.get_clo_heavy()

    # 冷房時は薄着とする。
    clo_is_ns[operation_mode_is_n == OperationMode.COOLING] = occupants.get_clo_light()

    # 運転停止（窓開）時は薄着とする。
    clo_is_ns[operation_mode_is_n == OperationMode.STOP_OPEN] = occupants.get_clo_light()

    # 運転停止（窓閉）時は薄着とする。
    clo_is_ns[operation_mode_is_n == OperationMode.STOP_CLOSE] = occupants.get_clo_middle()

    return clo_is_ns
