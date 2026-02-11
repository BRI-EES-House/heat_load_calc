import pytest

from heat_load_calc.input_all import InputAll


def test_common1():

    d = {
        'rooms': None
    }

    with pytest.raises(KeyError) as e:
        InputAll(d=d)

    assert 'Key common could not be found in the input file.' in str(e.value)


def test_common2():

    d = {
        'common': None
    }

    with pytest.raises(KeyError) as e:
        InputAll(d=d)

    assert 'Key rooms could not be found in the input file.' in str(e.value)


def test_common3():

    d = {
        'common': None,
        'rooms': 3
    }

    with pytest.raises(TypeError) as e:
        InputAll(d=d)

    assert 'Item rooms should be list in the input file.' in str(e.value)
 
