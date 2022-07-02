from enum import Enum
from typing import Dict
import logging


logger = logging.getLogger('HeatLoadCalc').getChild('building')

class Story(Enum):
    """
    建物の階数（共同住宅の場合は住戸の階数）
    """
    # 1階
    ONE = 1
    # 2階（2階以上の階数の場合も2階とする。）
    TWO = 2


class InsidePressure(Enum):
    """
    室内圧力
    """
    # 正圧
    POSITIVE = 'positive'
    # 負圧
    NEGATIVE = 'negative'
    # ゼロバランス
    BALANCED = 'balanced'


class Structure(Enum):
    """構造を表す列挙型
    """

    RC = 'rc'
    SRC = 'src'
    WOODEN = 'wooden'
    STEEL = 'steel'


class Building:

    def __init__(self, infiltration_method: str, story: Story, c_value: float, inside_pressure: InsidePressure):

        self._infiltration_method = infiltration_method
        self._story = story
        self._c_value = c_value
        self._inside_pressure = inside_pressure

    @classmethod
    def create_building(cls, d: Dict):

        ifl = d['infiltration']

        ifl_method = ifl['method']

        if ifl_method == 'balance_residential':

            # 建物の階数
            story = Story(ifl['story'])

            # C値
            if ifl['c_value_estimate'] == 'specify':

                c_value = ifl['c_value']

            elif ifl['c_value_estimate'] == 'calculate':

                c_value = cls._estimate_c_value(ua_value=ifl['ua_value'], struct=Structure(ifl['struct']))

            else:

                raise ValueError()

            # 換気の種類
            inside_pressure = InsidePressure(ifl['inside_pressure'])

        else:

            raise KeyError()

        return Building(
            infiltration_method=ifl_method,
            story=story,
            c_value=c_value,
            inside_pressure=inside_pressure
        )

    @property
    def infiltration_method(self):
        return self._infiltration_method

    @property
    def story(self):
        return self._story

    @property
    def c_value(self):
        return self._c_value

    @property
    def inside_pressure(self):
        return self._inside_pressure

    @classmethod
    def _estimate_c_value(cls, ua_value: float, struct: Structure):

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

