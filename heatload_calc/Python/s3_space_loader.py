import math
import numpy as np
from typing import List
from collections import namedtuple

from a39_global_parameters import OperationMode
from a39_global_parameters import BoundaryType

import psychrometrics as psy


class PreCalcParameters:

    def __init__(
            self,
            number_of_spaces,
            space_name_is,
            v_room_cap_is,
            g_f_is,
            c_x_is,
            c_room_is,
            c_cap_frnt_is,
            c_frnt_is,
            v_int_vent_is,
            name_bdry_js,
            sub_name_bdry_js,
            a_srf_js,
            v_mec_vent_is_ns,
            q_gen_is_ns,
            n_hum_is_ns,
            x_gen_is_ns,
            k_ei_is,
            number_of_bdry_is,
            f_mrt_hum_is_js,
            theta_dstrb_js_ns,
            r_js_ms,
            phi_t0_js,
            phi_a0_js,
            phi_t1_js_ms,
            phi_a1_js_ms,
            q_trs_sol_is_ns,
            v_ntrl_vent_is,
            ac_demand_is_ns,
            get_vac_xeout_def_is,
            is_radiative_heating_is,
            is_radiative_cooling_is,
            lrcap_is,
            radiative_cooling_max_capacity_is,
            flr_js_is,
            h_r_js,
            h_c_js,
            f_mrt_is_js,
            q_sol_js_ns,
            q_sol_frnt_is_ns,
            beta_is,
            wsr_js_is,
            wsb_js_is,
            brm_noncv_is,
            ivs_ax_js_js,
            brl_is_is,
            p_is_js,
            p_js_is,
            get_vac_xeout_is,
            is_ground_js,
            wsc_js_ns,
            k_ei_js_js
    ):

        # region 室に関すること

        # 室の数, [i]
        self.number_of_spaces = number_of_spaces

        # 室の名前, [i]
        self.space_name_is = space_name_is

        # 室iの容積, m3, [i, 1]
        self.v_room_cap_is = v_room_cap_is

        # 室iの家具等の湿気容量, kg/m3 kg/kgDA, [i]
        self.g_f_is = g_f_is

        # 室iの家具等と空気間の湿気コンダクタンス, kg/s kg/kgDA, [i]
        self.c_x_is = c_x_is

        # 室iの熱容量, J/K, [i, 1]
        self.c_room_is = c_room_is

        # 室iの家具等の熱容量, J/K, [i, 1]
        self.c_cap_frnt_is = c_cap_frnt_is

        # 室iの家具等と空気間の熱コンダクタンス, W/K, [i, 1]
        self.c_frnt_is = c_frnt_is

        # ステップnにおける室iの空調需要, [i, 8760*4]
        self.ac_demand_is_n = ac_demand_is_ns

        # ステップnの室iにおける在室人数, [i, 8760*4]
        self.n_hum_is_ns = n_hum_is_ns

        # ステップnの室iにおける人体発熱を除く内部発熱, W, [i, 8760*4]
        self.q_gen_is_ns = q_gen_is_ns

        # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [i, 8760*4]
        self.x_gen_is_ns = x_gen_is_ns

        # ステップnの室iにおける機械換気量（全般換気量+局所換気量）, m3/s, [i, 8760*4]
        self.v_mec_vent_is_ns = v_mec_vent_is_ns

        # 家具の吸収日射量, W, [i, 8760*4]
        self.q_sol_frnt_is_ns = q_sol_frnt_is_ns

        # 室iの自然風利用時の換気量, m3/s, [i, 1]
        self.v_ntrl_vent_is = v_ntrl_vent_is

        # ステップnの室iにおける窓の透過日射熱取得, W, [8760*4]
        self.q_trs_sol_is_ns = q_trs_sol_is_ns

        # endregion

        # 室iの隣室からの機械換気量, m3/s, [i, i]
        self.v_int_vent_is = v_int_vent_is

        # 統合された境界j*の名前, [j*]
        self.name_bdry_js = name_bdry_js

        # 統合された境界j*の名前2, [j*]
        self.sub_name_bdry_js = sub_name_bdry_js

        # 境界jが地盤かどうか, [j]
        self.is_ground_js = is_ground_js

        # 統合された境界j*の面積, m2, [j, 1]
        self.a_srf_js = a_srf_js

        # 境界の数（リスト）, [i]
        self.number_of_bdry_is = number_of_bdry_is

        # 境界の数（総数）
        total_number_of_bdry = np.sum(number_of_bdry_is)



        # 境界のリスト形式を室ごとのリスト形式に切るためのインデックス（不要になったら消すこと）
        self.start_indices = get_start_indices(number_of_boundaries=self.number_of_bdry_is)

        # 室温が裏面温度に与える影響を表すマトリクス, [j* * i]
        self.k_ei_is = k_ei_is

        # ステップnの集約境界j*における外気側等価温度の外乱成分, degree C, [j*, 8760*4]
        self.theta_dstrb_js_ns = theta_dstrb_js_ns

        # BRMの計算 式(5) ※ただし、通風なし
        self.brm_noncv_is = brm_noncv_is

        # BRLの計算 式(7)
        self.brl_is_is = brl_is_is

        # 放射暖房最大能力, W, [i]
        self.lrcap_is = lrcap_is

