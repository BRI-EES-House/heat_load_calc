import numpy as np
import json
from functools import reduce

from heat_load_calc.core.operation_mode import OperationMode
from heat_load_calc.core.pre_calc_parameters import PreCalcParameters
from heat_load_calc.core.conditions import Conditions
from heat_load_calc.external.global_number import get_c_air, get_rho_air, get_l_wtr
from heat_load_calc.core.log import Logger
from heat_load_calc.core import next_condition
from heat_load_calc.core import ot_target_pmv
from heat_load_calc.core import humidification
from heat_load_calc.core.matrix_method import v_diag
from heat_load_calc.core import occupants
from operator import add


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

    # 時刻 n, n+1 におけるデータの切り出し
    #   [i, n] のベクトルを[:, n] 又は[:, n+1] で切り出す。
    #   numpy の仕様として、切り出した時にある次元の配列数が1の場合に、次元を1つ減らすため、
    #   [:, n] 又は [:, n+1] で切り出した場合、[i] 又は [j] の1次元配列になる。
    #   ベクトル計算に都合の良いように、[i, 1] 又は [j, 1] の列ベクトルになおすために、 np.reshape(-1, 1)の操作をしている。

    # ステップnにおける室iの空調需要, [i, 1]
    ac_demand_is_n = ss.ac_demand_is_ns[:, n].reshape(-1, 1)

    # ステップnの境界jにおける外気側等価温度の外乱成分, degree C, [j, 1]
    theta_dstrb_js_n = ss.theta_dstrb_js_ns[:, n + 1].reshape(-1, 1)

    # ステップnの室iにおける在室人数, [i, 1]
    n_hum_is_n = ss.n_hum_is_ns[:, n].reshape(-1, 1)

    # ステップnの室iにおける人体発熱を除く内部発熱, W, [i, 1]
    q_gen_is_n = ss.q_gen_is_ns[:, n].reshape(-1, 1)

    # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [i, 1]
    x_gen_is_n = ss.x_gen_is_ns[:, n].reshape(-1, 1)

    # ステップn+1の境界jにおける係数 WSC, degree C, [j, 1]
    f_wsc_js_n_pls = ss.wsc_js_ns[:, n + 1].reshape(-1, 1)

    # ステップnの室iにおける機械換気量（全般換気量+局所換気量）, m3/s, [i, 1]
    v_vent_mec_is_n = ss.v_mec_vent_is_ns[:, n].reshape(-1, 1)

    # 家具の吸収日射量, W, [i, 1]
    # TODO: ここの左辺、右辺日射量はn+1とすべき？
    q_sol_frt_is_n = ss.q_sol_frt_is_ns[:, n].reshape(-1, 1)

    # ステップnにおける室iの状況（在室者周りの総合熱伝達率・運転状態・Clo値・目標とする作用温度）を取得する
    #     ステップnにおける室iの在室者周りの対流熱伝達率, W / m2K, [i, 1]
    #     ステップnにおける室iの在室者周りの放射熱伝達率, W / m2K, [i, 1]
    #     ステップnの室iにおける運転モード, [i, 1]
    #     ステップnの室iにおける目標作用温度下限値, [i, 1]
    #     ステップnの室iにおける目標作用温度上限値, [i, 1]
    #     ステップnの室iの在室者周りの風速, m/s, [i, 1]
    #     ステップnの室iにおけるClo値, [i, 1]
    #     ステップnの室iにおける目標作用温度, degree C, [i, 1]
    h_hum_c_is_n, h_hum_r_is_n, operation_mode_is_n, theta_lower_target_is_n_pls, theta_upper_target_is_n_pls, remarks_is_n \
        = ss.get_ot_target_and_h_hum(
            x_r_is_n=c_n.x_r_is_n,
            operation_mode_is_n_mns=c_n.operation_mode_is_n,
            theta_r_is_n=c_n.theta_r_is_n,
            theta_mrt_hum_is_n=c_n.theta_mrt_hum_is_n,

            ac_demand_is_n=ac_demand_is_n
        )

    # ステップnの境界jにおける裏面温度, degree C, [j, 1]
    theta_rear_js_n = np.dot(ss.k_ei_js_js, c_n.theta_ei_js_n) + theta_dstrb_js_n

    # ステップnの室iにおける1人あたりの人体発熱, W, [i, 1]
    q_hum_psn_is_n = occupants.get_q_hum_psn_is_n(theta_r_is_n=c_n.theta_r_is_n)

    # ステップnの室iにおける人体発熱, W, [i, 1]
    q_hum_is_n = q_hum_psn_is_n * n_hum_is_n

    # ステップnの室iにおける1人あたりの人体発湿, kg/s, [i, 1]
    x_hum_psn_is_n = occupants.get_x_hum_psn_is_n(theta_r_is_n=c_n.theta_r_is_n)

    # ステップnの室iにおける人体発湿, kg/s, [i, 1]
    x_hum_is_n = x_hum_psn_is_n * n_hum_is_n

    # ステップnの室iにおけるすきま風量, m3/s, [i, 1]
    v_leak_is_n = ss.get_infiltration(theta_r_is_n=c_n.theta_r_is_n, theta_o_n=ss.theta_o_ns[n])

    # ステップn+1の境界jにおける項別公比法の指数項mの吸熱応答の項別成分, degree C, [j, m] (m=12)
    theta_dsh_srf_a_js_ms_n_pls = ss.phi_a1_js_ms * c_n.q_srf_js_n + ss.r_js_ms * c_n.theta_dsh_srf_a_js_ms_n

    # ステップn+1の境界jにおける項別公比法の指数項mの貫流応答の項別成分, degree C, [j, m] (m=12)
    theta_dsh_srf_t_js_ms_n_pls = ss.phi_t1_js_ms * theta_rear_js_n + ss.r_js_ms * c_n.theta_dsh_srf_t_js_ms_n

    # ステップn+1の境界jにおける係数CVL, degree C, [j, 1]
    cvl_js_n_pls = np.sum(theta_dsh_srf_t_js_ms_n_pls + theta_dsh_srf_a_js_ms_n_pls, axis=1, keepdims=True)

    # ステップn+1の境界jにおける係数WSV, degree C, [j, 1]
    f_wsv_js_n_pls = np.dot(ss.ivs_f_ax_js_js, cvl_js_n_pls)

    # 室iの自然風利用による換気量, m3/s, [i, 1]
    # 自然風を利用していない場合は、0.0 m3/s になる。
    v_vent_ntr_is_n = np.where(operation_mode_is_n == OperationMode.STOP_OPEN, ss.v_ntrl_vent_is, 0.0)

    # ステップnにおける室iの外からの換気量, m3/s, [i, 1], eq.(25)
    v_vent_out_is_n = v_leak_is_n + v_vent_mec_is_n + v_vent_ntr_is_n

    # ステップn+1の室iにおける係数 BRC, W, [i, 1], eq.(24)
    f_brc_is_n_pls = ss.c_rm_is / delta_t * c_n.theta_r_is_n \
        + np.dot(ss.p_is_js, ss.h_s_c_js * ss.a_s_js * (f_wsc_js_n_pls + f_wsv_js_n_pls)) \
        + get_c_air() * get_rho_air() * v_vent_out_is_n * ss.theta_o_ns[n + 1] \
        + q_gen_is_n + q_hum_is_n \
        + ss.g_sh_frt_is * (
            ss.c_sh_frt_is * c_n.theta_frt_is_n + ss.q_sol_frt_is_ns[:, n].reshape(-1, 1) * delta_t
        ) / (ss.c_sh_frt_is + delta_t * ss.g_sh_frt_is)

    # ステップn+1における係数 BRM, W/K, [i, i], eq.(23)
    f_brm_is_is_n_pls = np.diag(ss.c_rm_is.flatten() / delta_t) \
        + np.dot(ss.p_is_js, (ss.p_js_is - ss.f_wsr_js_is) * ss.a_s_js * ss.h_s_c_js) \
        + np.diag((ss.c_sh_frt_is * ss.g_sh_frt_is / (ss.c_sh_frt_is + ss.g_sh_frt_is * delta_t)).flatten()) \
        + get_c_air() * get_rho_air() * (np.diag(v_vent_out_is_n.flatten()) - ss.v_vent_int_is_is)

    # ステップnにおける室iの在室者表面における対流熱伝達率の総合熱伝達率に対する比, -, [i, 1], eq.(22)
    kc_is_n = h_hum_c_is_n / (h_hum_c_is_n + h_hum_r_is_n)

    # ステップnにおける室iの在室者表面における放射熱伝達率の総合熱伝達率に対する比, -, [i, 1], eq.(21)
    kr_is_n = h_hum_r_is_n / (h_hum_c_is_n + h_hum_r_is_n)

    # ステップn+1における室iの係数 XOT, [i, i], eq.(20)
    f_xot_is_is_n_pls = np.linalg.inv(v_diag(kc_is_n) + kr_is_n * np.dot(ss.f_mrt_hum_is_js, ss.f_wsr_js_is))

    # ステップn+1における室iの係数 XC, [i, 1], eq.(19)
    f_xc_is_n_pls = np.dot(f_xot_is_is_n_pls, kr_is_n * np.dot(ss.f_mrt_hum_is_js, (f_wsc_js_n_pls + f_wsv_js_n_pls)))

    # ステップnにおける係数 BRMOT, W/K, [i, i], eq.(18)
    f_brm_ot_is_is_n_pls = np.dot(f_brm_is_is_n_pls, f_xot_is_is_n_pls)

    # ステップnにおける係数 BRCOT, W, [i, 1], eq.(17)
    f_brc_ot_is_n_pls = f_brc_is_n_pls + np.dot(f_brm_is_is_n_pls, f_xc_is_n_pls)

    # ステップ n+1 における自然作用温度, [i, 1], ℃, eq.(16)
    theta_r_ot_ntr_is_n_pls = np.dot(np.linalg.inv(f_brm_ot_is_is_n_pls), f_brc_ot_is_n_pls)

    # ステップ n から n+1 において室 i で実際に暖房・冷房が行われるかどうかの判定結果, [i, 1], eq(15a,15b)
    is_heating_is_n = (operation_mode_is_n == OperationMode.HEATING) & (theta_r_ot_ntr_is_n_pls < theta_lower_target_is_n_pls)
    is_cooling_is_n = (operation_mode_is_n == OperationMode.COOLING) & (theta_upper_target_is_n_pls < theta_r_ot_ntr_is_n_pls)

    # flr, -, [j,i], eq.(14)
    flr_js_is_n_pls = ss.flr_h_js_is * is_heating_is_n.flatten() + ss.flr_c_js_is * is_cooling_is_n.flatten()

    # beta, -, [i], eq.(13)
    beta_is_n_pls = ss.beta_h_is * is_heating_is_n + ss.beta_c_is * is_cooling_is_n

    # F_FLB, K/W, [j, i], eq.(12)
    f_flb_js_is_n_pls = flr_js_is_n_pls * (1.0 - beta_is_n_pls.T) * ss.phi_a0_js / ss.a_s_js \
        + np.dot(ss.k_ei_js_js, flr_js_is_n_pls * (1.0 - beta_is_n_pls.T)) * ss.phi_t0_js / (ss.h_s_c_js + ss.h_s_r_js) / ss.a_s_js

    # F_WSB, K/W, [j, i], eq.(11)
    f_wsb_js_is_n_pls = np.dot(ss.ivs_f_ax_js_js, f_flb_js_is_n_pls)

    # F_BRL, -, [i, i], eq.(10)
    f_brl_is_is_n_pls = np.dot(ss.p_is_js, f_wsb_js_is_n_pls * ss.h_s_c_js * ss.a_s_js) + np.diag(beta_is_n_pls.flatten())

    # ステップn+1における室iの係数 F_XLR, K/W, [i, i], eq.(9)
    f_xlr_is_is_n_pls = np.dot(f_xot_is_is_n_pls, kr_is_n * np.dot(ss.f_mrt_hum_is_js, f_wsb_js_is_n_pls))

    # ステップnにおける係数 F_BRL_OT, -, [i, i], eq.(8)
    f_brl_ot_is_is_n_pls = f_brl_is_is_n_pls + np.dot(f_brm_is_is_n_pls, f_xlr_is_is_n_pls)

    # ステップ n+1 における室 i の作用温度, degree C, [i, 1] (ステップn+1における瞬時値）
    # ステップ n における室 i に設置された対流暖房の放熱量, W, [i, 1] (ステップn～ステップn+1までの平均値）
    # ステップ n における室 i に設置された放射暖房の放熱量, W, [i, 1]　(ステップn～ステップn+1までの平均値）
    theta_ot_is_n_pls, l_sc_is_n, l_sr_is_n = ss.calc_next_temp_and_load(
        brc_ot_is_n=f_brc_ot_is_n_pls,
        brm_ot_is_is_n=f_brm_ot_is_is_n_pls,
        brl_ot_is_is_n=f_brl_ot_is_is_n_pls,
        theta_lower_target_is_n=theta_lower_target_is_n_pls,
        theta_upper_target_is_n=theta_upper_target_is_n_pls,
        operation_mode_is_n=operation_mode_is_n,
        ac_demand_is_n=ac_demand_is_n,
        theta_natural_is_n=theta_r_ot_ntr_is_n_pls,
        is_heating_is_n=is_heating_is_n,
        is_cooling_is_n=is_cooling_is_n
    )

    # ステップ n+1 における室 i の室温, degree C, [i, 1], eq.(6)
    theta_r_is_n_pls = np.dot(f_xot_is_is_n_pls, theta_ot_is_n_pls) - np.dot(f_xlr_is_is_n_pls, l_sr_is_n) - f_xc_is_n_pls

    # ステップ n+1 における境界 j の表面温度, degree C, [j, 1], eq.(5)
    theta_s_js_n_pls = np.dot(ss.f_wsr_js_is, theta_r_is_n_pls) + f_wsc_js_n_pls \
                       + np.dot(f_wsb_js_is_n_pls, l_sr_is_n) + f_wsv_js_n_pls

    # ステップ n+1 における室 i　の家具の温度, degree C, [i, 1], eq.(4)
    theta_frt_is_n_pls = (
        ss.c_sh_frt_is * c_n.theta_frt_is_n + delta_t * ss.g_sh_frt_is * theta_r_is_n_pls + q_sol_frt_is_n * delta_t
    ) / (ss.c_sh_frt_is + delta_t * ss.g_sh_frt_is)

    # ステップ n+1 における室 i の人体に対する平均放射温度, degree C, [i, 1], eq.(3)
    theta_mrt_hum_is_n_pls = np.dot(ss.f_mrt_hum_is_js, theta_s_js_n_pls)

    # ステップ n+1 における境界 j の等価温度, degree C, [j, 1], eq.(2)
    theta_ei_js_n_pls = (
        ss.h_s_c_js * np.dot(ss.p_js_is, theta_r_is_n_pls)
        + ss.h_s_r_js * np.dot(ss.f_dsh_mrt_js_js, theta_s_js_n_pls)
        + ss.q_sol_js_ns[:, n+1].reshape(-1, 1)
        + np.dot(flr_js_is_n_pls, (1.0 - beta_is_n_pls) * l_sr_is_n) / ss.a_s_js
    ) / (ss.h_s_c_js + ss.h_s_r_js)

    # ステップ n+1 における境界 j の表面熱流（壁体吸熱を正とする）, W/m2, [j, 1], eq.(1)
    q_s_js_n_pls = (theta_ei_js_n_pls - theta_s_js_n_pls) * (ss.h_s_c_js + ss.h_s_r_js)

    # --- ここから、湿度の計算 ---

    l_l_i_n, x_frt_is_n_pls, x_r_is_n_pls = calc_humidity_and_latent_load(
        delta_t=delta_t,
        l_cs_is_n=l_sc_is_n,
        ss=ss,
        theta_r_is_n_pls=theta_r_is_n_pls,
        v_vent_out_is_n=v_vent_out_is_n,
        x_gen_is_n=x_gen_is_n,
        x_hum_is_n=x_hum_is_n,
        v_room_is=ss.v_room_is,
        c_lh_frt_is=ss.c_lh_frt_is,
        g_lh_frt_is=ss.g_lh_frt_is,
        v_vent_int_is_is=ss.v_vent_int_is_is,
        x_o_n_pls=ss.x_o_ns[n + 1],
        x_r_is_n=c_n.x_r_is_n,
        x_frt_is_n=c_n.x_frt_is_n
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
        logger.l_cs[:, n] = l_sc_is_n.flatten()
        logger.l_rs[:, n] = l_sr_is_n.flatten()
        logger.l_cl[:, n] = l_l_i_n.flatten()
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
        theta_dsh_srf_a_js_ms_n=theta_dsh_srf_a_js_ms_n_pls,
        theta_dsh_srf_t_js_ms_n=theta_dsh_srf_t_js_ms_n_pls,
        q_srf_js_n=q_s_js_n_pls,
        theta_frt_is_n=theta_frt_is_n_pls,
        x_frt_is_n=x_frt_is_n_pls,
        theta_ei_js_n=theta_ei_js_n_pls
    )


