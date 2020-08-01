import numpy as np



def get_area_weighted_averaged_values_one_dimension(v: np.ndarray, a: np.ndarray) -> np.ndarray:
    """
    あるデータを面積荷重平均する。
    Args:
        v: ベクトル（1次元）, [m] (m=境界の数）
        a: 面積, m2, [m] (m=境界の数）

    Returns:
        面積荷重平均化された値
    """
    return np.sum(v * a / np.sum(a))


def get_area_weighted_averaged_values_two_dimension(v: np.ndarray, a: np.ndarray) -> np.ndarray:
    """
    時系列データ等複数の値もつ1次元配列のデータを複数もつマトリックスを面積加重平均する。

    Args:
        v: ベクトル（2次元） [m, n] （m=境界の数）
        a: 面積, m2, [境界の数]

    Returns:
        面積荷重平均化された1次元配列の値 [n]
    """

    # 面積割合, [境界の数]　ただし、行列計算可能なように[m,1]の2次元配列としている。
    r = (a / np.sum(a)).reshape(-1, 1)

    result = np.sum(v * r, axis=0)

    return result

