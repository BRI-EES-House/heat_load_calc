import numpy as np


def get_f_mrt_hum_is(a_bdry_i_js: np.ndarray, is_floor_bdry_i_js: np.ndarray) -> np.ndarray:
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

    return f_mrt_hum_i_js


