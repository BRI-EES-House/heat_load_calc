import math
import numpy as np

from heat_load_calc.external.global_number import get_sgm, get_eps


def get_h_r_js(a_srf_js, p_js_is):
    """ 放射熱伝達率

    Args:
        a_srf_js: 境界jの面積, m2, [j, 1]
        p_js_is: 室iと境界jの関係を表す係数（室iから境界jへの変換）
    　　　　　　　[[p_0_0 ... p_i_0]
    　　　　　　　　[ ...  ...  ... ]
    　　　　　　　　[ ...  ...  ... ]
    　　　　　　　　[p_0_j ... p_i_j]]
    Returns:

    """

    # 微小点に対する境界jの形態係数
    # 永田先生の方法
    FF_m = np.concatenate([
        calc_form_factor_of_microbodies(area_i_js=(a_srf_js * p_js_is)[:, i][p_js_is[:, i] == 1])
        for i in range(p_js_is.shape[1])])

    # 境界間の放射熱伝達率を決定する際、平均放射温度を20℃固定値であるとして計算する。
    MRT = 20.0

    hr_i_k_n = get_eps() / (1.0 - get_eps() * FF_m) * 4.0 * get_sgm() * (MRT + 273.15) ** 3.0

    return hr_i_k_n.reshape(-1, 1)


def get_f_mrt_is_js(a_srf_js, h_r_js, p_is_js):

    ah = a_srf_js * h_r_js

    return p_is_js * ah.T / np.dot(p_is_js, ah)


def calc_form_factor_of_microbodies(area_i_js):
    """
    微小体に対する部位の形態係数の計算

    Args:
        area_i_js:

    Returns:

    """

    # 面積比 式(95)
    a_k = area_i_js / sum(area_i_js)

    # 非線形方程式L(f̅)=0の解, float
    fb = get_fb(a_k)

    # 式（123）で示す放射伝熱計算で使用する微小球に対する部位の形態係数 [-] 式(94)
    FF_m = get_FF_m(fb, a_k)

    # 総和のチェック
    FF = np.sum(FF_m)
    if abs(FF - 1.0) > 1.0e-3:
        print('形態係数の合計値が不正 TotalFF=', FF)

    return FF_m


def get_fb(a):
    """非線形方程式L(f̅)=0の解

    Args:
        a:

    Returns:

    """

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
        if abs(L_m_n) < 1.e-8:  # 式(100)
            isConverge = True
            break

        if np.sign(L_m_n) == np.sign(L_m):
            m = m_n
        else:
            n = m_n
        m_n = (m + n) / 2.0

    # 収束しないときには警告を表示
    if not isConverge:
        print('形態係数パラメータが収束しませんでした。')

    return m_n


def get_L(a: float, fbd: float) -> float:
    return 0.5 * (1.0 - np.sign(1.0 - 4.0 * a / fbd) * math.sqrt(abs(1.0 - 4.0 * a / fbd)))


# 式（123）で示す放射伝熱計算で使用する微小球に対する部位の形態係数 [-] 式(94)
def get_FF_m(fb, a):
    return 0.5 * (1.0 - np.sign(1.0 - 4.0 * a / fb) * np.sqrt(abs(1.0 - 4.0 * a / fb)))


