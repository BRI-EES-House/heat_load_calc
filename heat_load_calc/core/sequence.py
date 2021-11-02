import numpy as np

from heat_load_calc.core.operation_mode import OperationMode
from heat_load_calc.core.pre_calc_parameters import PreCalcParameters
from heat_load_calc.core.conditions import Conditions
from heat_load_calc.external.global_number import get_c_air, get_rho_air, get_l_wtr
from heat_load_calc.core.log import Logger
from heat_load_calc.core.matrix_method import v_diag
from heat_load_calc.core import occupants


def run_tick(n: int, delta_t: float, ss: PreCalcParameters, c_n: Conditions, logger: Logger, run_up: bool) -> Conditions:
    """
    室の温湿度・熱負荷の計算
    Args:
        n: ステップ
        delta_t: 時間間隔, s
        ss: ループ計算前に計算可能なパラメータを含めたクラス
        c_n: 前の時刻からの状態量
        logger: ロギング用クラス
        run_up: 助走計算か否か
    Returns:
        次の時刻にわたす状態量
    """

    # ステップnにおける室iの状況（在室者周りの総合熱伝達率・運転状態・Clo値・目標とする作用温度）を取得する
    #     ステップnにおける室iの在室者周りの対流熱伝達率, W/(m2 K), [i, 1]
    #     ステップnにおける室iの在室者周りの放射熱伝達率, W/(m2 K), [i, 1]
    #     ステップnの室iにおける運転モード, [i, 1]
    #     ステップnの室iにおける目標作用温度下限値, degree C, [i, 1]
    #     ステップnの室iにおける目標作用温度上限値, degree C, [i, 1]
    #     ステップnの室iの在室者周りの風速, m/s, [i, 1]
    #     ステップnの室iにおけるClo値, [i, 1]
    #     ステップnの室iにおける目標作用温度, degree C, [i, 1]
    h_hum_c_is_n, h_hum_r_is_n, operation_mode_is_n, theta_lower_target_is_n_pls, theta_upper_target_is_n_pls, remarks_is_n \
        = ss.get_ot_target_and_h_hum(
            x_r_is_n=c_n.x_r_is_n,
            operation_mode_is_n_mns=c_n.operation_mode_is_n,
            theta_r_is_n=c_n.theta_r_is_n,
            theta_mrt_hum_is_n=c_n.theta_mrt_hum_is_n,
            ac_demand_is_n=ss.ac_demand_is_ns[:, n].reshape(-1, 1)
        )

    # ステップnの境界jにおける裏面温度, degree C, [j, 1]
    theta_rear_js_n = get_theta_rear_js_n(
        k_ei_js_js=ss.k_ei_js_js,
        theta_dstrb_js_n=ss.theta_dstrb_js_ns[:, n + 1].reshape(-1, 1),
        theta_ei_js_n=c_n.theta_ei_js_n
    )

    # ステップnからステップn+1における室iの1人あたりの人体発熱, W, [i, 1]
    q_hum_psn_is_n = occupants.get_q_hum_psn_is_n(theta_r_is_n=c_n.theta_r_is_n)

    # ステップ n からステップ n+1 における室 i の人体発熱, W, [i, 1]
    q_hum_is_n = get_q_hum_is_n(n_hum_is_n=ss.n_hum_is_ns[:, n].reshape(-1, 1), q_hum_psn_is_n=q_hum_psn_is_n)

    # ステップnの室iにおけるすきま風量, m3/s, [i, 1]
    v_leak_is_n = ss.get_infiltration(theta_r_is_n=c_n.theta_r_is_n, theta_o_n=ss.theta_o_ns[n])

    # ステップ n+1 の境界 j における項別公比法の指数項 m の貫流応答の項別成分, degree C, [j, m] (m=12), eq.(29)
    theta_dsh_s_t_js_ms_n_pls = get_theta_dsh_s_t_js_ms_n_pls(
        phi_t1_js_ms=ss.phi_t1_js_ms,
        r_js_ms=ss.r_js_ms,
        theta_dsh_srf_t_js_ms_n=c_n.theta_dsh_srf_t_js_ms_n,
        theta_rear_js_n=theta_rear_js_n
    )

    # ステップ n+1 の境界 j における項別公比法の指数項 m の吸熱応答の項別成分, degree C, [j, m]
    theta_dsh_s_a_js_ms_n_pls = get_theta_dsh_s_a_js_ms_n_pls(
        phi_a1_js_ms=ss.phi_a1_js_ms,
        q_srf_js_n=c_n.q_srf_js_n,
        r_js_ms=ss.r_js_ms,
        theta_dsh_srf_a_js_ms_n=c_n.theta_dsh_srf_a_js_ms_n
    )

    # ステップ n+1 の境界 j における係数f_CVL, degree C, [j, 1]
    f_cvl_js_n_pls = get_f_cvl_js_n_pls(
        theta_dsh_s_a_js_ms_n_pls=theta_dsh_s_a_js_ms_n_pls,
        theta_dsh_s_t_js_ms_n_pls=theta_dsh_s_t_js_ms_n_pls
    )

    # ステップ n+1 の境界 j における係数 f_WSV, degree C, [j, 1]
    f_wsv_js_n_pls = get_f_wsv_js_n_pls(
        f_cvl_js_n_pls=f_cvl_js_n_pls,
        f_ax_js_js=ss.f_ax_js_js
    )

    # ステップ n からステップ n+1 における室 i の自然風利用による換気量, m3/s, [i, 1]
    v_vent_ntr_is_n = get_v_vent_ntr_is_n(
        operation_mode_is_n=operation_mode_is_n,
        v_vent_ntr_set_is=ss.v_vent_ntr_set_is
    )

    # ステップ n からステップ n+1 における室 i の換気・隙間風・自然風の利用による外気の流入量, m3/s, [i, 1]
    v_vent_out_is_n = get_v_vent_out_is_n(
        v_leak_is_n=v_leak_is_n,
        v_vent_mec_is_n=ss.v_mec_vent_is_ns[:, n].reshape(-1, 1),
        v_vent_ntr_is_n=v_vent_ntr_is_n
    )

    # ステップ n+1 の室 i における係数 f_BRC, W, [i, 1]
    f_brc_is_n_pls = get_f_brc_is_n_pls(
        a_s_js=ss.a_s_js,
        c_air=get_c_air(),
        c_rm_is=ss.c_rm_is,
        c_sh_frt_is=ss.c_sh_frt_is,
        delta_t=delta_t,
        f_wsc_js_n_pls=ss.f_wsc_js_ns[:, n + 1].reshape(-1, 1),
        f_wsv_js_n_pls=f_wsv_js_n_pls,
        g_sh_frt_is=ss.g_sh_frt_is,
        h_s_c_js=ss.h_s_c_js,
        p_is_js=ss.p_is_js,
        q_gen_is_n=ss.q_gen_is_ns[:, n].reshape(-1, 1),
        q_hum_is_n=q_hum_is_n,
        q_sol_frt_is_n=ss.q_sol_frt_is_ns[:, n].reshape(-1, 1),
        rho_air=get_rho_air(),
        theta_frt_is_n=c_n.theta_frt_is_n,
        theta_o_n_pls=ss.theta_o_ns[n + 1],
        theta_r_is_n=c_n.theta_r_is_n,
        v_vent_out_is_n=v_vent_out_is_n
    )

    # ステップ n+1 における係数 f_BRM, W/K, [i, i]
    f_brm_is_is_n_pls = get_f_brm_is_is_n_pls(
        a_s_js=ss.a_s_js,
        c_air=get_c_air(),
        c_rm_is=ss.c_rm_is,
        c_sh_frt_is=ss.c_sh_frt_is,
        delta_t=delta_t,
        f_wsr_js_is=ss.f_wsr_js_is,
        g_sh_frt_is=ss.g_sh_frt_is,
        h_s_c_js=ss.h_s_c_js,
        p_is_js=ss.p_is_js,
        p_js_is=ss.p_js_is,
        rho_air=get_rho_air(),
        v_vent_int_is_is=ss.v_vent_int_is_is,
        v_vent_out_is_n=v_vent_out_is_n
    )

    # ステップ n における室 i の在室者表面における放射熱伝達率の総合熱伝達率に対する比, -, [i, 1]
    k_r_is_n = get_k_r_is_n(h_hum_c_is_n=h_hum_c_is_n, h_hum_r_is_n=h_hum_r_is_n)

    # ステップnにおける室iの在室者表面における対流熱伝達率の総合熱伝達率に対する比, -, [i, 1]
    k_c_is_n = get_k_c_is_n(h_hum_c_is_n=h_hum_c_is_n, h_hum_r_is_n=h_hum_r_is_n)

    # ステップn+1における室iの係数 XOT, [i, i]
    f_xot_is_is_n_pls = get_f_xot_is_is_n_pls(
        f_mrt_hum_is_js=ss.f_mrt_hum_is_js,
        f_wsr_js_is=ss.f_wsr_js_is,
        k_c_is_n=k_c_is_n,
        k_r_is_n=k_r_is_n
    )

    # ステップn+1における室iの係数 XC, [i, 1]
    f_xc_is_n_pls = get_f_xc_is_n_pls(
        f_mrt_hum_is_js=ss.f_mrt_hum_is_js,
        f_wsc_js_n_pls=ss.f_wsc_js_ns[:, n + 1].reshape(-1, 1),
        f_wsv_js_n_pls=f_wsv_js_n_pls,
        f_xot_is_is_n_pls=f_xot_is_is_n_pls,
        k_r_is_n=k_r_is_n
    )

    # ステップ n における係数 f_BRM,OT, W/K, [i, i]
    f_brm_ot_is_is_n_pls = get_f_brm_ot_is_is_n_pls(
        f_brm_is_is_n_pls=f_brm_is_is_n_pls,
        f_xot_is_is_n_pls=f_xot_is_is_n_pls
    )

    # ステップ n における係数 f_BRC,OT, W, [i, 1]
    f_brc_ot_is_n_pls = get_f_brc_ot_is_n_pls(
        f_brc_is_n_pls=f_brc_is_n_pls,
        f_brm_is_is_n_pls=f_brm_is_is_n_pls,
        f_xc_is_n_pls=f_xc_is_n_pls
    )

    # ステップ n+1 における自然作用温度, degree C, [i, 1]
    theta_r_ot_ntr_is_n_pls = get_theta_r_ot_ntr_is_n_pls(
        f_brc_ot_is_n_pls=f_brc_ot_is_n_pls,
        f_brm_ot_is_is_n_pls=f_brm_ot_is_is_n_pls
    )

    # ステップ n から n+1 において室 i で実際に暖房・冷房が行われるかどうかの判定結果, [i, 1]
    is_heating_is_n, is_cooling_is_n = get_is_heating_is_n_and_is_cooling_is_n(
        operation_mode_is_n=operation_mode_is_n,
        theta_lower_target_is_n_pls=theta_lower_target_is_n_pls,
        theta_r_ot_ntr_is_n_pls=theta_r_ot_ntr_is_n_pls,
        theta_upper_target_is_n_pls=theta_upper_target_is_n_pls
    )

    # ステップ n+1 における係数 f_flr, -, [j, i]
    f_flr_js_is_n = get_f_flr_js_is_n(
        f_flr_c_js_is=ss.f_flr_c_js_is,
        f_flr_h_js_is=ss.f_flr_h_js_is,
        is_cooling_is_n=is_cooling_is_n,
        is_heating_is_n=is_heating_is_n
    )

    # ステップ n からステップ n+1 における室 i の放射暖冷房設備の対流成分比率, -, [i, 1]
    beta_is_n = get_beta_is_n(
        beta_c_is=ss.beta_c_is,
        beta_h_is=ss.beta_h_is,
        is_cooling_is_n=is_cooling_is_n,
        is_heating_is_n=is_heating_is_n
    )

    # ステップ n における係数 f_FLB, K/W, [j, i]
    f_flb_js_is_n_pls = get_f_flb_js_is_n_pls(
        a_s_js=ss.a_s_js,
        beta_is_n=beta_is_n,
        f_flr_js_is_n=f_flr_js_is_n,
        h_s_c_js=ss.h_s_c_js,
        h_s_r_js=ss.h_s_r_js,
        k_ei_js_js=ss.k_ei_js_js,
        phi_a0_js=ss.phi_a0_js,
        phi_t0_js=ss.phi_t0_js
    )

    # ステップ n における係数 f_WSB, K/W, [j, i]
    f_wsb_js_is_n_pls = get_f_wsb_js_is_n_pls(
        f_flb_js_is_n_pls=f_flb_js_is_n_pls,
        f_ax_js_js=ss.f_ax_js_js
    )

    # ステップ n における係数 f_BRL, -, [i, i]
    f_brl_is_is_n = get_f_brl_is_is_n(
        a_s_js=ss.a_s_js,
        beta_is_n=beta_is_n,
        f_wsb_js_is_n_pls=f_wsb_js_is_n_pls,
        h_s_c_js=ss.h_s_c_js,
        p_is_js=ss.p_is_js
    )

    # ステップn+1における室iの係数 f_XLR, K/W, [i, i]
    f_xlr_is_is_n_pls = get_f_xlr_is_is_n_pls(
        f_mrt_hum_is_js=ss.f_mrt_hum_is_js,
        f_wsb_js_is_n_pls=f_wsb_js_is_n_pls,
        f_xot_is_is_n_pls=f_xot_is_is_n_pls,
        k_r_is_n=k_r_is_n
    )

    # ステップ n における係数 f_BRL_OT, -, [i, i]
    f_brl_ot_is_is_n = get_f_brl_ot_is_is_n(
        f_brl_is_is_n=f_brl_is_is_n,
        f_brm_is_is_n_pls=f_brm_is_is_n_pls,
        f_xlr_is_is_n_pls=f_xlr_is_is_n_pls
    )

    # ステップ n+1 における室 i の作用温度, degree C, [i, 1] (ステップn+1における瞬時値）
    # ステップ n における室 i に設置された対流暖房の放熱量, W, [i, 1] (ステップn～ステップn+1までの平均値）
    # ステップ n における室 i に設置された放射暖房の放熱量, W, [i, 1]　(ステップn～ステップn+1までの平均値）
    theta_ot_is_n_pls, l_cs_is_n, l_rs_is_n = ss.calc_next_temp_and_load(
        brc_ot_is_n=f_brc_ot_is_n_pls,
        brm_ot_is_is_n=f_brm_ot_is_is_n_pls,
        brl_ot_is_is_n=f_brl_ot_is_is_n,
        theta_lower_target_is_n=theta_lower_target_is_n_pls,
        theta_upper_target_is_n=theta_upper_target_is_n_pls,
        operation_mode_is_n=operation_mode_is_n,
        ac_demand_is_n=ss.ac_demand_is_ns[:, n].reshape(-1, 1),
        theta_natural_is_n=theta_r_ot_ntr_is_n_pls,
        is_heating_is_n=is_heating_is_n,
        is_cooling_is_n=is_cooling_is_n
    )

    # ステップ n+1 における室 i の室温, degree C, [i, 1]
    theta_r_is_n_pls = get_theta_r_is_n_pls(
        f_xc_is_n_pls=f_xc_is_n_pls,
        f_xlr_is_is_n_pls=f_xlr_is_is_n_pls,
        f_xot_is_is_n_pls=f_xot_is_is_n_pls,
        l_rs_is_n=l_rs_is_n,
        theta_ot_is_n_pls=theta_ot_is_n_pls
    )

    # ステップ n+1 における境界 j の表面温度, degree C, [j, 1]
    theta_s_js_n_pls = get_theta_s_js_n_pls(
        f_wsb_js_is_n_pls=f_wsb_js_is_n_pls,
        f_wsc_js_n_pls=ss.f_wsc_js_ns[:, n + 1].reshape(-1, 1),
        f_wsr_js_is=ss.f_wsr_js_is,
        f_wsv_js_n_pls=f_wsv_js_n_pls,
        l_rs_is_n=l_rs_is_n,
        theta_r_is_n_pls=theta_r_is_n_pls
    )

    # ステップ n+1 における室 i　の家具の温度, degree C, [i, 1]
    theta_frt_is_n_pls = get_theta_frt_is_n_pls(
        c_sh_frt_is=ss.c_sh_frt_is,
        delta_t=delta_t,
        g_sh_frt_is=ss.g_sh_frt_is,
        q_sol_frt_is_n=ss.q_sol_frt_is_ns[:, n].reshape(-1, 1),
        theta_frt_is_n=c_n.theta_frt_is_n,
        theta_r_is_n_pls=theta_r_is_n_pls
    )

    # ステップ n+1 における室 i の人体に対する平均放射温度, degree C, [i, 1]
    theta_mrt_hum_is_n_pls = get_theta_mrt_hum_is_n_pls(
        f_mrt_hum_is_js=ss.f_mrt_hum_is_js,
        theta_s_js_n_pls=theta_s_js_n_pls
    )

    # ステップ n+1 における境界 j の等価温度, degree C, [j, 1]
    theta_ei_js_n_pls = get_theta_ei_js_n_pls(
        a_s_js=ss.a_s_js,
        beta_is_n=beta_is_n,
        f_mrt_js_js=ss.f_mrt_js_js,
        f_flr_js_is_n=f_flr_js_is_n,
        h_s_c_js=ss.h_s_c_js,
        h_s_r_js=ss.h_s_r_js,
        l_rs_is_n=l_rs_is_n,
        p_js_is=ss.p_js_is,
        q_s_sol_js_n_pls=ss.q_s_sol_js_ns[:, n + 1].reshape(-1, 1),
        theta_r_is_n_pls=theta_r_is_n_pls,
        theta_s_js_n_pls=theta_s_js_n_pls
    )

    # ステップ n+1 における境界 j の表面熱流（壁体吸熱を正とする）, W/m2, [j, 1]
    q_s_js_n_pls = get_q_s_js_n_pls(
        h_s_c_js=ss.h_s_c_js,
        h_s_r_js=ss.h_s_r_js,
        theta_ei_js_n_pls=theta_ei_js_n_pls,
        theta_s_js_n_pls=theta_s_js_n_pls
    )

    # ステップnの室iにおける1人あたりの人体発湿, kg/s, [i, 1]
    x_hum_psn_is_n = occupants.get_x_hum_psn_is_n(theta_r_is_n=c_n.theta_r_is_n)

    # ステップnの室iにおける人体発湿, kg/s, [i, 1]
    x_hum_is_n = get_x_hum_is_n(
        n_hum_is_n=ss.n_hum_is_ns[:, n].reshape(-1, 1),
        x_hum_psn_is_n=x_hum_psn_is_n
    )

    # ステップ n における室　i　の潜熱バランスに関する係数, kg/s, [i, 1]
    f_h_cst_is_n = get_f_h_cst_is_n(
        c_lh_frt_is=ss.c_lh_frt_is,
        delta_t=delta_t,
        g_lh_frt_is=ss.g_lh_frt_is,
        rho_air=get_rho_air(),
        v_rm_is=ss.v_rm_is,
        v_vent_out_is_n=v_vent_out_is_n,
        x_frt_is_n=c_n.x_frt_is_n,
        x_gen_is_n=ss.x_gen_is_ns[:, n].reshape(-1, 1),
        x_hum_is_n=x_hum_is_n,
        x_o_n_pls=ss.x_o_ns[n + 1],
        x_r_is_n=c_n.x_r_is_n
    )

    # ステップ n における室 i* の絶対湿度が室 i の潜熱バランスに与える影響を表す係数,　kg/(s kg/kg(DA)), [i, i]
    f_h_wgt_is_is_n = get_f_h_wgt_is_is_n(
        c_lh_frt_is=ss.c_lh_frt_is,
        delta_t=delta_t,
        g_lh_frt_is=ss.g_lh_frt_is,
        rho_air=get_rho_air(),
        v_rm_is=ss.v_rm_is,
        v_vent_int_is_is=ss.v_vent_int_is_is,
        v_vent_out_is_n=v_vent_out_is_n
    )

    # ステップ n+1 における室 i の加湿・除湿を行わない場合の絶対湿度, kg/kg(DA) [i, 1]
    x_r_ntr_is_n_pls = get_x_r_ntr_is_n_pls(
        f_h_cst_is_n=f_h_cst_is_n,
        f_h_wgt_is_is_n=f_h_wgt_is_is_n
    )

    # ステップ n+1 における室 i∗ の絶対湿度がステップ n から n+1 における室 i の潜熱負荷に与える影響を表す係数, kg/(s (kg/kg(DA))), [i, i*]
    # ステップ n から n+1 における室 i の潜熱負荷に与える影響を表す係数, kg/s, [i, 1]
    f_l_cl_cst_is_n, f_l_cl_wgt_is_is_n = ss.get_f_l_cl(
        l_cs_is_n=l_cs_is_n,
        theta_r_is_n_pls=theta_r_is_n_pls,
        x_r_ntr_is_n_pls=x_r_ntr_is_n_pls
    )

    # ステップ n+1 における室 i の 絶対湿度, kg/kg(DA), [i, 1]
    x_r_is_n_pls = get_x_r_is_n_pls(
        f_h_cst_is_n=f_h_cst_is_n,
        f_h_wgt_is_is_n=f_h_wgt_is_is_n,
        f_l_cl_cst_is_n=f_l_cl_cst_is_n,
        f_l_cl_wgt_is_is_n=f_l_cl_wgt_is_is_n
    )

    # ステップ n から ステップ n+1 における室 i の潜熱負荷（加湿を正・除湿を負とする）, kg/s, [i, 1]
    l_cl_is_n = get_l_cl_is_n(
        f_l_cl_wgt_is_is_n=f_l_cl_wgt_is_is_n,
        f_l_cl_cst_is_n=f_l_cl_cst_is_n,
        l_wtr=get_l_wtr(),
        x_r_is_n_pls=x_r_is_n_pls
    )

    # ステップ n+1 における室 i の家具等の絶対湿度, kg/kg(DA), [i, 1]
    x_frt_is_n_pls = get_x_frt_is_n_pls(
        c_lh_frt_is=ss.c_lh_frt_is,
        delta_t=delta_t,
        g_lh_frt_is=ss.g_lh_frt_is,
        x_frt_is_n=c_n.x_frt_is_n,
        x_r_is_n_pls=x_r_is_n_pls
    )

    if not run_up:
        # 次の時刻に引き渡す値
        # 積算値
        logger.operation_mode[:, n] = operation_mode_is_n.flatten()
        # 瞬時値
        logger.theta_r[:, n] = theta_r_is_n_pls.flatten()
        logger.theta_mrt_hum[:, n] = theta_mrt_hum_is_n_pls.flatten()
        logger.x_r[:, n] = x_r_is_n_pls.flatten()
        logger.theta_frt[:, n] = theta_frt_is_n_pls.flatten()
        logger.x_frt[:, n] = x_frt_is_n_pls.flatten()
        logger.theta_ei[:, n] = theta_ei_js_n_pls.flatten()

        # 次の時刻に引き渡さない値
        # 積算値
        logger.q_hum[:, n] = q_hum_is_n.flatten()
        logger.x_hum[:, n] = x_hum_is_n.flatten()
        logger.l_cs[:, n] = l_cs_is_n.flatten()
        logger.l_rs[:, n] = l_rs_is_n.flatten()
        logger.l_cl[:, n] = l_cl_is_n.flatten()
        # 平均値
        logger.v_reak_is_ns[:, n] = v_leak_is_n.flatten()
        logger.v_ntrl_is_ns[:, n] = v_vent_ntr_is_n.flatten()
        logger.h_hum_c_is_n[:, n] = h_hum_c_is_n.flatten()
        logger.h_hum_r_is_n[:, n] = h_hum_r_is_n.flatten()
        # 瞬時値
        logger.theta_ot[:, n] = theta_ot_is_n_pls.flatten()
        logger.theta_s[:, n] = theta_s_js_n_pls.flatten()
        logger.theta_rear[:, n] = theta_rear_js_n.flatten()
        logger.qiall_s[:, n] = q_s_js_n_pls.flatten()

        logger.pmv_target[:, n] = np.array([remark['pmv_target'] for remark in remarks_is_n])
        logger.v_hum[:, n] = np.array([remark['v_hum m/s'] for remark in remarks_is_n])
        logger.clo[:, n] = np.array([remark['clo'] for remark in remarks_is_n])

    return Conditions(
        operation_mode_is_n=operation_mode_is_n,
        theta_r_is_n=theta_r_is_n_pls,
        theta_mrt_hum_is_n=theta_mrt_hum_is_n_pls,
        x_r_is_n=x_r_is_n_pls,
        theta_dsh_s_a_js_ms_n=theta_dsh_s_a_js_ms_n_pls,
        theta_dsh_s_t_js_ms_n=theta_dsh_s_t_js_ms_n_pls,
        q_srf_js_n=q_s_js_n_pls,
        theta_frt_is_n=theta_frt_is_n_pls,
        x_frt_is_n=x_frt_is_n_pls,
        theta_ei_js_n=theta_ei_js_n_pls
    )


