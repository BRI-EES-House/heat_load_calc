import numpy as np
from dataclasses import dataclass

from heat_load_calc import response_factor as rf


@dataclass()
class EarthenFloor:

    # 線熱貫流率, W/m K
    psi: float

    # 吸熱応答係数の初項, -
    rfa0: float

    # 貫流応答係数の初項, -
    rft0: float

    # 指数項別吸熱応答係数, -
    rfa1: np.ndarray

    # 指数項別貫流応答係数, -
    rft1: np.ndarray

    # 根の数
    n_root: int


def _get_rf_parameters_t() -> np.ndarray:
    """
    土間床外周部の貫流応答特性のパラメータを返す
    Returns:
        土間床外周部のパラメータ
    """

    return np.array([
        -0.0374209855594571,
        0.0941209125618409,
        -0.136869498520281,
        -0.493811564418963,
        0.0541164032804825,
        -0.415684492437867,
        0.198293349862905,
        -0.987302200526257,
        1.61323086601284,
        -0.320547647481877
    ])


def _get_rf_parameters_a() -> np.ndarray:
    """
    土間床外周部の吸熱応答特性のパラメータを返す
    Returns:
        土間床外周部のパラメータ
    """

    return np.array([
        -0.000375432069330334,
        0.00585684299109825,
        -0.054548410348266,
        -0.613447717287527,
        0.212610151690178,
        -0.922186268181334,
        0.790978785668312,
        -1.26629291125237,
        1.26609505908759,
        -4.0149975814435
    ])


def _rf_initial_term(parameters: np.ndarray, alpha_m: np.ndarray) -> float:
    """
    土間床外周部の応答係数の初項を計算する
    Args:
        parameters: 応答特性のパラメータ
        alpha_m: 固定根数列

    Returns:
        土間床外周部の応答係数の初項
    """

    return 1.0 + np.sum(parameters / (alpha_m * 900) * (1.0 - np.exp(-alpha_m * 900)))


def _calc_rf_exponential(parameters: np.ndarray, alpha_m: np.ndarray) -> np.ndarray:
    """
    土間床外周部の指数項別応答係数を計算する
    Args:
        parameters: 応答特性のパラメータ
        alpha_m: 固定根数列

    Returns:
        土間床外周部の指数項別応答
    """

    return - parameters / (alpha_m * 900.0) * (1.0 - np.exp(- alpha_m * 900.0)) ** 2.0


class EarthenFloorRF(EarthenFloor):

    def __init__(self, psi: float):

        # 線熱貫流率
        self.psi = psi

        # 貫流応答、吸熱応答のパラメータ取得
        parameters_t = _get_rf_parameters_t()
        parameters_a = _get_rf_parameters_a()

        # 土壌の根を取得
        alpha_m = rf._get_alpha_m(is_ground=True)

        # 根の数
        self.n_root = len(alpha_m)

        # 吸熱応答の初項
        self.rfa0 = psi * _rf_initial_term(parameters=parameters_a, alpha_m=alpha_m)
        # 貫流応答の初項
        self.rft0 = psi * _rf_initial_term(parameters=parameters_t, alpha_m=alpha_m)
        # 指数項別吸熱応答係数
        self.rfa1 = psi * _calc_rf_exponential(parameters=parameters_a, alpha_m=alpha_m)
        self.rft1 = psi * _calc_rf_exponential(parameters=parameters_t, alpha_m=alpha_m)


if __name__ == "__main__":

    erf = EarthenFloorRF(psi=1.0)
    print(erf.psi)
    print(erf.rfa0, erf.rft0)
    print(erf.rfa1)
    print(erf.rft1)

    erf2 = EarthenFloorRF(psi=0.5)
    print(erf2.psi)
    print(erf2.rfa0, erf2.rft0)
    print(erf2.rfa1)
    print(erf2.rft1)

    parameters_t = _get_rf_parameters_t()
    parameters_a = _get_rf_parameters_a()

    alpha_m = rf._get_alpha_m(is_ground=True)

    at0 = _rf_initial_term(parameters=parameters_t, alpha_m=alpha_m)
    aa0 = _rf_initial_term(parameters=parameters_a, alpha_m=alpha_m)

    print(aa0, at0)

    rft1 = _calc_rf_exponential(parameters=parameters_t, alpha_m=alpha_m)
    rfa1 = _calc_rf_exponential(parameters=parameters_a, alpha_m=alpha_m)

    print(rfa1, rft1)
