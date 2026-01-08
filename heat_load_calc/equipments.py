from typing import Callable, Dict, Tuple, List
from typing import Union
import numpy as np
from dataclasses import dataclass
from enum import Enum
from abc import ABC

from heat_load_calc import boundaries
from heat_load_calc.psychrometrics import get_x, get_p_vs
from heat_load_calc.global_number import get_c_a, get_rho_a
from heat_load_calc.matrix_method import v_diag


class HeatingEquipment(Enum):

    RAC = 'rac'
    FLOOR_HEATING = 'floor_heating'


class CoolingEquipment(Enum):

    RAC = 'rac'
    FLOOR_COOLING = 'floor_cooling'


@dataclass
class Equipment(ABC):

    # ID
    id: int

    # name
    name: str


@dataclass
class RAC_HC(Equipment, ABC):

    # room id which is heated or cooled by this RAC
    room_id: int

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
    def create_rac_hc(cls, d:Dict):

        prop = d['property']

        return RAC_HC(
            id=d['id'],
            name=d['name'],
            room_id=prop['space_id'],
            q_min=prop['q_min'],
            q_max=prop['q_max'],
            v_min=prop['v_min'],
            v_max=prop['v_max'],
            bf=prop['bf']
        )


@dataclass
class Floor_HC(Equipment, ABC):

    # id of the room which this radiative heating or cooling is equipped in.
    room_id: int

    # boundary id which radiative heating or cooling set at.
    boundary_id: int

    # heating or cooling capacity per area, W/m2
    max_capacity: float

    # area, m2
    area: float

    # ratio of convective heat flow to sum of convective and radiative heat flow, -
    convection_ratio: float

    @classmethod
    def create_floor_hc(cls, d: Dict, id_js: np.ndarray, connected_room_id_js: np.ndarray):
        
        prop = d['property']

        boundary_id = prop['boundary_id']
        boundary_index = _get_index_by_id(id_list=list(id_js.flatten()), searching_id=boundary_id)
        room_id = connected_room_id_js.flatten()[boundary_index]

        instance = Floor_HC(
            id=d['id'],
            name=d['name'],
            room_id=room_id,
            boundary_id=boundary_id,
            max_capacity=prop['max_capacity'],
            area=prop['area'],
            convection_ratio=prop['convection_ratio']
        )

        return instance
        
    def room_index(self, id_r_is: np.ndarray[int]) -> int:
        """Get the room index of the room which this raddiative heating or cooling is equipped in.

            Args:
                id_r_is: room indices, [I, 1]
            Returns:
                index number
        """

        return _get_index_by_id(id_list=list(id_r_is.flatten()), searching_id=self.room_id)


@dataclass
class RAC_H(RAC_HC):

    @classmethod
    def create_rac_h(cls, d:Dict):

        e = RAC_HC.create_rac_hc(d=d)

        return RAC_H(
            id=e.id,
            name=e.name,
            room_id=e.room_id,
            q_min=e.q_min,
            q_max=e.q_max,
            v_min=e.v_min,
            v_max=e.v_max,
            bf=e.bf
        )


@dataclass
class Floor_H(Floor_HC):
    
    @classmethod
    def create_floor_h(cls, d: Dict, id_js: np.ndarray, connected_room_id_js: np.ndarray):

        e = Floor_HC.create_floor_hc(d=d, id_js=id_js, connected_room_id_js=connected_room_id_js)

        return Floor_H(
            e.id,
            name=e.name,
            room_id=e.room_id,
            boundary_id=e.boundary_id,
            max_capacity=e.max_capacity,
            area=e.area,
            convection_ratio=e.convection_ratio
        )


@dataclass
class RAC_C(RAC_HC):

    @classmethod
    def create_rac_c(cls, d:Dict):

        e = RAC_HC.create_rac_hc(d=d)

        return RAC_C(
            id=e.id,
            name=e.name,
            room_id=e.room_id,
            q_min=e.q_min,
            q_max=e.q_max,
            v_min=e.v_min,
            v_max=e.v_max,
            bf=e.bf
        )


