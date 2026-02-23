import unittest
import pytest

from heat_load_calc.error_message import (
    key_not_exists as KNE,
    value_invalid as VI,
    value_out_of_range_GE as RGE,
    value_out_of_range_LE as RLE,
    value_out_of_range_GT as RGT,
    value_out_of_range_LT as RLT
)
from heat_load_calc.input_models.input_room import InputRoom
from heat_load_calc.tenum import EInterval, ERegion, EWeatherMethod, ENumberOfOccupants, EScheduleType
from heat_load_calc.input_models.input_schedule_data import InputScheduleData, InputScheduleDataConst, InputScheduleDataNumber
from heat_load_calc.input_models.input_furniture import InputFurniture, InputFurnitureDefault, InputFurnitureSpecify

def get_default_dict():

    return {
        'id': 1,
        'name': 'test',
        'sub_name': 'sub_test',
        'floor_area': 30.0,
        'volume': 70.0,
        'furniture': {
            'input_method': 'default',
        },
        'ventilation': {
            'natural': 50.0,
        },
        'MET': 1.2,
        'schedule': {
            'schedule_type': 'const',
            'schedule': {
                'const': {
                    'Weekday': {},
                    'Holiday_Out': {},
                    'Holiday_In': {}
                }
            }
        }
    }


def test_key__id__not_exists():

    d = get_default_dict()
    
    del d['id']

    with pytest.raises(KeyError) as e:
        InputRoom.read(d_room=d)

    assert KNE('id', 'room') in str(e)


def test_value__id__invalid():

    d = get_default_dict()
    d['id'] = 's'

    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=d)

    assert VI('id', 'room') in str(e)


def test_room_id_out_of_range():

    d = get_default_dict()
    d['id'] = '-1'

    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=d)

    assert RGE('id', 'room', '0.0') in str(e)


def test_key__name__not_exists():

    d = get_default_dict()
    
    del d['name']   

    with pytest.raises(KeyError) as e:
        InputRoom.read(d_room=d)

    assert KNE('name', 'room') in str(e)


def test_value__name__():

    d = get_default_dict()

    ipt = InputRoom.read(d_room=d)

    assert ipt.name == 'test'


def test_value__sub_name__():

    d = get_default_dict()

    ipt = InputRoom.read(d_room=d)

    assert ipt.sub_name == 'sub_test'


def test_value__sub_name__default():

    d = get_default_dict()

    del d['sub_name']

    ipt = InputRoom.read(d_room=d)

    assert ipt.sub_name == ''


def test_key__floor_area__not_exists():

    d = get_default_dict()

    del d['floor_area']

    with pytest.raises(KeyError) as e:
        InputRoom.read(d_room=d)

    assert KNE('floor_area', 'room') in str(e)


def test_value__floor_area__invlid_value():

    d = get_default_dict()

    d['floor_area'] = 'f'

    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=d)
    
    assert VI('floor_area', 'room') in str(e)
    

def test_value__floor_area__out_of_range():

    d = get_default_dict()
    d['floor_area'] = 0.0

    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=d)
    
    assert RGT('floor_area', 'room', '0.0') in str(e)


def test_key__volume__not_exists():

    d = get_default_dict()

    del d['volume']

    with pytest.raises(KeyError) as e:
        InputRoom.read(d_room=d)

    assert KNE('floor_area', 'room') in str(e)


def test_value__volume__invlid_value():

    d = get_default_dict()

    d['volume'] = 'f'

    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=d)
    
    assert VI('floor_area', 'room') in str(e)
    

def test_value__volume__out_of_range():

    d = get_default_dict()
    d['volume'] = 0.0

    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=d)
    
    assert RGT('floor_area', 'room', '0.0') in str(e)


def test_key__furniture__not_exists():

    d = get_default_dict()
    del d['furniture']

    with pytest.raises(KeyError) as e:
        InputRoom.read(d_room=d)

    assert KNE('furniture', 'room') in str(e)


def test_key__furniture__exists():

    d1 = get_default_dict()
    d2 = get_default_dict()

    d2['furniture'] = {
        'input_method': 'specify',
        'heat_capacity': 0.1,
        'heat_cond': 0.1,
        'moisture_capacity': 0.1,
        'moisture_cond': 0.1,
    }

    ipt1 = InputRoom.read(d_room=d1)
    ipt2 = InputRoom.read(d_room=d2)
    
    assert isinstance(ipt1.ipt_furniture, InputFurniture)
    assert isinstance(ipt1.ipt_furniture, InputFurnitureDefault)
    assert not isinstance(ipt1.ipt_furniture, InputFurnitureSpecify)

    assert isinstance(ipt2.ipt_furniture, InputFurniture)
    assert not isinstance(ipt2.ipt_furniture, InputFurnitureDefault)
    assert isinstance(ipt2.ipt_furniture, InputFurnitureSpecify)


def test_key__ventilationo__not_exists():

    d = get_default_dict()

    del d['ventilation']

    with pytest.raises(KeyError) as e:
        InputRoom.read(d_room=d)
    
    assert KNE('ventilation', 'room') in str(e)


def test_key__natural__not_exists():

    d = get_default_dict()

    del d['ventilation']['natural']

    with pytest.raises(KeyError) as e:
        InputRoom.read(d_room=d)
    
    assert KNE('natural', 'ventilation') in str(e)


def test_value__natural__():

    d = get_default_dict()

    ipt = InputRoom.read(d_room=d)

    assert ipt.v_vent_ntr_set == 50.0
    

def test_value__natural__out_of_range():

    d = get_default_dict()

    d['ventilation']['natural'] = -10.0

    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=d)
    
    assert RGE('natural', 'ventilation', 0.0) in str(e)


def test_value__MET__():

    d = get_default_dict()

    ipt = InputRoom.read(d_room=d)

    assert ipt.met == 1.2


def test_value__MET__invalid():

    d = get_default_dict()

    d['MET'] = 'test'

    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=d)
    
    assert VI('MET', 'room') in str(e)


def test_value__MET__out_of_range():

    d = get_default_dict()

    d['MET'] = 0.0

    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=d)
    
    assert RGT('MET', 'room', 0.0) in str(e)
 


def test_key__schedule__not_exists():

    d = get_default_dict()

    del d['schedule']

    with pytest.raises(KeyError) as e:
        InputRoom.read(d_room=d)
    
    assert KNE('schedule', 'room') in str(e)


def test_key__schedule__exists():

    d = get_default_dict()

    ipt = InputRoom.read(d_room=d)

    assert isinstance(ipt.ipt_schedule_data, InputScheduleData)

    

