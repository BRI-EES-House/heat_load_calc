

def get_a_f_nr(a_f_total: float, a_f_mr: float, a_f_or: float) -> float:
    """
    非居室の床面積を計算する。
    Args:
        a_f_total: 床面積の合計, m2
        a_f_mr: 主たる居室の床面積, m2
        a_f_or: その他の居室の床面積, m2
    Returns:
        非居室の床面積, m2
    """

    return a_f_total - a_f_mr - a_f_or
