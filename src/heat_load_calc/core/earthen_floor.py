import numpy as np
import response_factor as rf

def get_rf_parameters_t() -> np.ndarray:
    """
    土間床外周部の貫流応答特性のパラメータを返す
    Returns:
        土間床外周部のパラメータ
    """

    return np.array([
        0.00629674496799351,
        -0.0254298041223877,
        0.0187373088565465,
        -0.662536130328503,
        0.24717128823327,
        -0.658509645407002,
        0.53212068322401,
        -1.44873895869436,
        2.17282417034313,
        -0.755106925806161
    ])

def get_rf_parameters_a() -> np.ndarray:
    """
    土間床外周部の吸熱応答特性のパラメータを返す
    Returns:
        土間床外周部のパラメータ
    """

    return np.array([
        -0.00826303066004131,
        0.0472947046522058,
        -0.148182829904938,
        -0.458859710368281,
        -0.00918218989091338,
        -0.636035318028857,
        0.45069801906113,
        -0.901348816493565,
        0.937725558097192,
        -3.8315515360059
    ])

def rf_initial_term(parameters: np.ndarray, alpha_m: np.ndarray) -> float:
    """
    土間床外周部の応答係数の初項を計算する
    Args:
        parameters: 応答特性のパラメータ
        alpha_m: 固定根数列

    Returns:
        土間床外周部の応答係数の初項
    """

    return 1.0 + np.sum(parameters / (alpha_m * 900) * (1.0 - np.exp(-alpha_m * 900)))


def calc_rf_exponential(parameters: np.ndarray, alpha_m: np.ndarray) -> np.ndarray:
    """
    土間床外周部の指数項別応答係数を計算する
    Args:
        parameters: 応答特性のパラメータ
        alpha_m: 固定根数列

    Returns:
        土間床外周部の指数項別応答
    """

    return - parameters / (alpha_m * 900.0) * (1.0 - np.exp(- alpha_m * 900.0)) ** 2.0


if __name__ == "__main__":
    parameters_t = get_rf_parameters_t()
    parameters_a = get_rf_parameters_a()

    alpha_m = rf.get_alpha_m(is_ground=True)

    at0 = rf_initial_term(parameters=parameters_t, alpha_m=alpha_m)
    aa0 = rf_initial_term(parameters=parameters_a, alpha_m=alpha_m)

    print(at0, aa0)

    rft1 = calc_rf_exponential(parameters=parameters_t, alpha_m=alpha_m)
    rfa1 = calc_rf_exponential(parameters=parameters_a, alpha_m=alpha_m)

    print(rft1, rfa1)
