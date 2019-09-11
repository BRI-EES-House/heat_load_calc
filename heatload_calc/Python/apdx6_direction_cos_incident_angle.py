import math
import numpy as np

"""
付録6．入射角の方向余弦
"""


# 式(72)
def calc_cos_incident_angle(
        Sh_n: np.ndarray, cos_h_s: np.ndarray, sin_a_s: np.ndarray, cos_a_s: np.ndarray, Wa: float, Wb: float) -> np.ndarray:
    """
    Args:
        Sh_n: 太陽高度の正弦
        cos_h_s: 太陽高度の余弦
        sin_a_s: 太陽方位角の正弦
        cos_a_s: 太陽方位角の余弦
        Wa: 外表面の方位角, rad
        Wb: 外表面の傾斜角, rad
    Returns:
        入射角の方向余弦
    """

    return np.clip(
        Sh_n * math.cos(Wb)
        + cos_h_s * sin_a_s * math.sin(Wb) * math.sin(Wa)
        + cos_h_s * cos_a_s * math.sin(Wb) * math.cos(Wa),
        0.0,
        None
    )
