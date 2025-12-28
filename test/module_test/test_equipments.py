import unittest

from heat_load_calc.equipments import Equipments


class TestEquipments(unittest.TestCase):

    def test_heating_equipments_not_exist_error(self):
        d = {
            "cooling_equipments": []
        }

        with self.assertRaises(KeyError):
            Equipments(d=d, n_rm=None, n_b=None, bs=None)
    
    def test_cooling_equipments_not_exist_error(self):
        d = {
            "heating_equipments": []
        }

        with self.assertRaises(KeyError):
            Equipments(d=d, n_rm=None, n_b=None, bs=None)

