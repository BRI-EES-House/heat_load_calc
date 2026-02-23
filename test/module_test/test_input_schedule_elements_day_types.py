import pytest

from heat_load_calc.input_models.input_schedule_elements_day_types import InputScheduleElementsDayTypes
from heat_load_calc.input_models.input_schedule_element import InputScheduleElement


def make_default_dict():

    return {
        'Weekday': {},
        'Holiday_Out': {},
        'Holiday_In': {}
    }


def test_input_schedule_elements_exist():

    d = make_default_dict()

    ipt = InputScheduleElementsDayTypes.read(id=0, d=d)

    assert isinstance(ipt.input_schedule_elements_weekday, InputScheduleElement)
    assert isinstance(ipt.input_schedule_elements_holiday_in, InputScheduleElement)
    assert isinstance(ipt.input_schedule_elements_holiday_out, InputScheduleElement)


def test_input_schedule_elements_not_exists():

    dw = make_default_dict()
    dho = make_default_dict()
    dhi = make_default_dict()

    del dw['Weekday']
    del dho['Holiday_Out']
    del dhi['Holiday_In']

    with pytest.raises(KeyError) as ew:
        InputScheduleElementsDayTypes.read(id=0, d=dw)
    
    assert 'Key \'Weekday\' could not be found in \'const\' tag. (ID=0)' in str(ew)

    with pytest.raises(KeyError) as eho:
        InputScheduleElementsDayTypes.read(id=0, d=dho)
    
    assert 'Key \'Holiday_Out\' could not be found in \'const\' tag. (ID=0)' in str(eho)

    with pytest.raises(KeyError) as ehi:
        InputScheduleElementsDayTypes.read(id=0, d=dhi)
    
    assert 'Key \'Holiday_In\' could not be found in \'const\' tag. (ID=0)' in str(ehi)


