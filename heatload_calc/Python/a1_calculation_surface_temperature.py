import numpy as np

"""
付録1．	表面温度の計算
"""

# ********** 室内表面温度 **********

# 表面温度の計算 式(23)
def get_surface_temperature(matWSR, matWSB, matWSC, matWSV, Tr, Lrs):
    return matWSR * Tr + matWSC + matWSV + matWSB * Lrs

# ********** 表面温度を計算するための各種係数 **********

# 式(24)
def get_WSR(matAX, matFIA):
    return np.dot(matAX, matFIA)


# 式(24)
def get_WSB(matAX, matFLB):
    return np.dot(matAX, matFLB)


# 式(24)
def get_WSC(matAX, matCRX):
    # {WSC}=[XA]*{CRX}
    return np.dot(matAX, matCRX)


# {WSV}=[XA]*{CVL} 式(24)
def get_WSV(matAX, matCVL):
    return np.dot(matAX, matCVL)


# 式(25)中のAXはAXdの逆行列
def get_AX(matAXd):
    return np.linalg.inv(matAXd)


# 行列AX 式(25)
def get_AX(RFA0, hir, Fmrt, hi, Nsurf):
    # 単位行列の準備
    eye = np.eye(Nsurf)

    # 対角要素以外 式(25)上段
    matAXd = - RFA0[:,np.newaxis] * hir[:,np.newaxis] * Fmrt[np.newaxis,:]

    # 対角要素 式(25)下段
    matAXd[eye == 1] = 1. + RFA0 * hi - RFA0 * hir * Fmrt

    # 逆行列の計算
    return np.linalg.inv(matAXd)


# matFIAの作成 式(26)
def get_FIA(RFA0, hic):
    return RFA0 * hic


# FLB=φA0×flr×(1-Beta_i) 式(26)
def get_FLB(RFA0, flr, Beta, area):
    return RFA0 * flr * (1. - Beta) / area


# 式(26)
def get_CRX(RFT0, Teo, RSsol, RFA0):
    return RFT0 * Teo + RSsol * RFA0


# 畳み込み演算 式(26)
def get_CVL(oldTsd_t, oldTsd_a, Nroot):
    return [np.sum(oldTsd_t[i] + oldTsd_a[i]) for i in range(len(Nroot))]


# 室内表面熱流の計算 式(28)
def calc_qi(hic, area, hir, RSsol, flr, Ts, Tr: float, Fmrt: float, Lr: float, Beta: float):
    """
    :param Tr: 室温
    :param Tsx: 形態係数加重平均表面温度
    :param Lr:
    :param Beta:
    :return:
    """
    # 対流成分
    Qc = get_Qc(hic, area, Tr, Ts)

    # 平均放射温度の計算
    Tsx = get_Tsx(Fmrt, Ts)

    # 放射成分
    Qr = get_Qr(hir, area, Tsx, Ts)

    # 短波長熱取得成分
    RS = get_RS(RSsol, area)

    # 放射暖房成分
    Lr = get_Lr(flr,  Lr, Beta)

    # 表面熱流合計
    Qt = get_Qt(Qc, Qr, Lr, RS)

    # 前時刻熱流の保持
    oldqi = get_qi(Qt, area)

    return Qc, Qr, Lr, RS, Qt, oldqi

# 室内表面熱流 - 対流成分 [W]
def get_Qc(hic, area, Tr, Ts):
    return hic * area * (Tr - Ts)


# 室内表面熱流 - 放射成分 [W]
def get_Qr(hir, area, Tsx, Ts):
    return hir * area * (Tsx - Ts)


# 室内表面熱流 - 短波長熱取得成分 [W]
def get_RS(RSsol, area):
    return RSsol * area


# 室内表面熱流 - 放射暖房成分 [W]
def get_Lr(flr, Lr, Beta):
    return flr * Lr * (1.0 - Beta)


# 表面熱流合計 [W]
def get_Qt(Qc, Qr, Lr, RS):
    return Qc + Qr + Lr + RS


# 室内表面熱流 [W/m2]
def get_qi(Qt, area):
    return Qt / area


# 室内等価温度の計算 式(29)
def calc_Tei(hic, hi, hir, RSsol, flr, area, Tr, Fmrt, Ts, Lr, Beta):
    """
    :param Tr: 室温
    :param Tsx: 形態係数加重平均表面温度
    :param Lr:
    :param Beta:
    :return:
    """

    # 平均放射温度の計算
    Tsx = get_Tsx(Fmrt, Ts)

    return Tr * hic / hi \
                    + Tsx * hir / hi \
                    + RSsol / hi \
                    + flr * Lr * (1.0 - Beta) / hi / area

# 平均放射温度の計算
def get_Tsx(Fmrt, Ts):
    return np.sum(Fmrt * Ts)
