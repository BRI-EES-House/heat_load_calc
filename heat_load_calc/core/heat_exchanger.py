import numpy as np

from typing import Union

from heat_load_calc.external.psychrometrics import get_p_vs, get_x, get_p_vs_is2
from heat_load_calc.external.global_number import get_c_air, get_rho_air
from heat_load_calc.core.matrix_method import v_diag


def get_dehumid_coeff(lcs_is_n, theta_r_is_npls, x_r_non_dh_is_n, rac_spec):
    # Lcsは加熱が正で表される。
    # 加熱時は除湿しない。
    # 以下の取り扱いを簡単にするため（冷房負荷を正とするため）、正負を反転させる
    qs_is_n = -lcs_is_n

    dh = qs_is_n > 1.0e-3

    v_ac_is_n = np.zeros_like(lcs_is_n, dtype=float)

    v_ac_is_n[dh] = _get_vac_rac_i_n(
        q_rac_max_i=rac_spec['q_max'][dh],
        q_rac_min_i=rac_spec['q_min'][dh],
        q_s_i_n=qs_is_n[dh],
        v_rac_max_i=rac_spec['v_max'][dh]/60,
        v_rac_min_i=rac_spec['v_min'][dh]/60
    )

    bf = 0.2

    x_e_out_is_n = np.zeros_like(lcs_is_n, dtype=float)

    x_e_out_is_n[dh] = get_x_e_out_is_n(
        bf=bf,
        qs_is_n=qs_is_n[dh],
        theta_r_is_npls=theta_r_is_npls[dh],
        vac_is_n=v_ac_is_n[dh]
    )

    v_ac_is_n = v_ac_is_n * (1 - bf)

    brmx_rac_is = v_diag(get_rho_air() * v_ac_is_n)
    brxc_rac_is = get_rho_air() * v_ac_is_n * x_e_out_is_n

    brmx_rac_is = v_diag(np.where(x_e_out_is_n > x_r_non_dh_is_n, 0.0, np.diag(brmx_rac_is).reshape(-1, 1)))
    brxc_rac_is = np.where(x_e_out_is_n > x_r_non_dh_is_n, 0.0, brxc_rac_is)

    return brmx_rac_is, brxc_rac_is


def get_x_e_out_is_n(bf, qs_is_n, theta_r_is_npls, vac_is_n):

    # 熱交換器温度＝熱交換器部分吹出温度 式(113)

    theta_e_out_is_n = _get_theta_rac_ex_srf_i_n_pls(bf, qs_is_n, theta_r_is_npls, vac_is_n)

    x_e_out_is_n = get_x(get_p_vs_is2(theta_e_out_is_n))

    return x_e_out_is_n


def _get_theta_rac_ex_srf_i_n_pls(bf_rac_i: float, q_s_i_n: float, theta_r_i_n_pls: float, v_rac_i_n: float) -> float:
    """
    ステップ n+1 における室 i に設置されたルームエアコンディショナーの室内機の熱交換器表面温度を計算する。
    Args:
        bf_rac_i: 室 i に設置されたルームエアコンディショナーの室内機の熱交換器のバイパスファクター, -
        q_s_i_n: ステップ n から n+1 における室 i の顕熱負荷, W
        theta_r_i_n_pls: ステップ n+1 における室 i の温度, degree C
        v_rac_i_n: ステップ n から n+1 における室 i に設置されたルームエアコンディショナーの吹き出し風量, m3/s

    Returns:
        ステップ n+1 における室 i に設置されたルームエアコンディショナーの室内機の熱交換器表面温度, degree C
    Notes:
        繰り返し計算（温度と湿度） eq.14
    """

    return theta_r_i_n_pls - q_s_i_n / (get_c_air() * get_rho_air() * v_rac_i_n * (1.0 - bf_rac_i))


def _get_vac_rac_i_n(
        q_rac_max_i: Union[float, np.ndarray],
        q_rac_min_i: Union[float, np.ndarray],
        q_s_i_n: Union[float, np.ndarray],
        v_rac_max_i: Union[float, np.ndarray],
        v_rac_min_i: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """
    ルームエアコンディショナーの吹き出し風量を顕熱負荷に応じて計算する。

    Args:
        q_rac_max_i: 室 i に設置されたルームエアコンディショナーの最大能力, W
        q_rac_min_i: 室 i に設置されたルームエアコンディショナーの最小能力, W
        q_s_i_n:　ステップ n からステップ n+1 における室 i の顕熱負荷, W
        v_rac_max_i: 室 i に設置されたルームエアコンディショナーの最小能力時における風量, m3/s
        v_rac_min_i: 室 i に設置されたルームエアコンディショナーの最大能力時における風量, m3/s
    Returns:
        室iに設置されたルームエアコンディショナーの吹き出し風量, m3/s
    Notes:
        繰り返し計算（湿度と潜熱） eq.14
    """

    # 吹き出し風量（仮）, m3/s
    v = v_rac_min_i * (q_rac_max_i - q_s_i_n) / (q_rac_max_i - q_rac_min_i)\
        + v_rac_max_i * (q_rac_min_i - q_s_i_n) / (q_rac_min_i - q_rac_max_i)

    # 下限値・上限値でクリップ後の吹き出し風量, m3/s
    v_rac_i_n = np.clip(v, a_min=v_rac_min_i, a_max=v_rac_max_i)

    return v_rac_i_n

