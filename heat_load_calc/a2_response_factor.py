import math
import numpy as np
from typing import List

import heat_load_calc.a25_window as a25

from heat_load_calc.s3_surface_loader import Boundary
from heat_load_calc.s3_surface_loader import InternalPartSpec
from heat_load_calc.s3_surface_loader import GeneralPartSpec
from heat_load_calc.s3_surface_loader import TransparentOpeningPartSpec
from heat_load_calc.s3_surface_loader import OpaqueOpeningPartSpec
from heat_load_calc.s3_surface_loader import GroundSpec
from heat_load_calc.initializer.boundary_type import BoundaryType

"""
付録2．応答係数の初項、指数項別応答係数、公比の計算
"""


class ResponseFactor:

    def __init__(self, rft0, rfa0, rft1, rfa1, row, n_root):
        self.rft0 = rft0
        self.rfa0 = rfa0
        self.rft1 = rft1
        self.rfa1 = rfa1
        self.row = row
        self.n_root = n_root



# ラプラス変数の設定
def get_laps(alp: np.ndarray) -> np.ndarray:
    """
    :param alp: 固定根
    :return: ラプラス変数の配列
    """
    n = len(alp) * 2  # 与えるラプラス変数の個数
    laps = [None] * n  # ラプラス変数の配列

    for i in range(1, n + 1):
        if i % 2 == 0:
            # 偶数番目はαをそのまま入力
            laps[i - 1] = alp[int((i - 1) / 2)]
        elif i == 1:
            # 最初はα1/√(α2/α1）とする
            laps[i - 1] = alp[0] / math.sqrt(alp[1] / alp[0])
        else:
            # それ以外は等比数列で補間
            lngL = math.ceil((i - 1) / 2)
            laps[i - 1] = alp[lngL] / math.sqrt(alp[lngL] / alp[lngL - 1])

    return np.array(laps)


def get_alpha_m(is_ground: bool) -> np.ndarray:
    """
    固定根を取得する。

    Args:
        is_ground: 熱容量を持つ外皮が地盤かどうか。（地盤でない場合は、一般部位または間仕切り）

    Returns:
        固定根
    """

    # 地盤の場合
    if is_ground:
        return np.array([
            1.05970E-09,
            4.23890E-09,
            1.69560E-08,
            6.78060E-08,
            2.71280E-07,
            1.08500E-06,
            4.34170E-06,
            1.73610E-05,
            6.94444E-05,
            2.77778E-04
        ])
    # 地盤以外の場合
    else:
        return np.array([
            2.0000E-06,
            7.9000E-06,
            3.1205E-05,
            1.2325E-04,
            4.8687E-04,
            1.9231E-03,
            7.5964E-03,
            3.0006E-02
        ])


