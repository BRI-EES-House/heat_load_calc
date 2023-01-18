import numpy as np

from heat_load_calc.pre_calc_parameters import PreCalcParametersGround, PreCalcParameters
from heat_load_calc.conditions import GroundConditions


# 地盤の計算（n+1ステップを計算する）
def run_tick(pp: PreCalcParameters, gc_n: GroundConditions, ss: PreCalcParametersGround, n: int):

    is_ground = pp.bs.is_ground_js.flatten()

    # h_i_js = ss.h_s_r_js + ss.h_s_c_js
    #h_i_js = pp.bs.h_s_r_js[is_ground, :] + ss.h_s_c_js
    h_i_js = pp.bs.h_s_r_js[is_ground, :] + pp.bs.h_s_c_js[is_ground, :]

    #theta_dsh_srf_a_js_ms_npls = ss.phi_a1_js_ms * gc_n.q_srf_js_n + ss.r_js_ms * gc_n.theta_dsh_srf_a_js_ms_n
    theta_dsh_srf_a_js_ms_npls = pp.bs.phi_a1_js_ms[is_ground, :] * gc_n.q_srf_js_n + ss.r_js_ms * gc_n.theta_dsh_srf_a_js_ms_n

    # theta_dsh_srf_t_js_ms_npls = ss.phi_t1_js_ms * ss.k_eo_js * ss.theta_o_eqv_js_ns[:, [n]] + ss.r_js_ms * gc_n.theta_dsh_srf_t_js_ms_n
    theta_dsh_srf_t_js_ms_npls = ss.phi_t1_js_ms * pp.bs.k_eo_js[is_ground, :] * ss.theta_o_eqv_js_ns[:, [n]] + ss.r_js_ms * gc_n.theta_dsh_srf_t_js_ms_n

    theta_s_js_npls = (
        # ss.phi_a0_js * h_i_js * pp.weather.theta_o_ns_plus[n + 1]
        pp.bs.phi_a0_js[is_ground, :] * h_i_js * pp.weather.theta_o_ns_plus[n + 1]
        # + ss.phi_t0_js * ss.k_eo_js * ss.theta_o_eqv_js_ns[:, [n + 1]]
        # + ss.phi_t0_js * pp.bs.k_eo_js[is_ground, :] * ss.theta_o_eqv_js_ns[:, [n + 1]]
        + pp.bs.phi_t0_js[is_ground, :] * pp.bs.k_eo_js[is_ground, :] * ss.theta_o_eqv_js_ns[:, [n + 1]]
        + np.sum(theta_dsh_srf_a_js_ms_npls, axis=1, keepdims=True)
        + np.sum(theta_dsh_srf_t_js_ms_npls, axis=1, keepdims=True)
#    ) / (1.0 + ss.phi_a0_js * h_i_js)
    ) / (1.0 + pp.bs.phi_a0_js[is_ground, :] * h_i_js)

    q_srf_js_n = h_i_js * (pp.weather.theta_o_ns_plus[n + 1] - theta_s_js_npls)

    return GroundConditions(
        theta_dsh_srf_a_js_ms_n=theta_dsh_srf_a_js_ms_npls,
        theta_dsh_srf_t_js_ms_n=theta_dsh_srf_t_js_ms_npls,
        q_srf_js_n=q_srf_js_n,
    )


