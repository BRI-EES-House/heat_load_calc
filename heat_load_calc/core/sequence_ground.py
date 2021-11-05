import numpy as np

from heat_load_calc.core.pre_calc_parameters import PreCalcParametersGround
from heat_load_calc.core.conditions import GroundConditions


# 地盤の計算（n+1ステップを計算する）
def run_tick(gc_n: GroundConditions, ss: PreCalcParametersGround, n: int):

    h_i_js = ss.h_s_r_js + ss.h_s_c_js

    theta_dsh_srf_a_js_ms_npls = ss.phi_a1_js_ms * gc_n.q_srf_js_n + ss.r_js_ms * gc_n.theta_dsh_srf_a_js_ms_n
    theta_dsh_srf_t_js_ms_npls = ss.phi_t1_js_ms * ss.theta_dstrb_js_ns[:, [n]] + ss.r_js_ms * gc_n.theta_dsh_srf_t_js_ms_n

    theta_s_js_npls = (ss.phi_a0_js * h_i_js * ss.theta_o_ns[n+1] + ss.phi_t0_js * ss.theta_dstrb_js_ns[:, [n+1]]
        + np.sum(theta_dsh_srf_a_js_ms_npls, axis=1, keepdims=True)
        + np.sum(theta_dsh_srf_t_js_ms_npls, axis=1, keepdims=True)) \
        / (1.0 + ss.phi_a0_js * h_i_js)

    q_srf_js_n = h_i_js * (ss.theta_o_ns[n+1] - theta_s_js_npls)

    return GroundConditions(
        theta_dsh_srf_a_js_ms_n=theta_dsh_srf_a_js_ms_npls,
        theta_dsh_srf_t_js_ms_n=theta_dsh_srf_t_js_ms_npls,
        q_srf_js_n=q_srf_js_n,
    )


