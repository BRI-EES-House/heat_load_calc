import pytest

from heat_load_calc.error_message import (
    key_not_exists as KNE,
    value_invalid as VI,
    value_out_of_range_GE as RGE,
    value_out_of_range_LE as RLE,
    value_out_of_range_GT as RGT,
    value_out_of_range_LT as RLT
)
from heat_load_calc.input_models.input_boundary import (
    InputBoundary,
    InputBoundaryExternalGeneralPart,
    InputBoundaryExternalTransparentPart,
    InputBoundaryExternalOpaquePart,
    InputBoundaryGround,
    InputBoundaryInternal
)
from heat_load_calc.tenum import EBoundaryType, EGlassType
from heat_load_calc.direction import Direction


def get_default_dict():

    return {
        'id': 0,
        'name': 'test',
        'sub_name': 'sub_test',
        'connected_room_id': 0,
        'boundary_type': 'external_general_part',
        'area': 3.0,
        'inside_emissivity': 0.92,
        'h_c': 2.5,
        'temp_dif_coef': 1.0,
        'is_solar_absorbed_inside': True,
        'is_floor': True,
        'is_sun_striked_outside': True,
        'direction': 's',
        'solar_shading_part': {
            'existence': False
        },
        'outside_solar_absorption': 0.7,
        'outside_heat_transfer_resistance': 0.04,
        'outside_emissivity': 0.9,
        'layers': [
            {
                'name': 'wood_board-12',
                'thermal_resistance': 0.075,
                'thermal_capacity': 8.64,
            },
            {
                "name": "hgw24k-100",
                "thermal_resistance": 2.777777777777778,
                "thermal_capacity": 2.0,
            }
        ]
    }


def get_default_dict_external_general_part():

    return get_default_dict()


def get_default_dict_external_transparent_part():

    return {
        'id': 0,
        'name': 'test',
        'sub_name': 'sub_test',
        'connected_room_id': 0,
        'boundary_type': 'external_transparent_part',
        'area': 3.0,
        'inside_emissivity': 0.92,
        'h_c': 2.5,
        'temp_dif_coef': 1.0,
        'is_solar_absorbed_inside': False,
        'is_floor': False,
        'is_sun_striked_outside': True,
        'direction': 's',
        'solar_shading_part': {
            'existence': False
        },
        'outside_heat_transfer_resistance': 0.04,
        'outside_emissivity': 0.9,
        'u_value': 4.65,
        'eta_value': 0.792,
        'glass_area_ratio': 0.8,
        'incident_angle_characteristics': 'multiple',
        'inside_heat_transfer_resistance': 0.11,
    }


def get_default_dict_external_opaque_part():

    return {
        'id': 0,
        'name': 'test',
        'sub_name': 'sub_test',
        'connected_room_id': 0,
        'boundary_type': 'external_opaque_part',
        'area': 3.0,
        'inside_emissivity': 0.92,
        'h_c': 2.5,
        'temp_dif_coef': 1.0,
        'is_solar_absorbed_inside': False,
        'is_floor': False,
        'is_sun_striked_outside': True,
        'direction': 's',
        'solar_shading_part': {
            'existence': False
        },
        'outside_solar_absorption': 0.7,
        'outside_heat_transfer_resistance': 0.04,
        'outside_emissivity': 0.9,
        'u_value': 4.65,
        'inside_heat_transfer_resistance': 0.11,
    }


def get_default_dict_ground():

    return {
        'id': 0,
        'name': 'test',
        'sub_name': 'sub_test',
        'connected_room_id': 0,
        'boundary_type': 'ground',
        'area': 3.0,
        'inside_emissivity': 0.92,
        'h_c': 2.5,
        'temp_dif_coef': 1.0,
        'is_solar_absorbed_inside': False,
        'is_floor': True,
        'layers': [
            {
                "name": "hgw24k-100",
                "thermal_resistance": 2.777777777777778,
                "thermal_capacity": 2.0,
            }
        ]
    }


def get_default_dict_internal():

    return {
        'id': 0,
        'name': 'test',
        'sub_name': 'sub_test',
        'connected_room_id': 0,
        'boundary_type': 'internal',
        'area': 3.0,
        'inside_emissivity': 0.92,
        'h_c': 2.5,
        'temp_dif_coef': 1.0,
        'rear_surface_boundary_id': 9,
        'is_solar_absorbed_inside': False,
        'is_floor': False,
        'layers': [
            {
                'name': 'wood_board-12',
                'thermal_resistance': 0.075,
                'thermal_capacity': 8.64,
            },
        ]
    }


def test_value__id__():

    d = get_default_dict()

    d['id'] = 99

    ipt = InputBoundary.read(d=d)

    assert ipt.id == 99


