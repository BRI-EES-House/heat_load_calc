import unittest
import pytest

from heat_load_calc.input_rooms import InputRoom, InputScheduleData, InputScheduleDataConst, InputScheduleDataNumber
from heat_load_calc.tenum import EInterval, ERegion, EWeatherMethod, ENumberOfOccupants, EScheduleType


def get_default_dict():

    return {
        'id': 1,
        'name': None,
        'floor_area': 30.0,
        'schedule': None
    }

def test_room_id1():

    d_room = get_default_dict()
    del d_room['id']

    with pytest.raises(KeyError) as e:
        InputRoom.read(d_room=d_room)

    assert 'Key \'id\' could not be found in \'room\' tag.' in str(e)


def test_room_id2():

    def f(v):
        d_room = get_default_dict()
        d_room['id'] = v
        return d_room
    
    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=f('s'))

    assert 'An invalid value was specified for \'id\'. \'id\' must be an integer.' in str(e)

    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=f('-1'))

    assert '\'id\' should be greater than or equal to 0.' in str(e)


def test_room_name1():

    d_room = get_default_dict()
    del d_room['name']   

    with pytest.raises(KeyError) as e:
        InputRoom.read(d_room=d_room)

    assert 'Key \'name\' could not be found in \'room\' tag. (ID=1)' in str(e)


def test_room_floor_area1():

    d_room = get_default_dict()

    del d_room['floor_area']

    with pytest.raises(KeyError) as e:
        InputRoom.read(d_room=d_room)

    assert 'Key \'floor_area\' could not be found in \'room\' tag. (ID=1)' in str(e)


def test_room_floor_area2():

    def f(v):
        d_room = get_default_dict()
        d_room['floor_area'] = v
        return d_room

    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=f('f'))
    
    assert 'An invalid value was specified for \'floor_area\'. \'floor_area\' must be an float. (ID=1)' in str(e)
    
    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=f(0.0))
    
    assert '\'floor_area\' should be greater than 0.0. (ID=1)' in str(e)


def test_room_schedule1():

    d_room = get_default_dict()

    del d_room['schedule']

    with pytest.raises(KeyError) as e:
        InputRoom.read(d_room=d_room)
    
    assert 'Key \'schedule\' could not be found in \'room\' tag. (ID=1)' in str(e)


def test_room_schedule2():

    d_room = get_default_dict()

    d_room['schedule'] = {
        'schedule_type': 1
    }

    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=d_room)
    
    assert 'An invalid value was specified for \'schedule_type\' in \'schedule\' tag. (ID=1)' in str(e)


def test_room_schedule3():

    d_room = get_default_dict()

    d_room['schedule'] = {
        'schedule_type': 'const'
    }

    with pytest.raises(KeyError) as e:
        InputRoom.read(d_room=d_room)
    
    assert 'Key \'schedule\' could not be found in \'schedule\' tag. (ID=1)' in str(e)


def test_room_schedule4():

    d_room = get_default_dict()

    d_room['schedule'] = {
    }

    with pytest.raises(KeyError) as e:
        InputRoom.read(d_room=d_room)
    
    assert 'Key \'name\' could not be found in \'schedule\' tag. (ID=1)' in str(e)


def test_schedule_data_const1():

    d_schedule_data = {
        'const': {
            'Weekday': {},
            'Holiday_Out': {},
            'Holiday_In': {}
        }
    }

    result = InputScheduleData.read(id=1, d_schedule_data=d_schedule_data, schedule_type=EScheduleType.CONST)

    assert isinstance(result, InputScheduleDataConst)
    assert result.schedule_type == EScheduleType.CONST


def test_schedule_data_const2():

    d_schedule_data = {}

    with pytest.raises(KeyError) as e:
        InputScheduleData.read(id=1, d_schedule_data=d_schedule_data, schedule_type=EScheduleType.CONST)

    assert 'Key' in str(e) and 'could not be found in \'schedule\' tag. (ID=1)' in str(e)


def test_schedule_data_number1():

    d_schedule_data = {
        '1': {
            'Weekday': {},
            'Holiday_Out': {},
            'Holiday_In': {}
        },
        '2': {
            'Weekday': {},
            'Holiday_Out': {},
            'Holiday_In': {}
        },
        '3': {
            'Weekday': {},
            'Holiday_Out': {},
            'Holiday_In': {}
        },
        '4': {
            'Weekday': {},
            'Holiday_Out': {},
            'Holiday_In': {}
        }
    }

    result = InputScheduleData.read(id=1, d_schedule_data=d_schedule_data, schedule_type=EScheduleType.NUMBER)

    assert isinstance(result, InputScheduleDataNumber)
    assert result.schedule_type == EScheduleType.NUMBER


def test_schedule_data_number2():

    d_schedule_data = {
        '1': {},
        '2': {},
        '3': {}
    }

    with pytest.raises(KeyError) as e:
        InputScheduleData.read(id=1, d_schedule_data=d_schedule_data, schedule_type=EScheduleType.NUMBER)

    assert 'Key' in str(e) and 'could not be found in \'schedule\' tag. (ID=1)' in str(e)


def test_schedule_data_invalid_type():

    d_schedule_data = {}

    with pytest.raises(ValueError) as e:
        InputScheduleData.read(id=1, d_schedule_data=d_schedule_data, schedule_type='invalid')

    assert 'An invalid schedule_type was specified in \'schedule\' tag. (ID=1)' in str(e)


def test_schedule_data_const3():

    d_schedule_data = {
        'const': {
            'Weekday': {},
            'Holiday_Out': {},
            # 'Holiday_In': {}  # Missing key
        }
    }

    with pytest.raises(KeyError) as e:
        InputScheduleData.read(id=1, d_schedule_data=d_schedule_data, schedule_type=EScheduleType.CONST)

    assert 'Key' in str(e) and 'could not be found in \'const\' tag. (ID=1)' in str(e)





