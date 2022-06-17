from typing import Dict, List
import numpy as np
from dataclasses import dataclass


@dataclass
class MechanicalVentilation:

    # id
    id: int

    # 換気経路のタイプ
    root_type: str

    # 換気量, m3/h
    volume: float

    # 換気ルート
    root: List[int]


class MechanicalVentilations:

    def __init__(self, dict_mechanical_ventilations: Dict, n_rm: int):

        self._mechanical_ventilations = [
            MechanicalVentilation(
                id=v['id'],
                root_type=v['root_type'],
                volume=v['volume'],
                root=v['root']
            )
            for v in dict_mechanical_ventilations
        ]

        self._n_rm = n_rm

    def get_v_vent_mec_general_is(self) -> np.ndarray:

        v1 = np.zeros(shape=self._n_rm, dtype=float)

        for v in self._mechanical_ventilations:

            if v.root_type in ['type1', 'type2', 'type3']:

                r = v.root

                for i in range(len(r)):

                    if i == 0:
                        v1[r[0]] = v1[r[0]] + v.volume / 3600

            else:

                raise KeyError()

        v1 = v1.reshape(-1, 1)

        return v1

    def get_v_vent_int_is_is(self) -> np.ndarray:

        v2 = np.zeros(shape=(self._n_rm, self._n_rm), dtype=float)

        for v in self._mechanical_ventilations:

            if v.root_type in ['type1', 'type2', 'type3']:

                r = v.root

                for i in range(len(r)):

                    if i == 0:
                        pass
                    else:
                        v2[r[i], r[i-1]] = v2[r[i], r[i-1]] + v.volume / 3600
                        v2[r[i], r[i]] = v2[r[i], r[i]] - v.volume / 3600

            else:

                raise KeyError()

        return v2