def test_key__id__not_exists():

    d = get_default_dict()

    del d['id']

    with pytest.raises(KeyError) as e:
        InputBoundary.read(d=d)
    
    assert KNE('id', 'boundary') in str(e.value)


def test_value__id__invalid():

    d = get_default_dict()

    d['id'] = 'test'

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d=d)
    
    assert VI('id', 'boundary') in str(e.value)


def test_value__id__out_of_range():

    d = get_default_dict()

    d['id'] = -1

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d=d)
    
    assert RGE('id', 'boundary', 0) in str(e.value)


def test_value__name__():

    d = get_default_dict()

    ipt = InputBoundary.read(d=d)

    assert ipt.name == 'test'


def test_value__name__not_exists():

    d = get_default_dict()

    del d['name']

    with pytest.raises(KeyError) as e:
        InputBoundary.read(d=d)
    
    assert KNE('name', 'boundary') in str(e.value)


def test_value__sub_name__():

    d = get_default_dict()

    ipt = InputBoundary.read(d=d)

    assert ipt.sub_name == 'sub_test'


def test_value__sub_name__default():

    d = get_default_dict()

    del d['sub_name']

    ipt = InputBoundary.read(d=d)

    assert ipt.sub_name == ''


def test_connected_room__id__():

    d = get_default_dict()

    d['connected_room_id'] = 99

    ipt = InputBoundary.read(d=d)

    assert ipt.connected_room_id == 99


def test_key__connected_room_id__not_exists():

    d = get_default_dict()

    del d['connected_room_id']

    with pytest.raises(KeyError) as e:
        InputBoundary.read(d=d)
    
    assert KNE('connected_room_id', 'boundary') in str(e.value)


def test_value__connected_room_id__invalid():

    d = get_default_dict()

    d['connected_room_id'] = 'test'

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d=d)
    
    assert VI('connected_room_id', 'boundary') in str(e.value)


def test_value__connected_room_id__out_of_range():

    d = get_default_dict()

    d['connected_room_id'] = -1

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d=d)
    
    assert RGE('connected_room_id', 'boundary', 0) in str(e.value)


def test_value__boundary_type__():

    d = get_default_dict()

    ipt = InputBoundary.read(d=d)

    assert ipt.boundary_type == EBoundaryType.EXTERNAL_GENERAL_PART


def test_key__boundary_type__not_exists():

    d = get_default_dict()

    del d['boundary_type']

    with pytest.raises(KeyError) as e:
        InputBoundary.read(d=d)
    
    assert KNE('boundary_type', 'boundary') in str(e.value)


def test_value__boundary_type__invalid():

    d = get_default_dict()

    d['boundary_type'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d=d)

    assert VI('boundary_type', 'boundary') in str(e.value)


def test_value__area__():

    d = get_default_dict()

    ipt = InputBoundary.read(d=d)

    assert ipt.area == 3.0


def test_key__area__not_exists():

    d = get_default_dict()

    del d['area']

    with pytest.raises(KeyError) as e:
        InputBoundary.read(d=d)
    
    assert KNE('area', 'boundary') in str(e.value)


def test_value__area__invalid():

    d = get_default_dict()

    d['area'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d=d)
    
    assert VI('area', 'boundary') in str(e.value)


def test_value__area__out_of_range():

    d = get_default_dict()

    d['area'] = 0.0

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d=d)

    assert RGT('area', 'boundary', 0.0) in str(e.value)


def test_value__inside_emissivity__():

    d = get_default_dict()

    ipt = InputBoundary.read(d=d)

    assert ipt.inside_emissivity == 0.92


def test_value__inside_emissivity__default():

    d = get_default_dict()

    del d['inside_emissivity']

    ipt = InputBoundary.read(d=d)

    assert ipt.inside_emissivity == 0.9


def test_value__inside_emissivity__wrong_value():

    d = get_default_dict()

    d['inside_emissivity'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d=d)
    
    assert VI('inside_emissivity', 'boundary') in str(e.value)


def test_value__inside_emissivity__out_of_range_1():

    d = get_default_dict()

    d['inside_emissivity'] = -0.1

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d=d)
    
    assert RGE('inside_emissivity', 'boundary', 0.0) in str(e.value)


def test_value__inside_emissivity__out_of_range_2():

    d = get_default_dict()

    d['inside_emissivity'] = 1.1

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d=d)
    
    assert RLE('inside_emissivity', 'boundary', 0.0) in str(e.value)


def test_value__h_c__():

    d = get_default_dict()

    ipt = InputBoundary.read(d=d)

    assert ipt.h_c == 2.5


