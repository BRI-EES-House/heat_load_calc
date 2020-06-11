import numpy as np

import apdx3_human_body as a3
import a18_initial_value_constants as a18
from a39_global_parameters import OperationMode


# ********** （1）式から作用温度、室除去熱量を計算する方法 **********

# TODO: 空調運転モード3,4については未定義


def calc_next_steps(is_radiative_heating_is, BRCot_is, BRMot_is, BRLot_is, OTsets, lrcap_is, operation_mode_is_n):

    return np.vectorize(calc_next_step)(is_radiative_heating_is, BRCot_is,  BRMot_is, BRLot_is, OTsets, lrcap_is, operation_mode_is_n)

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

#    if Capfun > 0.0:
#        return (Capfun / delta_t * Tfun_i_n_m1 + Cfun * Tr + Qsolfun) / (Capfun / delta_t + Cfun)
#    else:
#        return 0.0
    return np.where(Capfun > 0.0, (Capfun / delta_t * Tfun_i_n_m1 + Cfun * Tr + Qsolfun) / (Capfun / delta_t + Cfun), 0.0)


def get_Qfuns(Cfun, Tr, Tfun):
    """

    :param Cfun: i室の家具と室空気間の熱コンダクタンス（付録14．による）
    :param Tr:
    :param Tfun: i室の家具の温度 [℃]
    :return:
    """
    return Cfun[:, np.newaxis] * (Tr - Tfun)
