from dataclasses import dataclass


from heat_load_calc.error_message import (
    key_not_exists as KNE,
    value_invalid as VI,
    value_out_of_range_GE as RGE,
    value_out_of_range_LE as RLE,
    value_out_of_range_GT as RGT,
    value_out_of_range_LT as RLT
)


@dataclass
class InputLayer:

    name: str

    thermal_resistance: float

    thermal_capacity: float

    @staticmethod
    def _get_name(d: dict):

        if 'name' not in d:
            raise KeyError(KNE('name', 'layer'))
        
        name = str(d['name'])

        return name

    @staticmethod
    def _get_thermal_capacity(d: dict):

        if 'thermal_capacity' not in d:
            raise KeyError(KNE('thermal_capacity', 'layer'))

        try:
            thermal_capacity = float(d['thermal_capacity']) 
        except:
            raise ValueError(VI('thermal_capacity', 'layer'))

        if thermal_capacity < 0.0:
            raise ValueError(RGE('thermal_capacity', 'layer', '0.0'))
        
        return thermal_capacity

    @staticmethod
    def _get_thermal_resistance(d: dict):

        if 'thermal_resistance' not in d:
            raise KeyError(KNE('thermal_resistance', 'layer'))

        try:
            thermal_resistance = float(d['thermal_resistance']) 
        except:
            raise ValueError(VI('thermal_resistance', 'layer'))

        if thermal_resistance <= 0.0:
            raise ValueError(RGT('thermal_resistance', 'layer', '0.0'))
        
        return thermal_resistance

    @classmethod
    def read(cls, d: dict):

        name = cls._get_name(d=d)

        thermal_capacity = cls._get_thermal_capacity(d=d)

        thermal_resistance = cls._get_thermal_resistance(d=d)

        return InputLayer(
            name=name,
            thermal_resistance=thermal_resistance,
            thermal_capacity=thermal_capacity
        )

