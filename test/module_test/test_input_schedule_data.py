import pytest

from heat_load_calc.input_models.input_schedule_data import InputScheduleData, InputScheduleDataConst, InputScheduleDataNumber
from heat_load_calc.input_models.input_schedule_elements_day_types import InputScheduleElementsDayTypes
from heat_load_calc.tenum import EScheduleType

def get_default_dict_const():

    return {
        'const': {
            'Weekday': {},
            'Holiday_Out': {},
            'Holiday_In': {}
        }
    }


def get_default_dict_number():

    return {
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


def test_schedule_const_not_exists():

    d = get_default_dict_const()

    del d['const']

    with pytest.raises(KeyError) as e:
        InputScheduleData.read(id=0, d_schedule_data=d, schedule_type=EScheduleType.CONST)

    assert 'Key \'const\' could not be found in \'schedule\' tag. (ID=0)' in str(e)


def test_schedule_const_exists():

    d = get_default_dict_const()

    ipt = InputScheduleData.read(id=0, d_schedule_data=d, schedule_type=EScheduleType.CONST)

    ipt_const: InputScheduleDataConst = ipt

    assert isinstance(ipt_const.ipt_schedule_data_day_types_const, InputScheduleElementsDayTypes)


def test_schedule_number_not_exists():

    d1 = get_default_dict_number()
    del d1['1']

    d2 = get_default_dict_number()
    del d2['2']
    
    d3 = get_default_dict_number()
    del d3['3']
    
    d4 = get_default_dict_number()
    del d4['4']

    with pytest.raises(KeyError) as e1:
        InputScheduleData.read(id=0, d_schedule_data=d1, schedule_type=EScheduleType.NUMBER)

    assert 'Key \'1\' could not be found in \'schedule\' tag. (ID=0)' in str(e1)

    with pytest.raises(KeyError) as e2:
        InputScheduleData.read(id=0, d_schedule_data=d2, schedule_type=EScheduleType.NUMBER)

    assert 'Key \'2\' could not be found in \'schedule\' tag. (ID=0)' in str(e2)

    with pytest.raises(KeyError) as e3:
        InputScheduleData.read(id=0, d_schedule_data=d3, schedule_type=EScheduleType.NUMBER)

    assert 'Key \'3\' could not be found in \'schedule\' tag. (ID=0)' in str(e3)

    with pytest.raises(KeyError) as e4:
        InputScheduleData.read(id=0, d_schedule_data=d4, schedule_type=EScheduleType.NUMBER)

    assert 'Key \'4\' could not be found in \'schedule\' tag. (ID=0)' in str(e4)


def test_schedule_number_exists():

    d = get_default_dict_number()

    ipt = InputScheduleData.read(id=0, d_schedule_data=d, schedule_type=EScheduleType.NUMBER)

    ipt_number: InputScheduleDataNumber = ipt

    assert isinstance(ipt_number.ipt_schedule_data_day_types_one, InputScheduleElementsDayTypes)
    assert isinstance(ipt_number.ipt_schedule_data_day_types_two, InputScheduleElementsDayTypes)
    assert isinstance(ipt_number.ipt_schedule_data_day_types_three, InputScheduleElementsDayTypes)
    assert isinstance(ipt_number.ipt_schedule_data_day_types_four, InputScheduleElementsDayTypes)