# 壁体の単位応答の計算
def get_step_reps_of_wall(C_i_k_p, R_i_k_p, laps: List[float], alp: List[float], M: int):
    """
    :param layers: 壁体構成部材
    :param laps: ラプラス変数
    :param alp: 固定根
    :param nroot: 根の数
    :param M: 応答係数で作成する項数
    :param DTime: 計算時間間隔[s]
    :return:
    """

    # 四端子基本行列の初期化
    matFi = np.zeros((len(C_i_k_p), 2, 2))

    # 吸熱、貫流の各伝達関数ベクトルの初期化
    nlaps = len(laps)
    matGA = np.zeros((nlaps, 1))
    matGT = np.zeros((nlaps, 1))

    # 単位貫流応答、単位吸熱応答の初期化
    dblAT0 = 1.0
    dblAA0 = sum(R_i_k_p)

    # GA(0), GT(0)
    dblGA0 = dblAA0
    dblGT0 = dblAT0

    # 壁体の熱容量が0（定常）の場合
    # 定常部位であっても、そのまま処理を継続する（計算上は問題ないため）
    # if abs(dblCtotal) < 0.001:
    #    pass #　暫定処理（VBAではここで処理を抜ける）

    # 吸熱、貫流の各伝達関数ベクトルの作成
    for lngI in range(0, len(laps)):
        # 四端子行列の作成
        for lngK, (R_k, C_k) in enumerate(zip(R_i_k_p, C_i_k_p)):

            # ---- 四端子基本行列 matFi ----
            if abs(C_k) < 0.001:
                # 定常部位（空気層等）の場合
                matFi[lngK] = np.array([
                    [1.0, R_k],
                    [0.0, 1.0]
                ])
            else:
                # 非定常部位の場合
                dblTemp = math.sqrt(R_k * C_k * laps[lngI])
                dblCosh = np.cosh(dblTemp)
                dblSinh = np.sinh(dblTemp)

                matFi[lngK] = np.array([
                    [dblCosh, R_k / dblTemp * dblSinh],
                    [dblTemp / R_k * dblSinh, dblCosh]
                ])

            # print('[Fi(', lngK, ')]')
            # print(matFi)

            # ---- 四端子行列 matFt ----
            if lngK == 0:
                # 室内側1層目の場合は、四端子行列に四端子基本行列をコピーする
                matFt = np.copy(matFi[lngK])
            else:
                # 室内側2層目以降は、四端子基本行列を乗算
                matFt = np.dot(matFt, matFi[lngK])

        # print('martFt')
        # print(matFt)

        # 吸熱、貫流の各伝達関数ベクトルの作成
        matGA[lngI] = matFt[0, 1] / matFt[1, 1] - dblGA0
        matGT[lngI] = 1.0 / matFt[1][1] - dblGT0

    # print('matGA', matGA)
    # print('matGT', matGT)
    # 伝達関数の係数を求めるための左辺行列を作成
    nroot = len(alp)
    matF = np.zeros((nlaps, nroot))
    for lngI, laps in enumerate(laps):
        for lngJ, root in enumerate(alp):
            matF[lngI, lngJ] = laps / (laps + root)

    # 最小二乗法のための係数行列を作成
    # matU = np.zeros((self.__Nroot, self.__Nroot))
    # for lngK in range(self.__Nroot):
    #    for lngJ in range(self.__Nroot):
    #        matU[lngK, lngJ] = np.sum([matF[:, lngK] * matF[:, lngJ]])
    matU = np.dot(matF.T, matF)

    # 最小二乗法のための定数項行列を作成
    matCA = np.zeros((nroot, 1))
    matCT = np.zeros((nroot, 1))
    matCA[:, 0] = np.sum([matF * matGA], axis=1)
    matCT[:, 0] = np.sum([matF * matGT], axis=1)

    # 最小二乗法のための係数行列の逆行列を計算
    matU_inv = np.linalg.inv(matU)

    # 伝達関数の係数を計算
    matAA = np.dot(matU_inv, matCA)
    matAT = np.dot(matU_inv, matCT)

    # 伝達関数の係数を一次元配列に変換
    dblAT = matAT[:, 0]
    dblAA = matAA[:, 0]

    # 単位応答を計算
    dblATstep = np.zeros(M)
    dblAAstep = np.zeros(M)
    for lngJ in range(M):
        dblATstep[lngJ] = dblAT0
        dblAAstep[lngJ] = dblAA0
        for lngK, root in enumerate(alp):
            dblATstep[lngJ] = dblATstep[lngJ] + dblAT[lngK] * math.exp(-root * lngJ * 900)
            dblAAstep[lngJ] = dblAAstep[lngJ] + dblAA[lngK] * math.exp(-root * lngJ * 900)

    # デバッグ用
    # print('四端子基本行列：', matFi)
    # print('四端子行列：', matFt)
    # print('貫流伝達関数ベクトル：', matGA)
    # print('吸熱伝達関数ベクトル：', matGT)
    # print('伝達関数の係数を求めるための左辺行列：', matF)
    # print('最小二乗法のための係数行列：', matU)
    # print('最小二乗法のための係数行列の逆行列：', matU_inv)
    # print('貫流定数項行列：', matCT)
    # print('吸熱定数項行列：', matCA)
    # print('貫流伝達関数の係数：', dblAT)
    # print('吸熱伝達関数の係数：', dblAA)
    # print('単位貫流応答：', dblATstep[:11])
    # print('単位吸熱応答：', dblAAstep[:11])

    return dblAT0, dblAA0, dblAT, dblAA, dblATstep, dblAAstep


