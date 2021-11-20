from typing import Dict, List
from typing import Union
import numpy as np
from dataclasses import dataclass

from heat_load_calc.core.boundary_simple import BoundarySimple
from heat_load_calc.core import boundary_simple
from heat_load_calc.external.psychrometrics import get_x, get_p_vs_is2
from heat_load_calc.external.global_number import get_c_a, get_rho_a


@dataclass
class HeatingEquipmentRAC:

    # ID
    id: int

    # 名前
    name: str

    # 暖房する空間のID
    space_id: int

    # 最小暖房能力, W
    q_min: float

    # 最大暖房能力, W
    q_max: float

    # 最小風量, m3/min
    v_min: float

    # 最大風量, m3/min
    v_max: float

    # バイパスファクター
    bf: float


@dataclass
class HeatingEquipmentFloorHeating:

    # ID
    id: int

    # 名前
    name: str

    # 放射暖房が設置される境界の番号
    boundary_id: int

    # 面積あたりの放熱能力, W/m2
    max_capacity: float

    # 面積, m2
    area: float

    # 対流成分比率
    convection_ratio: float


@dataclass
class CoolingEquipmentRAC:

    # ID
    id: int

    # 名前
    name: str

    # 冷房する空間のID
    space_id: int

    # 最小冷房能力, W
    q_min: float

    # 最大冷房能力, W
    q_max: float

    # 最小風量, m3/min
    v_min: float

    # 最大風量, m3/min
    v_max: float

    # バイパスファクター
    bf: float


@dataclass
class CoolingEquipmentFloorCooling:

    # ID
    id: int

    # 名前
    name: str

    # 放射冷房が設置される境界の番号
    boundary_id: int

    # 面積あたりの放熱能力, W/m2
    max_capacity: float

    # 面積, m2
    area: float

    # 対流成分比率
    convection_ratio: float