def get_x_frt_is_n_pls(c_lh_frt_is, delta_t: float, g_lh_frt_is, x_frt_is_n, x_r_is_n_pls):
    """

    Args:
        c_lh_frt_is: 室 i の備品等の湿気容量, kg/(kg/kg(DA)), [i, 1]
        delta_t: 1ステップの時間間隔, s
        g_lh_frt_is: 室 i の備品等と空気間の湿気コンダクタンス, kg/(s kg/kg(DA)), [i, 1]
        x_frt_is_n: ステップ n における室 i の備品等の絶対湿度, kg/kg(DA), [i, 1]
        x_r_is_n_pls: ステップ n+1 における室 i の絶対湿度, kg/kg(DA), [i, 1]

    Returns:
        ステップ n+1 における室 i の家具等の絶対湿度, kg/kg(DA), [i, 1]

    Notes:
        式(1.1)

    """

    return (c_lh_frt_is * x_frt_is_n + delta_t * g_lh_frt_is * x_r_is_n_pls) / (c_lh_frt_is + delta_t * g_lh_frt_is)


def get_l_cl_is_n(f_l_cl_wgt_is_is_n, f_l_cl_cst_is_n, l_wtr, x_r_is_n_pls):
    """

    Args:
        f_l_cl_wgt_is_is_n: 係数, kg/(s (kg/kg(DA)))
        f_l_cl_cst_is_n: 係数, kg/s
        l_wtr: 水の蒸発潜熱, J/kg
        x_r_is_n_pls: ステップ n+1 における室 i の絶対湿度, kg/kg(DA)

    Returns:
        ステップ n から ステップ n+1 における室 i の潜熱負荷（加湿を正・除湿を負とする）, W

    Notes:
        式(1.2)

    """

    return (np.dot(f_l_cl_wgt_is_is_n, x_r_is_n_pls) + f_l_cl_cst_is_n) * l_wtr


