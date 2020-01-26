import math
import numpy as np
from typing import List

import a9_rear_surface_equivalent_temperature as a9
import a14_furniture as a14
import a18_initial_value_constants as a18
from a39_global_parameters import OperationMode

import s4_1_sensible_heat as s41

import Psychrometrics as psy


# # 室温・熱負荷を計算するクラス

# ## １）室内部位に関連するクラス

# 室内部位に関する情報を保持します。
# 
# - is_skin:      外皮フラグ, 外皮の場合True
# - boundary:  方位・隣室名, string
# - unsteady:  非定常フラグ, 非定常壁体の場合True
# - name:      壁体・開口部名称, string
# - A_i_g:      面積, m2
# - sunbreak:  ひさし名称, string
# - flr_i_k:       放射暖房吸収比率, －
# - fot:       人体に対する形態係数, －

# ## ４）空間に関するクラス

# 空間に関する情報を保持します。
# 
# - roomname:      室区分, string
# - roomdiv:       室名称, string
# - HeatCcap:      最大暖房能力（対流）[W]
# - HeatRcap:      最大暖房能力（放射）[W]
# - CoolCcap:      最大冷房能力（対流）[W]
# - CoolRcap:      最大冷房能力（放射）[W]
# - Vol:           室気積, m3
# - Fnt:           家具熱容量, kJ/m3K
# - Vent:          計画換気量, m3/h
# - Inf:           すきま風量[Season]（list型、暖房・中間期・冷房の順）, m3/h
# - CrossVentRoom: 通風計算対象室, False
# - is_radiative_heating:       放射暖房対象室フラグ, True
# - Betat:         放射暖房対流比率, －
# - RoomtoRoomVents:      室間換気量（list型、暖房・中間期・冷房、風上室名称）, m3/h
# - d:             室内部位に関連するクラス, Surface