class Equipments:

    def __init__(self, e: Dict, n_rm: int):

        self._hes = [self._create_heating_equipment(dict_he=he) for he in e['heating_equipments']]
        self._ces = [self._create_cooling_equipment(dict_ce=ce) for ce in e['cooling_equipments']]
        self._n_rm = n_rm

    @staticmethod
    def _create_heating_equipment(dict_he):

        prop = dict_he['property']

        if dict_he['equipment_type'] == 'rac':

            return HeatingEquipmentRAC(
                id=dict_he['id'],
                name=dict_he['name'],
                space_id=prop['space_id'],
                q_min=prop['q_min'],
                q_max=prop['q_max'],
                v_min=prop['v_min'],
                v_max=prop['v_max'],
                bf=prop['bf']
            )

        elif dict_he['equipment_type'] == 'floor_heating':

            return HeatingEquipmentFloorHeating(
                id=dict_he['id'],
                name=dict_he['name'],
                boundary_id=prop['boundary_id'],
                max_capacity=prop['max_capacity'],
                area=prop['area'],
                convection_ratio=prop['convection_ratio']
            )

    @staticmethod
    def _create_cooling_equipment(dict_ce):

        prop = dict_ce['property']

        if dict_ce['equipment_type'] == 'rac':

            return CoolingEquipmentRAC(
                id=dict_ce['id'],
                name=dict_ce['name'],
                space_id=prop['space_id'],
                q_min=prop['q_min'],
                q_max=prop['q_max'],
                v_min=prop['v_min'],
                v_max=prop['v_max'],
                bf=prop['bf']
            )

        elif dict_ce['equipment_type'] == 'floor_cooling':

            return CoolingEquipmentFloorCooling(
                id=dict_ce['id'],
                name=dict_ce['name'],
                boundary_id=prop['boundary_id'],
                max_capacity=prop['max_capacity'],
                area=prop['area'],
                convection_ratio=prop['convection_ratio']
            )

    def get_is_radiative_heating_is(self, bss: List[BoundarySimple]):

        is_radiative_heating_is = np.full(shape=(self._n_rm, 1), fill_value=False)

        for he in self._hes:
            if he is HeatingEquipmentFloorHeating:
                bs = boundary_simple.get_boundary_by_id(bss=bss, boundary_id=he.boundary_id)
                is_radiative_heating_is[bs.connected_room_id, 0] = True

        return is_radiative_heating_is

    def get_is_radiative_cooling_is(self, bss: List[BoundarySimple]):

        is_radiative_cooling_is = np.full(shape=(self._n_rm, 1), fill_value=False)

        for ce in self._ces:
            if ce is CoolingEquipmentFloorCooling:
                bs = boundary_simple.get_boundary_by_id(bss=bss, boundary_id=ce.boundary_id)
                is_radiative_cooling_is[bs.connected_room_id, 0] = True

        return is_radiative_cooling_is

    def get_q_rs_h_max_is(self, bss: List[BoundarySimple]):

        q_rs_h_max_is = np.zeros(shape=(self._n_rm, 1), dtype=float)

        for he in self._hes:
            if he is HeatingEquipmentFloorHeating:
                bs = boundary_simple.get_boundary_by_id(bss=bss, boundary_id=he.boundary_id)
                space_id = bs.connected_room_id
                q_rs_h_max_is[space_id, 0] = q_rs_h_max_is[space_id, 0] + he.max_capacity * he.area

        return q_rs_h_max_is

    def get_q_rs_c_max_is(self, bss: List[BoundarySimple]):

        q_rs_c_max_is = np.zeros(shape=(self._n_rm, 1), dtype=float)

        for ce in self._ces:
            if ce is CoolingEquipmentFloorCooling:
                bs = boundary_simple.get_boundary_by_id(bss=bss, boundary_id=ce.boundary_id)
                space_id = bs.connected_room_id
                q_rs_c_max_is[space_id, 0] = q_rs_c_max_is[space_id, 0] + ce.max_capacity * ce.area

        return q_rs_c_max_is

    def get_f_beta_is(self, bss: List[BoundarySimple]):

        f_beta_eqp_ks_is = self._get_f_beta_eqp_ks_is(bss=bss)
        r_max_ks_is = self._get_r_max_ks_is(bss=bss)

        return np.sum(f_beta_eqp_ks_is * r_max_ks_is, axis=0).reshape(-1, 1)

    def _get_f_beta_eqp_ks_is(self, bss: List[BoundarySimple]):

        f_beta_eqp_ks_is = np.zeros(shape=(len(self._hes), self._n_rm), dtype=float)

        for k, he in enumerate(self._hes):
            if he is HeatingEquipmentFloorHeating:
                bs = boundary_simple.get_boundary_by_id(bss=bss, boundary_id=he.boundary_id)
                space_id = bs.connected_room_id
                f_beta_eqp_ks_is[k, space_id] = he.convection_ratio

        return f_beta_eqp_ks_is

    def _get_r_max_ks_is(self, bss: List[BoundarySimple]):

        q_max_ks_is = np.zeros(shape=(len(self._hes), self._n_rm), dtype=float)

        for k, he in enumerate(self._hes):
            if he is HeatingEquipmentFloorHeating:
                bs = boundary_simple.get_boundary_by_id(bss=bss, boundary_id=he.boundary_id)
                space_id = bs.connected_room_id
                q_max_ks_is[k, space_id] = he.max_capacity * he.area

        sum_of_q_max_is = q_max_ks_is.sum(axis=0)

        # 各室の放熱量の合計値がゼロだった場合、次の式のゼロ割を防ぐためにダミーの数字1.0を代入する。
        # この場合、次の式の分子の数はゼロであるため、結果として 0.0/1.0 = 0.0 となり、結果には影響を及ぼさない。
        sum_of_q_max_is[np.where(sum_of_q_max_is == 0.0)] = 1.0

        return q_max_ks_is / sum_of_q_max_is

    @staticmethod
    def _get_r_max_i(q_max_k):

        return q_max_k / np.sum(q_max_k)


