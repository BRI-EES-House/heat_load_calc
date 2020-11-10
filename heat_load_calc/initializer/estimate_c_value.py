from enum import IntEnum

class structure(IntEnum):

    '''
    構造を表す列挙型
    '''

    rc = 1
    src = 2
    wooden = 3
    steel = 4


def estimate_c_value(ua_value: float, struct: int) -> float:
    '''
    UA値からC値を推定する
    :param ua_value: UA値, W/m2 K
    :param struct: 構造
    :return: C値, cm2/m2
    '''

    a, b = {
        1: (2.58, 2.68),        # RC造
        2: (2.58, 2.68),        # SRC造
        3: (4.40, 3.17),        # 木造
        4: (4.40, 3.17),        # 鉄骨造
    }[struct]

    return a * ua_value + b


if __name__ == '__main__':
    print(estimate_c_value(0.5, int(structure.wooden)))
