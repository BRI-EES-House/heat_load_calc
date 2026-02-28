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
from heat_load_calc.tenum import BoundaryType

@dataclass
class InputBoundary:

    # id
    id: int

    # name
    name: str

    # sub name (default = '')
    sub_name: str

    # room id connected to this surface
    connected_room_id: int

    # boundary type
    boundary_type: BoundaryType

    # surface area, m2 (>0.0)
    area: float

    @classmethod
    def read(cls, d_boundary: dict):
        
        id = cls._get_id(d_boundary=d_boundary)

        name = cls._get_name(d_boundary=d_boundary)

        sub_name = cls._get_sub_name(d_boundary=d_boundary)

        connected_room_id = cls._get_connected_room_id(d_boundary=d_boundary)

        boundary_type = cls._get_boundary_type(d_boundary=d_boundary)

        area = cls._get_area(d_boundary=d_boundary)

        return InputBoundary(
            id=id,
            name=name,
            sub_name=sub_name,
            connected_room_id=connected_room_id,
            boundary_type=boundary_type,
            area=area
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
    def _get_name(d_boundary: dict):

        if 'name' not in d_boundary:
            raise KeyError(KNE('name', 'boundary'))
        
        name = str(d_boundary['name'])
        
        return name
    
    @staticmethod
    def _get_sub_name(d_boundary: dict):

        sub_name = str(d_boundary.get('sub_name', ''))

        return sub_name

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
    
    @staticmethod
    def _get_boundary_type(d_boundary: dict):

        if 'boundary_type' not in d_boundary:
            raise KeyError(KNE('boundary_type', 'boundary'))
        
        try:
            boundary_type = BoundaryType(d_boundary['boundary_type'])
        except ValueError:
            raise ValueError(VI('boundary_type', 'boundary'))
        
        return boundary_type

    @staticmethod
    def _get_area(d_boundary: dict):

        if 'area' not in d_boundary:
            raise KeyError(KNE('area', 'boundary'))
        
        try:
            area = float(d_boundary['area'])
        except ValueError:
            raise ValueError(VI('area', 'boundary'))
        
        if area <= 0.0:
            raise ValueError(RGT('area', 'boundary', 0.0))
        
        return area

        