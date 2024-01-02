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
    a_f: float

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

    # MET value
    met: float


class Rooms:

    def __init__(self, ds: List[Dict]):

        # room の数
        self._n_r = len(ds)

        rms : List[Room] = [self._get_rm(d=d) for d in ds]

        self._id_r_is = np.array([rm.id for rm in rms]).reshape(-1, 1)
        self._name_r_is = np.array([rm.name for rm in rms]).reshape(-1, 1)
        self._sub_name_r_is = np.array([rm.sub_name for rm in rms]).reshape(-1, 1)
        self._a_f_r_is = np.array([rm.a_f for rm in rms]).reshape(-1, 1)
        self._v_r_is = np.array([rm.v for rm in rms]).reshape(-1, 1)
        self._c_sh_frt_is = np.array([rm.c_sh_frt for rm in rms]).reshape(-1, 1)
        self._g_sh_frt_is = np.array([rm.g_sh_frt for rm in rms]).reshape(-1, 1)
        self._c_lh_frt_is = np.array([rm.c_lh_frt for rm in rms]).reshape(-1, 1)
        self._g_lh_frt_is = np.array([rm.g_lh_frt for rm in rms]).reshape(-1, 1)
        self._v_vent_ntr_set_is = np.array([rm.v_vent_ntr_set for rm in rms]).reshape(-1, 1)
        self._met_is = np.array([rm.met for rm in rms]).reshape(-1, 1)

    @staticmethod
    def _get_rm(d: Dict):

        v_r_i = float(d['volume'])

        c_lh_frt, c_sh_frt, g_lh_frt, g_sh_frt = furniture.get_furniture_specs(
            dict_furniture_i=d['furniture'],
            v_r_i=v_r_i
        )

        if 'MET' in d:
            met = float(d['MET'])
        else:
            met = 1.0

        # v_vent_ntr_set については m3/h から m3/s の単位変換を行う。
        return Room(
            id=int(d['id']),
            name=str(d['name']),
            sub_name=str(d['sub_name']),
            a_f=float(d['floor_area']),
            v=v_r_i,
            c_sh_frt=c_sh_frt,
            g_sh_frt=g_sh_frt,
            c_lh_frt=c_lh_frt,
            g_lh_frt=g_lh_frt,
            v_vent_ntr_set=float(d['ventilation']['natural']) / 3600.0,
            met=met
        )

    @property
    def n_r(self) -> int:
        """number of room / 室の数"""
        return self._n_r

    @property
    def id_r_is(self) -> np.ndarray:
        """ID of room i / 室iのID, [I, 1]"""
        return self._id_r_is

    @property
    def name_r_is(self) -> np.ndarray:
        """name of room i / 室iの名前, [I, 1]"""
        return self._name_r_is

    @property
    def sub_name_r_is(self) -> np.ndarray:
        """sub name of room i / 室iの名前2, [I, 1]"""
        return self._sub_name_r_is

    @property
    def a_f_r_is(self) -> np.ndarray:
        """area of room i / 室iの面積, m2, [I, 1]"""
        return self._a_f_r_is

    @property
    def v_r_is(self) -> np.ndarray:
        """volume of room i / 室iの容積, m3, [I, 1]"""
        return self._v_r_is

    @property
    def c_sh_frt_is(self) -> np.ndarray:
        """thermal capacity of furniture in room i / 室iの備品等の熱容量, J/K, [I, 1]"""
        return self._c_sh_frt_is

    @property
    def g_sh_frt_is(self) -> np.ndarray:
        """thermal conductance between air and furniture in room i / 室iの空気と備品等間の熱コンダクタンス, W/K, [I, 1]"""
        return self._g_sh_frt_is

    @property
    def c_lh_frt_is(self) -> np.ndarray:
        """moisture capacity of furniture in room i / 室iの備品等の湿気容量, kg/(kg/kgDA), [I, 1]"""
        return self._c_lh_frt_is

    @property
    def g_lh_frt_is(self) -> np.ndarray:
        """moisture conductance between air and furniture in room i / 室iの空気と備品等間の湿気コンダクタンス, kg/(s (kg/kgDA)), [I, 1]"""
        return self._g_lh_frt_is

    @property
    def v_vent_ntr_set_is(self) -> np.ndarray:
        """ventilation amount of room i when using natural ventilation / 室iの自然換気利用時の換気量, m3/s, [I, 1]"""
        return self._v_vent_ntr_set_is

    @property
    def met_is(self) -> np.ndarray:
        """MET value of occupants in room i / 室iの在室者のMet値, [i, 1]"""
        return self._met_is
