import numpy as np
from typing import List

import s4_1_sensible_heat as s41
import s4_2_latent_heat as s42

import a1_calculation_surface_temperature as a1
import a16_blowing_condition_rac as a16
import a18_initial_value_constants as a18
import x_35_occupants as x_35
from a39_global_parameters import OperationMode
from s3_space_loader import PreCalcParameters, Conditions
from a33_results_exporting import Logger


# 地盤の計算
def run_tick_groundonly(To_n: float, Tave: float, c_n: Conditions, ss: PreCalcParameters):

    theta_dsh_srf_a_jstrs_n_ms = c_n.theta_dsh_srf_a_js_ms_n
    q_srf_jstrs_n = c_n.q_srf_js_n.flatten()
    gs = ss.is_ground_js

    h_r_bnd_jstrs = ss.h_r_js.flatten()
    h_c_bnd_jstrs = ss.h_c_js.flatten()

    h_i_bnd_jstrs = h_r_bnd_jstrs + h_c_bnd_jstrs

    theta_srf_dsh_a_is_jstrs_npls_ms = a1.get_theta_srf_dsh_a_i_jstrs_npls_ms(
        q_srf_jstrs_n=q_srf_jstrs_n[gs],
        phi_a_1_bnd_jstrs_ms=ss.phi_a1_js_ms[gs, :],
        r_bnd_i_jstrs_ms=ss.r_js_ms[gs, :],
        theta_dsh_srf_a_jstrs_n_ms=theta_dsh_srf_a_jstrs_n_ms[gs, :])

    theta_dsh_srf_a_jstrs_n_ms[gs, :] = theta_srf_dsh_a_is_jstrs_npls_ms

    Ts_is_k_n = (ss.phi_a0_js.flatten()[gs] * h_i_bnd_jstrs[gs] * To_n
                 + np.sum(theta_srf_dsh_a_is_jstrs_npls_ms, axis=1) + Tave) \
               / (1.0 + ss.phi_a0_js.flatten()[gs] * h_i_bnd_jstrs[gs])

    q_srf_jstrs_n[gs] = h_i_bnd_jstrs[gs] * (To_n - Ts_is_k_n)

    return Conditions(
        operation_mode_is_n=c_n.operation_mode_is_n,
        theta_r_is_n=c_n.theta_r_is_n,
        theta_mrt_hum_is_n=c_n.theta_mrt_hum_is_n,
        x_r_is_n=c_n.x_r_is_n,
        theta_dsh_srf_a_js_ms_n=theta_dsh_srf_a_jstrs_n_ms,
        theta_dsh_srf_t_js_ms_n=c_n.theta_dsh_srf_t_js_ms_n,
        q_srf_js_n=q_srf_jstrs_n.reshape(-1, 1),
#        h_hum_c_is_n=c_n.h_hum_c_is_n,
#        h_hum_r_is_n=c_n.h_hum_r_is_n,
        theta_frnt_is_n=c_n.theta_frnt_is_n,
        x_frnt_is_n=c_n.x_frnt_is_n,
        theta_cl_is_n=c_n.theta_cl_is_n,
        theta_ei_js_n=c_n.theta_ei_js_n
    )


