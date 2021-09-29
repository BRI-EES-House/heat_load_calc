import numpy as np


def get_flr_i_js(area_i_js: np.ndarray, is_radiative_heating: bool, is_floor_i_js: np.ndarray):
    """
    放射暖房放射成分吸収比率の計算

    Args:
        area_i_js: 室 i における境界 j の面積, m2
        is_radiative_heating: 室 i に放射暖房が設置されているか否か
        is_floor_i_js: 室 i における境界 j が床か否か
    Returns:
        放射暖房放射成分吸収比率
    """

    # 室 i の床面積の合計, m2
    a_floor_i = np.sum(area_i_js[is_floor_i_js])

    flr_i_js = area_i_js / a_floor_i * is_radiative_heating * is_floor_i_js

    return flr_i_js


