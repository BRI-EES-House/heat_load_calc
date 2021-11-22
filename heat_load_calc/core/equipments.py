from typing import Dict, List
from typing import Union
import numpy as np
from dataclasses import dataclass

from heat_load_calc.core import boundary_simple
from heat_load_calc.external.psychrometrics import get_x, get_p_vs_is2
from heat_load_calc.external.global_number import get_c_a, get_rho_a
from heat_load_calc.core.matrix_method import v_diag


@dataclass
class HeatingEquipmentRAC:

    # ID
    id: int

    # 名前
    name: str

    # 暖房する室のID
    room_id: int

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

    # 暖房する室のID
    room_id: int

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

    # 冷房する室のID
    room_id: int

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

    # 冷房する室のID
    room_id: int

    # 放射冷房が設置される境界の番号
    boundary_id: int

    # 面積あたりの放熱能力, W/m2
    max_capacity: float

    # 面積, m2
    area: float

    # 対流成分比率
    convection_ratio: float


class Equipments:

    def __init__(self, dict_equipments: Dict, n_rm: int, n_b: int, bs: boundary_simple.Boundaries):
        """設備に関する情報を辞書形式で受け取り、データクラスに変換して保持する。
        暖房・冷房それぞれにおいて、
        辞書の中の "equipment_type" の種類に応じて対応するデータクラスを生成する。

        Args:
            dict_equipments: 設備の情報が記された辞書
            n_rm: 部屋の数
            n_b: 境界の数
            bs: Boundariesクラス

        Notes:
            ここで Boundaries クラスは、境界IDと室IDとの対応関係を見ることだけに使用される。
            放射暖冷房に関する設備情報には対応する境界IDしか記されていない。
            一方で、放射暖冷房においても、beta, f_flr の係数を計算する際には、
            その放射暖冷房がどの室に属しているのかの情報が必要になるため、
            Equipments を initialize する際に、あらかじめ放射暖冷房にも room_id を付与しておくこととする。
        """

        self._hes = [
            self._create_heating_equipment(dict_heating_equipment=he, bs=bs)
            for he in dict_equipments['heating_equipments']
        ]

        self._ces = [
            self._create_cooling_equipment(dict_cooling_equipment=ce, bs=bs)
            for ce in dict_equipments['cooling_equipments']
        ]

        self._n_rm = n_rm
        self._n_b = n_b

    @staticmethod
    def _create_heating_equipment(dict_heating_equipment, bs: boundary_simple.Boundaries):

        he_type = dict_heating_equipment['equipment_type']
        id = dict_heating_equipment['id']
        name = dict_heating_equipment['name']
        prop = dict_heating_equipment['property']

        if he_type == 'rac':

            return HeatingEquipmentRAC(
                id=id,
                name=name,
                room_id=prop['space_id'],
                q_min=prop['q_min'],
                q_max=prop['q_max'],
                v_min=prop['v_min'],
                v_max=prop['v_max'],
                bf=prop['bf']
            )

        elif he_type == 'floor_heating':

            room_id = bs.get_room_id_by_boundary_id(boundary_id=prop['boundary_id'])

            return HeatingEquipmentFloorHeating(
                id=id,
                name=name,
                room_id=room_id,
                boundary_id=prop['boundary_id'],
                max_capacity=prop['max_capacity'],
                area=prop['area'],
                convection_ratio=prop['convection_ratio']
            )

        else:
            raise Exception

    @staticmethod
    def _create_cooling_equipment(dict_cooling_equipment, bs: boundary_simple.Boundaries):

        ce_type = dict_cooling_equipment['equipment_type']
        id = dict_cooling_equipment['id']
        name = dict_cooling_equipment['name']
        prop = dict_cooling_equipment['property']

        if ce_type == 'rac':

            return CoolingEquipmentRAC(
                id=id,
                name=name,
                room_id=prop['space_id'],
                q_min=prop['q_min'],
                q_max=prop['q_max'],
                v_min=prop['v_min'],
                v_max=prop['v_max'],
                bf=prop['bf']
            )

        elif ce_type == 'floor_cooling':

            room_id = bs.get_room_id_by_boundary_id(boundary_id=prop['boundary_id'])

            return CoolingEquipmentFloorCooling(
                id=id,
                name=name,
                room_id=room_id,
                boundary_id=prop['boundary_id'],
                max_capacity=prop['max_capacity'],
                area=prop['area'],
                convection_ratio=prop['convection_ratio']
            )

        else:
            raise Exception

    def get_is_radiative_heating_is(self):
        """
        室に放射暖房があるか否かを判定する。
        Returns:
            放射暖房の有無, [i, 1]
        """

        return self._get_is_radiative_is(es=self._hes)

    def get_is_radiative_cooling_is(self):
        """
        室に放射冷房があるか否かを判定する。
        Returns:
            放射冷房の有無, [i, 1]
        """

        return self._get_is_radiative_is(es=self._ces)

    def get_q_rs_h_max_is(self):

        return self._get_q_rs_max_is(es=self._hes)

    def get_q_rs_c_max_is(self):

        return self._get_q_rs_max_is(es=self._ces)

    def _get_q_rs_max_is(self, es):

        q_rs_max_is = np.zeros(shape=(self._n_rm, 1), dtype=float)

        for e in es:
            if type(e) in [HeatingEquipmentFloorHeating, CoolingEquipmentFloorCooling]:
                q_rs_max_is[e.room_id, 0] = q_rs_max_is[e.room_id, 0] + e.max_capacity * e.area

        return q_rs_max_is

    def get_beta_h_is(self):

        return self._get_beta_is(es=self._hes)

    def get_beta_c_is(self):

        return self._get_beta_is(es=self._ces)

    def _get_is_radiative_is(self, es):
        """室に放射暖冷房があるか否かを判定する。

        Returns:
            放射暖冷房の有無, [i, 1]
        """

        is_radiative_is = np.full(shape=(self._n_rm, 1), fill_value=False)

        for e in es:
            if type(e) in [HeatingEquipmentFloorHeating, CoolingEquipmentFloorCooling]:
                is_radiative_is[e.room_id, 0] = True

        return is_radiative_is

    def _get_beta_is(self, es):

        f_beta_eqp_ks_is = self._get_f_beta_eqp_ks_is(es=es, n_rm=self._n_rm)
        r_max_ks_is = self._get_r_max_ks_is(es=es, n_rm=self._n_rm)

        return np.sum(f_beta_eqp_ks_is * r_max_ks_is, axis=0).reshape(-1, 1)

    def _get_p_ks_is(self, es):

        p_ks_is = np.zeros(shape=(len(es), self._n_rm), dtype=float)

        for k, e in enumerate(es):
            if type(e) in [HeatingEquipmentFloorHeating, CoolingEquipmentFloorCooling]:
                p_ks_is[k, e.room_id] = 1.0

        return p_ks_is

    @staticmethod
    def _get_f_beta_eqp_ks_is(es, n_rm):

        f_beta_eqp_ks_is = np.zeros(shape=(len(es), n_rm), dtype=float)

        for k, e in enumerate(es):
            if type(e) in [HeatingEquipmentFloorHeating, CoolingEquipmentFloorCooling]:
                f_beta_eqp_ks_is[k, e.room_id] = e.convection_ratio

        return f_beta_eqp_ks_is

    @staticmethod
    def _get_r_max_ks_is(es, n_rm):

        q_max_ks_is = np.zeros(shape=(len(es), n_rm), dtype=float)

        for k, e in enumerate(es):
            if type(e) in [HeatingEquipmentFloorHeating, CoolingEquipmentFloorCooling]:
                q_max_ks_is[k, e.room_id] = e.max_capacity * e.area

        sum_of_q_max_is = q_max_ks_is.sum(axis=0)

        # 各室の放熱量の合計値がゼロだった場合、次の式のゼロ割を防ぐためにダミーの数字1.0を代入する。
        # この場合、次の式の分子の数はゼロであるため、結果として 0.0/1.0 = 0.0 となり、結果には影響を及ぼさない。
        sum_of_q_max_is[np.where(sum_of_q_max_is == 0.0)] = 1.0

        return q_max_ks_is / sum_of_q_max_is

    def get_f_flr_h_js_is(self):

        return self._get_f_flr_js_is(es=self._hes)

    def get_f_flr_c_js_is(self):

        return self._get_f_flr_js_is(es=self._ces)

    def _get_f_flr_js_is(self, es):

        f_flr_eqp_js_ks = self._get_f_flr_eqp_js_ks(es=es)
        f_beta_eqp_ks_is = self._get_f_beta_eqp_ks_is(es=es, n_rm=self._n_rm)
        r_max_ks_is = self._get_r_max_ks_is(es=es, n_rm=self._n_rm)
        beta_is = self._get_beta_is(es=es)
        p_ks_is = self._get_p_ks_is(es=es)

        return np.dot(np.dot(f_flr_eqp_js_ks, (p_ks_is - f_beta_eqp_ks_is) * r_max_ks_is), v_diag(1 / (1 - beta_is)))

    def _get_f_flr_eqp_js_ks(self, es):

        f_flr_eqp_js_ks = np.zeros(shape=(self._n_b, len(es)), dtype=float)

        for k, e in enumerate(es):
            if type(e) in [HeatingEquipmentFloorHeating, CoolingEquipmentFloorCooling]:
                f_flr_eqp_js_ks[e.boundary_id, k] = e.convection_ratio

        return f_flr_eqp_js_ks

    def make_get_f_l_cl_funcs(self):

        # 顕熱負荷、室温、加湿・除湿をしない場合の自然絶対湿度から、係数 f_l_cl を求める関数を定義する。
        # 対流式と放射式に分けて係数を設定して、それぞれの除湿量を出す式に将来的に変更した方が良いかもしれない。

        def get_f_l_cl(l_cs_is_n, theta_r_is_n_pls, x_r_ntr_is_n_pls):
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

        return get_f_l_cl

    def _get_ls_a_ls_b(self, l_cs_is_n, theta_r_is_n_pls, x_r_ntr_is_n_pls, ce):

        if type(ce) is CoolingEquipmentRAC:
            return self._func_rac(
                l_cs_is_n=l_cs_is_n,
                theta_r_is_n_pls=theta_r_is_n_pls,
                x_r_ntr_is_n_pls=x_r_ntr_is_n_pls,
                ce=ce
            )
        elif type(ce) is CoolingEquipmentFloorCooling:
            raise NotImplementedError
        else:
            raise Exception

    def _func_rac(
            self,
            l_cs_is_n,
            theta_r_is_n_pls,
            x_r_ntr_is_n_pls,
            ce: CoolingEquipmentRAC
    ):

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

        return get_x(get_p_vs_is2(theta_rac_ex_srf_i_n_pls))

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


