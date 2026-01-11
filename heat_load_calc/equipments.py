from typing import Dict, Tuple, List
from typing import Union
import numpy as np
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

from heat_load_calc.psychrometrics import get_x, get_p_vs
from heat_load_calc.global_number import get_c_a, get_rho_a
from heat_load_calc.matrix_method import v_diag


class Individual:

    def __init__(self, id: int, name: str, room_id: int, boundary_id: int | None, e, id_r_is: np.ndarray, id_js: np.ndarray, p_is_js: np.ndarray):

        # ID
        self.id: int = id

        # name
        self.name: str = name

        # room_id
        self.room_id: int = room_id

        # room_index
        self.room_index: int = _get_room_index(room_id_is=id_r_is, spcf_room_id=room_id)

        # room_indices
        self.id_r_is: np.ndarray[int] = id_r_is

        # number of room
        self.n_rm = len(id_r_is)

        # boundary_id
        self.boundary_id: int | None = boundary_id

        # boundary_index
        self.boundary_index: int | None = _get_boundary_index(boundary_id_js=id_js, spcf_boundary_id=boundary_id) if boundary_id is not None else None

        # boundary indices
        self.id_b_js: np.ndarray[int] = id_js

        # relationship beween rooms and boundaries, [I, J]
        self.p_is_js: np.ndarray[int] = p_is_js

        # equipment
        self.e: IndividualEquipment = e
    
    @classmethod
    def create_for_heating(cls, d: Dict, id_b_js: np.ndarray, connected_room_id_js: np.ndarray, id_r_is: np.ndarray, p_is_js: np.ndarray):

        class HeatingEquipment(Enum):

            RAC = 'rac'
            FLOOR_HEATING = 'floor_heating'

        id = d['id']
        name = d['name']
        prop = d['property']

        match HeatingEquipment(d['equipment_type']):

            case HeatingEquipment.RAC:

                room_id = prop['space_id']

                boundary_id = None

                e = RAC_HC.create_for_heating(d=d)

            case HeatingEquipment.FLOOR_HEATING:

                boundary_id = prop['boundary_id']

                boundary_index = _get_boundary_index(boundary_id_js=id_b_js, spcf_boundary_id=boundary_id)
                
                room_id = connected_room_id_js.flatten()[boundary_index]

                e = Floor_HC.create_for_heating(d=d)

            case _:
                raise Exception()

        return Individual(id=id, name=name, room_id=room_id, boundary_id=boundary_id, e=e, id_r_is=id_r_is, id_js=id_b_js, p_is_js=p_is_js)
    
    @classmethod
    def create_for_cooling(cls, d: Dict, id_b_js: np.ndarray, connected_room_id_js: np.ndarray, id_r_is: np.ndarray, p_is_js: np.ndarray):

        class CoolingEquipment(Enum):

            RAC = 'rac'
            FLOOR_COOLING = 'floor_cooling'

        id = d['id']
        name = d['name']
        prop = d['property']

        match CoolingEquipment(d['equipment_type']):
            
            case CoolingEquipment.RAC:

                room_id = prop['space_id']

                boundary_id = None

                e = RAC_HC.create_for_cooling(d=d)

            case CoolingEquipment.FLOOR_COOLING:
                
                boundary_id = prop['boundary_id']

                boundary_index = _get_boundary_index(boundary_id_js=id_b_js, spcf_boundary_id=boundary_id)
                
                room_id = connected_room_id_js.flatten()[boundary_index]

                e = Floor_HC.create_for_cooling(d=d)
            
            case _:
                raise Exception

        return Individual(id=id, name=name, room_id=room_id, boundary_id=boundary_id, e=e, id_r_is=id_r_is, id_js=id_b_js, p_is_js=p_is_js)
    
    def get_is_radiative_is(self) -> np.ndarray:
        """Get bool type indices which the radiative heating or cooling exists.

        Returns:
            matrix of room which radiative heating or cooling is equipped in., [I, 1]
        """

        if self.e.is_radiative:
        
            is_radiative_js = np.full_like(a=self.id_b_js, fill_value=False, dtype=bool)
        
            is_radiative_js[self.boundary_index, 0] = True
        
            return np.dot(self.p_is_js, is_radiative_js)
        
        else:

            is_radiative_is = np.full_like(a=self.id_r_is, fill_value=False, dtype=bool)
        
            is_radiative_is[self.room_index, 0] = self.e.is_radiative

            return is_radiative_is

    def get_q_rs_max_is(self) -> np.ndarray:
        """Get maximum capacity of radiative heating or cooling.

        Returns:
            matrix of maximum capacity of radiative heating or cooling, W, [I, 1]
        """

        q_rs_max_is = np.zeros_like(a=self.id_r_is, dtype=float)
        
        q_rs_max_is[self.room_index, 0] = self.e.q_rs_max

        return q_rs_max_is

    def get_f_beta_eqp_is(self) -> np.ndarray:
        """Get the convective heat ratio of radiative heating or cooling.

        Returns:
            convective heat ratio of radiative heating or cooling, -, [I, 1]
        """

        f_beta_eqp_is = np.zeros_like(a=self.id_r_is, dtype=float)

        f_beta_eqp_is[self.room_index, 0] = self.e.f_beta_eqp

        return f_beta_eqp_is

    def get_f_flr_js(self) -> np.ndarray:
        """Get the absoption ratio of the inside room surface of boundary to radiative heat flow from the radiative heating or cooling.

        Returns:
            absorption ratio of inside room surface of boundary j to radiative heat flow from radiative heating or cooling in room i, -, [J, 1]
        """

        f_flr_js = np.zeros_like(a=self.id_b_js, dtype=float)

        if self.e.is_radiative:
            f_flr_js[self.boundary_index, 0] = 1.0
            return f_flr_js
        else:
            return f_flr_js

    def get_f_l_is_n(self, q_s_is_n: np.ndarray, theta_r_is_n_pls: np.ndarray, x_r_ntr_is_n_pls: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:

        q_s_i_n = q_s_is_n[self.room_index, 0]
        theta_r_i_n_pls = theta_r_is_n_pls[self.room_index, 0]
        x_r_ntr_i_n_pls = x_r_ntr_is_n_pls[self.room_index, 0]

        brmx_rac_is, brcx_rac_is = self.e.get_f_l_cl(q_s=q_s_i_n, theta_r=theta_r_i_n_pls, x_r=x_r_ntr_i_n_pls)

        f_l_cl_wgt_is_is_n = np.zeros((self.n_rm, self.n_rm), dtype=float)
        f_l_cl_cst_is_n = np.zeros((self.n_rm, 1), dtype=float)

        f_l_cl_wgt_is_is_n[self.room_index, self.room_index] = brmx_rac_is
        f_l_cl_cst_is_n[self.room_index, 0] = brcx_rac_is

        return f_l_cl_wgt_is_is_n, f_l_cl_cst_is_n
        


@dataclass
class IndividualEquipment(ABC):

    @property
    @abstractmethod
    def is_radiative(self) -> bool:
        """is radiative ?"""
        ...

    @property
    @abstractmethod
    def q_rs_max(self) -> float:
        """maximum capacity of radiative heating or cooling, W"""
        ...

    @property
    @abstractmethod
    def f_beta_eqp(self) -> float:
        """convective heat ratio of radiative heating or cooling, -"""
        ...

    @abstractmethod
    def get_f_l_cl(self, q_s: float, theta_r: float, x_r: float) -> Tuple[float, float]:
        """get parameters of constant and weighted for f_l_cl function.

        Args:
            q_s: sensitive heat load.
            theta_r: room temperature.
        """
        ...


@dataclass
class RAC_HC(IndividualEquipment, ABC):

    # minimum heating or cooling capacity, W
    q_min: float

    # maximum heating or cooling capacity, W
    q_max: float

    # minimum air flow volume, m3/min
    v_min: float

    # maximum air flow volume, m3/min
    v_max: float

    # bypass factor, -
    bf: float

    @classmethod
    def _read(cls, d:Dict):

        prop = d['property']

        q_min = float(prop['q_min'])
        q_max = float(prop['q_max'])
        v_min = float(prop['v_min'])
        v_max = float(prop['v_max'])
        bf = float(prop['bf'])

        return q_min, q_max, v_min, v_max, bf

    @classmethod
    def create_for_heating(cls, d:Dict):

        q_min, q_max, v_min, v_max, bf = cls._read(d=d)

        return RAC_H(
            q_min=q_min,
            q_max=q_max,
            v_min=v_min,
            v_max=v_max,
            bf=bf
        )
    
    @classmethod
    def create_for_cooling(cls, d:Dict):

        q_min, q_max, v_min, v_max, bf = cls._read(d=d)

        return RAC_C(
            q_min=q_min,
            q_max=q_max,
            v_min=v_min,
            v_max=v_max,
            bf=bf
        )

    @property
    def is_radiative(self) -> bool:
        """is radiative ?"""
        return False

    @property
    def q_rs_max(self) -> float:
        """maximum capacity of radiative heating or cooling, W"""
        return 0.0

    @property
    def f_beta_eqp(self) -> float:
        """convective heat ratio of radiative heating or cooling, -"""
        return 0.0

    def get_v(self, q_s: float) -> float:
        """Calculate the air flow rate.

        Args:
            q_s: sensitive heat load, W (Both heating and cooling load should be positive.)

        Returns:
            air flow rate, m3/s

        Notes:
            繰り返し計算（湿度と潜熱） eq.14

            Although the rated maximum and minimum capacities are total heat capacities,
            the values measured by the current test method are almost entirely dominated by sensible heat load.
            Therefore, we will calculate the airflow rate based on the sensible heat load.
        """

        # maximum air flow rate, m3/s
        v_max_per_sec = self.v_max / 60.0

        # minimum air flow rate, m3/s
        v_min_per_sec = self.v_min / 60.0

        # maximum capacity, W
        q_max = self.q_max

        # minimum capacity, W
        q_min = self.q_min

        # air flow rate without upper and lower limitation, m3/s
        v2 = v_min_per_sec * (q_max - q_s) / (q_max - q_min) + v_max_per_sec * (q_min - q_s) / (q_min - q_max)

        # air flow rate, m3/s
        v = np.clip(v2, a_min=v_min_per_sec, a_max=v_max_per_sec)

        return v

    @abstractmethod
    def get_f_l_cl(self, q_s: float, theta_r: float, x_r: float) -> Tuple[float, float]:
        ...


@dataclass
class RAC_H(RAC_HC):

    def get_f_l_cl(self, q_s: float, theta_r: float, x_r: float) -> Tuple[float, float]:
        """get parameters of constant and weighted for f_l_cl function.

        Args:
            q_s: sensitive heat load.
            theta_r: room temperature.
        """
        raise NotImplementedError


@dataclass
class RAC_C(RAC_HC):

    def get_f_l_cl(self, q_s: float, theta_r: float, x_r: float) -> Tuple[float, float]:
        """get parameters of constant and weighted for f_l_cl function.

        Args:
            q_s: sensitive heat load.
            theta_r: room temperature.
        """

        # air flow rate, m3/s
        v = self.get_v(q_s=q_s)

        # surface temperature of internal heat exchanger unit, deg. C
        theta_ex_srf = self._get_theta_ex_srf(q_s=q_s, theta_r=theta_r, v=v)

        # absolute humidity of internal heat exchanger unit, kg/kg(DA)
        x_ex_srf = get_x(get_p_vs(theta_ex_srf))

        if (x_r > x_ex_srf) & (q_s > 0.0):
            f_l_cl_wgt = get_rho_a() * v * (1 - self.bf)
            f_l_cl_cst = get_rho_a() * v * (1 - self.bf) * x_ex_srf
        else:
            f_l_cl_wgt = 0.0
            f_l_cl_cst = 0.0

        return f_l_cl_wgt, f_l_cl_cst

    def _get_theta_ex_srf(self, q_s: float, theta_r: float, v: float) -> float:
        """Calculate the surface temperature of internal heat exchange unit of RAC.
        
        Args:
            q_s: sensitive heat load, W
            theta_r: room temperature, degree C
            v: air flow rate, m3/s
        
        Returns:
            surface temperature of internal heat exchange unit, deg. C
        
        Notes:
            繰り返し計算（温度と湿度） eq.14

        """

        return theta_r - q_s / (get_c_a() * get_rho_a() * v * (1.0 - self.bf))


@dataclass
class Floor_HC(IndividualEquipment, ABC):

    # heating or cooling capacity per area, W/m2
    max_capacity: float

    # area, m2
    area: float

    # ratio of convective heat flow to sum of convective and radiative heat flow, -
    convection_ratio: float

    @classmethod
    def _read(cls, d: Dict):
        
        prop: Dict = d['property']

        max_capacity = float(prop['max_capacity'])
        area = float(prop['area'])
        convection_ratio = float(prop['convection_ratio'])

        return max_capacity, area, convection_ratio

    @classmethod
    def create_for_heating(cls, d: Dict):

        max_capacity, area, convection_ratio = cls._read(d=d)

        return Floor_H(
            max_capacity=max_capacity,
            area=area,
            convection_ratio=convection_ratio
        )

    @classmethod
    def create_for_cooling(cls, d:Dict):

        max_capacity, area, convection_ratio = cls._read(d=d)

        return Floor_C(
            max_capacity=max_capacity,
            area=area,
            convection_ratio=convection_ratio
        )

    @property        
    def is_radiative(self) -> bool:
        """is radiative ?"""
        return True

    @property
    def q_rs_max(self) -> float:
        """maximum capacity of radiative heating or cooling, W"""
        return self.max_capacity * self.area

    @property
    def f_beta_eqp(self) -> float:
        """convective heat ratio of radiative heating or cooling, -"""
        return self.convection_ratio

    def get_f_l_cl(self, q_s: float, theta_r: float, x_r: float) -> Tuple[float, float]:
        """get parameters of constant and weighted for f_l_cl function.

        Args:
            q_s: sensitive heat load.
            theta_r: room temperature.
        """
        raise NotImplementedError


@dataclass
class Floor_H(Floor_HC):

    ...
    
@dataclass
class Floor_C(Floor_HC):

    ...


class Equipments:

    def __init__(self, d: Dict, id_r_is: np.ndarray, id_b_js: np.ndarray, connected_room_id_js: np.ndarray, p_is_js: np.ndarray):
        """設備に関する情報を辞書形式で受け取り、データクラスに変換して保持する。
        暖房・冷房それぞれにおいて、
        辞書の中の "equipment_type" の種類に応じて対応するデータクラスを生成する。

        Args:
            d: dictionary of equipments spec / 設備の情報が記された辞書
            id_r_is: room ID, [I, 1]
            id_b_js: boundary ID, [J, 1]

        """
        
        if 'heating_equipments' in d:
            hes = [
                Individual.create_for_heating(d=d_he, id_b_js=id_b_js, connected_room_id_js=connected_room_id_js, id_r_is=id_r_is, p_is_js=p_is_js)
                for d_he in d['heating_equipments']
            ]
        else:
            raise KeyError("Can't find the heating_equipments key in equipments dictionary.")

        if 'cooling_equipments' in d:
            ces = [
                Individual.create_for_cooling(d=d_ce, id_b_js=id_b_js, connected_room_id_js=connected_room_id_js, id_r_is=id_r_is, p_is_js=p_is_js)
                for d_ce in d['cooling_equipments']
            ]
        else:
            raise KeyError("Can't find the cooling_equipments key in equipments dictionary.")

        self._hes = hes
        self._ces = ces

        is_radiative_heating_ks_is = _get_is_radiative_ks_is(es=hes)
        is_radiative_cooling_ks_is = _get_is_radiative_ks_is(es=ces)

        is_radiative_heating_count_is = np.count_nonzero(a=is_radiative_heating_ks_is, axis=0)
        is_radiative_cooling_count_is = np.count_nonzero(a=is_radiative_cooling_ks_is, axis=0)

        if(np.any(is_radiative_heating_count_is > 1)):
            raise Exception("Multiple radiative heating are installed in one room.")
        
        if(np.any(is_radiative_cooling_count_is > 1)):
            raise Exception("Multiple radiative cooling are installed in one room.")

        self._is_radiative_heating_is = np.any(a=is_radiative_heating_ks_is, axis=0)
        self._is_radiative_cooling_is = np.any(a=is_radiative_cooling_ks_is, axis=0)

        self._q_rs_h_max_is = _get_q_rs_max_is(es=hes)
        self._q_rs_c_max_is = _get_q_rs_max_is(es=ces)

        self._beta_h_is = _get_beta_is(es=hes)
        self._beta_c_is = _get_beta_is(es=ces)

        self._f_flr_h_js_is = _get_f_flr_js_is(es=hes, p_is_js=p_is_js)
        self._f_flr_c_js_is = _get_f_flr_js_is(es=ces, p_is_js=p_is_js)

    @property
    def is_radiative_heating_is(self) -> np.ndarray:
        """室iの暖房方式として放射空調が設置されているかどうか, bool値, [i, 1]"""
        return self._is_radiative_heating_is

    @property
    def is_radiative_cooling_is(self) -> np.ndarray:
        """室iの冷房方式として放射空調が設置されているかどうか, bool値, [i, 1]"""
        return self._is_radiative_cooling_is

    @property
    def q_rs_h_max_is(self) -> np.ndarray:
        """室iの暖房方式として放射空調が設置されている場合の、放射暖房最大能力, W, [i, 1]"""
        return self._q_rs_h_max_is

    @property
    def q_rs_c_max_is(self) -> np.ndarray:
        """室iの冷房方式として放射空調が設置されている場合の、放射冷房最大能力, W, [i, 1]"""
        return self._q_rs_c_max_is

    @property
    def beta_h_is(self) -> np.ndarray:
        """室iの放射暖房設備の対流成分比率, -, [i, 1]"""
        return self._beta_h_is

    @property
    def beta_c_is(self) -> np.ndarray:
        """室iの放射冷房設備の対流成分比率, -, [i, 1]"""
        return self._beta_c_is

    @property
    def f_flr_h_js_is(self) -> np.ndarray:
        """室iの放射暖房の放熱量の放射成分に対する境界jの室内側表面の吸収比率, - [j, i]"""
        return self._f_flr_h_js_is

    @property
    def f_flr_c_js_is(self) -> np.ndarray:
        """室iの放射冷房の吸熱量の放射成分に対する境界jの室内側表面の放熱比率, - [j, i]"""
        return self._f_flr_c_js_is

    def get_f_l_cl(
        self,
        l_cs_is_n: np.ndarray,
        theta_r_is_n_pls: np.ndarray,
        x_r_ntr_is_n_pls: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """

        Args:
            l_cs_is_n: ステップ n からステップ n+1 における室 i の暖冷房設備の顕熱処理量（暖房を正・冷房を負とする）, W, [i, 1]
            theta_r_is_n_pls: ステップ n+1 における室 i の温度, degree C, [i, 1]
            x_r_ntr_is_n_pls: ステップ n+1 における室 i の加湿・除湿を行わない場合の絶対湿度, kg/kg(DA), [i, 1]

        Returns:
            タプル
                ステップ n　からステップ n+1 における係数 f_l_cl_wgt, kg/s(kg/kg(DA)), [i, i]
                ステップ n　からステップ n+1 における係数 f_l_cl_cst, kg/s, [i, 1]
        """

        q_s_is_n = -l_cs_is_n

        ls = [
            ce.get_f_l_is_n(
                q_s_is_n=q_s_is_n,
                theta_r_is_n_pls=theta_r_is_n_pls,
                x_r_ntr_is_n_pls=x_r_ntr_is_n_pls
            )
            for ce in self._ces
        ]

        # 係数 la と 係数 lb をタプルから別々に取り出す。
        ls_a = np.array([l[0] for l in ls])
        ls_b = np.array([l[1] for l in ls])
        # 係数 la 及び lb それぞれ合計する。
        # la [i,i] kg/s(kg/kg(DA))
        # lb [i,1] kg/kg(DA)
        # TODO: La は正負が仕様書と逆になっている
        f_l_cl_wgt_is_is_n = - ls_a.sum(axis=0)
        f_l_cl_cst_is_n = ls_b.sum(axis=0)
        return f_l_cl_cst_is_n, f_l_cl_wgt_is_is_n


def _get_boundary_index(boundary_id_js: np.ndarray, spcf_boundary_id: int) -> int:
    """Find the boundary index corresponding to the boundary id.

    Args:
        boundary_id_js: boundary id, [J, 1]
        spcf_boundary_id: specified boundary id

    Returns:
        boundary index
    """

    return _get_index_by_id(id_list=list(boundary_id_js.flatten()), searching_id=spcf_boundary_id)


def _get_room_index(room_id_is: np.ndarray, spcf_room_id: int) -> int:
    """Find the room index corresponding to the room id.

    Args:
        room_id_is: room id, [I, 1]
        spcf_room_id: specified room id

    Returns:
        room index
    """

    return _get_index_by_id(id_list=list(room_id_is.flatten()), searching_id=spcf_room_id)


def _get_index_by_id(id_list: List, searching_id: int) -> int:

    indices = [i for (i, id) in enumerate(id_list) if id == searching_id]

    if len(indices) == 0:
        raise Exception("指定された id に一致するものが見つかりませんでした。")
    if len(indices) >1:
        raise Exception("指定された id に一致するものが複数見つかりました。")
    
    return indices[0]


def _get_is_radiative_ks_is(es: List[Individual]) -> np.ndarray:
    """Get bool type indices which the radiative heating or cooling exists.

    Args:
        es: list of Individual class, [K]

    Returns:
        matrix of room which radiative heating or cooling is equipped in., [K, I, 1]
    """

    return np.stack([e.get_is_radiative_is() for e in es])


def _get_q_rs_max_is(es: List[Individual]) -> np.ndarray:
    """Get maximum capacity of radiative heating or cooling.

    Args:
        es: list of Individual class, [K]

    Returns:
        maximum capacity of radiative heating or cooling, W, [I, 1]
    """

    q_rs_max_ks_is = np.stack([e.get_q_rs_max_is() for e in es])

    return np.sum(a=q_rs_max_ks_is, axis=0)


def _get_beta_is(es: List[Individual]) -> np.ndarray:
    """Get convective heat ratio of radiative heating or cooling.

    Args:
        es: list of Equipment class, [K]
        id_r_is: room id, [I, 1]

    Returns:
        convective heat ratio of radiative heating or cooling, -, [I, 1]
    """

    f_beta_eqp_ks_is = np.stack([e.get_f_beta_eqp_is() for e in es])

    return np.sum(f_beta_eqp_ks_is, axis=0)


def _get_f_flr_js_is(es: List[Individual], p_is_js: np.ndarray) -> np.ndarray:
    """Get the absorption ratio of inside surface of boundary to the radiative heat flow from the radiative heating or cooling in the room.

    Args:
        es: list of Equipment class, [K]
        p_is_js: matrix representing relationship between room i and boundary j, [I, J]

    Returns:
        absorption ratio of inside surface of boundary j to radiative heat flow from radiative heating or cooling in room i, -, [J, I]
    """

    # [K, J, 1]
    f_flr_ks_js = np.stack([e.get_f_flr_js() for e in es])

    # [J, 1]
    f_flr_js = f_flr_ks_js.sum(axis=0)

    # [J, I]
    return f_flr_js * p_is_js.T

