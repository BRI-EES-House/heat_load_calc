import math
import numpy as np
from typing import List
from collections import namedtuple

import a9_rear_surface_equivalent_temperature as a9
import a14_furniture as a14
import a16_blowing_condition_rac as a16
import a18_initial_value_constants as a18
from a39_global_parameters import OperationMode

import s4_1_sensible_heat as s41
import psychrometrics as psy


# 空間に関する情報の保持
class Space:
    """室クラス。

    室に関する情報を保持するクラス。

    Attributes:
        name_i: 名称
        room_type_i: 室タイプ
            main_occupant_room: 主たる居室
            other_occupant_room: その他の居室
            non_occupant_room: 非居室
            underfloor: 床下空間
    """

    def __init__(
            self,
            is_solar_absorbed_inside_bnd_i_jstrs,
            r_bdry_i_jstrs_ms,
            rft0_bnd_i_jstrs,
            rfa0_bnd_i_jstrs,
            rft1_bnd_i_jstrs,
            rfa1_bnd_i_jstrs,
            n_bnd_i_jstrs,
            q_trs_sol_i_ns: np.ndarray,
            air_conditioning_demand: np.ndarray,
            qmax_c_i: float,
            qmin_c_i: float,
            Vmax_i: float,
            Vmin_i: float,
            is_radiative_heating: bool,
            Lrcap_i: float, is_radiative_cooling: bool, radiative_cooling_max_capacity: float,
            heat_exchanger_type, convective_cooling_rtd_capacity: float, flr_i_k,
            h_r_bnd_i_jstrs, h_c_bnd_i_jstrs, F_mrt_i_g,
            Beta_i,
            AX_k_l, WSR_i_k, WSB_i_k,
            BRMnoncv_i, BRL_i,
            q_sol_srf_i_jstrs_ns,
            q_sol_frnt_i_ns,
            v_ntrl_vent_i
    ):

        # 室iの自然風利用時の換気量, m3/s
        self.v_ntrl_vent_i = v_ntrl_vent_i

        # Spaceクラスで持つ必要はない変数の可能性あり（インスタンス終了後破棄可能）（要調査）
        self.is_solar_absorbed_inside_bdry_i_jstrs = is_solar_absorbed_inside_bnd_i_jstrs

        self.r_bdry_i_jstrs_ms = r_bdry_i_jstrs_ms
        self.phi_t_0_bnd_i_jstrs = rft0_bnd_i_jstrs
        self.phi_a_0_bnd_i_jstrs = rfa0_bnd_i_jstrs
        self.phi_t_1_bnd_i_jstrs_ms = rft1_bnd_i_jstrs
        self.phi_a_1_bnd_i_jstrs_ms = rfa1_bnd_i_jstrs

        # 室iの統合された境界j*の数, [j*]
        self.n_bnd_i_jstrs = n_bnd_i_jstrs

        self.ac_demand = air_conditioning_demand  # 当該時刻の空調需要（0：なし、1：あり）

        self.qmax_c_i = qmax_c_i
        self.qmin_c_i = qmin_c_i
        self.Vmax_i = Vmax_i
        self.Vmin_i = Vmin_i

        self.get_vac_xeout = a16.make_get_vac_xeout_def(Vmin=Vmin_i, Vmax=Vmax_i, qmin_c=qmin_c_i, qmax_c=qmax_c_i)

        # 放射暖房有無（Trueなら放射暖房あり）
        self.is_radiative_heating = is_radiative_heating

        # 放射暖房最大能力[W]
        self.Lrcap_i = Lrcap_i

        # 冷房設備仕様の読み込み

        # 放射冷房有無（Trueなら放射冷房あり）
        self.is_radiative_cooling = is_radiative_cooling

        # 放射冷房最大能力[W]
        self.radiative_cooling_max_capacity = radiative_cooling_max_capacity

        # 熱交換器種類
        self.heat_exchanger_type = heat_exchanger_type

        # 定格冷房能力[W]
        self.convective_cooling_rtd_capacity = convective_cooling_rtd_capacity

        self.flr_i_k = flr_i_k

        # 表面熱伝達率の計算 式(123) 表16
        self.h_r_bnd_i_jstrs = h_r_bnd_i_jstrs
        self.h_c_bnd_i_jstrs = h_c_bnd_i_jstrs

        # 平均放射温度計算時の各部位表面温度の重み計算 式(101)
        self.F_mrt_i_g = F_mrt_i_g

        # ステップnの室iの統合された境界j*における透過日射熱取得量のうち表面に吸収される日射量, W/m2
        self.q_sol_srf_i_jstrs_ns = q_sol_srf_i_jstrs_ns

        # 家具の吸収日射量[W] 式(92)
        self.q_sol_frnt_i_ns = q_sol_frnt_i_ns

        # 放射暖房対流比率
        self.Beta_i = Beta_i

        # 行列AX 式(25)
        self.ivs_x_i = AX_k_l

        # WSR, WSB の計算 式(24)
        self.WSR_i_k = WSR_i_k
        self.WSB_i_k = WSB_i_k

        # BRMの計算 式(5) ※ただし、通風なし
        self.BRMnoncv_i = BRMnoncv_i

        # BRLの計算 式(7)
        self.BRL_i = BRL_i

        self.rsolfun__i = math.nan  # 透過日射の内家具が吸収する割合[－]

        self.q_trs_sol_i_ns = q_trs_sol_i_ns


