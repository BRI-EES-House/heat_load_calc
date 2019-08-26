from Psychrometrics import Pws, x
from common import conca, conrowa

# エアコンの熱交換部飽和絶対湿度の計算
def calcVac_xeout(space, nowAC):
    # Lcsは加熱が正
    # 加熱時は除湿ゼロ
    Qs = - space.Lcs
    if nowAC == 0 or Qs <= 1.0e-3:
        space.Vac = 0.0
        space.Ghum = 0.0
        space.Lcl = 0.0
        return
    else:
        # 風量[m3/s]の計算（線形補間）
        space.Vac = (space.Vmin + (space.Vmax - space.Vmin) \
                / (space.qmax_c - space.qmin_c) * (Qs - space.qmin_c)) / 60.0
        # 熱交換器温度＝熱交換器部分吹出温度
        space.Teout = space.Tr - Qs / (conca * conrowa * space.Vac * (1.0 - space.bypass_factor_rac))
        # 熱交換器吹出部分は飽和状態
        space.xeout = x(Pws(space.Teout))