def get_x_r_is_n_pls(f_h_cst_is_n, f_h_wgt_is_is_n, f_l_cl_cst_is_n, f_l_cl_wgt_is_is_n):
    """

    Args:
        f_h_cst_is_n: 係数, kg/s
        f_h_wgt_is_is_n: 係数, kg/(s (kg/kg(DA)))
        f_l_cl_cst_is_n: 係数, kg/s
        f_l_cl_wgt_is_is_n: 係数, kg/(s (kg/kg(DA)))

    Returns:
        ステップ n+1 における室 i の 絶対湿度, kg/kg(DA), [i, 1]

    Notes:
        式(1.3)

    """

    return np.dot(np.linalg.inv(f_h_wgt_is_is_n - f_l_cl_wgt_is_is_n), f_h_cst_is_n + f_l_cl_cst_is_n)


def get_x_r_ntr_is_n_pls(f_h_cst_is_n, f_h_wgt_is_is_n):
    """

    Args:
        f_h_cst_is_n: 係数, kg/s
        f_h_wgt_is_is_n: 係数, kg/(s (kg/kg(DA)))

    Returns:
        ステップ n+1 における室 i の加湿・除湿を行わない場合の絶対湿度, kg/kg(DA) [i, 1]

    Notes:
        式(1.4)

    """

    return np.dot(np.linalg.inv(f_h_wgt_is_is_n), f_h_cst_is_n)


