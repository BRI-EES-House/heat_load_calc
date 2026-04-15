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
from heat_load_calc.tenum import EBoundaryType, EGlassType
from heat_load_calc.direction import Direction
from heat_load_calc.input_models.input_solar_shading_part import InputSolarShadingPart, InputSolarShadingPartSimple, InputSolarShadingPartDetail, InputSolarShadingPartNot
from heat_load_calc.input_models.input_layer import InputLayer


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

    # is inside solar radiation absorbed of boundary j
    is_solar_absorbed_inside: bool

    # is boundary j floor
    is_floor: bool

    @classmethod
    def read(cls, d: dict):
        
        boundary_type = cls._get_boundary_type(d=d)

        match boundary_type:
        
            case EBoundaryType.EXTERNAL_GENERAL_PART:

                return InputBoundaryExternalGeneralPart.read(d=d)
            
            case EBoundaryType.EXTERNAL_TRANSPARENT_PART:

                return InputBoundaryExternalTransparentPart.read(d=d)

            case EBoundaryType.EXTERNAL_OPAQUE_PART:

                return InputBoundaryExternalOpaquePart.read(d=d)

            case EBoundaryType.GROUND:

                return InputBoundaryGround.read(d=d)
            
            case EBoundaryType.INTERNAL:

                return InputBoundaryInternal.read(d=d)

            case _:

                raise Exception()
    
    @staticmethod
    def _get_id(d: dict):

        if 'id' not in d:
            raise KeyError(KNE('id', 'boundary'))
        
        try:
            id = int(d['id'])
        except ValueError:
            raise ValueError(VI('id', 'boundary'))
        
        if id < 0:
            raise ValueError(RGE('id', 'boundary', '0'))

        return id
    
    @staticmethod
    def _get_name(d: dict):

        if 'name' not in d:
            raise KeyError(KNE('name', 'boundary'))
        
        name = str(d['name'])
        
        return name
    
    @staticmethod
    def _get_sub_name(d: dict):

        sub_name = str(d.get('sub_name', ''))

        return sub_name

    @staticmethod
    def _get_connected_room_id(d: dict):

        if 'connected_room_id' not in d:
            raise KeyError(KNE('connected_room_id', 'boundary'))
        
        try:
            connecte_room_id = int(d['connected_room_id'])
        except ValueError:
            raise ValueError(VI('connected_room_id', 'boundary'))
        
        if connecte_room_id < 0:
            raise ValueError(RGE('connected_room_id', 'boundary', '0'))

        return connecte_room_id
    
    @staticmethod
    def _get_boundary_type(d: dict):

        if 'boundary_type' not in d:
            raise KeyError(KNE('boundary_type', 'boundary'))
        
        try:
            boundary_type = EBoundaryType(d['boundary_type'])
        except ValueError:
            raise ValueError(VI('boundary_type', 'boundary'))
        
        return boundary_type

    @staticmethod
    def _get_area(d: dict):

        if 'area' not in d:
            raise KeyError(KNE('area', 'boundary'))
        
        try:
            area = float(d['area'])
        except ValueError:
            raise ValueError(VI('area', 'boundary'))
        
        if area <= 0.0:
            raise ValueError(RGT('area', 'boundary', '0.0'))
        
        return area

    @staticmethod
    def _get_inside_emissivity(d: dict):

        try:
            inside_emissivity = float(d.get('inside_emissivity', 0.9))
        except ValueError:
            raise ValueError(VI('inside_emissivity', 'boundary'))
    
        if inside_emissivity < 0.0:
            raise ValueError(RGE('inside_emissivity', 'boundary', '0.0'))
        
        if inside_emissivity > 1.0:
            raise ValueError(RLE('inside_emissivity', 'boundary', '0.0'))
        
        return inside_emissivity

    @staticmethod
    def _get_h_c(d: dict):

        if 'h_c' not in d:
            raise KeyError(KNE('h_c', 'boundary'))
        
        try:
            h_c = float(d['h_c'])
        except ValueError:
            raise ValueError(VI('h_c', 'boundary'))
        
        if h_c <= 0.0:
            raise ValueError(RGE('h_c', 'boundary', '0.0'))
        
        return h_c
    
    @staticmethod
    def _get_temp_dif_coef(d: dict):

        if 'temp_dif_coef' not in d:
            raise KeyError(KNE('temp_dif_coef', 'boundary'))

        try:
            temp_dif_coef = float(d['temp_dif_coef'])
        except ValueError:
            raise ValueError(VI('temp_dif_coef', 'boundary'))
        
        if temp_dif_coef > 1.0:
            raise ValueError(RLE('temp_dif_coef', 'boundary', '1.0'))
        
        if temp_dif_coef < 0.0:
            raise ValueError(RGE('temp_dif_coef', 'boundary', '0.0'))
        
        return temp_dif_coef
    
    @staticmethod
    def _get_is_solar_absorbed_inside(d: dict):

        if 'is_solar_absorbed_inside' not in d:
            raise KeyError(KNE('is_solar_absorbed_inside', 'boundary'))
        
        match d['is_solar_absorbed_inside']:
            case True:
                return True
            case False:
                return False
            case _:
                raise ValueError(VI('is_solar_absorbed_inside', 'boundary'))
    
    @staticmethod
    def _get_is_floor(d: dict):

        if 'is_floor' not in d:
            raise KeyError(KNE('is_floor', 'boundary'))
        
        match d['is_floor']:
            case True:
                return True
            case False:
                return False
            case _:
                raise ValueError(VI('is_floor', 'boundary'))

    @staticmethod
    def _get_rear_surface_boundary_id(d: dict):

        if 'rear_surface_boundary_id' not in d:
            raise KeyError(KNE('rear_surface_boundary_id', 'boundary'))
        
        try:
            rear_surface_boundary_id = int(d['rear_surface_boundary_id'])
        except ValueError:
            raise ValueError(VI('rear_surface_boundary_id', 'boundary'))
        
        if rear_surface_boundary_id < 0:
            raise ValueError(RGE('rear_surface_boundary_id', 'boundary', '0'))
        
        return rear_surface_boundary_id
    
    @staticmethod
    def _get_is_sun_striked_outside(d: dict):

        if 'is_sun_striked_outside' not in d:
            raise KeyError(KNE('is_sun_striked_outside', 'boundary'))
        
        match d['is_sun_striked_outside']:
            case True:
                return True
            case False:
                return False
            case _:
                raise ValueError(VI('is_sun_striked_outside', 'boundary'))            

    @staticmethod
    def _get_direction(d: dict, is_sun_striked_outside: bool):

        if is_sun_striked_outside:

            if 'direction' not in d:
                raise KeyError(KNE('direction', 'boundary'))
            
            try:
                direction = Direction(d['direction'])
            except ValueError:
                raise ValueError(VI('direction', 'boundary'))
        
            return direction
        
        else:
            
            return None
    
    @staticmethod
    def _get_solar_shading_part(d: dict, direction: Direction, is_sun_striked_outside: bool):

        if is_sun_striked_outside:

            if 'solar_shading_part' not in d:
                raise KeyError(KNE('solar_shading_part', 'boundary'))
            
            if not isinstance(d['solar_shading_part'], dict):
                raise ValueError(VI('solar_shading_part', 'boundary'))
            
            solar_shading_part = InputSolarShadingPart.read(d=d['solar_shading_part'], direction=direction)

            return solar_shading_part
        
        else:

            return None
    
    @staticmethod
    def _get_outside_solar_absorption(d: dict):

        if 'outside_solar_absorption' not in d:
            raise KeyError(KNE('outside_solar_absorption', 'boundary'))
        
        try:
            outside_solar_absorption = float(d['outside_solar_absorption'])
        except ValueError:
            raise ValueError(VI('outside_solar_absorption', 'boundary'))
        
        if outside_solar_absorption < 0.0:
            raise ValueError(RGE('outside_solar_absorption', 'boundary', '0.0'))
        
        if outside_solar_absorption > 1.0:
            raise ValueError(RLE('outside_solar_absorption', 'boundary', '1.0'))
        
        return outside_solar_absorption
    
    @staticmethod
    def _get_outside_heat_transfer_resistance(d: dict):

        if 'outside_heat_transfer_resistance' not in d:
            raise KeyError(KNE('outside_heat_transfer_resistance', 'boundary'))
        
        try:
            outside_heat_transfer_resistance = float(d['outside_heat_transfer_resistance'])
        except ValueError:
            raise ValueError(VI('outside_heat_transfer_resistance', 'boundary'))
        
        if outside_heat_transfer_resistance < 0.0:
            raise ValueError(RGE('outside_heat_transfer_resistance', 'boundary', '0.0'))
        
        return outside_heat_transfer_resistance
    
    @staticmethod
    def _get_outside_emissivity(d: dict):

        if 'outside_emissivity' not in d:
            raise KeyError(KNE('outside_emissivity', 'boundary'))
        
        try:
            outside_emissivity = float(d['outside_emissivity'])
        except ValueError:
            raise ValueError(VI('outside_emissivity', 'boundary'))
        
        if outside_emissivity > 1.0:
            raise ValueError(RLE('outside_emissivity', 'boundary', 1.0))
        
        if outside_emissivity < 0.0:
            raise ValueError(RGE('outside_emissivity', 'boundary', 0.0))
        
        return outside_emissivity
    
    @staticmethod
    def _get_u_value(d: dict):

        if 'u_value' not in d:
            raise KeyError(KNE('u_value', 'boundary'))
        
        try:
            u_value = float(d['u_value'])
        except ValueError:
            raise ValueError(VI('u_value', 'boundary'))
        
        if u_value <= 0.0:
            raise ValueError(RGT('u_value', 'boundary', 0.0))
        
        return u_value
    
    @staticmethod
    def _get_eta_value(d: dict):

        if 'eta_value' not in d:
            raise KeyError(KNE('eta_value', 'boundary'))
        
        try:
            eta_value = float(d['eta_value'])
        except ValueError:
            raise ValueError(VI('eta_value', 'boundary'))
        
        if eta_value <= 0.0:
            raise ValueError(RGT('eta_value', 'boundary', 0.0))
        
        if eta_value >= 1.0:
            raise ValueError(RLT('eta_value', 'boundary',1.0))
        
        return eta_value
    
    @staticmethod
    def _get_glass_area_ratio(d: dict):

        if 'glass_area_ratio' not in d:
            raise KeyError(KNE('glass_area_ratio', 'boundary'))
        
        try:
            glass_area_ratio = float(d['glass_area_ratio'])
        except ValueError:
            raise ValueError(VI('glass_area_ratio', 'boundary'))

        if glass_area_ratio <= 0.0:
            raise ValueError(RGT('glass_area_ratio', 'boundary', '0.0'))
        
        if glass_area_ratio > 1.0:
            raise ValueError(RLE('glass_area_ratio', 'boundary', '1.0'))
        
        return glass_area_ratio

    @staticmethod
    def _get_incident_angle_characteristics(d: dict):

        if 'incident_angle_characteristics' not in d:
            raise KeyError(KNE('incident_angle_characteristics', 'boundary'))

        try:
            incident_angle_characteristics = EGlassType(d['incident_angle_characteristics'])
        except ValueError:
            raise ValueError(VI('incident_angle_characteristics', 'boundary'))
        
        return incident_angle_characteristics
    
    @staticmethod
    def _get_layers(d: dict):

        if 'layers' not in d:
            raise KeyError(KNE('layers', 'boundary'))
        
        try:
            d_layers = d['layers']
        except ValueError:
            raise ValueError(VI('layers', 'boundary'))
        
        if not isinstance(d_layers, list):
            raise TypeError(VI('layers', 'boundary'))
        
        ipt_layers = [InputLayer.read(d=d_layer) for d_layer in d_layers]

        return ipt_layers
        


