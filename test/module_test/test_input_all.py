import pytest

from heat_load_calc.error_message import (
    key_not_exists as KNE,
    value_invalid as VI,
    value_out_of_range_GE as RGE,
    value_out_of_range_LE as RLE,
    value_out_of_range_GT as RGT,
    value_out_of_range_LT as RLT
)
from heat_load_calc.input_all import InputAll


def _get_default_dict():

    return {
        'common': {},
        'building': {},
        'rooms': [],
        'boundaries': []
    }


def test_key_common_not_exists():

    d = _get_default_dict()

    del d['common']

    with pytest.raises(KeyError) as e:
        InputAll(d=d)

    assert KNE('common', 'root') in str(e.value)


def test_key_building_not_exists():

    d = _get_default_dict()

    del d['building']

    with pytest.raises(KeyError) as e:
        InputAll(d=d)
    
    assert KNE('building', 'root') in str(e.value)


def test_key_rooms_not_exists():

    d = _get_default_dict()

    del d['rooms']

    with pytest.raises(KeyError) as e:
        InputAll(d=d)

    assert KNE('rooms', 'root') in str(e.value)


def test_value_rooms_not_list():

    d = _get_default_dict()

    d['rooms'] = {}

    with pytest.raises(TypeError) as e:
        InputAll(d=d)

    assert VI('rooms', 'root') in str(e.value)
 

def test_key_boundaries_not_exists():

    d = _get_default_dict()

    del d['boundaries']

    with pytest.raises(KeyError) as e:
        InputAll(d=d)
    
    assert KNE('boundaries', 'root') in str(e.value)


def test_value_boundaries_not_list():

    d = _get_default_dict()

    d['boundaries'] = {}

    with pytest.raises(TypeError) as e:
        InputAll(d=d)

    assert VI('boundaries', 'root') in str(e.value)