def calc_humidity_and_latent_load(
        delta_t: float,
        l_cs_is_n,
        ss,
        theta_r_is_n_pls: np.ndarray,
        v_vent_out_is_n: np.ndarray,
        x_gen_is_n: np.ndarray,
        x_hum_is_n: np.ndarray,
        v_room_is: np.ndarray,
        c_lh_frt_is: np.ndarray,
        g_lh_frt_is: np.ndarray,
        v_vent_int_is_is: np.ndarray,
        x_o_n_pls: float,
        x_r_is_n: np.ndarray,
        x_frt_is_n: np.ndarray
):
    """

    Args:
        delta_t: 1ステップの時間間隔, s
        l_cs_is_n:
        ss:
        theta_r_is_n_pls: ステップ  n+1 における室 i の温度, ℃
        v_vent_out_is_n: ステップ n から n+1 における室 i の外気との換気量, m3/s, [i, 1]
        x_gen_is_n: ステップ n における室 i の人体発湿を除く内部発湿, kg/s, [i, 1]
        x_hum_is_n: ステップ n における室 i の人体発湿, kg/s, [i, 1]
        v_room_is: 室 i の容積, m3, [i, 1]
        c_lh_frt_is: 室 i の家具等の湿気容量, kg/(kg/kg(DA)), [i, 1]
        g_lh_frt_is: 室 i の家具等と空気間の湿気コンダクタンス, kg/(s kg/kg(DA)), [i, 1]
        v_vent_int_is_is: 室 i から室 i への室間の機械換気量, m3/s, [i, i]
        x_o_n_pls: ステップ  n+1 における外気絶対湿度, kg/kg(DA)
        x_r_is_n: ステップ  n における室 i の絶対湿度, kg/kg(DA), [i, 1]
        x_frt_is_n: ステップ  n における室 i の家具等の絶対湿度, kg/kg(DA), [i, 1]

    Returns:

    """

    # ステップ n における室iの湿度に関する係数 F_{h,wgt},　ｋｇ(DA)/s [i, i]
    # 繰り返し計算（湿度と潜熱） eq.10
    f_h_wgt_is_is_n = v_diag(
        get_rho_air() * (v_room_is / delta_t + v_vent_out_is_n)
        + c_lh_frt_is * g_lh_frt_is / (c_lh_frt_is + delta_t * g_lh_frt_is)
    ) - get_rho_air() * v_vent_int_is_is

    # ステップ n における室iの湿度に関する係数 F_{h,cst}, kg/s, [i, 1]
    # 繰り返し計算（湿度と潜熱） eq.11
    f_h_cst_is_n = get_rho_air() * v_room_is / delta_t * x_r_is_n \
                   + get_rho_air() * v_vent_out_is_n * x_o_n_pls \
                   + c_lh_frt_is * g_lh_frt_is / (c_lh_frt_is + delta_t * g_lh_frt_is) * x_frt_is_n \
                   + x_gen_is_n + x_hum_is_n

    # ステップ n+1 における室 i の加湿・除湿を行わない場合の絶対湿度, kg/kg(DA) [i]
    # 繰り返し計算（湿度と潜熱） eq.6
    x_r_ntr_is_n_pls = np.dot(np.linalg.inv(f_h_wgt_is_is_n), f_h_cst_is_n)

    # ==== ルームエアコン吹出絶対湿度の計算 ====
    # 顕熱負荷・室内温度・除加湿を行わない場合の室絶対湿度から、除加湿計算に必要な係数 la 及び lb を計算する。
    # 下記、変数 l は、係数 la と lb のタプルであり、変数 ls は変数 l のリスト。
    ls = [
        f(lcs_is_n=l_cs_is_n, theta_r_is_n_pls=theta_r_is_n_pls, x_r_ntr_is_n_pls=x_r_ntr_is_n_pls)
        for f in ss.dehumidification_funcs
    ]

    # 係数 la と 係数 lb をタプルから別々に取り出す。
    ls_a = np.array([l[0] for l in ls])
    ls_b = np.array([l[1] for l in ls])

    # 係数 la 及び lb それぞれ合計する。
    # la [i,i] kg/s(kg/kg(DA))
    # lb [i,1] kg/kg(DA)
    l_a_is_is_n = ls_a.sum(axis=0)
    l_b_is_n = ls_b.sum(axis=0)

    # ステップ n+1 における室 i の 絶対湿度, kg/kg(DA), [i, 1]
    x_r_is_n_pls = np.dot(np.linalg.inv(f_h_wgt_is_is_n + l_a_is_is_n), f_h_cst_is_n + l_b_is_n)

    # ステップ n から ステップ n+1 における室 i の潜熱負荷（加湿を正・除湿を負とする）, kg/s
    l_l_i_n = - (np.dot(l_a_is_is_n, x_r_is_n_pls) - l_b_is_n) * get_l_wtr()

    # ステップ n+1 における室 i の家具等の絶対湿度, kg/kg(DA), [i, 1]
    x_frt_is_n_pls = (c_lh_frt_is * x_frt_is_n + delta_t * g_lh_frt_is * x_r_is_n_pls) \
        / (c_lh_frt_is + delta_t * g_lh_frt_is)

    return l_l_i_n, x_frt_is_n_pls, x_r_is_n_pls