# 二等辺三角波励振の応答係数、指数項別応答係数、公比の計算
def get_RFTRI(alp, AT0, AA0, AT, AA, M):
    # 二等辺三角波励振の応答係数の配列を初期化
    dblRFT = np.zeros(M)
    dblRFA = np.zeros(M)

    # 二等辺三角波励振の応答係数の初項を計算
    dblTemp = np.array(alp) * 900
    dblE1 = (1.0 - np.exp(-dblTemp)) / dblTemp
    dblRFT[0] = AT0 + np.sum(dblE1 * AT)
    dblRFA[0] = AA0 + np.sum(dblE1 * AA)

    # 二等辺三角波励振の応答係数の二項目以降を計算
    for lngJ in range(1, M):
        dblE1 = (1.0 - np.exp(-dblTemp)) ** 2.0 * np.exp(-(float(lngJ) - 1.0) * dblTemp) / dblTemp
        dblRFT[lngJ] = (-1.0) * np.sum(dblE1 * AT)
        dblRFA[lngJ] = (-1.0) * np.sum(dblE1 * AA)

    # 指数項別応答係数、公比を計算
    dblE1 = 1.0 / dblTemp * (1.0 - np.exp(-dblTemp)) ** 2.0
    dblRFT1 = - AT * dblE1
    dblRFA1 = - AA * dblE1
    dblRow = np.exp(-dblTemp)

    # デバッグ用
    # print('貫流応答係数：', dblRFT[:11])
    # print('吸熱応答係数：', dblRFA[:11])
    # print('指数項別貫流応答係数：', dblRFT1)
    # print('指数項別吸熱応答係数：', dblRFA1)
    # print('公比：', dblRow)

    return dblRFT, dblRFA, dblRFT1, dblRFA1, dblRow


# 応答係数
def calc_response_factor(is_ground: bool, C_i_k_p, R_i_k_p):
    """
    VBAからの主な変更点：
    (1)二次元配列（objArray）で壁体の情報を受け取っていたが、壁体情報クラスで受け取るように変更
    (2)lngStRow, lngOutputColは削除
    (3)固定根はシートから読み込んでいたが、初期化時に配列として与えるように変更
    (4)伝達関数近似のA0の周期は使用しない
    :param WallType: 壁体種類, 'wall' or 'soil'
    :param DTime: 計算時間間隔[s]
    :param wall: 壁体基本情報クラス
    """

    NcalTime = 50  # 応答係数を作成する時間数[h]
    M = int(NcalTime * 3600 / 900) + 1  # 応答係数で作成する項数

    # 固定根, 一般部位の場合[8], 地盤の場合[10]
    alpha_m = get_alpha_m(is_ground)

    # ラプラス変数の設定
    laps = get_laps(alpha_m)

    # 単位応答の計算
    AT0, AA0, AT, AA, ATstep, AAstep = get_step_reps_of_wall(C_i_k_p, R_i_k_p, laps, alpha_m, M)

    # 二等辺三角波励振の応答係数、指数項別応答係数、公比の計算
    RFT, RFA, RFT1, RFA1, Row = get_RFTRI(alpha_m, AT0, AA0, AT, AA, M)

    RFT0 = RFT[0]  # 貫流応答係数の初項
    RFA0 = RFA[0]  # 吸熱応答係数の初項
    Nroot = len(alpha_m)  # 根の数

    RFT1_12 = np.zeros(12)
    RFA1_12 = np.zeros(12)
    Row_12 = np.zeros(12)
    RFT1_12[:len(RFT1)] = RFT1
    RFA1_12[:len(RFA1)] = RFA1
    Row_12[:len(Row)] = Row

    return RFT0, RFA0, RFT1_12, RFA1_12, Row_12, Nroot