def get_f_h_wgt_is_is_n(c_lh_frt_is, delta_t, g_lh_frt_is, rho_air, v_rm_is, v_vent_int_is_is, v_vent_out_is_n):
    """

    Args:
        c_lh_frt_is: 室 i の備品等の湿気容量, kg/(kg/kg(DA)), [i, 1]
        delta_t: 1ステップの時間間隔, s
        g_lh_frt_is: 室 i の備品等と空気間の湿気コンダクタンス, kg/(s kg/kg(DA)), [i, 1]
        rho_air: 空気の密度, kg/m3
        v_rm_is: 室 i の容積, m3
        v_vent_int_is_is:　ステップ n から ステップ n+1 における室 i* から室 i への室間の空気移動量（流出換気量を含む）, m3/s
        v_vent_out_is_n: ステップ n から ステップ n+1 における室 i の換気・すきま風・自然風の利用による外気の流入量, m3/s

    Returns:
        ステップ n における室 i* の絶対湿度が室 i の潜熱バランスに与える影響を表す係数,　kg/(s kg/kg(DA)), [i, i]

    Notes:
        式(1.5)

    """

    return v_diag(
        rho_air * (v_rm_is / delta_t + v_vent_out_is_n)
        + c_lh_frt_is * g_lh_frt_is / (c_lh_frt_is + delta_t * g_lh_frt_is)
    ) - rho_air * v_vent_int_is_is