@dataclass
class InputBoundaryExternalGeneralPart(InputBoundary):

    temp_dif_coef: float

    is_sun_striked_outside: bool

    direction: Direction

    solar_shading_part: InputSolarShadingPart

    outside_solar_absorption: float

    outside_heat_transfer_resistance: float

    outside_emissivity: float

    ipt_layers: list[InputLayer]

    @classmethod
    def read(cls, d: dict):

        id = cls._get_id(d=d)

        name = cls._get_name(d=d)

        sub_name = cls._get_sub_name(d=d)

        connected_room_id = cls._get_connected_room_id(d=d)

        boundary_type = cls._get_boundary_type(d=d)

        area = cls._get_area(d=d)

        inside_emissivity = cls._get_inside_emissivity(d=d)

        h_c = cls._get_h_c(d=d)

        is_solar_absorbed_inside = cls._get_is_solar_absorbed_inside(d=d)

        is_floor = cls._get_is_floor(d=d)
        
        temp_dif_coef = cls._get_temp_dif_coef(d=d)

        is_sun_striked_outside = cls._get_is_sun_striked_outside(d=d)

        direction = cls._get_direction(d=d, is_sun_striked_outside=is_sun_striked_outside)

        solar_shading_part = cls._get_solar_shading_part(d=d, direction=direction, is_sun_striked_outside=is_sun_striked_outside)

        outside_solar_absorption = cls._get_outside_solar_absorption(d=d)

        outside_heat_transfer_resistance = cls._get_outside_heat_transfer_resistance(d=d)

        outside_emissivity = cls._get_outside_emissivity(d=d)

        ipt_layers = cls._get_layers(d=d)

        return InputBoundaryExternalGeneralPart(
            id=id,
            name=name,
            sub_name=sub_name,
            connected_room_id=connected_room_id,
            boundary_type=boundary_type,
            area=area,
            inside_emissivity=inside_emissivity,
            h_c=h_c,
            is_solar_absorbed_inside=is_solar_absorbed_inside,
            is_floor=is_floor,
            temp_dif_coef=temp_dif_coef,
            is_sun_striked_outside=is_sun_striked_outside,
            direction=direction,
            solar_shading_part=solar_shading_part,
            outside_solar_absorption=outside_solar_absorption,
            outside_heat_transfer_resistance=outside_heat_transfer_resistance,
            outside_emissivity=outside_emissivity,
            ipt_layers=ipt_layers
        )


