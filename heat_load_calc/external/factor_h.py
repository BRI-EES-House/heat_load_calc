def get_h(region: int, next_space: str) -> float:
    """
    Args:
        region: 地域の区分
        next_space: 隣接する空間の種類
    Returns:
        温度差係数
    Notes:
        隣接する空間の種類
            outdoor: 外気
            open_space: 外気又は外気に通じる空間
            closed_space: 外気に通じていない空間
            open_underfloor: 外気に通じる床裏
            air_conditioned: 住戸及び住戸と同様の熱的環境の空問
            closed_underfloor: 外気に通じていない床裏
    """

    return {
        'outdoor': 1.0,
        'open_space': 1.0,
        'closed_space': 0.7,
        'open_underfloor': 0.7,
        'air_conditioned': {
            1: 0.05,
            2: 0.05,
            3: 0.05,
            4: 0.15,
            5: 0.15,
            6: 0.15,
            7: 0.15,
            8: 0.15
        }[region],
        'closed_underfloor': {
            1: 0.05,
            2: 0.05,
            3: 0.05,
            4: 0.15,
            5: 0.15,
            6: 0.15,
            7: 0.15,
            8: 0.15
        }[region],
    }[next_space]
