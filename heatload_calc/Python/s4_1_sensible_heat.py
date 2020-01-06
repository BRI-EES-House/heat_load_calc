import numpy as np
import apdx3_human_body as a3
import a18_initial_value_constants as a18
from a39_global_parameters import ACMode, OperationMode
import a13_Win_ACselect as a13

# ********** 4.1 顕熱 **********


def get_theta_ot_is_n(
        h_hum_c_is_n: np.ndarray, h_hum_r_is_n: np.ndarray, h_hum_is_n: np.ndarray,
        theta_r_is_n: np.ndarray, theta_mrt_is_n: np.ndarray) -> np.ndarray:
    """作用温度を計算する。

    Args:
        h_hum_c_is_n: ステップnの室iにおける人体周りの対流熱伝達率, W/m2K, [i]
        h_hum_r_is_n: ステップnの室iにおける人体周りの放射熱伝達率, W/m2K, [i]
        h_hum_is_n: ステップnの室iにおける人体周りの総合熱伝達率, W/m2K, [i]
        theta_r_is_n: ステップnの室iにおける室温, degree C, [i]
        theta_mrt_is_n: ステップnの室iにおける平均放射温度, degree C, [i]

    Returns:
        ステップnの室iにおける作用温度
    """

    return (h_hum_r_is_n * theta_mrt_is_n + h_hum_c_is_n * theta_r_is_n) / h_hum_is_n


# 作用温度設定用係数への換算
def calc_OT_coeff(BRM_i, BRC_i, BRL_i, WSR_i_k, WSB_i_k, WSC_i_k, WSV_i_k, fot, kc_i, kr_i):
    # Deno 式(11)
    Deno = get_Deno(fot, kc_i, kr_i, WSR_i_k)

    # XLr 式(10)
    XLr = get_XLr_i(Deno, fot, kr_i, WSB_i_k)

    # XC 式(9)
    XC = get_XC_i(Deno, fot, kr_i, WSC_i_k, WSV_i_k)

    # Xot 式(8)
    Xot = get_Xot_i(Deno)

    # BRMot 式(2)
    BRMot = get_BRMot(BRM_i, Xot)

    # BRCot 式(3)
    BRCot = get_BRCot(BRC_i, BRM_i, XC)

    # BRLot 式(4)
    BRLot = get_BRLot(BRL_i, BRM_i, XLr)

    return BRMot, BRCot, BRLot, Xot, XLr, XC


# BRMot 式(2)
def get_BRMot(BRM, Xot):
    return BRM * Xot


# BRCot 式(3)
def get_BRCot(BRC, BRM, XC):
    return BRC + BRM * XC


# BRLot 式(4)
def get_BRLot(BRL, BRM, XLr):
    return BRL + BRM * XLr


# BRMの計算 式(5)
def get_BRM_i(Hcap, WSR_i_k, Cap_fun_i, C_fun_i, Vent, local_vent_amount_schedule, A_i_k, hc_i_k_n, V_nxt):
    ca = a18.get_c_air()
    rhoa = a18.get_rho_air()

    # 第1項
    BRM_0 = Hcap / 900

    # 第2項
    BRM_0 += np.sum(A_i_k * hc_i_k_n * (1.0 - WSR_i_k))

    # 空間換気
    BRM_0 += np.sum(ca * rhoa * V_nxt / 3600.0)

    # 家具からの熱取得
    BRM_0 += 1. / (900 / Cap_fun_i + 1. / C_fun_i) if Cap_fun_i > 0.0 else 0.0

    # 外気導入項の計算（3項目の0.0はすきま風量）
    # ※ここで、BRMがスカラー値(BRM_0)から1時間ごとの1次元配列(BRM_h)へ
    BRM_h = BRM_0 + ca * rhoa * (Vent + 0.0 + np.array(local_vent_amount_schedule[::4])) / 3600.0

    # 1時間当たり4ステップなので、配列を4倍に拡張
    BRM = np.repeat(BRM_h, 4)

    return BRM


