import numpy as np

"""
付録1．	表面温度の計算
"""


# ********** 表面温度を計算するための各種係数 **********

def get_theta_srf_dsh_a_i_jstrs_npls_ms(
        q_srf_jstrs_n: np.ndarray,
        phi_a_1_bnd_jstrs_ms: np.ndarray,
        r_bnd_i_jstrs_ms: np.ndarray,
        theta_dsh_srf_a_jstrs_n_ms: np.ndarray
) -> np.ndarray:
    """

    Args:
        q_srf_jstrs_n: ステップnの統合された境界j*における表面熱流（壁体吸熱を正とする）, W/m2, [j*]
        phi_a_1_bnd_jstrs_ms: 統合された境界j*における項別公比法の項mの吸熱応答係数の係数, m2K/W, [jstrs, 12]
        r_bnd_i_jstrs_ms: 室iの統合された境界j*の項mにおける公比, [jstrs, 12]
        theta_dsh_srf_a_jstrs_n_ms: ステップnの統合された境界j*における指数項mの吸熱応答の項別成分, degree C, [j*, 12]
    Returns:
        ステップn+1の室iの統合された境界j*における項別公比法の項mの吸熱応答に関する表面温度, degree C, [jstrs, 12]
    """

    return phi_a_1_bnd_jstrs_ms * q_srf_jstrs_n[:, np.newaxis] + r_bnd_i_jstrs_ms * theta_dsh_srf_a_jstrs_n_ms


def get_Qr(a_bnd_jstrs, h_r_bnd_jstrs, theta_s_jstrs_n, p, Tsx):
    """

    Args:
        a_bnd_jstrs:
        h_r_bnd_jstrs:
        theta_s_jstrs_n: ステップnにおける境界j*の表面温度, degree C, [j*]
        p:
        Tsx:
    Returns:

    """

    # 放射成分, W
    Qr = h_r_bnd_jstrs * a_bnd_jstrs * (np.dot(p.T, Tsx.reshape(-1, 1)).flatten() - theta_s_jstrs_n)

    return Qr


# 室内表面熱流の計算 式(28)
def calc_qi(
        h_c_bnd_jstrs, h_r_bnd_jstrs,
        theta_s_jstrs_n, theta_ei_jstrs_n):
    """

    Args:
        h_c_bnd_jstrs:
        h_r_bnd_jstrs:
        theta_s_jstrs_n: ステップnにおける境界j*の表面温度, degree C, [j*]
        theta_r_is_npls:
        theta_ei_jstrs_n:
    Returns:

    """

    oldqi = (theta_ei_jstrs_n - theta_s_jstrs_n) * (h_c_bnd_jstrs + h_r_bnd_jstrs)

    return oldqi


# 室内表面熱流 [W/m2]
def get_qi(Qt, area):
    return Qt / area


# 室内等価温度の計算 式(29)
def calc_Tei(h_c_bnd_i_jstrs, h_r_bnd_i_jstrs, q_sol_srf_i_jstrs_ns, flr_i_k, a_bnd_i_jstrs, theta_r_is_n, f_mrt_jstrs_jstrs, Ts_i_k_n, lrs_is_n, beta_is):
    """
    :param theta_r_is_n: 室温
    :param Tsx: 形態係数加重平均表面温度
    :param lrs_is_n:
    :param beta_is:
    :return:
    """

    # 平均放射温度の計算
    Tsx = get_Tsx(f_mrt_jstrs_jstrs, Ts_i_k_n)

    return theta_r_is_n * h_c_bnd_i_jstrs / (h_c_bnd_i_jstrs + h_r_bnd_i_jstrs) \
           + Tsx * h_r_bnd_i_jstrs / (h_c_bnd_i_jstrs + h_r_bnd_i_jstrs) \
           + q_sol_srf_i_jstrs_ns / (h_c_bnd_i_jstrs + h_r_bnd_i_jstrs) \
           + flr_i_k * lrs_is_n * (1.0 - beta_is) / (h_c_bnd_i_jstrs + h_r_bnd_i_jstrs) / a_bnd_i_jstrs


# 平均放射温度の計算
def get_Tsx(Fmrt, Ts):
    return np.sum(Fmrt * Ts)


def get_Tsx2(theta_s_jstrs_n, f_mrt_jstrs_jstrs: float):
    """

    Args:
        theta_s_jstrs_n: ステップnにおける境界j*の表面温度, degree C, [j*]
        f_mrt_jstrs_jstrs:　（他の）境界の境界に対する形態係数

    Returns:

    """

    # 平均放射温度の計算
    Tsx = (np.dot(f_mrt_jstrs_jstrs, theta_s_jstrs_n.reshape(-1, 1)).flatten())

    return Tsx