@dataclass
class InputBoundaryExternalTransparentPart(InputBoundary):

    temp_dif_coef: float

    is_sun_striked_outside: bool

    direction: Direction

    solar_shading_part: InputSolarShadingPart

    outside_heat_transfer_resistance: float

    outside_emissivity: float

    u_value: float

    eta_value: float

    glass_area_ratio: float

    incident_angle_characteristics: EGlassType

    @classmethod
    def read(cls, d: dict):

        id = cls._get_id(d=d)

        name = cls._get_name(d=d)

        sub_name = cls._get_sub_name(d=d)

        connected_room_id = cls._get_connected_room_id(d=d)

        boundary_type = cls._get_boundary_type(d=d)

        area = cls._get_area(d=d)

        inside_emissivity = cls._get_inside_emissivity(d=d)

        h_c = cls._get_h_c(d=d)

        is_solar_absorbed_inside = cls._get_is_solar_absorbed_inside(d=d)

        is_floor = cls._get_is_floor(d=d)

        temp_dif_coef = cls._get_temp_dif_coef(d=d)

        is_sun_striked_outside = cls._get_is_sun_striked_outside(d=d)

        direction = cls._get_direction(d=d, is_sun_striked_outside=is_sun_striked_outside)

        solar_shading_part = cls._get_solar_shading_part(d=d, direction=direction, is_sun_striked_outside=is_sun_striked_outside)

        outside_heat_transfer_resistance = cls._get_outside_heat_transfer_resistance(d=d)

        outside_emissivity = cls._get_outside_emissivity(d=d)

        u_value = cls._get_u_value(d=d)

        eta_value = cls._get_eta_value(d=d)

        glass_area_ratio = cls._get_glass_area_ratio(d=d)

        incident_angle_characteristics = cls._get_incident_angle_characteristics(d=d)

        return InputBoundaryExternalTransparentPart(
            id=id,
            name=name,
            sub_name=sub_name,
            connected_room_id=connected_room_id,
            boundary_type=boundary_type,
            area=area,
            inside_emissivity=inside_emissivity,
            h_c=h_c,
            is_solar_absorbed_inside=is_solar_absorbed_inside,
            is_floor=is_floor,
            temp_dif_coef=temp_dif_coef,
            is_sun_striked_outside=is_sun_striked_outside,
            direction=direction,
            solar_shading_part=solar_shading_part,
            outside_heat_transfer_resistance=outside_heat_transfer_resistance,
            outside_emissivity=outside_emissivity,
            u_value=u_value,
            eta_value=eta_value,
            glass_area_ratio=glass_area_ratio,
            incident_angle_characteristics=incident_angle_characteristics
        )