def test_key__h_c__not_exists():

    d = get_default_dict()

    del d['h_c']

    with pytest.raises(KeyError) as e:
        InputBoundary.read(d=d)
    
    assert KNE('h_c', 'boundary') in str(e.value)


def test_value__h_c__invalid():

    d = get_default_dict()

    d['h_c'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d=d)
    
    assert VI('h_c', 'boundary') in str(e.value)


def test_value__h_c__out_of_range():

    d = get_default_dict()

    d['h_c'] = -0.1

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d=d)

    assert RGE('h_c', 'boundary', 0.0) in str(e.value)


def test_value__temp_dif_coef__():

    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    ipt1: InputBoundaryExternalGeneralPart = InputBoundary.read(d=d1)
    ipt2: InputBoundaryExternalTransparentPart = InputBoundary.read(d=d2)
    ipt3: InputBoundaryExternalOpaquePart = InputBoundary.read(d=d3)

    assert ipt1.temp_dif_coef == 1.0
    assert ipt2.temp_dif_coef == 1.0
    assert ipt3.temp_dif_coef == 1.0


def test_key__temp_dif_coef__not_exists():
    
    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    del d1['temp_dif_coef']
    del d2['temp_dif_coef']
    del d3['temp_dif_coef']

    with pytest.raises(KeyError) as e1:
        InputBoundary.read(d=d1)
    
    with pytest.raises(KeyError) as e2:
        InputBoundary.read(d=d2)

    with pytest.raises(KeyError) as e3:
        InputBoundary.read(d=d3)

    assert KNE('temp_dif_coef', 'boundary') in str(e1.value)

    assert KNE('temp_dif_coef', 'boundary') in str(e2.value)

    assert KNE('temp_dif_coef', 'boundary') in str(e3.value)


def test_value__temp_dif_coef__wrong_value():
    
    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    d1['temp_dif_coef'] = 'wrong_value'
    d2['temp_dif_coef'] = 'wrong_value'
    d3['temp_dif_coef'] = 'wrong_value'

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)
    
    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d=d2)

    with pytest.raises(ValueError) as e3:
        InputBoundary.read(d=d3)

    assert VI('temp_dif_coef', 'boundary') in str(e1.value)

    assert VI('temp_dif_coef', 'boundary') in str(e2.value)

    assert VI('temp_dif_coef', 'boundary') in str(e3.value)


def test_value__temp_dif_coef__out_of_range1():
    
    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    d1['temp_dif_coef'] = -0.1
    d2['temp_dif_coef'] = -0.1
    d3['temp_dif_coef'] = -0.1

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)
    
    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d=d2)

    with pytest.raises(ValueError) as e3:
        InputBoundary.read(d=d3)

    assert RGE('temp_dif_coef', 'boundary', 0.0) in str(e1.value)

    assert RGE('temp_dif_coef', 'boundary', 0.0) in str(e2.value)

    assert RGE('temp_dif_coef', 'boundary', 0.0) in str(e3.value)


def test_value__temp_dif_coef__out_of_range2():
    
    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    d1['temp_dif_coef'] = 1.1
    d2['temp_dif_coef'] = 1.1
    d3['temp_dif_coef'] = 1.1

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)
    
    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d=d2)

    with pytest.raises(ValueError) as e3:
        InputBoundary.read(d=d3)

    assert RLE('temp_dif_coef', 'boundary', 1.0) in str(e1.value)

    assert RLE('temp_dif_coef', 'boundary', 1.0) in str(e2.value)

    assert RLE('temp_dif_coef', 'boundary', 1.0) in str(e3.value)


def test_value__is_solar_absorbed_inside__():

    d = get_default_dict()

    ipt = InputBoundary.read(d=d)

    assert ipt.is_solar_absorbed_inside == True


def test_key__is_solar_absorbed_inside__not_exists():

    d = get_default_dict()

    del d['is_solar_absorbed_inside']

    with pytest.raises(KeyError) as e:
        InputBoundary.read(d=d)
    
    assert KNE('is_solar_absorbed_inside', 'boundary') in str(e.value)


def test_value__is_solar_absorbed_inside__invalid():

    d = get_default_dict()

    d['is_solar_absorbed_inside'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d=d)
    
    assert VI('is_solar_absorbed_inside', 'boundary') in str(e.value)


def test_key__is_floor__not_exists():

    d = get_default_dict()

    del d['is_floor']

    with pytest.raises(KeyError) as e:
        InputBoundary.read(d=d)
    
    assert KNE('is_floor', 'boundary') in str(e.value)


def test_value__is_floor__invalid():

    d = get_default_dict()

    d['is_floor'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d=d)
    
    assert VI('is_floor', 'boundary') in str(e.value)


