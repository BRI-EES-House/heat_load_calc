import numpy as np

from heat_load_calc.external.psychrometrics import get_p_vs, get_x, get_p_vs_is2
from heat_load_calc.external.global_number import get_c_air, get_rho_air
from heat_load_calc.core.matrix_method import v_diag


def get_dehumid_coeff(lcs_is_n, theta_r_is_npls, rac_spec, x_r_non_dh_is_n):
    # Lcsは加熱が正で表される。
    # 加熱時は除湿しない。
    # 以下の取り扱いを簡単にするため（冷房負荷を正とするため）、正負を反転させる
    qs_is_n = -lcs_is_n

    dh = qs_is_n > 1.0e-3

    v_ac_is_n = np.zeros_like(lcs_is_n, dtype=float)

    v_ac_is_n[dh] = get_vac_is_n(
        q_max=rac_spec['q_max'][dh],
        q_min=rac_spec['q_min'][dh],
        qs_is_n=qs_is_n[dh],
        v_max=rac_spec['v_max'][dh],
        v_min=rac_spec['v_min'][dh]
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

    theta_e_out_is_n = theta_r_is_npls - qs_is_n / (get_c_air() * get_rho_air() * vac_is_n * (1.0 - bf))

    x_e_out_is_n = get_x(get_p_vs_is2(theta_e_out_is_n))

    return x_e_out_is_n


def get_vac_is_n(q_max, q_min, qs_is_n, v_max, v_min):

    # TODO 最小値・最大値処理がないような気がする
    return (v_min + (v_max - v_min) / (q_max - q_min) * (qs_is_n - q_min)) / 60.0

