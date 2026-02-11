import pytest


from heat_load_calc.input_models.input_weather import InputWeather, InputWeatherEES, InputWeatherFile
from heat_load_calc.tenum import EWeatherMethod, ERegion


def test_key__method__not_exists():

    d_weather = {}

    with pytest.raises(KeyError) as e:
        InputWeather.read(d_weather=d_weather)
    
    assert 'Key method could not be found in weather tag.' in str(e.value)


def test_value__method__wrong():

    d_weather = {
        'method': 'wrong value'
    }

    with pytest.raises(ValueError) as e:
        InputWeather.read(d_weather=d_weather)

    assert '\'wrong value\' is not a valid EWeatherMethod' in str(e.value)


def test_key__region__not_exists():

    d_weather = {
        'method': 'ees'
    }

    with pytest.raises(KeyError) as e:
        InputWeather.read(d_weather=d_weather)
    
    assert 'Key region should be specified if the ees method applied.' in str(e.value)


def test_value__region__is_invalid():

    d_weather = {
        'method': 'ees',
        'region': 's'
    }

    with pytest.raises(ValueError) as e:
        InputWeather.read(d_weather=d_weather)
    
    assert "invalid literal for int() with base 10: 's'" in str(e.value)


def test_value__region__is_out_of_range():

    d_weather = {
        'method': 'ees',
        'region': '9'
    }

    with pytest.raises(ValueError) as e:
        InputWeather.read(d_weather=d_weather)
    
    assert '9 is not a valid ERegion' in str(e.value)


def test_value__ees_method__and__region__():

    d_weather = {
        'method': 'ees',
        'region': '6'
    }

    ipt_weather = InputWeather.read(d_weather=d_weather)

    ipt_weather_ees: InputWeatherEES = ipt_weather
    
    assert ipt_weather_ees.method == EWeatherMethod.EES

    assert ipt_weather_ees.region == ERegion.Region6


def test_key__file_path__not_exists():

    d_weather = {
        'method': 'file'
    }

    with pytest.raises(KeyError) as e:
        InputWeather.read(d_weather=d_weather)

    assert 'Key file_path should be specified if the file method applied.' in str(e.value)


def test_value__latitude__is_invalid():

    x = 'some_file_name'

    d_weather = {
        'method': 'file',
        'file_path': x,
        'latitude': 'y',
        'longitude': 139.44
    }

    with pytest.raises(ValueError) as e:
        InputWeather.read(d_weather=d_weather)

    assert 'could not convert string to float: \'y\'' in str(e.value)


def test_value__latitude__is_out_of_range():

    x = 'some_file_name'

    d_weather = {
        'method': 'file',
        'file_path': x,
        'latitude': 91.0,
        'longitude': 139.44
    }

    with pytest.raises(ValueError) as e:
        InputWeather.read(d_weather=d_weather)

    assert 'Latitude should be defined between -90.0 deg. and 90.0 deg.' in str(e.value)


def test_value__longitude__is_invalid():

    x = 'some_file_name'

    d_weather = {
        'method': 'file',
        'file_path': x,
        'latitude': 35.39,
        'longitude': 'y'
    }

    with pytest.raises(ValueError) as e:
        InputWeather.read(d_weather=d_weather)

    assert 'could not convert string to float: \'y\'' in str(e.value)


def test_value__longitude__is_out_of_range():

    x = 'some_file_name'

    d_weather = {
        'method': 'file',
        'file_path': x,
        'latitude': 35.39,
        'longitude': 181.0
    }

    with pytest.raises(ValueError) as e:
        InputWeather.read(d_weather=d_weather)

    assert 'Longitude should be defined between -180.0 deg. and 180.0 deg.' in str(e.value)


def test_latitude_and_longitude_value():

    x = 'some_file_name'

    d_weather = {
        'method': 'file',
        'file_path': x,
        'latitude': 35.39,
        'longitude': 139.44
    }

    ipt_weather = InputWeather.read(d_weather=d_weather)

    ipt_weather_file: InputWeatherFile = ipt_weather

    assert ipt_weather_file.method == EWeatherMethod.FILE

    assert ipt_weather_file.latitude == 35.39

    assert ipt_weather_file.longitude == 139.44

