import pytest

from heat_load_calc.error_message import (
    key_not_exists as KNE,
    value_invalid as VI,
    value_out_of_range_GE as RGE,
    value_out_of_range_LE as RLE,
    value_out_of_range_GT as RGT,
    value_out_of_range_LT as RLT
)
from heat_load_calc.input_models.input_boundary import InputBoundary


def get_default_dict():

    return {
        'id': 0,
        'name': 'test',
        'sub_name': 'sub_test',
        'connected_room_id': 0,
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


