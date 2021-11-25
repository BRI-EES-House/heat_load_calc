﻿from typing import Dict
import numpy as np
from dataclasses import dataclass

from heat_load_calc.core import furniture

@dataclass
class Room:

    # id
    id: int

    # 名前
    name: str

    # 気積, m3
    v: float


class Rooms:

    def __init__(self, dict_rooms: Dict):

        # room の数
        self._n_rm = len(dict_rooms)

        self._rms = [self._get_rm(dict_room=rm) for rm in dict_rooms]

    @staticmethod
    def _get_rm(dict_room: Dict):
                
        return Room(id=dict_room['id'], name=dict_room['name'], v=dict_room['volume'])

    def get_n_rm(self):

        return self._n_rm

    def get_id_rm_is(self):

        return np.array([rm.id for rm in self._rms]).reshape(-1, 1)

    def get_name_rm_is(self):

        return np.array([rm.name for rm in self._rms]).reshape(-1, 1)

    def get_v_rm_is(self):

        return np.array([rm.v for rm in self._rms]).reshape(-1, 1)
