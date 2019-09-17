import numpy as np
from common import rhoa

# *********** 4.2 潜熱 **********

# 外気の流入量
def get_Voin(Ventset, Infset, LocalVentset):
    return (Ventset + Infset + LocalVentset) / 3600.


# 湿気容量の項
def get_temp(Gf, Cx):
    temp = Gf * Cx / (Gf + 900 * Cx)
    return temp

# 室絶対湿度の計算 式(16)
def get_xr(BRXC_i, BRMX_i):
    return BRXC_i / BRMX_i


# 式(17)
def get_BRMX(Ventset, Infset, LocalVentset, Gf, Cx, volume, RoomtoRoomVent):
    # 外気の流入量
    Voin = get_Voin(Ventset, Infset, LocalVentset)

    # 湿気容量の項
    temp = get_temp(Gf=Gf, Cx=Cx)

    # 配列準備
    next_volume = np.array([x.volume for x in RoomtoRoomVent])

    BRMX = (rhoa * (volume / 900 + Voin)
            + temp
            + np.sum(rhoa * next_volume / 3600.0))

    return BRMX


# 式(18)
def get_BRXC(Ventset, Infset, LocalVentset, Gf, Cx, volume, xo, oldxr, oldxf, Lin, RoomtoRoomVent):

    # 外気の流入量
    Voin = get_Voin(Ventset, Infset, LocalVentset)

    # 湿気容量の項
    temp = get_temp(Gf=Gf, Cx=Cx)

    # 配列準備
    next_volume = np.array([x.volume for x in RoomtoRoomVent])
    next_oldxr = np.array([x.oldxr for x in RoomtoRoomVent])

    BRXC = rhoa * (volume / 900 * oldxr + Voin * xo) \
           + temp * oldxf \
           + Lin \
           + np.sum([rhoa * next_volume * next_oldxr / 3600.0])

    return BRXC


# 式(19)
def get_xf(Gf, oldxf, Cx, xr):
    return (Gf / 900 * oldxf + Cx * xr) / (Gf / 900 + Cx)



def get_Qfunl(Cx, xr, xf):
    return Cx * (xr - xf)


# i室のn時点における除湿量 [ks/s] 式(20)
def get_Ghum(RhoVac, xeout, xr):
    """
    :param RhoVac:
    :param xeout:
    :param xr: 室空気の絶対湿度
    :return: i室のn時点における除湿量 [ks/s]
    """
    return RhoVac * (xeout - xr)