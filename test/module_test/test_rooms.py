import pytest
import numpy as np

from heat_load_calc.rooms import Rooms
from heat_load_calc.input_models.input_room import InputRoom
from heat_load_calc.input_models.input_furniture import InputFurniture, InputFurnitureDefault, InputFurnitureSpecify


def make_rooms():

    return [
        InputRoom(
            id=0,
            name='test0',
            sub_name='sub_test0',
            a_f=30.0,
            v=70.0,
            ipt_furniture=InputFurnitureDefault(solar_absorption_ratio=0.5),
            v_vent_ntr_set=350.0,
            met=1.0,
            ipt_schedule_data=None
        ),
        InputRoom(
            id=1,
            name='test1',
            sub_name='sub_test1',
            a_f=40.0,
            v=130.0,
            ipt_furniture=InputFurnitureDefault(solar_absorption_ratio=0.3),
            v_vent_ntr_set=620.0,
            met=2.0,
            ipt_schedule_data=None
        ),
    ]

def test_rooms_furniture_default():

    rms = Rooms(ipt_rooms=make_rooms())

    assert rms.n_r == 2

    np.testing.assert_array_equal(rms.id_r_is, np.array([[0], [1]]))
    np.testing.assert_array_equal(rms.name_r_is, np.array([['test0'], ['test1']]))
    np.testing.assert_array_equal(rms.sub_name_r_is, np.array([['sub_test0'], ['sub_test1']]))
    np.testing.assert_array_equal(rms.a_f_r_is, np.array([[30.0], [40.0]]))
    np.testing.assert_array_equal(rms.v_r_is, np.array([[70.0], [130.0]]))
    np.testing.assert_array_almost_equal(rms.c_sh_frt_is, np.array([[882000.0], [1638000.0]]))
    np.testing.assert_array_almost_equal(rms.g_sh_frt_is, np.array([[194.04], [360.36]]))
    np.testing.assert_array_almost_equal(rms.c_lh_frt_is, np.array([[1176.0], [2184.0]]))
    np.testing.assert_array_almost_equal(rms.g_lh_frt_is, np.array([[2.1168], [3.9312]]))
    np.testing.assert_array_almost_equal(rms.v_vent_ntr_set_is, np.array([[350.0], [620.0]])/3600.0)
    np.testing.assert_array_equal(rms.met_is, np.array([[1.0], [2.0]]))
    np.testing.assert_array_equal(rms.r_sol_frt_is, np.array([[0.5], [0.3]]))


def test_rooms_furniture_specify():

    rms = Rooms(ipt_rooms=make_rooms())

    np.testing.assert_array_equal(rms.id_r_is, np.array([[0], [1]]))
    np.testing.assert_array_equal(rms.name_r_is, np.array([['test0'], ['test1']]))
    np.testing.assert_array_equal(rms.sub_name_r_is, np.array([['sub_test0'], ['sub_test1']]))
    np.testing.assert_array_equal(rms.a_f_r_is, np.array([[30.0], [40.0]]))
    np.testing.assert_array_equal(rms.v_r_is, np.array([[70.0], [130.0]]))
    np.testing.assert_array_almost_equal(rms.c_sh_frt_is, np.array([[882000.0], [1638000.0]]))
    np.testing.assert_array_almost_equal(rms.g_sh_frt_is, np.array([[194.04], [360.36]]))
    np.testing.assert_array_almost_equal(rms.c_lh_frt_is, np.array([[1176.0], [2184.0]]))
    np.testing.assert_array_almost_equal(rms.g_lh_frt_is, np.array([[2.1168], [3.9312]]))
    np.testing.assert_array_almost_equal(rms.v_vent_ntr_set_is, np.array([[350.0], [620.0]])/3600.0)
    np.testing.assert_array_equal(rms.met_is, np.array([[1.0], [2.0]]))
    np.testing.assert_array_equal(rms.r_sol_frt_is, np.array([[0.5], [0.3]]))
