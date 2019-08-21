

def get_a_f_nr(a_f_total: float, a_f_mr: float, a_f_or: float) -> float:
    """
    Args:
        a_f_total: 床面積の合計, m2
        a_f_mr: 主たる居室の床面積, m2
        a_f_nr: その他の居室の床面積, m2
    """

    return a_f_total - a_f_mr - a_f_or
