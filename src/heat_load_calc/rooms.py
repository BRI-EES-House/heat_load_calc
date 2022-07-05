from typing import Dict, List
import numpy as np
from dataclasses import dataclass

from heat_load_calc import furniture


@dataclass
class Room:

    # id
    id: int

    # 名称
    name: str

    # 副名称
    sub_name: str

    # 気積, m3
    v: float

    # 床面積, m2
    floor_area: float

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

    def __init__(self, ds: List[Dict]):

        # room の数
        self._n_rm = len(ds)

        self._rms = [self._get_rm(d=d) for d in ds]

    @staticmethod
    def _get_rm(d: Dict):

        v_rm_i = d['volume']

        c_lh_frt, c_sh_frt, g_lh_frt, g_sh_frt = furniture.get_furniture_specs(
            dict_furniture_i=d['furniture'],
            v_rm_i=v_rm_i
        )

        return Room(
            id=d['id'],
            name=d['name'],
            sub_name=d['sub_name'],
            floor_area=d['floor_area'],
            v=v_rm_i,
            c_sh_frt=c_sh_frt,
            g_sh_frt=g_sh_frt,
            c_lh_frt=c_lh_frt,
            g_lh_frt=g_lh_frt,
            v_vent_ntr_set=d['ventilation']['natural']
        )

    @property
    def n_rm(self):

        return self._n_rm

    @property
    def id_rm_is(self):

        return np.array([rm.id for rm in self._rms]).reshape(-1, 1)

    @property
    def name_rm_is(self):

        return np.array([rm.name for rm in self._rms]).reshape(-1, 1)

    @property
    def sub_name_rm_is(self):

        return np.array([rm.sub_name for rm in self._rms]).reshape(-1, 1)

    @property
    def floor_area_is(self):

        return np.array([rm.floor_area for rm in self._rms]).reshape(-1, 1)

    @property
    def v_rm_is(self):

        return np.array([rm.v for rm in self._rms]).reshape(-1, 1)

    @property
    def c_sh_frt_is(self):

        return np.array([rm.c_sh_frt for rm in self._rms]).reshape(-1, 1)

    @property
    def g_sh_frt_is(self):

        return np.array([rm.g_sh_frt for rm in self._rms]).reshape(-1, 1)

    @property
    def c_lh_frt_is(self):

        return np.array([rm.c_lh_frt for rm in self._rms]).reshape(-1, 1)

    @property
    def g_lh_frt_is(self):

        return np.array([rm.g_lh_frt for rm in self._rms]).reshape(-1, 1)

    @property
    def v_vent_ntr_set_is(self):

        # m3/h から m3/s の単位変換を行う。
        return np.array([rm.v_vent_ntr_set / 3600.0 for rm in self._rms]).reshape(-1, 1)

    @property
    def met_is(self):

        return np.full(shape=(self._n_rm, 1), fill_value=1.0, dtype=float)
