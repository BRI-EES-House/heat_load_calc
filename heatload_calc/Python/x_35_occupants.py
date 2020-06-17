# 附属書X35 在室者に関する情報を定義する。

import math
import numpy as np
from typing import Union

import a39_global_parameters as a39
from a39_global_parameters import OperationMode
import psychrometrics as psy


def calc_operation(
        x_r_is_n: np.ndarray,
        operation_mode_is_n_mns: np.ndarray,
        is_radiative_heating_is: np.ndarray,
        is_radiative_cooling_is: np.ndarray,
        theta_r_is_n: np.ndarray,
        theta_cl_is_n: np.ndarray,
        theta_mrt_is_n: np.ndarray,
        ac_demand_is_n: np.ndarray
) -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray):
    """

    Args:
        x_r_is_n: ステップnにおける室iの絶対湿度, kg/kgDA, [i, 1]
        operation_mode_is_n_mns: ステップn-1における室iの運転状態, [i, 1]
            列挙体 OperationMode で表される。
                COOLING ： 冷房
                HEATING : 暖房
                STOP_OPEN : 暖房・冷房停止で窓「開」
                STOP_CLOSE : 暖房・冷房停止で窓「閉」
        is_radiative_heating_is:　放射暖房の有無, [i, 1]
        is_radiative_cooling_is: 放射冷房の有無, [i, 1]
        theta_r_is_n: ステップnにおける室iの空気温度, degree C, [i, 1]
        theta_cl_is_n: ステップnにおける室iの在室者の着衣温度, degree C, [i, 1]
            本来であれば着衣温度と人体周りの対流・放射熱伝達率を未知数とした熱収支式を収束計算等を用いて時々刻々求めるのが望ましい。
            今回、収束計算を回避するために前時刻の着衣温度を用いることにした。
        theta_mrt_is_n: ステップnにおける室iの在室者の平均放射温度, degree C, [i, 1]
        ac_demand_is_n: ステップnにおける室iの空調需要の有無, [i, 1]

    Returns:
        ステップnの室iにおける人体周りの総合熱伝達率, W/m2K, [i, 1]
        ステップnにおける室iの在室者周りの対流熱伝達率, W/m2K, [i, 1]
        ステップnにおける室iの在室者周りの放射熱伝達率, W/m2K, [i, 1]
        ステップnの室iにおける運転モード, [i, 1]
        ステップnの室iにおけるClo値, [i]
        ステップnの室iにおける目標作用温度, degree C, [i]
    """

    # ステップnにおける室iの水蒸気圧, Pa, [i, 1]
    p_v_r_is_n = psy.get_p_v_r_is_n(x_r_is_n=x_r_is_n)

    # ステップnにおける室iの在室者周りの風速, m/s, [i, 1]
    v_hum_is_n = get_v_hum_is_n(
        operation_mode_is_n=operation_mode_is_n_mns,
        is_radiative_heating_is=is_radiative_heating_is,
        is_radiative_cooling_is=is_radiative_cooling_is
    )

    # ステップnにおける室iの在室者周りの対流熱伝達率, W/m2K, [i, 1]
    h_hum_c_is_n = get_h_hum_c_is_n(
        theta_r_is_n=theta_r_is_n,
        theta_cl_is_n=theta_cl_is_n,
        v_hum_is_n=v_hum_is_n
    )

    # ステップnにおける室iの在室者周りの放射熱伝達率, W/m2K, [i, 1]
    h_hum_r_is_n = get_h_hum_r_is_n(
        theta_cl_is_n=theta_cl_is_n,
        theta_mrt_is_n=theta_mrt_is_n
    )

    # ステップnにおける室iの在室者周りの総合熱伝達率, W/m2K, [i, 1]
    h_hum_is_n = h_hum_r_is_n + h_hum_c_is_n

    # ステップnにおける室iの在室者の作用温度, degree C, [i, 1]
    theta_ot_is_n = (h_hum_r_is_n * theta_mrt_is_n + h_hum_c_is_n * theta_r_is_n) / h_hum_is_n

    # 厚着時のClo値
    clo_heavy = get_clo_heavy()

    # 中間着時のClo値
    clo_middle = get_clo_middle()

    # 薄着時のClo値
    clo_light = get_clo_light()

    # ステップnにおける室iの在室者の厚着時のPMV, [i, 1]
    pmv_heavy_is_n = get_pmv_is_n(
        theta_r_is_n=theta_r_is_n,
        clo_is_n=clo_heavy,
        p_a_is_n=p_v_r_is_n,
        h_hum_is_n=h_hum_is_n,
        theta_ot_is_n=theta_ot_is_n
    )

    # ステップnにおける室iの在室者の中間着時のPMV, [i, 1]
    pmv_middle_is_n = get_pmv_is_n(
        theta_r_is_n=theta_r_is_n,
        clo_is_n=clo_middle,
        p_a_is_n=p_v_r_is_n,
        h_hum_is_n=h_hum_is_n,
        theta_ot_is_n=theta_ot_is_n
    )

    # ステップnにおける室iの在室者の薄着時のPMV, [i, 1]
    pmv_light_is_n = get_pmv_is_n(
        theta_r_is_n=theta_r_is_n,
        clo_is_n=clo_light,
        p_a_is_n=p_v_r_is_n,
        h_hum_is_n=h_hum_is_n,
        theta_ot_is_n=theta_ot_is_n
    )

    # ステップnにおける室iの運転状態, [i, 1]
    operation_mode_is_n = get_operation_mode_is_n(
        ac_demand_is_n=ac_demand_is_n,
        operation_mode_is_n_mns=operation_mode_is_n_mns,
        pmv_heavy_is_n=pmv_heavy_is_n,
        pmv_middle_is_n=pmv_middle_is_n,
        pmv_light_is_n=pmv_light_is_n
    )

    # ステップnの室iにおけるClo値, [i, 1]
    clo_is_n = get_clo_is_n(
        operation_mode_is_n=operation_mode_is_n
    )

    # ステップnにおける室iの目標作用温度, degree C, [i]
    theta_ot_target_is_n = get_theta_ot_target_is_n(
        p_v_r_is_n=p_v_r_is_n.flatten(),
        h_hum_is_n=h_hum_is_n.flatten(),
        operation_mode_is_n=operation_mode_is_n.flatten(),
        clo_is_n=clo_is_n.flatten(),
    )

    return h_hum_is_n, h_hum_c_is_n, h_hum_r_is_n, operation_mode_is_n, clo_is_n, theta_ot_target_is_n.reshape(-1, 1)


