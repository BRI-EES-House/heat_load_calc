from dataclasses import dataclass
from abc import ABC, abstractmethod


from heat_load_calc.error_message import (
    key_not_exists as KNE,
    value_invalid as VI,
    value_out_of_range_GE as RGE,
    value_out_of_range_LE as RLE,
    value_out_of_range_GT as RGT,
    value_out_of_range_LT as RLT
)

@dataclass
class InputBoundary:

    id: int

    connected_room_id: int

    @classmethod
    def read(cls, d_boundary: dict):
        
        id = cls._get_id(d_boundary=d_boundary)

        connected_room_id = cls._get_connected_room_id(d_boundary=d_boundary)

        return InputBoundary(
            id=id,
            connected_room_id=connected_room_id
        )
    
    @staticmethod
    def _get_id(d_boundary: dict):

        if 'id' not in d_boundary:
            raise KeyError(KNE('id', 'boundary'))
        
        try:
            id = int(d_boundary['id'])
        except ValueError:
            raise ValueError(VI('id', 'boundary'))
        
        if id < 0:
            raise ValueError(RGE('id', 'boundary', 0))

        return id
    

    @staticmethod
    def _get_connected_room_id(d_boundary: dict):

        if 'connected_room_id' not in d_boundary:
            raise KeyError(KNE('connected_room_id', 'boundary'))
        
        try:
            connecte_room_id = int(d_boundary['connected_room_id'])
        except ValueError:
            raise ValueError(VI('connected_room_id', 'boundary'))
        
        if connecte_room_id < 0:
            raise ValueError(RGE('connected_room_id', 'boundary', 0))

        return connecte_room_id
    

