import pytest

from heat_load_calc.input_models.input_calculation_day import InputCalculationDay


def test_all_key_defined():

    d_calculation_day = {
        'main': 365,
        'run_up': 365,
        'run_up_building': 60
    }

    ipt_calculation_day = InputCalculationDay.read(d_calculation_day=d_calculation_day)

    assert ipt_calculation_day.n_d_main == 365
    assert ipt_calculation_day.n_d_run_up == 365
    assert ipt_calculation_day.n_d_run_up_build == 60


def test_only_key__main__defined():

    d_calculation_day = {
        'main': 365
    }

    ipt_calculation_day = InputCalculationDay.read(d_calculation_day=d_calculation_day)

    assert ipt_calculation_day.n_d_main == 365
    assert ipt_calculation_day.n_d_run_up is None
    assert ipt_calculation_day.n_d_run_up_build is None



def test_key__main__not_exists():
    
    d_calculation_day = {
        'run_up': 365,
        'run_up_building': 60
    }

    with pytest.raises(KeyError) as e:
        InputCalculationDay.read(d_calculation_day=d_calculation_day)

    #assert 'Key \'main\' is not esists in tag \'calculation_day\'.' in str(e)    


def test_key__main__invalid_value():

    d_calculation_day = {
        'main': 'test',
        'run_up': 365,
        'run_up_building': 60
    }

    with pytest.raises(ValueError) as e:
        InputCalculationDay.read(d_calculation_day=d_calculation_day)

    assert 'An invalid value was specified in \'calculation_day\' tag.' in str(e)


def test_key__run_up__invalid_value():

    d_calculation_day = {
        'main': 365,
        'run_up': 'test',
        'run_up_building': 60
    }

    with pytest.raises(ValueError) as e:
        InputCalculationDay.read(d_calculation_day=d_calculation_day)

    assert 'An invalid value was specified in \'calculation_day\' tag.' in str(e)


def test_key__run_up_building__invalid_value():

    d_calculation_day = {
        'main': 365,
        'run_up': 365,
        'run_up_building': 'test'
    }

    with pytest.raises(ValueError) as e:
        InputCalculationDay.read(d_calculation_day=d_calculation_day)

    assert 'An invalid value was specified in \'calculation_day\' tag.' in str(e)


def test_key__main__out_of_range_under_1():

    d_calculation_day = {
        'main': 0,
        'run_up': 365,
        'run_up_building': 60
    }

    with pytest.raises(ValueError) as e:
        InputCalculationDay.read(d_calculation_day=d_calculation_day)

    assert 'Value \'main\' in tag \'calculation_day\' is out of range.' in str(e)


def test_key__main__out_of_range_over_365():

    d_calculation_day = {
        'main': 366,
        'run_up': 365,
        'run_up_building': 60
    }

    with pytest.raises(ValueError) as e:
        InputCalculationDay.read(d_calculation_day=d_calculation_day)

    assert 'Value \'main\' in tag \'calculation_day\' is out of range.' in str(e)