#        radiative_cooling_max_capacity_is

        # 放射暖房有無（Trueなら放射暖房あり）
        self.is_radiative_heating_is = is_radiative_heating_is

        # 放射冷房有無（Trueなら放射冷房あり）
        self.is_radiative_cooling_is = is_radiative_cooling_is

        # 放射暖房対流比率, [i, 1]
        self.beta_is = beta_is

        self.get_vac_xeout_is = get_vac_xeout_is

        # === 境界j*に関すること ===

        # 統合された境界j*の項別公比法における項mの公比, [j*, 12]
        self.r_js_ms = r_js_ms

        # 統合された境界j*の貫流応答係数の初項, [j*]
        self.phi_t0_js = phi_t0_js

        # 統合された境界j*の吸熱応答係数の初項, m2K/W, [j*]
        self.phi_a0_js = phi_a0_js

        # 統合された境界j*の項別公比法における項mの貫流応答係数の第一項, [j*,12]
        self.phi_t1_js_ms = phi_t1_js_ms

        # 統合された境界j*の項別公比法における項mの吸熱応答係数の第一項 , m2K/W, [j*, 12]
        self.phi_a1_js_ms = phi_a1_js_ms

        # ステップnの統合された境界j*における透過日射熱取得量のうち表面に吸収される日射量, W/m2, [j*, 8760*4]
        self.q_sol_js_ns = q_sol_js_ns

        self.total_number_of_bdry = total_number_of_bdry
        self.ivs_ax_js_js = ivs_ax_js_js

        self.p_is_js = p_is_js
        self.p_js_is = p_js_is

        # 室iの在室者に対する境界j*の形態係数
        self.f_mrt_hum_is_js = f_mrt_hum_is_js

        # 平均放射温度計算時の各部位表面温度の重み計算 式(101)
        self.f_mrt_is_js = f_mrt_is_js

        # 境界jにおける室内側放射熱伝達率, W/m2K, [j, 1]
        self.h_r_js = h_r_js

        # 境界jにおける室内側対流熱伝達率, W/m2K, [j, 1]
        self.h_c_js = h_c_js

        # WSR, WSB の計算 式(24)
        self.wsr_js_is = wsr_js_is
        self.wsb_js = np.sum(wsb_js_is, axis=1)
        self.wsb_js_is = wsb_js_is

        # 床暖房の発熱部位？
        self.flr_js_is = flr_js_is

        # WSC, W, [j, n]
        self.wsc_js_ns = wsc_js_ns

        # 境界jの裏面温度に他の境界の等価温度が与える影響, [j, j]
        self.k_ei_js_js = k_ei_js_js


def get_start_indices(number_of_boundaries: np.ndarray):

    start_indices = []
    indices = 0
    for n_bdry in number_of_boundaries:
        indices = indices + n_bdry
        start_indices.append(indices)
    start_indices.pop(-1)
    return start_indices