@dataclass
class Floor_C(Floor_HC):

    @classmethod
    def create_floor_c(cls, d:Dict, id_js: np.ndarray, connected_room_id_js: np.ndarray):

        e = Floor_HC.create_floor_hc(d=d, id_js=id_js, connected_room_id_js=connected_room_id_js)

        return Floor_C(
            id=e.id,
            name=e.name,
            room_id=e.room_id,
            boundary_id=e.boundary_id,
            max_capacity=e.max_capacity,
            area=e.area,
            convection_ratio=e.convection_ratio
        )


class Equipments:

    def __init__(self, d: Dict, n_rm: int, n_b: int, bs: boundaries.Boundaries, id_r_is: np.ndarray):
        """設備に関する情報を辞書形式で受け取り、データクラスに変換して保持する。
        暖房・冷房それぞれにおいて、
        辞書の中の "equipment_type" の種類に応じて対応するデータクラスを生成する。

        Args:
            ds: dictionary of equipments spec / 設備の情報が記された辞書
            n_rm: number of rooms / 部屋の数
            n_b: number of boundaries / 境界の数
            bs: Boundaries class

        Notes:
            ここで Boundaries クラスは、境界IDと室IDとの対応関係を見ることだけに使用される。
            放射暖冷房に関する設備情報には対応する境界IDしか記されていない。
            一方で、放射暖冷房においても、beta, f_flr の係数を計算する際には、
            その放射暖冷房がどの室に属しているのかの情報が必要になるため、
            Equipments を initialize する際に、あらかじめ放射暖冷房にも room_id を付与しておくこととする。
        """

        if 'heating_equipments' in d:
            hes = [
                _create_heating_equipment(d_he=d_he, id_js=bs.id_js, connected_room_id_js=bs.connected_room_id_js)
                for d_he in d['heating_equipments']
            ]
        else:
            raise KeyError("Can't find the heating_equipments key in equipments dictionary.")

        if 'cooling_equipments' in d:
            ces = [
                _create_cooling_equipment(d_ce=d_ce, id_js=bs.id_js, connected_room_id_js=bs.connected_room_id_js)
                for d_ce in d['cooling_equipments']
            ]
        else:
            raise KeyError("Can't find the cooling_equipments key in equipments dictionary.")

        self._hes = hes
        self._ces = ces

        self._is_radiative_heating_is = _get_is_radiative_is(es=hes, id_r_is=id_r_is)
        self._is_radiative_cooling_is = _get_is_radiative_is(es=ces, id_r_is=id_r_is)
        self._q_rs_h_max_is = self._get_q_rs_max_is(es=hes, id_r_is=id_r_is)
        self._q_rs_c_max_is = self._get_q_rs_max_is(es=ces, id_r_is=id_r_is)
        self._beta_h_is = self._get_beta_is(es=hes, n_rm=n_rm, id_r_is=id_r_is)
        self._beta_c_is = self._get_beta_is(es=ces, n_rm=n_rm, id_r_is=id_r_is)
        self._f_flr_h_js_is = self._get_f_flr_js_is(es=hes, n_rm=n_rm, n_b=n_b, id_r_is=id_r_is)
        self._f_flr_c_js_is = self._get_f_flr_js_is(es=ces, n_rm=n_rm, n_b=n_b, id_r_is=id_r_is)

        self._n_rm = n_rm
        self._n_b = n_b

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

    def _get_q_rs_max_is(self, es, id_r_is: np.ndarray):

        q_rs_max_is = np.zeros_like(a=id_r_is, dtype=float)

        for e in es:
            if type(e) in [Floor_H, Floor_C]:

                er: Floor_HC = e

                index = er.room_index(id_r_is=id_r_is)

                q_rs_max_is[index, 0] = q_rs_max_is[index, 0] + e.max_capacity * e.area

        return q_rs_max_is

    def _get_beta_is(self, es, n_rm, id_r_is: np.ndarray):

        f_beta_eqp_ks_is = self._get_f_beta_eqp_ks_is(es=es, n_rm=n_rm, id_r_is=id_r_is)
        r_max_ks_is = self._get_r_max_ks_is(es=es, n_rm=n_rm, id_r_is=id_r_is)

        return np.sum(f_beta_eqp_ks_is * r_max_ks_is, axis=0).reshape(-1, 1)

    def _get_p_ks_is(self, es, n_rm, id_r_is: np.ndarray):

        n_rm = id_r_is.shape[0]
        p_ks_is = np.zeros(shape=(len(es), n_rm), dtype=float)

        for k, e in enumerate(es):
            if type(e) in [Floor_H, Floor_C]:
                index = _get_index_by_id(id_list=list(id_r_is.flatten()), searching_id=e.room_id)
                p_ks_is[k, index] = 1.0

        return p_ks_is

    @staticmethod
    def _get_f_beta_eqp_ks_is(es, n_rm, id_r_is: np.ndarray):

        n_rm = id_r_is.shape[0]

        f_beta_eqp_ks_is = np.zeros(shape=(len(es), n_rm), dtype=float)

        for k, e in enumerate(es):
            if type(e) in [Floor_H, Floor_C]:
                index = _get_index_by_id(id_list=list(id_r_is.flatten()), searching_id=e.room_id)
                f_beta_eqp_ks_is[k, index] = e.convection_ratio

        return f_beta_eqp_ks_is

    @staticmethod
    def _get_r_max_ks_is(es, n_rm, id_r_is: np.ndarray):

        n_rm = id_r_is.shape[0]
        q_max_ks_is = np.zeros(shape=(len(es), n_rm), dtype=float)

        for k, e in enumerate(es):
            if type(e) in [Floor_H, Floor_C]:
                index = _get_index_by_id(id_list=list(id_r_is.flatten()), searching_id=e.room_id)
                q_max_ks_is[k, index] = e.max_capacity * e.area

        sum_of_q_max_is = q_max_ks_is.sum(axis=0)

        # 各室の放熱量の合計値がゼロだった場合、次の式のゼロ割を防ぐためにダミーの数字1.0を代入する。
        # この場合、次の式の分子の数はゼロであるため、結果として 0.0/1.0 = 0.0 となり、結果には影響を及ぼさない。
        sum_of_q_max_is[np.where(sum_of_q_max_is == 0.0)] = 1.0

        return q_max_ks_is / sum_of_q_max_is

    @property
    def f_flr_h_js_is(self) -> np.ndarray:
        """室iの放射暖房の放熱量の放射成分に対する境界jの室内側表面の吸収比率, - [j, i]"""
        return self._f_flr_h_js_is

    @property
    def f_flr_c_js_is(self) -> np.ndarray:
        """室iの放射冷房の吸熱量の放射成分に対する境界jの室内側表面の放熱比率, - [j, i]"""
        return self._f_flr_c_js_is

    def _get_f_flr_js_is(self, es, n_rm, n_b, id_r_is: np.ndarray):

        f_flr_eqp_js_ks = self._get_f_flr_eqp_js_ks(es=es, n_b=n_b, id_r_is=id_r_is)
        f_beta_eqp_ks_is = self._get_f_beta_eqp_ks_is(es=es, n_rm=n_rm, id_r_is=id_r_is)
        r_max_ks_is = self._get_r_max_ks_is(es=es, n_rm=n_rm, id_r_is=id_r_is)
        beta_is = self._get_beta_is(es=es, n_rm=n_rm, id_r_is=id_r_is)
        p_ks_is = self._get_p_ks_is(es=es, n_rm=n_rm, id_r_is=id_r_is)

        return np.dot(np.dot(f_flr_eqp_js_ks, (p_ks_is - f_beta_eqp_ks_is) * r_max_ks_is), v_diag(1 / (1 - beta_is)))

    def _get_f_flr_eqp_js_ks(self, es, n_b, id_r_is:np.ndarray):

        f_flr_eqp_js_ks = np.zeros(shape=(n_b, len(es)), dtype=float)

        for k, e in enumerate(es):


            if type(e) in [Floor_H, Floor_C]:
                #TODO ここもidからboundaryのindexへの変換をしないといけないかもしれない。
                f_flr_eqp_js_ks[e.boundary_id, k] = e.convection_ratio

        return f_flr_eqp_js_ks

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

        ls = [
            self._get_ls_a_ls_b(
                l_cs_is_n=l_cs_is_n,
                theta_r_is_n_pls=theta_r_is_n_pls,
                x_r_ntr_is_n_pls=x_r_ntr_is_n_pls,
                ce=ce
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


    def _get_ls_a_ls_b(
        self,
        l_cs_is_n: np.ndarray,
        theta_r_is_n_pls: np.ndarray,
        x_r_ntr_is_n_pls: np.ndarray,
        ce: RAC_C
    ) -> Tuple[np.ndarray, np.ndarray]:

        if type(ce) is RAC_C:
            return self._func_rac(
                l_cs_is_n=l_cs_is_n,
                theta_r_is_n_pls=theta_r_is_n_pls,
                x_r_ntr_is_n_pls=x_r_ntr_is_n_pls,
                ce=ce
            )
        elif type(ce) is Floor_C:
            raise NotImplementedError
        else:
            raise Exception

    def _func_rac(
            self,
            l_cs_is_n: np.ndarray,
            theta_r_is_n_pls: np.ndarray,
            x_r_ntr_is_n_pls: np.ndarray,
            ce: RAC_C
    ) -> Tuple[np.ndarray, np.ndarray]:

        # 室の数
        n_rm = self._n_rm

        # Lcsは加熱が正で表される。
        # 加熱時は除湿しない。
        # 以下の取り扱いを簡単にするため（冷房負荷を正とするため）、正負を反転させる
        q_s_is_n = -l_cs_is_n

        q_s_i_n = q_s_is_n[ce.room_id, 0]
        theta_r_i_n_pls = theta_r_is_n_pls[ce.room_id, 0]
        x_r_ntr_i_n_pls = x_r_ntr_is_n_pls[ce.room_id, 0]

        v_rac_i_n = self._get_vac_rac_i_n(
            q_rac_max_i=ce.q_max,
            q_rac_min_i=ce.q_min,
            q_s_i_n=q_s_i_n,
            v_rac_max_i=ce.v_max / 60,
            v_rac_min_i=ce.v_min / 60
        )

        theta_rac_ex_srf_i_n_pls = self._get_theta_rac_ex_srf_i_n_pls(
            bf_rac_i=ce.bf,
            q_s_i_n=q_s_i_n,
            theta_r_i_n_pls=theta_r_i_n_pls,
            v_rac_i_n=v_rac_i_n
        )

        x_rac_ex_srf_i_n_pls = self._get_x_rac_ex_srf_i_n_pls(theta_rac_ex_srf_i_n_pls=theta_rac_ex_srf_i_n_pls)

        brmx_rac_is = np.where(
            (x_r_ntr_i_n_pls > x_rac_ex_srf_i_n_pls) & (q_s_i_n > 0.0),
            get_rho_a() * v_rac_i_n * (1 - ce.bf),
            0.0
        )

        brcx_rac_is = np.where(
            (x_r_ntr_i_n_pls > x_rac_ex_srf_i_n_pls) & (q_s_i_n > 0.0),
            get_rho_a() * v_rac_i_n * (1 - ce.bf) * x_rac_ex_srf_i_n_pls,
            0.0
        )

        brmx_is_is = np.zeros((n_rm, n_rm), dtype=float)
        brxc_is = np.zeros((n_rm, 1), dtype=float)

        brmx_is_is[ce.room_id, ce.room_id] = brmx_rac_is
        brxc_is[ce.room_id, 0] = brcx_rac_is

        return brmx_is_is, brxc_is

    @staticmethod
    def _get_x_rac_ex_srf_i_n_pls(theta_rac_ex_srf_i_n_pls: float) -> float:
        """
        ルームエアコンディショナーの室内機の熱交換器表面の絶対湿度を求める。
        Args:
            theta_rac_ex_srf_i_n_pls: ステップ n+1 における室 i に設置されたルームエアコンディショナーの室内機の熱交換器表面温度,degree C
        Returns:
            ステップ n+1 における室 i に設置されたルームエアコンディショナーの室内機の熱交換器表面の絶対湿度, kg/kg(DA)
        Notes:
            繰り返し計算（温度と湿度） eq.12
        """

        return get_x(get_p_vs(theta_rac_ex_srf_i_n_pls))

    @staticmethod
    def _get_theta_rac_ex_srf_i_n_pls(
            bf_rac_i: float,
            q_s_i_n: float,
            theta_r_i_n_pls: float,
            v_rac_i_n: float
    ) -> float:
        """
        ステップ n+1 における室 i に設置されたルームエアコンディショナーの室内機の熱交換器表面温度を計算する。
        Args:
            bf_rac_i: 室 i に設置されたルームエアコンディショナーの室内機の熱交換器のバイパスファクター, -
            q_s_i_n: ステップ n から n+1 における室 i の顕熱負荷, W
            theta_r_i_n_pls: ステップ n+1 における室 i の温度, degree C
            v_rac_i_n: ステップ n から n+1 における室 i に設置されたルームエアコンディショナーの吹き出し風量, m3/s
        Returns:
            ステップ n+1 における室 i に設置されたルームエアコンディショナーの室内機の熱交換器表面温度, degree C
        Notes:
            繰り返し計算（温度と湿度） eq.14
        """

        return theta_r_i_n_pls - q_s_i_n / (get_c_a() * get_rho_a() * v_rac_i_n * (1.0 - bf_rac_i))

    @staticmethod
    def _get_vac_rac_i_n(
            q_rac_max_i: Union[float, np.ndarray],
            q_rac_min_i: Union[float, np.ndarray],
            q_s_i_n: Union[float, np.ndarray],
            v_rac_max_i: Union[float, np.ndarray],
            v_rac_min_i: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """
        ルームエアコンディショナーの吹き出し風量を顕熱負荷に応じて計算する。

        Args:
            q_rac_max_i: 室 i に設置されたルームエアコンディショナーの最大能力, W
            q_rac_min_i: 室 i に設置されたルームエアコンディショナーの最小能力, W
            q_s_i_n:　ステップ n からステップ n+1 における室 i の顕熱負荷, W
            v_rac_max_i: 室 i に設置されたルームエアコンディショナーの最小能力時における風量, m3/s
            v_rac_min_i: 室 i に設置されたルームエアコンディショナーの最大能力時における風量, m3/s
        Returns:
            室iに設置されたルームエアコンディショナーの吹き出し風量, m3/s
        Notes:
            繰り返し計算（湿度と潜熱） eq.14
        """

        # 吹き出し風量（仮）, m3/s
        v = v_rac_min_i * (q_rac_max_i - q_s_i_n) / (q_rac_max_i - q_rac_min_i)\
            + v_rac_max_i * (q_rac_min_i - q_s_i_n) / (q_rac_min_i - q_rac_max_i)

        # 下限値・上限値でクリップ後の吹き出し風量, m3/s
        v_rac_i_n = np.clip(v, a_min=v_rac_min_i, a_max=v_rac_max_i)

        return v_rac_i_n


def _create_heating_equipment(d_he: Dict, id_js: np.ndarray, connected_room_id_js: np.ndarray):

    he = HeatingEquipment(d_he['equipment_type'])

    match he:

        case HeatingEquipment.RAC:

            return RAC_H.create_rac_h(d=d_he)

        case HeatingEquipment.FLOOR_HEATING:

            return Floor_H.create_floor_h(d=d_he, id_js=id_js, connected_room_id_js=connected_room_id_js)

        case _:
            raise Exception()


def _create_cooling_equipment(d_ce, id_js: np.ndarray, connected_room_id_js: np.ndarray):

    ce = CoolingEquipment(d_ce['equipment_type'])

    match ce:
        
        case CoolingEquipment.RAC:

            return RAC_C.create_rac_c(d=d_ce)

        case CoolingEquipment.FLOOR_COOLING:
            
            return Floor_C.create_floor_c(d=d_ce, id_js=id_js, connected_room_id_js=connected_room_id_js)
        
        case _:
            raise Exception


def _get_index_by_id(id_list: List, searching_id: int) -> int:

    indices = [i for (i, id) in enumerate(id_list) if id == searching_id]

    if len(indices) == 0:
        raise Exception("指定された id に一致するものが見つかりませんでした。")
    if len(indices) >1:
        raise Exception("指定された id に一致するものが複数見つかりました。")
    
    return indices[0]


def _get_is_radiative_is(es, id_r_is: np.ndarray):
    """Get bool type indices which the radiative heating or cooling exists.

    Args:
        id_r_is: room id, [I, 1]

    Returns:
        matrix of room which radiative heating or cooling is equipped in., [I, 1]
    """

    is_radiative_is = np.full_like(a=id_r_is, fill_value=False, dtype=bool)

    for e in es:
        if type(e) in [Floor_H, Floor_C]:
            er: Floor_HC = e
            index = er.room_index(id_r_is=id_r_is)
            is_radiative_is[index, 0] = True

    return is_radiative_is
