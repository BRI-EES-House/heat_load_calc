import numpy as np
import logging
from typing import List, Dict
from typing import Union

from heat_load_calc.global_number import get_sgm, get_eps
from scipy import optimize


def get_f_mrt_is_js(a_s_js: np.ndarray, h_s_r_js: np.ndarray, p_is_js: np.ndarray) -> np.ndarray:

    ah = a_s_js * h_s_r_js

    return p_is_js * ah.T / np.dot(p_is_js, ah)


def get_h_r_js(n_rm: int, a_s_js: np.ndarray, connected_room_id_js: np.ndarray) -> np.ndarray:

    a_s_js = a_s_js.flatten()

    connected_room_id_js = connected_room_id_js.flatten()

    h_r_is = np.zeros_like(a=a_s_js, dtype=float)

    for i in range(n_rm):

        is_connected = connected_room_id_js == i

        h_r_is[is_connected] = _get_h_r_i_js(a_s_js_dsh=a_s_js[is_connected])

    return h_r_is.reshape(-1, 1)


def _get_h_r_i_js(a_s_js_dsh: np.ndarray) -> np.ndarray:
    """ 放射熱伝達率（室単位で計算する）

    Args:
        a_s_js_dsh: 境界jの面積, m2, [j, 1]
    Returns:
        放射熱伝達率, W/m2K, [j, 1]
    """

    # 微小点に対する境界jの形態係数
    # 永田先生の方法
    f_js = _get_f_i_js(a_s_js_dsh=a_s_js_dsh)

    # 形態係数の総計をチェック
    if abs(f_js.sum() - 1.0) > 1.0e-5:
        raise ValueError()

    # 境界間の放射熱伝達率を決定する際、平均放射温度を20℃固定値であるとして計算する。
    t_mrt = 273.15 + 20.0

    hr_k_n = get_eps() / (1.0 - get_eps() * f_js) * 4.0 * get_sgm() * t_mrt ** 3.0

    return hr_k_n


def _get_f_i_js(a_s_js_dsh: np.ndarray) -> np.ndarray:
    """
    微小体に対する部位の形態係数の計算
    Args:
        a_s_js_dsh: 境界の表面積, m2, [js]
    Returns:
        微小体に対する部位の形態係数, -, [js]
    """

    # 面積比, [j]
    r_a_srf_js = a_s_js_dsh / sum(a_s_js_dsh)

    # 非線形方程式L(f̅)=0の解, float
    f_ver = _get_f_ver(r_a_srf_js=r_a_srf_js)

    # 放射伝熱計算で使用する微小球に対する部位の形態係数, -, [j]
    f_i_js = _get_f_j(f_ver=f_ver, r_a_srf_j=r_a_srf_js)

    # 総和のチェック
    if abs(np.sum(f_i_js) - 1.0) > 1.0e-3:
        logging.warning('形態係数の合計値が不正 TotalFF=', np.sum(f_i_js))

    return f_i_js


def _get_f_ver(r_a_srf_js: np.ndarray) -> float:
    """
    非線形方程式L(f̅)=0の解
    Args:
        r_a_srf_js: 面積比, [j]
    Returns:
        非線形方程式L(f̅)=0の解
    """

    def f(f_ver):
        return np.sum(_get_f_j(f_ver=f_ver, r_a_srf_j=r_a_srf_js)) - 1.0

    return float(optimize.fsolve(f, np.array(1.0))[0])


def _get_f_j(f_ver: float, r_a_srf_j: Union[float, np.ndarray]):
    """
    空間内の微小球からみた面iへの形態係数を計算する。
    Args:
        f_ver: f_ver
        r_a_srf_j: 面積割合
    Returns:
        空間内の微小球からみた面iへの形態係数
    """

    return 0.5 * (1.0 - np.sign(1.0 - 4.0 * r_a_srf_j / f_ver) * np.sqrt(abs(1.0 - 4.0 * r_a_srf_j / f_ver)))


