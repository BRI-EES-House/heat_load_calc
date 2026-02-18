import pytest

from heat_load_calc.input_models.input_infiltration import InputInfiltration
from heat_load_calc.tenum import EStory, EStructure, EInsidePressure


def get_default_dict_c_value_specify():

    return {
        'method': 'balance_residential',
        'story': 2,
        'c_value_estimate': 'specify',
        'c_value': 2.0,
        'inside_pressure': 'negative'
    }

def get_default_dict_c_value_calculate():

    return {
        'method': 'balance_residential',
        'story': 2,
        'c_value_estimate': 'calculate',
        'ua_value': 0.2,
        'struct': 'wooden',
        'inside_pressure': 'negative'
    }


def test_key_method_not_exists():

    d_infiltration = get_default_dict_c_value_specify()

    del d_infiltration['method']

    with pytest.raises(KeyError) as e:
        InputInfiltration.read(d_infiltration=d_infiltration)
    

    assert 'Key \'method\' should be defined in \'infiltration\' tag.' in str(e)


def test_key_method_wrong_value():
    
    d_infiltration = get_default_dict_c_value_specify()
    d_infiltration['method'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputInfiltration.read(d_infiltration=d_infiltration)

    assert 'An invalid value is specified for value \'method\' in \'infiltration\' tag.' in str(e)


def test_key_method_value():

    d1 = get_default_dict_c_value_specify()
    d2 = get_default_dict_c_value_calculate()

    ipt1 = InputInfiltration.read(d_infiltration=d1)
    ipt2 = InputInfiltration.read(d_infiltration=d2)

    assert ipt1.method == 'balance_residential'
    assert ipt2.method == 'balance_residential'



def test_key_story_not_exists():

    d_infiltration = get_default_dict_c_value_specify()

    del d_infiltration['story']

    with pytest.raises(KeyError) as e:
        InputInfiltration.read(d_infiltration=d_infiltration)

    assert 'Key \'story\' should be defined in \'infiltration\' tag.' in str(e.value)


def test_value_story_wrong_value():

    d_infiltration = get_default_dict_c_value_specify()

    d_infiltration['story'] = 3

    with pytest.raises(ValueError) as e:
        InputInfiltration.read(d_infiltration=d_infiltration)

    assert '3 is not a valid EStory' in str(e)


def test_value_story_wrong_type():

    d_infiltration = get_default_dict_c_value_specify()

    d_infiltration['story'] = 'first'

    with pytest.raises(ValueError) as e:
        InputInfiltration.read(d_infiltration=d_infiltration)

    assert '\'first\' is not a valid EStory' in str(e)


def test_value_story():

    d1 = get_default_dict_c_value_specify()
    d2 = get_default_dict_c_value_calculate()

    ipt1 = InputInfiltration.read(d_infiltration=d1)
    ipt2 = InputInfiltration.read(d_infiltration=d2)

    assert ipt1.story == EStory.TWO
    assert ipt2.story == EStory.TWO


def test_key_c_value_estimate_not_exits():

    d_infiltration = get_default_dict_c_value_specify()

    del d_infiltration['c_value_estimate']

    with pytest.raises(KeyError) as e:
        InputInfiltration.read(d_infiltration=d_infiltration)

    assert 'Key \'c_value_estimate\' should be defined in \'infiltration\' tag.' in str(e)


def test_value_c_value_estimate_wrong_value():

    d_infiltration = get_default_dict_c_value_specify()

    d_infiltration['c_value_estimate'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputInfiltration.read(d_infiltration=d_infiltration)

    assert 'An invalid value is specified in key \'c_value_estimate\' in tag \'infiltration\'.' in str(e)


def test_value_c_value_estimate():

    d1 = get_default_dict_c_value_specify()
    d2 = get_default_dict_c_value_calculate()

    ipt1 = InputInfiltration.read(d_infiltration=d1)
    ipt2 = InputInfiltration.read(d_infiltration=d2)

    assert ipt1.c_value_estimate == 'specify'
    assert ipt2.c_value_estimate == 'calculate'


def test_key_c_value_not_exists():

    d_infiltration = get_default_dict_c_value_specify()

    del d_infiltration['c_value']

    with pytest.raises(KeyError) as e:
        InputInfiltration.read(d_infiltration=d_infiltration)
    
    assert 'Key \'c_value\' should be defined in \'infiltration\' tag.' in str(e)


def test_value_c_value_wrong_value():

    d_infiltration = get_default_dict_c_value_specify()

    d_infiltration['c_value'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputInfiltration.read(d_infiltration=d_infiltration)

    assert 'Invalid value was specified in key \'c_value\' in \'infiltration\' tag.' in str(e)


def test_value_c_value_out_of_range():

    d_infiltration = get_default_dict_c_value_specify()

    d_infiltration['c_value'] = -0.01

    with pytest.raises(ValueError) as e:
        InputInfiltration.read(d_infiltration=d_infiltration)

    assert 'Value \'c_value\' should be more than or equal to zero.' in str(e.value)


def test_vale_c_value():

    d1 = get_default_dict_c_value_specify()
    d2 = get_default_dict_c_value_calculate()

    ipt1 = InputInfiltration.read(d_infiltration=d1)
    ipt2 = InputInfiltration.read(d_infiltration=d2)

    assert ipt1.c_value == 2.0
    assert ipt2.c_value is None


def test_key_ua_value_not_exists():

    d_infiltration = get_default_dict_c_value_calculate()

    del d_infiltration['ua_value']

    with pytest.raises(KeyError) as e:
        InputInfiltration.read(d_infiltration=d_infiltration)

    assert 'Key \'ua_value\' should be defined in \'infiltration\' tag.' in str(e.value)


def test_value_ua_value_wrong_value():

    d_infiltration = get_default_dict_c_value_calculate()

    d_infiltration['ua_value'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputInfiltration.read(d_infiltration=d_infiltration)

    assert 'Invalid value was specified in key \'ua_value\' in \'infiltration\' tag.' in str(e)


def test_value_ua_value_out_of_range():

    d_infiltration = get_default_dict_c_value_calculate()

    d_infiltration['ua_value'] = -0.01

    with pytest.raises(ValueError) as e:
        InputInfiltration.read(d_infiltration=d_infiltration)

    assert 'Invalid value was specified in key \'ua_value\' in \'infiltration\' tag.' in str(e)


def test_value_ua_value():

    d1 = get_default_dict_c_value_specify()
    d2 = get_default_dict_c_value_calculate()

    ipt1 = InputInfiltration.read(d_infiltration=d1)
    ipt2 = InputInfiltration.read(d_infiltration=d2)

    assert ipt1.ua_value is None
    assert ipt2.ua_value == 0.2


def test_key_struct_not_exists():

    d_infiltration = get_default_dict_c_value_calculate()

    del d_infiltration['struct']

    with pytest.raises(KeyError) as e:
        InputInfiltration.read(d_infiltration=d_infiltration)

    assert 'Key \'struct\' should be defined in \'infiltration\' tag.' in str(e.value)


def test_value_struct_wrong_value():

    d_infiltration = get_default_dict_c_value_calculate()

    d_infiltration['struct'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputInfiltration.read(d_infiltration=d_infiltration)

    assert 'Invalid value was specified in key \'struct\' in \'infiltration\' tag.' in str(e)


def test_value_struct():

    d1 = get_default_dict_c_value_specify()
    d2 = get_default_dict_c_value_calculate()

    ipt1 = InputInfiltration.read(d_infiltration=d1)
    ipt2 = InputInfiltration.read(d_infiltration=d2)

    assert ipt1.struct is None
    assert ipt2.struct == EStructure.WOODEN


def test_key_inside_pressure_not_exists():

    d_infiltration = get_default_dict_c_value_calculate()

    del d_infiltration['inside_pressure']

    with pytest.raises(KeyError) as e:
        InputInfiltration.read(d_infiltration=d_infiltration)

    assert 'Key \'inside_pressure\' should be defined in \'infiltration\' tag.' in str(e.value)


def test_value_inside_pressure_wrong_value():

    d_infiltration = get_default_dict_c_value_calculate()

    d_infiltration['inside_pressure'] = 'wrong_value'

    with pytest.raises(ValueError) as e:
        InputInfiltration.read(d_infiltration=d_infiltration)

    assert '\'wrong_value\' is not a valid EInsidePressure' in str(e)


def test_value_inside_pressure():

    d1 = get_default_dict_c_value_specify()
    d2 = get_default_dict_c_value_calculate()

    ipt1 = InputInfiltration.read(d_infiltration=d1)
    ipt2 = InputInfiltration.read(d_infiltration=d2)

    assert ipt1.inside_pressure == EInsidePressure.NEGATIVE
    assert ipt2.inside_pressure == EInsidePressure.NEGATIVE
    
