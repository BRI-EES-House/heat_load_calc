import numpy as np
from typing import List

import s4_1_sensible_heat as s41
import s4_2_latent_heat as s42

import a1_calculation_surface_temperature as a1
import apdx3_human_body as a3
import a9_rear_surface_equivalent_temperature as a9
import a13_Win_ACselect as a13
import a16_blowing_condition_rac as a16
import a18_initial_value_constants as a18
import a35_PMV as a35
from a39_global_parameters import OperationMode
from s3_space_loader import Space, Spaces, Conditions

import Psychrometrics as psy
from a39_global_parameters import BoundaryType
from a33_results_exporting import Logger2

def get_start_indices(spaces):
    number_of_bdry_is = np.array([s.number_of_boundary for s in spaces])
    start_indices = []
    indices = 0
    for n_bdry in number_of_bdry_is:
        indices = indices + n_bdry
        start_indices.append(indices)
    start_indices.pop(-1)
    return start_indices


# 地盤の計算
def run_tick_groundonly(To_n: float, Tave: float, c_n: Conditions, ss: Spaces):

    theta_dsh_srf_a_jstrs_n_ms = c_n.theta_dsh_srf_a_jstrs_n_ms
    q_srf_jstrs_n = c_n.q_srf_jstrs_n
    gs = ss.boundary_type_jstrs == BoundaryType.Ground

    h_r_bnd_jstrs = ss.h_r_bnd_jstrs
    h_c_bnd_jstrs = ss.h_c_bnd_jstrs

    h_i_bnd_jstrs = h_r_bnd_jstrs + h_c_bnd_jstrs

    theta_srf_dsh_a_is_jstrs_npls_ms = a1.get_theta_srf_dsh_a_i_jstrs_npls_ms(
        q_srf_jstrs_n=q_srf_jstrs_n[gs],
        phi_a_1_bnd_i_jstrs_ms=ss.phi_a_1_bnd_jstrs_ms[gs, :],
        r_bnd_i_jstrs_ms=ss.r_bnd_jstrs_ms[gs, :],
        theta_dsh_srf_a_jstrs_n_ms=theta_dsh_srf_a_jstrs_n_ms[gs, :])

    theta_dsh_srf_a_jstrs_n_ms[gs, :] = theta_srf_dsh_a_is_jstrs_npls_ms

    Ts_is_k_n = (ss.phi_a_0_bnd_jstrs[gs] * h_i_bnd_jstrs[gs] * To_n
                 + np.sum(theta_srf_dsh_a_is_jstrs_npls_ms, axis=1) + Tave) \
               / (1.0 + ss.phi_a_0_bnd_jstrs[gs] * h_i_bnd_jstrs[gs])

    q_srf_jstrs_n[gs] = h_i_bnd_jstrs[gs] * (To_n - Ts_is_k_n)

    return Conditions(
        operation_mode_is_n=c_n.operation_mode_is_n,
        theta_r_is_n=c_n.theta_r_is_n,
        theta_mrt_is_n=c_n.theta_mrt_is_n,
        x_r_is_n=c_n.x_r_is_n,
        theta_dsh_srf_a_jstrs_n_ms=theta_dsh_srf_a_jstrs_n_ms,
        theta_dsh_srf_t_jstrs_n_ms=c_n.theta_dsh_srf_t_jstrs_n_ms,
        q_srf_jstrs_n=q_srf_jstrs_n,
        h_hum_c_is_n=c_n.h_hum_c_is_n,
        h_hum_r_is_n=c_n.h_hum_r_is_n,
        theta_frnt_is_n=c_n.theta_frnt_is_n,
        x_frnt_is_n=c_n.x_frnt_is_n
    )


