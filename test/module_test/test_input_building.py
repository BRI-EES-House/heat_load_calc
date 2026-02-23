import pytest

from heat_load_calc.input_models.input_building import InputBuilding


def get_default_dict():

    return {

    }


def test_():

    d_building = get_default_dict()

    with pytest.raises(KeyError) as e:
        InputBuilding.read(d_building=d_building)

    assert 'Key \'infiltration\' is not defined in tag \'building\'.' in str(e.value)

