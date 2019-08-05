import numpy as np

# 表面温度の計算
def calc_surface_temperature(space):
    # 表面温度の計算
    for (matWSR, matWSV, matWSC, matWSB, surface) in zip(space.matWSR, space.matWSV, space.matWSC, space.matWSB, space.input_surfaces):
        surface.Ts = matWSR * space.Tr + matWSC + matWSV + matWSB * space.Lrs

# 室内等価温度の計算
def calc_Tei(surface, Tr, Tsx, Lr, Beta):
    """
    :param Tr: 室温
    :param Tsx: 形態係数加重平均表面温度
    :param Lr:
    :param Beta:
    :return:
    """
    return Tr * surface.hic / surface.hi \
                    + Tsx * surface.hir / surface.hi \
                    + surface.RSsol / surface.hi \
                    + surface.flr * Lr * (1.0 - Beta) / surface.hi / surface.area

# 室内表面熱流の計算
def calc_qi(surface, Tr: float, Tsx: float, Lr: float, Beta: float):
    """
    :param Tr: 室温
    :param Tsx: 形態係数加重平均表面温度
    :param Lr:
    :param Beta:
    :return:
    """
    # 対流成分
    surface.Qc = surface.hic * surface.area * (Tr - surface.Ts)

    # 放射成分
    surface.Qr = surface.hir * surface.area * (Tsx - surface.Ts)

    # 短波長熱取得成分
    surface.RS = surface.RSsol * surface.area

    # 放射暖房成分
    surface.Lr = surface.flr * Lr * (1.0 - Beta)

    # 表面熱流合計
    surface.Qt = surface.Qc + surface.Qr + surface.Lr + surface.RS
    # 前時刻熱流の保持
    surface.oldqi = surface.Qt / surface.area
    
# 行列CVL、WSVの計算
def calc_CVL_WSV(space):
    # {WSV}、{CVL}の初期化
    space.matWSV = [0.0 for j in range(space.Nsurf)]
    space.matCVL = [0.0 for j in range(space.Nsurf)]

    # 畳み込み演算
    i = 0
    for surface in space.input_surfaces:
        space.matCVL[i] = convolution(surface)
        i += 1

    # {WSV}=[XA]*{CVL}
    space.matWSV = np.dot(space.matAX, space.matCVL)

# 行列CRX、WSCの計算
def calc_CRX_WSC(space):
    # {WSC}、{CRX}の初期化
    space.matWSC = [0.0 for j in range(space.Nsurf)]
    space.matCRX = [0.0 for j in range(space.Nsurf)]

    # {CRX}の作成
    i = 0
    for surface in space.input_surfaces:
        space.matCRX[i] = surface.RFT0 * surface.Teo \
                                + surface.RSsol * surface.RFA0
        i += 1

    # {WSC}=[XA]*{CRX}
    space.matWSC = np.dot(space.matAX, space.matCRX)

# 室内表面熱収支計算のための行列作成
def make_matrix_for_surface_heat_balance(space):
    # 行列の準備と初期化
    # [AX]
    space.matAXd = [[0.0 for i in range(space.Nsurf)] for j in range(space.Nsurf)]
    # {FIA}
    space.matFIA = [0.0 for j in range(space.Nsurf)]
    # {CRX}
    space.matCRX = [0.0 for j in range(space.Nsurf)]
    # {CVL}
    space.matCVL = [0.0 for j in range(space.Nsurf)]
    # {FLB}
    space.matFLB = [0.0 for j in range(space.Nsurf)]
    # {WSC}
    space.matWSC = [0.0 for j in range(space.Nsurf)]
    # {WSV}
    space.matWSV = [0.0 for j in range(space.Nsurf)]

    i = 0
    for surface in space.input_surfaces:
        # matFIAの作成
        space.matFIA[i] = surface.RFA0 * surface.hic
        # FLB=φA0×flr×(1-Beta)
        space.matFLB[i] = surface.RFA0 * surface.flr * (1. - space.Beta) / surface.area

        # 放射計算のマトリックス作成
        j = 0
        for nxtsurface in space.input_surfaces:
            # 対角要素
            if i == j:
                space.matAXd[i][j] = 1. + surface.RFA0 * surface.hi \
                                        - surface.RFA0 * surface.hir * nxtsurface.Fmrt
            # 対角要素以外
            else:
                space.matAXd[i][j] = - surface.RFA0 * surface.hir * nxtsurface.Fmrt
            j += 1
        # print('放射計算マトリックス作成完了')
        i += 1

    # 逆行列の計算
    space.matAX = np.linalg.inv(space.matAXd)
    # {WSR}の計算
    space.matWSR = np.dot(space.matAX, space.matFIA)
    # {WSB}の計算
    space.matWSB = np.dot(space.matAX, space.matFLB)

# 畳み込み積分
def convolution(surface):
    sumTsd = 0.0
    for i in range(surface.Nroot):
        surface.oldTsd_t[i] = surface.oldTeo * surface.RFT1[i] + surface.Row[i] * surface.oldTsd_t[i]
        surface.oldTsd_a[i] = surface.oldqi * surface.RFA1[i] + surface.Row[i] * surface.oldTsd_a[i]
        sumTsd += surface.oldTsd_t[i] + surface.oldTsd_a[i]

    return sumTsd