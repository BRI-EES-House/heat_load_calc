import unittest
import json
import os
from typing import Dict
import numpy as np

from heat_load_calc.equipments import Equipments
from heat_load_calc.weather import Weather
from heat_load_calc.interval import Interval
from heat_load_calc.boundaries import Boundaries
from heat_load_calc.shape_factor import ShapeFactorMethod


class TestEquipments(unittest.TestCase):

    def test_heating_equipments_not_exist_error(self):
        d = {
            "cooling_equipments": []
        }

        with self.assertRaises(KeyError):
            Equipments(d=d, n_rm=None, n_b=None, bs=None, id_r_is=None)
    
    def test_cooling_equipments_not_exist_error(self):
        d = {
            "heating_equipments": []
        }

        with self.assertRaises(KeyError):
            Equipments(d=d, n_rm=None, n_b=None, bs=None, id_r_is=None)

    def test_(self):

        d = {
            "heating_equipments":[
                {
                    "equipment_type": "rac",
                    "id": 1,
                    "name": "rac_1",
                    "property": {
                        "space_id": 4,
                        "q_min": 200,
                        "q_max": 4000,
                        "v_min": 10,
                        "v_max": 30,
                        "bf": 0.2
                    }
                },
                {
                    "equipment_type": "floor_heating",
                    "id": 2,
                    "name": "floor_heating_1",
                    "property": {
                        "boundary_id": 9,
                        "max_capacity": 40,
                        "area": 8.0,
                        "convection_ratio": 0.1
                    }
                }
            ],
            "cooling_equipments":[
                {
                    "equipment_type": "rac",
                    "id": 1,
                    "name": "rac_1",
                    "property": {
                        "space_id": 4,
                        "q_min": 200,
                        "q_max": 4000,
                        "v_min": 10,
                        "v_max": 30,
                        "bf": 0.2
                    }
                },
                {
                    "equipment_type": "floor_cooling",
                    "id": 2,
                    "name": "floor_cooling_1",
                    "property": {
                        "boundary_id": 9,
                        "max_capacity": 40,
                        "area": 8.0,
                        "convection_ratio": 0.1
                    }
                }
            ]
        }

        d_input = _read_input_file()

        w = _get_weather_class()

        id_r_is = np.array([2, 4]).reshape(-1, 1)

        bs = Boundaries(id_r_is=id_r_is, ds=d_input['boundaries'], w=w, rad_method=ShapeFactorMethod.NAGATA)

        e = Equipments(d=d, n_rm=_get_n_rm(), n_b=bs.n_b, bs=bs, id_r_is=id_r_is)

        np.testing.assert_equal(np.array([True, False]).reshape(-1, 1), e.is_radiative_heating_is)

        np.testing.assert_equal(np.array([True, False]).reshape(-1, 1), e.is_radiative_cooling_is)


def _get_n_rm():

    return 2


def _read_input_file() -> Dict:

    # directory of input file
    s_folder = os.path.dirname(__file__)

    # read jason file
    data_path = os.path.join(s_folder, "test_boundaries_input_file.json")
    with open(data_path, 'r', encoding='utf-8') as js:
        d = json.load(js)
    
    return d


def _get_weather_class():

    itv = Interval.M15
    n = itv.get_n_step_annual()

    a_sun_ns = np.zeros(n, dtype=float)    
    a_sun_ns[:7] = np.array([0.0, np.pi/6, np.pi/3, np.pi/2, np.pi*2/3, np.pi*5/6, np.pi])
    h_sun_ns = np.zeros(n, dtype=float)
    h_sun_ns[:7] = np.array([0.0, np.pi/6, np.pi/3, np.pi/2, np.pi/3, np.pi/6, 0.0])
    i_dn_ns = np.zeros(n, dtype=float)
    i_dn_ns[:7] = np.array([10.0, 100.0, 200.0, 300.0, 200.0, 100.0, 10.0])
    i_sky_ns = np.zeros(n, dtype=float)
    i_sky_ns[:7] = np.array([10.0, 100.0, 200.0, 300.0, 200.0, 100.0, 10.0])
    r_n_ns = np.zeros(n, dtype=float)
    r_n_ns[:7] = np.array([20.0, 19.0, 18.0, 17.0, 18.0, 19.0, 20.0])
    theta_o_ns = np.zeros(n, dtype=float)
    theta_o_ns[:7] = np.array([-15.0, -12.0, 3.0, 5.0, 4.0, -3.0, -7.0])
    x_o_ns = np.zeros(n, dtype=float)
    x_o_ns[:7] = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    w = Weather(a_sun_ns=a_sun_ns, h_sun_ns=h_sun_ns, i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, r_n_ns=r_n_ns, theta_o_ns=theta_o_ns, x_o_ns=x_o_ns)

    return w