def make_get_f_l_cl_funcs(n_rm, cooling_equipments):

    # 顕熱負荷、室温、加湿・除湿をしない場合の自然絶対湿度から、係数 f_l_cl を求める関数を定義する。
    # 対流式と放射式に分けて係数を設定して、それぞれの除湿量を出す式に将来的に変更した方が良いかもしれない。

    def get_f_l_cl(l_cs_is_n, theta_r_is_n_pls, x_r_ntr_is_n_pls):
        # ==== ルームエアコン吹出絶対湿度の計算 ====
        # 顕熱負荷・室内温度・除加湿を行わない場合の室絶対湿度から、除加湿計算に必要な係数 la 及び lb を計算する。
        # 下記、変数 l は、係数 la と lb のタプルであり、変数 ls は変数 l のリスト。

        ls = [
            _func_rac(n_room=n_rm, lcs_is_n=l_cs_is_n, theta_r_is_n_pls=theta_r_is_n_pls, x_r_ntr_is_n_pls=x_r_ntr_is_n_pls, prop=equipment['property'])
            for equipment in cooling_equipments
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

    return get_f_l_cl


def _func_rac(
        n_room,
        lcs_is_n,
        theta_r_is_n_pls,
        x_r_ntr_is_n_pls,
        prop
):

    # Lcsは加熱が正で表される。
    # 加熱時は除湿しない。
    # 以下の取り扱いを簡単にするため（冷房負荷を正とするため）、正負を反転させる
    q_s_is_n = -lcs_is_n

    id = prop['space_id']

    q_rac_max_i = prop['q_max']
    q_rac_min_i = prop['q_min']
    v_rac_max_i = prop['v_max'] / 60
    v_rac_min_i = prop['v_min'] / 60
    bf_rac_i = prop['bf']
    q_s_i_n = q_s_is_n[id, 0]
    theta_r_i_n_pls = theta_r_is_n_pls[id, 0]
    x_r_ntr_i_n_pls = x_r_ntr_is_n_pls[id, 0]

    v_rac_i_n = _get_vac_rac_i_n(
        q_rac_max_i=q_rac_max_i,
        q_rac_min_i=q_rac_min_i,
        q_s_i_n=q_s_i_n,
        v_rac_max_i=v_rac_max_i,
        v_rac_min_i=v_rac_min_i
    )

    theta_rac_ex_srf_i_n_pls = _get_theta_rac_ex_srf_i_n_pls(
        bf_rac_i=bf_rac_i,
        q_s_i_n=q_s_i_n,
        theta_r_i_n_pls=theta_r_i_n_pls,
        v_rac_i_n=v_rac_i_n
    )

    x_rac_ex_srf_i_n_pls = _get_x_rac_ex_srf_i_n_pls(theta_rac_ex_srf_i_n_pls=theta_rac_ex_srf_i_n_pls)

    brmx_rac_is = np.where(
        (x_r_ntr_i_n_pls > x_rac_ex_srf_i_n_pls) & (q_s_i_n > 0.0),
        get_rho_a() * v_rac_i_n * (1 - bf_rac_i),
        0.0
    )

    brcx_rac_is = np.where(
        (x_r_ntr_i_n_pls > x_rac_ex_srf_i_n_pls) & (q_s_i_n > 0.0),
        get_rho_a() * v_rac_i_n * (1 - bf_rac_i) * x_rac_ex_srf_i_n_pls,
        0.0
    )

    brmx_is_is = np.zeros((n_room, n_room), dtype=float)
    brxc_is = np.zeros((n_room, 1), dtype=float)

    brmx_is_is[id, id] = brmx_rac_is
    brxc_is[id, 0] = brcx_rac_is

    return brmx_is_is, brxc_is


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

    return get_x(get_p_vs_is2(theta_rac_ex_srf_i_n_pls))


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


