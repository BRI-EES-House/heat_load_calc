import math
import numpy as np

"""
付録12．	室内表面の吸収日射量、形態係数、放射暖房放射成分吸収比率
"""


# 微小体に対する部位の形態係数の計算 式(94)
def calc_form_factor_of_microbodies(space_name, area):
    # 面積比 式(95)
    a_k = get_a_k(area)

    # 面積比の最大値 （ニュートン法の初期値計算用）
    max_a = get_max_a(a_k)

    # 非線形方程式L(f̅)=0の解
    fb = get_fb(max_a, space_name, a_k)

    # 式（123）で示す放射伝熱計算で使用する微小球に対する部位の形態係数 [-] 式(94)
    FF_m = get_FF_m(fb, a_k)
    # print(FF_m)

    # 総和のチェック
    FF = np.sum(FF_m)
    if abs(FF - 1.0) > 1.0e-3:
        print('形態係数の合計値が不正 name=', space_name, 'TotalFF=', FF)

    return FF_m


# 面積比 [-] 式(95)
def get_a_k(A_i_k):
    A_i = sum(A_i_k)
    a_k = A_i_k / A_i
    return a_k


def get_max_a(a):
    return max(a)


# 式（123）で示す放射伝熱計算で使用する微小球に対する部位の形態係数 [-] 式(94)
def get_FF_m(fb, a):
    return 0.5 * (1.0 - np.sign(1.0 - 4.0 * a / fb) * np.sqrt(abs(1.0 - 4.0 * a / fb)))


# 非線形方程式L(f̅)=0の解
def get_fb(max_a, space_name, a):
    # 室のパラメータの計算（ニュートン法）
    # 初期値を設定
    m = 1.0e-5  # 式(99)
    n = 100.0
    m_n = (m + n) / 2.0
    
    # 収束判定
    isConverge = False
    for i in range(50):
        L_m = -1.0  # 式(96)の一部
        L_n = -1.0
        L_m_n = -1.0
        for _a in a:
            L_m += get_L(_a, m)  # 式(96)の一部
            L_n += get_L(_a, n)
            L_m_n += get_L(_a, m_n)
        # print(i, 'm=', m, 'L_m=', L_m, 'n=', n, 'L_n=', L_n, 'm_n=', m_n, 'L_m_n=', L_m_n)
        # 収束判定
        if abs(L_m_n) < 1.e-4:  # 式(100)
            isConverge = True
            break

        if np.sign(L_m_n) == np.sign(L_m):
            m = m_n
        else:
            n = m_n
        m_n = (m + n) / 2.0
            
    # 収束しないときには警告を表示
    if not isConverge:
        print(space_name, '形態係数パラメータが収束しませんでした。')

    return m_n

def get_L(a: float, fbd: float) -> float:
    return 0.5 * (1.0 - np.sign(1.0 - 4.0 * a / fbd) * math.sqrt(abs(1.0 - 4.0 * a / fbd)))
    

# 平均放射温度計算時の各部位表面温度の重み計算 式(101)
def get_F_mrt_i_g(area, hir):
    # 各部位表面温度の重み=面積×放射熱伝達率の比率
    total_area_hir = np.sum(area * hir)

    F_mrt_i_k = area * hir / total_area_hir

    return F_mrt_i_k


# 家具の透過日射吸収比率 (表5 家具の場合)
def get_furniture_ratio_base():
    return 0.5


# 透過日射の吸収比率を設定する（家具の吸収比率を返す）
def calc_absorption_ratio_of_transmitted_solar_radiation():
    return 0.5


def get_SolR(area, is_solar_absorbed_inside, tolal_floor_area):
    FsolFlr = 0.5
    SolR = (FsolFlr * area / tolal_floor_area) * is_solar_absorbed_inside
    return SolR


# 部位の人体に対する形態係数の計算 表6
def calc_form_factor_for_human_body(area, is_solar_absorbed_inside):
    # 設定合計値もチェック
    total_Fot = 0.0

    # 下向き部位（床）の合計面積
    total_A_floor = np.sum(area * is_solar_absorbed_inside)

    # 床以外の合計面積
    total_Aex_floor = np.sum(area * (1 - is_solar_absorbed_inside))

    # 上向き、下向き、垂直部位の合計面積をチェックし人体に対する形態係数の割合を基準化
    fot_floor = 0.45
    fot_exfloor = 1.0 - fot_floor

    fot = np.zeros(len(area), dtype=np.float)

    # 人体に対する部位の形態係数の計算

    # 下向き部位（床）
    f1 = is_solar_absorbed_inside
    fot[f1] = area[f1] / total_A_floor * fot_floor

    # 床以外
    f2 = np.logical_not(is_solar_absorbed_inside)
    fot[f2] = area[f2] / total_Aex_floor * fot_exfloor

    return fot


# 室の透過日射熱取得から室内各部位の吸収日射量 式(91)
def get_Sol(Qgt, SolR, A_i_k):
    return Qgt * SolR / A_i_k


# 家具の吸収日射量[W] 式(92)
def get_Qsolfun(Qgt, rsolfun):
    return Qgt * rsolfun


# 放射暖房放射成分吸収比率 表7
def get_flr(A_i_g, A_fs_i, is_radiative_heating, is_solar_absorbed_inside):
    return (A_i_g / A_fs_i) * is_radiative_heating * is_solar_absorbed_inside
