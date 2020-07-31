import numpy as np

# TODO: 在室者に対する境界の形態係数を入力にするのではなく、例えば、床への形態係数のみをパラメータとして面積按分式は core プログラムに含めてしまった方が良いのではないか？
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


