import numpy as np
from typing import List

from heat_load_calc.core import boundary_simple


def get_f_mrt_hum_js(n_spaces: int, bss: List[boundary_simple.BoundarySimple]) -> np.ndarray:
    """
    境界jが接する室の在室者に対する境界jの形態係数を取得する。
    Args:
        n_spaces: 室の数
        bss: 境界, [j]
    Returns:
        境界jが接する室の在室者に対する境界jの形態係数
    """

    # 境界の数と等しい numpy リストを作成する。
    f_mrt_hum_is = np.zeros(shape=(len(bss)), dtype=float)

    # connected_room_id のリスト（numpy形式）
    connected_room_id_js = np.array([bs.connected_room_id for bs in bss])

    # 面積, m2, [i]
    a_srf_js = np.array([bs.area for bs in bss])

    # 床か否か, [i]
    is_floor_js = np.array([bs.is_floor for bs in bss])

    for i in range(n_spaces):

        is_connected_is = connected_room_id_js == i

        f_mrt_hum_is[is_connected_is] = get_f_mrt_hum_i_js(
            a_srf_i_js=a_srf_js[is_connected_is],
            is_floor_i_js=is_floor_js[is_connected_is]
        )

    return f_mrt_hum_is


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


