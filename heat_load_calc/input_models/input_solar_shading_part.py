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
    def read(cls, d: dict, direction: Direction):

        if 'existence' not in d:

            raise KeyError(KNE('existence', 'solar_shading_part'))
                
        match d['existence']:

            case True:

                if direction in [Direction.TOP, Direction.BOTTOM]:
                    raise ValueError('\'existence\' of solar shading shall be false when the direction of surface is top or bottom.')
                
                if 'input_method' not in d:
                    raise KeyError(KNE('input_method', 'solar_shading_part'))
                
                match d['input_method']:

                    case 'simple':
                        return InputSolarShadingPartSimple.read(d=d)
                    
                    case 'detail':
                        return InputSolarShadingPartDetail.read(d=d)
                    
                    case _:
                        raise ValueError(VI('input_method', 'solar_shading_part'))

            case False:
                return InputSolarShadingPartNot.read()

            case _:
                raise ValueError(VI('existence', 'solar_shading_part'))
        

@dataclass
class InputSolarShadingPartSimple(InputSolarShadingPart):

    depth: float

    d_h: float

    d_e: float

    @classmethod
    def read(cls, d: dict):

        if 'depth' not in d:
            raise KeyError(KNE('depth', 'solar_shading_part'))
        
        try:
            depth = float(d['depth'])
        except:
            raise ValueError(VI('depth', 'solar_shading_part'))
        
        if depth < 0.0:
            raise ValueError( RGE('depth', 'solar_shading_part', 0.0))

        if 'd_h' not in d:
            raise KeyError(KNE('d_h', 'solar_shading_part'))
        
        try:
            d_h = float(d['d_h'])
        except:
            raise ValueError(VI('d_h', 'solar_shading_part'))
        
        if d_h < 0.0:
            raise ValueError(RGE('d_h', 'solar_shading_part', 0.0))

        if 'd_e' not in d:
            raise KeyError(KNE('d_e', 'solar_shading_part'))
        
        try:
            d_e = float(d['d_e'])
        except:
            raise ValueError(VI('d_e', 'solar_shading_part'))
        
        if d_e < 0.0:
            raise ValueError(RGE('d_e', 'solar_shading_part', 0.0))

        return InputSolarShadingPartSimple(
            existence=True,
            depth=depth,
            d_h=d_h,
            d_e=d_e
        )


@dataclass
class InputSolarShadingPartDetail(InputSolarShadingPart):

    x1: float
    x2: float
    x3: float
    y1: float
    y2: float
    y3: float
    z_x_pls: float
    z_x_mns: float
    z_y_pls: float
    z_y_mns: float
    
    @classmethod
    def read(cls, d: dict):

        if 'x1' not in d:
            raise KeyError(KNE('x1', 'solar_shading_part'))
        
        try:
            x1 = float(d['x1'])
        except:
            raise ValueError(VI('x1', 'solar_shading_part'))
        
        if x1 < 0.0:
            raise ValueError(RGE('x1', 'solar_shading_part', 0.0))
        
        if 'x2' not in d:
            raise KeyError(KNE('x2', 'solar_shading_part'))
        
        try:
            x2 = float(d['x2'])
        except:
            raise ValueError(VI('x2', 'solar_shading_part'))
        
        if x2 < 0.0:
            raise ValueError(RGE('x2', 'solar_shading_part', 0.0))
        
        if 'x3' not in d:
            raise KeyError(KNE('x3', 'solar_shading_part'))
        
        try:
            x3 = float(d['x3'])
        except:
            raise ValueError(VI('x3', 'solar_shading_part'))
        
        if x3 < 0.0:
            raise ValueError(RGE('x3', 'solar_shading_part', 0.0))
        
        if 'y1' not in d:
            raise KeyError(KNE('y1', 'solar_shading_part'))
        
        try:
            y1 = float(d['y1'])
        except:
            raise ValueError(VI('y1', 'solar_shading_part'))
        
        if y1 < 0.0:
            raise ValueError(RGE('y1', 'solar_shading_part', 0.0))
        
        if 'y2' not in d:
            raise KeyError(KNE('y2', 'solar_shading_part'))
        
        try:
            y2 = float(d['y2'])
        except:
            raise ValueError(VI('y2', 'solar_shading_part'))
        
        if y2 < 0.0:
            raise ValueError(RGE('y2', 'solar_shading_part', 0.0))
        
        if 'y3' not in d:
            raise KeyError(KNE('y3', 'solar_shading_part'))
        
        try:
            y3 = float(d['y3'])
        except:
            raise ValueError(VI('y3', 'solar_shading_part'))
        
        if y3 < 0.0:
            raise ValueError(RGE('y3', 'solar_shading_part', 0.0))
        
        if 'z_x_pls' not in d:
            raise KeyError(KNE('z_x_pls', 'solar_shading_part'))
        
        try:
            z_x_pls = float(d['z_x_pls'])
        except:
            raise ValueError(VI('z_x_pls', 'solar_shading_part'))
        
        if z_x_pls < 0.0:
            raise ValueError(RGE('z_x_pls', 'solar_shading_part', 0.0))

        if 'z_x_mns' not in d:
            raise KeyError(KNE('z_x_mns', 'solar_shading_part'))
        
        try:
            z_x_mns = float(d['z_x_mns'])
        except:
            raise ValueError(VI('z_x_mns', 'solar_shading_part'))

        if z_x_mns < 0.0:
            raise ValueError(RGE('z_x_mns', 'solar_shading_part', 0.0))
        
        if 'z_y_pls' not in d:
            raise KeyError(KNE('z_y_pls', 'solar_shading_part'))
        
        try:
            z_y_pls = float(d['z_y_pls'])
        except:
            raise ValueError(VI('z_y_pls', 'solar_shading_part'))
        
        if z_y_pls < 0.0:
            raise ValueError(RGE('z_y_pls', 'solar_shading_part', 0.0))
        
        if 'z_y_mns' not in d:
            raise KeyError(KNE('z_y_mns', 'solar_shading_part'))
        
        try:
            z_y_mns = float(d['z_y_mns'])
        except:
            raise ValueError(VI('z_y_mns', 'solar_shading_part'))
        
        if z_y_mns < 0.0:
            raise ValueError(RGE('z_y_mns', 'solar_shading_part', 0.0))
        
        return InputSolarShadingPartDetail(
            existence=True,
            x1=x1,
            x2=x2,
            x3=x3,
            y1=y1,
            y2=y2,
            y3=y3,
            z_x_pls=z_x_pls,
            z_x_mns=z_x_mns,
            z_y_pls=z_y_pls,
            z_y_mns=z_y_mns
        )


@dataclass
class InputSolarShadingPartNot(InputSolarShadingPart):

    @classmethod
    def read(cls):

        return InputSolarShadingPartNot(
            existence=False
        )