def get_theta_cl_is_n(
        clo_is_n: Union[np.ndarray, float],
        theta_ot_is_n: np.ndarray,
        h_hum_is_n: np.ndarray
) -> np.ndarray:
    """着衣温度を計算する。

    Args:
        clo_is_n: ステップnにおける室iの在室者のClo値, [i]　又は、（厚着・中間着・薄着時の）Clo値（定数）
        theta_ot_is_n: ステップnにおける室iの在室者の作用温度, degree C, [i]
        h_hum_is_n: ステップnにおける室iの在室者周りの総合熱伝達率, W/m2K, [i]

    Returns:
        ステップnにおける室iの着衣温度, degree C, [i]
    """

    # ステップnにおける室iの在室者の着衣抵抗, m2K/W, [i]
    i_cl_is_n = get_i_cl_is_n(clo_is_n=clo_is_n)

    # ステップnにおける室iの在室者の着衣面積率, [i]
    f_cl_is_n = get_f_cl_is_n(i_cl_is_n=i_cl_is_n)

    # 代謝量（人体内部発熱量）, W/m2
    m = get_m()

    # ステップnにおける室iの在室者の着衣温度, degree C
    t_cl_i_n = (35.7 - 0.028 * m - theta_ot_is_n) / (1 + i_cl_is_n * f_cl_is_n * h_hum_is_n) + theta_ot_is_n

    return t_cl_i_n


