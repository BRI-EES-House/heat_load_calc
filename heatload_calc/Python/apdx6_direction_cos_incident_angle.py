import math
import numpy as np

"""
付録6．入射角の方向余弦
"""


# 式(72)
def calc_cos_incident_angle(
        h_sun_sin_n: np.ndarray, h_sun_cos_n: np.ndarray,
        a_sun_sin_n: np.ndarray, a_sun_cos_n: np.ndarray,
        w_alpha_k: np.ndarray, w_beta_k: np.ndarray) -> np.ndarray:
    """
    Args:
        h_sun_sin_n: 時刻nにおける太陽高度の正弦
        h_sun_cos_n: 時刻nにおける太陽高度の余弦
        a_sun_sin_n: 時刻nにおける太陽方位角の正弦
        a_sun_cos_n: 時刻nにおける太陽方位角の余弦
        w_alpha_k: 外表面の方位角, rad
        w_beta_k: 外表面の傾斜角, rad
    Returns:
        時刻nにおける入射角の方向余弦
    """

    return np.clip(
        h_sun_sin_n[np.newaxis,:] * np.cos(w_beta_k[:,np.newaxis])
        + h_sun_cos_n[np.newaxis,:] * a_sun_sin_n[np.newaxis,:] * np.sin(w_beta_k[:,np.newaxis]) * np.sin(w_alpha_k[:,np.newaxis])
        + h_sun_cos_n[np.newaxis,:] * a_sun_cos_n[np.newaxis,:] * np.sin(w_beta_k[:,np.newaxis]) * np.cos(w_alpha_k[:,np.newaxis]),
        0.0,
        None
    )
