from enum import Enum
from typing import Dict
import logging
import numpy as np
import math


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


class AirTightness:

    def __init__(self):
        pass
    
    @classmethod
    def create(cls, d:Dict):
        """_summary_

        Args:
            d: input data (d['building']['infiltration'])
        """

        match d['method']:

            case 'balance_residential':
                return AirTightnessBalanceResidential(d=d)
            
            case _:
                raise KeyError('Item "method" in "infiltration" is NOT defined.')

    def get_v_leak_is_n(self, theta_r_is_n: np.ndarray, theta_o_n: float, v_r_is: np.ndarray) -> np.ndarray:
        pass


class AirTightnessBalanceResidential(AirTightness):

    def __init__(self, d: Dict):
        """_summary_

        Args:
            d: input data (d['building']['infiltration'])
        """

        super().__init__()

        if 'story' not in d:
            raise KeyError('Item "story" is NOT defined in Air Tightness Balance Residential calculation.')

        self._story = Story(d['story'])

        if 'c_value_estimate' not in d:
            raise KeyError('Item "c_value_estimate" is NOT defined in Air Tightness Balance Residential calculation.')
        
        match d['c_value_estimate']:
            
            case 'specify':
                c = float(d['c_value'])
            
            case 'calculate':
                c = _estimate_c_value(u_a=d['ua_value'], struct=Structure(d['struct']))
            
            case _:
                raise KeyError('Wrong name is identified in the item "c_value_estimate".')
        
        self._c = c

        if 'inside_pressure' not in d:
            raise KeyError('Item "inside_pressure" is NOT defined in Air Tightness Balance Residential calculation.')
        
        self._inside_pressure = InsidePressure(d['inside_pressure'])
    
    def get_v_leak_is_n(self, theta_r_is_n: np.ndarray, theta_o_n: float, v_r_is: np.ndarray) -> np.ndarray:
        """Calculate the leakage air volume
        This calculation is approx. expression based on the elaborate results obtained by solving for pressure balance
        Args:
            theta_r_is_n: air temperature in room i in step n, degree C, [I,1]
            theta_o_n: outdoor temperature at step n, degree C
            v_r_is: room volume of room i, m3, [I,1]
        Returns:
            leakage air volume of rooms at step n, m3/s, [I,1]
        """

        # average air temperature at step n which is weghted by room volumes, degree C
        bar_theta_r_n = _get_bar_theta_r_n(theta_r_is_n=theta_r_is_n, v_r_is=v_r_is)

        # air temperature difference between room and outdoor at step n, K
        delta_theta_n = _get_delta_theta_n(bar_theta_r_n=bar_theta_r_n, theta_o_n=theta_o_n)

        # ventilation rate of air leakage at step n, 1/h
        n_leak_n = _get_n_leak_n(c_value=self._c, story=self._story, inside_pressure=self._inside_pressure, delta_theta_n=delta_theta_n)

        # leakage air volume of rooms at step n, m3/s, [i, 1]
        v_leak_is_n = _get_v_leak_is_n(n_leak_n=n_leak_n, v_r_is=v_r_is)

        return v_leak_is_n


class Building:

    def __init__(self, air_tightness: AirTightness):

        self._air_tightness = air_tightness

    @classmethod
    def create_building(cls, d: Dict):

        d_infiltration = d['infiltration']

        air_tightness = AirTightness.create(d=d_infiltration)

        return Building(air_tightness=air_tightness)

    def get_v_leak_is_n(
            self,
            theta_r_is_n: np.ndarray,
            theta_o_n: float,
            v_r_is: np.ndarray,
    ):
        """Calculate the leakage air volume
        This calculation is approx. expression based on the elaborate results obtained by solving for pressure balance
        Args:
            theta_r_is_n: air temperature in room i in step n, degree C, [I,1]
            theta_o_n: outdoor temperature at step n, degree C
            v_r_is: room volume of room i, m3, [I,1]
        Returns:
            leakage air volume of rooms at step n, m3/s, [I,1]
        """

        # leakage air volume of rooms at step n, m3/s, [i, 1]
        v_leak_is_n = self._air_tightness.get_v_leak_is_n(theta_r_is_n=theta_r_is_n, theta_o_n=theta_o_n, v_r_is=v_r_is)
    
        return v_leak_is_n


