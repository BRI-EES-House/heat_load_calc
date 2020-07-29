import numpy as np

from heat_load_calc.core.operation_mode import OperationMode
from heat_load_calc.core.pre_calc_parameters import PreCalcParameters
from heat_load_calc.core.conditions import Conditions
from heat_load_calc.external.global_number import get_c_air, get_rho_air, get_l_wtr
from heat_load_calc.core.log import Logger
from heat_load_calc.core import next_condition
from heat_load_calc.core import occupants
from heat_load_calc.core import heat_exchanger
from heat_load_calc.core.matrix_method import v_diag


# 室温、熱負荷の計算
def run_tick(n: int, ss: PreCalcParameters, c_n: Conditions, logger: Logger):
    """

    Args:
        theta_o_n:
        x_o_n:
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
    #     ステップnの室iにおける目標PMV, [i, 1]
    #     ステップnの室iにおけるClo値, [i, 1]
    #     ステップnの室iにおける目標作用温度, degree C, [i, 1]
    h_hum_is_n, h_hum_c_is_n, h_hum_r_is_n, operation_mode_is_n, pmv_target_is_n, v_hum_is_n, clo_is_n, theta_ot_target_is_n = occupants.calc_operation(
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
    theta_rear_js_npls = np.dot(ss.k_ei_js_js, c_n.theta_ei_js_n) + theta_dstrb_js_n

    # ステップnの室iにおける1人あたりの人体発熱, W, [i, 1]
    q_hum_psn_is_n = occupants.get_q_hum_psn_is_n(theta_r_is_n=c_n.theta_r_is_n)

    # ステップnの室iにおける人体発熱, W, [i, 1]
    q_hum_is_n = q_hum_psn_is_n * n_hum_is_n

    # ステップnの室iにおける1人あたりの人体発湿, kg/s, [i, 1]
    x_hum_psn_is_n = occupants.get_x_hum_psn_is_n(theta_r_is_n=c_n.theta_r_is_n)

    # ステップnの室iにおける人体発湿, kg/s, [i, 1]
    x_hum_is_n = x_hum_psn_is_n * n_hum_is_n

    # TODO: すきま風量未実装につき、とりあえず０とする
    # すきま風量を決めるにあたってどういった変数が必要なのかを決めること。
    # TODO: 単位は m3/s とすること。
    # ステップnの室iにおけるすきま風量, m3/s, [i, 1]
    v_reak_is_n = np.full((ss.n_spaces, 1), 0.0)

    # ステップn+1の境界jにおける項別公比法の指数項mの吸熱応答の項別成分, degree C, [j, m] (m=12)
    theta_dsh_srf_a_js_ms_npls = ss.phi_a1_js_ms * c_n.q_srf_js_n + ss.r_js_ms * c_n.theta_dsh_srf_a_js_ms_n

    # ステップn+1の境界jにおける項別公比法の指数項mの貫流応答の項別成分, degree C, [j, m] (m=12)
    theta_dsh_srf_t_js_ms_npls = theta_rear_js_npls * ss.phi_t1_js_ms + ss.r_js_ms * c_n.theta_dsh_srf_t_js_ms_n

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
    brc_is_n = ss.c_room_is / 900.0 * c_n.theta_r_is_n \
               + np.dot(ss.p_is_js, ss.h_c_js * ss.a_srf_js * (wsc_js_npls + wsv_js_npls)) \
               + get_c_air() * get_rho_air() * v_out_vent_is_n * ss.theta_o_ns[n] \
               + q_gen_is_n + q_hum_is_n \
               + ss.c_h_frt_is * (ss.c_cap_h_frt_is * c_n.theta_frnt_is_n + ss.q_sol_frnt_is_ns[:, n].reshape(-1, 1) * 900.0) / (ss.c_cap_h_frt_is + 900.0 * ss.c_h_frt_is)

    # ステップnにおける係数 BRM, W/K, [i, i]
    brm_is_is_n = ss.brm_non_vent_is_is\
        + get_c_air() * get_rho_air() * (np.diag(v_out_vent_is_n.flatten()) + ss.v_int_vent_is_is)

    # ステップnにおける室iの在室者表面における対流熱伝達率の総合熱伝達率に対する比, [i, 1]
    kc_is_n = h_hum_c_is_n / h_hum_is_n

    # ステップnにおける室iの在室者表面における放射熱伝達率の総合熱伝達率に対する比, [i, 1]
    kr_is_n = h_hum_r_is_n / h_hum_is_n

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
    theta_ot_is_npls, l_cs_is_n, l_hs_is_n = next_condition.calc_next_temp_and_load(
        is_radiative_heating_is=ss.is_radiative_heating_is,
        brc_ot_is_n=brc_ot_is_n,
        brm_ot_is_is_n=brm_ot_is_is_n,
        brl_ot_is_is_n=brl_ot_is_is_n,
        theta_ot_target_is_n=theta_ot_target_is_n,
        lrcap_is=ss.lrcap_is,
        operation_mode_is_n=operation_mode_is_n
    )

    # ステップ n+1 における室 i の室温, degree C, [i, 1]
    theta_r_is_npls = np.dot(xot_is_is_n, theta_ot_is_npls) - np.dot(xlr_is_is_npls, l_hs_is_n) - xc_is_npls

    # ステップ n+1 における室 i　の家具の温度, degree C, [i, 1]
    theta_frt_is_npls = (
        ss.c_cap_h_frt_is * c_n.theta_frnt_is_n + 900.0 * ss.c_h_frt_is * theta_r_is_npls + q_sol_frnt_is_n * 900.0
    ) / (ss.c_cap_h_frt_is + 900.0 * ss.c_h_frt_is)

    # ステップ n+1 における境界 j の表面温度, degree C, [j, 1]
    theta_s_js_npls = np.dot(ss.wsr_js_is, theta_r_is_npls) + wsc_js_npls + np.dot(ss.wsb_js_is, l_hs_is_n) + wsv_js_npls

    # ステップn+1における室iの人体に対する平均放射温度, degree C, [i, 1]
    theta_mrt_hum_is_npls = np.dot(ss.f_mrt_hum_is_js, theta_s_js_npls)

    # 室内表面熱流の計算 式(28)
    # ステップn+1の境界jにおける等価温度, degree C, [j, 1]
    theta_ei_js_npls = (
        ss.h_c_js * np.dot(ss.p_js_is, theta_r_is_npls)
        + ss.h_r_js * np.dot(np.dot(ss.p_js_is, ss.f_mrt_is_js), theta_s_js_npls)
        + ss.q_sol_js_ns[:, n].reshape(-1, 1)
        + np.dot(ss.flr_js_is, (1.0 - ss.beta_is) * l_hs_is_n) / ss.a_srf_js
    ) / (ss.h_c_js + ss.h_r_js)

    # ステップnの境界jにおける表面熱流（壁体吸熱を正とする）, W/m2, [j, 1]
    q_srf_js_n = (theta_ei_js_npls - theta_s_js_npls) * (ss.h_c_js + ss.h_r_js)

    # ステップnの室iにおける係数 brmx_pre, [i, 1]
    brmx_non_dh_is_n_pls = get_rho_air() * (v_diag(ss.v_room_is / 900 + v_out_vent_is_n) - ss.v_int_vent_is_is)\
        + v_diag(ss.c_cap_w_frt_is * ss.c_w_frt_is / (ss.c_cap_w_frt_is + 900 * ss.c_w_frt_is))

    # ステップnの室iにおける係数 brxc_pre, [i, 1]
    brxc_non_dh_is_n_pls = get_rho_air() * (
            ss.v_room_is / 900 * c_n.x_r_is_n
            + v_out_vent_is_n * ss.x_o_ns[n]
    ) + ss.c_cap_w_frt_is * ss.c_w_frt_is / (ss.c_cap_w_frt_is + 900 * ss.c_w_frt_is) * c_n.x_frt_is_n\
        + x_gen_is_n + x_hum_is_n

    x_r_non_dh_is_n_pls = np.dot(np.linalg.inv(brmx_non_dh_is_n_pls), brxc_non_dh_is_n_pls)

    # ==== ルームエアコン吹出絶対湿度の計算 ====

    # i室のn時点におけるエアコンの（BFを考慮した）相当風量[m3/s]
    # 空調の熱交換部飽和絶対湿度の計算
    brmx_rac_is_n_pls, brxc_rac_is_n_pls = heat_exchanger.get_dehumid_coeff(
        lcs_is_n=l_cs_is_n,
        theta_r_is_npls=theta_r_is_npls,
        rac_spec=ss.rac_spec,
        x_r_non_dh_is_n=x_r_non_dh_is_n_pls
    )

    # 室絶対湿度[kg/kg(DA)]の計算
    brmx_is_n_pls = brmx_non_dh_is_n_pls + brmx_rac_is_n_pls
    brxc_is_n_pls = brxc_non_dh_is_n_pls + brxc_rac_is_n_pls

    # 室絶対湿度の計算 式(16)
    x_r_is_npls = np.dot(np.linalg.inv(brmx_is_n_pls), brxc_is_n_pls)

    # 除湿量
    l_cl_i_n = - (np.dot(brmx_rac_is_n_pls, x_r_is_npls) - brxc_rac_is_n_pls) * get_l_wtr()

    # 備品類の絶対湿度の計算
    x_frt_is_npls = (ss.c_cap_w_frt_is * c_n.x_frt_is_n + 900 * ss.c_w_frt_is * x_r_is_npls) / (ss.c_cap_w_frt_is + 900 * ss.c_w_frt_is)

    # ステップnにおける室iの在室者の着衣温度, degree C, [i, 1]
    theta_cl_is_n_pls = occupants.get_theta_cl_is_n(clo_is_n=clo_is_n, theta_ot_is_n=theta_ot_is_npls, h_hum_is_n=h_hum_is_n)

    logger.operation_mode[:, n] = operation_mode_is_n.flatten()
    logger.theta_r[:, n] = theta_r_is_npls.flatten()
    logger.x_r[:, n] = x_r_is_npls.flatten()
    logger.theta_mrt[:, n] = theta_mrt_hum_is_npls.flatten()
    logger.theta_ot[:, n] = theta_ot_is_npls.flatten()
    logger.pmv_target[:, n] = pmv_target_is_n.flatten()
    logger.h_hum_c_is_n[:, n] = h_hum_c_is_n.flatten()
    logger.h_hum_r_is_n[:, n] = h_hum_r_is_n.flatten()
    logger.v_hum_is_n[:, n] = v_hum_is_n.flatten()
    logger.clo[:, n] = clo_is_n.flatten()
    logger.q_hum[:, n] = q_hum_is_n.flatten()
    logger.x_hum[:, n] = x_hum_is_n.flatten()
    logger.l_cs[:, n] = l_cs_is_n.flatten()
    logger.l_rs[:, n] = l_hs_is_n.flatten()
    logger.l_cl[:, n] = l_cl_i_n.flatten()
    logger.theta_frnt[:, n] = theta_frt_is_npls.flatten()
    logger.x_frnt[:, n] = x_frt_is_npls.flatten()
    logger.theta_s[:, n] = theta_s_js_npls.flatten()
    logger.theta_rear[:, n] = theta_rear_js_npls.flatten()
    logger.theta_ei[:, n] = theta_ei_js_npls.flatten()
    logger.qisol_s[:, n] = ss.q_sol_js_ns[:, n].flatten()
    logger.qiall_s[:, n] = [q for q in q_srf_js_n]
    logger.h_c_s[:, n] = [h for h in ss.h_c_js]
    logger.h_r_s[:, n] = [h for h in ss.h_r_js]

    return Conditions(
        operation_mode_is_n=operation_mode_is_n,
        theta_r_is_n=theta_r_is_npls,
        theta_mrt_hum_is_n=theta_mrt_hum_is_npls,
        x_r_is_n=x_r_is_npls,
        theta_dsh_srf_a_js_ms_n=theta_dsh_srf_a_js_ms_npls,
        theta_dsh_srf_t_js_ms_n=theta_dsh_srf_t_js_ms_npls,
        q_srf_js_n=q_srf_js_n,
        theta_frnt_is_n=theta_frt_is_npls,
        x_frnt_is_n=x_frt_is_npls,
        theta_cl_is_n=theta_cl_is_n_pls,
        theta_ei_js_n=theta_ei_js_npls
    )


