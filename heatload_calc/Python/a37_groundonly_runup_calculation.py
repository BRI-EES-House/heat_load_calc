import math
import numpy as np

"""
付録37．土壌の助走計算
"""


def get_Ts_i_n_k(Phi_A_i_k_0, hi_i_k, Tei_i_l_n, Ts_dash_A_l_n_m, a0):
    Ts_i_n_k = (Phi_A_i_k_0 * hi_i_k * Tei_i_l_n + np.sum(Ts_dash_A_l_n_m) + a0) / \
               (1 + Phi_A_i_k_0 * hi_i_k)
    return Ts_i_n_k


def calc_Tei_i_l_n(To_n):
    a0 = get_a0(To_n)
    a1 = get_a1(To_n)
    b1 = get_b1(To_n)

    To_d_bar = get_To_d_bar(a0, a1, b1)
    Tei_i_l_n = get_Tei_i_l_n(To_d_bar)

    return Tei_i_l_n


def get_Tei_i_l_n(To_d_bar):
    return To_d_bar


def get_To_d_bar(a0, a1, b1):
    d = np.repeat(np.arange(1, 366), 24)
    To_d_bar = a0 + 2 * (a1 * np.cos(2 * math.pi * d / 365) + b1 * np.sin(2 * math.pi * d / 365))
    return To_d_bar


def get_a0(To_n):
    a0 = np.average(To_n)
    return a0


def get_a1(To_n):
    n = np.arange(1, 8761)
    a1 = np.average(To_n * np.cos(2 * math.pi * n / 8760))
    return a1


def get_b1(To_n):
    n = np.arange(1, 8761)
    b1 = np.average(To_n * np.sin(2 * math.pi * n / 8760))
    return b1