def get_x_hum_psn_is_n(theta_r_is_n: np.ndarray) -> np.ndarray:
    """1人あたりの人体発湿を計算する。

    Args:
        theta_r_is_n: ステップnの室iにおける室温, degree C, [i]

    Returns:
        ステップnの室iにおける1人あたりの人体発湿, kg/s, [i]
    """

    # 水の蒸発潜熱, J/kg
    l_wtr = a39.get_l_wtr()

    # ステップnの室iにおける1人あたりの人体発熱, W, [i]
    q_hum_psn_is_n = get_q_hum_psn_is_n(theta_r_is_n=theta_r_is_n)

    return (119.0 - q_hum_psn_is_n) / l_wtr


def get_q_hum_psn_is_n(theta_r_is_n: np.ndarray) -> np.ndarray:
    """1人あたりの人体発湿を計算する。

    Args:
        theta_r_is_n: ステップnの室iにおける室温, degree C, [i]

    Returns:
        ステップnの室iにおける1人あたりの人体発熱, W, [i]
    """

    return np.minimum(63.0 - 4.0 * (theta_r_is_n - 24.0), 119.0)


def get_f_mrt_hum_is(
        a_bdry_i_jstrs: np.array,
        is_solar_absorbed_inside_bdry_i_jstrs: np.array
):
    """室iの在室者に対する境界j*の形態係数

    Args:
        a_bdry_i_jstrs: 室iの統合された境界j*の面積, m2, [j*]
        is_solar_absorbed_inside_bdry_i_jstrs: 室iの統合された境界j*の室内侵入日射吸収の有無, [j*]

    Returns:
        室iの在室者に対する境界j*の形態係数
    """

    # 室iの下向き部位（床）全体の形態係数
    f_mrt_hum_floor = 0.45

    # 人体に対する部位の形態係数の計算
    f_mrt_hum_is = np.zeros(len(a_bdry_i_jstrs), dtype=np.float)

    # 下向き部位（床）
    f1 = is_solar_absorbed_inside_bdry_i_jstrs
    f_mrt_hum_is[f1] = a_bdry_i_jstrs[f1] / np.sum(a_bdry_i_jstrs[f1]) * f_mrt_hum_floor

    # 床以外
    f2 = np.logical_not(is_solar_absorbed_inside_bdry_i_jstrs)
    f_mrt_hum_is[f2] = a_bdry_i_jstrs[f2] / np.sum(a_bdry_i_jstrs[f2]) * (1.0 - f_mrt_hum_floor)

    return f_mrt_hum_is


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


def get_h_hum_c_is_n(
        theta_r_is_n: np.ndarray,
        theta_cl_is_n: np.ndarray,
        v_hum_is_n: np.ndarray
) -> np.ndarray:
    """人体周りの対流熱伝達率を計算する。

    Args:
        theta_r_is_n: ステップnにおける室iの空気温度, degree C, [i, 1]
        theta_cl_is_n: ステップnにおける室iの在室者の着衣温度, degree C, [i, 1]
        v_hum_is_n: ステップnにおける室iの在室者周りの風速, m/s, [i, 1]

    Returns:
        ステップnの室iにおける在室者周りの対流熱伝達率, W/m2K, [i, 1]
    """

    return np.maximum(12.1 * np.sqrt(v_hum_is_n), 2.38 * np.abs(theta_cl_is_n - theta_r_is_n) ** 0.25)


