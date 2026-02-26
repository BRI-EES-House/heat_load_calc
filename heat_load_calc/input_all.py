from heat_load_calc.error_message import (
    key_not_exists as KNE,
    value_invalid as VI,
    value_out_of_range_GE as RGE,
    value_out_of_range_LE as RLE,
    value_out_of_range_GT as RGT,
    value_out_of_range_LT as RLT
)
from heat_load_calc.input_models.input_common import InputCommon
from heat_load_calc.input_models.input_building import InputBuilding
from heat_load_calc.input_models.input_room import InputRoom
from heat_load_calc.input_models.input_boundary import InputBoundary

class InputAll:

    def __init__(self, d: dict):

        if 'common' not in d:
            raise KeyError(KNE('common', 'root'))
        
        d_common = d['common']

        if 'building' not in d:
            raise KeyError(KNE('building', 'root'))
        
        d_building = d['building']

        if 'rooms' not in d:
            raise KeyError(KNE('rooms', 'root'))

        d_rooms = d['rooms']

        if not isinstance(d_rooms, list):
            raise TypeError(VI('rooms', 'root'))
        
        if 'boundaries' not in d:
            raise KeyError(KNE('boundaries', 'root'))
        
        d_boundaries = d['boundaries']

        if not isinstance(d_boundaries, list):
            raise TypeError(VI('boundaries', 'root'))
        

        self.ipt_common: InputCommon = InputCommon.read(d_common=d_common)

        self.ipt_building: InputBuilding = InputBuilding.read(d_building=d_building)

        self.ipt_rooms: list[InputRoom] = [InputRoom.read(d_room=d_room) for d_room in d_rooms]

        self.ipt_boundaries: list[InputBoundary] = [InputBoundary.read(d_boundary=d_boundary) for d_boundary in d_boundaries]