def get_brc_i_n(c_room_i: float, deta_t: float, theta_r_i_n: float, h_c_bnd_i_jstrs: np.ndarray,
                a_bnd_i_jstrs: np.ndarray, wsc_i_jstrs_npls: np.ndarray, wsv_i_jstrs_npls: np.ndarray,
                v_mec_vent_i_n: float, v_reak_i_n: float, v_int_vent_i_istrs: np.ndarray, v_ntrl_vent_i: float,
                theta_o_n: float, theta_r_int_vent_i_istrs_n: np.ndarray, q_gen_i_n: float,
                c_cap_frnt_i: float, k_frnt_i: float, q_sol_frnt_i_n: float, theta_frnt_i_n: float,
                operation_mode: OperationMode) -> np.ndarray:
    """係数BRC（通風なし）および係数BRC（通風あり）を取得する。

    Args:
        c_room_i: 室iの熱容量, J/K
        deta_t: 時間刻み, s
        theta_r_i_n: ステップnの室iにおける室温, degree C
        h_c_bnd_i_jstrs: 室iの統合された境界j*における対流熱伝達率, W/m2K
        a_bnd_i_jstrs: 室iの統合された境界j*における面積, m2
        wsc_i_jstrs_npls: ステップn+1の室iの統合された境界j*における係数WSC, degree C, [j*]
        wsv_i_jstrs_npls: ステップn+1の室iの統合された境界j*における係数WSV, degree C, [j*]
        v_mec_vent_i_n: ステップnの室iにおける機械換気量（全般換気量+局所換気量）, m3/s
        v_reak_i_n: ステップnの室iにおけるすきま風量, m3/s
        v_int_vent_i_istrs: 室iにおける隣室i*からの室間換気量, m3/s, [j*]
        v_ntrl_vent_i: 室iの自然風利用時の換気量, m3/s
        theta_o_n: ステップnにおける外気温度, ℃, [8760 * 4]
        theta_r_int_vent_i_istrs_n: ステップnの室iにおける隣室i*からの室間換気の空気温度, degree C, [i*]
        q_gen_i_n: ステップnの室iにおける内部発熱, W
        c_cap_frnt_i: 室iにおける家具の熱容量, J/K
        k_frnt_i: 室iにおける家具と室空気間の熱コンダクタンス, W/K
        q_sol_frnt_i_n: ステップnの室iにおける家具の吸収日射量, W, [8760*4]
        theta_frnt_i_n: ステップnの室iにおける家具の温度, degree C

    Returns:
        ステップnの室iにおける係数BRC, W
    """

    c_air = a18.get_c_air()
    rho_air = a18.get_rho_air()

    brc_non_ntrv_i_n = c_room_i / deta_t * theta_r_i_n \
        + np.sum(h_c_bnd_i_jstrs * a_bnd_i_jstrs * (wsc_i_jstrs_npls + wsv_i_jstrs_npls)) \
        + c_air * rho_air * (
                               (v_reak_i_n + v_mec_vent_i_n) * theta_o_n
                               + np.sum(v_int_vent_i_istrs * theta_r_int_vent_i_istrs_n)
                       ) \
        + q_gen_i_n \
        + (c_cap_frnt_i / deta_t * theta_frnt_i_n + q_sol_frnt_i_n) / (c_cap_frnt_i / (deta_t * k_frnt_i) + 1.0)

    if operation_mode == OperationMode.STOP_OPEN:
        return brc_non_ntrv_i_n + c_air * rho_air * v_ntrl_vent_i * theta_o_n
    else:
        return brc_non_ntrv_i_n


# BRLの計算 式(7)
def get_BRL_i(Beta_i, WSB_i_k, A_i_k, hc_i_k_n):
    BRL = np.sum(A_i_k * hc_i_k_n * WSB_i_k) + Beta_i
    return np.repeat([BRL], 8760 * 4)


# Xot 式(8)
def get_Xot_i(Deno):
    return 1.0 / Deno


# XC 式(9)
def get_XC_i(Deno, Fot_i_k, kr_i, WSC_k, WSV_k):
    return kr_i * np.sum(Fot_i_k * (WSC_k + WSV_k)) / Deno


# XLr 式(10)
def get_XLr_i(Deno, Fot_i_k, kr_i, WSB_i_k):
    return kr_i * np.sum(Fot_i_k * WSB_i_k) / Deno


# Deno 式(11)
def get_Deno(Fot_i_k, kc_i, kr_i, WSR_i_k):
    return kc_i + kr_i * np.sum(Fot_i_k * WSR_i_k)


# kc_i 式(12)
def calc_kr_i():
    return a3.get_alpha_hm_r() / (a3.get_alpha_hm_r() + a3.get_alpha_hm_c())


