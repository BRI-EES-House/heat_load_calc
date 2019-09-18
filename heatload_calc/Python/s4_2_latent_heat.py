import numpy as np
import a18_initial_value_constants as a18


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
def get_BRMX(Ventset, Infset, LocalVentset, Gf, Cx, volume, Vnext_i_j):
    # 外気の流入量
    Voin = get_Voin(Ventset, Infset, LocalVentset)

    # 湿気容量の項
    temp = get_temp(Gf=Gf, Cx=Cx)

    # 配列準備
    next_volume = np.array(Vnext_i_j)

    rhoa = a18.get_rhoa()

    BRMX = (rhoa * (volume / 900 + Voin)
            + temp
            + np.sum(rhoa * next_volume / 3600.0))

    return BRMX


# 式(18)
def get_BRXC(Ventset, Infset, LocalVentset, Gf, Cx, volume, xo, xr_i_nm1, xf_i_nm1, Lin, Vnext_i_j, xr_next_i_j_nm1):
    # 外気の流入量
    Voin = get_Voin(Ventset, Infset, LocalVentset)

    # 湿気容量の項
    temp = get_temp(Gf=Gf, Cx=Cx)

    rhoa = a18.get_rhoa()

    BRXC = rhoa * (volume / 900 * xr_i_nm1 + Voin * xo) \
           + temp * xf_i_nm1 \
           + Lin \
           + np.sum([rhoa * Vnext_i_j * xr_next_i_j_nm1 / 3600.0])

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