def get_f_h_cst_is_n(c_lh_frt_is, delta_t, g_lh_frt_is, rho_air, v_rm_is, v_vent_out_is_n, x_frt_is_n, x_gen_is_n, x_hum_is_n, x_o_n_pls, x_r_is_n):
    """

    Args:
        c_lh_frt_is: 室 i の備品等の湿気容量, kg/(kg/kg(DA)), [i, 1]
        delta_t: 1ステップの時間間隔, s
        g_lh_frt_is: 室 i の備品等と空気間の湿気コンダクタンス, kg/(s kg/kg(DA)), [i, 1]
        rho_air: 空気の密度, kg/m3
        v_rm_is: 室 i の容積, m3
        v_vent_out_is_n: ステップ n から ステップ n+1 における室 i の換気・すきま風・自然風の利用による外気の流入量, m3/s
        x_frt_is_n: ステップ n における室 i の備品等の絶対湿度, kg/kg(DA), [i, 1]
        x_gen_is_n: ステップ n からステップ n+1 における室 i の人体発湿を除く内部発湿, kg/s
        x_hum_is_n: ステップ n からステップ n+1 における室 i の人体発湿, kg/s
        x_o_n_pls: ステップ n における外気絶対湿度, kg/kg(DA)
        x_r_is_n: ステップ n における室 i の絶対湿度, kg/kg(DA)

    Returns:
        ステップ n における室 i の潜熱バランスに関する係数, kg/s, [i, 1]

    Notes:
        式(1.6)

    """

    return rho_air * v_rm_is / delta_t * x_r_is_n \
        + rho_air * v_vent_out_is_n * x_o_n_pls \
        + c_lh_frt_is * g_lh_frt_is / (c_lh_frt_is + delta_t * g_lh_frt_is) * x_frt_is_n \
        + x_gen_is_n + x_hum_is_n


def get_x_hum_is_n(n_hum_is_n, x_hum_psn_is_n):
    """

    Args:
        n_hum_is_n: ステップ n からステップ n+1 における室 i の在室人数, -
        x_hum_psn_is_n: ステップ n からステップ n+1 における室 i の1人あたりの人体発湿, kg/s

    Returns:
        ステップnの室iにおける人体発湿, kg/s, [i, 1]

    Notes:
        式(1.7)

    """

    return x_hum_psn_is_n * n_hum_is_n


def get_q_s_js_n_pls(h_s_c_js, h_s_r_js, theta_ei_js_n_pls, theta_s_js_n_pls):
    """

    Args:
        h_s_c_js: 境界 j の室内側対流熱伝達率, W/(m2 K), [j, 1]
        h_s_r_js: 境界 j の室内側放射熱伝達率, W/(m2 K), [j, 1]
        theta_ei_js_n_pls: ステップ n+1 における境界 j の等価温度, degree C, [j, 1]
        theta_s_js_n_pls: ステップ n+1 における境界 j の表面温度, degree C, [j, 1]

    Returns:
        ステップ n+1 における境界 j の表面熱流（壁体吸熱を正とする）, W/m2, [j, 1]

    Notes:
        式(2.1)

    """

    return (theta_ei_js_n_pls - theta_s_js_n_pls) * (h_s_c_js + h_s_r_js)


def get_theta_ei_js_n_pls(a_s_js, beta_is_n, f_mrt_js_js, f_flr_js_is_n, h_s_c_js, h_s_r_js, l_rs_is_n, p_js_is, q_s_sol_js_n_pls, theta_r_is_n_pls, theta_s_js_n_pls):
    """

    Args:
        a_s_js: 境界 j の面積, m2, [j, 1]
        beta_is_n: ステップ n からステップ n+1 における室 i の放射暖冷房設備の対流成分比率, -, [i, 1]
        f_mrt_js_js: 平均放射温度計算時の境界 j* の表面温度が境界 j に与える重み, -, [j, j*]
        f_flr_js_is_n: ステップ n からステップ n+1 における室 i の放射暖冷房設備の放熱量の放射成分に対する境界 j の室内側表面の吸収比率, -, [j, i]
        h_s_c_js: 境界 j の室内側対流熱伝達率, W/(m2 K), [j, 1]
        h_s_r_js: 境界 j の室内側放射熱伝達率, W/(m2 K), [j, 1]
        l_rs_is_n: ステップ n からステップ n+1 における室 i に放射暖冷房設備の顕熱処理量（暖房を正・冷房を負とする）, W, [i, 1]
        p_js_is: 室 i と境界 j の接続に関する係数（境界 j が室 i に接している場合は 1 とし、それ以外の場合は 0 とする。）, -, [j, i]
        q_s_sol_js_n_pls: ステップ n+1 における境界 j の透過日射吸収熱量, W/m2, [j, 1]
        theta_r_is_n_pls: ステップ n+1 における室 i の温度, degree C, [i, 1]
        theta_s_js_n_pls: ステップ n+1 における境界 j の表面温度, degree C, [j, 1]

    Returns:
        ステップ n+1 における境界 j の等価温度, degree C, [j, 1]
    Notes:
        式(2.2)

    """

    return (
        h_s_c_js * np.dot(p_js_is, theta_r_is_n_pls)
        + h_s_r_js * np.dot(f_mrt_js_js, theta_s_js_n_pls)
        + q_s_sol_js_n_pls
        + np.dot(f_flr_js_is_n, (1.0 - beta_is_n) * l_rs_is_n) / a_s_js
    ) / (h_s_c_js + h_s_r_js)


def get_theta_mrt_hum_is_n_pls(f_mrt_hum_is_js, theta_s_js_n_pls):
    """

    Args:
        f_mrt_hum_is_js: 境界 j から室 i の人体に対する形態係数, -, [i, j]
        theta_s_js_n_pls: ステップ n+1 における境界 j の表面温度, degree C, [j, 1]

    Returns:
        ステップ n+1 における室 i の人体に対する平均放射温度, degree C, [i, 1]

    Notes:
        式(2.3)

    """

    return np.dot(f_mrt_hum_is_js, theta_s_js_n_pls)


def get_theta_frt_is_n_pls(c_sh_frt_is, delta_t: float, g_sh_frt_is, q_sol_frt_is_n, theta_frt_is_n, theta_r_is_n_pls):
    """

    Args:
        c_sh_frt_is: 室 i の備品等の熱容量, J/K, [i, 1]
        delta_t: 1ステップの時間間隔, s
        g_sh_frt_is: 室 i の備品等と空気間の熱コンダクタンス, W/K, [i, 1]
        q_sol_frt_is_n: ステップ n からステップ n+1 における室 i に設置された家具による透過日射吸収熱量時間平均値, W, [i, 1]
        theta_frt_is_n: ステップ |n| における室 |i| の備品等の温度, degree C, [i, 1]
        theta_r_is_n_pls: ステップ n+1 における室 i の温度, degree C, [i, 1]

    Returns:
        ステップ n+1 における室 i　の家具の温度, degree C, [i, 1]

    Notes:
        式(2.4)

    """

    return (
        c_sh_frt_is * theta_frt_is_n + delta_t * g_sh_frt_is * theta_r_is_n_pls + q_sol_frt_is_n * delta_t
    ) / (c_sh_frt_is + delta_t * g_sh_frt_is)


def get_theta_s_js_n_pls(f_wsb_js_is_n_pls, f_wsc_js_n_pls, f_wsr_js_is, f_wsv_js_n_pls, l_rs_is_n, theta_r_is_n_pls):
    """

    Args:
        f_wsb_js_is_n_pls: ステップ n+1 における係数 f_WSB, K/W, [j, 1]
        f_wsc_js_n_pls: ステップ n+1 における係数 f_WSC, degree C, [j, 1]
        f_wsr_js_is: 係数 f_WSR, - [j, i]
        f_wsv_js_n_pls: ステップ n+1 における係数 f_WSV, degree C, [j, 1]
        l_rs_is_n: ステップ n からステップ n+1 における室 i に放射暖冷房設備の顕熱処理量（暖房を正・冷房を負とする）, W, [i, 1]
        theta_r_is_n_pls: ステップ n+1 における室 i の温度, degree C, [i, 1]

    Returns:
        ステップ n+1 における境界 j の表面温度, degree C, [j, 1]

    Notes:
        式(2.5)

    """

    return np.dot(f_wsr_js_is, theta_r_is_n_pls) + f_wsc_js_n_pls + np.dot(f_wsb_js_is_n_pls, l_rs_is_n) + f_wsv_js_n_pls