# kc_i 式(13)
def calc_kc_i():
    return a3.get_alpha_hm_c() / (a3.get_alpha_hm_r() + a3.get_alpha_hm_c())


# ********** （1）式から作用温度、室除去熱量を計算する方法 **********

# TODO: 空調運転モード3,4については未定義


def calc_next_step(
        is_radiative_heating: bool, BRCot: float, BRMot: float, BRLot: float, Tset: float, Lrcap_i, operation_mode
) -> (float, float, float):

    # TODO 以下の式の定義を加えないといけない。
    is_radiative_cooling = False

    if operation_mode in [OperationMode.STOP_CLOSE, OperationMode.STOP_OPEN]:
        return BRCot / BRMot, 0.0, 0.0

    elif operation_mode == OperationMode.COOLING:

        if is_radiative_cooling:

            # 仮の冷房負荷を計算
            Lrs_temp = (BRMot * Tset - BRCot) / BRLot

            # 加熱量がプラス、つまり冷房負荷がマイナスの場合は自然室温計算をする。
            if Lrs_temp > 0.0:
                return BRCot / BRMot, 0.0, 0.0
            else:
                # TODO ここの最大の冷房処理能力の部分の変数はLrcap_iとなっているが別の変数で定義しないといけない。
                if Lrs_temp < Lrcap_i:
                    return Tset, BRMot * Tset - BRCot - Lrcap_i * BRLot, Lrcap_i
                else:
                    return Tset, 0.0, Lrs_temp

        else:
            # 仮の冷房負荷を計算
            Lcs_temp = BRMot * Tset - BRCot

            # 加熱量がプラス、つまり冷房負荷がマイナスの場合は自然室温計算をする。
            if Lcs_temp > 0.0:
                return BRCot / BRMot, 0.0, 0.0
            else:
                return Tset, Lcs_temp, 0.0

    elif operation_mode == OperationMode.HEATING:

        if is_radiative_heating:

            # 仮の暖房負荷を計算
            Lrs_temp = (BRMot * Tset - BRCot) / BRLot

            # 加熱量がマイナス、つまり暖房負荷がマイナスの場合は自然室温計算をする。
            if Lrs_temp < 0.0:
                return BRCot / BRMot, 0.0, 0.0
            else:
                if Lrs_temp > Lrcap_i:
                    return Tset, BRMot * Tset - BRCot - Lrcap_i * BRLot, Lrcap_i
                else:
                    return Tset, 0.0, Lrs_temp

        else:

            # 仮の暖房負荷を計算
            Lcs_temp = BRMot * Tset - BRCot

            # 加熱量がマイナス、つまり暖房負荷がマイナスの場合は自然室温計算をする。
            if Lcs_temp < 0.0:
                return BRCot / BRMot, 0.0, 0.0
            else:
                return Tset, Lcs_temp, 0.0

    else:
        ValueError()


def get_OT_without_ac(BRCot, BRMot):
    OT = BRCot / BRMot
    return OT


# 自然室温を計算 式(14)
def get_Tr_i_n(OT, Lrs, Xot, XLr, XC):
    return Xot * OT - XLr * Lrs - XC


# 家具の温度 式(15)
def get_Tfun_i_n(Capfun, Tfun_i_n_m1, Cfun, Tr, Qsolfun):
    """

    :param Capfun: i室の家具の熱容量（付録14．による） [J/K]
    :param Tfun_i_n_m1: i室の家具の15分前の温度 [℃]
    :param Cfun: i室の家具と室空気間の熱コンダクタンス（付録14．による）
    :param Tr: 室温 [℃]
    :param Qsolfun: i室のn時点における家具の日射吸収熱量 [W]
    :return: 家具の温度 [℃]
    """

    delta_t = a18.get_delta_t()

    if Capfun > 0.0:
        return (Capfun / delta_t * Tfun_i_n_m1 + Cfun * Tr + Qsolfun) / (Capfun / delta_t + Cfun)
    else:
        return 0.0


def get_Qfuns(Cfun, Tr, Tfun):
    """

    :param Cfun: i室の家具と室空気間の熱コンダクタンス（付録14．による）
    :param Tr:
    :param Tfun: i室の家具の温度 [℃]
    :return:
    """
    return Cfun * (Tr - Tfun)
