import numpy as np
from typing import List

from heat_load_calc.core import boundaries


def get_f_mrt_hum_js(n_rm: int, n_b: int, p_is_js, a_s_js, is_floor_js) -> np.ndarray:
    """
    境界jが接する室の在室者に対する境界jの形態係数を取得する。
    Args:
        n_rm: 室の数
        n_b: 境界の数
        p_is_js: 室と境界との関係を表すベクトル
        a_s_js: 境界 j の面積, m2, [j, 1]
        is_floor_js: 境界 j が床かどうか, [j, 1]
    Returns:
        境界jが接する室の在室者に対する境界jの形態係数
    """

    # 境界の数と等しい numpy リストを作成する。
    f_mrt_hum_js = np.zeros(shape=(n_b), dtype=float)

    for i in range(n_rm):

        is_connected_is = p_is_js[i] == 1

        f_mrt_hum_js[is_connected_is] = get_f_mrt_hum_i_js(
            a_srf_i_js=a_s_js.flatten()[is_connected_is],
            is_floor_i_js=is_floor_js.flatten()[is_connected_is]
        )

    # 室iの在室者に対する境界j*の形態係数, [i, j]
    f_mrt_hum_is_js = p_is_js * f_mrt_hum_js[np.newaxis, :]

    return f_mrt_hum_is_js


def get_f_mrt_hum_i_js(a_srf_i_js: np.ndarray, is_floor_i_js: np.ndarray) -> np.ndarray:
    """
    室iの在室者に対する境界j*の形態係数
    Args:
        a_srf_i_js: 室iの境界j*の面積, m2, [j]
        is_floor_i_js: 室iの境界j*が床か否か, [j]
    Returns:
        室iの在室者に対する境界j*の形態係数
    """

    # 室iの下向き部位（床）全体の形態係数
    f_mrt_hum_floor = 0.45

    # 人体に対する部位の形態係数の計算
    f_mrt_hum_i_js = np.zeros(len(a_srf_i_js), dtype=np.float)

    # 下向き部位（床）
    # 値 0.45 を床である境界の面積で按分する。
    f1 = is_floor_i_js
    f_mrt_hum_i_js[f1] = a_srf_i_js[f1] / np.sum(a_srf_i_js[f1]) * f_mrt_hum_floor

    # 床以外
    # 1 から 0.45 を引いた残りの値を床ではない境界の面積で按分する。
    f2 = np.logical_not(is_floor_i_js)
    f_mrt_hum_i_js[f2] = a_srf_i_js[f2] / np.sum(a_srf_i_js[f2]) * (1.0 - f_mrt_hum_floor)

    # 合計値が1になっているかチェックする
    if abs(f_mrt_hum_i_js.sum() - 1.0) > 1.0e-4:
        raise ValueError()

    return f_mrt_hum_i_js