@dataclass
class InputBoundaryExternalOpaquePart(InputBoundary):

    temp_dif_coef: float

    is_sun_striked_outside: bool

    direction: Direction

    solar_shading_part: InputSolarShadingPart

    outside_solar_absorption: float

    outside_heat_transfer_resistance: float

    outside_emissivity: float

    u_value: float

    @classmethod
    def read(cls, d: dict):

        id = cls._get_id(d=d)

        name = cls._get_name(d=d)

        sub_name = cls._get_sub_name(d=d)

        connected_room_id = cls._get_connected_room_id(d=d)

        boundary_type = cls._get_boundary_type(d=d)

        area = cls._get_area(d=d)

        inside_emissivity = cls._get_inside_emissivity(d=d)

        h_c = cls._get_h_c(d=d)

        is_solar_absorbed_inside = cls._get_is_solar_absorbed_inside(d=d)

        is_floor = cls._get_is_floor(d=d)

        temp_dif_coef = cls._get_temp_dif_coef(d=d)

        is_sun_striked_outside = cls._get_is_sun_striked_outside(d=d)

        direction = cls._get_direction(d=d, is_sun_striked_outside=is_sun_striked_outside)

        solar_shading_part = cls._get_solar_shading_part(d=d, direction=direction, is_sun_striked_outside=is_sun_striked_outside)

        outside_solar_absorption = cls._get_outside_solar_absorption(d=d)

        outside_heat_transfer_resistance = cls._get_outside_heat_transfer_resistance(d=d)

        outside_emissivity = cls._get_outside_emissivity(d=d)

        u_value = cls._get_u_value(d=d)

        return InputBoundaryExternalOpaquePart(
            id=id,
            name=name,
            sub_name=sub_name,
            connected_room_id=connected_room_id,
            boundary_type=boundary_type,
            area=area,
            inside_emissivity=inside_emissivity,
            h_c=h_c,
            is_solar_absorbed_inside=is_solar_absorbed_inside,
            is_floor=is_floor,
            temp_dif_coef=temp_dif_coef,
            is_sun_striked_outside=is_sun_striked_outside,
            direction=direction,
            solar_shading_part=solar_shading_part,
            outside_solar_absorption=outside_solar_absorption,
            outside_heat_transfer_resistance=outside_heat_transfer_resistance,
            outside_emissivity=outside_emissivity,
            u_value=u_value
        )