def _estimate_c_value(u_a: float, struct: Structure) -> float:
    """Estimate C value.
    Args
        ua_value: UA value, W/m2 K
        struct: structure(RC, SRC, Wooden, Steel)
    Returns:
        C value, cm2/m2
    Note:
        eq.1
    """

    a = {
        Structure.RC: 4.16,       # RC造
        Structure.SRC: 4.16,      # SRC造
        Structure.WOODEN: 8.28,   # 木造
        Structure.STEEL: 8.28,    # 鉄骨造
    }[struct]

    return a * u_a


def _get_v_leak_is_n(n_leak_n: float, v_r_is: np.ndarray) -> np.ndarray:
    """calculate leakage air volume of rooms at step n
    Args:
        n_leak_n: ventilation rate of air leakage at step n, 1/h
        v_r_is: volume of rooms, m3, [I, 1]
    Returns:
        air leakage volume of rooms at step n, m3/s, [I, 1]
    Note:
        eq.2
    """

    v_leak_is_n = n_leak_n * v_r_is / 3600

    return v_leak_is_n


def _get_n_leak_n(
        c_value: float,
        story: Story,
        inside_pressure: InsidePressure,
        delta_theta_n: float
) -> float:
    """Calculate the leakage air volume
    This calculation is approx. expression based on the elaborate results obtained by solving for pressure balance
    Args:
        c_value: equivalent leakage area (C value), cm2/m2
        story: story
        inside_pressure: inside pressure against outdoor pressure
            'negative': negative pressure
            'positive': positive pressure
            'balanced': balanced
    Returns:
        ventilation rate of air leakage at step n, 1/h
    Note:
        eq.3    
    """

    # 係数aの計算, 回/(h (cm2/m2 K^0.5))
    b_1 = {
        # 1階建ての時の係数
        Story.ONE: 0.022,
        # 2階建ての時の係数
        Story.TWO: 0.020
    }[story]

    # 係数bの計算, 回/h
    # 階数と換気方式の組み合わせで決定する
    b_2 = {
        InsidePressure.BALANCED: {
            Story.ONE: 0.00,
            Story.TWO: 0.0
        }[story],
        InsidePressure.POSITIVE: {
            Story.ONE: 0.26,
            Story.TWO: 0.14
        }[story],
        InsidePressure.NEGATIVE: {
            Story.ONE: 0.28,
            Story.TWO: 0.13
        }[story]
    }[inside_pressure]

    # 換気回数の計算
    # Note: 切片bの符号は-が正解（報告書は間違っている）
    n_leak_n = np.maximum(b_1 * (c_value * math.sqrt(delta_theta_n)) - b_2, 0)

    return n_leak_n


def _get_delta_theta_n(bar_theta_r_n: float, theta_o_n: float) -> float:
    """Calculate the temperature difference between room and outside.

    Args:
        bar_theta_r_n: averate room temperature at step n, degree C
        theta_o_n: outside temperature at step n, degree C

    Returns:
        air temperature difference between room and outside at step n, K
    
    Notes:
        eq.4
    """

    delta_theta_n = abs(bar_theta_r_n - theta_o_n)

    return delta_theta_n


def _get_bar_theta_r_n(theta_r_is_n: np.ndarray, v_r_is: np.ndarray) -> float:
    """Calculate the average air temperature at step n which is weghted by room volumes.

    Args:
        theta_r_is_n: air temperature in room i at step n, degree C, [i, 1]
        v_r_is: volume of room i, m3, [i, 1]

    Returns:
        average air temperature at step n, degree C

    Note:
        eq.5
    """

    bar_theta_r_n = np.average(theta_r_is_n, weights=v_r_is)

    return bar_theta_r_n