class Logger:

    def __init__(self, n_bnd_i_jstrs):

        self.q_sol_frnt_i_ns = None

        self.q_trs_sol_i_ns = None

        # 当該時刻の空調需要
        self.air_conditioning_demand = None

        # ステップnの室iにおける機器発熱, W
        self.heat_generation_appliances_schedule = None

        # ステップnの室iにおける照明発熱, W, [8760*4]
        self.heat_generation_lighting_schedule = None

        # ステップnの室iの集約された境界j*における裏面温度, degree C, [j*, 8760*4]
        self.theta_rear_i_jstrs_ns = np.full((n_bnd_i_jstrs, 24 * 365 * 4 * 4), -99.9)

        # ステップnの室iにおける人体発熱, W
        self.q_hum_i_ns = np.zeros(24 * 365 * 4 * 3)

        # ステップnの室iにおける人体発湿, kg/s
        self.x_hum_i_ns = np.zeros(24 * 365 * 4 * 3)

        # ステップnの室iにおける運転状態
        self.operation_mode = np.empty(24 * 365 * 4 * 3, dtype=object)

        # ステップnの室iにおける家具の温度, degree C
        self.theta_frnt_i_ns = np.full(24 * 365 * 4 * 3, a18.get_Tfun_initial())

        # i室のn時点における室温
        self.theta_r_i_ns = np.zeros(24 * 365 * 4 * 3)

        # i室のn時点における室の作用温度
        self.OT_i_n = np.zeros(24 * 365 * 4 * 3)

        self.Qfuns_i_n = np.zeros(24 * 365 * 4 * 3)

        self.Qc = np.zeros((n_bnd_i_jstrs, 24 * 365 * 4 * 4))
        self.Qr = np.zeros((n_bnd_i_jstrs, 24 * 365 * 4 * 4))

        # ステップnにおける室iの部位j*における室内側表面温度, degree C
        self.Ts_i_k_n = np.zeros((n_bnd_i_jstrs, 24 * 365 * 4 * 4))

        # i室のn時点におけるMRV(平均放射温度)
        self.MRT_i_n = np.zeros(24 * 365 * 4 * 3)

        # i室の部位kにおけるn時点の室内等価温度
        self.Tei_i_k_n = np.zeros((n_bnd_i_jstrs, 24 * 365 * 4 * 4))

        # i室のn時点における放射空調熱負荷
        self.Lrs_i_n = np.zeros(24 * 365 * 4 * 3)

        # i室のn時点における対流空調熱負荷
        self.Lcs_i_n = np.zeros(24 * 365 * 4 * 3)

        # i室のn時点における室加湿熱量
        self.Lcl_i_n = np.zeros(24 * 365 * 4 * 3)

        # i室のn時点における備品類の絶対湿度
        self.xf_i_n = np.full(24 * 365 * 4 * 3, a18.get_xf_initial())

        # i室のn時点における家具の日射吸収熱量
        self.Qfunl_i_n = np.zeros(24 * 365 * 4 * 3)

        # i室のn時点における相対風速[m/s]
        self.Vel_i_n = np.full(24 * 365 * 4 * 3, 0.1)

        # i室のn時点における着衣量[Clo]
        self.Clo_i_n = np.ones(24 * 365 * 4 * 3)

        # i室のn時点における室絶対湿度
        self.x_r_i_ns = np.zeros(24 * 365 * 4 * 3)

        # i室のn時点における室相対湿度[%]
        self.RH_i_n = np.full(24 * 365 * 4 * 3, 50.0)


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
        v_room_cap_i: 気積, m3
        v_vent_ex_i: 外気からの機械換気量, m3/h
        name_vent_up_i_nis: 隣室からの機械換気量niの上流側の室の名称
        v_vent_up_i_nis: 隣室からの機械換気量niの換気量, m3/h
    """

    def __init__(
            self, i: int, name_i: str, room_type_i: str, v_room_cap_i: float,
            name_vent_up_i_nis: List[str], v_vent_up_i_nis: np.ndarray,
            name_bnd_i_jstrs: np.ndarray, sub_name_bnd_i_jstrs: np.ndarray, boundary_type_i_jstrs: np.ndarray,
            a_bnd_i_jstrs: np.ndarray, h_bnd_i_jstrs, next_room_type_bnd_i_jstrs,
            is_solar_absorbed_inside_bnd_i_jstrs, theta_o_sol_bnd_i_jstrs_ns, n_root_bnd_i_jstrs,
            row_bnd_i_jstrs, rft0_bnd_i_jstrs, rfa0_bnd_i_jstrs, rft1_bnd_i_jstrs, rfa1_bnd_i_jstrs, n_bnd_i_jstrs,
            q_trs_sol_i_ns: np.ndarray,
            theta_r_i_initial: float, x_r_i_initial: float,
            heat_generation_appliances_schedule: np.ndarray,
            x_gen_except_hum_i_ns: np.ndarray, heat_generation_lighting_schedule: np.ndarray,
            number_of_people_schedule: np.ndarray,
            air_conditioning_demand: np.ndarray,
            TsdA_initial: float, TsdT_initial: float, Fot_i_g: np.ndarray, A_total_i: float,
            qmax_c_i: float, qmin_c_i: float, Vmax_i: float, Vmin_i: float,
            is_radiative_heating: bool,
            Lrcap_i: float, is_radiative_cooling: bool, radiative_cooling_max_capacity: float,
            heat_exchanger_type, convective_cooling_rtd_capacity: float, flr_i_k,
            h_r_bnd_i_jstrs, h_c_bnd_i_jstrs, F_mrt_i_g,
            Ga,
            Beta_i,
            AX_k_l, WSR_i_k, WSB_i_k,
            BRMnoncv_i, BRL_i, c_room_i, c_cap_frnt_i, c_fun_i,
            q_gen_except_hum_i_ns,
            q_sol_srf_i_jstrs_ns,
            q_sol_frnt_i_ns,
            next_room_idxs_i,
            v_ntrl_vent_i,
            v_mec_vent_i_ns,
    ):

        self.name_i = name_i
        self.room_type_i = room_type_i

        # 室iの容積, m3
        self.v_room_cap_i = v_room_cap_i

        # 室iの自然風利用時の換気量, m3/s
        self.v_ntrl_vent_i = v_ntrl_vent_i

        # ステップnの室iにおける機械換気量（全般換気量+局所換気量）, m3/s
        self.v_mec_vent_i_ns = v_mec_vent_i_ns

        self.name_vent_up_i_nis = name_vent_up_i_nis

        # 室iの隣室からの機械換気量niの換気量, m3/s, [ni]
        self.v_int_vent_i_istrs = v_vent_up_i_nis / 3600.0
        self.next_room_idxs_i = next_room_idxs_i

        # 室iの隣室からの機械換気量, m3/s, [i]
        self.v_int_vent_i = np.array([0.0, 0.0, 0.0])
        self.v_int_vent_i[self.next_room_idxs_i] = self.v_int_vent_i_istrs

        self.name_bdry_i_jstrs = name_bnd_i_jstrs
        self.sub_name_bdry_i_jstrs = sub_name_bnd_i_jstrs

        # 室iの統合された境界j*の種類, [j*]
        self.boundary_type_i_jstrs = boundary_type_i_jstrs

        # 室iの統合された境界j*の数
        self.number_of_boundary = len(boundary_type_i_jstrs)

        self.a_bnd_i_jstrs = a_bnd_i_jstrs

        # 室iの統合された境界j*の温度差係数, [j*]
        self.h_bnd_i_jstrs = h_bnd_i_jstrs

        # 室iの統合された境界j*の傾斜面のステップnにおける相当外気温度, ℃, [j*, 8760*4]
        self.theta_o_sol_bnd_i_jstrs_ns = theta_o_sol_bnd_i_jstrs_ns

        # ステップnの室iの集約された境界j * の外乱による裏面温度, degree C, [j*, 8760*4]
        self.theta_dstrb_i_jstrs_ns = theta_o_sol_bnd_i_jstrs_ns * h_bnd_i_jstrs.reshape(-1, 1)

        # 室温が裏面温度に与える影響を表すマトリクス, [j* * i]
        self.m = a9.get_matrix(
            boundary_type_i_jstrs=boundary_type_i_jstrs,
            h_bnd_i_jstrs=h_bnd_i_jstrs,
            i=i,
            next_room_type_bnd_i_jstrs=next_room_type_bnd_i_jstrs)

        # 室iの統合された境界j*の隣室タイプ, [j*]
        self.next_room_type_bnd_i_jstrs = next_room_type_bnd_i_jstrs
        # Spaceクラスで持つ必要はない変数の可能性あり（インスタンス終了後破棄可能）（要調査）
        self.is_solar_absorbed_inside_bdry_i_jstrs = is_solar_absorbed_inside_bnd_i_jstrs

        self.n_root_bnd_i_jstrs = n_root_bnd_i_jstrs
        self.r_bnd_i_jstrs_ms = row_bnd_i_jstrs
        self.phi_t_0_bnd_i_jstrs = rft0_bnd_i_jstrs
        self.phi_a_0_bnd_i_jstrs = rfa0_bnd_i_jstrs
        self.phi_t_1_bnd_i_jstrs_ms = rft1_bnd_i_jstrs
        self.phi_a_1_bnd_i_jstrs_ms = rfa1_bnd_i_jstrs

        # 室iの統合された境界j*の数, [j*]
        self.n_bnd_i_jstrs = n_bnd_i_jstrs

        # ステップnの室iにおける在室人数, [8760*4]
        self.n_hum_i_ns = number_of_people_schedule

        # ステップnの室iにおける人体発熱を除く内部発熱, W, [8760*4]
        self.q_gen_except_hum_i_ns = q_gen_except_hum_i_ns
        # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [8760*4]
        self.x_gen_except_hum_i_ns = x_gen_except_hum_i_ns

        self.ac_demand = air_conditioning_demand  # 当該時刻の空調需要（0：なし、1：あり）

        self.theta_r_i_npls = theta_r_i_initial
        self.theta_mrt_i_n = theta_r_i_initial
        self.v_hum_i_n = 0.0
        # ステップnの室iにおける衣服の表面温度, degree C
        self.theta_cl_i_n = theta_r_i_initial

        self.x_r_i_n = x_r_i_initial

        # 水蒸気圧, Pa
        self.p_a_i_n = psy.get_p_vs(x_r_i_initial) * 0.5

        # （26）式中の〖CVL〗_(i,l)の計算式右辺
        self.theta_srf_dsh_a_i_jstrs_n_m = np.full((n_bnd_i_jstrs, 12), TsdA_initial)

        # （26）式中の〖CVL〗_(i,l)の計算式右辺
        self.theta_srf_dsh_t_i_jstrs_n_m = np.full((n_bnd_i_jstrs, 12), TsdT_initial)

        # 前時刻の室内側表面熱流
        self.q_srf_i_jstrs_n = np.zeros(n_bnd_i_jstrs)

        # 合計面積の計算
        self.A_total_i = A_total_i

        # 部位の人体に対する形態係数を計算 表6
        self.Fot_i_g = Fot_i_g

        self.qmax_c_i = qmax_c_i
        self.qmin_c_i = qmin_c_i
        self.Vmax_i = Vmax_i
        self.Vmin_i = Vmin_i

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

        # 室空気の質量[kg]
        self.Ga = Ga

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

        # 室iの熱容量, J/K
        self.c_room_i = c_room_i

        # 家具熱容量, J/K
        self.c_cap_frnt_i = c_cap_frnt_i

        # 家具と空気間の熱コンダクタンス, W/K
        self.c_fun_i = c_fun_i

        self.rsolfun__i = math.nan  # 透過日射の内家具が吸収する割合[－]
        self.kc_i = s41.calc_kc_i()  # i室の人体表面における対流熱伝達率の総合熱伝達率に対する比
        self.kr_i = s41.calc_kr_i()  # i室の人体表面における放射熱伝達率の総合熱伝達率に対する比

        # 前時刻の運転状態
        self.operation_mode = OperationMode.STOP_CLOSE

        # 家具の熱容量、湿気容量の計算

        # Gf_i:湿気容量[kg/(kg/kg(DA))]、Cx_i:湿気コンダクタンス[kg/(s･kg/kg(DA))]

        self.old_theta_frnt_i = a18.get_Tfun_initial()
        self.Gf_i = a14.get_Gf(self.v_room_cap_i)  # i室の備品類の湿気容量
        self.Cx_i = a14.get_Cx(self.Gf_i)  # i室の備品類と室空気間の湿気コンダクタンス
        self.xf_i_npls = a18.get_xf_initial()

        # 計算結果出力用ロガー
        self.logger = Logger(n_bnd_i_jstrs=n_bnd_i_jstrs)

        self.logger.air_conditioning_demand = air_conditioning_demand
        # ステップnの室iにおける機器発熱, W
        self.logger.heat_generation_appliances_schedule = heat_generation_appliances_schedule
        # ステップnの室iにおける照明発熱, W
        self.logger.heat_generation_lighting_schedule = heat_generation_lighting_schedule

        self.logger.q_trs_sol_i_ns = q_trs_sol_i_ns

        self.logger.q_sol_frnt_i_ns = q_sol_frnt_i_ns


class Spaces:

    def __init__(self, spaces: List[Space]):

        # ステップnの室iにおける空調需要, [i, 8760*4]
        self.ac_demand_is_n = np.concatenate([[s.ac_demand] for s in spaces])

        # 室温が裏面温度に与える影響を表すマトリクス, [j* * i]
        self.m_is = np.concatenate([s.m for s in spaces])

        # ステップnの集約された境界j*の外乱による裏面温度, degree C, [j*, 8760*4]
        self.theta_dstrb_jstrs_ns = np.concatenate([s.theta_dstrb_i_jstrs_ns for s in spaces])

        # ステップnの室iにおける在室人数, [i, 8760*4]
        self.n_hum_is_n = np.concatenate([[s.n_hum_i_ns] for s in spaces])

        # ステップnの室iにおける人体発熱を除く内部発熱, W, [i, 8760*4]
        self.q_gen_except_hum_is_n = np.concatenate([[s.q_gen_except_hum_i_ns] for s in spaces])

        # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [i, 8760*4]
        self.x_gen_except_hum_is_n = np.concatenate([[s.x_gen_except_hum_i_ns] for s in spaces])

        # 室iの熱容量, J/K, [i]
        self.c_room_is = np.array([s.c_room_i for s in spaces])

        # ステップnの室iにおける機械換気量（全般換気量+局所換気量）, m3/s
        self.v_mec_vent_is_ns = np.concatenate([[s.v_mec_vent_i_ns] for s in spaces])

        # 室iの隣室からの機械換気量, m3/s, [i, i]
        self.v_int_vent_is = np.concatenate([[s.v_int_vent_i] for s in spaces])

        # 家具熱容量, J/K
        self.c_cap_frnt_is = np.array([s.c_cap_frnt_i for s in spaces])

        # 家具と空気間の熱コンダクタンス, W/K, [i]
        self.c_fun_is = np.array([s.c_fun_i for s in spaces])

        # 家具の吸収日射量, W, [i, 8760*4]
        self.q_sol_frnt_is_ns = np.concatenate([[s.q_sol_frnt_i_ns] for s in spaces])

        # 室iの自然風利用時の換気量, m3/s, [i]
        self.v_ntrl_vent_is = np.array([s.v_ntrl_vent_i for s in spaces])

        # BRMの計算 式(5) ※ただし、通風なし
        self.BRMnoncv_is = np.concatenate([[s.BRMnoncv_i] for s in spaces])

        # BRLの計算 式(7)
        self.brl_is_ns = np.concatenate([[s.BRL_i] for s in spaces])

        # i室の人体表面における対流熱伝達率の総合熱伝達率に対する比
        self.kc_is = np.array([s.kc_i for s in spaces])

        # i室の人体表面における放射熱伝達率の総合熱伝達率に対する比
        self.kr_is = np.array([s.kr_i for s in spaces])

        # 放射暖房最大能力, W, [i]
        self.lrcap_is = np.array([s.Lrcap_i for s in spaces])

        # 放射暖房有無（Trueなら放射暖房あり）
        self.is_radiative_heating_is = np.array([s.is_radiative_heating for s in spaces])

        # 放射暖房対流比率
        self.beta_is = np.array([s.Beta_i for s in spaces])

        # === 境界j*に関すること ===

        # 統合された境界j*の吸熱応答係数の初項, m2K/W, [j*]
        self.phi_a_0_bnd_jstrs = np.concatenate([s.phi_a_0_bnd_i_jstrs for s in spaces])

        # 統合された境界j*の項別公比法における項mの吸熱応答係数の第一項 , m2K/W, [j*, 12]
        self.phi_a_1_bnd_jstrs_ms = np.concatenate([s.phi_a_1_bnd_i_jstrs_ms for s in spaces])

        # 統合された境界j*の項別公比法における項mの公比, [j*, 12]
        self.r_bnd_jstrs_ms = np.concatenate([s.r_bnd_i_jstrs_ms for s in spaces])

        # 統合された境界j*の貫流応答係数の初項, [j*]
        self.phi_t_0_bnd_i_jstrs = np.concatenate([s.phi_t_0_bnd_i_jstrs for s in spaces])

        # 統合された境界j*の項別公比法における項mの貫流応答係数の第一項, [j*,12]
        self.phi_t_1_bnd_jstrs_ms = np.concatenate([s.phi_t_1_bnd_i_jstrs_ms for s in spaces])

        # ステップnの統合された境界j*における透過日射熱取得量のうち表面に吸収される日射量, W/m2, [j*, 8760*4]
        self.q_sol_srf_jstrs_ns = np.concatenate([s.q_sol_srf_i_jstrs_ns for s in spaces])

        s_idcs = get_start_indices2(spaces=spaces)  # [0, 11, 23, 32]
        total_number_of_bdry_is = sum([s.number_of_boundary for s in spaces])  # 32
        self.ivs_x_is = np.zeros((total_number_of_bdry_is, total_number_of_bdry_is))
        for i, s in enumerate(spaces):
            self.ivs_x_is[s_idcs[i]:s_idcs[i+1], s_idcs[i]:s_idcs[i+1]] = s.ivs_x_i

        self.p = np.zeros((len(spaces), total_number_of_bdry_is))
        for i, s in enumerate(spaces):
            self.p[i, s_idcs[i]:s_idcs[i+1]] = 1.0

        # 部位の人体に対する形態係数を計算 表6
        self.fot_jstrs = np.zeros((len(spaces), total_number_of_bdry_is))
        for i, s in enumerate(spaces):
            self.fot_jstrs[i, s_idcs[i]:s_idcs[i+1]] = s.Fot_i_g

        # 平均放射温度計算時の各部位表面温度の重み計算 式(101)
        self.f_mrt_jstrs = np.zeros((len(spaces), total_number_of_bdry_is))
        for i, s in enumerate(spaces):
            self.f_mrt_jstrs[i, s_idcs[i]:s_idcs[i+1]] = s.F_mrt_i_g

        # 統合された境界j*の種類, [j*]
        self.boundary_type_jstrs = np.concatenate([s.boundary_type_i_jstrs for s in spaces])

        # 統合された境界j*における室内側放射熱伝達率, W/m2K, [j*]
        self.h_r_bnd_jstrs = np.concatenate([s.h_r_bnd_i_jstrs for s in spaces])

        # 統合された境界j*における室内側対流熱伝達率, W/m2K, [j*]
        self.h_c_bnd_jstrs = np.concatenate([s.h_c_bnd_i_jstrs for s in spaces])

        # 統合された境界j*の面積, m2, [j*]
        self.a_bnd_jstrs = np.concatenate([s.a_bnd_i_jstrs for s in spaces])

        # WSR, WSB の計算 式(24)
        self.wsr_jstrs = np.concatenate([s.WSR_i_k for s in spaces])
        self.wsb_jstrs = np.concatenate([s.WSB_i_k for s in spaces])

        # 床暖房の発熱部位？
        self.flr_is_k = np.concatenate([s.flr_i_k for s in spaces])


def get_start_indices2(spaces):

    number_of_bdry_is = np.array([s.number_of_boundary for s in spaces])
    start_indices = [0]
    indices = 0
    for n_bdry in number_of_bdry_is:
        indices = indices + n_bdry
        start_indices.append(indices)

    return start_indices
