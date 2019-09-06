import numpy as np

# 表面温度の計算 式(23)
def get_surface_temperature(matWSR, matWSV, matWSC, matWSB, surfaces, Tr, Lrs):
    return matWSR * Tr + matWSC + matWSV + matWSB * Lrs

# 室内等価温度の計算 式(29)
def get_Tei(hic, hi, hir, RSsol, flr, area, Tr, Tsx, Lr, Beta):
    """
    :param Tr: 室温
    :param Tsx: 形態係数加重平均表面温度
    :param Lr:
    :param Beta:
    :return:
    """
    return Tr * hic / hi \
                    + Tsx * hir / hi \
                    + RSsol / hi \
                    + flr * Lr * (1.0 - Beta) / hi / area

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

# 室内表面熱流の計算 式(28)
def calc_qi(hic, area, hir, RSsol, flr, Ts, Tr: float, Tsx: float, Lr: float, Beta: float):
    """
    :param Tr: 室温
    :param Tsx: 形態係数加重平均表面温度
    :param Lr:
    :param Beta:
    :return:
    """
    # 対流成分
    Qc = get_Qc(hic, area, Tr, Ts)

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


# 行列CVL、WSVの計算
def calc_CVL_WSV(matAX, surfaces):
    # 畳み込み演算 式(26)
    matCVL = get_CVL(surfaces)

    # {WSV}=[XA]*{CVL} 式(24)
    matWSV = get_WSV(matAX, matCVL)

    return matCVL, matWSV

# {WSV}=[XA]*{CVL} 式(24)
def get_WSV(matAX, matCVL):
    return np.dot(matAX, matCVL)

# 畳み込み演算 式(26)
def get_CVL(surfaces):
    return [get_Tsd(surface) for surface in surfaces]


# 畳み込み積分
def get_Tsd(surface):
    sumTsd = 0.0
    for i in range(surface.Nroot):
        sumTsd += surface.oldTsd_t[i] + surface.oldTsd_a[i]

    return sumTsd

# 畳み込み積分 式(27)
def update_Tsd(space):
    for surface in space.input_surfaces:
        for i in range(surface.Nroot):
            surface.oldTsd_t[i] = surface.oldTeo * surface.RFT1[i] + surface.Row[i] * surface.oldTsd_t[i]
            surface.oldTsd_a[i] = surface.oldqi * surface.RFA1[i] + surface.Row[i] * surface.oldTsd_a[i]

# 行列CRX、WSCの計算
def calc_CRX_WSC(RFT0, Teo, RSsol, RFA0, matAX, sequence_number: int):
    # 配列の準備

    # {CRX}の作成
    matCRX = get_CRX(RFT0, Teo, RSsol, RFA0)

    # {WSC}=[XA]*{CRX}
    matWSC = get_WSC(matAX, matCRX)

    return matCRX, matWSC

# 式(24)
def get_WSC(matAX, matCRX):
    # {WSC}=[XA]*{CRX}
    return np.dot(matAX, matCRX)

# 式(26)
def get_CRX(RFT0, Teo, RSsol, RFA0):
    return RFT0 * Teo + RSsol * RFA0

# 室内表面熱収支計算のための行列作成
def calc_matrix_for_surface_heat_balance(RFA0, hic, flr, area, hir, Fmrt, hi, Nsurf, Beta):
    # matFIAの作成 式(26)
    matFIA = get_FIA(RFA0, hic)

    # FLB=φA0×flr×(1-Beta) 式(26)
    matFLB = get_FLB(RFA0, flr, Beta, area)

    # 行列AX 式(25)
    matAXd = get_AXd(RFA0, hir, Fmrt, hi, Nsurf)

    # 逆行列の計算
    matAX = np.linalg.inv(matAXd)

    # {WSR}の計算 式(24)
    matWSR = get_WSR(matAX, matFIA)

    # {WSB}の計算 式(24)
    matWSB = get_WSB(matAX, matFLB)

    return (matAX, matWSR, matWSB)

# 式(24)
def get_WSR(matAX, matFIA):
    return np.dot(matAX, matFIA)

# 式(24)
def get_WSB(matAX, matFLB):
    return np.dot(matAX, matFLB)

# 式(24)中のAXはAXdの逆行列
def get_AX(matAXd):
    return np.linalg.inv(matAXd)

# 行列AX 式(25)
def get_AXd(RFA0, hir, Fmrt, hi, Nsurf):
    # 単位行列の準備
    eye = np.eye(Nsurf)

    # 対角要素以外 式(25)上段
    matAXd = - RFA0[:,np.newaxis] * hir[:,np.newaxis] * Fmrt[np.newaxis,:]

    # 対角要素 式(25)下段
    matAXd[eye == 1] = 1. + RFA0 * hi - RFA0 * hir * Fmrt

    return matAXd

# matFIAの作成 式(26)
def get_FIA(RFA0, hic):
    return RFA0 * hic

# FLB=φA0×flr×(1-Beta) 式(26)
def get_FLB(RFA0, flr, Beta, area):
    return RFA0 * flr * (1. - Beta) / area