class Conditions:

    def __init__(
            self,
            operation_mode_is_n,
            theta_r_is_n,
            theta_mrt_hum_is_n,
            x_r_is_n,
            theta_dsh_srf_a_js_ms_n,
            theta_dsh_srf_t_js_ms_n,
            q_srf_js_n,
            theta_frnt_is_n,
            x_frnt_is_n,
            theta_cl_is_n,
            theta_ei_js_n
    ):

        # ステップnにおける室iの運転状態, [i, 1]
        # 列挙体 OperationMode で表される。
        #     COOLING ： 冷房
        #     HEATING : 暖房
        #     STOP_OPEN : 暖房・冷房停止で窓「開」
        #     STOP_CLOSE : 暖房・冷房停止で窓「閉」
        self.operation_mode_is_n = operation_mode_is_n

        # ステップnにおける室iの空気温度, degree C, [i, 1]
        self.theta_r_is_n = theta_r_is_n

        # ステップnにおける室iの在室者の平均放射温度, degree C, [i]
        self.theta_mrt_hum_is_n = theta_mrt_hum_is_n

        # ステップnにおける室iの絶対湿度, kg/kgDA, [i]
        self.x_r_is_n = x_r_is_n

        # ステップnの境界jにおける項別公比法の指数項mの吸熱応答の項別成分, degree C, [j, m] (m=12)
        self.theta_dsh_srf_a_js_ms_n = theta_dsh_srf_a_js_ms_n

        # ステップnの境界jにおける項別公比法の指数項mの貫流応答の項別成分, degree C, [j, m] (m=12)
        self.theta_dsh_srf_t_js_ms_n = theta_dsh_srf_t_js_ms_n

        # ステップnの境界jにおける表面熱流（壁体吸熱を正とする）, W/m2, [j, 1]
        self.q_srf_js_n = q_srf_js_n

        # ステップnの室iにおける家具の温度, degree C, [i, 1]
        self.theta_frnt_is_n = theta_frnt_is_n

        # ステップnの室iにおける家具の絶対湿度, kg/kgDA, [i]
        self.x_frnt_is_n = x_frnt_is_n

        # ステップnにおける室iの在室者の着衣温度, degree C, [i]
        # 本来であれば着衣温度と人体周りの対流・放射熱伝達率を未知数とした熱収支式を収束計算等を用いて時々刻々求めるのが望ましい。
        # 今回、収束計算を回避するために前時刻の着衣温度を用いることにした。
        self.theta_cl_is_n = theta_cl_is_n

        # [i, 1]
        self.theta_ei_js_n = theta_ei_js_n


def initialize_conditions(ss: PreCalcParameters):

    # 空間iの数
    total_number_of_spaces = ss.number_of_spaces

    # 統合された境界j*の数
    total_number_of_bdry = ss.total_number_of_bdry

    # ステップnにおける室iの運転状態, [i, 1]
    # 初期値を暖房・冷房停止で窓「閉」とする。
    operation_mode_is_n = np.full((total_number_of_spaces, 1), OperationMode.STOP_CLOSE)

    # ステップnにおける室iの空気温度, degree C, [i, 1]
    # 初期値を15℃とする。
    theta_r_is_n = np.full((total_number_of_spaces, 1), 15.0)

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
    theta_dsh_srf_a_js_ms_n0 = np.full((total_number_of_bdry, 12), 0.0)

    # ステップnの統合された境界j*における指数項mの貫流応答の項別成分, degree C, [j*, 12]
    # 初期値を0.0℃とする。
    theta_dsh_srf_t_js_ms_n0 = np.full((total_number_of_bdry, 12), 0.0)

    # ステップnの境界jにおける表面熱流（壁体吸熱を正とする）, W/m2, [j, 1]
    # 初期値を0.0W/m2とする。
    q_srf_jstrs_n = np.zeros((total_number_of_bdry, 1), dtype=float)

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
        theta_dsh_srf_a_js_ms_n=theta_dsh_srf_a_js_ms_n0,
        theta_dsh_srf_t_js_ms_n=theta_dsh_srf_t_js_ms_n0,
        q_srf_js_n=q_srf_jstrs_n,
#        h_hum_c_is_n=h_hum_c_is_n,
#        h_hum_r_is_n=h_hum_r_is_n,
        theta_frnt_is_n=theta_frnt_is_n.reshape(-1, 1),
        x_frnt_is_n=x_frnt_is_n,
        theta_cl_is_n=theta_cl_is_n,
        theta_ei_js_n=np.full(total_number_of_bdry, 15.0).reshape(-1, 1)
    )

