import pytest

from heat_load_calc.error_message import (
    key_not_exists as KNE,
    value_invalid as VI,
    value_out_of_range_GE as RGE,
    value_out_of_range_LE as RLE,
    value_out_of_range_GT as RGT,
    value_out_of_range_LT as RLT
)

from heat_load_calc.input_models.input_solar_shading_part import (
    InputSolarShadingPart,
    InputSolarShadingPartSimple,
    InputSolarShadingPartDetail,
    InputSolarShadingPartNot
)
from heat_load_calc.direction import Direction


def get_default_dict_simple():

    return {
        'existence': True,
        'input_method': 'simple',
        'depth': 0.5,
        'd_h': 0.5,
        'd_e': 0.5
    }


def get_default_dict_detail():

    return {
        'existence': True,
        'input_method': 'detail',
        'x1': 0.5,
        'x2': 0.5,
        'x3': 0.5,
        'y1': 0.5,
        'y2': 0.5,
        'y3': 0.5,
        'z_x_pls': 0.5,
        'z_x_mns': 0.5,
        'z_y_pls': 0.5,
        'z_y_mns': 0.5
    }


def get_default_dict_not():

    return {
        'existence': False
    }


def test_key__existence__not_exists():

    d = get_default_dict_simple()
    del d['existence']

    with pytest.raises(KeyError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert KNE('existence', 'solar_shading_part') in str(e.value)


def test_direction__top():

    d = get_default_dict_simple()

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.TOP)

    assert 'existence\' of solar shading shall be false when the direction of surface is top or bottom.' in str(e.value)


def test_direction__bottom():

    d = get_default_dict_simple()

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.BOTTOM)

    assert 'existence\' of solar shading shall be false when the direction of surface is top or bottom.' in str(e.value)


