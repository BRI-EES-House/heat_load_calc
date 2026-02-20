import pytest

from heat_load_calc.input_models.input_schedule_elements import InputScheduleElements


def get_default_dict():

    return {}


def test_value():

    d = get_default_dict()

    d['number_of_people'] = [1.0]
    d['heat_generation_appliances'] = [100.0]
    d['heat_generation_lighting'] = [90.0]
    d['heat_generation_cooking'] = [200.0]
    d['vapor_generation_cooking'] = [7.0]
    d['local_vent_amount'] = [55.0]
    d['is_temp_limit_set'] = [1]


    ipt = InputScheduleElements.read(id=0, d=d)

    assert ipt.number_of_people == [1.0]

    assert ipt.heat_generation_appliances == [100.0]

    assert ipt.heat_generation_lighting == [90.0]

    assert ipt.heat_generation_cooking == [200.0]

    assert ipt.vapor_generation_cooking == [7.0]

    assert ipt.local_vent_amount == [55.0]

    assert ipt.is_temp_limit_set == [1]


def test_number_of_people_default_value():

    d = get_default_dict()

    ipt = InputScheduleElements.read(id=0, d=d)

    assert ipt.number_of_people == [0.0]

    assert ipt.heat_generation_appliances == [0.0]

    assert ipt.heat_generation_lighting == [0.0]

    assert ipt.heat_generation_cooking == [0.0]

    assert ipt.vapor_generation_cooking == [0.0]

    assert ipt.local_vent_amount == [0.0]

    assert ipt.is_temp_limit_set == [0]


def test_number_of_people_wrong_value():

    d = get_default_dict()

    d['number_of_people'] = ['error']

    with pytest.raises(ValueError) as e:

        InputScheduleElements.read(id=0, d=d)

    assert 'An invalid value was specified for \'number_of_people\' in \'schedule\' tag. (ID=0)' in str(e)


def test_heat_generation_appliances_wrong_value():

    d = get_default_dict()

    d['heat_generation_appliances'] = ['error']

    with pytest.raises(ValueError) as e:

        InputScheduleElements.read(id=0, d=d)

    assert 'An invalid value was specified for \'heat_generation_appliances\' in \'schedule\' tag. (ID=0)' in str(e)


def test_heat_generation_lighting_wrong_value():

    d = get_default_dict()

    d['heat_generation_lighting'] = ['error']

    with pytest.raises(ValueError) as e:

        InputScheduleElements.read(id=0, d=d)

    assert 'An invalid value was specified for \'heat_generation_lighting\' in \'schedule\' tag. (ID=0)' in str(e)


def test_heat_generation_cooking_wrong_value():

    d = get_default_dict()

    d['heat_generation_cooking'] = ['error']

    with pytest.raises(ValueError) as e:

        InputScheduleElements.read(id=0, d=d)

    assert 'An invalid value was specified for \'heat_generation_cooking\' in \'schedule\' tag. (ID=0)' in str(e)


def test_vapor_generation_cooking_wrong_value():

    d = get_default_dict()

    d['vapor_generation_cooking'] = ['error']

    with pytest.raises(ValueError) as e:

        InputScheduleElements.read(id=0, d=d)

    assert 'An invalid value was specified for \'vapor_generation_cooking\' in \'schedule\' tag. (ID=0)' in str(e)


def test_local_vent_amount_wrong_value():

    d = get_default_dict()

    d['local_vent_amount'] = ['error']

    with pytest.raises(ValueError) as e:

        InputScheduleElements.read(id=0, d=d)

    assert 'An invalid value was specified for \'local_vent_amount\' in \'schedule\' tag. (ID=0)' in str(e)


def test_is_temp_limit_set_wrong_value():

    d = get_default_dict()

    d['is_temp_limit_set'] = ['error']

    with pytest.raises(ValueError) as e:

        InputScheduleElements.read(id=0, d=d)

    assert 'An invalid value was specified for \'is_temp_limit_set\' in \'schedule\' tag. (ID=0)' in str(e)


def test_number_of_people_invalid_list_length():

    d = get_default_dict()

    d['number_of_people'] = [0.0, 0.0]

    with pytest.raises(ValueError) as e:

        InputScheduleElements.read(id=0, d=d)

    assert 'The length of the list should be 1, 24, 48, or 96 for \'number_of_people\' in \'schedule\' tag. (ID=0)' in str(e)


def test_heat_generation_appliances_invalid_list_length():

    d = get_default_dict()

    d['heat_generation_appliances'] = [0.0, 0.0]

    with pytest.raises(ValueError) as e:

        InputScheduleElements.read(id=0, d=d)

    assert 'The length of the list should be 1, 24, 48, or 96 for \'heat_generation_appliances\' in \'schedule\' tag. (ID=0)' in str(e)


def test_heat_generation_lighting_invalid_list_length():

    d = get_default_dict()

    d['heat_generation_lighting'] = [0.0, 0.0]

    with pytest.raises(ValueError) as e:

        InputScheduleElements.read(id=0, d=d)

    assert 'The length of the list should be 1, 24, 48, or 96 for \'heat_generation_lighting\' in \'schedule\' tag. (ID=0)' in str(e)


def test_heat_generation_cooking_invalid_list_length():

    d = get_default_dict()

    d['heat_generation_cooking'] = [0.0, 0.0]

    with pytest.raises(ValueError) as e:

        InputScheduleElements.read(id=0, d=d)

    assert 'The length of the list should be 1, 24, 48, or 96 for \'heat_generation_cooking\' in \'schedule\' tag. (ID=0)' in str(e)


def test_vapor_generation_cooking_invalid_list_length():

    d = get_default_dict()

    d['vapor_generation_cooking'] = [0.0, 0.0]

    with pytest.raises(ValueError) as e:

        InputScheduleElements.read(id=0, d=d)

    assert 'The length of the list should be 1, 24, 48, or 96 for \'vapor_generation_cooking\' in \'schedule\' tag. (ID=0)' in str(e)


def test_local_vent_amount_invalid_list_length():

    d = get_default_dict()

    d['local_vent_amount'] = [0.0, 0.0]

    with pytest.raises(ValueError) as e:

        InputScheduleElements.read(id=0, d=d)

    assert 'The length of the list should be 1, 24, 48, or 96 for \'local_vent_amount\' in \'schedule\' tag. (ID=0)' in str(e)


def test_is_temp_limit_set_invalid_list_length():

    d = get_default_dict()

    d['is_temp_limit_set'] = [0.0, 0.0]

    with pytest.raises(ValueError) as e:

        InputScheduleElements.read(id=0, d=d)

    assert 'The length of the list should be 1, 24, 48, or 96 for \'is_temp_limit_set\' in \'schedule\' tag. (ID=0)' in str(e)

