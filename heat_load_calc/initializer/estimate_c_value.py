from enum import Enum


class Structure(Enum):

    '''
    構造を表す列挙型
    '''

    RC = 'rc'
    SRC = 'src'
    WOODEN = 'wooden'
    STEEL = 'steel'


def estimate_c_value(ua_value: float, struct: Structure) -> float:
    '''
    UA値からC値を推定する
    :param ua_value: UA値, W/m2 K
    :param struct: 構造
    :return: C値, cm2/m2
    '''

    a, b = {
        Structure.RC: (2.58, 2.68),        # RC造
        Structure.SRC: (2.58, 2.68),        # SRC造
        Structure.WOODEN: (4.40, 3.17),        # 木造
        Structure.STEEL: (4.40, 3.17),        # 鉄骨造
    }[struct]

    return a * ua_value + b


if __name__ == '__main__':
    print(estimate_c_value(0.5, Structure.WOODEN))
    print(Structure('rc'))
    print(Structure.RC.value)
