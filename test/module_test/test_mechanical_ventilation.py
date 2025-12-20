import unittest

from heat_load_calc import building
from heat_load_calc.mechanical_ventilations import MechanicalVentilations


class TestMechanicalVentilations(unittest.TestCase):

    def test_v_vent_mec_general_is_type1(self):

        mv = MechanicalVentilations(
            ds=[
                {
                    'id': 0,
                    'root_type': 'type1',
                    'volume': 30.0,
                    'root': [0, 1, 2]
                }
            ],
            n_rm=3
        )

        v_vent_mec_general_is = mv.get_v_vent_mec_general_is()

        self.assertEqual(v_vent_mec_general_is[0], 30.0/3600)
        self.assertEqual(v_vent_mec_general_is[1], 0.0)
        self.assertEqual(v_vent_mec_general_is[2], 0.0)

    def test_v_vent_mec_general_is_type2(self):

        mv = MechanicalVentilations(
            ds=[
                {
                    'id': 0,
                    'root_type': 'type2',
                    'volume': 30.0,
                    'root': [0, 1, 2]
                }
            ],
            n_rm=3
        )

        v_vent_mec_general_is = mv.get_v_vent_mec_general_is()

        self.assertEqual(v_vent_mec_general_is[0], 30.0/3600)
        self.assertEqual(v_vent_mec_general_is[1], 0.0)
        self.assertEqual(v_vent_mec_general_is[2], 0.0)

    def test_v_vent_mec_general_is_type3(self):

        mv = MechanicalVentilations(
            ds=[
                {
                    'id': 0,
                    'root_type': 'type3',
                    'volume': 30.0,
                    'root': [0, 1, 2]
                }
            ],
            n_rm=3
        )

        v_vent_mec_general_is = mv.get_v_vent_mec_general_is()

        self.assertEqual(v_vent_mec_general_is[0], 30.0/3600)
        self.assertEqual(v_vent_mec_general_is[1], 0.0)
        self.assertEqual(v_vent_mec_general_is[2], 0.0)

    def test_v_vent_mec_general_is_natural_loop(self):

        mv = MechanicalVentilations(
            ds=[
                {
                    'id': 0,
                    'root_type': 'natural_loop',
                    'volume': 30.0,
                    'root': [0, 1, 2]
                }
            ],
            n_rm=3
        )

        v_vent_mec_general_is = mv.get_v_vent_mec_general_is()

        self.assertEqual(v_vent_mec_general_is[0], 0.0)
        self.assertEqual(v_vent_mec_general_is[1], 0.0)
        self.assertEqual(v_vent_mec_general_is[2], 0.0)

    def test_v_vent_int_is_is_type1(self):

        mv = MechanicalVentilations(
            ds=[
                {
                    'id': 0,
                    'root_type': 'type1',
                    'volume': 30.0,
                    'root': [0, 1, 2]
                }
            ],
            n_rm=3
        )

        v_vent_int_is_is = mv.get_v_vent_int_is_is()

        self.assertEqual(v_vent_int_is_is[0,0], 0.0)
        self.assertEqual(v_vent_int_is_is[0,1], 0.0)
        self.assertEqual(v_vent_int_is_is[0,2], 0.0)
        self.assertEqual(v_vent_int_is_is[1,0], 30.0/3600)
        self.assertEqual(v_vent_int_is_is[1,1], -30.0/3600)
        self.assertEqual(v_vent_int_is_is[1,2], 0.0)
        self.assertEqual(v_vent_int_is_is[2,0], 0.0)
        self.assertEqual(v_vent_int_is_is[2,1], 30.0/3600)
        self.assertEqual(v_vent_int_is_is[2,2], -30.0/3600)

    def test_v_vent_int_is_is_type2(self):

        mv = MechanicalVentilations(
            ds=[
                {
                    'id': 0,
                    'root_type': 'type2',
                    'volume': 30.0,
                    'root': [0, 1, 2]
                }
            ],
            n_rm=3
        )

        v_vent_int_is_is = mv.get_v_vent_int_is_is()

        self.assertEqual(v_vent_int_is_is[0,0], 0.0)
        self.assertEqual(v_vent_int_is_is[0,1], 0.0)
        self.assertEqual(v_vent_int_is_is[0,2], 0.0)
        self.assertEqual(v_vent_int_is_is[1,0], 30.0/3600)
        self.assertEqual(v_vent_int_is_is[1,1], -30.0/3600)
        self.assertEqual(v_vent_int_is_is[1,2], 0.0)
        self.assertEqual(v_vent_int_is_is[2,0], 0.0)
        self.assertEqual(v_vent_int_is_is[2,1], 30.0/3600)
        self.assertEqual(v_vent_int_is_is[2,2], -30.0/3600)

    def test_v_vent_int_is_is_type3(self):

        mv = MechanicalVentilations(
            ds=[
                {
                    'id': 0,
                    'root_type': 'type3',
                    'volume': 30.0,
                    'root': [0, 1, 2]
                }
            ],
            n_rm=3
        )

        v_vent_int_is_is = mv.get_v_vent_int_is_is()

        self.assertEqual(v_vent_int_is_is[0,0], 0.0)
        self.assertEqual(v_vent_int_is_is[0,1], 0.0)
        self.assertEqual(v_vent_int_is_is[0,2], 0.0)
        self.assertEqual(v_vent_int_is_is[1,0], 30.0/3600)
        self.assertEqual(v_vent_int_is_is[1,1], -30.0/3600)
        self.assertEqual(v_vent_int_is_is[1,2], 0.0)
        self.assertEqual(v_vent_int_is_is[2,0], 0.0)
        self.assertEqual(v_vent_int_is_is[2,1], 30.0/3600)
        self.assertEqual(v_vent_int_is_is[2,2], -30.0/3600)

    def test_v_vent_int_is_is_natural_loop(self):

        mv = MechanicalVentilations(
            ds=[
                {
                    'id': 0,
                    'root_type': 'natural_loop',
                    'volume': 30.0,
                    'root': [0, 1, 2]
                }
            ],
            n_rm=3
        )

        v_vent_int_is_is = mv.get_v_vent_int_is_is()

        self.assertEqual(v_vent_int_is_is[0,0], -30.0/3600)
        self.assertEqual(v_vent_int_is_is[0,1], 0.0)
        self.assertEqual(v_vent_int_is_is[0,2], 30.0/3600)
        self.assertEqual(v_vent_int_is_is[1,0], 30.0/3600)
        self.assertEqual(v_vent_int_is_is[1,1], -30.0/3600)
        self.assertEqual(v_vent_int_is_is[1,2], 0.0)
        self.assertEqual(v_vent_int_is_is[2,0], 0.0)
        self.assertEqual(v_vent_int_is_is[2,1], 30.0/3600)
        self.assertEqual(v_vent_int_is_is[2,2], -30.0/3600)