# 室温、熱負荷の計算
def run_tick(spaces: List[Space], theta_o_n: float, xo_n: float, n: int, start_indices: List[int], ss: Spaces, c_n: Conditions, logger2: Logger2):

    # ステップn+1の室iにおける水蒸気圧, Pa
    p_v_r_is_n = psy.get_p_v_r(x_r_is_n=c_n.x_r_is_n)

    # ステップnの室iにおける人体周りの総合熱伝達率, W/m2K, [i]
    h_hum_is_n = a35.get_h_hum_is_n(
        h_hum_r_is_n=c_n.h_hum_r_is_n,
        h_hum_c_is_n=c_n.h_hum_c_is_n
    )

    # ステップnの室iにおける作用温度, degree C, [i]
    theta_ot_is_n = a35.get_theta_ot_is_n(
        h_hum_c_is_n=c_n.h_hum_c_is_n,
        h_hum_r_is_n=c_n.h_hum_r_is_n,
        h_hum_is_n=h_hum_is_n,
        theta_r_is_n=c_n.theta_r_is_n,
        theta_mrt_is_n=c_n.theta_mrt_is_n
    )

    # ステップnの室iにおける厚着・中間着・薄着をした場合のそれぞれのclo値, [i]
    clo_heavy_is_n = np.full(ss.total_number_of_spaces, a35.get_clo_heavy())
    clo_middle_is_n = np.full(ss.total_number_of_spaces, a35.get_clo_middle())
    clo_light_is_n = np.full(ss.total_number_of_spaces, a35.get_clo_light())

    # ステップnの室iにおける厚着・中間着・薄着をした場合のそれぞれの着衣温度, degree C, [i]
    theta_cl_heavy_is_n = a35.get_theta_cl_is_n(
        clo_is_n=clo_heavy_is_n,
        theta_ot_is_n=theta_ot_is_n,
        h_hum_is_n=h_hum_is_n
    )
    theta_cl_middle_is_n = a35.get_theta_cl_is_n(
        clo_is_n=clo_middle_is_n,
        theta_ot_is_n=theta_ot_is_n,
        h_hum_is_n=h_hum_is_n
    )
    theta_cl_light_is_n = a35.get_theta_cl_is_n(
        clo_is_n=clo_light_is_n,
        theta_ot_is_n=theta_ot_is_n,
        h_hum_is_n=h_hum_is_n
    )

    # ステップnの室iにおける厚着・中間着・薄着をした場合のそれぞれのPMV, [i]
    pmv_heavy_is_n = a35.get_pmv_is_n(
        theta_r_is_n=c_n.theta_r_is_n,
        theta_cl_is_n=theta_cl_heavy_is_n,
        clo_is_n=clo_heavy_is_n,
        p_a_is_n=p_v_r_is_n,
        h_hum_is_n=h_hum_is_n,
        theta_ot_is_n=theta_ot_is_n
    )
    pmv_middle_is_n = a35.get_pmv_is_n(
        theta_r_is_n=c_n.theta_r_is_n,
        theta_cl_is_n=theta_cl_middle_is_n,
        clo_is_n=clo_middle_is_n,
        p_a_is_n=p_v_r_is_n,
        h_hum_is_n=h_hum_is_n,
        theta_ot_is_n=theta_ot_is_n
    )
    pmv_light_is_n = a35.get_pmv_is_n(
        theta_r_is_n=c_n.theta_r_is_n,
        theta_cl_is_n=theta_cl_light_is_n,
        clo_is_n=clo_light_is_n,
        p_a_is_n=p_v_r_is_n,
        h_hum_is_n=h_hum_is_n,
        theta_ot_is_n=theta_ot_is_n
    )

    # ステップnの室iにおける運転モード, [i]
    operation_mode_is_n = a13.get_operation_mode_is_n(
        ac_demand_is_n=ss.ac_demand_is_n[:, n],
        operation_mode_is_n_mns=c_n.operation_mode_is_n,
        pmv_heavy_is_n=pmv_heavy_is_n,
        pmv_middle_is_n=pmv_middle_is_n,
        pmv_light_is_n=pmv_light_is_n
    )

    # ステップnの室iにおけるClo値, [i]
    clo_is_n = a13.get_clo_is_n(
        operation_mode_is_n=operation_mode_is_n,
        clo_heavy_is_n=clo_heavy_is_n,
        clo_middle_is_n=clo_middle_is_n,
        clo_light_is_n=clo_light_is_n
    )

    # ステップnの室iにおける着衣表面温度, degree C, [i]
    theta_cl_is_n = a13.get_theta_cl_is_n(
        operation_mode_is_n=operation_mode_is_n,
        theta_cl_heavy_is_n=theta_cl_heavy_is_n,
        theta_cl_middle_is_n=theta_cl_middle_is_n,
        theta_cl_light_is_n=theta_cl_light_is_n
    )

    # ステップnの室iにおける目標作用温度, degree C, [i]
    OTsets = a13.get_theta_ot_target_is_n(
        p_a_is_n=p_v_r_is_n,
        h_hum_is_n=h_hum_is_n,
        operation_mode_is_n=operation_mode_is_n,
        clo_is_n=clo_is_n,
        theta_cl_is_n=theta_cl_is_n
    )

    # ステップnの室iの集約された境界j*における裏面温度, degree C, [j*]
    theta_rear_is_jstrs_n = a9.get_theta_rear_i_jstrs_n(
        theta_r_is_n=c_n.theta_r_is_n,
        m=ss.m_is,
        theta_dstrb_i_jstrs_n=ss.theta_dstrb_jstrs_ns[:, n]
    )

    # ステップnの室iにおける人体発熱, W, [i]
    q_hum_is_n = a3.get_q_hum_i_n(theta_r_is_n=c_n.theta_r_is_n, n_hum_i_n=ss.n_hum_is_n[:, n])

    # ステップnの室iにおける人体発湿, kg/s, [i]
    x_hum_is_n = a3.get_x_hum_i_n(theta_r_is_n=c_n.theta_r_is_n, n_hum_i_n=ss.n_hum_is_n[:, n])

    # ステップnの室iにおける内部発熱, W
    q_gen_is_n = ss.q_gen_is_ns[:, n] + q_hum_is_n

    # ステップnの室iにおける内部発湿, kg/s
    x_gen_is_n = ss.x_gen_is_ns[:, n] + x_hum_is_n

    # TODO: すきま風量未実装につき、とりあえず０とする
    # すきま風量を決めるにあたってどういった変数が必要なのかを決めること。
    # TODO: 単位は m3/s とすること。
    v_reak_is_n = np.full(len(spaces), 0.0)

    # ステップn+1の室iの統合された境界j*における項別公比法の項mの吸熱応答に関する表面温度, degree C, [jstrs, 12]
    theta_srf_dsh_a_is_jstrs_npls_ms = a1.get_theta_srf_dsh_a_i_jstrs_npls_ms(
        q_srf_jstrs_n=c_n.q_srf_jstrs_n,
        phi_a_1_bnd_i_jstrs_ms=ss.phi_a_1_bnd_jstrs_ms,
        r_bnd_i_jstrs_ms=ss.r_bnd_jstrs_ms,
        theta_dsh_srf_a_jstrs_n_ms=c_n.theta_dsh_srf_a_jstrs_n_ms
    )

    # ステップn+1の室iの統合された境界j*における項別公比法の項mの貫流応答に関する表面温度, degree C, [jstrs, 12]
    theta_srf_dsh_t_is_jstrs_npls_ms = a1.get_theta_srf_dsh_t_i_jstrs_npls_ms(
        theta_rear_i_jstrs_n=theta_rear_is_jstrs_n,
        phi_t_1_bnd_i_jstrs_ms=ss.phi_t_1_bnd_jstrs_ms,
        r_bnd_i_jstrs_ms=ss.r_bnd_jstrs_ms,
        theta_dsh_srft_jstrs_n_m=c_n.theta_dsh_srf_t_jstrs_n_ms
    )

    # ステップn+1の室iの統合された境界j*における係数CVL, degree C, [j*]
    cvl_is_jstrs_npls = a1.get_cvl_i_jstrs_npls(
        theta_srf_dsh_t_i_jstrs_npls_ms=theta_srf_dsh_t_is_jstrs_npls_ms,
        theta_srf_dsh_a_i_jstrs_npls_ms=theta_srf_dsh_a_is_jstrs_npls_ms)

    # ステップn+1の室iの統合された境界j*における係数CRX, degree C, [j*]
    crx_is_jstrs_npls = a1.get_crx_i_jstrs_npls(
        phi_a_0_bnd_i_jstrs=ss.phi_a_0_bnd_jstrs,
        q_sol_floor_i_jstrs_n=ss.q_sol_srf_jstrs_ns[:, n],
        phi_t_0_bnd_i_jstrs=ss.phi_t_0_bnd_i_jstrs,
        theta_rear_i_jstrs_n=theta_rear_is_jstrs_n
    )

    # ステップn+1の室iの断熱された境界j*における係数WSC, degree C, [j*]
    wsc_is_jstrs_npls = a1.get_wsc_i_jstrs_npls(ivs_x_i=ss.ivs_x_is, crx_i_jstrs_npls=crx_is_jstrs_npls)

    # ステップn+1の室iの断熱された境界j*における係数WSV, degree C, [j*]
    wsv_is_jstrs_npls = a1.get_wsv_i_jstrs_npls(ivs_x_i=ss.ivs_x_is, cvl_i_jstrs_npls=cvl_is_jstrs_npls)

    v_ntrl_vent_is = np.where(operation_mode_is_n == OperationMode.STOP_OPEN, ss.v_ntrl_vent_is, 0.0)

    # ステップnの室iにおける係数BRC
    brc_i_n = s41.get_brc_i_n(
        p=ss.p,
        c_room_i=ss.c_room_is,
        deta_t=900.0,
        theta_r_is_n=c_n.theta_r_is_n,
        h_c_bnd_i_jstrs=ss.h_c_bnd_jstrs,
        a_bnd_i_jstrs=ss.a_bnd_jstrs,
        wsc_i_jstrs_npls=wsc_is_jstrs_npls,
        wsv_i_jstrs_npls=wsv_is_jstrs_npls,
        v_mec_vent_i_n=ss.v_mec_vent_is_ns[:, n],
        v_reak_i_n=v_reak_is_n,
        v_ntrl_vent_i=v_ntrl_vent_is,
        theta_o_n=theta_o_n,
        q_gen_i_n=q_gen_is_n,
        c_cap_frnt_i=ss.c_cap_frnt_is,
        k_frnt_i=ss.c_fun_is,
        q_sol_frnt_i_n=ss.q_sol_frnt_is_ns[:, n],
        theta_frnt_i_n=c_n.theta_frnt_is_n,
        v_int_vent_is=ss.v_int_vent_is
    )

    brm_is_n = ss.BRMnoncv_is[:, n] + a18.get_c_air() * a18.get_rho_air() * v_ntrl_vent_is

    # OT計算用の係数補正
    BRMot_is, BRCot_is, BRLot_is, Xot_is, XLr_is, XC_is = s41.calc_OT_coeff(
        brm_is_n=brm_is_n,
        brc_i_n=brc_i_n,
        brl_is_n=ss.brl_is_ns[:, n],
        wsr_jstrs=ss.wsr_jstrs,
        wsb_jstrs=ss.wsb_jstrs,
        wsc_is_jstrs_npls=wsc_is_jstrs_npls,
        wsv_is_jstrs_npls=wsv_is_jstrs_npls,
        fot_jstrs=ss.fot_jstrs,
        kc_is=ss.kc_is,
        kr_is=ss.kr_is,
    )

    theta_ot_is_n, lcs_is_n, lrs_is_n = s41.calc_next_steps(
        ss.is_radiative_heating_is, BRCot_is, BRMot_is, BRLot_is, OTsets, ss.lrcap_is,
        operation_mode_is_n)

    # 自然室温 Tr を計算 式(14)
    theta_r_is_n_pls = s41.get_Tr_i_n(theta_ot_is_n, lrs_is_n, Xot_is, XLr_is, XC_is)

    # 家具の温度 Tfun を計算 式(15)
    theta_frnt_is_n = s41.get_Tfun_i_n(
        ss.c_cap_frnt_is,
        c_n.theta_frnt_is_n,
        ss.c_fun_is, theta_r_is_n_pls,
        ss.q_sol_frnt_is_ns[:, n]
    )

    # 表面温度の計算 式(23)
    ts_is_k_n = a1.get_surface_temperature(
        wsr_jstrs=ss.wsr_jstrs,
        wsb_jstrs=ss.wsb_jstrs,
        wsc_is_jstrs_npls=wsc_is_jstrs_npls,
        wsv_is_jstrs_npls=wsv_is_jstrs_npls,
        theta_r_is_npls=theta_r_is_n_pls,
        lrs_is_n=lrs_is_n,
        p=ss.p
    )

    # MRT_i_n、AST、平均放射温度の計算
    theta_mrt_is_n_pls = get_MRT(
        fot_jstrs=ss.fot_jstrs,
        ts_is_k_n=ts_is_k_n)

    # 室内表面熱流の計算 式(28)
    # ステップnの統合された境界j*における表面熱流（壁体吸熱を正とする）, W/m2, [j*]
    Qcs, Qrs, q_srf_is_jstrs_n = a1.calc_qi(
        h_c_bnd_jstrs=ss.h_c_bnd_jstrs,
        a_bnd_jstrs=ss.a_bnd_jstrs,
        h_r_bnd_jstrs=ss.h_r_bnd_jstrs,
        q_sol_srf_jstrs_n=ss.q_sol_srf_jstrs_ns[:, n],
        flr_is_k=ss.flr_is_k,
        ts_is_k_n=ts_is_k_n,
        theta_r_is_npls=theta_r_is_n_pls,
        f_mrt_jstrs=ss.f_mrt_jstrs,
        lrs_is_n=lrs_is_n,
        beta_is=ss.beta_is,
        p=ss.p
    )

    # 式(17)
    BRMX_pre_is = s42.get_BRMX(
        v_reak_is_n=v_reak_is_n,
        gf_is=ss.gf_is,
        cx_is=ss.cx_is,
        v_room_cap_is=ss.v_room_cap_is,
        v_mec_vent_is_n=ss.v_mec_vent_is_ns[:, n],
        v_int_vent_is=ss.v_int_vent_is
    )

    # 式(18)
    BRXC_pre_is = s42.get_BRXC(
        v_reak_is_n=v_reak_is_n,
        gf_is=ss.gf_is,
        cx_is=ss.cx_is,
        v_room_cap_is=ss.v_room_cap_is,
        x_r_is_n=c_n.x_r_is_n,
        x_frnt_is_n=c_n.x_frnt_is_n,
        x_gen_is_n=x_gen_is_n,
        xo=xo_n,
        v_mec_vent_is_n=ss.v_mec_vent_is_ns[:, n],
        v_int_vent_is=ss.v_int_vent_is
    )

    # ==== ルームエアコン吹出絶対湿度の計算 ====

    # i室のn時点におけるエアコンの（BFを考慮した）相当風量[m3/s]
    # 空調の熱交換部飽和絶対湿度の計算
    v_ac_is_n, x_e_out_is_n = ss.get_vac_xeout_is(
        lcs_is_n=lcs_is_n,
        theta_r_is_npls=theta_r_is_n_pls,
        operation_mode_is_n=operation_mode_is_n
    )

    # 空調機除湿の項 式(20)より
    RhoVac = a16.get_RhoVac(v_ac_is_n)

    # 室絶対湿度[kg/kg(DA)]の計算
    BRMX_base = BRMX_pre_is + RhoVac
    BRXC_base = BRXC_pre_is + RhoVac * x_e_out_is_n

    # 室絶対湿度の計算 式(16)
    xr_base = s42.get_xr(BRXC_base, BRMX_base)

    # 補正前の加湿量の計算 [ks/s] 式(20)
    Ghum_base = s42.get_Ghum(RhoVac, x_e_out_is_n, xr_base)

    # 除湿量が負値(加湿量が正)になった場合にはルームエアコン風量V_(ac,n)をゼロとして再度室湿度を計算する
    Ghum_is_n = np.minimum(Ghum_base, 0.0)

    # 除湿量が負値(加湿量が正)になった場合にはルームエアコン風量V_(ac,n)をゼロとして再度室湿度を計算する
    x_r_is_n_pls = np.where(Ghum_base > 0.0, s42.get_xr(BRXC_pre_is, BRMX_pre_is), xr_base)

    # 除湿量から室加湿熱量を計算 式(21)
    Lcl_i_n = get_Lcl(Ghum_is_n)

    # 当面は放射空調の潜熱は0
    # TODO: 配列にすること
    Lrl_is_n = get_Lrl()

    # ステップn+1の室iにおける飽和水蒸気圧, Pa
