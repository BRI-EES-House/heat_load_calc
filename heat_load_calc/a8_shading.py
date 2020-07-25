import numpy as np
from collections import namedtuple
from typing import Dict

import heat_load_calc.x_19_external_boundaries_direction as x_19


"""
付録8．ひさしの影面積の計算
"""


class SolarShadingPart:

    def __init__(self, existence, input_method, depth, d_h, d_e, x1, x2, x3, y1, y2, y3, z_x_pls, z_x_mns, z_y_pls, z_y_mns):

        self.existence = existence
        self.input_method = input_method
        self.depth = depth
        self.d_h = d_h
        self.d_e = d_e
        self.x1 = x1
        self.x2 = x2
        self.x3 = x3
        self.y1 = y1
        self.y2 = y2
        self.y3 = y3
        self.z_x_pls = z_x_pls
        self.z_x_mns = z_x_mns
        self.z_y_pls = z_y_pls
        self.z_y_mns = z_y_mns



def get_solar_shading_part(ssp: Dict) -> SolarShadingPart:
    """
    入力ファイルの辞書の'solar_shading_part'を読み込む。

    Args:
        ssp: 'solar shading part' の辞書

    Returns:
        SolarShadingPart クラス
    """

    existence = ssp['existence']

    if existence:

        input_method = ssp['input_method']

        if ssp['input_method'] == 'simple':

            return SolarShadingPart(
                existence=existence,
                input_method=input_method,
                depth=ssp['depth'],
                d_h=ssp['d_h'],
                d_e=ssp['d_e'],
                x1=None,
                x2=None,
                x3=None,
                y1=None,
                y2=None,
                y3=None,
                z_x_pls=None,
                z_x_mns=None,
                z_y_pls=None,
                z_y_mns=None
            )

        elif ssp['input_method'] == 'detail':

            return SolarShadingPart(
                existence=existence,
                input_method=input_method,
                depth=None,
                d_h=None,
                d_e=None,
                x1=ssp['x1'],
                x2=ssp['x2'],
                x3=ssp['x3'],
                y1=ssp['y1'],
                y2=ssp['y2'],
                y3=ssp['y3'],
                z_x_pls=ssp['z_x_pls'],
                z_x_mns=ssp['z_x_mns'],
                z_y_pls=ssp['z_y_pls'],
                z_y_mns=ssp['z_y_mns']
            )

        else:
            raise ValueError()

    else:

        return SolarShadingPart(
            existence=existence,
            input_method=None,
            depth=None,
            d_h=None,
            d_e=None,
            x1=None,
            x2=None,
            x3=None,
            y1=None,
            y2=None,
            y3=None,
            z_x_pls=None,
            z_x_mns=None,
            z_y_pls=None,
            z_y_mns=None
        )


def get_FSDW_i_k_n2(h_sun_n, a_sun_n, direction_i_ks: str, solar_shading_part_i_ks):

    # 室iの境界kの傾斜面の方位角, rad
    # 室iの境界kの傾斜面の傾斜角, rad
    w_alpha_i_k, _ = x_19.get_w_alpha_i_j_w_beta_i_j(direction_i_j=direction_i_ks)

    ###################################################################################
    h_s = np.where(h_sun_n > 0.0, h_sun_n, 0.0)
    a_s = np.where(h_sun_n > 0.0, a_sun_n, 0.0)
    # 日除けの日影面積率の計算
    if solar_shading_part_i_ks.existence:
        if solar_shading_part_i_ks.input_method == 'simple':


            return calc_F_SDW_i_k_n(
                D_i_k=solar_shading_part_i_ks.depth,  # 出幅
                d_e=solar_shading_part_i_ks.d_e,  # 窓の上端から庇までの距離
                d_h=solar_shading_part_i_ks.d_h,  # 窓の高さ
                a_s_n=a_s,
                h_s_n=h_s,
                Wa_i_k=w_alpha_i_k
            )
        elif solar_shading_part_i_ks.input_method == 'detailed':
            raise NotImplementedError()
        else:
            raise ValueError
    else:
        return np.full(len(h_sun_n), 1.0)


# 日除けの影面積を計算する（当面、簡易入力のみに対応）式(79)
def calc_F_SDW_i_k_n(D_i_k: float, d_e: float, d_h: float, a_s_n: np.ndarray, h_s_n: np.ndarray, Wa_i_k: float) -> np.ndarray:
    """
    :param D_i_k: 出幅 [m]
    :param d_e: 窓の上端から庇までの距離 [m]
    :param d_h: 窓の高さ [m]
    :param a_s_n: 太陽方位角 [rad]
    :param h_s_n: 太陽高度 [rad]
    :param Wa_i_k: 庇の設置してある窓の傾斜面方位角[rad]
    :return: 日除けの影面積比率 [-]
    """

    # DPの計算[m] 式(83)
    D_P_i_k = get_D_P_i_k(D_i_k, h_s_n, a_s_n, Wa_i_k)

    # DH'の計算[m] 式(82)
    D_H_dash_i_k = get_D_H_dash_i_k(d_e, D_P_i_k)

    # DHの計算[m] 式(81)
    DH_i_k = get_D_H_i_k(d_h, D_H_dash_i_k)

    # 日影面積率の計算 式(79)
    F_SDW_i_k = get_F_SDW_i_k(d_h, DH_i_k, h_s_n)

    return F_SDW_i_k


# 日影面積率 式(79)
def get_F_SDW_i_k(d_h, DH, h_s_n):
    """
    :param d_h: 窓の高さ [m]
    :param DH:
    :return:
    """
    F_SDW_i_k = DH / d_h

    # 日が出ていないときは0
    F_SDW_i_k[h_s_n <= 0] = 0.0

    return F_SDW_i_k


# 式(80)
def get_A_SDW_i_k(W_R_i_k, D_H_i_k):
    return W_R_i_k * D_H_i_k

# 式(81)
def get_D_H_i_k(d_h, DH_dash):
    """
    :param d_h: 窓の高さ [m]
    :param DH_dash:
    :return:
    """
    return np.clip(DH_dash, 0.0, d_h)


# 式(82)
def get_D_H_dash_i_k(d_e, DP):
    """
    :param d_e: 窓の上端から庇までの距離 [m]
    :param DP: DP
    :return:
    """
    return DP - d_e

# 式(83)
def get_D_P_i_k(D_i_k, h_s, a_s, Wa):
    """
    :param D_i_k: 出幅 [m]
    :param d_h: 窓の高さ [m]
    :param a_s: 太陽方位角 [rad]
    :param Wa: 庇の設置してある窓の傾斜面方位角[rad]
    :return:
    """
    # γの計算[rad]
    gamma = a_s - Wa

    # tan(プロファイル角)の計算
    tan_fai = np.tan(h_s) / np.cos(gamma)

    DP = D_i_k * tan_fai
    return DP


