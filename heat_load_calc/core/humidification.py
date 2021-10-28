import numpy as np
from functools import partial
from typing import Union

from heat_load_calc.external.psychrometrics import get_x, get_p_vs_is2
from heat_load_calc.external.global_number import get_c_air, get_rho_air


def make_get_f_l_cl_funcs(n_rm, cooling_equipments):

    # 顕熱負荷、室温、加湿・除湿をしない場合の自然絶対湿度から、係数 f_l_cl を求める関数を定義する。
    # 対流式と放射式に分けて係数を設定して、それぞれの除湿量を出す式に将来的に変更した方が良いかもしれない。

    def get_f_l_cl(l_cs_is_n, theta_r_is_n_pls, x_r_ntr_is_n_pls):
        # ==== ルームエアコン吹出絶対湿度の計算 ====
        # 顕熱負荷・室内温度・除加湿を行わない場合の室絶対湿度から、除加湿計算に必要な係数 la 及び lb を計算する。
        # 下記、変数 l は、係数 la と lb のタプルであり、変数 ls は変数 l のリスト。

        ls = [
            _func_rac(n_room=n_rm, lcs_is_n=l_cs_is_n, theta_r_is_n_pls=theta_r_is_n_pls, x_r_ntr_is_n_pls=x_r_ntr_is_n_pls, prop=equipment['property'])
            for equipment in cooling_equipments
        ]

        # 係数 la と 係数 lb をタプルから別々に取り出す。
        ls_a = np.array([l[0] for l in ls])
        ls_b = np.array([l[1] for l in ls])
        # 係数 la 及び lb それぞれ合計する。
        # la [i,i] kg/s(kg/kg(DA))
        # lb [i,1] kg/kg(DA)
        # TODO: La は正負が仕様書と逆になっている
        f_l_cl_wgt_is_is_n = - ls_a.sum(axis=0)
        f_l_cl_cst_is_n = ls_b.sum(axis=0)
        return f_l_cl_cst_is_n, f_l_cl_wgt_is_is_n

    return get_f_l_cl


def _func_rac(
        n_room,
        lcs_is_n,
        theta_r_is_n_pls,
        x_r_ntr_is_n_pls,
        prop
):

    # Lcsは加熱が正で表される。
    # 加熱時は除湿しない。
    # 以下の取り扱いを簡単にするため（冷房負荷を正とするため）、正負を反転させる
    q_s_is_n = -lcs_is_n

    id = prop['space_id']

    q_rac_max_i = prop['q_max']
    q_rac_min_i = prop['q_min']
    v_rac_max_i = prop['v_max'] / 60
    v_rac_min_i = prop['v_min'] / 60
    bf_rac_i = prop['bf']
    q_s_i_n = q_s_is_n[id, 0]
    theta_r_i_n_pls = theta_r_is_n_pls[id, 0]
    x_r_ntr_i_n_pls = x_r_ntr_is_n_pls[id, 0]

    v_rac_i_n = _get_vac_rac_i_n(
        q_rac_max_i=q_rac_max_i,
        q_rac_min_i=q_rac_min_i,
        q_s_i_n=q_s_i_n,
        v_rac_max_i=v_rac_max_i,
        v_rac_min_i=v_rac_min_i
    )

    theta_rac_ex_srf_i_n_pls = _get_theta_rac_ex_srf_i_n_pls(
        bf_rac_i=bf_rac_i,
        q_s_i_n=q_s_i_n,
        theta_r_i_n_pls=theta_r_i_n_pls,
        v_rac_i_n=v_rac_i_n
    )

    x_rac_ex_srf_i_n_pls = _get_x_rac_ex_srf_i_n_pls(theta_rac_ex_srf_i_n_pls=theta_rac_ex_srf_i_n_pls)

    brmx_rac_is = np.where(
        (x_r_ntr_i_n_pls > x_rac_ex_srf_i_n_pls) & (q_s_i_n > 0.0),
        get_rho_air() * v_rac_i_n * (1 - bf_rac_i),
        0.0
    )

    brcx_rac_is = np.where(
        (x_r_ntr_i_n_pls > x_rac_ex_srf_i_n_pls) & (q_s_i_n > 0.0),
        get_rho_air() * v_rac_i_n * (1 - bf_rac_i) * x_rac_ex_srf_i_n_pls,
        0.0
    )

    brmx_is_is = np.zeros((n_room, n_room), dtype=float)
    brxc_is = np.zeros((n_room, 1), dtype=float)

    brmx_is_is[id, id] = brmx_rac_is
    brxc_is[id, 0] = brcx_rac_is

    return brmx_is_is, brxc_is


