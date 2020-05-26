import math
import numpy as np
from typing import List
from collections import namedtuple

from a39_global_parameters import OperationMode

import psychrometrics as psy


class Spaces:

    def __init__(
            self,
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
            n_hum_is_ns,
            x_gen_is_ns,
            k_ei_is,
            number_of_bdry_is,
            f_mrt_hum_jstrs,
            theta_dstrb_is_jstrs_ns,
            r_bdry_jstrs_ms,
            phi_t0_bdry_jstrs,
            phi_a0_bdry_jstrs,
            phi_t1_bdry_jstrs_ms,
            phi_a1_bdry_jstrs_ms,
            q_trs_sol_is_ns,
            v_ntrl_vent_is,
            ac_demand_is_ns,
            get_vac_xeout_def_is,
            is_radiative_heating_is,
            is_radiative_cooling_is,
            Lrcap_is,
            radiative_cooling_max_capacity_is,
            flr_jstrs,
            h_r_bnd_jstrs,
            h_c_bnd_jstrs,
            f_mrt_jstrs,
            q_sol_floor_jstrs_ns,
            q_sol_frnt_is_ns,
            Beta_is,
            WSR_is_k,
            WSB_is_k,
            BRMnoncv_is,
            ivs_x_is,
            BRL_is,
            p
    ):

        # region 室に関すること

        # 室の数, [i]
        self.number_of_spaces = number_of_spaces

        # 室の名前, [i]
        self.space_names = space_names

        # 室iの容積, m3, [i]
        self.v_room_cap_is = v_room_cap_is

        # 室iの家具等の湿気容量, kg/m3 kg/kgDA, [i]
        self.g_f_is = g_f_is

        # 室iの家具等と空気間の湿気コンダクタンス, kg/s kg/kgDA, [i]
        self.c_x_is = c_x_is

        # 室iの熱容量, J/K, [i]
        self.c_room_is = c_room_is

        # 室iの家具等の熱容量, J/K, [i]
        self.c_cap_frnt_is = c_cap_frnt_is

        # 室iの家具等と空気間の熱コンダクタンス, W/K, [i]
        self.c_frnt_is = c_frnt_is

        # ステップnにおける室iの空調需要, [i, 8760*4]
        self.ac_demand_is_n = ac_demand_is_ns

        # ステップnの室iにおける在室人数, [i, 8760*4]
        self.n_hum_is_n = n_hum_is_ns

        # ステップnの室iにおける人体発熱を除く内部発熱, W, [i, 8760*4]
        self.q_gen_is_ns = q_gen_is_ns

        # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [i, 8760*4]
        self.x_gen_is_ns = x_gen_is_ns

        # ステップnの室iにおける機械換気量（全般換気量+局所換気量）, m3/s, [i, 8760*4]
        self.v_mec_vent_is_ns = v_mec_vent_is_ns

        # 家具の吸収日射量, W, [i, 8760*4]
        self.q_sol_frnt_is_ns = q_sol_frnt_is_ns

        # 室iの自然風利用時の換気量, m3/s, [i]
        self.v_ntrl_vent_is = v_ntrl_vent_is

        # ステップnの室iにおける窓の透過日射熱取得, W, [8760*4]
        self.q_trs_sol_is_ns = q_trs_sol_is_ns

        # endregion

        # 室iの隣室からの機械換気量, m3/s, [i, i]
        self.v_int_vent_is = v_int_vent_is

        # 統合された境界j*の名前, [j*]
        self.name_bdry_jstrs = name_bdry_jstrs

        # 統合された境界j*の名前2, [j*]
        self.sub_name_bdry_jstrs = sub_name_bdry_jstrs

        # 統合された境界j*の種類, [j*]
        self.type_bdry_jstrs = type_bdry_jstrs

        # 統合された境界j*の面積, m2, [j*]
        self.a_bdry_jstrs = a_bdry_jstrs

        # 境界の数（リスト）, [i]
        self.number_of_bdry_is = number_of_bdry_is

        # 境界の数（総数）
        total_number_of_bdry = np.sum(number_of_bdry_is)



        # 境界のリスト形式を室ごとのリスト形式に切るためのインデックス（不要になったら消すこと）
        self.start_indices = get_start_indices(number_of_boundaries=self.number_of_bdry_is)

        # 室温が裏面温度に与える影響を表すマトリクス, [j* * i]
        self.k_ei_is = k_ei_is

        # ステップnの集約された境界j*の外乱による裏面温度, degree C, [j*, 8760*4]
        self.theta_dstrb_jstrs_ns = theta_dstrb_is_jstrs_ns

        # BRMの計算 式(5) ※ただし、通風なし
        self.BRMnoncv_is = BRMnoncv_is

        # BRLの計算 式(7)
        # self.brl_is_ns = np.concatenate([[s.BRL_i] for s in spaces])
        self.brl_is_ns = BRL_is

        # 放射暖房最大能力, W, [i]
        self.lrcap_is = Lrcap_is