def get_h_hum_r_is_n(
        theta_cl_is_n: np.ndarray,
        theta_mrt_is_n: np.ndarray
) -> np.ndarray:
    """在室者周りの放射熱伝達率を計算する。

    Args:
        theta_cl_is_n: ステップnにおける室iの在室者の着衣温度, degree C, [i, 1]
        theta_mrt_is_n: ステップnにおける室iの在室者の平均放射温度, degree C, [i, 1]

    Returns:
        ステップnにおける室iの在室者周りの放射熱伝達率, W/m2K, [i, 1]
    """

    # ステップnにおける室iの在室者の着衣温度, K, [i, 1]
    t_cl_is_n = theta_cl_is_n + 273.0

    # ステップnにおける室iの在室者の平均放射温度, K, [i, 1]
    t_mrt_is_n = theta_mrt_is_n + 273.0

    return 3.96 * 10 ** (-8) * (
                t_cl_is_n ** 3.0 + t_cl_is_n ** 2.0 * t_mrt_is_n + t_cl_is_n * t_mrt_is_n ** 2.0 + t_mrt_is_n ** 3.0)


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


def get_pmv_is_n(
        theta_r_is_n: np.ndarray,
        clo_is_n: float,
        p_a_is_n: np.ndarray,
        h_hum_is_n: np.ndarray,
        theta_ot_is_n: np.ndarray
) -> np.ndarray:
    """PMVを計算する

    Args:
        theta_r_is_n: ステップnにおける室iの空気温度, degree C, [i, 1]
        clo_is_n: （厚着・中間着・薄着時の）Clo値
        p_a_is_n:　ステップnにおける室iの水蒸気圧, Pa, [i, 1]
        h_hum_is_n: ステップnにおける室iの在室者周りの総合熱伝達率, W/m2K, [i, 1]
        theta_ot_is_n: ステップnにおける室iの在室者の作用温度, degree C, [i, 1]

    Returns:
        ステップnにおける室iの在室者のPMV, [i, 1]

    Notes:
        ISOで定める計算方法ではなく、前の時刻に求めた人体周りの熱伝達率、着衣温度を使用して収束計算が生じないようにしている。

    """

    # ステップnにおける室iの在室者の着衣抵抗, m2K/W, [i, 1]
    i_cl_is_n = get_i_cl_is_n(clo_is_n=clo_is_n)

    # 代謝量（人体内部発熱量）, W/m2
    m = get_m()

    # ステップnにおける室iの在室者の着衣面積率, [i, 1]
    f_cl_is_n = get_f_cl_is_n(i_cl_is_n=i_cl_is_n)

    return (0.303 * math.exp(-0.036 * m) + 0.028) * (
            m  # 活動量, W/m2
            - 3.05 * 10 ** (-3) * (5733.0 - 6.99 * m - p_a_is_n)  # 皮膚からの潜熱損失, W/m2
            - max(0.42 * (m - 58.15), 0.0)  # 発汗熱損失, W/m2
            - 1.7 * 10 ** (-5) * m * (5867.0 - p_a_is_n)  # 呼吸に伴う潜熱損失, W/m2
            - 0.0014 * m * (34.0 - theta_r_is_n)  # 呼吸に伴う顕熱損失, W/m2 ( = 呼吸量, (g/s)/m2 ✕ (34.0 - 室温)
            - f_cl_is_n * h_hum_is_n * (35.7 - 0.028 * m - theta_ot_is_n) / (1 + i_cl_is_n * f_cl_is_n * h_hum_is_n))  # 着衣からの熱損失


