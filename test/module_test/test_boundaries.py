import unittest
import numpy as np

from heat_load_calc import boundaries
from heat_load_calc.boundaries import Boundaries
from heat_load_calc.interval import Interval
from heat_load_calc.weather import Weather


class TestBoundaries(unittest.TestCase):

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

    def test_get_p_is_js_ptn0(self):

        result = boundaries._get_p_is_js(
            id_r_is=np.array([0,1,2]),
            connected_room_id_js=np.array([0,0,0,1,1,1,1,2,2,2])
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
            id_r_is=np.array([3,7,5]),
            connected_room_id_js=np.array([3,3,3,7,7,7,7,5,5,5])
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
                id_r_is=np.array([3,7,5]),
                connected_room_id_js=np.array([0,3,3,7,7,7,7,5,5,5])
            )
        

    def test_id(self):

        ds = _get_boundary_dict()

        bs = Boundaries(id_r_is=np.array([0,1,2]), ds=ds, w=self.w)
        
        self.assertAlmostEqual(0.0, 0.0)


def _get_boundary_dict():

    return [
            {
                "id": 0,
                "name": "north_exterior_wall",
                "sub_name": "",
                "connected_room_id": 0,
                "boundary_type": "external_general_part",
                "area": 4.9775,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0432,
                            "thermal_capacity": 7.885
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 1.28,
                            "thermal_capacity": 0.512
                        },
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        },
                        {
                            "name": "wood-wool_and_flake_boards",
                            "thermal_resistance": 0.0882,
                            "thermal_capacity": 25.1789
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "n",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 1,
                "name": "north_exterior_door",
                "sub_name": "",
                "connected_room_id": 0,
                "boundary_type": "external_opaque_part",
                "area": 1.62,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "n",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "u_value": 4.65,
                "inside_heat_transfer_resistance": 0.11,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 2,
                "name": "east_exterior_wall",
                "sub_name": "",
                "connected_room_id": 0,
                "boundary_type": "external_general_part",
                "area": 17.982,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0432,
                            "thermal_capacity": 7.885
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 1.28,
                            "thermal_capacity": 0.512
                        },
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        },
                        {
                            "name": "wood-wool_and_flake_boards",
                            "thermal_resistance": 0.0882,
                            "thermal_capacity": 25.1789
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "e",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 3,
                "name": "east_exterior_window",
                "sub_name": "",
                "connected_room_id": 0,
                "boundary_type": "external_transparent_part",
                "area": 3.13,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "e",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "u_value": 4.65,
                "inside_heat_transfer_resistance": 0.11,
                "eta_value": 0.792,
                "incident_angle_characteristics": "multiple",
                "glass_area_ratio": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 4,
                "name": "south_exterior_wall",
                "sub_name": "",
                "connected_room_id": 0,
                "boundary_type": "external_general_part",
                "area": 10.2135,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0432,
                            "thermal_capacity": 7.885
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 1.28,
                            "thermal_capacity": 0.512
                        },
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        },
                        {
                            "name": "wood-wool_and_flake_boards",
                            "thermal_resistance": 0.0882,
                            "thermal_capacity": 25.1789
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "s",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 5,
                "name": "south_exterior_window",
                "sub_name": "",
                "connected_room_id": 0,
                "boundary_type": "external_transparent_part",
                "area": 6.94,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "solar_shading_part": {
                    "existence": True,
                    "input_method": "simple",
                    "depth": 0.91,
                    "d_h": 2.1,
                    "d_e": 0.48
                },
                "is_sun_striked_outside": True,
                "direction": "s",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "u_value": 4.65,
                "inside_heat_transfer_resistance": 0.11,
                "eta_value": 0.792,
                "incident_angle_characteristics": "multiple",
                "glass_area_ratio": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 6,
                "name": "exterior_floor",
                "sub_name": "",
                "connected_room_id": 0,
                "boundary_type": "external_general_part",
                "area": 29.81,
                "h_c": 0.7,
                "is_solar_absorbed_inside": True,
                "is_floor": True,
                "layers": [
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 1.28,
                            "thermal_capacity": 0.512
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": False,
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.15,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 0.7
            },
            {
                "id": 7,
                "name": "exterior_ceiling",
                "sub_name": "",
                "connected_room_id": 0,
                "boundary_type": "external_general_part",
                "area": 4.14,
                "h_c": 5.0,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0432,
                            "thermal_capacity": 7.885
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 3.42,
                            "thermal_capacity": 1.368
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "top",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.09,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 8,
                "name": "internal_wall_non_occupant",
                "sub_name": "",
                "connected_room_id": 0,
                "boundary_type": "internal",
                "area": 21.6125,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "outside_heat_transfer_resistance": 0.11,
                "rear_surface_boundary_id": 45
            },
            {
                "id": 9,
                "name": "internal_ceiling_other_occupant",
                "sub_name": "",
                "connected_room_id": 0,
                "boundary_type": "internal",
                "area": 10.77,
                "h_c": 5.0,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.07,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "outside_heat_transfer_resistance": 0.15,
                "rear_surface_boundary_id": 22
            },
            {
                "id": 10,
                "name": "internal_ceiling_other_occupant",
                "sub_name": "",
                "connected_room_id": 0,
                "boundary_type": "internal",
                "area": 10.77,
                "h_c": 5.0,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.07,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "outside_heat_transfer_resistance": 0.15,
                "rear_surface_boundary_id": 29
            },
            {
                "id": 11,
                "name": "internal_wall_other_occupant",
                "sub_name": "",
                "connected_room_id": 0,
                "boundary_type": "internal",
                "area": 8.736,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "outside_heat_transfer_resistance": 0.11,
                "rear_surface_boundary_id": 37
            },
            {
                "id": 12,
                "name": "south_exterior_wall",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "external_general_part",
                "area": 8.098,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0432,
                            "thermal_capacity": 7.885
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 1.28,
                            "thermal_capacity": 0.512
                        },
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        },
                        {
                            "name": "wood-wool_and_flake_boards",
                            "thermal_resistance": 0.0882,
                            "thermal_capacity": 25.1789
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "s",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 13,
                "name": "south_exterior_window",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "external_transparent_part",
                "area": 1.73,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "solar_shading_part": {
                    "existence": True,
                    "input_method": "simple",
                    "depth": 0.65,
                    "d_h": 1.05,
                    "d_e": 0.5125
                },
                "is_sun_striked_outside": True,
                "direction": "s",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "u_value": 4.65,
                "inside_heat_transfer_resistance": 0.11,
                "eta_value": 0.792,
                "incident_angle_characteristics": "multiple",
                "glass_area_ratio": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 14,
                "name": "west_exterior_wall",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "external_general_part",
                "area": 8.838,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0432,
                            "thermal_capacity": 7.885
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 1.28,
                            "thermal_capacity": 0.512
                        },
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        },
                        {
                            "name": "wood-wool_and_flake_boards",
                            "thermal_resistance": 0.0882,
                            "thermal_capacity": 25.1789
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "w",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 15,
                "name": "west_exterior_window",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "external_transparent_part",
                "area": 0.99,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "w",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "u_value": 4.65,
                "inside_heat_transfer_resistance": 0.11,
                "eta_value": 0.792,
                "incident_angle_characteristics": "multiple",
                "glass_area_ratio": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 16,
                "name": "exterior_ceiling",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "external_general_part",
                "area": 13.25,
                "h_c": 5.0,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0432,
                            "thermal_capacity": 7.885
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 3.42,
                            "thermal_capacity": 1.368
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "top",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.09,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 17,
                "name": "internal_wall_non_occupant",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "internal",
                "area": 8.736,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "outside_heat_transfer_resistance": 0.11,
                "rear_surface_boundary_id": 49
            },
            {
                "id": 18,
                "name": "south_exterior_wall",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "external_general_part",
                "area": 4.76525,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0432,
                            "thermal_capacity": 7.885
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 1.28,
                            "thermal_capacity": 0.512
                        },
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        },
                        {
                            "name": "wood-wool_and_flake_boards",
                            "thermal_resistance": 0.0882,
                            "thermal_capacity": 25.1789
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "s",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 19,
                "name": "south_exterior_window",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "external_transparent_part",
                "area": 3.22,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "solar_shading_part": {
                    "existence": True,
                    "input_method": "simple",
                    "depth": 0.65,
                    "d_h": 1.95,
                    "d_e": 0.65
                },
                "is_sun_striked_outside": True,
                "direction": "s",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "u_value": 4.65,
                "inside_heat_transfer_resistance": 0.11,
                "eta_value": 0.792,
                "incident_angle_characteristics": "multiple",
                "glass_area_ratio": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 20,
                "name": "exterior_ceiling",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "external_general_part",
                "area": 10.77,
                "h_c": 5.0,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0432,
                            "thermal_capacity": 7.885
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 3.42,
                            "thermal_capacity": 1.368
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "top",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.09,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 21,
                "name": "internal_wall_non_occupant",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "internal",
                "area": 7.098,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "outside_heat_transfer_resistance": 0.11,
                "rear_surface_boundary_id": 47
            },
            {
                "id": 22,
                "name": "internal_floor_main_occupant",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "internal",
                "area": 10.77,
                "h_c": 0.7,
                "is_solar_absorbed_inside": True,
                "is_floor": True,
                "layers": [
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.07,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "outside_heat_transfer_resistance": 0.09,
                "rear_surface_boundary_id": 9
            },
            {
                "id": 23,
                "name": "east_exterior_wall",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "external_general_part",
                "area": 9.168,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0432,
                            "thermal_capacity": 7.885
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 1.28,
                            "thermal_capacity": 0.512
                        },
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        },
                        {
                            "name": "wood-wool_and_flake_boards",
                            "thermal_resistance": 0.0882,
                            "thermal_capacity": 25.1789
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "e",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 24,
                "name": "east_exterior_window",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "external_transparent_part",
                "area": 0.66,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "e",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "u_value": 4.65,
                "inside_heat_transfer_resistance": 0.11,
                "eta_value": 0.792,
                "incident_angle_characteristics": "multiple",
                "glass_area_ratio": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 25,
                "name": "south_exterior_wall",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "external_general_part",
                "area": 4.76525,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0432,
                            "thermal_capacity": 7.885
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 1.28,
                            "thermal_capacity": 0.512
                        },
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        },
                        {
                            "name": "wood-wool_and_flake_boards",
                            "thermal_resistance": 0.0882,
                            "thermal_capacity": 25.1789
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "s",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 26,
                "name": "south_exterior_window",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "external_transparent_part",
                "area": 3.22,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "solar_shading_part": {
                    "existence": True,
                    "input_method": "simple",
                    "depth": 0.65,
                    "d_h": 1.95,
                    "d_e": 0.65
                },
                "is_sun_striked_outside": True,
                "direction": "s",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "u_value": 4.65,
                "inside_heat_transfer_resistance": 0.11,
                "eta_value": 0.792,
                "incident_angle_characteristics": "multiple",
                "glass_area_ratio": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 27,
                "name": "exterior_ceiling",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "external_general_part",
                "area": 10.77,
                "h_c": 5.0,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0432,
                            "thermal_capacity": 7.885
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 3.42,
                            "thermal_capacity": 1.368
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "top",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.09,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 28,
                "name": "internal_wall_non_occupant",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "internal",
                "area": 7.098,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "outside_heat_transfer_resistance": 0.11,
                "rear_surface_boundary_id": 48
            },
            {
                "id": 29,
                "name": "internal_floor_main_occupant",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "internal",
                "area": 10.77,
                "h_c": 0.7,
                "is_solar_absorbed_inside": True,
                "is_floor": True,
                "layers": [
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.07,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "outside_heat_transfer_resistance": 0.09,
                "rear_surface_boundary_id": 10
            },
            {
                "id": 30,
                "name": "north_exterior_wall",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "external_general_part",
                "area": 2.639,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0432,
                            "thermal_capacity": 7.885
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 1.28,
                            "thermal_capacity": 0.512
                        },
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        },
                        {
                            "name": "wood-wool_and_flake_boards",
                            "thermal_resistance": 0.0882,
                            "thermal_capacity": 25.1789
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "n",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 31,
                "name": "south_exterior_wall",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "external_general_part",
                "area": 8.605,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0432,
                            "thermal_capacity": 7.885
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 1.28,
                            "thermal_capacity": 0.512
                        },
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        },
                        {
                            "name": "wood-wool_and_flake_boards",
                            "thermal_resistance": 0.0882,
                            "thermal_capacity": 25.1789
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "s",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 32,
                "name": "south_exterior_window",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "external_transparent_part",
                "area": 4.59,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "s",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "u_value": 4.65,
                "inside_heat_transfer_resistance": 0.11,
                "eta_value": 0.792,
                "incident_angle_characteristics": "multiple",
                "glass_area_ratio": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 33,
                "name": "west_exterior_wall",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "external_general_part",
                "area": 10.556,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0432,
                            "thermal_capacity": 7.885
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 1.28,
                            "thermal_capacity": 0.512
                        },
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        },
                        {
                            "name": "wood-wool_and_flake_boards",
                            "thermal_resistance": 0.0882,
                            "thermal_capacity": 25.1789
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "w",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 34,
                "name": "exterior_floor",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "external_general_part",
                "area": 16.56,
                "h_c": 0.7,
                "is_solar_absorbed_inside": True,
                "is_floor": True,
                "layers": [
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 1.28,
                            "thermal_capacity": 0.512
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": False,
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.15,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 0.7
            },
            {
                "id": 35,
                "name": "exterior_ceiling",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "external_general_part",
                "area": 3.31,
                "h_c": 5.0,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0432,
                            "thermal_capacity": 7.885
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 3.42,
                            "thermal_capacity": 1.368
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "top",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.09,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 36,
                "name": "internal_wall_non_occupant",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "internal",
                "area": 8.736,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "outside_heat_transfer_resistance": 0.11,
                "rear_surface_boundary_id": 46
            },
            {
                "id": 37,
                "name": "internal_wall_main_occupant",
                "sub_name": "",
                "connected_room_id": 1,
                "boundary_type": "internal",
                "area": 8.736,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "outside_heat_transfer_resistance": 0.11,
                "rear_surface_boundary_id": 11
            },
            {
                "id": 38,
                "name": "north_exterior_wall",
                "sub_name": "",
                "connected_room_id": 2,
                "boundary_type": "external_general_part",
                "area": 43.2205,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0432,
                            "thermal_capacity": 7.885
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 1.28,
                            "thermal_capacity": 0.512
                        },
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        },
                        {
                            "name": "wood-wool_and_flake_boards",
                            "thermal_resistance": 0.0882,
                            "thermal_capacity": 25.1789
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "n",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 39,
                "name": "north_exterior_window",
                "sub_name": "",
                "connected_room_id": 2,
                "boundary_type": "external_transparent_part",
                "area": 3.69,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "n",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "u_value": 4.65,
                "inside_heat_transfer_resistance": 0.11,
                "eta_value": 0.792,
                "incident_angle_characteristics": "multiple",
                "glass_area_ratio": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 40,
                "name": "east_exterior_wall",
                "sub_name": "",
                "connected_room_id": 2,
                "boundary_type": "external_general_part",
                "area": 4.914,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0432,
                            "thermal_capacity": 7.885
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 1.28,
                            "thermal_capacity": 0.512
                        },
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        },
                        {
                            "name": "wood-wool_and_flake_boards",
                            "thermal_resistance": 0.0882,
                            "thermal_capacity": 25.1789
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "e",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 41,
                "name": "west_exterior_wall",
                "sub_name": "",
                "connected_room_id": 2,
                "boundary_type": "external_general_part",
                "area": 12.5,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0432,
                            "thermal_capacity": 7.885
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 1.28,
                            "thermal_capacity": 0.512
                        },
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        },
                        {
                            "name": "wood-wool_and_flake_boards",
                            "thermal_resistance": 0.0882,
                            "thermal_capacity": 25.1789
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "w",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 42,
                "name": "west_exterior_window",
                "sub_name": "",
                "connected_room_id": 2,
                "boundary_type": "external_transparent_part",
                "area": 2.97,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "w",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.04,
                "u_value": 4.65,
                "inside_heat_transfer_resistance": 0.11,
                "eta_value": 0.792,
                "incident_angle_characteristics": "multiple",
                "glass_area_ratio": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 43,
                "name": "exterior_floor",
                "sub_name": "",
                "connected_room_id": 2,
                "boundary_type": "external_general_part",
                "area": 21.52,
                "h_c": 0.7,
                "is_solar_absorbed_inside": True,
                "is_floor": True,
                "layers": [
                        {
                            "name": "plywood",
                            "thermal_resistance": 0.075,
                            "thermal_capacity": 8.64
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 1.28,
                            "thermal_capacity": 0.512
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": False,
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.15,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 0.7
            },
            {
                "id": 44,
                "name": "exterior_ceiling",
                "sub_name": "",
                "connected_room_id": 2,
                "boundary_type": "external_general_part",
                "area": 25.68,
                "h_c": 5.0,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0432,
                            "thermal_capacity": 7.885
                        },
                        {
                            "name": "glass_wool_10K",
                            "thermal_resistance": 3.42,
                            "thermal_capacity": 1.368
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "is_sun_striked_outside": True,
                "direction": "top",
                "outside_emissivity": 0.9,
                "outside_heat_transfer_resistance": 0.09,
                "outside_solar_absorption": 0.8,
                "temp_dif_coef": 1.0
            },
            {
                "id": 45,
                "name": "internal_wall_main_occupant",
                "sub_name": "",
                "connected_room_id": 2,
                "boundary_type": "internal",
                "area": 21.6125,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "outside_heat_transfer_resistance": 0.11,
                "rear_surface_boundary_id": 8
            },
            {
                "id": 46,
                "name": "internal_wall_other_occupant",
                "sub_name": "",
                "connected_room_id": 2,
                "boundary_type": "internal",
                "area": 8.736,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "outside_heat_transfer_resistance": 0.11,
                "rear_surface_boundary_id": 36
            },
            {
                "id": 47,
                "name": "internal_wall_other_occupant",
                "sub_name": "",
                "connected_room_id": 2,
                "boundary_type": "internal",
                "area": 7.098,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "outside_heat_transfer_resistance": 0.11,
                "rear_surface_boundary_id": 21
            },
            {
                "id": 48,
                "name": "internal_wall_other_occupant",
                "sub_name": "",
                "connected_room_id": 2,
                "boundary_type": "internal",
                "area": 7.098,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "outside_heat_transfer_resistance": 0.11,
                "rear_surface_boundary_id": 28
            },
            {
                "id": 49,
                "name": "internal_wall_other_occupant",
                "sub_name": "",
                "connected_room_id": 2,
                "boundary_type": "internal",
                "area": 8.736,
                "h_c": 2.5,
                "is_solar_absorbed_inside": False,
                "is_floor": False,
                "layers": [
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        },
                        {
                            "name": "non-hermetic_air_layer",
                            "thermal_resistance": 0.09,
                            "thermal_capacity": 0.0
                        },
                        {
                            "name": "plaster_board",
                            "thermal_resistance": 0.0568,
                            "thermal_capacity": 10.375
                        }
                    ],
                "solar_shading_part": {
                    "existence": False
                },
                "outside_heat_transfer_resistance": 0.11,
                "rear_surface_boundary_id": 17
            }
        ]