#        radiative_cooling_max_capacity_is

        # 放射暖房有無（Trueなら放射暖房あり）
        self.is_radiative_heating_is = is_radiative_heating_is

        # 放射冷房有無（Trueなら放射冷房あり）
        self.is_radiative_cooling_is = is_radiative_cooling_is

        # 放射暖房対流比率
        self.beta_is = Beta_is

        def get_vac_xeout_is(lcs_is_n, theta_r_is_npls, operation_mode_is_n):

            vac_is_n = []
            xeout_is_n = []

            for lcs_i_n, theta_r_i_npls, operation_mode_i_n, get_vac_xeout_def_i in zip(lcs_is_n, theta_r_is_npls, operation_mode_is_n, get_vac_xeout_def_is):
                Vac_n_i, xeout_i_n = get_vac_xeout_def_i(lcs_i_n, theta_r_i_npls, operation_mode_i_n)
                vac_is_n.append(Vac_n_i)
                xeout_is_n.append(xeout_i_n)

            return np.array(vac_is_n), np.array(xeout_is_n)

        self.get_vac_xeout_is = get_vac_xeout_is

        # === 境界j*に関すること ===

        # 統合された境界j*の項別公比法における項mの公比, [j*, 12]
        self.r_bdry_jstrs_ms = r_bdry_jstrs_ms

        # 統合された境界j*の貫流応答係数の初項, [j*]
        self.phi_t0_bdry_jstrs = phi_t0_bdry_jstrs

        # 統合された境界j*の吸熱応答係数の初項, m2K/W, [j*]
        self.phi_a0_bdry_jstrs = phi_a0_bdry_jstrs

        # 統合された境界j*の項別公比法における項mの貫流応答係数の第一項, [j*,12]
        self.phi_t1_bdry_jstrs_ms = phi_t1_bdry_jstrs_ms

        # 統合された境界j*の項別公比法における項mの吸熱応答係数の第一項 , m2K/W, [j*, 12]
        self.phi_a1_bdry_jstrs_ms = phi_a1_bdry_jstrs_ms

        # ステップnの統合された境界j*における透過日射熱取得量のうち表面に吸収される日射量, W/m2, [j*, 8760*4]
        self.q_sol_srf_jstrs_ns = q_sol_floor_jstrs_ns

        self.total_number_of_bdry = total_number_of_bdry
        self.ivs_x_is = ivs_x_is

        self.p = p

        # 室iの在室者に対する境界j*の形態係数
        self.fot_jstrs = f_mrt_hum_jstrs

        # 平均放射温度計算時の各部位表面温度の重み計算 式(101)
        self.f_mrt_jstrs = f_mrt_jstrs

        # 統合された境界j*における室内側放射熱伝達率, W/m2K, [j*]
        self.h_r_bnd_jstrs = h_r_bnd_jstrs

        # 統合された境界j*における室内側対流熱伝達率, W/m2K, [j*]
        self.h_c_bnd_jstrs = h_c_bnd_jstrs

        # WSR, WSB の計算 式(24)
        self.wsr_jstrs = WSR_is_k
        self.wsb_jstrs = WSB_is_k

        # 床暖房の発熱部位？
        self.flr_is_k = flr_jstrs


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
    total_number_of_spaces = ss.number_of_spaces

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

