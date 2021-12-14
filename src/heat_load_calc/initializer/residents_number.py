
def get_total_number_of_residents(a_floor_total: float) -> float:
    """
    床面積の合計から居住人数を計算する。
    Args:
        a_floor_total: 床面積の合計, m2

    Returns:
        居住人数 float型
    """

    if a_floor_total < 30.0:
        return 1.0
    elif a_floor_total < 120.0:
        return a_floor_total / 30.0
    else:
        return 4.0