def get_operation_mode_is_n(
        ac_demand_is_n: np.ndarray,
        operation_mode_is_n_mns: np.ndarray,
        pmv_heavy_is_n: np.ndarray,
        pmv_middle_is_n: np.ndarray,
        pmv_light_is_n: np.ndarray
) -> np.ndarray:
    """運転モードを決定する。

    Args:
        ac_demand_is_n: ステップnにおける室iの空調需要の有無, [i, 1]
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
        ac_demand_i_n: bool,
        operation_mode_i_n_mns: OperationMode,
        pmv_heavy_i_n: float,
        pmv_middle_i_n: float,
        pmv_light_i_n: float
) -> OperationMode:
    """運転モードを決定する。

    Args:
        ac_demand_i_n: ステップnにおける室iの空調需要の有無
        operation_mode_i_n_mns: ステップn-1における室iの運転状態
        pmv_heavy_i_n: ステップnにおける室iの厚着時のPMV
        pmv_middle_i_n: ステップnにおける室iの中間着時のPMV
        pmv_light_i_n: ステップnにおける室iの薄着時のPMV

    Returns:
        ステップnにおける室iの運転状態
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


def get_clo_is_n(
        operation_mode_is_n: np.ndarray
) -> np.ndarray:
    """運転モードに応じた在室者のClo値を決定する。

    Args:
        operation_mode_is_n: ステップnにおける室iの運転状態, [i, 1]

    Returns:
        ステップnにおける室iの在室者のClo値, [i, 1]
    """

    return np.vectorize(get_clo_i_n)(operation_mode_is_n)


def get_clo_i_n(
        operation_mode_i_n: OperationMode
) -> float:
    """運転モードに応じたClo値を決定する。

    Args:
        operation_mode_i_n: ステップnにおける室iの運転状況

    Returns:
        ステップnにおける室iの在室者のClo値
    """

    return {
        OperationMode.HEATING: get_clo_heavy(),
        OperationMode.COOLING: get_clo_light(),
        OperationMode.STOP_OPEN: get_clo_middle(),
        OperationMode.STOP_CLOSE: get_clo_middle()
    }[operation_mode_i_n]


def select_theta_cl_i_n(
        operation_mode_i_n: OperationMode,
        theta_cl_heavy_i_n: float,
        theta_cl_middle_i_n: float,
        theta_cl_light_i_n: float
) -> float:
    """運転モードから着衣温度を決定する。

    Args:
        operation_mode_i_n: ステップnにおける室iの運転状態
        theta_cl_heavy_i_n: ステップnにおける室iの厚着時の在室者の着衣温度, degree C
        theta_cl_middle_i_n: ステップnにおける室iの中間着時の在室者の着衣温度, degree C
        theta_cl_light_i_n: ステップnにおける室iの薄着時の在室者の着衣温度, degree C

    Returns:
        ステップnにおける室iの在室者の着衣温度, degree C
    """

    return {
        OperationMode.HEATING: theta_cl_heavy_i_n,
        OperationMode.COOLING: theta_cl_light_i_n,
        OperationMode.STOP_OPEN: theta_cl_middle_i_n,
        OperationMode.STOP_CLOSE: theta_cl_middle_i_n
    }[operation_mode_i_n]


def get_theta_ot_target_is_n(
        p_v_r_is_n: np.ndarray,
        h_hum_is_n: np.ndarray,
        operation_mode_is_n: np.ndarray,
        clo_is_n: np.ndarray,
) -> np.ndarray:
    """目標作用温度を計算する。

    Args:
        p_v_r_is_n: ステップnにおける室iの水蒸気圧, Pa
        h_hum_is_n: ステップnにおける室iの在室者周りの総合熱伝達率, W/m2K, [i]
        operation_mode_is_n: ステップnにおける室iの運転状態, [i]
        clo_is_n: ステップnにおける室iのClo値, [i]

    Returns:
        ステップnにおける室iの目標作用温度, degree C, [i]
    """

    # ステップnの室iにおける目標PMV, [i]
    pmv_target_is_n = np.vectorize(get_pmv_target_i_n)(operation_mode_is_n)

    return np.where(
        (operation_mode_is_n == OperationMode.HEATING) | (operation_mode_is_n == OperationMode.COOLING),
        get_theta_ot_target(
            clo_is_n=clo_is_n,
            p_a_is_n=p_v_r_is_n,
            h_hum_is_n=h_hum_is_n,
            pmv_target_is_n=pmv_target_is_n
        ),
        0.0
    )


