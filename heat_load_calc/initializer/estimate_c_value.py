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

    a = {
        Structure.RC: 4.07,       # RC造
        Structure.SRC: 4.07,      # SRC造
        Structure.WOODEN: 17.1,   # 木造
        Structure.STEEL: 17.1,    # 鉄骨造
    }[struct]

    return a * ua_value


if __name__ == '__main__':
    print(estimate_c_value(0.5, Structure.WOODEN))
    print(Structure('rc'))
    print(Structure.RC.value)
