from enum import Enum


class Structure(Enum):

    """構造を表す列挙型
    """

    RC = 'rc'
    SRC = 'src'
    WOODEN = 'wooden'
    STEEL = 'steel'


def estimate_c_value(ua_value: float, struct: Structure) -> float:

    """
    Args
        ua_value: UA値, W/m2 K
        struct: 構造
    Returns:
        C値, cm2/m2
    """

    a = {
        Structure.RC: 4.16,       # RC造
        Structure.SRC: 4.16,      # SRC造
        Structure.WOODEN: 8.28,   # 木造
        Structure.STEEL: 8.28,    # 鉄骨造
    }[struct]

    return a * ua_value


if __name__ == '__main__':
    print(estimate_c_value(0.5, Structure.WOODEN))
    print(Structure('rc'))
    print(Structure.RC.value)