def test_key__rear_surface_boundary_id__not_exists():
    
    d = get_default_dict_internal()

    del d['rear_surface_boundary_id']

    with pytest.raises(KeyError) as e:
        InputBoundary.read(d=d)
    
    assert KNE('rear_surface_boundary_id', 'boundary') in str(e.value)


def test_value__rear_surface_boundary_id__wrong_value():
    
    d = get_default_dict_internal()

    d['rear_surface_boundary_id'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d=d)
    
    assert VI('rear_surface_boundary_id', 'boundary') in str(e.value)


def test_value__rear_surface_boundary_id__out_of_range1():
    
    d = get_default_dict_internal()

    d['rear_surface_boundary_id'] = -1

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d=d)
    
    assert RGE('rear_surface_boundary_id', 'boundary', 0) in str(e.value)


def test_value__is_sun_striked_outside__():

    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    ipt1: InputBoundaryExternalGeneralPart = InputBoundary.read(d=d1)
    ipt2: InputBoundaryExternalTransparentPart = InputBoundary.read(d=d2)
    ipt3: InputBoundaryExternalOpaquePart = InputBoundary.read(d=d3)

    assert ipt1.is_sun_striked_outside == True
    assert ipt2.is_sun_striked_outside == True
    assert ipt3.is_sun_striked_outside == True


def test_key__is_sun_striked_outside__not_exists():
    
    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    del d1['is_sun_striked_outside']
    del d2['is_sun_striked_outside']
    del d3['is_sun_striked_outside']

    with pytest.raises(KeyError) as e1:
        InputBoundary.read(d=d1)
    
    with pytest.raises(KeyError) as e2:
        InputBoundary.read(d=d2)

    with pytest.raises(KeyError) as e3:
        InputBoundary.read(d=d3)

    assert KNE('is_sun_striked_outside', 'boundary') in str(e1.value)

    assert KNE('is_sun_striked_outside', 'boundary') in str(e2.value)

    assert KNE('is_sun_striked_outside', 'boundary') in str(e3.value)


def test_value__is_sun_striked_outside__wrong_value():
    
    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    d1['is_sun_striked_outside'] = 'wrong_value'
    d2['is_sun_striked_outside'] = 'wrong_value'
    d3['is_sun_striked_outside'] = 'wrong_value'

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)
    
    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d=d2)

    with pytest.raises(ValueError) as e3:
        InputBoundary.read(d=d3)

    assert VI('is_sun_striked_outside', 'boundary') in str(e1.value)

    assert VI('is_sun_striked_outside', 'boundary') in str(e2.value)

    assert VI('is_sun_striked_outside', 'boundary') in str(e3.value)


def test_value__direction__():
    
    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    ipt1: InputBoundaryExternalGeneralPart = InputBoundary.read(d=d1)
    ipt2: InputBoundaryExternalTransparentPart = InputBoundary.read(d=d2)
    ipt3: InputBoundaryExternalOpaquePart = InputBoundary.read(d=d3)

    assert ipt1.direction == Direction.S
    assert ipt2.direction == Direction.S
    assert ipt3.direction == Direction.S


def test_key__direction__not_exists():
    
    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()
    d4 = get_default_dict_external_general_part()
    d5 = get_default_dict_external_transparent_part()
    d6 = get_default_dict_external_opaque_part()

    del d1['direction']
    del d2['direction']
    del d3['direction']
    del d4['direction']
    del d5['direction']
    del d6['direction']

    d4['is_sun_striked_outside'] = False
    d5['is_sun_striked_outside'] = False
    d6['is_sun_striked_outside'] = False

    with pytest.raises(KeyError) as e1:
        InputBoundary.read(d=d1)
    
    with pytest.raises(KeyError) as e2:
        InputBoundary.read(d=d2)

    with pytest.raises(KeyError) as e3:
        InputBoundary.read(d=d3)

    assert KNE('direction', 'boundary') in str(e1.value)

    assert KNE('direction', 'boundary') in str(e2.value)

    assert KNE('direction', 'boundary') in str(e3.value)


def test_value__direction__wrong_value():
    
    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    d1['direction'] = 'wrong_value'
    d2['direction'] = 'wrong_value'
    d3['direction'] = 'wrong_value'

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)
    
    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d=d2)

    with pytest.raises(ValueError) as e3:
        InputBoundary.read(d=d3)

    assert VI('direction', 'boundary') in str(e1.value)

    assert VI('direction', 'boundary') in str(e2.value)

    assert VI('direction', 'boundary') in str(e3.value)


