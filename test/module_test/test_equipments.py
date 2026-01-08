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
            Equipments(d=d, n_rm=None, n_b=None, id_r_is=None, id_js=None, connected_room_id_js=None)
    
    def test_cooling_equipments_not_exist_error(self):
        d = {
            "heating_equipments": []
        }

        with self.assertRaises(KeyError):
            Equipments(d=d, n_rm=None, n_b=None, id_r_is=None, id_js=None, connected_room_id_js=None)

    def test_radiative_heating_equipments_duplicated_error(self):

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
                },
                {
                    "equipment_type": "floor_heating",
                    "id": 3,
                    "name": "floor_heating_2",
                    "property": {
                        "boundary_id": 7,
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

        id_r_is = np.array([2, 4]).reshape(-1, 1)

        n_b = 14
        id_js = np.array([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27]).reshape(-1, 1)
        connected_room_id_js = np.array([2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 2, 4, 2, 4]).reshape(-1, 1)

        with self.assertRaises(Exception):
            Equipments(d=d, n_rm=_get_n_rm(), n_b=n_b, id_r_is=id_r_is, id_js=id_js, connected_room_id_js=connected_room_id_js)

    def test_radiative_heating_equipments_duplicated_error(self):

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
                },
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
                },
                {
                    "equipment_type": "floor_cooling",
                    "id": 3,
                    "name": "floor_cooling_2",
                    "property": {
                        "boundary_id": 7,
                        "max_capacity": 40,
                        "area": 8.0,
                        "convection_ratio": 0.1
                    }
                }
            ]
        }

        id_r_is = np.array([2, 4]).reshape(-1, 1)

        n_b = 14
        id_js = np.array([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27]).reshape(-1, 1)
        connected_room_id_js = np.array([2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 2, 4, 2, 4]).reshape(-1, 1)

        with self.assertRaises(Exception):
            Equipments(d=d, n_rm=_get_n_rm(), n_b=n_b, id_r_is=id_r_is, id_js=id_js, connected_room_id_js=connected_room_id_js)

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

        id_r_is = np.array([2, 4]).reshape(-1, 1)

        n_b = 14
        id_js = np.array([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27]).reshape(-1, 1)
        connected_room_id_js = np.array([2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 2, 4, 2, 4]).reshape(-1, 1)


        e = Equipments(d=d, n_rm=_get_n_rm(), n_b=n_b, id_r_is=id_r_is, id_js=id_js, connected_room_id_js=connected_room_id_js)

        np.testing.assert_equal(np.array([True, False]).reshape(-1, 1), e.is_radiative_heating_is)

        np.testing.assert_equal(np.array([True, False]).reshape(-1, 1), e.is_radiative_cooling_is)

        np.testing.assert_equal(np.array([320.0, 0.0]).reshape(-1, 1), e.q_rs_h_max_is)

        np.testing.assert_equal(np.array([320.0, 0.0]).reshape(-1, 1), e.q_rs_c_max_is)

        np.testing.assert_equal(np.array([0.1, 0.0]).reshape(-1, 1), e.beta_h_is)

        np.testing.assert_equal(np.array([0.1, 0.0]).reshape(-1, 1), e.beta_c_is)


def _get_n_rm():

    return 2

