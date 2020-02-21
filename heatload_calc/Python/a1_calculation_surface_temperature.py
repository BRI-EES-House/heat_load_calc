import numpy as np

"""
付録1．	表面温度の計算
"""


# ********** 室内表面温度 **********

# 表面温度の計算 式(23)
def get_surface_temperature(wsr_jstrs, wsb_jstrs, wsc_is_jstrs_npls, wsv_is_jstrs_npls, theta_r_is_npls, lrs_is_n, p):

    return (
        wsr_jstrs * np.dot(p.T, theta_r_is_npls.reshape(-1, 1)).flatten()
        + wsc_is_jstrs_npls
        + wsv_is_jstrs_npls
        + wsb_jstrs * np.dot(p.T, lrs_is_n.reshape(-1, 1)).flatten()
    )

# ********** 表面温度を計算するための各種係数 **********

# 式(24)
def get_WSR(AX_k_l, FIA_i_l):
    return np.dot(AX_k_l, FIA_i_l)


# 式(24)
def get_WSB(AX_k_l, FLB_i_l):
    return np.dot(AX_k_l, FLB_i_l)


def get_wsc_i_jstrs_npls(ivs_x_i: np.ndarray, crx_i_jstrs_npls: np.ndarray) -> np.ndarray:
    """

    Args:
        ivs_x_i: 室iにおける行列X, [j*, j*]
       crx_i_jstrs_npls: ステップn+1の室iの統合された境界j*における係数CRX, degree C, [j*]

    Returns:
        ステップn+1の室iの断熱された境界j*における係数WSC, degree C, [j*]
    """

    return np.dot(ivs_x_i, crx_i_jstrs_npls)


def get_wsv_i_jstrs_npls(ivs_x_i: np.ndarray, cvl_i_jstrs_npls: np.ndarray) -> np.ndarray:
    """

    Args:
        ivs_x_i: 室iにおける行列X, [j*, j*]
        cvl_i_jstrs_npls: ステップn+1の室iの統合された境界j*における係数CVL, degree C, [j*]

    Returns:
        ステップn+1の室iの統合された境界j*における係数WSV, degree C, [j*]
    """

    return np.dot(ivs_x_i, cvl_i_jstrs_npls)


# 式(25)中のAXはAXdの逆行列
def get_AX(matAXd):
    return np.linalg.inv(matAXd)


# 行列AX 式(25)
def get_AX(RFA0, hir, Fmrt, hi, Nsurf):
    # 単位行列の準備
    eye = np.eye(Nsurf)

    # 対角要素以外 式(25)上段
    matAXd = - RFA0[:, np.newaxis] * hir[:, np.newaxis] * Fmrt[np.newaxis, :]

    # 対角要素 式(25)下段
    matAXd[eye == 1] = 1. + RFA0 * hi - RFA0 * hir * Fmrt

    # 逆行列の計算
    return np.linalg.inv(matAXd)


# matFIAの作成 式(26)
def get_FIA(RFA0, hic):
    return RFA0 * hic


# FLB=φA0×flr_i_k×(1-Beta_i) 式(26)
def get_FLB(RFA0, flr, Beta, area):
    return RFA0 * flr * (1. - Beta) / area


def get_crx_i_jstrs_npls(
        phi_a_0_bnd_i_jstrs: np.ndarray,
        q_sol_floor_i_jstrs_n: np.ndarray,
        phi_t_0_bnd_i_jstrs: np.ndarray,
        theta_rear_i_jstrs_n: np.ndarray
) -> np.ndarray:
    """

    Args:
        phi_a_0_bnd_i_jstrs: 室iの統合された境界j*における吸熱応答係数の初項, m2K/W, [j*]
        q_sol_floor_i_jstrs_n:
            ステップnの室iの統合された境界j*における透過日射熱取得量のうち表面に吸収される日射量, W/m2, [j*]
        phi_t_0_bnd_i_jstrs: 室iの統合された境界j*における貫流応答係数の初項, [j*]
        theta_rear_i_jstrs_n: ステップnの室iの統合された境界j*における裏面の温度, degree C, [j*]

    Returns:
        ステップn+1の室iの統合された境界j*における係数CRX, degree C, [j*]
    """
    return phi_t_0_bnd_i_jstrs * theta_rear_i_jstrs_n + q_sol_floor_i_jstrs_n * phi_a_0_bnd_i_jstrs


def get_theta_srf_dsh_a_i_jstrs_npls_ms(
        q_srf_jstrs_n: np.ndarray,
        phi_a_1_bnd_i_jstrs_ms: np.ndarray,
        r_bnd_i_jstrs_ms: np.ndarray,
        theta_dsh_srf_a_jstrs_n_ms: np.ndarray
) -> np.ndarray:
    """

    Args:
        q_srf_jstrs_n: ステップnの統合された境界j*における表面熱流（壁体吸熱を正とする）, W/m2, [j*]
        phi_a_1_bnd_i_jstrs_ms: 室iの統合された境界j*における項別公比法の項mの吸熱応答係数の係数, m2K/W, [jstrs, 12]
        r_bnd_i_jstrs_ms: 室iの統合された境界j*の項mにおける公比, [jstrs, 12]
        theta_dsh_srf_a_jstrs_n_ms: ステップnの統合された境界j*における指数項mの吸熱応答の項別成分, degree C, [j*, 12]
    Returns:
        ステップn+1の室iの統合された境界j*における項別公比法の項mの吸熱応答に関する表面温度, degree C, [jstrs, 12]
    """

    return phi_a_1_bnd_i_jstrs_ms * q_srf_jstrs_n[:, np.newaxis] + r_bnd_i_jstrs_ms * theta_dsh_srf_a_jstrs_n_ms


