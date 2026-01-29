import unittest
import pytest

from heat_load_calc import input_all
from heat_load_calc.tenum import EInterval, ERegion, EWeatherMethod


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


def test_common_weather6():

    d_common = for_test_common_weather()

    d_common['weather'] = {
        'method': 'ees',
        'region': '9'
    }

    with pytest.raises(ValueError) as e:
        input_all.InputCommon.read(d_common=d_common)
    
    assert '9 is not a valid ERegion' in str(e.value)


def test_common_weather7():

    d_common = for_test_common_weather()

    d_common['weather'] = {
        'method': 'ees',
        'region': '6'
    }

    ipt_common = input_all.InputCommon.read(d_common=d_common)

    ipt_weather: input_all.InputWeatherEES = ipt_common.ipt_weather
    
    assert ipt_weather.method == EWeatherMethod.EES

    assert ipt_weather.region == ERegion.Region6


def test_common_weather8():

    d_common = for_test_common_weather()

    d_common['weather'] = {
        'method': 'file'
    }

    with pytest.raises(KeyError) as e:
        input_all.InputCommon.read(d_common=d_common)

    assert 'Key file_path should be specified if the file method applied.' in str(e.value)


def test_common_weather9():

    d_common = for_test_common_weather()

    x = 'some_file_name'

    d_common['weather'] = {
        'method': 'file',
        'file_path': x,
        'latitude': 'y',
        'longitude': 139.44
    }

    with pytest.raises(ValueError) as e:
        input_all.InputCommon.read(d_common=d_common)

    assert 'could not convert string to float: \'y\'' in str(e.value)


def test_common_weather10():

    d_common = for_test_common_weather()

    x = 'some_file_name'

    d_common['weather'] = {
        'method': 'file',
        'file_path': x,
        'latitude': 91.0,
        'longitude': 139.44
    }

    with pytest.raises(ValueError) as e:
        input_all.InputCommon.read(d_common=d_common)

    assert 'Latitude should be defined between -90.0 deg. and 90.0 deg.' in str(e.value)


def test_common_weather11():

    d_common = for_test_common_weather()

    x = 'some_file_name'

    d_common['weather'] = {
        'method': 'file',
        'file_path': x,
        'latitude': 35.39,
        'longitude': 'y'
    }

    with pytest.raises(ValueError) as e:
        input_all.InputCommon.read(d_common=d_common)

    assert 'could not convert string to float: \'y\'' in str(e.value)


def test_common_weather12():

    d_common = for_test_common_weather()

    x = 'some_file_name'

    d_common['weather'] = {
        'method': 'file',
        'file_path': x,
        'latitude': 35.39,
        'longitude': 181.0
    }

    with pytest.raises(ValueError) as e:
        input_all.InputCommon.read(d_common=d_common)

    assert 'Longitude should be defined between -180.0 deg. and 180.0 deg.' in str(e.value)


def test_common_weather13():

    d_common = for_test_common_weather()

    x = 'some_file_name'

    d_common['weather'] = {
        'method': 'file',
        'file_path': x,
        'latitude': 35.39,
        'longitude': 139.44
    }

    ipt_common = input_all.InputCommon.read(d_common=d_common)

    ipt_weather: input_all.InputWeatherFile = ipt_common.ipt_weather

    assert ipt_weather.method == EWeatherMethod.FILE

    assert ipt_weather.latitude == 35.39

    assert ipt_weather.longitude == 139.44




