import numpy as np


def v_diag(v_matrix: np.ndarray) -> np.ndarray:
    arr = v_matrix.flatten()
    return np.diag(arr)