def get_theta_srf_dsh_t_i_jstrs_npls_ms(
        theta_rear_i_jstrs_n: np.ndarray,
        phi_t_1_bnd_i_jstrs_ms: np.ndarray,
        r_bnd_i_jstrs_ms: np.ndarray,
        theta_dsh_srft_jstrs_n_m: np.ndarray
) -> np.ndarray:
    """

    Args:
        theta_rear_i_jstrs_n: ステップnの室iの統合された境界j*における裏面の温度, degree C, [jstrs]
        phi_t_1_bnd_i_jstrs_ms: 室iの統合された境界j*における項別公比法の項mの貫流応答の係数, [jstrs, 12]
        r_bnd_i_jstrs_ms: 室iの統合された境界j*の項mにおける公比, [jstrs, 12]
        theta_dsh_srft_jstrs_n_m: ステップnの統合された境界j*における指数項mの貫流応答の項別成分, degree C, [j*, 12]
    Returns:
        ステップn+1の室iの統合された境界j*における項別公比法の項mの貫流応答に関する表面温度, degree C, [jstrs, 12]
    """

    return theta_rear_i_jstrs_n[:, np.newaxis] * phi_t_1_bnd_i_jstrs_ms + r_bnd_i_jstrs_ms * theta_dsh_srft_jstrs_n_m


def get_cvl_i_jstrs_npls(
        theta_srf_dsh_t_i_jstrs_npls_ms: np.ndarray, theta_srf_dsh_a_i_jstrs_npls_ms: np.ndarray) -> np.ndarray:
    """

    Args:
        theta_srf_dsh_t_i_jstrs_npls_ms:
            ステップn+1の室iの統合された境界j*における項別公比法の項mの貫流応答に関する表面温度, degree C, [j*, 12]
        theta_srf_dsh_a_i_jstrs_npls_ms:
            ステップn+1の室iの統合された境界j*における項別公比法の項mの吸熱応答に関する表面温度, degree C, [j*, 12]

    Returns:
        ステップn+1の室iの統合された境界j*における係数CVL, degree C, [i*]
    """

    return np.sum(theta_srf_dsh_t_i_jstrs_npls_ms + theta_srf_dsh_a_i_jstrs_npls_ms, axis=1)


# 室内表面熱流の計算 式(28)
def calc_qi(
        h_c_bnd_jstrs, a_bnd_jstrs, h_r_bnd_jstrs, q_sol_srf_jstrs_n, flr_is_k,
        ts_is_k_n, theta_r_is_npls: float, f_mrt_jstrs: float, lrs_is_n: float, beta_is: float, p):
    """
    :param Tr: 室温
    :param Tsx: 形態係数加重平均表面温度
    :param Lr:
    :param Beta:
    :return:
    """

    # 対流成分, W
    Qc = h_c_bnd_jstrs * a_bnd_jstrs * (np.dot(p.T, theta_r_is_npls).flatten() - ts_is_k_n)

    # 平均放射温度の計算
    Tsx = (np.dot(f_mrt_jstrs, ts_is_k_n.reshape(-1, 1)).flatten())

    # 放射成分, W
    Qr = h_r_bnd_jstrs * a_bnd_jstrs * (np.dot(p.T, Tsx.reshape(-1, 1)).flatten() - ts_is_k_n)

    # 短波長熱取得成分, W
    RS = q_sol_srf_jstrs_n * a_bnd_jstrs

    # 放射暖房成分, W
    Lr = flr_is_k * np.dot(p.T, (lrs_is_n * (1.0 - beta_is)).reshape(-1, 1)).flatten()

    # 表面熱流合計, W
    Qt = Qc + Qr + Lr + RS

    # 前時刻熱流の保持
    oldqi = Qt / a_bnd_jstrs

    return Qc, Qr, oldqi


# 室内表面熱流 [W/m2]
def get_qi(Qt, area):
    return Qt / area


# 室内等価温度の計算 式(29)
def calc_Tei(hic, hir, RSsol, flr, area, Tr, Fmrt, Ts, Lr, Beta):
    """
    :param Tr: 室温
    :param Tsx: 形態係数加重平均表面温度
    :param Lr:
    :param Beta:
    :return:
    """

    # 平均放射温度の計算
    Tsx = get_Tsx(Fmrt, Ts)

    return Tr * hic / (hic + hir) \
           + Tsx * hir / (hic + hir) \
           + RSsol / (hic + hir) \
           + flr * Lr * (1.0 - Beta) / (hic + hir) / area


# 平均放射温度の計算
def get_Tsx(Fmrt, Ts):
    return np.sum(Fmrt * Ts)
