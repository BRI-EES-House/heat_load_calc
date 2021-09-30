import numpy as np


def get_f_mrt_hum_js(a_srf_js, connected_room_id_js, is_floor_js, n_boundaries, n_spaces):
    f_mrt_hum_is = np.zeros(shape=(n_boundaries), dtype=float)
    for i in range(n_spaces):
        is_connected = connected_room_id_js == i

        f_mrt_hum_is[is_connected] = get_f_mrt_hum_i_js(
            a_bdry_i_js=a_srf_js[is_connected],
            is_floor_bdry_i_js=is_floor_js[is_connected]
        )
    return f_mrt_hum_is


def get_f_mrt_hum_i_js(a_bdry_i_js: np.ndarray, is_floor_bdry_i_js: np.ndarray) -> np.ndarray:
    """
    室iの在室者に対する境界j*の形態係数
    Args:
        a_bdry_i_js: 室iの境界jの面積, m2, [j]
        is_floor_bdry_i_js: 室iの境界jが床か否か, [j]
    Returns:
        室iの在室者に対する境界jの形態係数
    Notes:
        TODO: 在室者に対する境界の形態係数を入力にするのではなく、例えば、床への形態係数のみをパラメータとして面積按分式は core プログラムに含めてしまった方が良いのではないか？
    """

    # 室iの下向き部位（床）全体の形態係数
    f_mrt_hum_floor = 0.45

    # 人体に対する部位の形態係数の計算
    f_mrt_hum_i_js = np.zeros(len(a_bdry_i_js), dtype=np.float)

    # 下向き部位（床）
    f1 = is_floor_bdry_i_js
    f_mrt_hum_i_js[f1] = a_bdry_i_js[f1] / np.sum(a_bdry_i_js[f1]) * f_mrt_hum_floor

    # 床以外
    f2 = np.logical_not(is_floor_bdry_i_js)
    f_mrt_hum_i_js[f2] = a_bdry_i_js[f2] / np.sum(a_bdry_i_js[f2]) * (1.0 - f_mrt_hum_floor)

    # 合計値が1になっているかチェックする
    if abs(f_mrt_hum_i_js.sum() - 1.0) > 1.0e-4:
        raise ValueError()

    return f_mrt_hum_i_js


