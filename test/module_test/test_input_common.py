import pytest

from heat_load_calc.input_models.input_common import InputCommon
from heat_load_calc.input_models.input_weather import InputWeather
from heat_load_calc.input_models.input_season import InputSeasonDefined, InputSeasonNotDefined
from heat_load_calc.tenum import EInterval, ENumberOfOccupants, EShapeFactorMethod
from heat_load_calc.input_models.input_calculation_day import InputCalculationDay


def default_dict():

    return {
        'weather': {
            'method': 'ees',
            'region': 6
        }
    }


def test_default_value__interval__():

    d_common = default_dict()

    ipt_common = InputCommon.read(d_common=d_common)

    assert ipt_common.itv == EInterval.M15


def test_value__interval__15m__():

    d_common = default_dict()
    d_common['interval'] = '15m'
    
    ipt_common = InputCommon.read(d_common=d_common)

    assert ipt_common.itv == EInterval.M15


def test_value__interval__30m__():

    d_common = default_dict()
    d_common['interval'] = '30m'
    
    ipt_common = InputCommon.read(d_common=d_common)

    assert ipt_common.itv == EInterval.M30


def test_value__interval__is_invalid():

    d_common = default_dict()
    d_common['interval'] = '20m'

    with pytest.raises(ValueError) as e:
        InputCommon.read(d_common=d_common)

    assert '\'20m\' is not a valid EInterval' in str(e.value)


def test_key__weather__not_exists():

    d_common = {}

    with pytest.raises(KeyError) as e:
        InputCommon.read(d_common=d_common)
    
    assert 'Key weather could not be found in common tag.' in str(e.value)


def test_key__weather__exists():

    d_common = default_dict()

    ipt_common = InputCommon.read(d_common=d_common)

    assert isinstance(ipt_common.ipt_weather, InputWeather)


def test_key__season__not_exists():

    d_common = default_dict()

    ipt_common = InputCommon.read(d_common=d_common)

    assert isinstance(ipt_common.ipt_season, InputSeasonNotDefined)


def test_key__season__exists():

    d_common = default_dict()
    d_common['season'] = {
        'is_summer_period_set': False,
        'is_winter_period_set': False
    }

    ipt_common = InputCommon.read(d_common=d_common)

    assert isinstance(ipt_common.ipt_season, InputSeasonDefined)


def test_number_of_occupants_default():

    d_common = default_dict()

    ipt_common = InputCommon.read(d_common=d_common)

    assert ipt_common.n_ocp == ENumberOfOccupants.Auto


def test_value__number_of_occupants__():

    def f(n: str):
        d_common = default_dict()
        d_common['number_of_occupants'] = n
        return d_common

    ipt_common = InputCommon.read(d_common=f('1'))

    assert ipt_common.n_ocp == ENumberOfOccupants.One

    ipt_common = InputCommon.read(d_common=f('2'))

    assert ipt_common.n_ocp == ENumberOfOccupants.Two

    ipt_common = InputCommon.read(d_common=f('3'))

    assert ipt_common.n_ocp == ENumberOfOccupants.Three

    ipt_common = InputCommon.read(d_common=f('4'))

    assert ipt_common.n_ocp == ENumberOfOccupants.Four

    with pytest.raises(ValueError) as e:
        InputCommon.read(d_common=f('5'))
    
    assert '\'5\' is not a valid ENumberOfOccupants' in str(e.value)


def test_key__calculation_day__not_exists():

    d_common = default_dict()

    input_common = InputCommon.read(d_common=d_common)

    assert input_common.ipt_calculation_day is None


def test_key__calculation_day__exists():

    d_common = default_dict()
    d_common['calculation_day'] = {
        'main': 365,
        'run_up': 365,
        'run_up_building': 60
    }

    input_common = InputCommon.read(d_common=d_common)

    assert isinstance(input_common.ipt_calculation_day, InputCalculationDay)


def test_value__shape_factor_method():

    d1 = default_dict()
    d1['mutual_radiation_method'] = 'Nagata'

    ipt1 = InputCommon.read(d_common=d1)

    assert ipt1.shape_factor_method == EShapeFactorMethod.NAGATA

    d2 = default_dict()
    d2['mutual_radiation_method'] = 'area_average'

    ipt2 = InputCommon.read(d_common=d2)

    assert ipt2.shape_factor_method == EShapeFactorMethod.AREA_AVERAGE


def test_value__shape_factor_method_default():

    d = default_dict()

    ipt = InputCommon.read(d_common=d)

    assert ipt.shape_factor_method == EShapeFactorMethod.NAGATA