def get_pmv_target_i_n(
        operation_mode_i_n: OperationMode
) -> float:
    """運転モードから目標とするPMVを決定する。

    Args:
        operation_mode_i_n: ステップnの室iにおける運転状況


    Returns:
        ステップnの室iにおける目標PMV
    """

    return {
        OperationMode.HEATING: -0.5,
        OperationMode.COOLING: 0.5,
        OperationMode.STOP_OPEN: 0.0,
        OperationMode.STOP_CLOSE: 0.0
    }[operation_mode_i_n]


def get_theta_ot_target(
        clo_is_n: np.ndarray,
        p_a_is_n: np.ndarray,
        h_hum_is_n: np.ndarray,
        pmv_target_is_n: np.ndarray
) -> np.ndarray:
    """指定したPMVを満たすOTを計算する

    Args:
        clo_is_n: ステップnにおける室iの在室者のClo値, [i]
        p_a_is_n:　ステップnにおける室iの水蒸気圧, Pa
        h_hum_is_n: ステップnにおける室iの在室者周りの総合熱伝達率, W/m2K, [i]
        pmv_target_is_n: ステップnにおける室iの在室者の目標PMV, [i]

    Returns:
        ステップnにおける室iの在室者の目標OT, [i]

    Notes:
        ISOで定める計算方法ではなく、前の時刻に求めた人体周りの熱伝達率、着衣温度を使用して収束計算が生じないようにしている。

    """

    # 着衣抵抗, m2K/W
    i_cl_is_n = get_i_cl_is_n(clo_is_n=clo_is_n)

    # 代謝量（人体内部発熱量）, W/m2
    m = get_m()

    # ステップnにおける室iの着衣面積率, [i]
    f_cl_is_n = get_f_cl_is_n(i_cl_is_n=i_cl_is_n)

    return (pmv_target_is_n / (0.303 * math.exp(-0.036 * m) + 0.028) - m
            + 3.05 * 10 ** (-3) * (5733.0 - 6.99 * m - p_a_is_n)
            + max(0.42 * (m - 58.15), 0.0)
            + 1.7 * 10 ** (-5) * m * (5867.0 - p_a_is_n)
            + 0.0014 * m * 34.0
            + f_cl_is_n * h_hum_is_n * (35.7 - 0.028 * m) / (1 + i_cl_is_n * f_cl_is_n * h_hum_is_n)
            )/(0.0014 * m + f_cl_is_n * h_hum_is_n / (1 + i_cl_is_n * f_cl_is_n * h_hum_is_n))


def get_f_cl_is_n(i_cl_is_n: np.ndarray) -> np.ndarray:
    """着衣面積率を計算する。

    Args:
        i_cl_is_n: ステップnにおける室iの在室者の着衣抵抗, m2K/W, [i, 1]

    Returns:
        ステップnにおける室iの在室者の着衣面積率, [i, 1]
    """

    return np.where(i_cl_is_n <= 0.078, 1.00 + 1.290 * i_cl_is_n, 1.05 + 0.645 * i_cl_is_n)


def get_m():
    """代謝量を得る。

    Returns:
        代謝量, W/m2

    Notes:
        代謝量は1.0 met に固定とする。
        1.0 met は、ISOにおける、Resting - Seated, quiet に相当
        1 met = 58.15 W/m2
    """

    return 58.15


def get_i_cl_is_n(clo_is_n: Union[np.ndarray, float]) -> np.ndarray:
    """Clo値から着衣抵抗を計算する。

    Args:
        clo_is_n: ステップnにおける室iの在室者のClo値, [i, 1]

    Returns:
        ステップnにおける室iの在室者の着衣抵抗, m2K/W, [i, 1]

    Notes:
        1 clo = 0.155 m2K/W
    """

    return clo_is_n * 0.155


# endregion