def test_key__solar_shading_part__not_exists():
    
    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    del d1['solar_shading_part']
    del d2['solar_shading_part']
    del d3['solar_shading_part']

    with pytest.raises(KeyError) as e1:
        InputBoundary.read(d=d1)
    
    with pytest.raises(KeyError) as e2:
        InputBoundary.read(d=d2)

    with pytest.raises(KeyError) as e3:
        InputBoundary.read(d=d3)

    assert KNE('solar_shading_part', 'boundary') in str(e1.value)

    assert KNE('solar_shading_part', 'boundary') in str(e2.value)

    assert KNE('solar_shading_part', 'boundary') in str(e3.value)


def test_value__solar_shading_part__invalid():
    
    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    d1['solar_shading_part'] = 'wrong_value'
    d2['solar_shading_part'] = 'wrong_value'
    d3['solar_shading_part'] = 'wrong_value'

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)
    
    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d=d2)

    with pytest.raises(ValueError) as e3:
        InputBoundary.read(d=d3)

    assert VI('solar_shading_part', 'boundary') in str(e1.value)

    assert VI('solar_shading_part', 'boundary') in str(e2.value)

    assert VI('solar_shading_part', 'boundary') in str(e3.value)


def test_value__outside_solar_absorption__():

    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_opaque_part()

    ipt1: InputBoundaryExternalGeneralPart = InputBoundary.read(d=d1)
    ipt2: InputBoundaryExternalOpaquePart = InputBoundary.read(d=d2)

    assert ipt1.outside_solar_absorption == 0.7
    assert ipt2.outside_solar_absorption == 0.7


def test_key__outside_solar_absorption__not_exists():
    
    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_opaque_part()

    del d1['outside_solar_absorption']
    del d2['outside_solar_absorption']

    with pytest.raises(KeyError) as e1:
        InputBoundary.read(d=d1)
    
    with pytest.raises(KeyError) as e2:
        InputBoundary.read(d=d2)

    assert KNE('outside_solar_absorption', 'boundary') in str(e1.value)

    assert KNE('outside_solar_absorption', 'boundary') in str(e2.value)


def test_value__outside_solar_absorption__wrong_value():
    
    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_opaque_part()

    d1['outside_solar_absorption'] = 'wrong_value'
    d2['outside_solar_absorption'] = 'wrong_value'

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)
    
    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d=d2)

    assert VI('outside_solar_absorption', 'boundary') in str(e1.value)

    assert VI('outside_solar_absorption', 'boundary') in str(e2.value)


def test_value__outside_solar_absorption__out_of_range1():
    
    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_opaque_part()

    d1['outside_solar_absorption'] = -0.1
    d2['outside_solar_absorption'] = -0.1

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)
    
    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d=d2)

    assert RGE('outside_solar_absorption', 'boundary', 0.0) in str(e1.value)

    assert RGE('outside_solar_absorption', 'boundary', 0.0) in str(e2.value)


def test_value__outside_solar_absorption__out_of_range2():
    
    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_opaque_part()

    d1['outside_solar_absorption'] = 1.1
    d2['outside_solar_absorption'] = 1.1

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)
    
    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d=d2)

    assert RLE('outside_solar_absorption', 'boundary', 1.0) in str(e1.value)

    assert RLE('outside_solar_absorption', 'boundary', 1.0) in str(e2.value)


def test_value__outside_heat_transfer_resistance__():

    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    ipt1: InputBoundaryExternalGeneralPart = InputBoundary.read(d=d1)
    ipt2: InputBoundaryExternalTransparentPart = InputBoundary.read(d=d2)
    ipt3: InputBoundaryExternalOpaquePart = InputBoundary.read(d=d3)

    assert ipt1.outside_heat_transfer_resistance == 0.04
    assert ipt2.outside_heat_transfer_resistance == 0.04
    assert ipt3.outside_heat_transfer_resistance == 0.04


def test_key__outside_heat_transfer_resistance__not_exists():

    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    del d1['outside_heat_transfer_resistance']
    del d2['outside_heat_transfer_resistance']
    del d3['outside_heat_transfer_resistance']

    with pytest.raises(KeyError) as e1:
        InputBoundary.read(d=d1)

    with pytest.raises(KeyError) as e2:
        InputBoundary.read(d=d2)

    with pytest.raises(KeyError) as e3:
        InputBoundary.read(d=d3)
    
    assert KNE('outside_heat_transfer_resistance', 'boundary') in str(e1.value)

    assert KNE('outside_heat_transfer_resistance', 'boundary') in str(e2.value)

    assert KNE('outside_heat_transfer_resistance', 'boundary') in str(e3.value)


