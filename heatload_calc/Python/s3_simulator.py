import numpy as np
from typing import List

import s4_1_sensible_heat as s41
import s4_2_latent_heat as s42

import a1_calculation_surface_temperature as a1
import apdx3_human_body as a3
import a9_rear_surface_equivalent_temperature as a9
import a12_indoor_radiative_heat_transfer as a12
import a13_Win_ACselect as a13
import a16_blowing_condition_rac as a16
import a18_initial_value_constants as a18
import a28_operative_temperature as a28
import a35_PMV as a35
import a37_groundonly_runup_calculation as a37
from s3_space_loader import Space

from Psychrometrics import rhtx


# 地盤の計算
def run_tick_groundonly(spaces: List[Space], To_n: float, n: int, Tave: float):

    for s in spaces:

        g = np.array(s.boundary_type_i_jstrs) == 'ground'  # [jstr]

        theta_srf_dsh_a_i_jstrs_npls_ms = a1.get_theta_srf_dsh_a_i_jstrs_npls_ms(
            q_srf_i_jstrs_n=s.q_srf_i_jstrs_n[g], phi_a_1_bnd_i_jstrs_ms=s.phi_a_1_bnd_i_jstrs_ms[g, :],
            r_bnd_i_jstrs_ms=s.r_bnd_i_jstrs_ms[g,:],
            theta_srf_dsh_a_i_jstrs_n_ms=s.theta_srf_dsh_a_i_jstrs_n_m[g, :])

        Ts_i_k_n = (s.phi_a_0_bnd_i_jstrs[g] * s.h_i_bnd_i_jstrs[g] * To_n
                            + np.sum(theta_srf_dsh_a_i_jstrs_npls_ms, axis=1) + Tave)\
            / (1.0 + s.phi_a_0_bnd_i_jstrs[g] * s.h_i_bnd_i_jstrs[g])

        s.q_srf_i_jstrs_n[g] = s.h_i_bnd_i_jstrs[g] * (To_n - Ts_i_k_n)

        s.theta_srf_dsh_a_i_jstrs_n_m[g, :] = theta_srf_dsh_a_i_jstrs_npls_ms


