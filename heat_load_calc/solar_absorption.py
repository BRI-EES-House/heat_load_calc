import numpy as np


def get_q_sol_frt_is_ns(q_trs_sor_is_ns: np.ndarray, r_sol_frt_is: np.ndarray) -> np.ndarray:
    """室に設置された家具による透過日射吸収熱量の時間平均値を計算する。
    Calculate the average value of the transparented solar radiation absorbed by the furniture in room i
    Args:
        q_trs_sor_is_ns: ステップnにおける室iの透過日射量, W, [i, n]
        r_sol_frt_is: solar absorption ratio of furniture in room i / 室iの備品等の日射吸収割合, -, [I, 1]
    Returns:
        ステップnからステップn+1における室iに設置された家具による透過日射吸収熱量の時間平均値, W, [i, n]
    Note:
        eq.(1)
    """

    return q_trs_sor_is_ns * r_sol_frt_is


def get_q_s_sol_js_ns(p_is_js: np.ndarray, a_s_js: np.ndarray, p_s_sol_abs_js: np.ndarray, p_js_is: np.ndarray, q_trs_sol_is_ns: np.ndarray, r_sol_frt_is: np.ndarray) -> np.ndarray:
    """境界の透過日射吸収熱量を計算する。
    Calculate the transparent solar radiation absorbed by the boundary j at step n.
    Args:
        p_is_js: 室 i と境界 j の接続に関する係数（境界 j が室 i に接している場合は 1 とし、それ以外の場合は 0 とする。）, -, [i, j]
        a_s_js: 境界 j の面積, m2, [j, 1]
        p_s_sol_abs_js: 境界 j において透過日射を吸収するか否かを表す係数（吸収する場合は 1 とし、吸収しない場合は 0 とする。）, -, [j, 1]
        p_js_is: 室 i と境界 j の接続に関する係数（境界 j が室 i に接している場合は 1 とし、それ以外の場合は 0 とする。）, -, [j, i]
        q_trs_sol_is_ns: ステップ n における室 i の透過日射熱量, W, [i, n]
        r_sol_frt_is: solar absorption ratio of furniture in room i / 室iの備品等の日射吸収割合, -, [I, 1]
    Returns:
        ステップ n における境界 j の透過日射吸収熱量, W/m2, [j, n]
    Notes:
        eq.(2)
    """

    # 室iにおける日射が吸収される境界の面積の合計, m2, [i, 1]
    a_s_abs_is = _get_a_s_abs_is(p_is_js=p_is_js, a_s_js=a_s_js, p_s_sol_abs_js=p_s_sol_abs_js)

    # ステップnの境界jにおける透過日射吸収熱量, W/m2, [j, n]
    return np.dot(p_js_is, q_trs_sol_is_ns / a_s_abs_is * (1.0 - r_sol_frt_is)) * p_s_sol_abs_js


def _get_a_s_abs_is(p_is_js: np.ndarray, a_s_js: np.ndarray, p_s_sol_abs_js: np.ndarray) -> np.ndarray:
    """室の日射が吸収される境界の面積の合計を取得する。
    Calculate the sum of the area of the boundaries which absorb solar radiation in room i.
    Args:
        p_is_js: 室 i と境界 j の接続に関する係数（境界 j が室 i に接している場合は 1 とし、それ以外の場合は 0 とする。）, -, [i, j]
        a_s_js: 境界 j の面積, m2, [j, 1]
        p_s_sol_abs_js: 境界 j において透過日射を吸収するか否かを表す係数（吸収する場合は 1 とし、吸収しない場合は 0 とする。）, -, [j, 1]
    Returns:
        室iの日射が吸収される境界の面積の合計, m2, [i, 1]
    Note:
        eq.(3)
    """
    
    return np.dot(p_is_js, a_s_js * p_s_sol_abs_js)


def _get_r_sol_frt() -> float:
    """室内侵入日射のうち家具に吸収される割合を取得する。
    Get the ratio of absorbed solar radiation by furniture to transparented solar radiation into the room.
    Returns:
        室内 i の侵入日射のうち家具に吸収される割合, -
    Note:
        eq.(4)
    """

    return 0.5
