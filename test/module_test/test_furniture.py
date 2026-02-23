import pytest

from heat_load_calc import furniture
from heat_load_calc.input_models.input_furniture import InputFurniture, InputFurnitureDefault, InputFurnitureSpecify


def test_use_default_value():

    ipt = InputFurnitureDefault(
        solar_absorption_ratio=0.5
    )

    c_lh_frt_i, c_sh_frt_i, g_lh_frt_i, g_sh_frt_i, r_sol_frt = furniture.get_furniture_specs(
        input_furniture=ipt,
        v_r_i=100.0
    )

    assert c_sh_frt_i == pytest.approx(1260000.0)
    assert g_sh_frt_i == pytest.approx(1260000 * 0.00022)
    assert c_lh_frt_i == pytest.approx(1680)
    assert g_lh_frt_i == pytest.approx(1680*0.0018)
    assert r_sol_frt == 0.5


def test_use_specified_value():

    ipt = InputFurnitureSpecify(
        solar_absorption_ratio=0.3,
        heat_capacity=1260000.0,
        heat_cond=1260000.0 * 0.00022,
        moisture_capacity=1680.0,
        moisture_cond=1680.0 * 0.0018
    )

    c_lh_frt_i, c_sh_frt_i, g_lh_frt_i, g_sh_frt_i, r_sol_frt = furniture.get_furniture_specs(
        input_furniture=ipt,
        v_r_i=100.0
    )

    assert c_sh_frt_i == 1260000.0
    assert g_sh_frt_i == 1260000.0 * 0.00022
    assert c_lh_frt_i == 1680.0
    assert g_lh_frt_i == 1680.0 * 0.0018
    assert r_sol_frt == 0.3
