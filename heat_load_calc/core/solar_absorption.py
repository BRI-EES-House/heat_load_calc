import numpy as np


def get_q_sol_frt_is_ns(q_trs_sor_is_ns):
    """

    Args:
        q_trs_sor_is_ns:

    Returns:
        ステップ n からステップ n+1 における室 i に設置された家具による透過日射吸収熱量時間平均値, W, [i, n]
    """

    return q_trs_sor_is_ns * _get_r_sol_frt()


def get_q_s_sol_js_ns(p_is_js, a_s_js, p_s_sol_abs_js, p_js_is, q_trs_sol_is_ns):
    """

    Args:
        p_is_js: 室 i と境界 j の接続に関する係数（境界 j が室 i に接している場合は 1 とし、それ以外の場合は 0 とする。）, -, [i, j]
        a_s_js: 境界 j の面積, m2, [j, 1]
        p_s_sol_abs_js: 境界 j において透過日射を吸収するか否かを表す係数（吸収する場合は 1 とし、吸収しない場合は 0 とする。）, -, [j, 1]
        p_js_is: 室 i と境界 j の接続に関する係数（境界 j が室 i に接している場合は 1 とし、それ以外の場合は 0 とする。）, -, [j, i]
        q_trs_sol_is_ns:　ステップ n における室 i の透過日射熱量, W, [i, 1]

    Returns:
        ステップ n における境界 j の透過日射吸収熱量, W/m2, [j, n]
    """

    # 室iにおける日射が吸収される境界の面積の合計, m2, [i, 1]
    a_srf_abs_is = np.dot(p_is_js, a_s_js * p_s_sol_abs_js)

    # ステップnの境界jにおける透過日射吸収熱量, W/m2, [j, n]
    return np.dot(p_js_is, q_trs_sol_is_ns / a_srf_abs_is) * p_s_sol_abs_js * (1.0 - _get_r_sol_frt())


def _get_r_sol_frt() -> float:
    """

    Returns:
        室内侵入日射のうち家具に吸収される割合, -

    """

    return 0.5

