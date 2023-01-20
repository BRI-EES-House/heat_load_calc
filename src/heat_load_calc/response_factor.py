"""応答係数の初項、指数項別応答係数、公比の計算

"""

import math
import numpy as np
from typing import List, Dict


class ResponseFactor:

    # 根の数
    n_root = 12

    def __init__(self, rft0: float, rfa0: float, rft1: np.ndarray, rfa1: np.ndarray, row: np.ndarray):
        """イニシャライザ

        Args:
            rft0: 貫流応答係数の初項
            rfa0: 吸熱応答係数の初項
            rft1: 貫流応答係数
            rfa1: 吸熱応答係数
            row: 公比
        """

        self._rft0 = rft0
        self._rfa0 = rfa0
        self._rft1 = rft1
        self._rfa1 = rfa1
        self._row = row

    @property
    def rft0(self):
        return self._rft0

    @property
    def rfa0(self):
        return self._rfa0

    @property
    def rft1(self):
        return self._rft1

    @property
    def rfa1(self):
        return self._rfa1

    @property
    def row(self):
        return self._row

    @classmethod
    def create_for_steady(cls, u_w: float, r_i: float):
        """

        Args:
            u_w: 熱貫流率, W/m2K
            r_i: 室内側（総合）熱伝達抵抗, m2K/W

        Returns:
            応答係数
        """

        # 開口部の室内表面から屋外までの熱コンダクタンス, W/m2K
        u_so = 1.0 / (1.0 / u_w - r_i)

        return ResponseFactor(
            rft0=1.0,
            rfa0=1.0 / u_so,
            rft1=np.zeros(cls.n_root, dtype=float),
            rfa1=np.zeros(cls.n_root, dtype=float),
            row=np.zeros(cls.n_root, dtype=float)
        )

    @classmethod
    def create_for_unsteady_not_ground(cls, cs: np.ndarray, rs: np.ndarray, r_o: float):
        """応答係数を作成する（地盤以外に用いる）

        裏面に、熱抵抗をもち、熱容量は 0.0 の層を追加する。
        Args:
            cs: 単位面積あたりの熱容量, kJ/m2K, [layer数]
            rs: 熱抵抗, m2K/W, [layer数]
            r_o: 室外側熱伝達抵抗, m2K/W

        Returns:
            応答係数
        """

        # 裏面に熱容量 0.0 、熱抵抗 r_o の層を加える。
        cs = np.append(cs, 0.0)
        rs = np.append(rs, r_o)

        # 単位変換 kJ/m2K -> J/m2K
        cs = cs * 1000.0

        # 応答係数
        frt0, rfa0, rft1, rfa1, row = calc_response_factor_non_residential(C_i_k_p=cs, R_i_k_p=rs)

        return ResponseFactor(rft0=frt0, rfa0=rfa0, rft1=rft1, rfa1=rfa1, row=row)

    @classmethod
    def create_for_unsteady_ground(cls, cs: np.ndarray, rs: np.ndarray):
        """応答係数を作成する（地盤用）

        地盤層を追加する。
        Args:
            cs: 単位面積あたりの熱容量, kJ/m2K, [layer数]
            rs: 熱抵抗, m2K/W, [layer数]

        Returns:
            応答係数
        """

        # 裏面に地盤の層を加える。
        cs = np.append(cs, 3300.0 * 3.0)
        rs = np.append(rs, 3.0 / 1.0)

        # 単位変換 kJ/m2K -> J/m2K
        cs = cs * 1000.0

        # 応答係数
        rft0, rfa0, rft1, rfa1, row = calc_response_factor(is_ground=True, cs=cs, rs=rs)

        # 貫流応答係数の上書
        # 土壌の計算は吸熱応答のみで計算するため、畳み込み積分に必要な指数項別応答係数はすべて０にする
        # 貫流応答の初項は年平均気温掛かる係数であることから１とし、計算された貫流応答係数をすべて上書きする
        rft0 = 1.0
        rft1 = np.zeros(12)

        return ResponseFactor(rft0=rft0, rfa0=rfa0, rft1=rft1, rfa1=rfa1, row=row)


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
            1.05699306612549E-08,
            3.27447457677204E-08,
            1.01440436059147E-07,
            3.14253839100315E-07,
            9.73531652917036E-07,
            3.01591822058485E-06,
            9.34305801562961E-06,
            0.0000289439987091205,
            0.0000896660450863221,
            0.000277777777777778
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
    for lngI, lap in enumerate(laps):
        for lngJ, root in enumerate(alp):
            matF[lngI, lngJ] = lap / (lap + root)

    # 最小二乗法のための係数行列を作成
    # matU = np.zeros((nroot, nroot))
    # for lngK in range(nroot):
    #    for lngJ in range(nroot):
    #         matU[lngK, lngJ] = np.sum([matF[:, lngK] * matF[:, lngJ]])
    matU = np.dot(matF.T, matF)

    # 最小二乗法のための定数項行列を作成
    matCA = np.zeros((nroot, 1))
    matCT = np.zeros((nroot, 1))
    matCA[:, 0] = np.sum([matF * matGA], axis=1)
    matCT[:, 0] = np.sum([matF * matGT], axis=1)

    # 伝達関数の係数を計算
    matAA = np.linalg.solve(matU, matCA)
    matAT = np.linalg.solve(matU, matCT)

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


