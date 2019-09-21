import numpy as np
import apdx3_human_body as a3
import a18_initial_value_constants as a18


# ********** 4.1 顕熱 **********

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
    ca = a18.get_ca()
    rhoa = a18.get_rhoa()

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


# 室温・負荷計算の定数項BRCを計算する 式(6)
def get_BRC_i(WSC_i_k, WSV_i_k, area, hc_i_k_n, Ta, Hn, Ventset, Infset, LocalVentset, Hcap, oldTr, Cap_fun_i, C_fun_i,
              Qsolfun, oldTfun, Vnext_i_j, Tr_next_i_j_nm1):
    ca = a18.get_ca()
    rhoa = a18.get_rhoa()

    BRC = np.sum(WSC_i_k * area * hc_i_k_n) \
          + ca * rhoa * (Ventset + Infset + LocalVentset) * Ta / 3600.0 \
          + ca * rhoa * np.sum(Vnext_i_j * Tr_next_i_j_nm1) / 3600.0 \
          + Hcap / 900 * oldTr \
          + ((Cap_fun_i / 900 * oldTfun + Qsolfun) / (Cap_fun_i / (900 * C_fun_i) + 1.) if Cap_fun_i > 0.0 else 0.0) \
          + np.sum(area * hc_i_k_n * WSV_i_k) \
          + Hn
    return BRC


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

# 作用温度、室除去熱量の計算ルーティン
def calc_heatload(ac_mode: int, is_radiative_heating: bool, BRCot: float, BRMot: float, BRLot: float,
                  Lrcap: float, Tset: float) -> (float, float, float):
    """

    :param ac_mode:
    :param is_radiative_heating:
    :param BRCot:
    :param BRMot:
    :param BRLot:
    :param Lrcap:
    :param Tset:
    :return: 室温、対流空調熱負荷、放射空調熱負荷を返す
    """

    # 非空調時の室温計算
    if ac_mode == 0:
        Lrs = 0.0
        Lcs = 0.0
        OT = get_OT_natural(BRCot, BRMot)

    # 熱負荷計算（能力無制限）
    elif ac_mode == 1 or ac_mode == -1 or ac_mode == 4:
        # 対流式空調の場合
        if (is_radiative_heating is not True) or (is_radiative_heating and ac_mode < 0):
            Lrs = 0.0
            Lcs = BRMot * Tset - BRCot
        # 放射式空調
        else:
            Lcs = 0.0
            Lrs = (BRMot * Tset - BRCot) / BRLot
        # 室温の計算
        OT = (BRCot + Lcs + BRLot * Lrs) / BRMot

    # 放射暖房最大能力運転（当面は暖房のみ）
    elif ac_mode == 3 and Lrcap > 0.0:
        Lrs = Lrcap
        # 室温は対流式で維持する
        Lcs = BRMot * Tset - BRCot - Lrs * BRLot
        # 室温の計算
        OT = (BRCot + Lcs + BRLot * Lrs) / BRMot

    else:
        Lrs = 0.0
        Lcs = 0.0
        OT = get_OT_natural(BRCot, BRMot)

    return (OT, Lcs, Lrs)


def get_OT_natural(BRCot, BRMot):
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
