import unittest
import pytest

from heat_load_calc.input_models.input_room import InputRoom
from heat_load_calc.tenum import EInterval, ERegion, EWeatherMethod, ENumberOfOccupants, EScheduleType
from heat_load_calc.input_models.input_schedule_data import InputScheduleData, InputScheduleDataConst, InputScheduleDataNumber


def get_default_dict():

    return {
        'id': 1,
        'name': 'test',
        'sub_name': 'sub_test',
        'floor_area': 30.0,
        'volume': 70.0,
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

    assert 'Key \'id\' could not be found in \'room\' tag.' in str(e)


def test_value__id__invalid():

    d = get_default_dict()
    d['id'] = 's'

    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=d)

    assert 'An invalid value was specified for \'id\'. \'id\' must be an integer.' in str(e)


def test_room_id2():

    d = get_default_dict()
    d['id'] = '-1'

    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=d)

    assert '\'id\' should be greater than or equal to 0.' in str(e)


def test_key__name__not_exists():

    d = get_default_dict()
    
    del d['name']   

    with pytest.raises(KeyError) as e:
        InputRoom.read(d_room=d)

    assert 'Key \'name\' could not be found in \'room\' tag. (ID=1)' in str(e)


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

    assert 'Key \'floor_area\' could not be found in \'room\' tag. (ID=1)' in str(e)


def test_value__floor_area__invlid_value():

    d = get_default_dict()

    d['floor_area'] = 'f'

    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=d)
    
    assert 'An invalid value was specified for \'floor_area\'. \'floor_area\' must be an float. (ID=1)' in str(e)
    

def test_value__floor_area__out_of_range():

    d = get_default_dict()
    d['floor_area'] = 0.0

    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=d)
    
    assert '\'floor_area\' should be greater than 0.0. (ID=1)' in str(e)


def test_key__volume__not_exists():

    d = get_default_dict()

    del d['volume']

    with pytest.raises(KeyError) as e:
        InputRoom.read(d_room=d)

    assert 'Key \'volume\' could not be found in \'room\' key. (ID=1)' in str(e)


def test_value__volume__invlid_value():

    d = get_default_dict()

    d['volume'] = 'f'

    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=d)
    
    assert 'An invalid value was specified for \'volume\' in \'room\' key.' in str(e)
    

def test_value__volume__out_of_range():

    d = get_default_dict()
    d['volume'] = 0.0

    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=d)
    
    assert '\'volume\' should be greater than 0.0. (ID=1)' in str(e)


def test_key__schedule__not_exists():

    d = get_default_dict()

    del d['schedule']

    with pytest.raises(KeyError) as e:
        InputRoom.read(d_room=d)
    
    assert 'Key \'schedule\' could not be found in \'room\' tag. (ID=1)' in str(e)


def test_key__schedule__exists():

    d = get_default_dict()

    ipt = InputRoom.read(d_room=d)

    assert isinstance(ipt.ipt_schedule_data, InputScheduleData)

    

