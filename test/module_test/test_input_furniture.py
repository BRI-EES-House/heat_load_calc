import pytest


from heat_load_calc.input_models.input_furniture import InputFurniture, InputFurnitureDefault, InputFurnitureSpecify
from heat_load_calc.error_message import (
    key_not_exists as KNE,
    value_invalid as VI,
    value_out_of_range_GE as RGE,
    value_out_of_range_LE as RLE,
    value_out_of_range_GT as RGT,
    value_out_of_range_LT as RLT
)


def get_default_dict_default():

    return {
        'input_method': 'default',
        'solar_absorption_ratio': 0.2
    }


def get_default_dict_specify():

    return {
        'input_method': 'specify',
        'heat_capacity': 1.0,
        'heat_cond': 2.0,
        'moisture_capacity': 3.0,
        'moisture_cond': 4.0,
        'solar_absorption_ratio': 0.2
    }


def test_input_method_not_exists():

    d = get_default_dict_default()

    del d['input_method']

    with pytest.raises(KeyError) as e:
        InputFurniture.read(d_furniture=d)
    
    assert KNE('input_method', 'furniture') in str(e)


def test_input_method_wrong_value():

    d = get_default_dict_default()
    d['input_method'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputFurniture.read(d_furniture=d)
    
    assert VI('input_method', 'furniture') in str(e)


def test_input_method_default():

    d = get_default_dict_default()

    ipt = InputFurniture.read(d_furniture=d)

    assert isinstance(ipt, InputFurnitureDefault)
    assert ipt.solar_absorption_ratio == 0.2


def test_input_method_default_solar_absorption_ratio_default():

    d = get_default_dict_default()

    del d['solar_absorption_ratio']

    ipt = InputFurniture.read(d_furniture=d)

    assert ipt.solar_absorption_ratio == 0.5


def test_input_method_default_solar_absorption_ratio_out_of_range():

    d1 = get_default_dict_default()
    d2 = get_default_dict_default()

    d1['solar_absorption_ratio'] = -0.1
    d2['solar_absorption_ratio'] = 1.1

    with pytest.raises(ValueError) as e1:
        InputFurniture.read(d_furniture=d1)

    assert RGE('solar_absorption_ratio', 'furniture', 0.0) in str(e1)

    with pytest.raises(ValueError) as e2:
        InputFurniture.read(d_furniture=d2)

    assert RLE('solar_absorption_ratio', 'furniture', 1.0) in str(e2)


def test_input_method_specify():

    d = get_default_dict_specify()

    ipt = InputFurniture.read(d_furniture=d)

    assert isinstance(ipt, InputFurnitureSpecify)

    assert ipt.heat_capacity == 1.0
    assert ipt.heat_cond == 2.0
    assert ipt.moisture_capacity == 3.0
    assert ipt.moisture_cond == 4.0
    assert ipt.solar_absorption_ratio == 0.2


def test_input_method_specify_solar_absorption_ratio_default():

    d = get_default_dict_specify()

    del d['solar_absorption_ratio']

    ipt = InputFurniture.read(d_furniture=d)

    assert ipt.solar_absorption_ratio == 0.5


def test_input_method_default_solar_absorption_ratio_out_of_range():

    d1 = get_default_dict_specify()
    d2 = get_default_dict_specify()
    d3 = get_default_dict_specify()
    d4 = get_default_dict_specify()
    d5 = get_default_dict_specify()
    d6 = get_default_dict_specify()

    d1['heat_capacity'] = 0.0
    d2['heat_cond'] = 0.0
    d3['moisture_capacity'] = 0.0
    d4['moisture_cond'] = 0.0
    d5['solar_absorption_ratio'] = -0.1
    d6['solar_absorption_ratio'] = 1.1

    with pytest.raises(ValueError) as e1:
        InputFurniture.read(d_furniture=d1)

    assert RGT('heat_capacity', 'furniture', 0.0) in str(e1)

    with pytest.raises(ValueError) as e2:
        InputFurniture.read(d_furniture=d2)

    assert RGT('heat_cond', 'furniture', 0.0) in str(e2)

    with pytest.raises(ValueError) as e3:
        InputFurniture.read(d_furniture=d3)

    assert RGT('moisture_capacity', 'furniture', 0.0) in str(e3)

    with pytest.raises(ValueError) as e4:
        InputFurniture.read(d_furniture=d4)

    assert RGT('moisture_cond', 'furniture', 0.0) in str(e4)

    with pytest.raises(ValueError) as e5:
        InputFurniture.read(d_furniture=d5)

    assert RGE('solar_absorption_ratio', 'furniture', 0.0) in str(e5)

    with pytest.raises(ValueError) as e6:
        InputFurniture.read(d_furniture=d6)

    assert RLE('solar_absorption_ratio', 'furniture', 1.0) in str(e6)