class Spaces:

    def __init__(
            self,
            spaces: List[Space],
            number_of_spaces,
            space_names,
            v_room_cap_is,
            g_f_is,
            c_x_is,
            c_room_is,
            c_cap_frnt_is,
            c_frnt_is,
            v_int_vent_is,
            name_bdry_jstrs,
            sub_name_bdry_jstrs,
            type_bdry_jstrs,
            a_bdry_jstrs,
            v_mec_vent_is_ns,
            q_gen_is_ns,
            number_of_people_schedules,
            x_gen_is_ns,
            k_ei_is,
            number_of_bdry_is,
            idx_bdry_is,
            f_mrt_hum_jstrs,
            theta_dstrb_is_jstrs_ns
    ):

        # 室の数
        self.total_number_of_spaces = number_of_spaces

        # 室の名前
        self.names = space_names

        # 室iの容積, m3
        self.v_room_cap_is = v_room_cap_is

        # 室iの家具等の湿気容量, kg/m3 kg/kgDA, [i]
        self.gf_is = g_f_is

        # 室iの家具等と空気間の湿気コンダクタンス, kg/s kg/kgDA
        self.cx_is = c_x_is

        # 室iの熱容量, J/K, [i]
        self.c_room_is = c_room_is

        # 室iの家具等の熱容量, J/K
        self.c_cap_frnt_is = c_cap_frnt_is

        # 室iの家具等と空気間の熱コンダクタンス, W/K, [i]
        self.c_frnt_is = c_frnt_is

        # 室iの隣室からの機械換気量, m3/s, [i, i]
        self.v_int_vent_is = v_int_vent_is

        # 統合された境界j*の名前, [j*]
        self.name_bdry_jstrs = name_bdry_jstrs

        # 統合された境界j*の名前2, [j*]
        self.sub_name_bdry_jstrs = sub_name_bdry_jstrs

        # 統合された境界j*の種類, [j*]
        self.boundary_type_jstrs = type_bdry_jstrs

        # 統合された境界j*の面積, m2, [j*]
        self.a_bdry_jstrs = a_bdry_jstrs

        # 境界の数（リスト）, [i]
        self.number_of_bdry_is = number_of_bdry_is

        # 境界の数（総数）
        total_number_of_bdry = np.sum(number_of_bdry_is)



        # 境界のリスト形式を室ごとのリスト形式に切るためのインデックス（不要になったら消すこと）
        self.start_indices = get_start_indices(number_of_boundaries=self.number_of_bdry_is)

        # ステップnにおける室iの空調需要, [i, 8760*4]
        self.ac_demand_is_n = np.concatenate([[s.ac_demand] for s in spaces])

        # 室温が裏面温度に与える影響を表すマトリクス, [j* * i]
        self.k_ei_is = k_ei_is

        # ステップnの集約された境界j*の外乱による裏面温度, degree C, [j*, 8760*4]
        self.theta_dstrb_jstrs_ns = theta_dstrb_is_jstrs_ns

        # ステップnの室iにおける在室人数, [i, 8760*4]
        self.n_hum_is_n = number_of_people_schedules

        # ステップnの室iにおける人体発熱を除く内部発熱, W, [i, 8760*4]
        self.q_gen_is_ns = q_gen_is_ns

        # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [i, 8760*4]
        self.x_gen_is_ns = x_gen_is_ns

        # ステップnの室iにおける機械換気量（全般換気量+局所換気量）, m3/s
        self.v_mec_vent_is_ns = v_mec_vent_is_ns


        # 家具の吸収日射量, W, [i, 8760*4]
        self.q_sol_frnt_is_ns = np.concatenate([[s.q_sol_frnt_i_ns] for s in spaces])

        # 室iの自然風利用時の換気量, m3/s, [i]
        self.v_ntrl_vent_is = np.array([s.v_ntrl_vent_i for s in spaces])

        # BRMの計算 式(5) ※ただし、通風なし
        self.BRMnoncv_is = np.concatenate([[s.BRMnoncv_i] for s in spaces])

        # BRLの計算 式(7)
        self.brl_is_ns = np.concatenate([[s.BRL_i] for s in spaces])

        # 放射暖房最大能力, W, [i]
        self.lrcap_is = np.array([s.Lrcap_i for s in spaces])

        # 放射暖房有無（Trueなら放射暖房あり）
        self.is_radiative_heating_is = np.array([s.is_radiative_heating for s in spaces])

        # 放射冷房有無（Trueなら放射冷房あり）
        self.is_radiative_cooling_is = np.array([s.is_radiative_cooling for s in spaces])

        # 放射暖房対流比率
        self.beta_is = np.array([s.Beta_i for s in spaces])

        def get_vac_xeout_is(lcs_is_n, theta_r_is_npls, operation_mode_is_n):

            vac_is_n = []
            xeout_is_n = []

            for s, lcs_i_n, theta_r_i_npls, operation_mode_i_n in zip(spaces, lcs_is_n, theta_r_is_npls, operation_mode_is_n):
                Vac_n_i, xeout_i_n = s.get_vac_xeout(lcs_i_n, theta_r_i_npls, operation_mode_i_n)
                vac_is_n.append(Vac_n_i)
                xeout_is_n.append(xeout_i_n)

            return np.array(vac_is_n), np.array(xeout_is_n)

        self.get_vac_xeout_is = get_vac_xeout_is

        # === 境界j*に関すること ===

        # 統合された境界j*の吸熱応答係数の初項, m2K/W, [j*]
        self.phi_a_0_bnd_jstrs = np.concatenate([s.phi_a_0_bnd_i_jstrs for s in spaces])

        # 統合された境界j*の項別公比法における項mの吸熱応答係数の第一項 , m2K/W, [j*, 12]
        self.phi_a_1_bnd_jstrs_ms = np.concatenate([s.phi_a_1_bnd_i_jstrs_ms for s in spaces])

        # 統合された境界j*の項別公比法における項mの公比, [j*, 12]
        self.r_bdry_jstrs_ms = np.concatenate([s.r_bdry_i_jstrs_ms for s in spaces])

        # 統合された境界j*の貫流応答係数の初項, [j*]
        self.phi_t_0_bnd_i_jstrs = np.concatenate([s.phi_t_0_bnd_i_jstrs for s in spaces])

        # 統合された境界j*の項別公比法における項mの貫流応答係数の第一項, [j*,12]
        self.phi_t_1_bnd_jstrs_ms = np.concatenate([s.phi_t_1_bnd_i_jstrs_ms for s in spaces])

        # ステップnの統合された境界j*における透過日射熱取得量のうち表面に吸収される日射量, W/m2, [j*, 8760*4]
        self.q_sol_srf_jstrs_ns = np.concatenate([s.q_sol_srf_i_jstrs_ns for s in spaces])

        s_idcs = idx_bdry_is

        self.total_number_of_bdry = total_number_of_bdry
        self.ivs_x_is = np.zeros((total_number_of_bdry, total_number_of_bdry))
        for i, s in enumerate(spaces):
            self.ivs_x_is[s_idcs[i]:s_idcs[i+1], s_idcs[i]:s_idcs[i+1]] = s.ivs_x_i

        self.p = np.zeros((len(spaces), total_number_of_bdry))
        for i, s in enumerate(spaces):
            self.p[i, s_idcs[i]:s_idcs[i+1]] = 1.0

        # 室iの在室者に対する境界j*の形態係数
        self.fot_jstrs = f_mrt_hum_jstrs

        # 平均放射温度計算時の各部位表面温度の重み計算 式(101)
        self.f_mrt_jstrs = np.zeros((len(spaces), total_number_of_bdry))
        for i, s in enumerate(spaces):
            self.f_mrt_jstrs[i, s_idcs[i]:s_idcs[i+1]] = s.F_mrt_i_g

        # 統合された境界j*における室内側放射熱伝達率, W/m2K, [j*]
        self.h_r_bnd_jstrs = np.concatenate([s.h_r_bnd_i_jstrs for s in spaces])

        # 統合された境界j*における室内側対流熱伝達率, W/m2K, [j*]
        self.h_c_bnd_jstrs = np.concatenate([s.h_c_bnd_i_jstrs for s in spaces])

        # WSR, WSB の計算 式(24)
        self.wsr_jstrs = np.concatenate([s.WSR_i_k for s in spaces])
        self.wsb_jstrs = np.concatenate([s.WSB_i_k for s in spaces])

        # 床暖房の発熱部位？
        self.flr_is_k = np.concatenate([s.flr_i_k for s in spaces])

        # ステップnの室iにおける窓の透過日射熱取得, W, [8760*4]
        self.q_trs_sol_is_ns = np.concatenate([[s.q_trs_sol_i_ns] for s in spaces])


