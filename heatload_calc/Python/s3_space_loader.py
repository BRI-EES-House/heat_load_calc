import math
import numpy as np
from typing import List

import a12_indoor_radiative_heat_transfer as a12
import a13_Win_ACselect as a13
import a14_furniture as a14
import a15_air_flow_rate_rac as a15
import a18_initial_value_constants as a18
import a1_calculation_surface_temperature as a1
import a20_room_spec as a20
import a21_next_vent_spec as a21
import a22_radiative_heating_spec as a22
import a23_surface_heat_transfer_coefficient as a23
import a29_local_vent_schedule as a29
import a30_internal_heat_schedule as a30
import a31_lighting_schedule as a31
import a32_resident_schedule as a32
import a34_building_part_summarize as a34

import s3_surface_loader as s3
import s4_1_sensible_heat as s41


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

    FsolFlr = 0.5  # 床の日射吸収比率

    def __init__(
            self, d_room, name_i: str, room_type_i: str, v_room_cap_i: float, v_vent_ex_i,
            name_vent_up_i_nis: List[str], v_vent_up_i_nis: np.ndarray,
            name_bdry_i_jstrs: np.ndarray, sub_name_bdry_i_jstrs: np.ndarray, boundary_type_i_jstrs: np.ndarray,
            a_bdry_i_jstrs: np.ndarray, is_sun_striked_outside_bdry_i_jstrs, h_bdry_i_jstrs, next_room_type_bdry_i_jstrs,
            is_solar_absorbed_inside_bdry_i_jstrs, h_i_bdry_i_jstrs, theta_o_sol_bdry_i_jstrs_ns, n_root_bdry_i_jstrs,
            row_bdry_i_jstrs, rft0_bdry_i_jstrs, rfa0_bdry_i_jstrs, rft1_bdry_i_jstrs, rfa1_bdry_i_jstrs, n_bdry_i_jstrs,
            q_trs_sol_i_ns: np.ndarray
    ):

        self.name_i = name_i
        self.room_type_i = room_type_i
        self.v_room_cap_i = v_room_cap_i
        self.v_vent_ex_i = v_vent_ex_i
        self.name_vent_up_i_nis = name_vent_up_i_nis
        self.v_vent_up_i_nis = v_vent_up_i_nis

        self.name_bdry_i_jstrs = name_bdry_i_jstrs
        self.sub_name_bdry_i_jstrs = sub_name_bdry_i_jstrs
        self.boundary_type_i_jstrs = boundary_type_i_jstrs
        self.a_bdry_i_jstrs = a_bdry_i_jstrs
        self.is_sun_striked_outside_bdry_i_jstrs = is_sun_striked_outside_bdry_i_jstrs
        self.h_bdry_i_jstrs = h_bdry_i_jstrs
        self.next_room_type_bdry_i_jstrs = next_room_type_bdry_i_jstrs
        # Spaceクラスで持つ必要はない変数の可能性あり（インスタンス終了後破棄可能）（要調査）
        self.is_solar_absorbed_inside_bdry_i_jstrs = is_solar_absorbed_inside_bdry_i_jstrs
        self.h_i_bdry_i_jstrs = h_i_bdry_i_jstrs
        self.theta_o_sol_bdry_i_jstrs_ns = theta_o_sol_bdry_i_jstrs_ns
        self.n_root_bdry_i_jstrs = n_root_bdry_i_jstrs
        self.row_bdry_i_jstrs = row_bdry_i_jstrs
        self.rft0_bdry_i_jstrs = rft0_bdry_i_jstrs
        self.rfa0_bdry_i_jstrs = rfa0_bdry_i_jstrs
        self.rft1_bdry_i_jstrs = rft1_bdry_i_jstrs
        self.rfa1_bdry_i_jstrs = rfa1_bdry_i_jstrs
        self.n_bdry_i_jstrs = n_bdry_i_jstrs
        # 室iの相当隙間面積（C値）,
        # TODO: 相当隙間面積についてはからすきま風量を変換する部分については実装されていない。
        self.Inf = 0.0  # すきま風量（暫定値）
        self.q_trs_sol_i_ns = q_trs_sol_i_ns


        # 室iの自然風利用時の換気回数, 1/h
        self.Nventtime_i = d_room['natural_vent_time']

        # 破棄してもよい？（要調査）
        self.Lrs = 0.0
        # 破棄してもよい？（要調査）
        self.Ls = None

        self.Tr_i_n = np.full(24 * 365 * 4 * 3, a18.get_Tr_initial())  # i室のn時点における室温
        self.OT_i_n = np.zeros(24 * 365 * 4 * 3)  # i室のn時点における室の作用温度
        self.OTset = 0.0  # i室のn時点における室の空調設定作用温度(目標作用温度)
        self.Ts_i_k_n = np.zeros((0, 24 * 365 * 4 * 3))  # i室の部位kにおけるn時点の室内側表面温度 (max(k)が不明なのであとで初期化

        self.xr_i_n = np.full(24 * 365 * 4 * 3, a18.get_xr_initial())  # i室のn時点における室絶対湿度
        self.RH_i_n = np.full(24 * 365 * 4 * 3, 50.0)  # i室のn時点における室相対湿度[%]

        self.Qfuns_i_n = np.zeros(24 * 365 * 4 * 3)
        self.rsolfun__i = math.nan  # 透過日射の内家具が吸収する割合[－]
        self.kc_i = s41.calc_kc_i()  # i室の人体表面における対流熱伝達率の総合熱伝達率に対する比
        self.kr_i = s41.calc_kr_i()  # i室の人体表面における放射熱伝達率の総合熱伝達率に対する比
        self.air_conditioning_demand = False  # 当該時刻の空調需要（0：なし、1：あり）
        self.prev_air_conditioning_mode = 0  # 前時刻の空調運転状態（0：停止、正：暖房、負：冷房）
        self.is_prev_window_open = False  # 前時刻の窓状態（0：閉鎖、1：開放）
        self.now_air_conditioning_mode = np.full(24 * 365 * 4 * 3, 0)  # 当該時刻の空調運転状態（0：なし、正：暖房、負：冷房）
        self.is_now_window_open_i_n = np.full(24 * 365 * 4 * 3, False)  # 当該時刻の窓状態（0：閉鎖、1：開放）
        self.Met_i_n = np.zeros(24 * 365 * 4 * 3)  # i室のn時点における代謝量[Met]
        self.Wme_i_n = np.zeros(24 * 365 * 4 * 3)  # i室のn時点における外部仕事[Met]
        self.Vel_i_n = np.full(24 * 365 * 4 * 3, 0.1)  # i室のn時点における相対風速[m/s]
        self.Clo_i_n = np.ones(24 * 365 * 4 * 3)  # i室のn時点における着衣量[Clo]
        self.PMV_i_n = np.zeros(24 * 365 * 4 * 3)  # i室のn時点におけるPMV(Predicted Mean Vote,予測温冷感申告)
        self.MRT_i_n = np.zeros(24 * 365 * 4 * 3)  # i室のn時点におけるMRV(平均放射温度)
        self.Lcs_i_n = np.zeros(24 * 365 * 4 * 3)  # i室のn時点における対流空調熱負荷
        self.Lrs_i_n = np.zeros(24 * 365 * 4 * 3)  # i室のn時点における放射空調熱負荷
        self.Lcl_i_n = np.zeros(24 * 365 * 4 * 3)  # i室のn時点における室加湿熱量
        self.Lrl_i_n = np.zeros(24 * 365 * 4 * 3)  # i室のn時点における放射空調の潜熱
        self.is_radiative_heating = False
        self.Lrcap_i = 0.0  # 放射暖房最大能力

        # 暖房設備仕様の読み込み

        # 放射暖房有無（Trueなら放射暖房あり）
        self.is_radiative_heating = a22.read_is_radiative_heating(d_room)

        # 放射暖房最大能力[W]
        self.Lrcap_i = a22.read_radiative_heating_max_capacity(d_room)

        # 冷房設備仕様の読み込み

        # 放射冷房有無（Trueなら放射冷房あり）
        self.is_radiative_cooling = a22.read_is_radiative_cooling(d_room)

        # 放射冷房最大能力[W]
        self.radiative_cooling_max_capacity = a22.read_is_radiative_cooling(d_room)

        # 熱交換器種類
        self.heat_exchanger_type = a22.read_heat_exchanger_type(d_room)

        # 定格冷房能力[W]
        self.convective_cooling_rtd_capacity = a22.read_convective_cooling_rtd_capacity(d_room)

        # 家具の熱容量、湿気容量の計算
        # Capfun:家具熱容量[J/K]、Cfun:家具と室空気間の熱コンダクタンス[W/K]
        # Gf_i:湿気容量[kg/(kg/kg(DA))]、Cx_i:湿気コンダクタンス[kg/(s･kg/kg(DA))]
        self.Capfun = a14.get_Capfun(self.v_room_cap_i)
        self.Cfun = a14.get_Cfun(self.Capfun)
        self.Tfun_i_n = np.full(24 * 365 * 4 * 3, a18.get_Tfun_initial())  # i室のn時点における家具の温度
        self.Qfunl_i_n = np.zeros(24 * 365 * 4 * 3)  # i室のn時点における家具の日射吸収熱量
        self.Qsolfun_i_n = np.zeros(24 * 365 * 4 * 3)
        self.Gf_i = a14.get_Gf(self.v_room_cap_i)  # i室の備品類の湿気容量
        self.Cx_i = a14.get_Cx(self.Gf_i)  # i室の備品類と室空気間の湿気コンダクタンス
        self.xf_i_n = np.full(24 * 365 * 4 * 3, a18.get_xf_initial())  # i室のn時点における備品類の絶対湿度
        self.Ghum_i_n = np.zeros(24 * 365 * 4 * 3)

        self.xeout_i_n = np.zeros(24 * 365 * 4 * 3)  # i室のn時点におけるルームエアコン熱交換器出口の絶対湿度
        self.Vac_n = np.zeros(24 * 365 * 4 * 3)  # i室のn時点におけるエアコンの風量[m3/s]

        # i室のn時点における窓開放時通風量
        # 室空気の熱容量
        ca = a18.get_ca()
        rhoa = a18.get_rhoa()
        self.Hcap = self.v_room_cap_i * rhoa * ca
        # print(self.Hcap)

        self.Beta_i = 0.0  # 放射暖房対流比率

        # ********** 計算準備14 局所換気スケジュール、機器発熱スケジュール、
        # 照明発熱スケジュール、人体発熱スケジュールの読み込み **********

        # 局所換気スケジュールの読み込み
        self.local_vent_amount_schedule = a29.read_local_vent_schedules_from_json(d_room)

        # 機器発熱スケジュールの読み込み
        self.heat_generation_appliances_schedule, \
        self.heat_generation_cooking_schedule, \
        self.vapor_generation_cooking_schedule = a30.read_internal_heat_schedules_from_json(d_room)

        # 照明発熱スケジュールの読み込み
        self.heat_generation_lighting_schedule = a31.read_lighting_schedules_from_json(d_room)

        # 在室人数スケジュールの読み込み
        self.number_of_people_schedule = a32.read_resident_schedules_from_json(d_room)

        # 空調スケジュールの読み込み
        #   設定温度上限値, degree C * 365* 96
        #   設定温度下限値, degree C * 365* 96
        #   PMV上限値, degree C * 365* 96
        #   PMV下限値, degree C * 365* 96
        self.is_upper_temp_limit_set_schedule, \
            self.is_lower_temp_limit_set_schedule, \
            self.pmv_upper_limit_schedule, \
            self.pmv_lower_limit_schedule = a13.read_air_conditioning_schedules_from_json(d_room)

        # ********** 計算準備6 隣室間換気の読み込み **********

        self.Hhums = np.zeros(24 * 365 * 4 * 3)
        self.Hhuml = np.zeros(24 * 365 * 4 * 3)

