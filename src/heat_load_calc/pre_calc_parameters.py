import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Callable, Optional, Tuple
import logging
from enum import Enum

from heat_load_calc.matrix_method import v_diag
from heat_load_calc.building import Building
from heat_load_calc import ot_target, next_condition, schedule, rooms, boundaries, equipments, \
    infiltration, occupants_form_factor, shape_factor, solar_absorption, mechanical_ventilations, operation_, interval
from heat_load_calc.weather import Weather
from heat_load_calc.schedule import Schedule
from heat_load_calc.rooms import Rooms
from heat_load_calc.boundaries import Boundaries

class ACMethod(Enum):

    PMV = 'pmv'
    SIMPLE = 'simple'
    OT = 'ot'
    AIR_TEMPERATURE = 'air_temperature'


@dataclass
class PreCalcParameters:

    # Weather Class
    #   ステップnの外気温度, degree C, [N+1]
    #   ステップnの外気絶対湿度, kg / kg(DA), [N+1]
    #   ステップnの法線面直達日射量, W / m2, [N+1]
    #   ステップnの水平面天空日射量, W / m2, [N+1]
    #   ステップnの夜間放射量, W / m2, [N+1]
    #   ステップnの太陽高度, rad, [N+1]
    #   ステップnの太陽方位角, rad, [N+1]
    weather: Weather

    # Schedule Class
    #   ステップnの室iにおける人体発熱を除く内部発熱, W, [i, N]
    #   ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [i, N]
    #   ステップnの室iにおける局所換気量, m3/s, [i, N]
    #   ステップnの室iにおける在室人数, [i, N]
    #   ステップnの室iにおける空調需要, [i, N]
    #   ステップnの室iにおける空調モード, [i, N]
    scd: Schedule

    # Rooms Class
    #   空間の数, [i]
    #   空間のID, [i]
    #   空間の名前, [i]
    #   室iの容積, m3, [i, 1]
    #   室iの備品等の熱容量, J/K, [i, 1]
    #   室iの備品等の湿気容量, kg/(kg/kgDA), [i, 1]
    #   室iの空気と備品等間の熱コンダクタンス, W/K, [i, 1]
    #   室iの空気と備品等間の湿気コンダクタンス, kg/(s (kg/kgDA)), [i, 1]
    #   室iの自然風利用時の換気量, m3/s, [i, 1]
    #   室iの在室者のMet値, [i, 1]
    rms: Rooms

    # Boundaries Class
    #   境界の数
    #   id_js: 境界jのID, [j, 1]
    #   境界jの名前, [j]
    #   境界jの名前2, [j]
    #   p_is_js: 室iと境界jの関係を表す係数（境界jから室iへの変換）, [i, j]
    #   p_js_is: 室iと境界jの関係を表す係数（室iから境界jへの変換）
    #   床かどうか, [j, 1]
    #   地盤かどうか, [j, 1]
    #   境界jの裏面温度に他の境界の等価温度が与える影響, [j, j]
    #   境界jの裏面温度に室温が与える影響, [j, i]
    bs: Boundaries

    # region 空間に関すること

    # ステップnの室iにおける機械換気量（全般換気量+局所換気量）, m3/s, [i, 8760*4]
    v_vent_mec_is_ns: np.ndarray

    # ステップ n における室 i に設置された備品等による透過日射吸収熱量, W, [i, n+1]
    q_sol_frt_is_ns: np.ndarray

    # ステップ n における室 i の窓の透過日射熱取得, W, [i, n+1]
    q_trs_sol_is_ns: np.ndarray

    # endregion

    # 室iの隣室からの機械換気量, m3/s, [i, i]
    v_vent_int_is_is: np.ndarray

    # 境界jが地盤かどうか, [j, 1]
    is_ground_js: np.ndarray

    # 境界jの面積, m2, [j, 1]
    a_s_js: np.ndarray

    # 放射暖房対流比率, [i, 1]
    beta_h_is: np.ndarray
    beta_c_is: np.ndarray

    # === 境界jに関すること ===

    # 境界jの項別公比法における項mの公比, [j, 12]
    r_js_ms: np.ndarray

    # 境界jの貫流応答係数の初項, [j]
    phi_t0_js: np.ndarray

    # 境界jの吸熱応答係数の初項, m2K/W, [j]
    phi_a0_js: np.ndarray

    # 境界jの項別公比法における項mの貫流応答係数の第一項, [j,12]
    phi_t1_js_ms: np.ndarray

    # 境界jの項別公比法における項mの吸熱応答係数の第一項 , m2K/W, [j, 12]
    phi_a1_js_ms: np.ndarray

    # ステップnの境界jにおける透過日射熱取得量のうち表面に吸収される日射量, W/m2, [j, 8760*4]
    q_s_sol_js_ns: np.ndarray

    f_ax_js_js: np.ndarray

    # 室iの在室者に対する境界j*の形態係数
    f_mrt_hum_is_js: np.ndarray

    # 平均放射温度計算時の境界 j* の表面温度が境界 j に与える重み, [j, j]
    f_mrt_is_js: np.ndarray

    # 境界jにおける室内側放射熱伝達率, W/m2K, [j, 1]
    h_s_r_js: np.ndarray

    # 境界jにおける室内側対流熱伝達率, W/m2K, [j, 1]
    h_s_c_js: np.ndarray

    # 境界jにおけるシミュレーションに用いる表面熱伝達抵抗での熱貫流率, W/m2K, [j,1]
    simulation_u_value: np.ndarray

    # WSR, WSB の計算 式(24)
    f_wsr_js_is: np.ndarray

    # 床暖房の発熱部位？
    f_flr_h_js_is: np.ndarray
    f_flr_c_js_is: np.ndarray

    # WSC, W, [j, n]
    f_wsc_js_ns: np.ndarray

    # 温度差係数, -, [j, 1]
    k_eo_js: np.ndarray

    # ステップ n の境界 j における相当外気温度, ℃, [j, n]
    theta_o_eqv_js_ns: np.ndarray

    get_operation_mode_is_n: Callable[[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray], np.ndarray]

    get_theta_target_is_n: Callable[[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]]

    get_infiltration: Callable[[np.ndarray, float], np.ndarray]

    calc_next_temp_and_load: Callable[[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray, np.ndarray]]

    get_f_l_cl: Callable[[np.ndarray, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]


@dataclass
class PreCalcParametersGround:

    # 地盤の数
    n_grounds: int

    # 地盤jの項別公比法における項mの公比, [j, 12]
    r_js_ms: np.ndarray

    # 境界jの貫流応答係数の初項, [j]
    phi_t0_js: np.ndarray

    # 地盤jの吸熱応答係数の初項, m2K/W, [j, 1]
    phi_a0_js: np.ndarray

    # 境界jの項別公比法における項mの貫流応答係数の第一項, [j,12]
    phi_t1_js_ms: np.ndarray

    # 地盤jの項別公比法における項mの吸熱応答係数の第一項 , m2K/W, [j, 12]
    phi_a1_js_ms: np.ndarray

    # 地盤jにおける室内側放射熱伝達率, W/m2K, [j, 1]
    h_s_r_js: np.ndarray

    # 地盤jにおける室内側対流熱伝達率, W/m2K, [j, 1]
    h_s_c_js: np.ndarray

    # 温度差係数, -, [j, 1]
    k_eo_js: np.ndarray

    # ステップ n の境界 j における相当外気温度, ℃, [j, n]
    theta_o_eqv_js_ns: np.ndarray


def make_pre_calc_parameters(
        itv: interval.Interval,
        rd: Dict,
        weather: Weather,
        scd: schedule.Schedule,
        q_trs_sol_is_ns: Optional[np.ndarray] = None,
        theta_o_eqv_js_ns: Optional[np.ndarray] = None
) -> Tuple[PreCalcParameters, PreCalcParametersGround]:
    """助走計算用パラメータの生成

    Args:
        itv: 時間間隔
        rd: 住宅計算条件
        weather: Weatherクラス
        scd: スケジュールクラス
        q_trs_sol_is_ns: optional テスト用　値を指定することができる。未指定の場合は計算する。
        theta_o_eqv_js_ns: optional テスト用　値を指定することができる。未指定の場合は計算する。

    Returns:
        PreCalcParameters および PreCalcParametersGround のタプル
    """

    logger = logging.getLogger('HeatLoadCalc').getChild('core').getChild('pre_calc_parameters')

    delta_t = itv.get_delta_t()

    # Building Class
    building = Building.create_building(d=rd['building'])

    # Rooms Class
    rms = rooms.Rooms(ds=rd['rooms'])

    # region boundaries

    bs = boundaries.Boundaries(id_rm_is=rms.id_rm_is, bs_list=rd['boundaries'], w=weather)

    # 温度差係数
    k_eo_js = bs.k_eo_js

    # 境界jの日射吸収の有無, [j, 1]
    p_s_sol_abs_js = bs.p_s_sol_abs_js

    # 境界jの室内側表面放射熱伝達率, W/m2K, [j, 1]
    h_s_r_js = bs.h_s_r_js

    # 境界jの室内側表面対流熱伝達率, W/m2K, [j, 1]
    h_s_c_js = bs.h_s_c_js

    # シミュレーションに用いる表面熱伝達抵抗での熱貫流率, W/m2K, [j,1]
    simulation_u_value = bs.simulation_u_value

    # 境界jの面積, m2, [j, 1]
    a_s_js = bs.a_s_js

    # 境界jの吸熱応答係数の初項, m2K/W, [j, 1]
    phi_a0_js = bs.phi_a0_js

    # 境界jの項別公比法における項mの吸熱応答係数の第一項 , m2K/W, [j, 12]
    phi_a1_js_ms = bs.phi_a1_js_ms

    # 境界jの貫流応答係数の初項, [j, 1]
    phi_t0_js = bs.phi_t0_js

    # 境界jの項別公比法における項mの貫流応答係数の第一項, [j, 12]
    phi_t1_js_ms = bs.phi_t1_js_ms

    # 境界jの項別公比法における項mの公比, [j, 12]
    r_js_ms = bs.r_js_ms

    # ステップ n の室 i における窓の透過日射熱取得, W, [n]
    #　このif文は、これまで実施してきたテストを維持するために設けている。
    # いずれテスト方法を整理して、csvで与える方式を削除すべきである。
    # CSVで与える方式があることは（将来的に削除予定であるため）仕様書には記述しない。
    if q_trs_sol_is_ns is None:
        q_trs_sol_is_ns = bs.q_trs_sol_is_ns
    else:
        # ステップn+1に対応するために0番要素に最終要素を代入
        q_trs_sol_is_ns = np.append(q_trs_sol_is_ns, q_trs_sol_is_ns[:, 0:1], axis=1)

    # ステップ n の境界 j における相当外気温度, ℃, [j, n]
    #　このif文は、これまで実施してきたテストを維持するために設けている。
    # いずれテスト方法を整理して、csvで与える方式を削除すべきである。
    # CSVで与える方式があることは（将来的に削除予定であるため）仕様書には記述しない。
    if theta_o_eqv_js_ns is None:
        theta_o_eqv_js_ns = bs.theta_o_eqv_js_ns
    else:
        # ステップn+1に対応するために0番要素に最終要素を代入
        theta_o_eqv_js_ns = np.append(theta_o_eqv_js_ns, theta_o_eqv_js_ns[:, 0:1], axis=1)

    # endregion

    # region mechanical ventilations

    mvs = mechanical_ventilations.MechanicalVentilations(
        vs=rd['mechanical_ventilations'],
        n_rm=rms.n_rm
    )

    # 室iの機械換気量（局所換気を除く）, m3/s, [i, 1]
    v_vent_mec_general_is = mvs.get_v_vent_mec_general_is()

    # 室iの隣室iからの機械換気量, m3/s, [i, i]
    v_vent_int_is_is = mvs.get_v_vent_int_is_is()

    # endregion

    # region equipments

    es = equipments.Equipments(dict_equipments=rd['equipments'], n_rm=rms.n_rm, n_b=bs.n_b, bs=bs)

    # 室iの暖房方式として放射空調が設置されているかどうか。  bool値, [i, 1]
    is_radiative_heating_is = es.get_is_radiative_heating_is()

    # 室iの暖房方式として放射空調が設置されている場合の、放射暖房最大能力, W, [i, 1]
    q_rs_h_max_is = es.get_q_rs_h_max_is()

    # 室iの冷房方式として放射空調が設置されているかどうか。  bool値, [i, 1]
    is_radiative_cooling_is = es.get_is_radiative_cooling_is()

    # 室iの冷房方式として放射空調が設置されている場合の、放射冷房最大能力, W, [i, 1]
    q_rs_c_max_is = es.get_q_rs_c_max_is()

    # 室 i の放射暖房設備の対流成分比率, -, [i, 1]
    beta_h_is = es.get_beta_h_is()

    # 室 i の放射冷房設備の対流成分比率, -, [i, 1]
    beta_c_is = es.get_beta_c_is()

    # 室 i の放射暖房の放熱量の放射成分に対する境界 j の室内側表面の吸収比率, - [j, i]
    f_flr_h_js_is = es.get_f_flr_h_js_is()

    # 室 i の放射冷房の吸熱量の放射成分に対する境界 j の室内側表面の放熱比率, - [j, i]
    f_flr_c_js_is = es.get_f_flr_c_js_is()

    # 次の係数を求める関数
    #   ステップ n　からステップ n+1 における係数 f_l_cl_wgt, kg/s(kg/kg(DA)), [i, i]
    #   ステップ n　からステップ n+1 における係数 f_l_cl_cst, kg/s, [i, 1]
    get_f_l_cl = es.make_get_f_l_cl_funcs()

    # endregion

    # 室 i の在室者に対する境界jの形態係数, [i, j]
    f_mrt_hum_is_js = occupants_form_factor.get_f_mrt_hum_js(
        n_rm=rms.n_rm,
        n_b=bs.n_b,
        p_is_js=bs.p_is_js,
        a_s_js=a_s_js,
        is_floor_js=bs.is_floor_js
    )

    # 室 i の微小球に対する境界 j の形態係数, -, [i, j]
    f_mrt_is_js = shape_factor.get_f_mrt_is_js(a_s_js=a_s_js, h_s_r_js=h_s_r_js, p_is_js=bs.p_is_js)

    # ステップ n からステップ n+1 における室 i の機械換気量（全般換気量と局所換気量の合計値）, m3/s, [i, 1]
    v_vent_mec_is_ns = get_v_vent_mec_is_ns(
        v_vent_mec_general_is=v_vent_mec_general_is,
        v_vent_mec_local_is_ns=scd.v_mec_vent_local_is_ns
    )

    # ステップ n における室 i に設置された備品等による透過日射吸収熱量, W, [i, n+1]
    q_sol_frt_is_ns = solar_absorption.get_q_sol_frt_is_ns(q_trs_sor_is_ns=q_trs_sol_is_ns)

    # ステップ n における境界 j の透過日射吸収熱量, W/m2, [j, n]
    q_s_sol_js_ns = solar_absorption.get_q_s_sol_js_ns(
        p_is_js=bs.p_is_js,
        a_s_js=a_s_js,
        p_s_sol_abs_js=p_s_sol_abs_js,
        p_js_is=bs.p_js_is,
        q_trs_sol_is_ns=q_trs_sol_is_ns
    )

    # 係数 f_AX, -, [j, j]
    f_ax_js_js = get_f_ax_js_is(
        f_mrt_is_js=f_mrt_is_js,
        h_s_c_js=h_s_c_js,
        h_s_r_js=h_s_r_js,
        k_ei_js_js=bs.k_ei_js_js,
        p_js_is=bs.p_js_is,
        phi_a0_js=phi_a0_js,
        phi_t0_js=phi_t0_js
    )

    # 係数 f_FIA, -, [j, i]
    f_fia_js_is = get_f_fia_js_is(
        h_s_c_js=h_s_c_js,
        h_s_r_js=h_s_r_js,
        k_ei_js_js=bs.k_ei_js_js,
        p_js_is=bs.p_js_is,
        phi_a0_js=phi_a0_js,
        phi_t0_js=phi_t0_js,
        k_s_r_js_is=bs.k_s_r_js_is
    )

    # 係数 f_CRX, degree C, [j, n]
    f_crx_js_ns = get_f_crx_js_ns(
        h_s_c_js=h_s_c_js,
        h_s_r_js=h_s_r_js,
        k_ei_js_js=bs.k_ei_js_js,
        phi_a0_js=phi_a0_js,
        phi_t0_js=phi_t0_js,
        q_s_sol_js_ns=q_s_sol_js_ns,
        k_eo_js=k_eo_js,
        theta_o_eqv_js_ns=theta_o_eqv_js_ns
    )

    # 係数 f_WSR, -, [j, i]
    f_wsr_js_is = get_f_wsr_js_is(f_ax_js_js=f_ax_js_js, f_fia_js_is=f_fia_js_is)

    # 係数 f_{WSC, n}, degree C, [j, n]
    f_wsc_js_ns = get_f_wsc_js_ns(f_ax_js_js=f_ax_js_js, f_crx_js_ns=f_crx_js_ns)

    # region 読み込んだ値から新たに関数を作成する

    ac_method = ACMethod(rd['common']['ac_method'])

    if 'ac_config' in rd['common']:
        ac_config = rd['common']['ac_config']
    else:
        ac_config = [{'mode': 1, 'lower': 20.0, 'upper': 27.0}]

    # ac_method = 'simple'

    get_operation_mode_is_n = operation_.make_get_operation_mode_is_n_function(
        ac_method=ac_method.value,
        ac_demand_is_ns=scd.ac_demand_is_ns,
        is_radiative_heating_is=is_radiative_heating_is,
        is_radiative_cooling_is=is_radiative_cooling_is,
        met_is=rms.met_is
    )

    get_theta_target_is_n = ot_target.make_get_theta_target_is_n_function(
        ac_method=ac_method.value,
        is_radiative_heating_is=is_radiative_heating_is,
        is_radiative_cooling_is=is_radiative_cooling_is,
        met_is=rms.met_is,
        ac_setting_is_ns=scd.ac_demand_is_ns,
        ac_config=ac_config
    )

    # すきま風を計算する関数
    # 引数:
    #   theta_r_is_n: 時刻nの室温, degree C, [i,1]
    #   theta_o_n: 時刻n+1の外気温度, degree C
    # 戻り値:
    #   すきま風量, m3/s, [i,1]
    get_infiltration = infiltration.make_get_infiltration_function(
        v_rm_is=rms.v_rm_is,
        building=building
    )

    # 次のステップの室温と負荷を計算する関数
    calc_next_temp_and_load = next_condition.make_get_next_temp_and_load_function(
        ac_demand_is_ns=scd.ac_demand_is_ns,
        is_radiative_heating_is=is_radiative_heating_is,
        is_radiative_cooling_is=is_radiative_cooling_is,
        lr_h_max_cap_is=q_rs_h_max_is,
        lr_cs_max_cap_is=q_rs_c_max_is
    )

    # endregion




    pre_calc_parameters = PreCalcParameters(
        weather=weather,
        scd=scd,
        rms=rms,
        bs=bs,
        v_vent_int_is_is=v_vent_int_is_is,
        a_s_js=a_s_js,
        v_vent_mec_is_ns=v_vent_mec_is_ns,
        f_mrt_hum_is_js=f_mrt_hum_is_js,
        r_js_ms=r_js_ms,
        phi_t0_js=phi_t0_js,
        phi_a0_js=phi_a0_js,
        phi_t1_js_ms=phi_t1_js_ms,
        phi_a1_js_ms=phi_a1_js_ms,
        q_trs_sol_is_ns=q_trs_sol_is_ns,
        f_flr_h_js_is=f_flr_h_js_is,
        f_flr_c_js_is=f_flr_c_js_is,
        h_s_r_js=h_s_r_js,
        h_s_c_js=h_s_c_js,
        simulation_u_value=simulation_u_value,
        f_mrt_is_js=f_mrt_is_js,
        q_s_sol_js_ns=q_s_sol_js_ns,
        q_sol_frt_is_ns=q_sol_frt_is_ns,
        beta_h_is=beta_h_is,
        beta_c_is=beta_c_is,
        f_wsr_js_is=f_wsr_js_is,
        f_ax_js_js=f_ax_js_js,
        is_ground_js=bs.is_ground_js,
        f_wsc_js_ns=f_wsc_js_ns,
        get_operation_mode_is_n=get_operation_mode_is_n,
        get_theta_target_is_n=get_theta_target_is_n,
        get_infiltration=get_infiltration,
        calc_next_temp_and_load=calc_next_temp_and_load,
        get_f_l_cl=get_f_l_cl,
        k_eo_js=k_eo_js,
        theta_o_eqv_js_ns=theta_o_eqv_js_ns
    )

    # 地盤の数
    n_grounds = bs.n_ground

    pre_calc_parameters_ground = PreCalcParametersGround(
        n_grounds=n_grounds,
        r_js_ms=r_js_ms[bs.is_ground_js.flatten(), :],
        phi_a0_js=phi_a0_js[bs.is_ground_js.flatten(), :],
        phi_t0_js=phi_t0_js[bs.is_ground_js.flatten(), :],
        phi_a1_js_ms=phi_a1_js_ms[bs.is_ground_js.flatten(), :],
        phi_t1_js_ms=phi_t1_js_ms[bs.is_ground_js.flatten(), :],
        h_s_r_js=h_s_r_js[bs.is_ground_js.flatten(), :],
        h_s_c_js=h_s_c_js[bs.is_ground_js.flatten(), :],
        k_eo_js=k_eo_js[bs.is_ground_js.flatten(), :],
        theta_o_eqv_js_ns=theta_o_eqv_js_ns[bs.is_ground_js.flatten(), :]
    )

    return pre_calc_parameters, pre_calc_parameters_ground


def get_f_wsc_js_ns(f_ax_js_js, f_crx_js_ns):
    """

    Args:
        f_ax_js_js: 係数 f_{AX}, -, [j, j]
        f_crx_js_ns: 係数 f_{CRX,n}, degree C, [j, n]

    Returns:
        係数 f_{WSC,n}, degree C, [j, n]

    Notes:
        式(4.1)
    """

    return np.linalg.solve(f_ax_js_js, f_crx_js_ns)


def get_f_wsr_js_is(f_ax_js_js, f_fia_js_is):
    """

    Args:
        f_ax_js_js: 係数 f_AX, -, [j, j]
        f_fia_js_is: 係数 f_FIA, -, [j, i]

    Returns:
        係数 f_WSR, -, [j, i]

    Notes:
        式(4.2)
    """

    return np.linalg.solve(f_ax_js_js, f_fia_js_is)


def get_f_crx_js_ns(h_s_c_js, h_s_r_js, k_ei_js_js, phi_a0_js, phi_t0_js, q_s_sol_js_ns, k_eo_js, theta_o_eqv_js_ns):
    """

    Args:
        h_s_c_js: 境界 j の室内側対流熱伝達率, W/(m2 K), [j, 1]
        h_s_r_js: 境界 j の室内側放射熱伝達率, W/(m2 K), [j, 1]
        k_ei_js_js: 境界 j の裏面温度に境界　j∗ の等価温度が与える影響, -, [j, j]
        phi_a0_js: 境界 j の吸熱応答係数の初項, m2 K/W, [j, 1]
        phi_t0_js: 境界 j の貫流応答係数の初項, -, [j, 1]
        q_s_sol_js_ns: ステップ n における境界 j の透過日射吸収熱量, W/m2, [j, n]
        k_eo_js: 境界 j の裏面温度に境界 j の相当外気温度が与える影響, -, [j, 1]
        theta_o_eqv_js_ns: ステップ n における境界 j の相当外気温度, degree C, [j, 1]

    Returns:
        係数 f_CRX, degree C, [j, n]

    Notes:
        式(4.3)
    """

    return phi_a0_js * q_s_sol_js_ns\
        + phi_t0_js * np.dot(k_ei_js_js, q_s_sol_js_ns / (h_s_c_js + h_s_r_js))\
        + phi_t0_js * theta_o_eqv_js_ns * k_eo_js


def get_f_fia_js_is(h_s_c_js, h_s_r_js, k_ei_js_js, p_js_is, phi_a0_js, phi_t0_js, k_s_r_js_is):
    """

    Args:
        h_s_c_js: 境界 j の室内側対流熱伝達率, W/(m2 K), [j, 1]
        h_s_r_js: 境界 j の室内側放射熱伝達率, W/(m2 K), [j, 1]
        k_ei_js_js: 境界 j の裏面温度に境界　j∗ の等価温度が与える影響, -, [j, j]
        p_js_is: 室 i と境界 j の接続に関する係数（境界 j が室 i に接している場合は 1 とし、それ以外の場合は 0 とする。）, -, [j, i]
        phi_a0_js: 境界 j の吸熱応答係数の初項, m2 K/W, [j, 1]
        phi_t0_js: 境界 j の貫流応答係数の初項, -, [j, 1]

    Returns:
        係数 f_FIA, -, [j, i]

    Notes:
        式(4.4)
    """

    return phi_a0_js * h_s_c_js * p_js_is + np.dot(k_ei_js_js, p_js_is * h_s_c_js / (h_s_c_js + h_s_r_js)) * phi_t0_js + phi_t0_js * k_s_r_js_is


def get_f_ax_js_is(f_mrt_is_js, h_s_c_js, h_s_r_js, k_ei_js_js, p_js_is, phi_a0_js, phi_t0_js):
    """

    Args:
        f_mrt_is_js: 室 i の微小球に対する境界 j の形態係数, -, [i, j]
        h_s_c_js: 境界 j の室内側対流熱伝達率, W/(m2 K), [j, 1]
        h_s_r_js: 境界 j の室内側放射熱伝達率, W/(m2 K), [j, 1]
        k_ei_js_js: 境界 j の裏面温度に境界　j∗ の等価温度が与える影響, -, [j, j]
        p_js_is: 室 i と境界 j の接続に関する係数（境界 j が室 i に接している場合は 1 とし、それ以外の場合は 0 とする。）, -, [j, i]
        phi_a0_js: 境界 j の吸熱応答係数の初項, m2 K/W, [j, 1]
        phi_t0_js: 境界 j の貫流応答係数の初項, -, [j, 1]

    Returns:
        係数 f_AX, -, [j, j]

    Notes:
        式(4.5)
    """

    return v_diag(1.0 + phi_a0_js * (h_s_c_js + h_s_r_js)) \
        - np.dot(p_js_is, f_mrt_is_js) * h_s_r_js * phi_a0_js \
        - np.dot(k_ei_js_js, np.dot(p_js_is, f_mrt_is_js) * h_s_r_js / (h_s_c_js + h_s_r_js)) * phi_t0_js


def get_v_vent_mec_is_ns(v_vent_mec_general_is, v_vent_mec_local_is_ns):
    """

    Args:
        v_vent_mec_general_is: ステップ n からステップ n+1 における室 i の機械換気量（全般換気量）, m3/s, [i, 1]
        v_vent_mec_local_is_ns: ステップ n からステップ n+1 における室 i の機械換気量（局所換気量）, m3/s, [i, 1]

    Returns:
        ステップ n からステップ n+1 における室 i の機械換気量（全般換気量と局所換気量の合計値）, m3/s, [i, 1]

    Notes:
        式(4.7)
    """

    return v_vent_mec_general_is + v_vent_mec_local_is_ns

