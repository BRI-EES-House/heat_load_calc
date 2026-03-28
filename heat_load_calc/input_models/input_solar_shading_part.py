from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
import os


from heat_load_calc.error_message import (
    key_not_exists as KNE,
    value_invalid as VI,
    value_out_of_range_GE as RGE,
    value_out_of_range_LE as RLE,
    value_out_of_range_GT as RGT,
    value_out_of_range_LT as RLT
)
from heat_load_calc.tenum import ENumberOfOccupants, EScheduleType
from heat_load_calc.direction import Direction


@dataclass
class InputSolarShadingPart(ABC):
    
    existence: bool

    @classmethod
    def read(cls, id: int, d: dict, dict: Direction):

        if 'existence' not in d:

            raise KeyError(KNE('existence', 'solar_shading_part'))
                
        match d['existence']:

            case True:

                if dict in [Direction.TOP, Direction.BOTTOM]:
                    raise ValueError('\'existence\' of solar shading shall be false when the direction of surface is top or bottom.')
                
                if 'input_method' not in d:
                    raise KeyError(KNE('input_method', 'solar_shading_part'))
                
                match d['input_method']:

                    case 'simple':
                        return InputSolarShadingPartSimple.read(d=d)
                    
                    case 'detail':
                    
                    case _:
                        raise ValueError(VI('input_method', 'solar_shading_part'))

            case False:
                return InputSolarShadingPartNot.read()

            case _:
                raise ValueError(VI('existence', 'solar_shading_part'))
        

@dataclass
class InputSolarShadingPartNot(InputSolarShadingPart):

    @classmethod
    def read(cls):

        InputSolarShadingPartNot(
            existence=False
        )


@dataclass
class InputSolarShadingPartSimple(InputSolarShadingPart):

    depth: float

    d_h: float

    d_e: float

    @classmethod
    def read(cls, d: dict):

        if 'depth' not in d:
            raise KeyError(KNE('depth', 'sloar_shading_part'))
        
        try:
            depth = float(['depth'])
        except:
            raise ValueError(VI('depth', 'solar_shadeing_part'))
        
        if depth < 0.0:
            raise ValueError(VI('depth', 'solar_shadeing_part'))
        depth = d['depth']
        d_h = d['d_h']
        d_e = d['d_e']


        InputSolarShadingPartSimple(
            existence=True,
            depth=depth,
            d_h=d_h,
            d_e=d_e
        )