from typing import Dict, List
import numpy as np

from heat_load_calc.core.boundary_simple import BoundarySimple
from heat_load_calc.core import boundary_simple

class Equipments:

    def __init__(self, e: Dict, n_rm: int):

        self._hes = e['heating_equipments']
        self._ces = e['cooling_equipments']
        self._n_rm = n_rm

    def get_is_radiative_heating_is(self, bss: List[BoundarySimple]):

        is_radiative_heating_is = np.full(shape=(self._n_rm, 1), fill_value=False)

        for he in self._hes:
            if he['equipment_type'] == 'floor_heating':
                bs = boundary_simple.get_boundary_by_id(bss=bss, boundary_id=he['property']['boundary_id'])
                is_radiative_heating_is[bs.connected_room_id] = True

        return is_radiative_heating_is

    def get_is_radiative_cooling_is(self, bss: List[BoundarySimple]):

        is_radiative_cooling_is = np.full(shape=(self._n_rm, 1), fill_value=False)

        for ce in self._ces:
            if ce['equipment_type'] == 'floor_cooling':
                bs = boundary_simple.get_boundary_by_id(bss=bss, boundary_id=ce['property']['boundary_id'])
                is_radiative_cooling_is[bs.connected_room_id] = True

        return is_radiative_cooling_is

    def get_q_rs_h_max_is(self):

        q_rs_h_max_is = np.zeros(shape=(self._n_rm, 1), dtype=float)

        for he in self._hes:
            if he['equipment_type'] == 'floor_heating':
                q_rs_h_max_is[he['property']['space_id']] = q_rs_h_max_is[he['property']['space_id']] + he['property']['max_capacity'] * he['property']['area']

        return q_rs_h_max_is

    def get_q_rs_c_max_is(self):

        q_rs_c_max_is = np.zeros(shape=(self._n_rm, 1), dtype=float)

        for ce in self._ces:
            if ce['equipment_type'] == 'floor_cooling':
                q_rs_c_max_is[ce['property']['space_id']] = q_rs_c_max_is[ce['property']['space_id']] + ce['property']['max_capacity'] * ce['property']['area']

        return q_rs_c_max_is

