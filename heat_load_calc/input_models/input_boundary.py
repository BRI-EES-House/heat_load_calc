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
from heat_load_calc.tenum import EBoundaryType

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
    boundary_type: EBoundaryType

    # surface area, m2 (>0.0)
    area: float

    # inside emissivity at the surface, (1.0>= and >=0.0)
    inside_emissivity: float

    # inside surface convective heat transfer coefficient, W/m2K (>0.0)
    h_c: float

    @classmethod
    def read(cls, d_boundary: dict):
        
        id = cls._get_id(d_boundary=d_boundary)

        name = cls._get_name(d_boundary=d_boundary)

        sub_name = cls._get_sub_name(d_boundary=d_boundary)

        connected_room_id = cls._get_connected_room_id(d_boundary=d_boundary)

        boundary_type = cls._get_boundary_type(d_boundary=d_boundary)

        area = cls._get_area(d_boundary=d_boundary)

        inside_emissivity = cls._get_inside_emissivity(d_boundary=d_boundary)

        h_c = cls._get_h_c(d_boundary=d_boundary)

        match boundary_type:
        
            case EBoundaryType.EXTERNAL_GENERAL_PART:

                return InputBoundaryExternalGeneralPart.read(d_boundary=d_boundary)
            
            case EBoundaryType.EXTERNAL_TRANSPARENT_PART:

                return InputBoundaryExternalTransparentPart.read(d_boundary=d_boundary)

            case EBoundaryType.EXTERNAL_OPAQUE_PART:

                return InputBoundaryExternalOpaquePart.read(d_boundary=d_boundary)

            case EBoundaryType.GROUND:

                return InputBoundaryGround.read(d_boundary=d_boundary)
            
            case EBoundaryType.INTERNAL:

                return InputBoundaryInternal.read(d_boundary=d_boundary)

            case _:

                raise Exception()
    
    @staticmethod
    def _get_id(d_boundary: dict):

        if 'id' not in d_boundary:
            raise KeyError(KNE('id', 'boundary'))
        
        try:
            id = int(d_boundary['id'])
        except ValueError:
            raise ValueError(VI('id', 'boundary'))
        
        if id < 0:
            raise ValueError(RGE('id', 'boundary', '0'))

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
            raise ValueError(RGE('connected_room_id', 'boundary', '0'))

        return connecte_room_id
    
    @staticmethod
    def _get_boundary_type(d_boundary: dict):

        if 'boundary_type' not in d_boundary:
            raise KeyError(KNE('boundary_type', 'boundary'))
        
        try:
            boundary_type = EBoundaryType(d_boundary['boundary_type'])
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
            raise ValueError(RGT('area', 'boundary', '0.0'))
        
        return area

    @staticmethod
    def _get_inside_emissivity(d_boundary: dict):

        try:
            inside_emissivity = float(d_boundary.get('inside_emissivity', 0.9))
        except ValueError:
            raise ValueError(VI('inside_emissivity', 'boundary'))
    
        if inside_emissivity < 0.0:
            raise ValueError(RGE('inside_emissivity', 'boundary', '0.0'))
        
        if inside_emissivity > 1.0:
            raise ValueError(RLE('inside_emissivity', 'boundary', '0.0'))
        
        return inside_emissivity

    @staticmethod
    def _get_h_c(d_boundary: dict):

        if 'h_c' not in d_boundary:
            raise KeyError(KNE('h_c', 'boundary'))
        
        try:
            h_c = float(d_boundary['h_c'])
        except ValueError:
            raise ValueError(VI('h_c', 'boundary'))
        
        if h_c <= 0.0:
            raise ValueError(RGE('h_c', 'boundary', '0.0'))
        
        return h_c
    
    @staticmethod
    def _get_temp_dif_coef(d_boundary: dict):

        if 'temp_dif_coef' not in d_boundary:
            raise KeyError(KNE('temp_dif_coef', 'boundary'))

        try:
            temp_dif_coef = float(d_boundary['temp_dif_coef'])
        except ValueError:
            raise ValueError(VI('temp_dif_coef', 'boundary'))
        
        if temp_dif_coef > 1.0:
            raise ValueError(RLE('temp_dif_coef', 'boundary', '1.0'))
        
        if temp_dif_coef < 0.0:
            raise ValueError(RGE('temp_dif_coef', 'boundary', '0.0'))
        
        return temp_dif_coef


