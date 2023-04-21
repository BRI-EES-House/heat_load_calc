from typing import Dict, List
import numpy as np
from dataclasses import dataclass
from enum import Enum


class VentilationType(Enum):

    TYPE1 = 'type1'
    TYPE2 = 'type2'
    TYPE3 = 'type3'
    NATURAL_LOOP = 'natural_loop'


@dataclass
class MechanicalVentilation:

    # id
    id: int

    # ventilation root type
    root_type: VentilationType

    # the amount of ventilation, m3/h
    volume: float

    # root of ventilation
    # the list of 'id's of rooms
    root: List[int]


class MechanicalVentilations:

    def __init__(self, vs: List[Dict], n_rm: int):

        self._mechanical_ventilations = [
            MechanicalVentilation(
                id=v['id'],
                root_type=VentilationType(v['root_type']),
                volume=v['volume'],
                root=v['root']
            )
            for v in vs
        ]

        self._n_rm = n_rm

        self._v_vent_mec_general_is = self.get_v_vent_mec_general_is()

        self._v_vent_int_is_is = self.get_v_vent_int_is_is()

    @property
    def v_vent_mec_general_is(self) -> np.ndarray:
        """mechanical ventilation amount (excluding local ventilation) of room i, m3/s, [i, 1]"""
        return self._v_vent_mec_general_is

    @property
    def v_vent_int_is_is(self) -> np.ndarray:
        """mechanical ventilation amount from the upstream room of room i, m3/s, [i, i]"""
        return self._v_vent_int_is_is

    def get_v_vent_mec_general_is(self) -> np.ndarray:
        """Calculate the mechanical ventilation (general) of room i.

        Returns:
            mechanical ventilation (general) of room i, m3/s
        
        Note:
            eq. 1
        """

        v1 = np.zeros(shape=self._n_rm, dtype=float)

        # calculate one loop
        # mv: one mechanical ventilation loop
        for mv in self._mechanical_ventilations:

            # In case that the mechanical ventialtion tyepe is type1, type2 or type3,
            # the outdoor air flows into the room with top ID.
            # Therefore, add the ventilation amount to the matrix of the room ID.
            if mv.root_type in [VentilationType.TYPE1, VentilationType.TYPE2, VentilationType.TYPE3]:
                
                # the list of the mechanical ventilation loot
                r = mv.root

                # Add the ventilation amount to the room which ID equals to the top ID of mechanical ventilation list.
                # Convert the unit from m3/h to m3/s.
                v1[r[0]] = v1[r[0]] + mv.volume / 3600

        v1 = v1.reshape(-1, 1)

        return v1

    def get_v_vent_int_is_is(self) -> np.ndarray:
        """Calculate the tamount of the air moved from the room i* to the room i.

        Returns:
            the amount of the air moved from the room i* to tohe room i, [i, i], m3/s
        
        """

        # Make the matrix N times N.
        # The initial values are zero.
        # N is the number of rooms.
        v = np.zeros(shape=(self._n_rm, self._n_rm), dtype=float)

        # mv: one mechanical ventilation root
        for mv in self._mechanical_ventilations:

            if mv.root_type in [VentilationType.TYPE1, VentilationType.TYPE2, VentilationType.TYPE3]:

                r = mv.root

                for i in range(len(r)):

                    if i == 0:
                        pass
                    else:
                        v[r[i], r[i-1]] = v[r[i], r[i-1]] + mv.volume / 3600
                        v[r[i], r[i]] = v[r[i], r[i]] - mv.volume / 3600

            elif mv.root_type == VentilationType.NATURAL_LOOP:

                r = mv.root

                for i in range(len(r)):

                    if i == 0:
                        i_upstream = len(r) - 1
                    else:
                        i_upstream = i - 1

                    v[r[i], r[i_upstream]] = v[r[i], r[i_upstream]] + mv.volume / 3600
                    v[r[i], r[i]] = v[r[i], r[i]] - mv.volume / 3600

            else:

                raise KeyError()

        return v
