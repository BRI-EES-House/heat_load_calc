from enum import Enum
from typing import Dict
import logging
import numpy as np
import math
from abc import ABC, abstractmethod


from heat_load_calc.tenum import EStory, EStructure, EInsidePressure, EInfiltrationMethod, ECValueEstimateMethod
from heat_load_calc.input_models.input_building import InputBuilding
from heat_load_calc.input_models.input_infiltration import InputInfiltration

logger = logging.getLogger('HeatLoadCalc').getChild('building')





class AirTightness(ABC):

    def __init__(self):
        pass
    
    @classmethod
    def create(cls, ipt_infiltration: InputInfiltration):
        """create AirTightness class

        Args:
            ipt_infiltration: InputInfiltration class
        """

        #match d['method']:
        match ipt_infiltration.method:

            #case 'balance_residential':
            case EInfiltrationMethod.BALANCE_RESIDENTIAL:

                return AirTightnessBalanceResidential(ipt_infiltration=ipt_infiltration)
            
            case _:

                raise KeyError('Item "method" in "infiltration" is NOT defined.')

    @abstractmethod
    def get_v_leak_is_n(self, theta_r_is_n: np.ndarray, theta_o_n: float, v_r_is: np.ndarray) -> np.ndarray:
        pass


class AirTightnessBalanceResidential(AirTightness):

    def __init__(self, ipt_infiltration: InputInfiltration):
        """create AirTightnessBalanceResidential Class

        Args:
            ipt_infiltration: InputInfiltration Class
        """

        ipt = ipt_infiltration

        super().__init__()

        self._story = ipt.story

        match ipt_infiltration.c_value_estimate:

            case ECValueEstimateMethod.SPECIFY:

                c = ipt.c_value
            
            case ECValueEstimateMethod.CALCULATE:

                c = _estimate_c_value(u_a=ipt.ua_value, struct=ipt.struct)
            
            case _:
                raise Exception()

        self._c = c

        self._inside_pressure = ipt.inside_pressure        

    
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
        bar_theta_r_n = self._get_bar_theta_r_n(theta_r_is_n=theta_r_is_n, v_r_is=v_r_is)

        # air temperature difference between room and outdoor at step n, K
        delta_theta_n = self._get_delta_theta_n(bar_theta_r_n=bar_theta_r_n, theta_o_n=theta_o_n)

        # ventilation rate of air leakage at step n, 1/h
        n_leak_n = self._get_n_leak_n(c_value=self._c, story=self._story, inside_pressure=self._inside_pressure, delta_theta_n=delta_theta_n)

        # leakage air volume of rooms at step n, m3/s, [i, 1]
        v_leak_is_n = self._get_v_leak_is_n(n_leak_n=n_leak_n, v_r_is=v_r_is)

        return v_leak_is_n

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def _get_n_leak_n(
            c_value: float,
            story: EStory,
            inside_pressure: EInsidePressure,
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
            EStory.ONE: 0.022,
            # 2階建ての時の係数
            EStory.TWO: 0.020
        }[story]

        # 係数bの計算, 回/h
        # 階数と換気方式の組み合わせで決定する
        b_2 = {
            EInsidePressure.BALANCED: {
                EStory.ONE: 0.00,
                EStory.TWO: 0.0
            }[story],
            EInsidePressure.POSITIVE: {
                EStory.ONE: 0.26,
                EStory.TWO: 0.14
            }[story],
            EInsidePressure.NEGATIVE: {
                EStory.ONE: 0.28,
                EStory.TWO: 0.13
            }[story]
        }[inside_pressure]

        # 換気回数の計算
        # Note: 切片bの符号は-が正解（報告書は間違っている）
        n_leak_n = np.maximum(b_1 * (c_value * math.sqrt(delta_theta_n)) - b_2, 0)

        return n_leak_n

    @staticmethod
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


class Building:

    def __init__(self, air_tightness: AirTightness):

        self._air_tightness = air_tightness

    @classmethod
    def create_building(cls, ipt_building: InputBuilding):

        ipt_infiltration: InputInfiltration = ipt_building.ipt_infiltration

        air_tightness = AirTightness.create(ipt_infiltration=ipt_infiltration)

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


def _estimate_c_value(u_a: float, struct: EStructure) -> float:
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
        EStructure.RC: 4.16,       # RC造
        EStructure.SRC: 4.16,      # SRC造
        EStructure.WOODEN: 8.28,   # 木造
        EStructure.STEEL: 8.28,    # 鉄骨造
    }[struct]

    return a * u_a


