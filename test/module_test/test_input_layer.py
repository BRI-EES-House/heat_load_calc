import pytest

from heat_load_calc.error_message import (
    key_not_exists as KNE,
    value_invalid as VI,
    value_out_of_range_GE as RGE,
    value_out_of_range_LE as RLE,
    value_out_of_range_GT as RGT,
    value_out_of_range_LT as RLT
)
from heat_load_calc.input_models.input_layer import InputLayer


def get_default_dict():

    return {
        "name": "wood_board-12",
        "thermal_resistance": 0.075,
        "thermal_capacity": 8.64
    }


def test_value__name__():

    d = get_default_dict()

    ipt = InputLayer.read(d=d)

    assert ipt.name == 'wood_board-12'


def test_key__name__not_exists():

    d = get_default_dict()

    del d['name']

    with pytest.raises(KeyError) as e:
        InputLayer.read(d=d)
    
    assert KNE('name', 'layer') in str(e.value)


def test_value__thermal_capacity__():

    d = get_default_dict()

    ipt = InputLayer.read(d=d)

    assert ipt.thermal_capacity == 8.64


def test_key__thermal_capacity__not_exists():

    d = get_default_dict()

    del d['thermal_capacity']

    with pytest.raises(KeyError) as e:
        InputLayer.read(d=d)
    
    assert KNE('thermal_capacity', 'layer') in str(e.value)

def test_value__thermal_capacity__invalid():

    d = get_default_dict()

    d['thermal_capacity'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputLayer.read(d=d)
    
    assert VI('thermal_capacity', 'layer') in str(e.value)


def test_value__thermal_capacity__out_of_range():

    d = get_default_dict()

    d['thermal_capacity'] = -0.1

    with pytest.raises(ValueError) as e:
        InputLayer.read(d=d)
    
    assert RGE('thermal_capacity', 'layer', '0.0') in str(e.value)


def test_value__thermal_resistance__():

    d = get_default_dict()

    ipt = InputLayer.read(d=d)

    assert ipt.thermal_resistance == 0.075


def test_key__thermal_resistance__not_exists():

    d = get_default_dict()

    del d['thermal_resistance']

    with pytest.raises(KeyError) as e:
        InputLayer.read(d=d)
    
    assert KNE('thermal_resistance', 'layer') in str(e.value)

def test_value__thermal_resistance__invalid():

    d = get_default_dict()

    d['thermal_resistance'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputLayer.read(d=d)
    
    assert VI('thermal_resistance', 'layer') in str(e.value)


def test_value__thermal_resistance__out_of_range():

    d = get_default_dict()

    d['thermal_resistance'] = 0.0

    with pytest.raises(ValueError) as e:
        InputLayer.read(d=d)
    
    assert RGT('thermal_resistance', 'layer', '0.0') in str(e.value)