# 室温、熱負荷の計算
def run_tick(spaces: List[Space], theta_o_n: float, xo_n: float, n: int):

    # ステップnの室iにおける室温, degree C, [i]
    # 室内壁の場合の裏面温度を計算する際に隣りの室の室温を持ちるために使用する。
    theta_r_is_n = np.array([s.theta_r_i_npls for s in spaces])
    # ステップnの室iにおける絶対湿度
    x_r_is_n = np.array([s.x_r_i_npls for s in spaces])

    for i, s in enumerate(spaces):

        # ステップnの室iにおける室温, degree C
        theta_r_i_n = theta_r_is_n[i]

        # ステップnの室iの集約された境界j*における裏面温度, degree C, [j*]
        theta_rear_i_jstrs_n = a9.get_theta_rear_i_jstrs_n(
            theta_r_i_n=theta_r_i_n,
            n_bnd_i_jstrs=s.n_bnd_i_jstrs,
            boundary_type_i_jstrs=s.boundary_type_i_jstrs,
            h_bnd_i_jstrs=s.h_bnd_i_jstrs,
            next_room_type_bnd_i_jstrs=s.next_room_type_bnd_i_jstrs,
            theta_r_is_n=theta_r_is_n,
            theta_o_sol_bnd_i_jstrs_n=s.theta_o_sol_bnd_i_jstrs_ns[:, n]
        )

        # ステップnの室iにおける人体発熱, W
        q_hum_i_n = a3.get_q_hum_i_n(theta_r_i_n=theta_r_i_n, n_hum_i_n=s.n_hum_i_ns[n])

        # ステップnの室iにおける人体発湿, kg/s
        x_hum_i_n = a3.get_x_hum_i_n(theta_r_i_n=theta_r_i_n, n_hum_i_n=s.n_hum_i_ns[n])

        # ステップnの室iにおける内部発熱, W
        q_gen_i_n = s.q_gen_except_hum_i_ns[n] + q_hum_i_n

        # ステップnの室iにおける内部発湿, kg/s
        x_gen_i_n = s.x_gen_except_hum_i_ns[n] + x_hum_i_n

        # TODO: すきま風量未実装につき、とりあえず０とする
        # すきま風量を決めるにあたってどういった変数が必要なのかを決めること。
        # TODO: 単位は m3/s とすること。
        v_reak_i_n = 0.0

        # ステップn+1の室iの統合された境界j*における項別公比法の項mの吸熱応答に関する表面温度, degree C, [jstrs, 12]
        theta_srf_dsh_a_i_jstrs_npls_ms = a1.get_theta_srf_dsh_a_i_jstrs_npls_ms(
            q_srf_i_jstrs_n=s.q_srf_i_jstrs_n, phi_a_1_bnd_i_jstrs_ms=s.phi_a_1_bnd_i_jstrs_ms,
            r_bnd_i_jstrs_ms=s.r_bnd_i_jstrs_ms, theta_srf_dsh_a_i_jstrs_n_ms=s.theta_srf_dsh_a_i_jstrs_n_m)

        # ステップn+1の室iの統合された境界j*における項別公比法の項mの貫流応答に関する表面温度, degree C, [jstrs, 12]
        theta_srf_dsh_t_i_jstrs_npls_ms = a1.get_theta_srf_dsh_t_i_jstrs_npls_ms(
            theta_rear_i_jstrs_n=theta_rear_i_jstrs_n, phi_t_1_bnd_i_jstrs_ms=s.phi_t_1_bnd_i_jstrs_ms,
            r_bnd_i_jstrs_ms=s.r_bnd_i_jstrs_ms, theta_srf_dsh_t_i_jstrs_n_m=s.theta_srf_dsh_t_i_jstrs_n_m)

        # ステップn+1の室iの統合された境界j*における係数CVL, degree C, [j*]
        cvl_i_jstrs_npls = a1.get_cvl_i_jstrs_npls(
            theta_srf_dsh_t_i_jstrs_npls_ms=theta_srf_dsh_t_i_jstrs_npls_ms,
            theta_srf_dsh_a_i_jstrs_npls_ms=theta_srf_dsh_a_i_jstrs_npls_ms)

        # ステップn+1の室iの統合された境界j*における係数CRX, degree C, [j*]
        crx_i_jstrs_npls = a1.get_crx_i_jstrs_npls(
            phi_a_0_bnd_i_jstrs=s.phi_a_0_bnd_i_jstrs,
            q_sol_floor_i_jstrs_n=s.q_sol_srf_i_jstrs_ns[:, n],
            phi_t_0_bnd_i_jstrs=s.phi_t_0_bnd_i_jstrs,
            theta_rear_i_jstrs_n=theta_rear_i_jstrs_n)

        # ステップn+1の室iの断熱された境界j*における係数WSC, degree C, [j*]
        wsc_i_jstrs_npls = a1.get_wsc_i_jstrs_npls(ivs_x_i=s.ivs_x_i, crx_i_jstrs_npls=crx_i_jstrs_npls)

        # ステップn+1の室iの断熱された境界j*における係数WSV, degree C, [j*]
        wsv_i_jstrs_npls = a1.get_wsv_i_jstrs_npls(ivs_x_i=s.ivs_x_i, cvl_i_jstrs_npls=cvl_i_jstrs_npls)

        # ステップnの室iにおける隣室i*からの室間換気の空気温度, degree C, [i*]
        theta_r_int_vent_i_istrs_n = np.array([theta_r_is_n[x] for x in s.next_room_idxs_i])

        # ステップnの室iにおける隣室i*からの室間換気の絶対湿度, kg/kgDA, [i*]
        x_r_int_vent_i_istrs_n = np.array([x_r_is_n[x] for x in s.next_room_idxs_i])

        # ステップnの室iにおける係数BRC（通風なし）, W
        # ステップnの室iにおける係数BRC（通風あり）, W
        brc_non_ntrv_i_n, brc_ntrv_i_n = s41.get_brc_i_n(
            c_room_i=s.c_room_i, deta_t=900.0, theta_r_i_n=theta_r_i_n, h_c_bnd_i_jstrs=s.h_c_bnd_i_jstrs,
            a_bnd_i_jstrs=s.a_bnd_i_jstrs, wsc_i_jstrs_npls=wsc_i_jstrs_npls, wsv_i_jstrs_npls=wsv_i_jstrs_npls,
            v_mec_vent_i_n=s.v_mec_vent_i_ns[n], v_reak_i_n=v_reak_i_n, v_int_vent_i_istrs=s.v_int_vent_i_istrs,
            v_ntrl_vent_i=s.v_ntrl_vent_i, theta_o_n=theta_o_n, theta_r_int_vent_i_istrs_n=theta_r_int_vent_i_istrs_n,
            q_gen_i_n=q_gen_i_n, c_cap_frnt_i=s.c_cap_frnt_i, k_frnt_i=s.k_frnt_i, q_sol_frnt_i_n=s.q_sol_frnt_i_ns[n],
            theta_frnt_i_n=s.old_theta_frnt_i)

        brm_non_ntrv_i_n = s.BRMnoncv_i[n]
        brm_ntrv_i_n = brm_non_ntrv_i_n + a18.get_c_air() * a18.get_rho_air() * s.v_ntrl_vent_i

        # 自然室温計算時窓開閉条件の設定
        # 空調需要がなければ窓閉鎖、空調需要がある場合は前時刻の窓開閉状態
        is_now_window_open_i_n = s.old_is_now_window_open_i and s.air_conditioning_demand[n]

        brc_i_n = brc_ntrv_i_n if is_now_window_open_i_n else brc_non_ntrv_i_n
        brm_i_n = brm_ntrv_i_n if is_now_window_open_i_n else brm_non_ntrv_i_n

        # ********** 非空調(自然)作用温度、PMV の計算 **********

        BRMot_without_ac, BRCot_without_ac, _, Xot_without_ac, XLr_without_ac, XC_without_ac = s41.calc_OT_coeff(
            BRM_i=brm_i_n, BRC_i=brc_i_n, BRL_i=s.BRL_i[n],
            WSR_i_k=s.WSR_i_k, WSB_i_k=s.WSB_i_k, WSC_i_k=wsc_i_jstrs_npls, WSV_i_k=wsv_i_jstrs_npls, fot=s.Fot_i_g, kc_i=s.kc_i,
            kr_i=s.kr_i)

        # 自然作用温度の計算
        OT_without_ac = s41.get_OT_without_ac(BRCot_without_ac, BRMot_without_ac)

        ##### ここが仮計算！！！！！！！！！！！！！（１回目）
        # 自然室温を計算 式(14)
        Tr_without_ac = s41.get_Tr_i_n(OT_without_ac, 0.0, Xot_without_ac, XLr_without_ac, XC_without_ac)

        # 自然MRTを計算 TODO:仕様書内の場所不明
        MRT_without_ac = (OT_without_ac - s.kc_i * Tr_without_ac) / s.kr_i

        # 着衣量 式(128)
        I_cl = a35.get_I_cl(OT_without_ac)

        # 自然PMVを計算する
        Vel_without_ac = 0.0 if not is_now_window_open_i_n else 0.1
        PMV_without_ac = a35.calc_PMV(
            t_a=Tr_without_ac, t_r_bar=MRT_without_ac, clo_value=I_cl,
            v_ar=Vel_without_ac, rh=s.RH_i_npls)

        # ********** 窓開閉、空調発停の決定 **********

        # 窓の開閉と空調発停の切り替え判定
        is_now_window_open_i_n, ac_mode = a13.mode_select(
            s.air_conditioning_demand[n], s.prev_air_conditioning_mode, s.is_prev_window_open, PMV_without_ac)

        # 目標PMVの計算（冷房時は上限、暖房時は下限PMVを目標値とする）
        # 空調モード: -1=冷房, 0=停止, 1=暖房, 2=, 3=    ==>  [停止, 暖房, 暖房(1), 暖房(2), 冷房]
        PMV_set = [None,
                   s.pmv_lower_limit_schedule[n],
                   s.pmv_lower_limit_schedule[n],
                   s.pmv_lower_limit_schedule[n],
                   s.pmv_upper_limit_schedule[n]][ac_mode]

        # 最終計算のための係数整備
        brc_i_n = brc_ntrv_i_n if is_now_window_open_i_n else brc_non_ntrv_i_n
        brm_i_n = brm_ntrv_i_n if is_now_window_open_i_n else brm_non_ntrv_i_n

        # OT計算用の係数補正
        BRMot, BRCot, BRLot, Xot, XLr, XC = s41.calc_OT_coeff(
            brm_i_n, brc_i_n, s.BRL_i[n], s.WSR_i_k, s.WSB_i_k, wsc_i_jstrs_npls, wsv_i_jstrs_npls,s.Fot_i_g, s.kc_i, s.kr_i)

        # ********** 空調設定温度の計算 **********

        # 前時刻の相対湿度を用い、PMV目標値を満たすような目標作用温度を求める
        OTset, Clo_i_n, Vel_i_n = a28.calc_OTset(ac_mode, s.is_radiative_heating, s.RH_i_npls, PMV_set)

        ot_i_n, lcs_i_n, lrs_i_n = s41.calc_next_step(
            ac_mode, s.is_radiative_heating, BRCot, BRMot, BRLot, OTset, s.Lrcap_i)

        # ********** 室温 Tr、家具温度 Tfun、表面温度 Ts_i_k_n、室内表面熱流 q の計算 **********

        # 自然室温 Tr を計算 式(14)
        theta_r_i_npls = s41.get_Tr_i_n(ot_i_n, lrs_i_n, Xot, XLr, XC)

        # 家具の温度 Tfun を計算 式(15)
        theta_frnt_i_n = s41.get_Tfun_i_n(s.c_cap_frnt_i, s.old_theta_frnt_i, s.k_frnt_i, theta_r_i_npls, s.q_sol_frnt_i_ns[n])

        # 表面温度の計算 式(23)
        Ts_i_k_n = a1.get_surface_temperature(s.WSR_i_k, s.WSB_i_k, wsc_i_jstrs_npls, wsv_i_jstrs_npls, theta_r_i_npls, lrs_i_n)

        # MRT_i_n、AST、平均放射温度の計算
        MRT_i_n = get_MRT(s.Fot_i_g, Ts_i_k_n)

        # 室内表面熱流の計算 式(28)
        Qc, Qr, q_srf_i_jstrs_n = a1.calc_qi(
            s.h_c_bnd_i_jstrs, s.a_bnd_i_jstrs, s.h_r_bnd_i_jstrs, s.q_sol_srf_i_jstrs_ns[:, n], s.flr_i_k,
            Ts_i_k_n, theta_r_i_npls, s.F_mrt_i_g, lrs_i_n, s.Beta_i)

        # ********** 室湿度 xr、除湿量 G_hum、湿加湿熱量 Ll の計算 **********

        # 式(17)
        BRMX_pre = s42.get_BRMX(
            v_reak_i_n=v_reak_i_n,
            Gf=s.Gf_i,
            Cx=s.Cx_i,
            volume=s.v_room_cap_i,
            v_int_vent_i_istrs=s.v_int_vent_i_istrs,
            v_mec_vent_i_n=s.v_mec_vent_i_ns[n]
        )

        # 式(18)
        BRXC_pre = s42.get_BRXC(
            v_reak_i_n=v_reak_i_n,
            Gf=s.Gf_i,
            Cx=s.Cx_i,
            volume=s.v_room_cap_i,
            v_int_vent_i_istrs=s.v_int_vent_i_istrs,
            xr_next_i_j_nm1=x_r_int_vent_i_istrs_n,
            xr_i_nm1=s.x_r_i_npls,
            xf_i_nm1=s.xf_i_npls,
            Lin=x_gen_i_n,
            xo=xo_n,
            v_mec_vent_i_n=s.v_mec_vent_i_ns[n]
        )

        # ==== ルームエアコン吹出絶対湿度の計算 ====

        # バイパスファクターBF 式(114)
        BF = a16.get_BF()

        # i室のn時点におけるエアコンの風量[m3/s]
        # 空調の熱交換部飽和絶対湿度の計算
        Vac_n, xeout_i_n = \
            a16.calcVac_xeout(lcs_i_n, s.Vmin_i, s.Vmax_i, s.qmin_c_i, s.qmax_c_i, theta_r_i_npls, BF, ac_mode)

        # 空調機除湿の項 式(20)より
        RhoVac = get_RhoVac(Vac_n, BF)

        # 室絶対湿度[kg/kg(DA)]の計算
        BRMX_base = BRMX_pre + RhoVac
        BRXC_base = BRXC_pre + RhoVac * xeout_i_n

        # 室絶対湿度の計算 式(16)
        xr_base = s42.get_xr(BRXC_base, BRMX_base)

        # 補正前の加湿量の計算 [ks/s] 式(20)
        Ghum_base = s42.get_Ghum(RhoVac, xeout_i_n, xr_base)

        # 除湿量が負値(加湿量が正)になった場合にはルームエアコン風量V_(ac,n)をゼロとして再度室湿度を計算する
        if Ghum_base > 0.0:
            Ghum_i_n = 0.0
            x_r_i_ns = s42.get_xr(BRXC_pre, BRMX_pre)
        else:
            Ghum_i_n = Ghum_base
            x_r_i_ns = xr_base

        # 除湿量から室加湿熱量を計算 式(21)
        Lcl_i_n = get_Lcl(Ghum_i_n)

        # 当面は放射空調の潜熱は0
        Lrl_i_n = get_Lrl()

        # 室相対湿度の計算 式(22)
        RH_i_n = rhtx(theta_r_i_npls, x_r_i_ns)

        # ********** 備品類の絶対湿度 xf の計算 **********

        # 備品類の絶対湿度の計算
        xf_i_n = s42.get_xf(s.Gf_i, s.xf_i_npls, s.Cx_i, x_r_i_ns)
        Qfunl_i_n = s42.get_Qfunl(s.Cx_i, x_r_i_ns, xf_i_n)
        pmv_i_n = a35.calc_PMV(t_a=theta_r_i_npls, t_r_bar=MRT_i_n, clo_value=Clo_i_n, v_ar=Vel_i_n, rh=RH_i_n)

        # ********** 窓開閉、空調発停の決定 **********

        # 次の時刻に用いる変数の引き渡し
        s.theta_srf_dsh_a_i_jstrs_n_m = theta_srf_dsh_a_i_jstrs_npls_ms
        s.theta_srf_dsh_t_i_jstrs_n_m = theta_srf_dsh_t_i_jstrs_npls_ms
        s.old_is_now_window_open_i = is_now_window_open_i_n
        s.old_theta_frnt_i = theta_frnt_i_n
        s.theta_r_i_npls = theta_r_i_npls
        s.q_srf_i_jstrs_n = q_srf_i_jstrs_n
        s.xf_i_npls = xf_i_n
        s.prev_air_conditioning_mode = ac_mode
        s.RH_i_npls = RH_i_n
        s.x_r_i_npls = x_r_i_ns

        # ロギング
        s.logger.theta_r_i_ns[n] = theta_r_i_npls
        s.logger.theta_rear_i_jstrs_ns[:, n] = theta_rear_i_jstrs_n
        s.logger.q_hum_i_ns[n] = q_hum_i_n
        s.logger.x_hum_i_ns[n] = x_hum_i_n
        s.logger.is_now_window_open_i_n[n] = is_now_window_open_i_n
        s.logger.theta_frnt_i_ns[n] = theta_frnt_i_n
        s.logger.OT_i_n[n] = ot_i_n
        s.logger.Qfuns_i_n[n] = s41.get_Qfuns(s.k_frnt_i, theta_r_i_npls, theta_frnt_i_n)
        s.logger.Qc[:, n] = Qc
        s.logger.Qr[:, n] = Qr
        s.logger.Ts_i_k_n[:, n] = Ts_i_k_n
        s.logger.MRT_i_n[n] = MRT_i_n
        # 室内側等価温度の計算 式(29)
        s.logger.Tei_i_k_n[:, n] = a1.calc_Tei(
            s.h_c_bnd_i_jstrs, s.h_i_bnd_i_jstrs, s.h_r_bnd_i_jstrs, s.q_sol_srf_i_jstrs_ns[:, n], s.flr_i_k,
            s.a_bnd_i_jstrs, theta_r_i_npls, s.F_mrt_i_g, Ts_i_k_n, lrs_i_n, s.Beta_i)
        s.logger.Lrs_i_n[n] = lrs_i_n
        s.logger.Lcs_i_n[n] = lcs_i_n
        s.logger.Lcl_i_n[n] = Lcl_i_n
        s.logger.xf_i_n[n] = xf_i_n
        s.logger.Qfunl_i_n[n] = Qfunl_i_n
        s.logger.pmv_i_ns[n] = pmv_i_n
        s.logger.Vel_i_n[n] = Vel_i_n
        s.logger.Clo_i_n[n] = Clo_i_n
        s.logger.now_air_conditioning_mode[n] = ac_mode
        s.logger.RH_i_n[n] = RH_i_n
        s.logger.x_r_i_ns[n] = x_r_i_ns


# MRTの計算
def get_MRT(fot, Ts):
    return np.sum(fot * Ts)


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