def _get_x_rac_ex_srf_i_n_pls(theta_rac_ex_srf_i_n_pls: float) -> float:
    """
    ルームエアコンディショナーの室内機の熱交換器表面の絶対湿度を求める。
    Args:
        theta_rac_ex_srf_i_n_pls: ステップ n+1 における室 i に設置されたルームエアコンディショナーの室内機の熱交換器表面温度,degree C
    Returns:
        ステップ n+1 における室 i に設置されたルームエアコンディショナーの室内機の熱交換器表面の絶対湿度, kg/kg(DA)
    Notes:
        繰り返し計算（温度と湿度） eq.12
    """

    return get_x(get_p_vs_is2(theta_rac_ex_srf_i_n_pls))


def _get_theta_rac_ex_srf_i_n_pls(
        bf_rac_i: float,
        q_s_i_n: float,
        theta_r_i_n_pls: float,
        v_rac_i_n: float
) -> float:
    """
    ステップ n+1 における室 i に設置されたルームエアコンディショナーの室内機の熱交換器表面温度を計算する。
    Args:
        bf_rac_i: 室 i に設置されたルームエアコンディショナーの室内機の熱交換器のバイパスファクター, -
        q_s_i_n: ステップ n から n+1 における室 i の顕熱負荷, W
        theta_r_i_n_pls: ステップ n+1 における室 i の温度, degree C
        v_rac_i_n: ステップ n から n+1 における室 i に設置されたルームエアコンディショナーの吹き出し風量, m3/s
    Returns:
        ステップ n+1 における室 i に設置されたルームエアコンディショナーの室内機の熱交換器表面温度, degree C
    Notes:
        繰り返し計算（温度と湿度） eq.14
    """

    return theta_r_i_n_pls - q_s_i_n / (get_c_air() * get_rho_air() * v_rac_i_n * (1.0 - bf_rac_i))


def _get_vac_rac_i_n(
        q_rac_max_i: Union[float, np.ndarray],
        q_rac_min_i: Union[float, np.ndarray],
        q_s_i_n: Union[float, np.ndarray],
        v_rac_max_i: Union[float, np.ndarray],
        v_rac_min_i: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """
    ルームエアコンディショナーの吹き出し風量を顕熱負荷に応じて計算する。

    Args:
        q_rac_max_i: 室 i に設置されたルームエアコンディショナーの最大能力, W
        q_rac_min_i: 室 i に設置されたルームエアコンディショナーの最小能力, W
        q_s_i_n:　ステップ n からステップ n+1 における室 i の顕熱負荷, W
        v_rac_max_i: 室 i に設置されたルームエアコンディショナーの最小能力時における風量, m3/s
        v_rac_min_i: 室 i に設置されたルームエアコンディショナーの最大能力時における風量, m3/s
    Returns:
        室iに設置されたルームエアコンディショナーの吹き出し風量, m3/s
    Notes:
        繰り返し計算（湿度と潜熱） eq.14
    """

    # 吹き出し風量（仮）, m3/s
    v = v_rac_min_i * (q_rac_max_i - q_s_i_n) / (q_rac_max_i - q_rac_min_i)\
        + v_rac_max_i * (q_rac_min_i - q_s_i_n) / (q_rac_min_i - q_rac_max_i)

    # 下限値・上限値でクリップ後の吹き出し風量, m3/s
    v_rac_i_n = np.clip(v, a_min=v_rac_min_i, a_max=v_rac_max_i)

    return v_rac_i_n