def test_value__outside_heat_transfer_resistance__wrong_value():

    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    d1['outside_heat_transfer_resistance'] = 'wrong_value'
    d2['outside_heat_transfer_resistance'] = 'wrong_value'
    d3['outside_heat_transfer_resistance'] = 'wrong_value'

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)

    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d=d2)

    with pytest.raises(ValueError) as e3:
        InputBoundary.read(d=d3)

    assert VI('outside_heat_transfer_resistance', 'boundary') in str(e1.value)

    assert VI('outside_heat_transfer_resistance', 'boundary') in str(e2.value)

    assert VI('outside_heat_transfer_resistance', 'boundary') in str(e3.value)


def test_value__outside_heat_transfer_resistance__out_of_range():

    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    d1['outside_heat_transfer_resistance'] = -1
    d2['outside_heat_transfer_resistance'] = -1
    d3['outside_heat_transfer_resistance'] = -1

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)

    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d=d2)

    with pytest.raises(ValueError) as e3:
        InputBoundary.read(d=d3)

    assert RGE('outside_heat_transfer_resistance', 'boundary', '0.0') in str(e1.value)

    assert RGE('outside_heat_transfer_resistance', 'boundary', '0.0') in str(e2.value)

    assert RGE('outside_heat_transfer_resistance', 'boundary', '0.0') in str(e3.value)


def test_value__outside_emissivity__():

    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    ipt1: InputBoundaryExternalGeneralPart = InputBoundary.read(d=d1)
    ipt2: InputBoundaryExternalTransparentPart = InputBoundary.read(d=d2)
    ipt3: InputBoundaryExternalOpaquePart = InputBoundary.read(d=d3)

    assert ipt1.outside_emissivity == 0.9
    assert ipt2.outside_emissivity == 0.9
    assert ipt3.outside_emissivity == 0.9


def test_key__outside_emissivity__not_exists():

    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    del d1['outside_emissivity']
    del d2['outside_emissivity']
    del d3['outside_emissivity']

    with pytest.raises(KeyError) as e1:
        InputBoundary.read(d=d1)

    with pytest.raises(KeyError) as e2:
        InputBoundary.read(d=d2)

    with pytest.raises(KeyError) as e3:
        InputBoundary.read(d=d3)
    
    assert KNE('outside_emissivity', 'boundary') in str(e1.value)

    assert KNE('outside_emissivity', 'boundary') in str(e2.value)

    assert KNE('outside_emissivity', 'boundary') in str(e3.value)


def test_value__outside_emissivity__wrong_value():

    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    d1['outside_emissivity'] = 'wrong_value'
    d2['outside_emissivity'] = 'wrong_value'
    d3['outside_emissivity'] = 'wrong_value'

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)

    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d=d2)

    with pytest.raises(ValueError) as e3:
        InputBoundary.read(d=d3)

    assert VI('outside_emissivity', 'boundary') in str(e1.value)

    assert VI('outside_emissivity', 'boundary') in str(e2.value)

    assert VI('outside_emissivity', 'boundary') in str(e3.value)


def test_value__outside_emissivity__out_of_range1():

    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    d1['outside_emissivity'] = -1
    d2['outside_emissivity'] = -1
    d3['outside_emissivity'] = -1

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)

    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d=d2)

    with pytest.raises(ValueError) as e3:
        InputBoundary.read(d=d3)

    assert RGE('outside_emissivity', 'boundary', '0.0') in str(e1.value)

    assert RGE('outside_emissivity', 'boundary', '0.0') in str(e2.value)

    assert RGE('outside_emissivity', 'boundary', '0.0') in str(e3.value)


def test_value__outside_emissivity__out_of_range2():

    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    d1['outside_emissivity'] = 1.1
    d2['outside_emissivity'] = 1.1
    d3['outside_emissivity'] = 1.1

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)

    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d=d2)

    with pytest.raises(ValueError) as e3:
        InputBoundary.read(d=d3)

    assert RLE('outside_emissivity', 'boundary', '1.0') in str(e1.value)

    assert RLE('outside_emissivity', 'boundary', '1.0') in str(e2.value)

    assert RLE('outside_emissivity', 'boundary', '1.0') in str(e3.value)


def test_value__u_value__():

    d1 = get_default_dict_external_transparent_part()
    d2 = get_default_dict_external_opaque_part()
    
    ipt1: InputBoundaryExternalTransparentPart = InputBoundary.read(d=d1)
    ipt2: InputBoundaryExternalOpaquePart = InputBoundary.read(d=d2)

    assert ipt1.u_value == 4.65
    assert ipt2.u_value == 4.65