def get_start_indices(number_of_boundaries: np.ndarray):

    start_indices = []
    indices = 0
    for n_bdry in number_of_boundaries:
        indices = indices + n_bdry
        start_indices.append(indices)
    start_indices.pop(-1)
    return start_indices


Conditions = namedtuple('Conditions', [

    # ステップnにおける室iの運転状態, [i]
    # 列挙体 OperationMode で表される。
    #     COOLING ： 冷房
    #     HEATING : 暖房
    #     STOP_OPEN : 暖房・冷房停止で窓「開」
    #     STOP_CLOSE : 暖房・冷房停止で窓「閉」
    'operation_mode_is_n',

    # ステップnにおける室iの空気温度, degree C, [i]
    'theta_r_is_n',

    # ステップnにおける室iの在室者の平均放射温度, degree C, [i]
    'theta_mrt_hum_is_n',

    # ステップnにおける室iの絶対湿度, kg/kgDA, [i]
    'x_r_is_n',

    # ステップnの統合された境界j*における指数項mの吸熱応答の項別成分, degree C, [j*, 12]
    'theta_dsh_srf_a_jstrs_n_ms',

    # ステップnの統合された境界j*における指数項mの貫流応答の項別成分, degree C, [j*, 12]
    'theta_dsh_srf_t_jstrs_n_ms',

    # ステップnの統合された境界j*における表面熱流（壁体吸熱を正とする）, W/m2, [j*]
    'q_srf_jstrs_n',

    # ステップnの室iにおける家具の温度, degree C, [i]
    'theta_frnt_is_n',

    # ステップnの室iにおける家具の絶対湿度, kg/kgDA, [i]
    'x_frnt_is_n',

    # ステップnにおける室iの在室者の着衣温度, degree C, [i]
    # 本来であれば着衣温度と人体周りの対流・放射熱伝達率を未知数とした熱収支式を収束計算等を用いて時々刻々求めるのが望ましい。
    # 今回、収束計算を回避するために前時刻の着衣温度を用いることにした。
    'theta_cl_is_n'

])


