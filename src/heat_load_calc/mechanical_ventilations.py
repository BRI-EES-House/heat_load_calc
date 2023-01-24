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

    # 換気経路のタイプ
    root_type: VentilationType

    # 換気量, m3/h
    volume: float

    # 換気ルート
    root: List[int]


class MechanicalVentilations:

    def __init__(self, vs: Dict, n_rm: int):

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
    def v_vent_mec_general_is(self):
        return self._v_vent_mec_general_is

    @property
    def v_vent_int_is_is(self):
        return self._v_vent_int_is_is

    def get_v_vent_mec_general_is(self) -> np.ndarray:

        v1 = np.zeros(shape=self._n_rm, dtype=float)

        for v in self._mechanical_ventilations:

            if v.root_type in [VentilationType.TYPE1, VentilationType.TYPE2, VentilationType.TYPE3]:

                r = v.root

                v1[r[0]] = v1[r[0]] + v.volume / 3600

        v1 = v1.reshape(-1, 1)

        return v1

    def get_v_vent_int_is_is(self) -> np.ndarray:

        v2 = np.zeros(shape=(self._n_rm, self._n_rm), dtype=float)

        for v in self._mechanical_ventilations:

            if v.root_type in [VentilationType.TYPE1, VentilationType.TYPE2, VentilationType.TYPE3]:

                r = v.root

                for i in range(len(r)):

                    if i == 0:
                        pass
                    else:
                        v2[r[i], r[i-1]] = v2[r[i], r[i-1]] + v.volume / 3600
                        v2[r[i], r[i]] = v2[r[i], r[i]] - v.volume / 3600

            elif v.root_type == VentilationType.NATURAL_LOOP:

                r = v.root

                for i in range(len(r)):

                    if i == 0:
                        i_upstream = len(r) - 1
                    else:
                        i_upstream = i - 1

                    v2[r[i], r[i_upstream]] = v2[r[i], r[i_upstream]] + v.volume / 3600
                    v2[r[i], r[i]] = v2[r[i], r[i]] - v.volume / 3600

            else:

                raise KeyError()

        return v2