# 室温、熱負荷の計算
def run_tick(theta_o_n: float, xo_n: float, n: int, ss: PreCalcParameters, c_n: Conditions, logger: Logger):
    """

    Args:
        theta_o_n:
        xo_n:
        n:
        ss:
        c_n: 前の時刻からの状態量
            operation_mode_is_n: ステップnにおける室iの運転状態, [i]
                列挙体 OperationMode で表される。
                    COOLING ： 冷房
                    HEATING : 暖房
                    STOP_OPEN : 暖房・冷房停止で窓「開」
                    STOP_CLOSE : 暖房・冷房停止で窓「閉」
            theta_r_is_n: ステップnにおける室iの空気温度, degree C, [i]
            theta_mrt_is_n: ステップnにおける室iの在室者の平均放射温度, degree C, [i]
            x_r_is_n: ステップnにおける室iの絶対湿度, kg/kgDA, [i]
            theta_dsh_srf_a_jstrs_n_ms: ステップnの統合された境界j*における指数項mの吸熱応答の項別成分, degree C, [j*, 12]
            theta_dsh_srf_t_jstrs_n_ms: ステップnの統合された境界j*における指数項mの貫流応答の項別成分, degree C, [j*, 12]
            q_srf_jstrs_n: ステップnの統合された境界j*における表面熱流（壁体吸熱を正とする）, W/m2, [j*]
            theta_frnt_is_n: ステップnの室iにおける家具の温度, degree C, [i]
            x_frnt_is_n: ステップnの室iにおける家具の絶対湿度, kg/kgDA, [i]
            theta_cl_is_n: ステップnにおける室iの在室者の着衣温度, degree C, [i]
                本来であれば着衣温度と人体周りの対流・放射熱伝達率を未知数とした熱収支式を収束計算等を用いて時々刻々求めるのが望ましい。
                今回、収束計算を回避するために前時刻の着衣温度を用いることにした。
        logger:

    Returns:

    """

    ##### 時刻 n, n+1 におけるデータの切り出し #####
    # [i, n] のベクトルを[:, n] 又は[:, n+1] で切り出す。
    # numpy の仕様として、切り出した時にある次元の配列数が1の場合に、次元を1つ減らすため、
    # [:, n] 又は [:, n+1] で切り出した場合、[i] 又は [j] の1次元配列になる。
    # ベクトル計算に都合の良いように、[i, 1] 又は [j, 1] の列ベクトルになおすために、 np.reshape(-1, 1)の操作をしている。

    # ステップnにおける室iの空調需要, [i, 8760*4]
    ac_demand_is_n = ss.ac_demand_is_ns[:, n].reshape(-1, 1)

    # ステップnの集約境界j*における外気側等価温度の外乱成分, degree C, [j*, 8760*4]
    theta_dstrb_js_n = ss.theta_dstrb_js_ns[:, n].reshape(-1, 1)

    # ステップnの室iにおける在室人数, [i, 8760*4]
    n_hum_is_n = ss.n_hum_is_ns[:, n].reshape(-1, 1)

    # ステップnの室iにおける人体発熱を除く内部発熱, W, [i, 8760*4]
    q_gen_is_n = ss.q_gen_is_ns[:, n].reshape(-1, 1)

    # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [i, 8760*4]
    x_gen_is_n = ss.x_gen_is_ns[:, n].reshape(-1, 1)

    # ステップn+1の境界jにおける係数 WSC, degree C, [j, 1]
    # TODO: WSC n+1 にもかかわらず、n の値が代入されている。n+1 を代入すべきではないのか？その場合、計算の最終ステップの計算はどうする？
    wsc_js_npls = ss.wsc_js_ns[:, n].reshape(-1, 1)

    # ステップnの室iにおける機械換気量（全般換気量+局所換気量）, m3/s, [i, 8760*4]
    v_mec_vent_is_n = ss.v_mec_vent_is_ns[:, n].reshape(-1, 1)

    # 家具の吸収日射量, W, [i, 8760*4]
    q_sol_frnt_is_n = ss.q_sol_frnt_is_ns[:, n].reshape(-1, 1)

    # ステップnにおける室iの状況（在室者周りの総合熱伝達率・運転状態・Clo値・目標とする作用温度）を取得する
    #     ステップnの室iにおける人体周りの総合熱伝達率, W / m2K, [i, 1]
    #     ステップnにおける室iの在室者周りの対流熱伝達率, W / m2K, [i, 1]
    #     ステップnにおける室iの在室者周りの放射熱伝達率, W / m2K, [i, 1]
    #     ステップnの室iにおける運転モード, [i, 1]
    #     ステップnの室iにおけるClo値, [i, 1]
    #     ステップnの室iにおける目標作用温度, degree C, [i, 1]
    h_hum_is_n, h_hum_c_is_n, h_hum_r_is_n, operation_mode_is_n, clo_is_n, theta_ot_target_is_n = x_35.calc_operation(
        x_r_is_n=c_n.x_r_is_n,
        operation_mode_is_n_mns=c_n.operation_mode_is_n,
        is_radiative_heating_is=ss.is_radiative_heating_is,
        is_radiative_cooling_is=ss.is_radiative_cooling_is,
        theta_r_is_n=c_n.theta_r_is_n,
        theta_cl_is_n=c_n.theta_cl_is_n,
        theta_mrt_is_n=c_n.theta_mrt_hum_is_n,
        ac_demand_is_n=ac_demand_is_n,
    )

    # ステップnの境界jにおける裏面温度, degree C, [j, 1]
    theta_rear_js_n = np.dot(ss.k_ei_js_js, c_n.theta_ei_js_n) + theta_dstrb_js_n

    # ステップnの室iにおける1人あたりの人体発熱, W, [i, 1]
    q_hum_psn_is_n = x_35.get_q_hum_psn_is_n(theta_r_is_n=c_n.theta_r_is_n)

    # ステップnの室iにおける人体発熱, W, [i, 1]
    q_hum_is_n = q_hum_psn_is_n * n_hum_is_n

    # ステップnの室iにおける1人あたりの人体発湿, kg/s, [i, 1]
    x_hum_psn_is_n = x_35.get_x_hum_psn_is_n(theta_r_is_n=c_n.theta_r_is_n)

    # ステップnの室iにおける人体発湿, kg/s, [i, 1]
    x_hum_is_n = x_hum_psn_is_n * n_hum_is_n

    # TODO: すきま風量未実装につき、とりあえず０とする
    # すきま風量を決めるにあたってどういった変数が必要なのかを決めること。
    # TODO: 単位は m3/s とすること。
    # ステップnの室iにおけるすきま風量, m3/s, [i, 1]
    v_reak_is_n = np.full((ss.number_of_spaces, 1), 0.0)

    # ステップn+1の境界jにおける項別公比法の指数項mの吸熱応答の項別成分, degree C, [j, m] (m=12)
    theta_dsh_srf_a_js_ms_npls = ss.phi_a1_js_ms * c_n.q_srf_js_n + ss.r_js_ms * c_n.theta_dsh_srf_a_js_ms_n

    # ステップn+1の境界jにおける項別公比法の指数項mの貫流応答の項別成分, degree C, [j, m] (m=12)
    theta_dsh_srf_t_js_ms_npls = theta_rear_js_n * ss.phi_t1_js_ms + ss.r_js_ms * c_n.theta_dsh_srf_t_js_ms_n

    # ステップn+1の境界jにおける係数CVL, degree C, [j, 1]
    cvl_js_npls = np.sum(theta_dsh_srf_t_js_ms_npls + theta_dsh_srf_a_js_ms_npls, axis=1, keepdims=True)

    # ステップn+1の境界jにおける係数WSV, degree C, [j, 1]
    wsv_js_npls = np.dot(ss.ivs_ax_js_js, cvl_js_npls)

    # 室iの自然風利用による換気量, m3/s, [i, 1]
    # 自然風を利用していない場合は、0.0 m3/s になる。
    v_ntrl_vent_is = np.where(operation_mode_is_n == OperationMode.STOP_OPEN, ss.v_ntrl_vent_is, 0.0)

    # ステップnにおける室iの外からの換気量, m3/s, [i, 1]
    # 機械換気量・すきま風量・自然風利用時の換気量との合計である。
    v_out_vent_is_n = v_reak_is_n + v_mec_vent_is_n + v_ntrl_vent_is

    # ステップnの室iにおける係数 BRC, W, [i, 1]
    brc_is_n = ss.c_room_is / 900.0 * c_n.theta_r_is_n\
        + np.dot(ss.p_is_js, ss.h_c_js * ss.a_srf_js * (wsc_js_npls + wsv_js_npls))\
        + a18.get_c_air() * a18.get_rho_air() * v_out_vent_is_n * theta_o_n\
        + q_gen_is_n + q_hum_is_n\
        + ss.c_frnt_is * (ss.c_cap_frnt_is * c_n.theta_frnt_is_n + ss.q_sol_frnt_is_ns[:, n].reshape(-1, 1) * 900.0) / (ss.c_cap_frnt_is + 900.0 * ss.c_frnt_is)

    # ステップnにおける係数 BRM, W/K, [i, i]
    brm_is_is_n = ss.brm_non_vent_is_is\
        + a18.get_c_air() * a18.get_rho_air() * (np.diag(v_out_vent_is_n.flatten()) + ss.v_int_vent_is_is)

    # ステップnにおける室iの在室者表面における対流熱伝達率の総合熱伝達率に対する比, [i, 1]
    kc_is_n = h_hum_c_is_n / h_hum_is_n

    # ステップnにおける室iの在室者表面における放射熱伝達率の総合熱伝達率に対する比, [i, 1]
    kr_is_n = h_hum_r_is_n / h_hum_is_n

    def v_diag(v_matrix):
        arr = v_matrix.flatten()
        return np.diag(arr)

    # ステップnにおける室iの係数 XOT, [i, i]
    xot_is_is_n = np.linalg.inv(v_diag(kc_is_n) + kr_is_n * np.dot(ss.f_mrt_hum_is_js, ss.wsr_js_is))

    # ステップn+1における室iの係数 XLR, [i, i]
    xlr_is_is_npls = np.dot(xot_is_is_n, kr_is_n * np.dot(ss.f_mrt_hum_is_js, ss.wsb_js_is))

    # ステップn+1における室iの係数 XC, [i, 1]
    xc_is_npls = kr_is_n * np.dot(xot_is_is_n, np.dot(ss.f_mrt_hum_is_js, (wsc_js_npls + wsv_js_npls)))

    # ステップnにおける係数 BRMOT, W/K, [i, i]
    brm_ot_is_is_n = np.dot(brm_is_is_n, xot_is_is_n)

    # ステップnにおける係数 BRLOT, [i, i]
    brl_ot_is_is_n = ss.brl_is_is + np.dot(brm_is_is_n, xlr_is_is_npls)

    # ステップnにおける係数 BRCOT, [i, 1]
    brc_ot_is_n = brc_is_n + np.dot(brm_is_is_n, xc_is_npls)

    # ステップ n+1 における室 i の作用温度, degree C, [i, 1]
    # ステップ n+1 における室 i に設置された対流暖房の放熱量, W, [i, 1]
    # ステップ n+1 における室 i に設置された放射暖房の放熱量, W, [i, 1]
    theta_ot_is_npls, lc_is_npls, lr_is_npls = s41.calc_next_temp_and_load(
        is_radiative_heating_is=ss.is_radiative_heating_is,
        brc_ot_is_n=brc_ot_is_n,
        brm_ot_is_is_n=brm_ot_is_is_n,
        brl_ot_is_is_n=brl_ot_is_is_n,
        theta_ot_target_is_n=theta_ot_target_is_n,
        lrcap_is=ss.lrcap_is,
        operation_mode_is_n=operation_mode_is_n
    )

    # ステップ n+1 における室 i の室温, degree C, [i, 1]
    theta_r_is_n_pls = np.dot(xot_is_is_n, theta_ot_is_npls) - np.dot(xlr_is_is_npls, lr_is_npls) - xc_is_npls

    # ステップ n+1 における室 i　の家具の温度, degree C, [i, 1]
    theta_frnt_is_n = (
        ss.c_cap_frnt_is * c_n.theta_frnt_is_n + 900.0 * ss.c_frnt_is * theta_r_is_n_pls + q_sol_frnt_is_n * 900.0
    ) / (ss.c_cap_frnt_is + 900.0 * ss.c_frnt_is)

    # ステップ n+1 における境界 j の表面温度, degree C, [j, 1]
    theta_s_js_n = np.dot(ss.wsr_js_is, theta_r_is_n_pls) + wsc_js_npls + np.dot(ss.wsb_js_is, lr_is_npls) + wsv_js_npls

    # ステップn+1における室iの人体に対する平均放射温度, degree C, [i, 1]
    theta_mrt_hum_is_n_pls = np.dot(ss.f_mrt_hum_is_js, theta_s_js_n)

    # 室内表面熱流の計算 式(28)
    # ステップn+1の境界jにおける等価温度, degree C, [j, 1]
    theta_ei_js_npls = (
        ss.h_c_js * np.dot(ss.p_js_is, theta_r_is_n_pls)
        + ss.h_r_js * np.dot(np.dot(ss.p_js_is, ss.f_mrt_is_js), theta_s_js_n)
        + ss.q_sol_js_ns[:, n].reshape(-1, 1)
        + np.dot(ss.flr_js_is, (1.0 - ss.beta_is) * lr_is_npls) / ss.a_srf_js
    ) / (ss.h_c_js + ss.h_r_js)

    # ステップnの境界jにおける表面熱流（壁体吸熱を正とする）, W/m2, [j, 1]
    q_srf_js_n = (theta_ei_js_npls - theta_s_js_n) * (ss.h_c_js + ss.h_r_js)

    # 式(17)
    BRMX_pre_is = s42.get_BRMX(
        v_reak_is_n=v_reak_is_n.flatten(),
        gf_is=ss.g_f_is,
        cx_is=ss.c_x_is,
        v_room_cap_is=ss.v_room_cap_is.flatten(),
        v_mec_vent_is_n=ss.v_mec_vent_is_ns[:, n],
        v_int_vent_is=ss.v_int_vent_is_is
    )

    # 式(18)
    BRXC_pre_is = s42.get_BRXC(
        v_reak_is_n=v_reak_is_n.flatten(),
        gf_is=ss.g_f_is,
        cx_is=ss.c_x_is,
        v_room_cap_is=ss.v_room_cap_is.flatten(),
        x_r_is_n=c_n.x_r_is_n.flatten(),
        x_frnt_is_n=c_n.x_frnt_is_n,
        x_gen_is_n=(x_gen_is_n + x_hum_is_n).flatten(),
        xo=xo_n,
        v_mec_vent_is_n=ss.v_mec_vent_is_ns[:, n],
        v_int_vent_is=ss.v_int_vent_is_is
    )

    # ==== ルームエアコン吹出絶対湿度の計算 ====

    # i室のn時点におけるエアコンの（BFを考慮した）相当風量[m3/s]
    # 空調の熱交換部飽和絶対湿度の計算
    v_ac_is_n, x_e_out_is_n = ss.get_vac_xeout_is(
        lcs_is_n=lc_is_npls.flatten(),
        theta_r_is_npls=theta_r_is_n_pls.flatten(),
        operation_mode_is_n=operation_mode_is_n.flatten()
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
    xf_i_n = s42.get_xf(ss.g_f_is, c_n.x_frnt_is_n, ss.c_x_is, x_r_is_n_pls)

    # kg/s
    Qfunl_i_n = s42.get_Qfunl(ss.c_x_is, x_r_is_n_pls, xf_i_n)

    # ステップnにおける室iの在室者の着衣温度, degree C, [i]
    theta_cl_is_n_pls = x_35.get_theta_cl_is_n(clo_is_n=clo_is_n.flatten(), theta_ot_is_n=theta_ot_is_npls.flatten(), h_hum_is_n=h_hum_is_n.flatten())

    logger.operation_mode[:, n] = operation_mode_is_n.flatten()
    logger.theta_r[:, n] = theta_r_is_n_pls.flatten()
    logger.x_r[:, n] = x_r_is_n_pls
    logger.theta_mrt[:, n] = theta_mrt_hum_is_n_pls.flatten()
    logger.theta_ot[:, n] = theta_ot_is_npls.flatten()
    logger.clo[:, n] = clo_is_n.flatten()
    logger.q_hum[:, n] = q_hum_is_n.flatten()
    logger.x_hum[:, n] = x_hum_is_n.flatten()
    logger.l_cs[:, n] = lc_is_npls.flatten()
    logger.l_rs[:, n] = lr_is_npls.flatten()
    logger.l_cl[:, n] = Lcl_i_n
    logger.theta_frnt[:, n] = theta_frnt_is_n.flatten()
    logger.x_frnt[:, n] = xf_i_n
    logger.q_l_frnt[:, n] = Qfunl_i_n
    logger.theta_s[:, n] = theta_s_js_n.flatten()
    logger.theta_rear[:, n] = theta_rear_js_n.flatten()
    logger.theta_ei[:, n] = theta_ei_js_npls.flatten()

    return Conditions(
        operation_mode_is_n=operation_mode_is_n,
        theta_r_is_n=theta_r_is_n_pls,
        theta_mrt_hum_is_n=theta_mrt_hum_is_n_pls,
        x_r_is_n=x_r_is_n_pls.reshape(-1, 1),
        theta_dsh_srf_a_js_ms_n=theta_dsh_srf_a_js_ms_npls,
        theta_dsh_srf_t_js_ms_n=theta_dsh_srf_t_js_ms_npls,
        q_srf_js_n=q_srf_js_n,
        theta_frnt_is_n=theta_frnt_is_n,
        x_frnt_is_n=xf_i_n,
        theta_cl_is_n=theta_cl_is_n_pls.reshape(-1, 1),
        theta_ei_js_n=theta_ei_js_npls
    )


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