#    p_vs_is_n_pls = psy.get_p_vs_is(theta_r_is_n_pls)

    # ステップn+1の室iにおける水蒸気圧, Pa
#    p_v_is_n_pls = psy.get_p_v_r(x_r_is_n=x_r_is_n_pls)

    # ステップn+1の室iにおける相対湿度, %
#    rh_i_n_pls = psy.get_h(p_v=p_v_is_n_pls, p_vs=p_vs_is_n_pls)

    # ********** 備品類の絶対湿度 xf の計算 **********

    # 備品類の絶対湿度の計算
    xf_i_n = s42.get_xf(ss.gf_is, c_n.x_frnt_is_n, ss.cx_is, x_r_is_n_pls)

    # kg/s
    Qfunl_i_n = s42.get_Qfunl(ss.cx_is, x_r_is_n_pls, xf_i_n)

    # ステップnの室iにおける着衣温度, degree C, [i]
    theta_cl_is_n_pls = a35.get_theta_cl_is_n(clo_is_n=clo_is_n, theta_ot_is_n=theta_ot_is_n, h_hum_is_n=h_hum_is_n)

    # ステップnの室iにおける人体周りの風速, m/s, [i]
    v_hum_i_n_pls = get_v_hum_is_n_pls(operation_mode_is_n, ss.is_radiative_heating_is, ss.is_radiative_cooling_is)

    # ステップnの室iにおける人体周りの対流熱伝達率, W/m2K, [i]
    h_hum_c_is_n_pls = a35.get_h_hum_c_is_n(
        theta_r_is_n=theta_r_is_n_pls,
        theta_cl_is_n=theta_cl_is_n_pls,
        v_hum_is_n=v_hum_i_n_pls
    )

    # ステップnの室iにおける人体周りの放射熱伝達率, W/m2K, [i]
    h_hum_r_is_n_pls = a35.get_h_hum_r_is_n(
        theta_cl_is_n=theta_cl_is_n_pls,
        theta_mrt_is_n=theta_mrt_is_n_pls
    )

    logger2.operation_mode[:, n] = operation_mode_is_n
    logger2.theta_r[:, n] = theta_r_is_n_pls
    logger2.x_r[:, n] = x_r_is_n_pls
    logger2.theta_mrt[:, n] = theta_mrt_is_n_pls
    logger2.theta_ot[:, n] = theta_ot_is_n
    logger2.clo[:, n] = clo_is_n
    logger2.v_hum[:, n] = v_hum_i_n_pls
    logger2.q_hum[:, n] = q_hum_is_n
    logger2.x_hum[:, n] = x_hum_is_n
    logger2.l_cs[:, n] = lcs_is_n
    logger2.l_rs[:, n] = lrs_is_n
    logger2.l_cl[:, n] = Lcl_i_n
    logger2.theta_frnt[:, n] = theta_frnt_is_n
    logger2.x_frnt[:, n] = xf_i_n
    logger2.q_l_frnt[:, n] = Qfunl_i_n
    logger2.theta_s[:, n] = ts_is_k_n
    logger2.theta_e[:, n] = None
    logger2.theta_rear[:, n] = theta_rear_is_jstrs_n
    logger2.qr[:, n] = Qrs
    logger2.qc[:, n] = Qcs

    for i, s in enumerate(spaces):

        Ts_i_k_n = np.split(ts_is_k_n, start_indices)[i]

        # 室内側等価温度の計算 式(29)
        s.logger.Tei_i_k_n[:, n] = a1.calc_Tei(
            s.h_c_bnd_i_jstrs, s.h_r_bnd_i_jstrs, s.q_sol_srf_i_jstrs_ns[:, n], s.flr_i_k,
            s.a_bnd_i_jstrs, theta_r_is_n_pls[i], s.F_mrt_i_g, Ts_i_k_n, lrs_is_n[i], s.Beta_i)

    return Conditions(
        operation_mode_is_n=operation_mode_is_n,
        theta_r_is_n=theta_r_is_n_pls,
        theta_mrt_is_n=theta_mrt_is_n_pls,
        x_r_is_n=x_r_is_n_pls,
        theta_dsh_srf_a_jstrs_n_ms=theta_srf_dsh_a_is_jstrs_npls_ms,
        theta_dsh_srf_t_jstrs_n_ms=theta_srf_dsh_t_is_jstrs_npls_ms,
        q_srf_jstrs_n=q_srf_is_jstrs_n,
        h_hum_c_is_n=h_hum_c_is_n_pls,
        h_hum_r_is_n=h_hum_r_is_n_pls,
        theta_frnt_is_n=theta_frnt_is_n,
        x_frnt_is_n=xf_i_n
    )


