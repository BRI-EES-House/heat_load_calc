import numpy as np
import apdx3_human_body as a3
from common import conca, conrowa

# ********** 4.1 顕熱 **********

# 作用温度設定用係数への換算
def calc_OT_coeff(BRC, BRM, matWSV, matWSC, fot, matWSR, matWSB, kc, kr, BRL):
    # Deno 式(11)
    Deno = get_Deno(fot, kc, kr, matWSR)

    # XLr 式(10)
    XLr = get_XLr(Deno, fot, kr, matWSB)

    # XC 式(9)
    XC = get_XC(Deno, fot, kr, matWSC, matWSV)

    # Xot 式(8)
    Xot = get_Xot(Deno)

    # BRMot 式(2)
    BRMot = get_BRMot(BRM, Xot)

    # BRCot 式(3)
    BRCot = get_BRCot(BRC, BRM, XC)

    # BRLot 式(4)
    BRLot = get_BRLot(BRL, BRM, XLr)

    return BRMot, BRLot, BRCot, Xot, XLr, XC


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
def get_BRM(Hcap, matWSR, Capfun, Cfun, Vent, local_vent_amount_schedule, A_i_k, hic, V_nxt):
    # 第1項
    BRM_0 = Hcap / 900

    # 第2項
    BRM_0 += np.sum(A_i_k * hic * (1.0 - matWSR))

    # 空間換気
    BRM_0 += np.sum(conca * conrowa * V_nxt / 3600.0)

    # 家具からの熱取得
    BRM_0 += 1. / (900 / Capfun + 1. / Cfun) if Capfun > 0.0 else 0.0

    # 外気導入項の計算（3項目の0.0はすきま風量）
    # ※ここで、BRMがスカラー値(BRM_0)から1時間ごとの1次元配列(BRM_h)へ
    BRM_h = BRM_0 + conca * conrowa * (Vent + 0.0 + np.array(local_vent_amount_schedule)) / 3600.0

    # 1時間当たり4ステップなので、配列を4倍に拡張
    BRM = np.repeat(BRM_h, 4)

    return BRM


# 室温・負荷計算の定数項BRCを計算する 式(6)
def get_BRC(matWSC, matWSV, area, hic, Ta, Hn, Ventset, Infset, LocalVentset, Hcap, oldTr, Capfun, Cfun,
            Qsolfun, oldTfun, nextroom_volume, nextroom_oldTr):
    BRC = np.sum(matWSC * area * hic) \
        + conca * conrowa * (Ventset + Infset + LocalVentset) * Ta / 3600.0 \
        + conca * conrowa * np.sum(nextroom_volume * nextroom_oldTr) / 3600.0 \
        + Hcap / 900 * oldTr \
        + ((Capfun / 900 * oldTfun + Qsolfun) / (Capfun / (900 * Cfun) + 1.) if Capfun > 0.0 else 0.0) \
        + np.sum(area * hic * matWSV) \
        + Hn
    return BRC


# BRLの計算 式(7)
def get_BRL(Beta, matWSB, A_i_k, hic):
    BRL = np.sum(A_i_k * hic * matWSB) + Beta
    return np.repeat([BRL], 8760 * 4)


# Xot 式(8)
def get_Xot(Deno):
    return 1.0 / Deno


# XC 式(9)
def get_XC(Deno, fot, kr, matWSC, matWSV):
    return kr * np.sum(fot * (matWSC + matWSV)) / Deno


# XLr 式(10)
def get_XLr(Deno, fot, kr, matWSB):
    return kr * np.sum(fot * matWSB) / Deno


# Deno 式(11)
def get_Deno(fot, kc, kr, matWSR):
    return kc + kr * np.sum(fot * matWSR)


# kc 式(12)
def calc_kr():
    return a3.get_alpha_hm_r() / (a3.get_alpha_hm_r() + a3.get_alpha_hm_c())


# kc 式(13)
def calc_kc():
    return a3.get_alpha_hm_c() / (a3.get_alpha_hm_r() + a3.get_alpha_hm_c())


# 自然室温を計算 式(14)
def get_Tr(Lrs, OT, Xot, XLr, XC):
    return Xot * OT - XLr * Lrs - XC


# 家具の温度を計算する 式(15)
def calcTfun(Capfun, oldTfun, Cfun, Tr, Qsolfun):
    """

    :param Capfun: i室の家具の熱容量（付録14．による） [J/K]
    :param oldTfun: i室の家具の15分前の温度 [℃]
    :param Cfun: i室の家具と室空気間の熱コンダクタンス（付録14．による）
    :param Tr:
    :param Qsolfun: i室のn時点における家具の日射吸収熱量 [W]
    :return: i室の家具の温度 [℃]
    """
    Tfun = get_Tfun(Capfun, oldTfun, Cfun, Tr, Qsolfun)
    Qfuns = get_Qfuns(Cfun, Tr, Tfun)

    return Tfun, Qfuns



# 家具の温度 式(15)
def get_Tfun(Capfun, oldTfun, Cfun, Tr, Qsolfun):
    """

    :param Capfun: i室の家具の熱容量（付録14．による） [J/K]
    :param oldTfun: i室の家具の15分前の温度 [℃]
    :param Cfun: i室の家具と室空気間の熱コンダクタンス（付録14．による）
    :param Tr:
    :param Qsolfun: i室のn時点における家具の日射吸収熱量 [W]
    :return:
    """
    return (((Capfun / 900 * oldTfun
                   + Cfun * Tr + Qsolfun)
                  / (Capfun / 900 + Cfun)))


def get_Qfuns(Cfun, Tr, Tfun):
    """

    :param Cfun: i室の家具と室空気間の熱コンダクタンス（付録14．による）
    :param Tr:
    :param Tfun: i室の家具の温度 [℃]
    :return:
    """
    return Cfun * (Tr - Tfun)