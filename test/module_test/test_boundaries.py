import os
import json
import unittest
import numpy as np
from typing import Dict

from heat_load_calc import boundaries
from heat_load_calc.boundaries import Boundaries
from heat_load_calc.boundaries import BoundaryType
from heat_load_calc.interval import Interval
from heat_load_calc.weather import Weather
from heat_load_calc import shape_factor
from heat_load_calc.shape_factor import ShapeFactorMethod


class TestBoundaries(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        d = _read_input_file()

        w = _get_weather_class()

        id_r_is = np.array([2,4]).reshape(-1, 1)

        bs = Boundaries(id_r_is=id_r_is, ds=d['boundaries'], w=w, rad_method=ShapeFactorMethod.NAGATA)

        cls._bs: Boundaries = bs

    def test_get_p_is_js_ptn0(self):

        result = boundaries._get_p_is_js(
            id_r_is=np.array([0,1,2]).reshape(-1, 1),
            connected_room_id_js=np.array([0,0,0,1,1,1,1,2,2,2]).reshape(-1, 1)
        )

        self.assertEqual(result.ndim, 2)
        self.assertEqual(result.shape[0], 3)
        self.assertEqual(result.shape[1], 10)

        self.assertEqual(result[0][0], 1)
        self.assertEqual(result[0][1], 1)
        self.assertEqual(result[0][2], 1)
        self.assertEqual(result[0][3], 0)
        self.assertEqual(result[0][4], 0)
        self.assertEqual(result[0][5], 0)
        self.assertEqual(result[0][6], 0)
        self.assertEqual(result[0][7], 0)
        self.assertEqual(result[0][8], 0)
        self.assertEqual(result[0][9], 0)
        self.assertEqual(result[1][0], 0)
        self.assertEqual(result[1][1], 0)
        self.assertEqual(result[1][2], 0)
        self.assertEqual(result[1][3], 1)
        self.assertEqual(result[1][4], 1)
        self.assertEqual(result[1][5], 1)
        self.assertEqual(result[1][6], 1)
        self.assertEqual(result[1][7], 0)
        self.assertEqual(result[1][8], 0)
        self.assertEqual(result[1][9], 0)
        self.assertEqual(result[2][0], 0)
        self.assertEqual(result[2][1], 0)
        self.assertEqual(result[2][2], 0)
        self.assertEqual(result[2][3], 0)
        self.assertEqual(result[2][4], 0)
        self.assertEqual(result[2][5], 0)
        self.assertEqual(result[2][6], 0)
        self.assertEqual(result[2][7], 1)
        self.assertEqual(result[2][8], 1)
        self.assertEqual(result[2][9], 1)

    def test_get_p_is_js_ptn1(self):

        result = boundaries._get_p_is_js(
            id_r_is=np.array([3,7,5]).reshape(-1, 1),
            connected_room_id_js=np.array([3,3,3,7,7,7,7,5,5,5]).reshape(-1, 1)
        )

        self.assertEqual(result.ndim, 2)
        self.assertEqual(result.shape[0], 3)
        self.assertEqual(result.shape[1], 10)

        self.assertEqual(result[0][0], 1)
        self.assertEqual(result[0][1], 1)
        self.assertEqual(result[0][2], 1)
        self.assertEqual(result[0][3], 0)
        self.assertEqual(result[0][4], 0)
        self.assertEqual(result[0][5], 0)
        self.assertEqual(result[0][6], 0)
        self.assertEqual(result[0][7], 0)
        self.assertEqual(result[0][8], 0)
        self.assertEqual(result[0][9], 0)
        self.assertEqual(result[1][0], 0)
        self.assertEqual(result[1][1], 0)
        self.assertEqual(result[1][2], 0)
        self.assertEqual(result[1][3], 1)
        self.assertEqual(result[1][4], 1)
        self.assertEqual(result[1][5], 1)
        self.assertEqual(result[1][6], 1)
        self.assertEqual(result[1][7], 0)
        self.assertEqual(result[1][8], 0)
        self.assertEqual(result[1][9], 0)
        self.assertEqual(result[2][0], 0)
        self.assertEqual(result[2][1], 0)
        self.assertEqual(result[2][2], 0)
        self.assertEqual(result[2][3], 0)
        self.assertEqual(result[2][4], 0)
        self.assertEqual(result[2][5], 0)
        self.assertEqual(result[2][6], 0)
        self.assertEqual(result[2][7], 1)
        self.assertEqual(result[2][8], 1)
        self.assertEqual(result[2][9], 1)

    def test_get_p_is_js_ptn2(self):
        """指定された room id が無い場合にエラーを発生させる。
        """

        with self.assertRaises(ValueError):
            result = boundaries._get_p_is_js(
                id_r_is=np.array([3,7,5]).reshape(-1,1),
                connected_room_id_js=np.array([0,3,3,7,7,7,7,5,5,5]).reshape(-1, 1)
            )

    def test_n_b(self):

        # number of boundaries        
        self.assertEqual(14, self._bs.n_b)
    
    def test_n_ground(self):

        # number of grounds
        self.assertEqual(0, self._bs.n_ground)

    def test_id(self):

        # id
        np.testing.assert_array_equal(_get_id_js(), self._bs.id_js)

    def test_name(self):

        # name
        np.testing.assert_array_equal(
            np.array([
                "s_wall_1F_room",
                "w_wall_1F_room",
                "e_wall_1F_room",
                "n_wall_1F_room",
                "floor_1F_room",
                "s_wall_2F_room",
                "w_wall_2F_room",
                "e_wall_2F_room",
                "n_wall_2F_room",
                "roof_2F_room",
                "south_window_1F_room",
                "south_window_2F_room",
                "internal_1",
                "internal_2"
            ]).reshape(-1, 1),
            self._bs.name_js
        )
    
    def test_sub_name(self):

        # sub name
        np.testing.assert_array_equal(
            np.full(shape=(14,1), fill_value="", dtype=str),
            self._bs.sub_name_js
        )
    
    def test_connected_room_id(self):

        # connected room id
        np.testing.assert_equal(
            np.array([2,2,2,2,2,4,4,4,4,4,2,4,2,4]).reshape(-1, 1),
            self._bs.connected_room_id_js
        )
    
    def test_p_is_js(self):

        # matrix of relationship between rooms and boundaries
        np.testing.assert_equal(_get_p_is_js(), self._bs.p_is_js)

    def test_p_js_is(self):

        # matrix of relationship between rooms and boundaries
        np.testing.assert_equal(
            np.array([
                [1,0],
                [1,0],
                [1,0],
                [1,0],
                [1,0],
                [0,1],
                [0,1],
                [0,1],
                [0,1],
                [0,1],
                [1,0],
                [0,1],
                [1,0],
                [0,1]
            ]),
            self._bs.p_js_is
        )
    
    def test_b_floor(self):

        # is boundary floor ?
        np.testing.assert_equal(
            np.array([False, False, False, False, True, False, False, False, False, False, False, False, False, True]).reshape(-1, 1),
            self._bs.b_floor_js
        )

    def test_b_ground(self):

        # is boundary ground?
        np.testing.assert_equal(
            np.full(shape=(14,1), fill_value=False),
            self._bs.b_ground_js
        )

    def test_k_ei(self):

        # effect of equivalent room temperature of other boundary surface to rear temperature of given boundary
        np.testing.assert_equal(
            np.array([
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]
            ]),
            self._bs.k_ei_js_js
        )
    
    def test_k_eo(self):
        
        # effect of outdoor temperature to the rear surface temperature of given boundary (temperature difference coefficient)
        np.testing.assert_equal(
            np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0]).reshape(-1, 1),
            self._bs.k_eo_js
        )

    def test_k_s_r(self):

        # coefficient of effects of room temperature to rear surface temperature of boundary
        np.testing.assert_equal(
            np.array([
                [0, 0],
                [0, 0],
                [0, 0],
                [0, 0],
                [0, 0],
                [0, 0],
                [0, 0],
                [0, 0],
                [0, 0],
                [0, 0],
                [0, 0],
                [0, 0],
                [0, 0],
                [0, 0]
            ]),
            self._bs.k_s_r_js_is
        )

    def test_b_s_sol_abs(self):

        # is inside solar radiationn absorbed of boundary
        np.testing.assert_equal(
            np.array([False, False, False, False, True, False, False, False, False, False, False, False, False, True]).reshape(-1, 1),
            self._bs.b_s_sol_abs_js
        )
    
    def test_h_s_r(self):

        # radiative heat transfer coefficient of inside surface of boundary, W/m2K
        np.testing.assert_equal(_get_h_s_r_js(), self._bs.h_s_r_js)
    
    def test_h_s_c(self):

        # convective heat transfer coefficient of inside surface of boundary, W/m2K
        np.testing.assert_equal(_get_h_s_c_js(), self._bs.h_s_c_js)
    
    def test_u(self):

        h_s_c_js = _get_h_s_c_js()
        h_s_r_js = _get_h_s_r_js()
        h_s_c_rear_js = np.array([None, None, None, None, None, None, None, None, None, None, None, None, h_s_c_js[13,0], h_s_c_js[12,0]])
        h_s_r_rear_js = np.array([None, None, None, None, None, None, None, None, None, None, None, None, h_s_r_js[13,0], h_s_r_js[12,0]])

        t_b_js = np.array([
            BoundaryType.EXTERNAL_GENERAL_PART,
            BoundaryType.EXTERNAL_GENERAL_PART,
            BoundaryType.EXTERNAL_GENERAL_PART,
            BoundaryType.EXTERNAL_GENERAL_PART,
            BoundaryType.EXTERNAL_GENERAL_PART,
            BoundaryType.EXTERNAL_GENERAL_PART,
            BoundaryType.EXTERNAL_GENERAL_PART,
            BoundaryType.EXTERNAL_GENERAL_PART,
            BoundaryType.EXTERNAL_GENERAL_PART,
            BoundaryType.EXTERNAL_GENERAL_PART,
            BoundaryType.EXTERNAL_TRANSPARENT_PART,
            BoundaryType.EXTERNAL_TRANSPARENT_PART,
            BoundaryType.INTERNAL,
            BoundaryType.INTERNAL
        ])
        id_js = _get_id_js().flatten()
        r_s_o_js = np.array([0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, None, None])
        u_w_std_js = np.array([None, None, None, None, None, None, None, None, None, None, 4.65, 4.65, None, None])
        ds = _read_input_file()
        rfs = [
            boundaries._get_response_factor(d=d, h_s_c_rear_j=h_s_c_rear_j, h_s_r_rear_j=h_s_r_rear_j, id_j=id_j, t_b_j=t_b_j, r_s_o_j=r_s_o_j, u_w_std_j=u_w_std_j)
            for (d, h_s_c_rear_j, h_s_r_rear_j, id_j, t_b_j, r_s_o_j, u_w_std_j)
            in zip(ds['boundaries'], h_s_c_rear_js, h_s_r_rear_js, id_js, t_b_js, r_s_o_js, u_w_std_js)
        ]

        r_total_js = np.array([rf.r_total for rf in rfs]).reshape(-1, 1)

        u_js = 1.0 / (1.0 / (h_s_c_js + h_s_r_js) + r_total_js)
         
        np.testing.assert_equal(u_js, self._bs.u_js)
    
    def test_a_s_js(self):

        # surface area of boundary, m2
        np.testing.assert_equal(_get_a_s_js(), self._bs.a_s_js)

    def test_eps_r_i(self):

        # long wave emissivity of internal surface of boundary, -
        np.testing.assert_equal(_get_eps_r_i_js(), self._bs.eps_r_i_js)