@dataclass
class InputBoundaryExternalGeneralPart(InputBoundary):

    temp_dif_coef: float

    @classmethod
    def read(cls, d_boundary: dict):

        id = cls._get_id(d_boundary=d_boundary)

        name = cls._get_name(d_boundary=d_boundary)

        sub_name = cls._get_sub_name(d_boundary=d_boundary)

        connected_room_id = cls._get_connected_room_id(d_boundary=d_boundary)

        boundary_type = cls._get_boundary_type(d_boundary=d_boundary)

        area = cls._get_area(d_boundary=d_boundary)

        inside_emissivity = cls._get_inside_emissivity(d_boundary=d_boundary)

        h_c = cls._get_h_c(d_boundary=d_boundary)

        temp_dif_coef = cls._get_temp_dif_coef(d_boundary=d_boundary)

        return InputBoundaryExternalGeneralPart(
            id=id,
            name=name,
            sub_name=sub_name,
            connected_room_id=connected_room_id,
            boundary_type=boundary_type,
            area=area,
            inside_emissivity=inside_emissivity,
            h_c=h_c,
            temp_dif_coef=temp_dif_coef
        )


@dataclass
class InputBoundaryExternalTransparentPart(InputBoundary):

    temp_dif_coef: float

    @classmethod
    def read(cls, d_boundary: dict):

        id = cls._get_id(d_boundary=d_boundary)

        name = cls._get_name(d_boundary=d_boundary)

        sub_name = cls._get_sub_name(d_boundary=d_boundary)

        connected_room_id = cls._get_connected_room_id(d_boundary=d_boundary)

        boundary_type = cls._get_boundary_type(d_boundary=d_boundary)

        area = cls._get_area(d_boundary=d_boundary)

        inside_emissivity = cls._get_inside_emissivity(d_boundary=d_boundary)

        h_c = cls._get_h_c(d_boundary=d_boundary)

        temp_dif_coef = cls._get_temp_dif_coef(d_boundary=d_boundary)

        return InputBoundaryExternalTransparentPart(
            id=id,
            name=name,
            sub_name=sub_name,
            connected_room_id=connected_room_id,
            boundary_type=boundary_type,
            area=area,
            inside_emissivity=inside_emissivity,
            h_c=h_c,
            temp_dif_coef=temp_dif_coef
        )


@dataclass
class InputBoundaryExternalOpaquePart(InputBoundary):

    temp_dif_coef: float

    @classmethod
    def read(cls, d_boundary: dict):

        id = cls._get_id(d_boundary=d_boundary)

        name = cls._get_name(d_boundary=d_boundary)

        sub_name = cls._get_sub_name(d_boundary=d_boundary)

        connected_room_id = cls._get_connected_room_id(d_boundary=d_boundary)

        boundary_type = cls._get_boundary_type(d_boundary=d_boundary)

        area = cls._get_area(d_boundary=d_boundary)

        inside_emissivity = cls._get_inside_emissivity(d_boundary=d_boundary)

        h_c = cls._get_h_c(d_boundary=d_boundary)

        temp_dif_coef = cls._get_temp_dif_coef(d_boundary=d_boundary)

        return InputBoundaryExternalOpaquePart(
            id=id,
            name=name,
            sub_name=sub_name,
            connected_room_id=connected_room_id,
            boundary_type=boundary_type,
            area=area,
            inside_emissivity=inside_emissivity,
            h_c=h_c,
            temp_dif_coef=temp_dif_coef
        )


@dataclass
class InputBoundaryGround(InputBoundary):

    @classmethod
    def read(cls, d_boundary: dict):

        id = cls._get_id(d_boundary=d_boundary)

        name = cls._get_name(d_boundary=d_boundary)

        sub_name = cls._get_sub_name(d_boundary=d_boundary)

        connected_room_id = cls._get_connected_room_id(d_boundary=d_boundary)

        boundary_type = cls._get_boundary_type(d_boundary=d_boundary)

        area = cls._get_area(d_boundary=d_boundary)

        inside_emissivity = cls._get_inside_emissivity(d_boundary=d_boundary)

        h_c = cls._get_h_c(d_boundary=d_boundary)

        return InputBoundaryGround(
            id=id,
            name=name,
            sub_name=sub_name,
            connected_room_id=connected_room_id,
            boundary_type=boundary_type,
            area=area,
            inside_emissivity=inside_emissivity,
            h_c=h_c
        )


@dataclass
class InputBoundaryInternal(InputBoundary):

    @classmethod
    def read(cls, d_boundary: dict):

        id = cls._get_id(d_boundary=d_boundary)

        name = cls._get_name(d_boundary=d_boundary)

        sub_name = cls._get_sub_name(d_boundary=d_boundary)

        connected_room_id = cls._get_connected_room_id(d_boundary=d_boundary)

        boundary_type = cls._get_boundary_type(d_boundary=d_boundary)

        area = cls._get_area(d_boundary=d_boundary)

        inside_emissivity = cls._get_inside_emissivity(d_boundary=d_boundary)

        h_c = cls._get_h_c(d_boundary=d_boundary)

        return InputBoundaryInternal(
            id=id,
            name=name,
            sub_name=sub_name,
            connected_room_id=connected_room_id,
            boundary_type=boundary_type,
            area=area,
            inside_emissivity=inside_emissivity,
            h_c=h_c
        )