def test_key__input_method__not_exists():

    d = get_default_dict_simple()
    del d['input_method']

    with pytest.raises(KeyError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert KNE('input_method', 'solar_shading_part') in str(e.value)


def test_value__input_method__invalid():

    d = get_default_dict_simple()
    d['input_method'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert VI('input_method', 'solar_shading_part') in str(e.value)


def test_value__input_solar_shading_part_simple__():

    d = get_default_dict_simple()

    ipt = InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert isinstance(ipt, InputSolarShadingPartSimple)

    assert ipt.existence == True
    assert ipt.depth == 0.5
    assert ipt.d_h == 0.5
    assert ipt.d_e == 0.5


def test_value__depth__not_exists():

    d = get_default_dict_simple()
    del d['depth']

    with pytest.raises(KeyError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert KNE('depth', 'solar_shading_part') in str(e.value)


def test_value__depth__invalid():

    d = get_default_dict_simple()
    d['depth'] = 'invalid_value'

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert VI('depth', 'solar_shading_part') in str(e.value)


def test_value__depth__out_of_range():

    d = get_default_dict_simple()
    d['depth'] = -0.01

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert RGE('depth', 'solar_shading_part', 0.0) in str(e.value)


def test_value__d_h__not_exists():

    d = get_default_dict_simple()
    del d['d_h']

    with pytest.raises(KeyError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert KNE('d_h', 'solar_shading_part') in str(e.value)


def test_value__d_h__invalid():

    d = get_default_dict_simple()
    d['d_h'] = 'invalid_value'

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert VI('d_h', 'solar_shading_part') in str(e.value)


def test_value__d_h__out_of_range():

    d = get_default_dict_simple()
    d['d_h'] = -0.01

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert RGE('d_h', 'solar_shading_part', 0.0) in str(e.value)


def test_value__d_e__not_exists():

    d = get_default_dict_simple()
    del d['d_e']

    with pytest.raises(KeyError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert KNE('d_e', 'solar_shading_part') in str(e.value)


def test_value__d_e__invalid():

    d = get_default_dict_simple()
    d['d_e'] = 'invalid_value'

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert VI('d_e', 'solar_shading_part') in str(e.value)


def test_value__d_e__out_of_range():

    d = get_default_dict_simple()
    d['d_e'] = -0.01

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert RGE('d_e', 'solar_shading_part', 0.0) in str(e.value)


def test_value__input_solar_shading_part_detail__():

    d = get_default_dict_detail()

    ipt = InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert isinstance(ipt, InputSolarShadingPartDetail)

    assert ipt.existence == True
    assert ipt.x1 == 0.5
    assert ipt.x2 == 0.5
    assert ipt.x3 == 0.5
    assert ipt.y1 == 0.5
    assert ipt.y2 == 0.5
    assert ipt.y3 == 0.5
    assert ipt.z_x_pls == 0.5
    assert ipt.z_x_mns == 0.5
    assert ipt.z_y_pls == 0.5
    assert ipt.z_y_mns == 0.5


def test_value__x1__not_exists():

    d = get_default_dict_detail()
    del d['x1']

    with pytest.raises(KeyError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert KNE('x1', 'solar_shading_part') in str(e.value)


def test_value__x1__invalid():

    d = get_default_dict_detail()
    d['x1'] = 'invalid_value'

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert VI('x1', 'solar_shading_part') in str(e.value)


def test_value__x1__out_of_range():

    d = get_default_dict_detail()
    d['x1'] = -0.01

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert RGE('x1', 'solar_shading_part', 0.0) in str(e.value)


def test_value__x2__not_exists():

    d = get_default_dict_detail()
    del d['x2']

    with pytest.raises(KeyError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert KNE('x2', 'solar_shading_part') in str(e.value)


def test_value__x2__invalid():

    d = get_default_dict_detail()
    d['x2'] = 'invalid_value'

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert VI('x2', 'solar_shading_part') in str(e.value)


def test_value__x2__out_of_range():

    d = get_default_dict_detail()
    d['x2'] = -0.01

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert RGE('x2', 'solar_shading_part', 0.0) in str(e.value)


def test_value__x3__not_exists():

    d = get_default_dict_detail()
    del d['x3']

    with pytest.raises(KeyError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert KNE('x3', 'solar_shading_part') in str(e.value)


def test_value__x3__invalid():

    d = get_default_dict_detail()
    d['x3'] = 'invalid_value'

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert VI('x3', 'solar_shading_part') in str(e.value)


def test_value__x3__out_of_range():

    d = get_default_dict_detail()
    d['x3'] = -0.01

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert RGE('x3', 'solar_shading_part', 0.0) in str(e.value)


def test_value__y1__not_exists():

    d = get_default_dict_detail()
    del d['y1']

    with pytest.raises(KeyError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert KNE('y1', 'solar_shading_part') in str(e.value)


def test_value__y1__invalid():

    d = get_default_dict_detail()
    d['y1'] = 'invalid_value'

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert VI('y1', 'solar_shading_part') in str(e.value)


def test_value__y1__out_of_range():

    d = get_default_dict_detail()
    d['y1'] = -0.01

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert RGE('y1', 'solar_shading_part', 0.0) in str(e.value)


def test_value__y2__not_exists():

    d = get_default_dict_detail()
    del d['y2']

    with pytest.raises(KeyError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert KNE('y2', 'solar_shading_part') in str(e.value)


def test_value__y2__invalid():

    d = get_default_dict_detail()
    d['y2'] = 'invalid_value'

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert VI('y2', 'solar_shading_part') in str(e.value)


def test_value__y2__out_of_range():

    d = get_default_dict_detail()
    d['y2'] = -0.01

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert RGE('y2', 'solar_shading_part', 0.0) in str(e.value)


def test_value__y3__not_exists():

    d = get_default_dict_detail()
    del d['y3']

    with pytest.raises(KeyError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert KNE('y3', 'solar_shading_part') in str(e.value)


def test_value__y3__invalid():

    d = get_default_dict_detail()
    d['y3'] = 'invalid_value'

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert VI('y3', 'solar_shading_part') in str(e.value)


def test_value__y3__out_of_range():

    d = get_default_dict_detail()
    d['y3'] = -0.01

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert RGE('y3', 'solar_shading_part', 0.0) in str(e.value)


def test_value__z_x_pls__not_exists():

    d = get_default_dict_detail()
    del d['z_x_pls']

    with pytest.raises(KeyError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert KNE('z_x_pls', 'solar_shading_part') in str(e.value)


def test_value__z_x_pls__invalid():

    d = get_default_dict_detail()
    d['z_x_pls'] = 'invalid_value'

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert VI('z_x_pls', 'solar_shading_part') in str(e.value)


def test_value__z_x_pls__out_of_range():

    d = get_default_dict_detail()
    d['z_x_pls'] = -0.01

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert RGE('z_x_pls', 'solar_shading_part', 0.0) in str(e.value)


def test_value__z_x_mns__not_exists():

    d = get_default_dict_detail()
    del d['z_x_mns']

    with pytest.raises(KeyError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert KNE('z_x_mns', 'solar_shading_part') in str(e.value)


def test_value__z_x_mns__invalid():

    d = get_default_dict_detail()
    d['z_x_mns'] = 'invalid_value'

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert VI('z_x_mns', 'solar_shading_part') in str(e.value)


def test_value__z_x_mns__out_of_range():

    d = get_default_dict_detail()
    d['z_x_mns'] = -0.01

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert RGE('z_x_mns', 'solar_shading_part', 0.0) in str(e.value)


def test_value__z_y_pls__not_exists():

    d = get_default_dict_detail()
    del d['z_y_pls']

    with pytest.raises(KeyError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert KNE('z_y_pls', 'solar_shading_part') in str(e.value)


def test_value__z_y_pls__invalid():

    d = get_default_dict_detail()
    d['z_y_pls'] = 'invalid_value'

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert VI('z_y_pls', 'solar_shading_part') in str(e.value)


def test_value__z_y_pls__out_of_range():

    d = get_default_dict_detail()
    d['z_y_pls'] = -0.01

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert RGE('z_y_pls', 'solar_shading_part', 0.0) in str(e.value)


def test_value__z_y_mns__not_exists():

    d = get_default_dict_detail()
    del d['z_y_mns']

    with pytest.raises(KeyError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert KNE('z_y_mns', 'solar_shading_part') in str(e.value)


def test_value__z_y_mns__invalid():

    d = get_default_dict_detail()
    d['z_y_mns'] = 'invalid_value'

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert VI('z_y_mns', 'solar_shading_part') in str(e.value)


def test_value__z_y_mns__out_of_range():

    d = get_default_dict_detail()
    d['z_y_mns'] = -0.01

    with pytest.raises(ValueError) as e:
        InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert RGE('z_y_mns', 'solar_shading_part', 0.0) in str(e.value)


def test_value__input_solar_shading_part_not__():

    d = get_default_dict_not()

    ipt = InputSolarShadingPart.read(d=d, direction=Direction.N)

    assert isinstance(ipt, InputSolarShadingPartNot)

    assert ipt.existence == False