def test_key__u_value__not_exists():

    d1 = get_default_dict_external_transparent_part()
    d2 = get_default_dict_external_opaque_part()

    del d1['u_value']
    del d2['u_value']

    with pytest.raises(KeyError) as e1:
        InputBoundary.read(d=d1)

    with pytest.raises(KeyError) as e2:
        InputBoundary.read(d=d2)

    assert KNE('u_value', 'boundary') in str(e1.value)

    assert KNE('u_value', 'boundary') in str(e2.value)


def test_value__u_value__wrong_value():

    d1 = get_default_dict_external_transparent_part()
    d2 = get_default_dict_external_opaque_part()

    d1['u_value'] = 'wrong_value'
    d2['u_value'] = 'wrong_value'

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)

    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d=d2)

    assert VI('u_value', 'boundary') in str(e1.value)

    assert VI('u_value', 'boundary') in str(e2.value)


def test_value__u_value__out_of_range():

    d1 = get_default_dict_external_transparent_part()
    d2 = get_default_dict_external_opaque_part()

    d1['u_value'] = 0.0
    d2['u_value'] = 0.0

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)

    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d=d2)

    assert RGT('u_value', 'boundary', '0.0') in str(e1.value)

    assert RGT('u_value', 'boundary', '0.0') in str(e2.value)


def test_value__eta_value__():

    d1 = get_default_dict_external_transparent_part()

    ipt1: InputBoundaryExternalTransparentPart = InputBoundary.read(d=d1)

    assert ipt1.eta_value == 0.792


def test_key__eta_value__not_exists():

    d1 = get_default_dict_external_transparent_part()

    del d1['eta_value']

    with pytest.raises(KeyError) as e1:
        InputBoundary.read(d=d1)

    assert KNE('eta_value', 'boundary') in str(e1.value)


def test_value__eta_value__wrong_value():

    d1 = get_default_dict_external_transparent_part()

    d1['eta_value'] = 'wrong_value'

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)

    assert VI('eta_value', 'boundary') in str(e1.value)


def test_value__eta_value__out_of_range1():

    d1 = get_default_dict_external_transparent_part()

    d1['eta_value'] = 0.0

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)

    assert RGT('eta_value', 'boundary', '0.0') in str(e1.value)


def test_value__eta_value__out_of_range2():

    d1 = get_default_dict_external_transparent_part()

    d1['eta_value'] = 1.0

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)

    assert RLT('eta_value', 'boundary', '1.0') in str(e1.value)


def test_value__glass_area_ratio__():

    d1 = get_default_dict_external_transparent_part()

    ipt1: InputBoundaryExternalTransparentPart = InputBoundary.read(d=d1)

    assert ipt1.glass_area_ratio == 0.8


def test_key__glass_area_ratio__not_exists():

    d1 = get_default_dict_external_transparent_part()

    del d1['glass_area_ratio']

    with pytest.raises(KeyError) as e1:
        InputBoundary.read(d=d1)

    assert KNE('glass_area_ratio', 'boundary') in str(e1.value)


def test_value__glass_area_ratio__wrong_value():

    d1 = get_default_dict_external_transparent_part()

    d1['glass_area_ratio'] = 'wrong_value'

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)

    assert VI('glass_area_ratio', 'boundary') in str(e1.value)


def test_value__glass_area_ratio__out_of_range1():

    d1 = get_default_dict_external_transparent_part()

    d1['glass_area_ratio'] = 0.0

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)

    assert RGT('glass_area_ratio', 'boundary', '0.0') in str(e1.value)


def test_value__glass_area_ratio__out_of_range2():

    d1 = get_default_dict_external_transparent_part()

    d1['glass_area_ratio'] = 1.1

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)

    assert RLE('glass_area_ratio', 'boundary', '1.0') in str(e1.value)


def test_value__incident_angle_characteristics__():

    d1 = get_default_dict_external_transparent_part()

    ipt1: InputBoundaryExternalTransparentPart = InputBoundary.read(d=d1)

    assert ipt1.incident_angle_characteristics == EGlassType.MULTIPLE


def test_key__incident_angle_characteristics__not_exists():

    d1 = get_default_dict_external_transparent_part()

    del d1['incident_angle_characteristics']

    with pytest.raises(KeyError) as e1:
        InputBoundary.read(d=d1)

    assert KNE('incident_angle_characteristics', 'boundary') in str(e1.value)


def test_value__incident_angle_characteristics__wrong_value():

    d1 = get_default_dict_external_transparent_part()

    d1['incident_angle_characteristics'] = 'wrong_value'

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)

    assert VI('incident_angle_characteristics', 'boundary') in str(e1.value)


