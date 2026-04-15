import unittest
import pytest
import numpy as np

from heat_load_calc.solar_shading import SolarShading
from heat_load_calc.direction import Direction
from heat_load_calc.input_models.input_solar_shading_part import InputSolarShadingPartNot, InputSolarShadingPartSimple, InputSolarShadingPartDetail


def make_input_solar_shading_part_not():

    return InputSolarShadingPartNot(
        existence=False
    )


def make_input_solar_shading_part_simple():

    return InputSolarShadingPartSimple(
        existence=True,
        depth=0.4,
        d_h=2.0,
        d_e=0.1
    )


def make_input_solar_shading_part_detail():

    return InputSolarShadingPartDetail(
        existence=True,
        x1=0.1,
        x2=0.2,
        x3=0.3,
        y1=0.4,
        y2=0.5,
        y3=0.6,
        z_x_pls=0.7,
        z_x_mns=0.8,
        z_y_pls=0.9,
        z_y_mns=1.0
    )


def test_direction_top_bottom():

    SolarShading.create(
        direction=Direction.TOP,
        input_solar_shading_part=make_input_solar_shading_part_not()
    )

    with pytest.raises(ValueError) as e:
        SolarShading.create(
            direction=Direction.TOP,
            input_solar_shading_part=make_input_solar_shading_part_simple()
        )
    
    assert '方位が「上方」「下方」の場合に日除けを定義することはできません。' in str(e.value)

    with pytest.raises(ValueError) as e:
        SolarShading.create(
            direction=Direction.BOTTOM,
            input_solar_shading_part=make_input_solar_shading_part_detail()
        )


def test_solar_shading_not():

    ss = SolarShading.create(
        direction=Direction.S,
        input_solar_shading_part=make_input_solar_shading_part_not()
    )

    np.testing.assert_array_equal(ss.get_f_ss_dn_j_ns(h_sun_ns=np.array([0.0]), a_sun_ns=np.array([0.0])), np.array([0.0]))
    assert ss.get_f_ss_sky_j() == 0.0
    assert ss.get_f_ss_ref_j() == 0.0


def test_solar_shading_simple():
    ss = SolarShading.create(
        direction=Direction.S,
        input_solar_shading_part=make_input_solar_shading_part_simple()
    )

    results = ss.get_f_ss_dn_j_ns(
        h_sun_ns=np.array([0.0, np.pi/4, np.pi/4]),
        a_sun_ns=np.array([0.0, 0.0, np.pi/4])
    )
    expected = [0.0, 0.15, (0.4*2**0.5-0.1)/2.0]

    np.testing.assert_array_almost_equal(results, expected)

    assert pytest.approx(ss.get_f_ss_sky_j()) == 0.068638682

    assert ss.get_f_ss_ref_j() == 0.0


@pytest.mark.skip(reason='not implemented')
def test_solar_shading_detail():
    ss = SolarShading.create(
        direction=Direction.S,
        input_solar_shading_part=make_input_solar_shading_part_detail()
    )

    results = ss.get_f_ss_dn_j_ns(
        h_sun_ns=np.array([0.0, np.pi/4, np.pi/4]),
        a_sun_ns=np.array([0.0, 0.0, np.pi/4])
    )
    expected = None


