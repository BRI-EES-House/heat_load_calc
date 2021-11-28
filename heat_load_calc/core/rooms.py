from typing import Dict
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

    # 備品等の熱容量, J/K
    c_sh_frt: float

    # 空気と備品等間の熱コンダクタンス, W/K
    g_sh_frt: float

    # 備品等の湿気容量, kg/(kg/kgDA)
    c_lh_frt: float

    # 空気と備品等間の湿気コンダクタンス, kg/(s (kg/kgDA))
    g_lh_frt: float

    # 自然風利用時の換気量, m3/s
    v_vent_ntr_set: float


class Rooms:

    def __init__(self, dict_rooms: Dict):

        # room の数
        self._n_rm = len(dict_rooms)

        self._rms = [self._get_rm(dict_room=rm) for rm in dict_rooms]

    @staticmethod
    def _get_rm(dict_room: Dict):

        v_rm_i = dict_room['volume']

        c_lh_frt, c_sh_frt, g_lh_frt, g_sh_frt = furniture.get_furniture_specs(
            dict_furniture_i=dict_room['furniture'],
            v_rm_i=v_rm_i
        )

        return Room(
            id=dict_room['id'],
            name=dict_room['name'],
            v=v_rm_i,
            c_sh_frt=c_sh_frt,
            g_sh_frt=g_sh_frt,
            c_lh_frt=c_lh_frt,
            g_lh_frt=g_lh_frt,
            v_vent_ntr_set=dict_room['ventilation']['natural']
        )

    def get_n_rm(self):

        return self._n_rm

    def get_id_rm_is(self):

        return np.array([rm.id for rm in self._rms]).reshape(-1, 1)

    def get_name_rm_is(self):

        return np.array([rm.name for rm in self._rms]).reshape(-1, 1)

    def get_v_rm_is(self):

        return np.array([rm.v for rm in self._rms]).reshape(-1, 1)

    def get_c_sh_frt(self):

        return np.array([rm.c_sh_frt for rm in self._rms]).reshape(-1, 1)

    def get_g_sh_frt(self):

        return np.array([rm.g_sh_frt for rm in self._rms]).reshape(-1, 1)

    def get_c_lh_frt(self):

        return np.array([rm.c_lh_frt for rm in self._rms]).reshape(-1, 1)

    def get_g_lh_frt(self):

        return np.array([rm.g_lh_frt for rm in self._rms]).reshape(-1, 1)

    def get_v_vent_ntr_set_is(self):

        # m3/h から m3/s の単位変換を行う。
        return np.array([rm.v_vent_ntr_set / 3600.0 for rm in self._rms]).reshape(-1, 1)