def get_v_hum_is_n_pls(operation_mode_is_n, is_radiative_heating_is, is_radiative_cooling_is):

    return np.vectorize(get_v_hum_i_n_pls)(operation_mode_is_n, is_radiative_heating_is, is_radiative_cooling_is)


def get_v_hum_i_n_pls(operation_mode_i_n, is_radiative_heating, is_radiative_cooling):

    if operation_mode_i_n == OperationMode.HEATING:
        if is_radiative_heating:
            return 0.0
        else:
            return 0.2
    elif operation_mode_i_n == OperationMode.COOLING:
        if is_radiative_cooling:
            return 0.0
        else:
            return 0.2
    elif operation_mode_i_n == OperationMode.STOP_CLOSE:
        return 0.0
    elif operation_mode_i_n == OperationMode.STOP_OPEN:
        return 0.1
    else:
        raise ValueError()


# MRTの計算
def get_MRT(fot_jstrs, ts_is_k_n) -> np.ndarray:

    return np.dot(fot_jstrs, ts_is_k_n.reshape(-1, 1)).flatten()


# ASTの計算
def get_AST(area, Ts, Atotal):
    return np.sum(area * Ts / Atotal)


# 当面は放射空調の潜熱は0
def get_Lrl():
    return 0.0


# 除湿量から室加湿熱量を計算 式(21)
def get_Lcl(Ghum: float):
    """除湿量から室加湿熱量を計算

    :param Ghum: i室のn時点における除湿量 [ks/s]
    :return:
    """
    conra = a18.get_conra()
    return Ghum * conra


# 式(20)のうちの一部
def get_RhoVac(Vac: float, BF: float):
    rhoa = a18.get_rho_air()
    return rhoa * Vac * (1.0 - BF)
