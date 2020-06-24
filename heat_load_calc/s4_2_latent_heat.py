
# 室絶対湿度の計算 式(16)
def get_xr(BRXC_i, BRMX_i):
    return BRXC_i / BRMX_i


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
