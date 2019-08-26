import math


def round_num(num: float, digit: int) -> float:
    """
    四捨五入を行う関数
    Args:
        num: 対象とする数字
        digit: 四捨五入を行う桁数
    Returns:
        四捨五入された値
    Notes:
        PythonのRound関数は最近接偶数への丸めとなるため、四捨五入を行う関数を独自に定義する。
    Examples:
        >>> round2(2.732, 2)
        2.73
        >>> round2(2.735, 2)
        2.74
        >>> round2(2.737, 2)
        2.74
        >>> round2(-2.732, 2)
        -2.73
        >>> round2(-2.735, 2)
        -2.74
        >>> round2(-2.737, 2)
        -2.74
    """

    power = 10 ** digit  # 10のべき乗
    sign = math.copysign(1, num)  # 符号
    return math.floor(sign * power * num + 0.5) / (sign * power)

