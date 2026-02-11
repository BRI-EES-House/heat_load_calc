import pytest

from heat_load_calc.input_models.input_season import InputSeason, InputSeasonDefined, InputSeasonNotDefined


def test_is_summer_period_set_key_not_defined():

    d_season = {
        'is_winter_period_set': False
    }

    with pytest.raises(KeyError) as e:
        InputSeasonDefined.read(d_season=d_season)
    
    assert 'Key is_summer_period_set could not be found in season tag.' in str(e.value)


def test_is_winter_period_set_key_not_defined():

    d_season = {
        'is_summer_period_set': False
    }

    with pytest.raises(KeyError) as e:
        InputSeasonDefined.read(d_season=d_season)
    
    assert 'Key is_winter_period_set could not be found in season tag.' in str(e.value)


def test_is_summer_period_set_value_wrong():

    d_season = {
        'is_summer_period_set': 'test',
        'is_winter_period_set': False
    }

    with pytest.raises(ValueError) as e:
        InputSeasonDefined.read(d_season=d_season)
    
    assert 'Value of tag is_summer_period_set should be bool.' in str(e.value)


def test_is_winter_period_set_value_wrong():

    d_season = {
        'is_summer_period_set': False,
        'is_winter_period_set': 'test'
    }

    with pytest.raises(ValueError) as e:
        InputSeasonDefined.read(d_season=d_season)
    
    assert 'Value of tag is_winter_period_set should be bool.' in str(e.value)
 

def test_common_season6():

    def f(v1: str, v2: str):

        return {
            'is_summer_period_set': True,
            'is_winter_period_set': False,
            'summer_start': v1,
            'summer_end': v2
        }

    with pytest.raises(ValueError) as e:
        InputSeasonDefined.read(d_season=f('7/1/1', '9/30'))
    
    assert 'Value of summer_start is wrong format or not exist day.' in str(e.value)

    with pytest.raises(ValueError) as e:
        InputSeasonDefined.read(d_season=f('7/32', '9/30'))
    
    assert 'Value of summer_start is wrong format or not exist day.' in str(e.value)

    with pytest.raises(TypeError) as e:
        InputSeasonDefined.read(d_season=f(2, '9/30'))
    
    assert 'Value of summer_start is not str.' in str(e.value)

    with pytest.raises(ValueError) as e:
        InputSeasonDefined.read(d_season=f('7/1', '9/30/1'))
    
    assert 'Value of summer_end is wrong format or not exist day.' in str(e.value)

    with pytest.raises(ValueError) as e:
        InputSeasonDefined.read(d_season=f('7/1', '9/31'))
    
    assert 'Value of summer_end is wrong format or not exist day.' in str(e.value)

    with pytest.raises(TypeError) as e:
        InputSeasonDefined.read(d_season=f('7/1', 2))
    
    assert 'Value of summer_end is not str.' in str(e.value)


def test_common_season7():

    def f(v1: str, v2: str):

        return {
            'is_summer_period_set': False,
            'is_winter_period_set': True,
            'winter_start': v1,
            'winter_end': v2
        }

        return d_common

    with pytest.raises(ValueError) as e:
        InputSeasonDefined.read(d_season=f('11/1/1', '3/31'))
    
    assert 'Value of winter_start is wrong format or not exist day.' in str(e.value)

    with pytest.raises(ValueError) as e:
        InputSeasonDefined.read(d_season=f('11/32', '3/31'))
    
    assert 'Value of winter_start is wrong format or not exist day.' in str(e.value)

    with pytest.raises(TypeError) as e:
        InputSeasonDefined.read(d_season=f(2, '3/31'))
    
    assert 'Value of winter_start is not str.' in str(e.value)

    with pytest.raises(ValueError) as e:
        InputSeasonDefined.read(d_season=f('11/1', '3/31/1'))
    
    assert 'Value of winter_end is wrong format or not exist day.' in str(e.value)

    with pytest.raises(ValueError) as e:
        InputSeasonDefined.read(d_season=f('11/1', '3/32'))
    
    assert 'Value of winter_end is wrong format or not exist day.' in str(e.value)

    with pytest.raises(TypeError) as e:
        InputSeasonDefined.read(d_season=f('11/1', 2))
    
    assert 'Value of winter_end is not str.' in str(e.value)