def get_theta_r_is_n_pls(f_xc_is_n_pls, f_xlr_is_is_n_pls, f_xot_is_is_n_pls, l_rs_is_n, theta_ot_is_n_pls):
    """

    Args:
        f_xc_is_n_pls: ステップ n+1 における係数 f_XC, degree C, [i, 1]
        f_xlr_is_is_n_pls: ステップ n+1 における係数 f_XLR, K/W, [i, i]
        f_xot_is_is_n_pls: ステップ n+1 における係数 f_XOT, -, [i, i]
        l_rs_is_n: ステップ n からステップ n+1 における室 i に放射暖冷房設備の顕熱処理量（暖房を正・冷房を負とする）, W, [i, 1]
        theta_ot_is_n_pls: ステップ n+1 における室 i の作用温度, ℃

    Returns:
        ステップ n+1 における室 i の室温, degree C, [i, 1]

    Notes:
        式(2.6)

    """

    return np.dot(f_xot_is_is_n_pls, theta_ot_is_n_pls) - np.dot(f_xlr_is_is_n_pls, l_rs_is_n) - f_xc_is_n_pls


def get_f_brl_ot_is_is_n(f_brl_is_is_n, f_brm_is_is_n_pls, f_xlr_is_is_n_pls):
    """

    Args:
        f_brl_is_is_n: ステップ n における係数 f_BRL, -, [i, i]
        f_brm_is_is_n_pls: ステップ n+1 における係数 f_BRM, W/K, [i, i]
        f_xlr_is_is_n_pls: ステップ n+1 における係数 f_XLR, K/W, [i, i]

    Returns:
        ステップ n における係数 f_BRL,OT, -, [i, i]

    Notes:
        式(2.8)

    """

    return f_brl_is_is_n + np.dot(f_brm_is_is_n_pls, f_xlr_is_is_n_pls)


def get_f_xlr_is_is_n_pls(f_mrt_hum_is_js, f_wsb_js_is_n_pls, f_xot_is_is_n_pls, k_r_is_n):
    """

    Args:
        f_mrt_hum_is_js: 境界 j から室 i の人体に対する形態係数, -, [i, j]
        f_wsb_js_is_n_pls: ステップ n+1 における係数 f_WSB, K/W, [j, 1]
        f_xot_is_is_n_pls: ステップ n+1 における係数 f_XOT, -, [i, i]
        k_r_is_n: ステップ n における室 i の人体表面の放射熱伝達率が総合熱伝達率に占める割合, -, [i, 1]

    Returns:
        ステップ n+1 における係数 f_XLR, K/W, [i, i]

    Notes:
        式(2.9)

    """

    return np.dot(f_xot_is_is_n_pls, k_r_is_n * np.dot(f_mrt_hum_is_js, f_wsb_js_is_n_pls))


def get_f_brl_is_is_n(a_s_js, beta_is_n, f_wsb_js_is_n_pls, h_s_c_js, p_is_js):
    """

    Args:
        a_s_js: 境界 j の面積, m2, [j, 1]
        beta_is_n: ステップ n からステップ n+1 における室 i の放射暖冷房設備の対流成分比率, -, [i, 1]
        f_wsb_js_is_n_pls: ステップ n+1 における係数 f_WSB, K/W, [j, 1]
        h_s_c_js: 境界 j の室内側対流熱伝達率, W/(m2 K), [j, 1]
        p_is_js: 室 i と境界 j の接続に関する係数（境界 j が室 i に接している場合は 1 とし、それ以外の場合は 0 とする。）, -, [i, j]

    Returns:
        ステップ n における係数 f_BRL, -, [i, i]

    Notes:
        式(2.10)

    """

    return np.dot(p_is_js, f_wsb_js_is_n_pls * h_s_c_js * a_s_js) + v_diag(beta_is_n)


def get_f_wsb_js_is_n_pls(f_flb_js_is_n_pls, f_ax_js_js):
    """

    Args:
        f_flb_js_is_n_pls: ステップ n+1 における係数 f_FLB, K/W, [j, i]
        f_ax_js_js: 係数 f_AX, -, [j, j]

    Returns:
        ステップ n+1 における係数 f_WSB, K/W, [j, i]

    Notes:
        式(2.11)

    """

    return np.dot(np.linalg.inv(f_ax_js_js), f_flb_js_is_n_pls)


def get_f_flb_js_is_n_pls(a_s_js, beta_is_n, f_flr_js_is_n, h_s_c_js, h_s_r_js, k_ei_js_js, phi_a0_js, phi_t0_js):
    """

    Args:
        a_s_js: 境界 j の面積, m2, [j, 1]
        beta_is_n: ステップ n からステップ n+1 における室 i の放射暖冷房設備の対流成分比率, -, [i, 1]
        f_flr_js_is_n: ステップ n からステップ n+1 における室 i の放射暖冷房設備の放熱量の放射成分に対する境界 j の室内側表面の吸収比率, -, [j, i]
        h_s_c_js: 境界 j の室内側対流熱伝達率, W/(m2 K), [j, 1]
        h_s_r_js: 境界 j の室内側放射熱伝達率, W/(m2 K), [j, 1]
        k_ei_js_js: 境界 j の裏面温度に境界　j* の等価温度が与える影響, -, [j*, j]
        phi_a0_js: 境界 j の吸熱応答係数の初項, m2 K/W, [j]
        phi_t0_js: 境界 |j| の貫流応答係数の初項, -, [j]

    Returns:
        ステップ n+1 における係数 f_FLB, K/W, [j, i]

    Notes:
        式(2.12)

    """

    return f_flr_js_is_n * (1.0 - beta_is_n.T) * phi_a0_js / a_s_js \
        + np.dot(k_ei_js_js, f_flr_js_is_n * (1.0 - beta_is_n.T)) * phi_t0_js / (h_s_c_js + h_s_r_js) / a_s_js


def get_beta_is_n(beta_c_is, beta_h_is, is_cooling_is_n, is_heating_is_n):
    """

    Args:
        beta_c_is: 室 i の放射冷房設備の対流成分比率, -, [i, 1]
        beta_h_is: 室 i の放射暖房設備の対流成分比率, -, [i, 1]
        is_cooling_is_n: 「ステップ n から n+1 における室 i の運転が冷房運転時の場合」かの有無, -, [i, 1]
        is_heating_is_n: 「ステップ n から n+1 における室 i の運転が暖房運転時の場合」かの有無, -, [i, 1]

    Returns:
        ステップ n からステップ n+1 における室 i の放射暖冷房設備の対流成分比率, -, [i, 1]

    Notes:
        式(2.13)
    """

    return beta_h_is * is_heating_is_n + beta_c_is * is_cooling_is_n


