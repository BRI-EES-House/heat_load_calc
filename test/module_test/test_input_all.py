import unittest
import pytest

from heat_load_calc import input_all
from heat_load_calc.tenum import EInterval


def for_test_common_interval():

    return {
        'weather': {
            'method': 'ees',
            'region': 6
        }
    }

def test_common_interval1():

    d_common = for_test_common_interval()

    ipt_common = input_all.InputCommon.read(d_common=d_common)

    assert ipt_common.itv == EInterval.M15

def test_common_interval2():

    d_common = for_test_common_interval()
    d_common['interval'] = '15m'
    
    ipt_common = input_all.InputCommon.read(d_common=d_common)

    assert ipt_common.itv == EInterval.M15

def test_common_interval3():

    d_common = for_test_common_interval()
    d_common['interval'] = '30m'
    
    ipt_common = input_all.InputCommon.read(d_common=d_common)

    assert ipt_common.itv == EInterval.M30

def test_common_interval4():

    d_common = for_test_common_interval()
    d_common['interval'] = '20m'

    with pytest.raises(ValueError) as e:
        input_all.InputCommon.read(d_common=d_common)

    assert '\'20m\' is not a valid EInterval' in str(e.value)

def for_test_common_weather():

    return {

    }

def test_common_weather1():

    d_common = for_test_common_weather()

    with pytest.raises(KeyError) as e:
        input_all.InputCommon.read(d_common=d_common)
    
    assert 'Key weather could not be found in common tag.' in str(e.value)

def test_common_weather2():

    d_common = for_test_common_weather()

    d_common['weather'] = {}

    with pytest.raises(KeyError) as e:
        input_all.InputCommon.read(d_common=d_common)
    
    assert 'Key method could not be found in weather tag.' in str(e.value)

def test_common_weather3():

    d_common = for_test_common_weather()

    d_common['weather'] = {
        'method': 'wrong value'
    }

    with pytest.raises(ValueError) as e:
        input_all.InputCommon.read(d_common=d_common)
    
    assert '\'wrong value\' is not a valid EWeatherMethod' in str(e.value)

def test_common_weather4():

    d_common = for_test_common_weather()

    d_common['weather'] = {
        'method': 'ees'
    }

    with pytest.raises(KeyError) as e:
        input_all.InputCommon.read(d_common=d_common)
    
    assert 'Key region should be specified if the ees method applied.' in str(e.value)

def test_common_weather5():

    d_common = for_test_common_weather()

    d_common['weather'] = {
        'method': 'ees',
        'region': 's'
    }

    with pytest.raises(ValueError) as e:
        input_all.InputCommon.read(d_common=d_common)
    
    assert "invalid literal for int() with base 10: 's'" in str(e.value)
