import unittest
import pytest
import numpy as np
import math

from heat_load_calc import building
from heat_load_calc.tenum import EStory, EStructure, EInsidePressure, EInfiltrationMethod, ECValueEstimateMethod
from heat_load_calc.building import Building, AirTightnessBalanceResidential
from heat_load_calc.input_models.input_building import InputBuilding
from heat_load_calc.input_models.input_infiltration import InputInfiltration


def test_air_tightness_values():
    
    bdg = Building.create_building(
        ipt_building=InputBuilding(
            d_infiltration=None,
            ipt_infiltration=InputInfiltration(
                method=EInfiltrationMethod.BALANCE_RESIDENTIAL,
                story=EStory.ONE,
                c_value_estimate=ECValueEstimateMethod.SPECIFY,
                c_value=1.0,
                ua_value=None,
                struct=None,
                inside_pressure=EInsidePressure.NEGATIVE
            )
        )
    )

    air_tightness: AirTightnessBalanceResidential = bdg._air_tightness

    assert air_tightness._story == EStory.ONE
    assert air_tightness._c == 1.0
    assert air_tightness._inside_pressure == EInsidePressure.NEGATIVE    


def test_calculate_c_value():

    def make_air_tightness(struct: str):

        bdg = Building.create_building(
            ipt_building=InputBuilding(
                d_infiltration=None,
                ipt_infiltration=InputInfiltration(
                    method=EInfiltrationMethod.BALANCE_RESIDENTIAL,
                    story=EStory.ONE,
                    c_value_estimate=ECValueEstimateMethod.CALCULATE,
                    c_value=None,
                    ua_value=1.0,
                    struct=EStructure(struct),
                    inside_pressure=EInsidePressure.NEGATIVE
                )
            )            
        )

        air_tightness: AirTightnessBalanceResidential = bdg._air_tightness

        return air_tightness
    
    at_rc = make_air_tightness(struct='rc')

    assert at_rc._c == 4.16

    at_src = make_air_tightness(struct='src')

    assert at_src._c == 4.16

    at_wood = make_air_tightness(struct='wooden')
    
    assert at_wood._c == 8.28

    at_steel = make_air_tightness(struct='steel')

    assert at_steel._c == 8.28


def test_specify_c_value():

    bdg = Building.create_building(
        ipt_building=InputBuilding(
            d_infiltration=None,
            ipt_infiltration=InputInfiltration(
                method=EInfiltrationMethod.BALANCE_RESIDENTIAL,
                story=EStory.ONE,
                c_value_estimate=ECValueEstimateMethod.SPECIFY,
                c_value=0.2,
                ua_value=None,
                struct=None,
                inside_pressure=EInsidePressure.NEGATIVE
            )
        )            
    )

    air_tightness: AirTightnessBalanceResidential = bdg._air_tightness

    assert air_tightness._c == 0.2


def test_air_leakage():

    def make_bdg(story: float, inside_pressure: str):

        return Building.create_building(
            ipt_building=InputBuilding(
                d_infiltration=None,
                ipt_infiltration=InputInfiltration(
                    method=EInfiltrationMethod.BALANCE_RESIDENTIAL,
                    story=EStory(story),
                    c_value_estimate=ECValueEstimateMethod.SPECIFY,
                    c_value=0.2,
                    ua_value=None,
                    struct=None,
                    inside_pressure=EInsidePressure(inside_pressure)
                )
            )
        )
    
    # make Building class

    bdg_1_negative = make_bdg(story=1, inside_pressure='negative')
    bdg_1_positive = make_bdg(story=1, inside_pressure='positive')
    bdg_1_balanced = make_bdg(story=1, inside_pressure='balanced')
    bdg_2_negative = make_bdg(story=2, inside_pressure='negative')
    bdg_2_positive = make_bdg(story=2, inside_pressure='positive')
    bdg_2_balanced = make_bdg(story=2, inside_pressure='balanced')

    # calculate v_leak

    theta_r_is_n = np.array([20.0, 30.0]).reshape(-1, 1)
    theta_o_n = 0.0
    v_r_is=np.array([40.0, 60.0]).reshape(-1, 1)
    v_leak_1_is_n_negative = bdg_1_negative.get_v_leak_is_n(theta_r_is_n=theta_r_is_n, theta_o_n=theta_o_n, v_r_is=v_r_is)
    v_leak_is_n_1_positive = bdg_1_positive.get_v_leak_is_n(theta_r_is_n=theta_r_is_n, theta_o_n=theta_o_n, v_r_is=v_r_is)
    v_leak_is_n_1_balanced = bdg_1_balanced.get_v_leak_is_n(theta_r_is_n=theta_r_is_n, theta_o_n=theta_o_n, v_r_is=v_r_is)
    v_leak_is_n_2_negative = bdg_2_negative.get_v_leak_is_n(theta_r_is_n=theta_r_is_n, theta_o_n=theta_o_n, v_r_is=v_r_is)
    v_leak_is_n_2_positive = bdg_2_positive.get_v_leak_is_n(theta_r_is_n=theta_r_is_n, theta_o_n=theta_o_n, v_r_is=v_r_is)
    v_leak_is_n_2_balanced = bdg_2_balanced.get_v_leak_is_n(theta_r_is_n=theta_r_is_n, theta_o_n=theta_o_n, v_r_is=v_r_is)

    n_leak_1_negative = max(0.022 * 0.2 * math.sqrt(26.0) - 0.28, 0.0)
    n_leak_1_positive = max(0.022 * 0.2 * math.sqrt(26.0) - 0.26, 0.0)
    n_leak_1_balanced = max(0.022 * 0.2 * math.sqrt(26.0), 0.0)
    n_leak_2_negative = max(0.020 * 0.2 * math.sqrt(26.0) - 0.13, 0.0)
    n_leak_2_positive = max(0.020 * 0.2 * math.sqrt(26.0) - 0.14, 0.0)
    n_leak_2_balanced = max(0.020 * 0.2 * math.sqrt(26.0), 0.0)

    assert v_leak_1_is_n_negative[0] == n_leak_1_negative * 40.0 / 3600
    assert v_leak_1_is_n_negative[1] == n_leak_1_negative * 60.0 / 3600

    assert v_leak_is_n_1_positive[0] == n_leak_1_positive * 40.0 / 3600
    assert v_leak_is_n_1_positive[1] == n_leak_1_positive * 60.0 / 3600

    assert v_leak_is_n_1_balanced[0] == n_leak_1_balanced * 40.0 / 3600
    assert v_leak_is_n_1_balanced[1] == n_leak_1_balanced * 60.0 / 3600

    assert v_leak_is_n_2_negative[0] == n_leak_2_negative * 40.0 / 3600
    assert v_leak_is_n_2_negative[1] == n_leak_2_negative * 60.0 / 3600

    assert v_leak_is_n_2_positive[0] == n_leak_2_positive * 40.0 / 3600
    assert v_leak_is_n_2_positive[1] == n_leak_2_positive * 60.0 / 3600

    assert v_leak_is_n_2_balanced[0] == pytest.approx(n_leak_2_balanced * 40.0 / 3600)
    assert v_leak_is_n_2_balanced[1] == pytest.approx(n_leak_2_balanced * 60.0 / 3600)

