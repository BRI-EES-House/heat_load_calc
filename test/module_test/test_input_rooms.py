import unittest
import pytest

from heat_load_calc.input_rooms import InputRoom
from heat_load_calc.tenum import EInterval, ERegion, EWeatherMethod, ENumberOfOccupants


def test_room_id1():

    d_room = {
        'schedule': None
    }

    with pytest.raises(KeyError) as e:
        InputRoom.read(d_room=d_room)

    assert 'Key id could not be found in room tag.'

def test_room_floor_area1():

    d_room = {
        'id': 1,
        'schedule': None
    }


    with pytest.raises(KeyError) as e:
        InputRoom.read(d_room=d_room)

    assert 'Key floor_area could not be found in room tag.' in str(e)


def test_room_floor_area2():

    def f(v):

        return {
            'id': 1,
            'schedule': None,
            'floor_area': v
        }

    with pytest.raises(ValueError) as e:
        InputRoom.read(d_room=f('f'))
    
    assert 'could not convert string to float: \'f\'' in str(e)
    