# 伝達関数の計算
def calc_transfer_function(C_i_k_p: List[float], R_i_k_p: List[float], laps: float) -> (float, float):

    """

    Args:
        C_i_k_p: 層の熱容量[J/m2K]
        R_i_k_p: 層の熱抵抗[m2K/W]
        laps: ラプラス変数[1/s]

    Returns:
        貫流伝達関数[K]
        吸熱伝達関数[K]
    """

    # 四端子行列の初期化
    matFt = np.identity(2, dtype=float)

    for lngK, (R_k, C_k) in enumerate(zip(R_i_k_p, C_i_k_p)):

        # ---- 四端子基本行列 matFi ----
        if abs(C_k) < 0.001:
            # 定常部位（空気層等）の場合
            matFi = np.array([
                [1.0, R_k],
                [0.0, 1.0]
            ])
        else:
            # 非定常部位の場合
            dblTemp = math.sqrt(R_k * C_k * laps)
            dblCosh = np.cosh(dblTemp)
            dblSinh = np.sinh(dblTemp)

            matFi = np.array([
                [dblCosh, R_k / dblTemp * dblSinh],
                [dblTemp / R_k * dblSinh, dblCosh]
            ])

        # print('[Fi(', lngK, ')]')
        # print(matFi)

        # ---- 四端子行列 matFt ----
        matFt = np.dot(matFt, matFi)

    # print('martFt')
    # print(matFt)

    # 吸熱、貫流の各伝達関数ベクトルの作成
    GA = matFt[0, 1] / matFt[1, 1]
    GT = 1.0 / matFt[1][1]

    return (GA, GT)


# 壁体の単位応答の計算（非住宅向け重み付き最小二乗法適用）
def get_step_reps_of_wall_weighted(C_i_k_p, R_i_k_p, laps: List[float], alp: List[float], M: int):
    """
    重み付き最小二乗法の適用
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
    matFt = np.identity(2, dtype=float)
    for lngI, lap in enumerate(laps):

        # 伝達関数の計算
        (GA, GT) = calc_transfer_function(C_i_k_p=C_i_k_p, R_i_k_p=R_i_k_p, laps=lap)

        # 吸熱、貫流の各伝達関数ベクトルの作成
        matGA[lngI] = GA - dblGA0
        matGT[lngI] = GT - dblGT0

    # print('matGA', matGA)
    # print('matGT', matGT)
    # 伝達関数の係数を求めるための左辺行列を作成
    nroot = len(alp)
    matF = np.zeros((nlaps, nroot))
    for lngI, lap in enumerate(laps):
        for lngJ, root in enumerate(alp):
            matF[lngI, lngJ] = lap / (lap + root)

    # 最小二乗法のための係数行列を作成
    matU = np.zeros((nroot, nroot))
    for lngK in range(nroot):
       for lngJ in range(nroot):
           for lngI in range(nlaps):
               matU[lngK, lngJ] += np.power(laps[lngI], 2.0) * matF[lngI, lngK] * matF[lngI, lngJ]
    # matU = np.dot(matF.T, matF)

    # 最小二乗法のための定数項行列を作成
    matCA = np.zeros((nroot, 1))
    matCT = np.zeros((nroot, 1))
    for lngK in range(nroot):
        for lngI in range(nlaps):
            matCA[lngK, 0] += laps[lngI] ** 2.0 * matF[lngI, lngK] * matGA[lngI, 0]
            matCT[lngK, 0] += laps[lngI] ** 2.0 * matF[lngI, lngK] * matGT[lngI, 0]

    # 伝達関数の係数を計算
    matAA = np.linalg.solve(matU, matCA)
    matAT = np.linalg.solve(matU, matCT)

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
def calc_response_factor(is_ground: bool, cs, rs):
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
    AT0, AA0, AT, AA, ATstep, AAstep = get_step_reps_of_wall(cs, rs, laps, alpha_m, M)

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

    return RFT0, RFA0, RFT1_12, RFA1_12, Row_12


# 応答係数（非住宅用　住宅との相違は固定根と重み付き最小二乗法を使用する点）
def calc_response_factor_non_residential(C_i_k_p, R_i_k_p):
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

    # 固定根, 初稿 1/(86400*365)、終項 1/600、項数 10
    alpha_m = np.logspace(np.log10(1.0 / (86400.0 * 365.0)), np.log10(1.0 / 600.0), 10)

    # ラプラス変数の設定
    laps = get_laps(alpha_m)

    # 単位応答の計算
    AT0, AA0, AT, AA, ATstep, AAstep = get_step_reps_of_wall_weighted(C_i_k_p, R_i_k_p, laps, alpha_m, M)

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

    return RFT0, RFA0, RFT1_12, RFA1_12, Row_12

if __name__ == '__main__':

    C = np.array([
        10375.0,
        0.0,
        10375.0,
        0.0
    ])

    R = np.array([
        0.0568,
        0.09,
        0.0568,
        0.120289612356129
    ])

    print(calc_transfer_function(C, R, 1.0 / (900)))