@dataclass
class InputBoundaryGround(InputBoundary):

    ipt_layers: list[InputLayer]

    @classmethod
    def read(cls, d: dict):

        id = cls._get_id(d=d)

        name = cls._get_name(d=d)

        sub_name = cls._get_sub_name(d=d)

        connected_room_id = cls._get_connected_room_id(d=d)

        boundary_type = cls._get_boundary_type(d=d)

        area = cls._get_area(d=d)

        inside_emissivity = cls._get_inside_emissivity(d=d)

        h_c = cls._get_h_c(d=d)

        is_solar_absorbed_inside = cls._get_is_solar_absorbed_inside(d=d)

        is_floor = cls._get_is_floor(d=d)

        ipt_layers = cls._get_layers(d=d)

        return InputBoundaryGround(
            id=id,
            name=name,
            sub_name=sub_name,
            connected_room_id=connected_room_id,
            boundary_type=boundary_type,
            area=area,
            inside_emissivity=inside_emissivity,
            h_c=h_c,
            is_solar_absorbed_inside=is_solar_absorbed_inside,
            is_floor=is_floor,
            ipt_layers=ipt_layers
        )


@dataclass
class InputBoundaryInternal(InputBoundary):

    rear_surface_boundary_id: int

    ipt_layers: list[InputLayer]

    @classmethod
    def read(cls, d: dict):

        id = cls._get_id(d=d)

        name = cls._get_name(d=d)

        sub_name = cls._get_sub_name(d=d)

        connected_room_id = cls._get_connected_room_id(d=d)

        boundary_type = cls._get_boundary_type(d=d)

        area = cls._get_area(d=d)

        inside_emissivity = cls._get_inside_emissivity(d=d)

        h_c = cls._get_h_c(d=d)

        is_solar_absorbed_inside = cls._get_is_solar_absorbed_inside(d=d)

        is_floor = cls._get_is_floor(d=d)

        rear_surface_boundary_id = cls._get_rear_surface_boundary_id(d=d)

        ipt_layers = cls._get_layers(d=d)

        return InputBoundaryInternal(
            id=id,
            name=name,
            sub_name=sub_name,
            connected_room_id=connected_room_id,
            boundary_type=boundary_type,
            area=area,
            inside_emissivity=inside_emissivity,
            h_c=h_c,
            is_solar_absorbed_inside=is_solar_absorbed_inside,
            is_floor=is_floor,
            rear_surface_boundary_id=rear_surface_boundary_id,
            ipt_layers=ipt_layers
        )