def get_c_layer_i_k_ls(b: Boundary):

    if type(b.spec) is InternalPartSpec:
        c = [layer.thermal_capacity for layer in b.spec.layers]
        c.append(0.0)
        return np.array(c) * 1000.0
    elif type(b.spec) is GeneralPartSpec:
        c = [layer.thermal_capacity for layer in b.spec.layers]
        c.append(0.0)
        return np.array(c) * 1000.0
    elif type(b.spec) is TransparentOpeningPartSpec:
        return None
    elif type(b.spec) is OpaqueOpeningPartSpec:
        return None
    elif type(b.spec) is GroundSpec:
        c = [layer.thermal_capacity for layer in b.spec.layers]
        c.append(3300.0 * 3.0)
        return np.array(c) * 1000.0
    else:
        raise TypeError


def get_r_layer_i_k_ls(b):
    if type(b.spec) is InternalPartSpec:
        r = [layer.thermal_resistance for layer in b.spec.layers]
        r.append(b.spec.outside_heat_transfer_resistance)
        return np.array(r)
    elif type(b.spec) is GeneralPartSpec:
        r = [layer.thermal_resistance for layer in b.spec.layers]
        r.append(b.spec.outside_heat_transfer_resistance)
        return np.array(r)
    elif type(b.spec) is TransparentOpeningPartSpec:
        return None
    elif type(b.spec) is OpaqueOpeningPartSpec:
        return None
    elif type(b.spec) is GroundSpec:
        r = [layer.thermal_resistance for layer in b.spec.layers]
        r.append(3.0 / 1.0)
        return np.array(r)
    else:
        raise TypeError


def get_response_factors(b: Boundary) -> ResponseFactor:

    if b.boundary_type in [BoundaryType.ExternalGeneralPart, BoundaryType.Internal, BoundaryType.Ground]:

        is_ground = b.boundary_type == BoundaryType.Ground

        c_layer_i_k_l = get_c_layer_i_k_ls(b)
        r_layer_i_k_l = get_r_layer_i_k_ls(b)

        # 応答係数
        _RFT0, _RFA0, _RFT1, _RFA1, _Row, _n_root_i_js = \
            calc_response_factor(is_ground, c_layer_i_k_l, r_layer_i_k_l)

    elif b.boundary_type in [BoundaryType.ExternalTransparentPart, BoundaryType.ExternalOpaquePart]:

        # 室iの境界kの熱貫流率, W/m2K
        # 定常で解く部位、つまり、透明な開口部・不透明な開口部で定義される。

        # 室iの境界kの室内側熱伝達抵抗, m2K/W
        # 室内側熱伝達抵抗は全ての part 種類において存在する
        # 従って下記のコードは少し冗長であるがspecの1階層下で定義されているため、念の為かき分けておく。

        # 開口部の室内表面から屋外までの熱貫流率[W / (m2･K)] 式(124)
        _Uso = a25.get_Uso(u_w=b.spec.u_value, r_i_i_k_n=b.spec.inside_heat_transfer_resistance)

        _RFT0, _RFA0, _RFT1, _RFA1, _Row, _n_root_i_js = \
            1.0, 1.0 / _Uso, np.zeros(12), np.zeros(12), np.zeros(12), 0

    else:

        raise ValueError()

    return ResponseFactor(rft0=_RFT0, rfa0=_RFA0, rft1=_RFT1, rfa1=_RFA1, row=_Row, n_root=_n_root_i_js)


