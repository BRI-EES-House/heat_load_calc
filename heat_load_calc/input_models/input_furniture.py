from dataclasses import dataclass
from abc import ABC, abstractmethod
from heat_load_calc.tenum import EFurnitureSpecifyMethod
from heat_load_calc.error_message import (
    key_not_exists as mKNE,
    value_invalid as mVI,
    value_out_of_range_GT as mORGT,
    value_out_of_range_GE as mORGE,
    value_out_of_range_LE as mORLE
)


@dataclass
class InputFurniture(ABC):
    
    # solar absorption ratio of furniture, >= 0.0 and <= 1.0
    solar_absorption_ratio: float

    @classmethod
    def read(cls, d_furniture: dict):

        if 'input_method' not in d_furniture:
            raise KeyError(mKNE('input_method', 'furniture'))
        
        try:
            method = EFurnitureSpecifyMethod(d_furniture['input_method'])
        except ValueError:
            raise ValueError(mVI('input_method', 'furniture'))

        match method:

            case EFurnitureSpecifyMethod.DEFAULT:

                return InputFurnitureDefault.read(d_furniture=d_furniture)
            
            case EFurnitureSpecifyMethod.SPECIFY:

                return InputFurnitureSpecify.read(d_furniture=d_furniture)
    
    @staticmethod
    def get_solar_absorption_ratio(d_furniture: dict):

        try:
            solar_absorption_ratio = float(d_furniture.get('solar_absorption_ratio', 0.5))
        except:
            raise ValueError(mVI('solar_absorption_ratio', 'furniture'))

        if solar_absorption_ratio < 0.0:
            raise ValueError(mORGE('solar_absorption_ratio', 'furniture', '0.0'))

        if solar_absorption_ratio > 1.0:
            raise ValueError(mORLE('solar_absorption_ratio', 'furniture', '1.0'))
        
        return solar_absorption_ratio


@dataclass
class InputFurnitureDefault(InputFurniture):

    @classmethod
    def read(cls, d_furniture: dict):
        solar_absorption_ratio = InputFurniture.get_solar_absorption_ratio(d_furniture=d_furniture)

        return InputFurnitureDefault(
            solar_absorption_ratio=solar_absorption_ratio
        )


@dataclass
class InputFurnitureSpecify(InputFurniture):

    # thermal capacity of furniture, J/K
    heat_capacity: float

    # thermal conductance between air and furniture, W/K
    heat_cond: float

    # moisture capacity of furniture, kg/(kg/kgDA)
    moisture_capacity: float

    # moisture conductance between air and furniture, kg/(s (kg/kgDA))
    moisture_cond: float

    @classmethod
    def read(cls, d_furniture: dict):

        if 'heat_capacity' not in d_furniture:
            raise KeyError(mKNE('heat_capacity', 'furniture'))
        
        try:
            heat_capacity = float(d_furniture['heat_capacity'])
        except:
            raise ValueError(mVI('heat_capacity', 'furniture'))
        
        if heat_capacity <= 0.0:
            raise ValueError(mORGT('heat_capacity', 'furniture', '0.0'))
        
        if 'heat_cond' not in d_furniture:
            raise KeyError(mKNE('heat_cond', 'furniture'))
        
        try:
            heat_cond = float(d_furniture['heat_cond'])
        except:
            raise ValueError(mVI('heat_cond', 'furniture'))
        
        if heat_cond <= 0.0:
            raise ValueError(mORGT('heat_cond', 'furniture', '0.0'))
            
        if 'moisture_capacity' not in d_furniture:
            raise KeyError(mKNE('moisture_capacity', 'furniture'))
        
        try:
            moisture_capacity = float(d_furniture['moisture_capacity'])
        except:
            raise ValueError(mVI('moisture_capacity', 'furniture'))
        
        if moisture_capacity <= 0.0:
            raise ValueError(mORGT('moisture_capacity', 'furniture', '0.0'))

        if 'moisture_cond' not in d_furniture:
            raise KeyError(mKNE('moisture_cond', 'furniture'))
        
        try:
            moisture_cond = float(d_furniture['moisture_cond'])
        except:
            raise ValueError(mVI('moisture_cond', 'furniture'))
        
        if moisture_cond <= 0.0:
            raise ValueError(mORGT('moisture_cond', 'furniture', '0.0'))
        
        solar_absorption_ratio = InputFurniture.get_solar_absorption_ratio(d_furniture=d_furniture)

        return InputFurnitureSpecify(
            heat_capacity=heat_capacity,
            heat_cond=heat_cond,
            moisture_capacity=moisture_capacity,
            moisture_cond=moisture_cond,
            solar_absorption_ratio=solar_absorption_ratio
        )