def _get_id_js():
    """[J, 1]"""

    return np.array([1,3,5,7,9,11,13,15,17,19,21,23,25,27]).reshape(-1, 1)


def _get_p_is_js():
    """[I, J]"""
    
    return np.array([
        [1,1,1,1,1,0,0,0,0,0,1,0,1,0],
        [0,0,0,0,0,1,1,1,1,1,0,1,0,1]
    ])


def _get_h_s_r_js():
    """[J, 1]"""

    a_s_js = _get_a_s_js()

    p_is_js = _get_p_is_js()

    eps_r_i_js = _get_eps_r_i_js()

    method = ShapeFactorMethod.NAGATA

    return shape_factor.get_h_s_r_js(a_s_js=a_s_js, p_is_js=p_is_js, eps_r_i_js=eps_r_i_js, method=method)


def _get_eps_r_i_js():
    """[J, 1]"""

    return np.full(shape=(14,1), fill_value=0.9)


def _get_a_s_js():
    """[J, 1]"""

    return np.array([0.5, 1.0, 1.0, 1.0, 1.0, 0.5, 1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 1.0, 1.0]).reshape(-1, 1)


def _get_h_s_c_js():
    """[J, 1]"""

    return np.full(shape=(14,1), fill_value=2.5)


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


def _read_input_file() -> Dict:

    # directory of input file
    s_folder = os.path.dirname(__file__)

    # read jason file
    data_path = os.path.join(s_folder, "test_boundaries_input_file.json")
    with open(data_path, 'r', encoding='utf-8') as js:
        d = json.load(js)
    
    return d
