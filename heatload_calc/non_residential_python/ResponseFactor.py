import math
import numpy as np
from Wall import Wall, Layer
from typing import List
# import matplotlib.pyplot as plt

# ラプラス変数の設定
def get_laps(alp: List[float]) -> List[float]:
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

    return laps


# 固定根の取得
def get_alps(wall_type: str) -> List[float]:
    if wall_type == 'wall':
        return [
            0.000002,
            0.0000079,
            0.000031205,
            0.00012325975,
            0.0004868760125,
            0.001923160249375,
            0.00759648298503125,
            0.0300061077908735
        ]
    elif wall_type == 'soil':
        return [
            1.0597E-09,
            4.2389E-09,
            1.6956E-08,
            6.7806E-08,
            2.7128E-07,
            1.0850E-06,
            4.3417E-06,
            1.7361E-05,
            6.94444E-05,
            0.000277778
        ]
    else:
        raise ValueError('指定されたWallType[{}]の固定根は定義されていません'.format(wall_type))


# 壁体の単位応答の計算
def get_step_reps_of_wall(layers: List[Layer], laps: List[float], alp: List[float], M: int, DTime):
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
    matFi = np.zeros((len(layers), 2, 2))

    # 吸熱、貫流の各伝達関数ベクトルの初期化
    nlaps = len(laps)
    matGA = np.zeros((nlaps, 1))
    matGT = np.zeros((nlaps, 1))

    # 単位貫流応答、単位吸熱応答の初期化
    dblAT0 = 1.0
    dblAA0 = sum([layer.R for layer in layers])

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
        for lngK, layer in enumerate(layers):

            # ---- 四端子基本行列 matFi ----
            if abs(layer.C) < 0.001:
                # 定常部位（空気層等）の場合
                matFi[lngK] = np.array([
                    [1.0, layer.R],
                    [0.0, 1.0]
                ])
            else:
                # 非定常部位の場合
                dblTemp = math.sqrt(layer.R * layer.C * laps[lngI])
                dblCosh = np.cosh(dblTemp)
                dblSinh = np.sinh(dblTemp)

                matFi[lngK] = np.array([
                    [dblCosh, layer.R / dblTemp * dblSinh],
                    [dblTemp / layer.R * dblSinh, dblCosh]
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
        matGA[lngI][0] = matFt[0, 1] / matFt[1, 1] - dblGA0
        matGT[lngI][0] = 1.0 / matFt[1][1] - dblGT0

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
            dblATstep[lngJ] = dblATstep[lngJ] + dblAT[lngK] * math.exp( -root * lngJ * DTime )
            dblAAstep[lngJ] = dblAAstep[lngJ] + dblAA[lngK] * math.exp( -root * lngJ * DTime )

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
def get_RFTRI(alp, AT0, AA0, AT, AA, M, DTime):
    # 二等辺三角波励振の応答係数の配列を初期化
    dblRFT = np.zeros(M)
    dblRFA = np.zeros(M)

    # 二等辺三角波励振の応答係数の初項を計算
    dblTemp = np.array(alp) * DTime
    dblE1 = (1.0 - np.exp(-dblTemp)) / dblTemp
    dblRFT[0] = AT0 + np.sum(dblE1 * AT)
    dblRFA[0] = AA0 + np.sum(dblE1 * AA)

    # 二等辺三角波励振の応答係数の二項目以降を計算
    for lngJ in range(1, M):
        dblE1 = (1.0 - np.exp(-dblTemp)) ** 2.0 * np.exp(-(float(lngJ) - 1.0) * dblTemp) / dblTemp
        dblRFT[lngJ] = (-1.0) * np.sum(dblE1 * AT)
        dblRFA[lngJ] = - np.sum(dblE1 * AA)

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
class ResponseFactor:
    # 初期化
    def __init__(self, WallType: str, DTime: int, NcalTime: int, Wall: Wall):
        """
        VBAからの主な変更点：
        (1)二次元配列（objArray）で壁体の情報を受け取っていたが、壁体情報クラスで受け取るように変更
        (2)lngStRow, lngOutputColは削除
        (3)固定根はシートから読み込んでいたが、初期化時に配列として与えるように変更
        (4)伝達関数近似のA0の周期は使用しない
        :param WallType: 壁体種類, 'wall' or 'soil'
        :param DTime: 計算時間間隔[s]
        :param NcalTime: 応答係数を作成する時間数[h]
        :param Wall: 壁体基本情報クラス
        """
        M = int(NcalTime * 3600 / DTime) + 1  # 応答係数で作成する項数

        # 固定根の設定
        alps = get_alps(WallType)

        # ラプラス変数の設定
        laps = get_laps(alps)

        # 単位応答の計算
        AT0, AA0, AT, AA, ATstep, AAstep = get_step_reps_of_wall(Wall.Layers, laps, alps, M, DTime)
        # plt.plot(ATstep)
        # plt.show()
        # plt.plot(AAstep)
        # plt.show()

        # 二等辺三角波励振の応答係数、指数項別応答係数、公比の計算
        RFT, RFA, self.RFT1, self.RFA1, self.Row = get_RFTRI(alps, AT0, AA0, AT, AA, M, DTime)
        # print('RFT0', RFT[0], 'RFA0', RFA[0])
        # print('RFT1', self.RFT1, 'RFA1', self.RFA1, 'Row', self.Row)

        self.RFT0 = RFT[0]  # 貫流応答係数の初項
        self.RFA0 = RFA[0]  # 吸熱応答係数の初項
        self.Nroot = len(alps)  # 根の数
