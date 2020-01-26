import numpy as np
import a18_initial_value_constants as a18


# *********** 4.2 潜熱 **********

# 外気の流入量
def get_v_ex_i_n(v_reak_i_n, v_mec_vent_i_n):
    return v_mec_vent_i_n + v_reak_i_n / 3600.


# 湿気容量の項
def get_temp(Gf, Cx):
    temp = Gf * Cx / (Gf + 900 * Cx)
    return temp


# 室絶対湿度の計算 式(16)
def get_xr(BRXC_i, BRMX_i):
    return BRXC_i / BRMX_i


# 式(17)
def get_BRMX(v_reak_is_n, gf_is, cx_is, v_room_cap_is, v_mec_vent_is_n, v_int_vent_is):

    v_room_cap_i = v_room_cap_is

    # 外気の流入量
    Voin = get_v_ex_i_n(v_reak_i_n=v_reak_is_n, v_mec_vent_i_n=v_mec_vent_is_n)

    # 湿気容量の項
    temp = get_temp(Gf=gf_is, Cx=cx_is)

    rhoa = a18.get_rho_air()

    return (rhoa * (v_room_cap_i / 900 + Voin)
            + temp
            + rhoa * np.sum(v_int_vent_is,axis=1)
            )


# 式(18)
def get_BRXC(v_reak_i_n, Gf, Cx, volume, xo, xr_i_nm1, xf_i_nm1, Lin, v_int_vent_i_istrs, xr_next_i_j_nm1, v_mec_vent_i_n):
    # 外気の流入量
    Voin = get_v_ex_i_n(v_reak_i_n=v_reak_i_n, v_mec_vent_i_n=v_mec_vent_i_n)

    # 湿気容量の項
    temp = get_temp(Gf=Gf, Cx=Cx)

    rhoa = a18.get_rho_air()

    BRXC = rhoa * (volume / 900 * xr_i_nm1 + Voin * xo) \
           + temp * xf_i_nm1 \
           + Lin \
           + np.sum([rhoa * v_int_vent_i_istrs * xr_next_i_j_nm1])

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
