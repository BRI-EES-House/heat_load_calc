import math
import numpy as np

"""
付録6．入射角の方向余弦
"""

# 式(72)
def calc_cos_incident_angle(
        sin_h_s: np.ndarray, cos_h_s: np.ndarray, sin_a_s: np.ndarray, cos_a_s: np.ndarray, wa: float, wb: float) -> np.ndarray:
    """
    Args:
        sin_h_s: 太陽高度の正弦
        cos_h_s: 太陽高度の余弦
        sin_a_s: 太陽方位角の正弦
        cos_a_s: 太陽方位角の余弦
        wa: 外表面の方位角, rad
        wb: 外表面の傾斜角, rad
    Returns:
        入射角の方向余弦
    """

    return np.clip(
        sin_h_s * math.cos(wb)
        + cos_h_s * sin_a_s * math.sin(wb) * math.sin(wa)
        + cos_h_s * cos_a_s * math.sin(wb) * math.cos(wa),
        0.0,
        None
    )
