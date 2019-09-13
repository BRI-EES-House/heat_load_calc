import math
import numpy as np

"""
付録6．入射角の方向余弦
"""


# 式(72)
def calc_cos_incident_angle(
        h_sun_sin_n: np.ndarray, h_sun_cos_n: np.ndarray,
        a_sun_sin_n: np.ndarray, a_sun_cos_n: np.ndarray,
        w_alpha: float, w_beta: float) -> np.ndarray:
    """
    Args:
        h_sun_sin_n: 時刻nにおける太陽高度の正弦
        h_sun_cos_n: 時刻nにおける太陽高度の余弦
        a_sun_sin_n: 時刻nにおける太陽方位角の正弦
        a_sun_cos_n: 時刻nにおける太陽方位角の余弦
        w_alpha: 外表面の方位角, rad
        w_beta: 外表面の傾斜角, rad
    Returns:
        時刻nにおける入射角の方向余弦
    """

    return np.clip(
        h_sun_sin_n * math.cos(w_beta)
        + h_sun_cos_n * a_sun_sin_n * math.sin(w_beta) * math.sin(w_alpha)
        + h_sun_cos_n * a_sun_cos_n * math.sin(w_beta) * math.cos(w_alpha),
        0.0,
        None
    )