def get_f_flr_js_is_n(f_flr_c_js_is, f_flr_h_js_is, is_cooling_is_n, is_heating_is_n):
    """

    Args:
        f_flr_c_js_is: 室 i の放射冷房設備の放熱量の放射成分に対する境界 j の室内側表面の吸収比率, -, [j, i]
        f_flr_h_js_is: 室 i の放射暖房設備の放熱量の放射成分に対する境界 j の室内側表面の吸収比率, -, [j, i]
        is_cooling_is_n: 「ステップ n から n+1 における室 i の運転が冷房運転時の場合」かの有無, -, [i, 1]
        is_heating_is_n: 「ステップ n から n+1 における室 i の運転が暖房運転時の場合」かの有無, -, [i, 1]

    Returns:
        ステップ n からステップ n+1 における室 i の放射暖冷房設備の放熱量の放射成分に対する境界 j の室内側表面の吸収比率, -, [j, i]

    Notes:
        式(2.14)

    """

    return f_flr_h_js_is * is_heating_is_n.flatten() + f_flr_c_js_is * is_cooling_is_n.flatten()


def get_is_heating_is_n_and_is_cooling_is_n(
        operation_mode_is_n, theta_lower_target_is_n_pls, theta_r_ot_ntr_is_n_pls, theta_upper_target_is_n_pls
):
    """

    Args:
        operation_mode_is_n: ステップ n からステップ n+1 における室 i の運転モード, [i, 1]
        theta_lower_target_is_n_pls: ステップ n+1 における室 i の目標作用温度の下限値 , degree C, [i, 1]
        theta_r_ot_ntr_is_n_pls: ステップ n+1 における室 i の自然作用温度 , degree C, [i, 1]
        theta_upper_target_is_n_pls: ステップ n+1 における室 i の目標作用温度の上限値 , degree C, [i, 1]

    Returns:
        「ステップ n から n+1 における室 i の運転が暖房運転時の場合」かの有無, -, [i, 1]
        「ステップ n から n+1 における室 i の運転が冷房運転時の場合」かの有無, -, [i, 1]

    Notes:
        式(2.15a), 式(2.15b)
    """

    is_heating_is_n = (operation_mode_is_n == OperationMode.HEATING) & (
                theta_r_ot_ntr_is_n_pls < theta_lower_target_is_n_pls)
    is_cooling_is_n = (operation_mode_is_n == OperationMode.COOLING) & (
                theta_upper_target_is_n_pls < theta_r_ot_ntr_is_n_pls)

    return is_heating_is_n, is_cooling_is_n


def get_theta_r_ot_ntr_is_n_pls(f_brc_ot_is_n_pls, f_brm_ot_is_is_n_pls):
    """

    Args:
        f_brc_ot_is_n_pls: ステップ n+1 における係数 f_BRC,OT, W, [i, 1]
        f_brm_ot_is_is_n_pls: ステップ n+1 における係数 f_BRM,OT, W/K, [i, 1]

    Returns:
        ステップ n+1 における室 i の自然作用温度 , degree C, [i, 1]

    Notes:
        式(2.16)
    """

    return np.dot(np.linalg.inv(f_brm_ot_is_is_n_pls), f_brc_ot_is_n_pls)


def get_f_brc_ot_is_n_pls(f_brc_is_n_pls, f_brm_is_is_n_pls, f_xc_is_n_pls):
    """

    Args:
        f_brc_is_n_pls: ステップ n+1 における係数 f_BRC,OT, W, [i, 1]
        f_brm_is_is_n_pls: ステップ n+1 における係数 f_BRM, W/K, [i, i]
        f_xc_is_n_pls: ステップ n+1 における係数 f_XC, degree C, [i, 1]

    Returns:
        ステップ n+1 における係数 f_BRC,OT, W, [i, 1]

    Notes:
        式(2.17)
    """

    return f_brc_is_n_pls + np.dot(f_brm_is_is_n_pls, f_xc_is_n_pls)


def get_f_brm_ot_is_is_n_pls(f_brm_is_is_n_pls, f_xot_is_is_n_pls):
    """

    Args:
        f_brm_is_is_n_pls: ステップ n+1 における係数 f_BRM, W/K, [i, i]
        f_xot_is_is_n_pls: ステップ n+1 における係数 f_XOT, -, [i, i]

    Returns:
        ステップ n+1 における係数 f_BRM,OT, W/K, [i, 1]

    Notes:
        式(2.18)
    """

    return np.dot(f_brm_is_is_n_pls, f_xot_is_is_n_pls)


def get_f_xc_is_n_pls(f_mrt_hum_is_js, f_wsc_js_n_pls, f_wsv_js_n_pls, f_xot_is_is_n_pls, k_r_is_n):
    """

    Args:
        f_mrt_hum_is_js: 境界 j から室 i の人体に対する形態係数, -, [i, j]
        f_wsc_js_n_pls: ステップ n+1 における係数 f_WSC, degree C, [j, 1]
        f_wsv_js_n_pls: ステップ n+1 における係数 f_WSV, degree C, [j, 1]
        f_xot_is_is_n_pls: ステップ n+1 における係数 f_XOT, -, [i, i]
        k_r_is_n: ステップ n における室 i の人体表面の放射熱伝達率が総合熱伝達率に占める割合, -, [i, 1]

    Returns:
        ステップ n+1 における係数 f_XC, degree C, [i, 1]

    Notes:
        式(2.19)
    """

    return np.dot(f_xot_is_is_n_pls, k_r_is_n * np.dot(f_mrt_hum_is_js, (f_wsc_js_n_pls + f_wsv_js_n_pls)))


def get_f_xot_is_is_n_pls(f_mrt_hum_is_js, f_wsr_js_is, k_c_is_n, k_r_is_n):
    """

    Args:
        f_mrt_hum_is_js: 境界 j から室 i の人体に対する形態係数, -, [i, j]
        f_wsr_js_is: 係数 f_WSR, - [j, i]
        k_c_is_n: ステップ n における室 i の人体表面の対流熱伝達率が総合熱伝達率に占める割合, -, [i, 1]
        k_r_is_n: ステップ n における室 i の人体表面の放射熱伝達率が総合熱伝達率に占める割合, -, [i, 1]

    Returns:
        ステップ n+1 における係数 f_XOT, -, [i, i]

    Notes:
        式(2.20)
    """

    return np.linalg.inv(v_diag(k_c_is_n) + k_r_is_n * np.dot(f_mrt_hum_is_js, f_wsr_js_is))


def get_k_c_is_n(h_hum_c_is_n, h_hum_r_is_n):
    """

    Args:
        h_hum_c_is_n:
        h_hum_r_is_n:

    Returns:
        ステップ n における室 i の人体表面の対流熱伝達率が総合熱伝達率に占める割合, -, [i, 1]

    Notes:
        式(2.21)
    """

    return h_hum_c_is_n / (h_hum_c_is_n + h_hum_r_is_n)


def get_k_r_is_n(h_hum_c_is_n, h_hum_r_is_n):
    """

    Args:
        h_hum_c_is_n:
        h_hum_r_is_n:

    Returns:
        ステップ n における室 i の人体表面の放射熱伝達率が総合熱伝達率に占める割合, -, [i, 1]

    Notes:
        式(2.22)
    """

    return h_hum_r_is_n / (h_hum_c_is_n + h_hum_r_is_n)


