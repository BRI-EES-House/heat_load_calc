import pytest

from heat_load_calc.input_models.input_schedule_data import InputScheduleData, InputScheduleDataConst, InputScheduleDataNumber
from heat_load_calc.input_models.input_schedule_elements_day_types import InputScheduleElementsDayTypes
from heat_load_calc.tenum import EScheduleType

def get_default_dict_const():

    return {
        'schedule_type': 'const',
        'schedule': {
            'const': {
                'Weekday': {},
                'Holiday_Out': {},
                'Holiday_In': {}
            }
        }
    }


def get_default_dict_number():

    return {
        'schedule_type': 'number',
        'schedule': {
            '1': {
                'Weekday': {},
                'Holiday_Out': {},
                'Holiday_In': {}
            },
            '2': {
                'Weekday': {},
                'Holiday_Out': {},
                'Holiday_In': {}
            },
            '3': {
                'Weekday': {},
                'Holiday_Out': {},
                'Holiday_In': {}
            },
            '4': {
                'Weekday': {},
                'Holiday_Out': {},
                'Holiday_In': {}
            }
        }
    }


def get_default_dict_correct_file():

    return {
        'name': 'dammy_for_test_correct'
    }


def get_default_dict_incorrect_file():

    return {
        'name': 'dammy_for_test_incorrect'
    }


def test_key__name__not_exists():

    d = get_default_dict_correct_file()
    
    del d['name']

    with pytest.raises(KeyError) as e:
        InputScheduleData.read(id=0, d_schedule=d)

    assert 'Key \'name\' should be defined in \'schedule\' tag. (ID=0)' in str(e)


def test_value__name__invalid():

    d = get_default_dict_correct_file()

    d['name'] = 'wrong_file_name'

    with pytest.raises(FileNotFoundError) as e:
        InputScheduleData.read(id=0, d_schedule=d)
    
    assert "Schedule file \'wrong_file_name\' could not found." in str(e)


def test_read_correct_file():

    d = get_default_dict_correct_file()

    ipt = InputScheduleData.read(id=0, d_schedule=d)

    assert ipt.schedule_type == EScheduleType.CONST

    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_weekday.number_of_people == [0.0]
    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_weekday.heat_generation_appliances == [100.0]
    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_weekday.heat_generation_lighting == [70.0]
    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_weekday.heat_generation_cooking == [230.0]
    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_weekday.vapor_generation_cooking == [0.7]
    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_weekday.local_vent_amount == [30.0]
    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_weekday.is_temp_limit_set == [1]

    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_holiday_in.number_of_people == [0.0]
    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_holiday_in.heat_generation_appliances == [100.0]
    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_holiday_in.heat_generation_lighting == [70.0]
    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_holiday_in.heat_generation_cooking == [230.0]
    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_holiday_in.vapor_generation_cooking == [0.7]
    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_holiday_in.local_vent_amount == [30.0]
    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_holiday_in.is_temp_limit_set == [1]

    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_holiday_out.number_of_people == [0.0]
    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_holiday_out.heat_generation_appliances == [100.0]
    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_holiday_out.heat_generation_lighting == [70.0]
    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_holiday_out.heat_generation_cooking == [230.0]
    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_holiday_out.vapor_generation_cooking == [0.7]
    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_holiday_out.local_vent_amount == [30.0]
    assert ipt.ipt_schedule_data_day_types_const.input_schedule_elements_holiday_out.is_temp_limit_set == [1]


def test_read_incorrect_file():

    d = get_default_dict_incorrect_file()

    with pytest.raises(KeyError) as e:
        InputScheduleData.read(id=0, d_schedule=d)
    
    assert 'Key \'schedule_type\' should be defined in \'schedule\' tag. (ID=0)' in str(e)


def test_schedule_type_exists():

    dc = get_default_dict_const()
    dn = get_default_dict_number()

    ipt_c = InputScheduleData.read(id=0, d_schedule=dc)
    ipt_n = InputScheduleData.read(id=0, d_schedule=dn)

    assert ipt_c.schedule_type == EScheduleType.CONST
    assert ipt_n.schedule_type == EScheduleType.NUMBER


def test_schedule_and_name_not_exists():

    dc = get_default_dict_const()
    dn = get_default_dict_number()

    del dc['schedule']
    del dn['schedule']

    with pytest.raises(KeyError) as ec:
        InputScheduleData.read(id=0, d_schedule=dc)
    
    assert 'Key \'name\' should be defined in \'schedule\' tag. (ID=0)' in str(ec)

    with pytest.raises(KeyError) as en:
        InputScheduleData.read(id=0, d_schedule=dn)
    
    assert 'Key \'name\' should be defined in \'schedule\' tag. (ID=0)' in str(en)


def test_schedule_type_invalid_value():

    d = get_default_dict_const()
    
    d['schedule_type'] = 'error'

    with pytest.raises(ValueError) as e:
        InputScheduleData.read(id=0, d_schedule=d)

    assert 'An invalid value was specified for \'schedule_type\' in \'schedule\' tag. (ID=0)' in str(e)


def test_schedule_const_not_exists():

    d = get_default_dict_const()

    del d['schedule']['const']

    with pytest.raises(KeyError) as e:
        InputScheduleData.read(id=0, d_schedule=d)

    assert 'Key \'const\' could not be found in \'schedule\' tag. (ID=0)' in str(e)


def test_schedule_const_exists():

    d = get_default_dict_const()

    ipt = InputScheduleData.read(id=0, d_schedule=d)

    ipt_const: InputScheduleDataConst = ipt

    assert isinstance(ipt_const.ipt_schedule_data_day_types_const, InputScheduleElementsDayTypes)


def test_schedule_number_not_exists():

    d1 = get_default_dict_number()
    del d1['schedule']['1']

    d2 = get_default_dict_number()
    del d2['schedule']['2']
    
    d3 = get_default_dict_number()
    del d3['schedule']['3']
    
    d4 = get_default_dict_number()
    del d4['schedule']['4']

    with pytest.raises(KeyError) as e1:
        InputScheduleData.read(id=0, d_schedule=d1)

    assert 'Key \'1\' could not be found in \'schedule\' tag. (ID=0)' in str(e1)

    with pytest.raises(KeyError) as e2:
        InputScheduleData.read(id=0, d_schedule=d2)

    assert 'Key \'2\' could not be found in \'schedule\' tag. (ID=0)' in str(e2)

    with pytest.raises(KeyError) as e3:
        InputScheduleData.read(id=0, d_schedule=d3)

    assert 'Key \'3\' could not be found in \'schedule\' tag. (ID=0)' in str(e3)

    with pytest.raises(KeyError) as e4:
        InputScheduleData.read(id=0, d_schedule=d4)

    assert 'Key \'4\' could not be found in \'schedule\' tag. (ID=0)' in str(e4)


def test_schedule_number_exists():

    d = get_default_dict_number()

    ipt = InputScheduleData.read(id=0, d_schedule=d)

    ipt_number: InputScheduleDataNumber = ipt

    assert isinstance(ipt_number.ipt_schedule_data_day_types_one, InputScheduleElementsDayTypes)
    assert isinstance(ipt_number.ipt_schedule_data_day_types_two, InputScheduleElementsDayTypes)
    assert isinstance(ipt_number.ipt_schedule_data_day_types_three, InputScheduleElementsDayTypes)
    assert isinstance(ipt_number.ipt_schedule_data_day_types_four, InputScheduleElementsDayTypes)
