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
    InputBoundaryExternalOpaquePart
)
from heat_load_calc.tenum import EBoundaryType


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
        'is_floor': True
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
        'is_floor': False
    }


def test_value__id__():

    d = get_default_dict()

    d['id'] = 99

    ipt = InputBoundary.read(d_boundary=d)

    assert ipt.id == 99


def test_key__id__not_exists():

    d = get_default_dict()

    del d['id']

    with pytest.raises(KeyError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert KNE('id', 'boundary') in str(e.value)


def test_value__id__invalid():

    d = get_default_dict()

    d['id'] = 'test'

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert VI('id', 'boundary') in str(e.value)


def test_value__id__out_of_range():

    d = get_default_dict()

    d['id'] = -1

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert RGE('id', 'boundary', 0) in str(e.value)


def test_value__name__():

    d = get_default_dict()

    ipt = InputBoundary.read(d_boundary=d)

    assert ipt.name == 'test'


def test_value__name__not_exists():

    d = get_default_dict()

    del d['name']

    with pytest.raises(KeyError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert KNE('name', 'boundary') in str(e.value)


def test_value__sub_name__():

    d = get_default_dict()

    ipt = InputBoundary.read(d_boundary=d)

    assert ipt.sub_name == 'sub_test'


def test_value__sub_name__default():

    d = get_default_dict()

    del d['sub_name']

    ipt = InputBoundary.read(d_boundary=d)

    assert ipt.sub_name == ''


def test_connected_room__id__():

    d = get_default_dict()

    d['connected_room_id'] = 99

    ipt = InputBoundary.read(d_boundary=d)

    assert ipt.connected_room_id == 99


def test_key__connected_room_id__not_exists():

    d = get_default_dict()

    del d['connected_room_id']

    with pytest.raises(KeyError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert KNE('connected_room_id', 'boundary') in str(e.value)


def test_value__connected_room_id__invalid():

    d = get_default_dict()

    d['connected_room_id'] = 'test'

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert VI('connected_room_id', 'boundary') in str(e.value)


def test_value__connected_room_id__out_of_range():

    d = get_default_dict()

    d['connected_room_id'] = -1

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert RGE('connected_room_id', 'boundary', 0) in str(e.value)


def test_value__boundary_type__():

    d = get_default_dict()

    ipt = InputBoundary.read(d_boundary=d)

    assert ipt.boundary_type == EBoundaryType.EXTERNAL_GENERAL_PART


def test_key__boundary_type__not_exists():

    d = get_default_dict()

    del d['boundary_type']

    with pytest.raises(KeyError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert KNE('boundary_type', 'boundary') in str(e.value)


def test_value__boundary_type__invalid():

    d = get_default_dict()

    d['boundary_type'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d_boundary=d)

    assert VI('boundary_type', 'boundary') in str(e.value)


def test_value__area__():

    d = get_default_dict()

    ipt = InputBoundary.read(d_boundary=d)

    assert ipt.area == 3.0


def test_key__area__not_exists():

    d = get_default_dict()

    del d['area']

    with pytest.raises(KeyError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert KNE('area', 'boundary') in str(e.value)


def test_value__area__invalid():

    d = get_default_dict()

    d['area'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert VI('area', 'boundary') in str(e.value)


def test_value__area__out_of_range():

    d = get_default_dict()

    d['area'] = 0.0

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d_boundary=d)

    assert RGT('area', 'boundary', 0.0) in str(e.value)


def test_value__inside_emissivity__():

    d = get_default_dict()

    ipt = InputBoundary.read(d_boundary=d)

    assert ipt.inside_emissivity == 0.92


def test_value__inside_emissivity__default():

    d = get_default_dict()

    del d['inside_emissivity']

    ipt = InputBoundary.read(d_boundary=d)

    assert ipt.inside_emissivity == 0.9


def test_value__inside_emissivity__wrong_value():

    d = get_default_dict()

    d['inside_emissivity'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert VI('inside_emissivity', 'boundary') in str(e.value)


def test_value__inside_emissivity__out_of_range_1():

    d = get_default_dict()

    d['inside_emissivity'] = -0.1

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert RGE('inside_emissivity', 'boundary', 0.0) in str(e.value)


def test_value__inside_emissivity__out_of_range_2():

    d = get_default_dict()

    d['inside_emissivity'] = 1.1

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert RLE('inside_emissivity', 'boundary', 0.0) in str(e.value)


def test_value__h_c__():

    d = get_default_dict()

    ipt = InputBoundary.read(d_boundary=d)

    assert ipt.h_c == 2.5


def test_key__h_c__not_exists():

    d = get_default_dict()

    del d['h_c']

    with pytest.raises(KeyError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert KNE('h_c', 'boundary') in str(e.value)


def test_value__h_c__invalid():

    d = get_default_dict()

    d['h_c'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert VI('h_c', 'boundary') in str(e.value)


def test_value__h_c__out_of_range():

    d = get_default_dict()

    d['h_c'] = -0.1

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d_boundary=d)

    assert RGE('h_c', 'boundary', 0.0) in str(e.value)


def test_value__temp_dif_coef__():

    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    ipt1: InputBoundaryExternalGeneralPart = InputBoundary.read(d_boundary=d1)
    ipt2: InputBoundaryExternalTransparentPart = InputBoundary.read(d_boundary=d2)
    ipt3: InputBoundaryExternalOpaquePart = InputBoundary.read(d_boundary=d3)

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
        InputBoundary.read(d_boundary=d1)
    
    with pytest.raises(KeyError) as e2:
        InputBoundary.read(d_boundary=d2)

    with pytest.raises(KeyError) as e3:
        InputBoundary.read(d_boundary=d3)

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
        InputBoundary.read(d_boundary=d1)
    
    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d_boundary=d2)

    with pytest.raises(ValueError) as e3:
        InputBoundary.read(d_boundary=d3)

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
        InputBoundary.read(d_boundary=d1)
    
    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d_boundary=d2)

    with pytest.raises(ValueError) as e3:
        InputBoundary.read(d_boundary=d3)

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
        InputBoundary.read(d_boundary=d1)
    
    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d_boundary=d2)

    with pytest.raises(ValueError) as e3:
        InputBoundary.read(d_boundary=d3)

    assert RLE('temp_dif_coef', 'boundary', 1.0) in str(e1.value)

    assert RLE('temp_dif_coef', 'boundary', 1.0) in str(e2.value)

    assert RLE('temp_dif_coef', 'boundary', 1.0) in str(e3.value)


def test_value__is_solar_absorbed_inside__():

    d = get_default_dict()

    ipt = InputBoundary.read(d_boundary=d)

    assert ipt.is_solar_absorbed_inside == True


def test_key__is_solar_absorbed_inside__not_exists():

    d = get_default_dict()

    del d['is_solar_absorbed_inside']

    with pytest.raises(KeyError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert KNE('is_solar_absorbed_inside', 'boundary') in str(e.value)


def test_value__is_solar_absorbed_inside__invalid():

    d = get_default_dict()

    d['is_solar_absorbed_inside'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert VI('is_solar_absorbed_inside', 'boundary') in str(e.value)


def test_key__is_floor__not_exists():

    d = get_default_dict()

    del d['is_floor']

    with pytest.raises(KeyError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert KNE('is_floor', 'boundary') in str(e.value)


def test_value__is_floor__invalid():

    d = get_default_dict()

    d['is_floor'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert VI('is_floor', 'boundary') in str(e.value)


def test_key__rear_surface_boundary_id__not_exists():
    
    d = get_default_dict_internal()

    del d['rear_surface_boundary_id']

    with pytest.raises(KeyError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert KNE('rear_surface_boundary_id', 'boundary') in str(e.value)


def test_value__rear_surface_boundary_id__wrong_value():
    
    d = get_default_dict_internal()

    d['rear_surface_boundary_id'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert VI('rear_surface_boundary_id', 'boundary') in str(e.value)


def test_value__rear_surface_boundary_id__out_of_range1():
    
    d = get_default_dict_internal()

    d['rear_surface_boundary_id'] = -1

    with pytest.raises(ValueError) as e:
        InputBoundary.read(d_boundary=d)
    
    assert RGE('rear_surface_boundary_id', 'boundary', 0) in str(e.value)


def test_value__is_sun_striked_outside__():

    d1 = get_default_dict_external_general_part()
    d2 = get_default_dict_external_transparent_part()
    d3 = get_default_dict_external_opaque_part()

    ipt1: InputBoundaryExternalGeneralPart = InputBoundary.read(d_boundary=d1)
    ipt2: InputBoundaryExternalTransparentPart = InputBoundary.read(d_boundary=d2)
    ipt3: InputBoundaryExternalOpaquePart = InputBoundary.read(d_boundary=d3)

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
        InputBoundary.read(d_boundary=d1)
    
    with pytest.raises(KeyError) as e2:
        InputBoundary.read(d_boundary=d2)

    with pytest.raises(KeyError) as e3:
        InputBoundary.read(d_boundary=d3)

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
        InputBoundary.read(d_boundary=d1)
    
    with pytest.raises(ValueError) as e2:
        InputBoundary.read(d_boundary=d2)

    with pytest.raises(ValueError) as e3:
        InputBoundary.read(d_boundary=d3)

    assert VI('is_sun_striked_outside', 'boundary') in str(e1.value)

    assert VI('is_sun_striked_outside', 'boundary') in str(e2.value)

    assert VI('is_sun_striked_outside', 'boundary') in str(e3.value)