def test_value__inside_heat_transfer_resistance__():

    d1 = get_default_dict_external_transparent_part()
    d2 = get_default_dict_external_opaque_part()

    ipt1: InputBoundaryExternalTransparentPart = InputBoundary.read(d=d1)
    ipt2: InputBoundaryExternalOpaquePart = InputBoundary.read(d=d2)

    assert ipt1.inside_heat_transfer_resistance == 0.11
    assert ipt2.inside_heat_transfer_resistance == 0.11


def test_value__inside_heat_transfer_resistance__not_exists():

    d1 = get_default_dict_external_transparent_part()
    d2 = get_default_dict_external_opaque_part()

    del d1['inside_heat_transfer_resistance']
    del d2['inside_heat_transfer_resistance']

    with pytest.raises(KeyError) as e1:
        InputBoundary.read(d=d1)
    
    with pytest.raises(KeyError) as e2:
        InputBoundary.read(d=d2)

    assert KNE('inside_heat_transfer_resistance', 'boundary') in str(e1.value)

    assert KNE('inside_heat_transfer_resistance', 'boundary') in str(e2.value)


def test_value__inside_heat_transfer_resistance__wrong_value():

    d1 = get_default_dict_external_transparent_part()
    d2 = get_default_dict_external_opaque_part()

    d1['inside_heat_transfer_resistance'] = 'wrong_value'
    d2['inside_heat_transfer_resistance'] = 'wrong_value'

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)

    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d=d2)

    assert VI('inside_heat_transfer_resistance', 'boundary') in str(e1.value)

    assert VI('inside_heat_transfer_resistance', 'boundary') in str(e2.value)


def test_value__inside_heat_transfer_resistance__out_of_range():

    d1 = get_default_dict_external_transparent_part()
    d2 = get_default_dict_external_opaque_part()

    d1['inside_heat_transfer_resistance'] = 0.0
    d2['inside_heat_transfer_resistance'] = 0.0

    with pytest.raises(ValueError) as e1:
        InputBoundary.read(d=d1)

    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d=d2)

    assert RGT('inside_heat_transfer_resistance', 'boundary', '0.0') in str(e1.value)

    assert RGT('inside_heat_transfer_resistance', 'boundary', '0.0') in str(e2.value)


def test_value__layers__():

    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_ground()
    d3 = get_default_dict_internal()

    ipt1: InputBoundaryExternalGeneralPart = InputBoundary.read(d=d1)
    ipt2: InputBoundaryGround = InputBoundary.read(d=d2)
    ipt3: InputBoundaryInternal = InputBoundary.read(d=d3)

    assert ipt1.ipt_layers[0].name == 'wood_board-12'
    assert ipt1.ipt_layers[0].thermal_resistance == 0.075
    assert ipt1.ipt_layers[0].thermal_capacity == 8.64
    assert ipt1.ipt_layers[1].name == 'hgw24k-100'
    assert ipt1.ipt_layers[1].thermal_resistance == 2.777777777777778
    assert ipt1.ipt_layers[1].thermal_capacity == 2.0

    assert ipt2.ipt_layers[0].name == 'hgw24k-100'
    assert ipt2.ipt_layers[0].thermal_resistance == 2.777777777777778
    assert ipt2.ipt_layers[0].thermal_capacity == 2.0

    assert ipt3.ipt_layers[0].name == 'wood_board-12'
    assert ipt3.ipt_layers[0].thermal_resistance == 0.075
    assert ipt3.ipt_layers[0].thermal_capacity == 8.64


def test_key__layers__not_exists():

    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_ground()
    d3 = get_default_dict_internal()

    del d1['layers']
    del d2['layers']
    del d3['layers']

    with pytest.raises(KeyError) as e1:
        InputBoundary.read(d=d1)

    with pytest.raises(KeyError) as e2:
        InputBoundary.read(d=d2)

    with pytest.raises(KeyError) as e3:
        InputBoundary.read(d=d3)

    assert KNE('layers', 'boundary') in str(e1.value)
    assert KNE('layers', 'boundary') in str(e2.value)
    assert KNE('layers', 'boundary') in str(e3.value)


def test_key__layers__wrong_value():

    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_ground()
    d3 = get_default_dict_internal()

    d1['layers'] = 'wrong_value'
    d2['layers'] = 'wrong_value'
    d3['layers'] = 'wrong_value'

    with pytest.raises(TypeError) as e1:
        InputBoundary.read(d=d1)

    with pytest.raises(TypeError) as e2:
        InputBoundary.read(d=d2)

    with pytest.raises(TypeError) as e3:
        InputBoundary.read(d=d3)

    assert VI('layers', 'boundary') in str(e1.value)
    assert VI('layers', 'boundary') in str(e2.value)
    assert VI('layers', 'boundary') in str(e3.value)
