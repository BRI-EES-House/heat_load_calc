import numpy as np
import math

import s4_1_sensible_heat as s41

import a1_calculation_surface_temperature as a1
from a4_weather import enmWeatherComponent, WeaData, get_datetime_list
import a14_furniture as a14
import a15_air_flow_rate_rac as a15
import a12_indoor_radiative_heat_transfer as a12
import a13_Win_ACselect as a13
import a18_initial_value_constants as a18
import a20_room_spec as a20
import a21_next_vent_spec as a21
import a22_radiative_heating_spec as a22
import a23_surface_heat_transfer_coefficient as a23
import a29_local_vent_schedule as a29
import a30_internal_heat_schedule as a30
import a31_lighting_schedule as a31
import a32_resident_schedule as a32
import a34_building_part_summarize as a34

from Surface import Surface

"""
付録20．空間の定義
付録21．隣室間換気の定義
付録22．室供給熱量の最大能力の定義
"""


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
    FsolFlr = 0.5  # 床の日射吸収比率

    # 初期化
    def __init__(self, d_room):
        """
        :param Gdata:
        :param ExsrfMng:
        :param SunbrkMng:
        :param roomname: 室用途（主たる居室、その他居室、非居室）
        :param HeatCcap:
        :param HeatRcap:
        :param CoolCcap:
        :param Vol:
        :param Fnt:
        :param Vent:
        :param Inf:
        :param CrossVentRoom:
        :param is_radiative_heating:
        :param Beta_i:
        :param RoomtoRoomVents:
        :param input_surfaces:
        """
        self.name = d_room['name']  # 室名称
        self.room_type = d_room['room_type']  # 室用途（1:主たる居室、2:その他居室、3:非居室）
        self.AnnualLoadcCs = 0.0  # 年間顕熱冷房熱負荷（主暖房）
        self.AnnualLoadcHs = 0.0  # 年間顕熱暖房熱負荷（対流成分）
        self.AnnualLoadcCl = 0.0  # 年間潜熱冷房熱負荷（対流成分）
        self.AnnualLoadcHl = 0.0  # 年間潜熱暖房熱負荷（対流成分）
        self.AnnualLoadrCs = 0.0  # 年間顕熱冷房熱負荷（放射成分）
        self.AnnualLoadrHs = 0.0  # 年間顕熱暖房熱負荷（放射成分）
        self.AnnualLoadrCl = 0.0  # 年間潜熱冷房熱負荷（放射成分）
        self.AnnualLoadrHl = 0.0  # 年間潜熱暖房熱負荷（放射成分）
        self.Lrs = 0.0
        self.Ls = None

        self.Tr_i_n = np.full(24 * 365 * 4, a18.get_Tr_initial())  # i室のn時点における室温
        self.OT_i_n = np.zeros(24 * 365 * 4)  # i室のn時点における室の作用温度
        self.OTset = 0.0  # i室のn時点における室の空調設定作用温度(目標作用温度)
        self.Ts_i_k_n = np.zeros((0, 24 * 365 * 4))  # i室の部位kにおけるn時点の室内側表面温度 (max(k)が不明なのであとで初期化

        self.xr_i_n = np.full(24 * 365 * 4, a18.get_xr_initial())  # i室のn時点における室絶対湿度
        self.RH_i_n = np.full(24 * 365 * 4, 50.0)  # i室のn時点における室相対湿度[%]

        self.Qfuns_i_n = np.zeros(24 * 365 * 4)
        self.rsolfun__i = math.nan  # 透過日射の内家具が吸収する割合[－]
        self.kc_i = s41.calc_kc_i()  # i室の人体表面における対流熱伝達率の総合熱伝達率に対する比
        self.kr_i = s41.calc_kr_i()  # i室の人体表面における放射熱伝達率の総合熱伝達率に対する比
        self.air_conditioning_demand = False  # 当該時刻の空調需要（0：なし、1：あり）
        self.prev_air_conditioning_mode = 0  # 前時刻の空調運転状態（0：停止、正：暖房、負：冷房）
        self.is_prev_window_open = False  # 前時刻の窓状態（0：閉鎖、1：開放）
        self.now_air_conditioning_mode = 0  # 当該時刻の空調運転状態（0：なし、正：暖房、負：冷房）
        self.is_now_window_open_i_n = np.full(24 * 365 * 4, False)  # 当該時刻の窓状態（0：閉鎖、1：開放）
        self.Met_i_n = np.zeros(24 * 365 * 4)  # i室のn時点における代謝量[Met]
        self.Wme_i_n = np.zeros(24 * 365 * 4)  # i室のn時点における外部仕事[Met]
        self.Vel_i_n = np.full(24 * 365 * 4, 0.1)  # i室のn時点における相対風速[m/s]
        self.Clo_i_n = np.ones(24 * 365 * 4)  # i室のn時点における着衣量[Clo]
        self.PMV_i_n = np.zeros(24 * 365 * 4)  # i室のn時点におけるPMV(Predicted Mean Vote,予測温冷感申告)
        self.MRT_i_n = np.zeros(24 * 365 * 4)  # i室のn時点におけるMRV(平均放射温度)
        self.Lcs_i_n = np.zeros(24 * 365 * 4)  # i室のn時点における対流空調熱負荷
        self.Lrs_i_n = np.zeros(24 * 365 * 4)  # i室のn時点における放射空調熱負荷
        self.Lcl_i_n = np.zeros(24 * 365 * 4)  # i室のn時点における室加湿熱量
        self.Lrl_i_n = np.zeros(24 * 365 * 4)  # i室のn時点における放射空調の潜熱
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

        # 室気積[m3]
        self.volume = a20.read_volume(d_room)
        rhoa = a18.get_rhoa()
        self.Ga = self.volume * rhoa  # 室空気の質量[kg]

        # 家具の熱容量、湿気容量の計算
        # Capfun:家具熱容量[J/K]、Cfun:家具と室空気間の熱コンダクタンス[W/K]
        # Gf_i:湿気容量[kg/(kg/kg(DA))]、Cx_i:湿気コンダクタンス[kg/(s･kg/kg(DA))]
        self.Capfun = a14.get_Capfun(self.volume)
        self.Cfun = a14.get_Cfun(self.Capfun)
        self.Tfun_i_n = np.full(24 * 365 * 4, a18.get_Tfun_initial())  # i室のn時点における家具の温度
        self.Qfunl_i_n = np.zeros(24 * 365 * 4)  # i室のn時点における家具の日射吸収熱量
        self.Qsolfun_i_n = np.zeros(24 * 365 * 4)
        self.Gf_i = a14.get_Gf(self.volume)  # i室の備品類の湿気容量
        self.Cx_i = a14.get_Cx(self.Gf_i)  # i室の備品類と室空気間の湿気コンダクタンス
        self.xf_i_n = np.full(24 * 365 * 4, a18.get_xf_initial())  # i室のn時点における備品類の絶対湿度
        self.Ghum_i_n = np.zeros(24 * 365 * 4)

        self.xeout_i_n = np.zeros(24 * 365 * 4)  # i室のn時点におけるルームエアコン熱交換器出口の絶対湿度
        self.Vac_n = np.zeros(24 * 365 * 4)  # i室のn時点におけるエアコンの風量[m3/s]
        self.NV_i_n = np.full(24 * 365 * 4, self.volume * a20.read_natural_vent_time(d_room))
        # i室のn時点における窓開放時通風量
        # 室空気の熱容量
        ca = a18.get_ca()
        self.Hcap = self.volume * rhoa * ca
        # print(self.Hcap)

        # 計画換気量
        self.Vent = a20.read_vent(d_room)
        self.Inf = 0.0  # すきま風量（暫定値）
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
        self.is_upper_temp_limit_set_schedule, \
        self.is_lower_temp_limit_set_schedule, \
        self.pmv_upper_limit_schedule, \
        self.pmv_lower_limit_schedule = a13.read_air_conditioning_schedules_from_json(d_room)

        # ********** 計算準備6 隣室間換気の読み込み **********

        # 室間換気量クラスの構築
        self.Rtype_i_j = a21.read_upstream_room_type(d_room)
        self.Vnext_i_j = a21.read_next_vent_volume(d_room)

        # i室の部位の読み込み
        self.surf_i = Surface(d_room['boundaries'])

        self.QGT_i_n = np.zeros(24 * 365 * 4)
        self.surfG_i = None
        self.NsurfG_i = 0

    def init(self, weather, solar_position, I_DN_n, I_sky_n, RN_n, To_n):
        # i室の部位の初期化
        self.surf_i.init(solar_position, I_DN_n, I_sky_n, RN_n, To_n, weather.AnnualTave)

        # 透過日射熱取得の集約し、i室のn時点における透過日射熱取得 QGT_i_n を計算
        self.QGT_i_n = np.sum(self.surf_i.QGT_i_k_n, axis=0)

        # i室の境界条件が同じ部位kを集約し、部位gを作成
        self.surfG_i = a34.GroupedSurface(self.surf_i)

        # i室の部位の面数(集約後)
        self.NsurfG_i = self.surfG_i.NsurfG_i

        # 部位ごとの計算結果用変数
        self.Ts_i_k_n = np.zeros((self.NsurfG_i, 24 * 365 * 4))
        self.Teo_i_k_n = np.full((self.NsurfG_i, 24 * 365 * 4), a18.get_Teo_initial())  # i室の部位kにおけるn時点の裏面相当温度
        self.Tei_i_k_n = np.zeros((self.NsurfG_i, 24 * 365 * 4))  # i室の部位kにおけるn時点の室内等価温度
        self.TsdA_l_n_m = np.full((self.NsurfG_i, 24 * 365 * 4, 12), a18.get_TsdT_initial())  # （26）式中の〖CVL〗_(i,l)の計算式右辺
        self.TsdT_l_n_m = np.full((self.NsurfG_i, 24 * 365 * 4, 12), a18.get_TsdT_initial())  # （26）式中の〖CVL〗_(i,l)の計算式右辺
        self.Sol_i_g_n = np.zeros((self.NsurfG_i, 24 * 365 * 4))
        self.oldqi = self.surfG_i.oldqi

        eps_m = a18.get_eps()

        # 部位の人体に対する形態係数を計算 表6
        self.Fot_i_g = a12.calc_form_factor_for_human_body(self.surfG_i.A_i_g, self.surfG_i.is_solar_absorbed_inside)

        # 合計面積の計算
        self.A_total_i = np.sum(self.surfG_i.A_i_g)

        # 合計床面積の計算
        A_fs_i = np.sum(self.surfG_i.A_i_g * self.surfG_i.is_solar_absorbed_inside)

        # ルームエアコンの仕様の設定 式(107)-(111)
        self.qrtd_c_i = a15.get_qrtd_c(A_fs_i)
        self.qmax_c_i = a15.get_qmax_c(self.qrtd_c_i)
        self.qmin_c_i = a15.get_qmin_c()
        self.Vmax_i = a15.get_Vmax(self.qrtd_c_i)
        self.Vmin_i = a15.get_Vmin(self.Vmax_i)

        # 放射暖房の発熱部位の設定（とりあえず床発熱） 表7
        self.flr_i_k = a12.get_flr(self.surfG_i.A_i_g, A_fs_i, self.is_radiative_heating,
                                   self.surfG_i.is_solar_absorbed_inside)

        # 微小点に対する室内部位の形態係数の計算（永田先生の方法） 式(94)
        FF_m = a12.calc_form_factor_of_microbodies(self.name, self.surfG_i.A_i_g)

        # 表面熱伝達率の計算 式(123) 表16
        self.hr_i_g_n, self.hc_i_g_n = a23.calc_surface_transfer_coefficient(eps_m, FF_m, self.surfG_i.hi_i_g_n)

        # 平均放射温度計算時の各部位表面温度の重み計算 式(101)
        self.F_mrt_i_g = a12.get_F_mrt_i_g(self.surfG_i.A_i_g, self.hr_i_g_n)

        # 日射吸収比率の計算

        # 床の室内部位表面吸収比率の設定 表(5) 床の場合
        self.Rsol_floor_i_g = a12.get_SolR(self.surfG_i.A_i_g, self.surfG_i.is_solar_absorbed_inside, A_fs_i)

        self.Rsol_fun_i = a12.calc_absorption_ratio_of_transmitted_solar_radiation()

        # *********** 室内表面熱収支計算のための行列作成 ***********

        # FIA, FLBの作成 式(26)
        FIA_i_l = a1.get_FIA(self.surfG_i.RFA0, self.hc_i_g_n)
        FLB_i_l = a1.get_FLB(self.surfG_i.RFA0, self.flr_i_k, self.Beta_i, self.surfG_i.A_i_g)

        # 行列AX 式(25)
        self.AX_k_l = a1.get_AX(self.surfG_i.RFA0, self.hr_i_g_n, self.F_mrt_i_g, self.surfG_i.hi_i_g_n, self.NsurfG_i)

        # WSR, WSB の計算 式(24)
        self.WSR_i_k = a1.get_WSR(self.AX_k_l, FIA_i_l)
        self.WSB_i_k = a1.get_WSB(self.AX_k_l, FLB_i_l)

        # ****************************************************

        # BRMの計算 式(5)
        self.BRM_i = s41.get_BRM_i(
            Hcap=self.Hcap,
            WSR_i_k=self.WSR_i_k,
            Cap_fun_i=self.Capfun,
            C_fun_i=self.Cfun,
            Vent=self.Vent,
            local_vent_amount_schedule=self.local_vent_amount_schedule,
            A_i_k=self.surfG_i.A_i_g,
            hc_i_k_n=self.hc_i_g_n,
            V_nxt=self.Vnext_i_j
        )

        # BRLの計算 式(7)
        self.BRL_i = s41.get_BRL_i(
            Beta_i=self.Beta_i,
            WSB_i_k=self.WSB_i_k,
            A_i_k=self.surfG_i.A_i_g,
            hc_i_k_n=self.hc_i_g_n
        )


def create_spaces(rooms, weather, solar_position):
    objSpace = {}

    dtlist = get_datetime_list()
    I_DN_n = np.zeros(24 * 365 * 4)
    I_sky_n = np.zeros(24 * 365 * 4)
    RN_n = np.zeros(24 * 365 * 4)
    To_n = np.zeros(24 * 365 * 4)

    for n, dtmNow in enumerate(dtlist):
        # i室のn時点における法線面直達日射量
        I_DN_n[n] = WeaData(weather, enmWeatherComponent.I_DN, dtmNow, solar_position, n)

        # i室のn時点における水平面天空日射量
        I_sky_n[n] = WeaData(weather, enmWeatherComponent.I_sky, dtmNow, solar_position, n)

        # i室のn時点における夜間放射量
        RN_n[n] = WeaData(weather, enmWeatherComponent.RN, dtmNow, solar_position, n)

        # i室のn時点における外気温度
        To_n[n] = WeaData(weather, enmWeatherComponent.To, dtmNow, solar_position, n)

    for room in rooms:
        space = Space(room)
        space.init(weather, solar_position, I_DN_n, I_sky_n, RN_n, To_n)
        objSpace[room['name']] = space
    return objSpace