def get_f_brm_is_is_n_pls(
        a_s_js, c_air, c_rm_is, c_sh_frt_is, delta_t, f_wsr_js_is, g_sh_frt_is, h_s_c_js, p_is_js,
        p_js_is, rho_air, v_vent_int_is_is, v_vent_out_is_n
):
    """

    Args:
        a_s_js: 境界 j の面積, m2, [j, 1]
        c_air:
        c_rm_is:
        c_sh_frt_is: 室 i の備品等の熱容量, J/K, [i, 1]
        delta_t: 1ステップの時間間隔, s
        f_wsr_js_is: 係数 f_WSR, - [j, i]
        g_sh_frt_is: 室 i の備品等と空気間の熱コンダクタンス, W/K, [i, 1]
        h_s_c_js: 境界 j の室内側対流熱伝達率, W/(m2 K), [j, 1]
        p_is_js: 室 i と境界 j の接続に関する係数（境界 j が室 i に接している場合は 1 とし、それ以外の場合は 0 とする。）, -, [i, j]
        p_js_is: 室 i と境界 j の接続に関する係数（境界 j が室 i に接している場合は 1 とし、それ以外の場合は 0 とする。）, -, [j, i]
        rho_air:
        v_vent_int_is_is:
        v_vent_out_is_n:

    Returns:
        ステップ n+1 における係数 f_BRM, W/K, [i, i]

    Notes:
        式(2.23)
    """

    return v_diag(c_rm_is / delta_t) \
        + np.dot(p_is_js, (p_js_is - f_wsr_js_is) * a_s_js * h_s_c_js) \
        + v_diag(c_sh_frt_is * g_sh_frt_is / (c_sh_frt_is + g_sh_frt_is * delta_t)) \
        + c_air * rho_air * (v_diag(v_vent_out_is_n) - v_vent_int_is_is)


def get_f_brc_is_n_pls(
        a_s_js, c_air, c_rm_is, c_sh_frt_is, delta_t, f_wsc_js_n_pls, f_wsv_js_n_pls, g_sh_frt_is,
        h_s_c_js, p_is_js, q_gen_is_n, q_hum_is_n, q_sol_frt_is_n, rho_air, theta_frt_is_n,
        theta_o_n_pls, theta_r_is_n, v_vent_out_is_n
):
    """

    Args:
        a_s_js: 境界 j の面積, m2, [j, 1]
        c_air:
        c_rm_is:
        c_sh_frt_is: 室 i の備品等の熱容量, J/K, [i, 1]
        delta_t: 1ステップの時間間隔, s
        f_wsc_js_n_pls: ステップ n+1 における係数 f_WSC, degree C, [j, 1]
        f_wsv_js_n_pls: ステップ n+1 における係数 f_WSV, degree C, [j, 1]
        g_sh_frt_is: 室 i の備品等と空気間の熱コンダクタンス, W/K, [i, 1]
        h_s_c_js: 境界 j の室内側対流熱伝達率, W/(m2 K), [j, 1]
        p_is_js: 室 i と境界 j の接続に関する係数（境界 j が室 i に接している場合は 1 とし、それ以外の場合は 0 とする。）, -, [i, j]
        q_gen_is_n:
        q_hum_is_n:
        q_sol_frt_is_n: ステップ n からステップ n+1 における室 i に設置された家具による透過日射吸収熱量時間平均値, W, [i, 1]
        rho_air:
        theta_frt_is_n: ステップ |n| における室 |i| の備品等の温度, degree C, [i, 1]
        theta_o_n_pls:
        theta_r_is_n:
        v_vent_out_is_n:

    Returns:
        ステップ n+1 における係数 f_BRC,OT, W, [i, 1]

    Notes:
        式(2.24)
    """

    return c_rm_is / delta_t * theta_r_is_n \
        + np.dot(p_is_js, h_s_c_js * a_s_js * (f_wsc_js_n_pls + f_wsv_js_n_pls)) \
        + c_air * rho_air * v_vent_out_is_n * theta_o_n_pls \
        + q_gen_is_n + q_hum_is_n \
        + g_sh_frt_is * (c_sh_frt_is * theta_frt_is_n + q_sol_frt_is_n * delta_t) / (c_sh_frt_is + delta_t * g_sh_frt_is)


def get_v_vent_out_is_n(v_leak_is_n, v_vent_mec_is_n, v_vent_ntr_is_n):
    """

    Args:
        v_leak_is_n:
        v_vent_mec_is_n:
        v_vent_ntr_is_n:

    Returns:
        ステップ n からステップ n+1 における室 i の換気・隙間風・自然風の利用による外気の流入量, m3/s, [i, 1]

    Notes:
        式(2.25)
    """

    return v_leak_is_n + v_vent_mec_is_n + v_vent_ntr_is_n


def get_v_vent_ntr_is_n(operation_mode_is_n, v_vent_ntr_set_is):
    """

    Args:
        operation_mode_is_n:
        v_vent_ntr_set_is:

    Returns:
        ステップ n からステップ n+1 における室 i の自然風利用による換気量, m3/s, [i, 1]

    Notes:
        式(2.26)
    """

    return np.where(operation_mode_is_n == OperationMode.STOP_OPEN, v_vent_ntr_set_is, 0.0)


def get_f_wsv_js_n_pls(f_cvl_js_n_pls, f_ax_js_js):
    """

    Args:
        f_cvl_js_n_pls:
        f_ax_js_js: 係数 f_AX, -, [j, j]

    Returns:
        ステップ n+1 の係数 f_WSV, degree C, [j, 1]

    Notes:
        式(2.27)
    """

    return np.dot(np.linalg.inv(f_ax_js_js), f_cvl_js_n_pls)


def get_f_cvl_js_n_pls(theta_dsh_s_a_js_ms_n_pls, theta_dsh_s_t_js_ms_n_pls):
    """

    Args:
        theta_dsh_s_a_js_ms_n_pls:
        theta_dsh_s_t_js_ms_n_pls:

    Returns:
        ステップ n+1 の境界 j における係数f_CVL, degree C, [j, 1]

    Notes:
        式(2.28)
    """
    return np.sum(theta_dsh_s_t_js_ms_n_pls + theta_dsh_s_a_js_ms_n_pls, axis=1, keepdims=True)


def get_theta_dsh_s_a_js_ms_n_pls(phi_a1_js_ms, q_srf_js_n, r_js_ms, theta_dsh_srf_a_js_ms_n):
    """

    Args:
        phi_a1_js_ms:
        q_srf_js_n:
        r_js_ms:
        theta_dsh_srf_a_js_ms_n:

    Returns:
        ステップ n+1 の境界 j における項別公比法の指数項 m の吸熱応答の項別成分, degree C, [j, m]

    Notes:
        式(2.29)
    """

    return phi_a1_js_ms * q_srf_js_n + r_js_ms * theta_dsh_srf_a_js_ms_n


def get_theta_dsh_s_t_js_ms_n_pls(phi_t1_js_ms, r_js_ms, theta_dsh_srf_t_js_ms_n, theta_rear_js_n):
    """

    Args:
        phi_t1_js_ms:
        r_js_ms:
        theta_dsh_srf_t_js_ms_n:
        theta_rear_js_n:

    Returns:
        ステップ n+1 の境界 j における項別公比法の指数項 m の貫流応答の項別成分, degree C, [j, m] (m=12)

    Notes:
        式(2.30)
    """

    return phi_t1_js_ms * theta_rear_js_n + r_js_ms * theta_dsh_srf_t_js_ms_n


def get_q_hum_is_n(n_hum_is_n, q_hum_psn_is_n):
    """

    Args:
        n_hum_is_n:
        q_hum_psn_is_n:

    Returns:
        ステップ n からステップ n+1 における室 i の人体発熱, W, [i, 1]

    Notes:
        式(2.31)
    """

    return q_hum_psn_is_n * n_hum_is_n


def get_theta_rear_js_n(k_ei_js_js, theta_dstrb_js_n, theta_ei_js_n):
    """

    Args:
        k_ei_js_js: 境界 j の裏面温度に境界　j* の等価温度が与える影響, -, [j*, j]
        theta_dstrb_js_n:
        theta_ei_js_n:

    Returns:
        ステップnの境界jにおける裏面温度, degree C, [j, 1]

    Notes:
        式(2.32)
    """

    return np.dot(k_ei_js_js, theta_ei_js_n) + theta_dstrb_js_n