def initialize_conditions(ss: Spaces):

    # 空間iの数
    total_number_of_spaces = ss.total_number_of_spaces

    # 統合された境界j*の数
    total_number_of_bdry = ss.total_number_of_bdry

    # ステップnにおける室iの運転状態, [i]
    # 初期値を暖房・冷房停止で窓「閉」とする。
    operation_mode_is_n = np.full(total_number_of_spaces, OperationMode.STOP_CLOSE)

    # ステップnにおける室iの空気温度, degree C, [i]
    # 初期値を15℃とする。
    theta_r_is_n = np.full(total_number_of_spaces, 15.0)

    # ステップnにおける室iの在室者の着衣温度, degree C, [i]
    # 初期値を15℃とする。
    theta_cl_is_n = np.full(total_number_of_spaces, 15.0)

    # ステップnにおける室iの在室者の平均放射温度, degree C, [i]
    # 初期値を15℃と設定する。
    theta_mrt_hum_is_n = np.full(total_number_of_spaces, 15.0)

    # ステップnにおける室iの絶対湿度, kg/kgDA, [i]
    # 初期値を空気温度20℃相対湿度40%の時の値とする。
    x_r_is_n = np.full(total_number_of_spaces, psy.get_x(psy.get_p_vs(theta=20.0) * 0.4))

    # ステップnの統合された境界j*における指数項mの吸熱応答の項別成分, degree C, [j*, 12]
    # 初期値を0.0℃とする。
    theta_dsh_srf_a_jstrs_n_ms = np.full((total_number_of_bdry, 12), 0.0)

    # ステップnの統合された境界j*における指数項mの貫流応答の項別成分, degree C, [j*, 12]
    # 初期値を0.0℃とする。
    theta_dsh_srf_t_jstrs_n_ms = np.full((total_number_of_bdry, 12), 0.0)

    # ステップnの統合された境界j*における表面熱流（壁体吸熱を正とする）, W/m2, [j*]
    # 初期値を0.0W/m2とする。
    q_srf_jstrs_n = np.zeros(total_number_of_bdry)

    # ステップnの室iにおける家具の温度, degree C, [i]
    # 初期値を15℃とする。
    theta_frnt_is_n = np.full(total_number_of_spaces, 15.0)

    # ステップnの室iにおける家具の絶対湿度, kg/kgDA, [i]
    # 初期値を空気温度20℃相対湿度40%の時の値とする。
    x_frnt_is_n = np.full(total_number_of_spaces, psy.get_x(psy.get_p_vs(theta=20.0) * 0.4))

    return Conditions(
        operation_mode_is_n=operation_mode_is_n,
        theta_r_is_n=theta_r_is_n,
        theta_mrt_hum_is_n=theta_mrt_hum_is_n,
        x_r_is_n=x_r_is_n,
        theta_dsh_srf_a_jstrs_n_ms=theta_dsh_srf_a_jstrs_n_ms,
        theta_dsh_srf_t_jstrs_n_ms=theta_dsh_srf_t_jstrs_n_ms,
        q_srf_jstrs_n=q_srf_jstrs_n,
#        h_hum_c_is_n=h_hum_c_is_n,
#        h_hum_r_is_n=h_hum_r_is_n,
        theta_frnt_is_n=theta_frnt_is_n,
        x_frnt_is_n=x_frnt_is_n,
        theta_cl_is_n=theta_cl_is_n
    )

