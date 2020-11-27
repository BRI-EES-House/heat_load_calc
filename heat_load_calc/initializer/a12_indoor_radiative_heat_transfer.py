"""
付録12．	室内表面の吸収日射量、形態係数、放射暖房放射成分吸収比率
"""

import numpy as np


def get_flr_i_js(area_i_js: np.ndarray, is_radiative_heating: bool, is_floor_i_js: np.ndarray):
    """
    放射暖房放射成分吸収比率
    Args:
        area_i_js:
        is_radiative_heating:
        is_floor_i_js:

    Returns:
        放射暖房放射成分吸収比率
    """

    a_floor_i = np.sum(area_i_js[is_floor_i_js])

    flr_i_js = area_i_js / a_floor_i * is_radiative_heating * is_floor_i_js

    return flr_i_js


