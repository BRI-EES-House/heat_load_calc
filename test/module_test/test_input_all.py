import pytest

from heat_load_calc.input_all import InputAll


def _get_default_dict():

    return {
        'common': {},
        'building': {},
        'rooms': [],
    }


def test_key_common_not_exists():

    d = _get_default_dict()

    del d['common']

    with pytest.raises(KeyError) as e:
        InputAll(d=d)

    assert 'Key \'common\' is not defined.' in str(e.value)


def test_key_building_not_exists():

    d = _get_default_dict()

    del d['building']

    with pytest.raises(KeyError) as e:
        InputAll(d=d)
    
    assert 'Key \'building\' is not defined.' in str(e.value)


def test_key_rooms_not_exists():

    d = _get_default_dict()

    del d['rooms']

    with pytest.raises(KeyError) as e:
        InputAll(d=d)

    assert 'Key \'rooms\' is not defined.' in str(e.value)


def test_value_rooms_not_list():

    d = _get_default_dict()

    d['rooms'] = {}

    with pytest.raises(TypeError) as e:
        InputAll(d=d)

    assert 'Value \'rooms\' should be list.' in str(e.value)
 
