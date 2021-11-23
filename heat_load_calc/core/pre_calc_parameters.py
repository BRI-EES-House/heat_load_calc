import json
import numpy as np
from typing import Tuple
import csv
import pandas as pd
from dataclasses import dataclass
from typing import List, Callable

from heat_load_calc.core import infiltration, response_factor, shape_factor, \
    occupants_form_factor, boundary_simple, furniture
from heat_load_calc.core import ot_target
from heat_load_calc.core import next_condition
from heat_load_calc.core.matrix_method import v_diag

from heat_load_calc.initializer.boundary_type import BoundaryType
from heat_load_calc.core import solar_absorption
from heat_load_calc.core import equipments


@dataclass
class PreCalcParameters:

    # region 建物全体に関すること

    # 該当なし

    # endregion

    # region 空間に関すること

    # 空間の数, [i]
    n_rm: int

    # 空間のID
    id_rm_is: List[int]

    # 空間の名前, [i]
    name_rm_is: List[str]

    # 室iの容積, m3, [i, 1]
    v_rm_is: np.ndarray

    # 室 i の備品等の熱容量, J/K, [i, 1]
    c_sh_frt_is: np.ndarray

    # 室 i の備品等の湿気容量, kg/(kg/kgDA), [i, 1]
    c_lh_frt_is: np.ndarray

    #  室 i の空気と備品等間の熱コンダクタンス, W/K, [i, 1]
    g_sh_frt_is: np.ndarray

    # 室 i の空気と備品等間の湿気コンダクタンス, kg/(s (kg/kgDA)), [i, 1]
    g_lh_frt_is: np.ndarray

    # ステップnにおける室iの空調需要, [i, 8760*4]
    ac_demand_is_ns: np.ndarray

    # ステップnの室iにおける在室人数, [i, 8760*4]
    n_hum_is_ns: np.ndarray

    # ステップnの室iにおける人体発熱を除く内部発熱, W, [i, 8760*4]
    q_gen_is_ns: np.ndarray

    # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [i, 8760*4]
    x_gen_is_ns: np.ndarray

    # ステップnの室iにおける機械換気量（全般換気量+局所換気量）, m3/s, [i, 8760*4]
    v_vent_mec_is_ns: np.ndarray

    # ステップ n からステップ n+1 における室 i に設置された備品等による透過日射吸収熱量時間平均値, W, [i, n]
    q_sol_frt_is_ns: np.ndarray

    # 室iの自然風利用時の換気量, m3/s, [i, 1]
    v_vent_ntr_set_is: np.ndarray

    # ステップnの室iにおける窓の透過日射熱取得, W, [8760*4]
    q_trs_sol_is_ns: np.ndarray

    # endregion

    # 室iの隣室からの機械換気量, m3/s, [i, i]
    v_vent_int_is_is: np.ndarray

    # 境界jの名前, [j]
    name_bdry_js: np.ndarray

    # 境界jの名前2, [j]
    sub_name_bdry_js: List[str]

    # 境界jが地盤かどうか, [j, 1]
    is_ground_js: np.ndarray

    # 境界jの面積, m2, [j, 1]
    a_s_js: np.ndarray

    # ステップnの境界jにおける外気側等価温度の外乱成分, degree C, [j, 8760*4]
    theta_dstrb_js_ns: np.ndarray

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

    n_bdry: int

    f_ax_js_js: np.ndarray

    p_is_js: np.ndarray
    p_js_is: np.ndarray

    # 室iの在室者に対する境界j*の形態係数
    f_mrt_hum_is_js: np.ndarray

    # 平均放射温度計算時の境界 j* の表面温度が境界 j に与える重み, [j, j]
    f_mrt_is_js: np.ndarray

    # 境界jにおける室内側放射熱伝達率, W/m2K, [j, 1]
    h_s_r_js: np.ndarray

    # 境界jにおける室内側対流熱伝達率, W/m2K, [j, 1]
    h_s_c_js: np.ndarray

    # WSR, WSB の計算 式(24)
    f_wsr_js_is: np.ndarray

    # 床暖房の発熱部位？
    f_flr_h_js_is: np.ndarray
    f_flr_c_js_is: np.ndarray

    # WSC, W, [j, n]
    f_wsc_js_ns: np.ndarray

    # 境界jの裏面温度に他の境界の等価温度が与える影響, [j, j]
    k_ei_js_js: np.ndarray

    # ステップnの外気温度, degree C, [n]
    theta_o_ns: np.ndarray

    # ステップnの外気絶対湿度, kg/kg(DA), [n]
    x_o_ns: np.ndarray

    get_ot_target_and_h_hum: Callable[[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray], tuple]

    get_infiltration: Callable[[np.ndarray, float], np.ndarray]

    calc_next_temp_and_load: Callable

    get_f_l_cl: [Callable]


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

    # ステップnの外気温度, degree C, [n]
    theta_o_ns: np.ndarray

    # ステップnの境界jにおける外気側等価温度の外乱成分, degree C, [j, 8760*4]
    theta_dstrb_js_ns: np.ndarray


def make_pre_calc_parameters(
        delta_t: float, data_directory: str, q_trans_sol_calculate=True, theta_o_sol_calculate=True
) -> (PreCalcParameters, PreCalcParametersGround):
    """

    Args:
        delta_t:
        data_directory:
        q_trans_sol_calculate: optional テスト用　これを False に指定すると、CSVファイルから直接読み込むことができる。
        theta_o_sol_calculate: optional テスト用　これを False に指定すると、CSVファイルから直接読み込むことができる。

    Returns:

    """

    with open(data_directory + '/mid_data_house.json') as f:
        rd = json.load(f)

    # 以下の気象データの読み込み
    # 外気温度, degree C, [n]
    # 外気絶対湿度, kg/kg(DA), [n]
    # 法線面直達日射量, W/m2, [n]
    # 水平面天空日射量, W/m2, [n]
    # 夜間放射量, W/m2, [n]
    # 太陽高度, rad, [n]
    # 太陽方位角, rad, [n]
    a_sun_ns, h_sun_ns, i_dn_ns, i_sky_ns, r_n_ns, theta_o_ns, x_o_ns = _read_weather_data(input_data_dir=data_directory)

    a_sun_ns = np.append(a_sun_ns, a_sun_ns[0])
    h_sun_ns = np.append(h_sun_ns, h_sun_ns[0])
    i_dn_ns = np.append(i_dn_ns, i_dn_ns[0])
    i_sky_ns = np.append(i_sky_ns, i_sky_ns[0])
    r_n_ns = np.append(r_n_ns, r_n_ns[0])
    theta_o_ns = np.append(theta_o_ns, theta_o_ns[0])
    x_o_ns = np.append(x_o_ns, x_o_ns[0])

    # ステップnの室iにおける局所換気量, m3/s, [i, 8760*4]
    with open(data_directory + '/mid_data_local_vent.csv', 'r') as f:
        r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        v_vent_mec_local_is_ns = np.array([row for row in r]).T

    # ステップnの室iにおける内部発熱, W, [8760*4]
    with open(data_directory + '/mid_data_heat_generation.csv', 'r') as f:
        r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        q_gen_is_ns = np.array([row for row in r]).T

    # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [8760*4]
    with open(data_directory + '/mid_data_moisture_generation.csv', 'r') as f:
        r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        x_gen_is_ns = np.array([row for row in r]).T

    # ステップnの室iにおける在室人数, [8760*4]
    with open(data_directory + '/mid_data_occupants.csv', 'r') as f:
        r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        n_hum_is_ns = np.array([row for row in r]).T

    # ステップnの室iにおける空調需要, [8760*4]
    with open(data_directory + '/mid_data_ac_demand.csv', 'r') as f:
        r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        ac_demand_is_ns = np.array([row for row in r]).T

    # region rooms の読み込み

    # rooms の取り出し
    rms = rd['rooms']

    # room の数
    n_rm = len(rms)

    # id, [i, 1]
    id_rm_is = np.array([int(rm['id']) for rm in rms]).reshape(-1, 1)

    # 空間iの名前, [i, 1]
    name_rm_is = np.array([str(rm['name']) for rm in rms]).reshape(-1, 1)

    # 空間iの気積, m3, [i, 1]
    v_rm_is = np.array([float(rm['volume']) for rm in rms]).reshape(-1, 1)

    # 室iの機械換気量（局所換気を除く）, m3/s, [i, 1]
    # 入力は m3/h なので、3600で除して m3/s への変換を行う。
    v_vent_mec_general_is = (np.array([rm['ventilation']['mechanical'] for rm in rms]) / 3600).reshape(-1, 1)

    # 室iの隣室iからの機械換気量, m3/s, [i, i]
    v_vent_int_is_is = _get_v_vent_int_is_is(
        next_vent_is_ks=[rm['ventilation']['next_spaces'] for rm in rms]
    )

    # 室iの自然風利用時の換気量, m3/s, [i, 1]
    # 入力は m3/h なので、3600 で除して m3/s への変換を行っている。
    v_vent_ntr_set_is = np.array([s['ventilation']['natural'] / 3600 for s in rms]).reshape(-1, 1)

    # 備品等に関する物性値を取得する。
    #   室 i の備品等の熱容量, J/K, [i, 1]
    #   室 i の空気と備品等間の熱コンダクタンス, W/K, [i, 1]
    #   室 i の備品等の湿気容量, kg/(kg/kgDA), [i, 1]
    #   室 i の空気と備品等間の湿気コンダクタンス, kg/(s (kg/kgDA)), [i, 1]
    c_lh_frt_is, c_sh_frt_is, g_lh_frt_is, g_sh_frt_is = furniture.get_furniture_specs(
        d_frt=[rm['furniture'] for rm in rms],
        v_rm_is=v_rm_is
    )

    # endregion

    # region boundaries

    bs = boundary_simple.Boundaries(
        a_sun_ns=a_sun_ns,
        h_sun_ns=h_sun_ns,
        i_dn_ns=i_dn_ns,
        i_sky_ns=i_sky_ns,
        n_rm=n_rm,
        r_n_ns=r_n_ns,
        theta_o_ns=theta_o_ns,
        bs=rd['boundaries']
    )

    # 境界の数
    n_b = bs.get_n_b()

    # 名前, [j, 1]
    name_bdry_js = bs.get_name_bdry_js()

    # 名前2, [j, 1]
    sub_name_bdry_js = bs.get_sub_name_bdry_js()

    # 室iと境界jの関係を表す係数（境界jから室iへの変換）
    p_is_js = bs.get_p_is_js(n_rm=n_rm)

    # 室iと境界jの関係を表す係数（室iから境界jへの変換）
    p_js_is = bs.get_p_js_is(n_rm=n_rm)

    # 床かどうか, [j, 1]
    is_floor_js = bs.get_is_floor_js()

    # 地盤かどうか, [j, 1]
    is_ground_js = bs.get_is_ground_js()

    # 境界jの裏面温度に他の境界の等価温度が与える影響, [j, j]
    k_ei_js_js = bs.get_k_ei_js_js()

    # 温度差係数
    k_eo_js = bs.get_k_eo_js()

    # 境界jの日射吸収の有無, [j, 1]
    p_s_sol_abs_js = bs.get_p_s_sol_abs_js()

    # 境界jの室内側表面放射熱伝達率, W/m2K, [j, 1]
    h_s_r_js = bs.get_h_s_r_js()

    # 境界jの室内側表面対流熱伝達率, W/m2K, [j, 1]
    h_s_c_js = bs.get_h_s_c_js()

    # 境界jの面積, m2, [j, 1]
    a_s_js = bs.get_a_s_js()

    # 境界jの吸熱応答係数の初項, m2K/W, [j, 1]
    phi_a0_js = bs.get_phi_a0_js()

    # 境界jの項別公比法における項mの吸熱応答係数の第一項 , m2K/W, [j, 12]
    phi_a1_js_ms = bs.get_phi_a1_js_ms()

    # 境界jの貫流応答係数の初項, [j, 1]
    phi_t0_js = bs.get_phi_t0_js()

    # 境界jの項別公比法における項mの貫流応答係数の第一項, [j, 12]
    phi_t1_js_ms = bs.get_phi_t1_js_ms()

    # 境界jの項別公比法における項mの公比, [j, 12]
    r_js_ms = bs.get_r_js_ms()

    # ステップnの室iにおける窓の透過日射熱取得, W, [8760*4]
    #　このif文は、これまで実施してきたテストを維持するために設けている。
    # いずれテスト方法を整理して、csvで与える方式を削除すべきである。
    # CSVで与える方式があることは（将来的に削除予定であるため）仕様書には記述しない。
    if q_trans_sol_calculate:
        q_trs_sol_is_ns = bs.get_q_trs_sol_is_ns(n_rm=n_rm)
    else:
        with open(data_directory + '/mid_data_q_trs_sol.csv', 'r') as f:
            r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            q_trs_sol_is_ns = np.array([row for row in r]).T
        # ステップn+1に対応するために0番要素に最終要素を代入
        q_trs_sol_is_ns = np.append(q_trs_sol_is_ns, q_trs_sol_is_ns[:, 0:1], axis=1)

    # ステップnの境界jにおける裏面等価温度, ℃, [j, 8760*4]
    #　このif文は、これまで実施してきたテストを維持するために設けている。
    # いずれテスト方法を整理して、csvで与える方式を削除すべきである。
    # CSVで与える方式があることは（将来的に削除予定であるため）仕様書には記述しない。
    if theta_o_sol_calculate:
        theta_o_eqv_js_ns = bs.get_theta_o_eqv_js_ns()
    else:
        with open(data_directory + '/mid_data_theta_o_sol.csv', 'r') as f:
            r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            theta_o_eqv_js_ns = np.array([row for row in r]).T
        # ステップn+1に対応するために0番要素に最終要素を代入
        theta_o_eqv_js_ns = np.append(theta_o_eqv_js_ns, theta_o_eqv_js_ns[:, 0:1], axis=1)

    # endregion

    # region equipments

    es = equipments.Equipments(dict_equipments=rd['equipments'], n_rm=n_rm, n_b=n_b, bs=bs)

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

    # 室iの在室者に対する境界jの形態係数, [i, j]
    f_mrt_hum_is_js = occupants_form_factor.get_f_mrt_hum_js(
        n_rm=n_rm,
        n_b=n_b,
        p_is_js=p_is_js,
        a_s_js=a_s_js,
        is_floor_js=is_floor_js
    )

    # 室 i の微小球に対する境界 j の形態係数, -, [i, j]
    f_mrt_is_js = shape_factor.get_f_mrt_is_js(a_s_js=a_s_js, h_s_r_js=h_s_r_js, p_is_js=p_is_js)

    # ステップ n からステップ n+1 における室 i の機械換気量（全般換気量と局所換気量の合計値）, m3/s, [i, 1]
    v_vent_mec_is_ns = get_v_vent_mec_is_ns(
        v_vent_mec_general_is=v_vent_mec_general_is,
        v_vent_mec_local_is_ns=v_vent_mec_local_is_ns
    )

    # ステップ n からステップ n+1 における室 i に設置された備品等による透過日射吸収熱量時間平均値, W, [i, n]
    q_sol_frt_is_ns = solar_absorption.get_q_sol_frt_is_ns(q_trs_sor_is_ns=q_trs_sol_is_ns)

    # ステップ n における境界 j の透過日射吸収熱量, W/m2, [j, n]
    q_s_sol_js_ns = solar_absorption.get_q_s_sol_js_ns(
        p_is_js=p_is_js,
        a_s_js=a_s_js,
        p_s_sol_abs_js=p_s_sol_abs_js,
        p_js_is=p_js_is,
        q_trs_sol_is_ns=q_trs_sol_is_ns
    )

    # ステップ n の境界 j における外気側等価温度の外乱成分, ℃, [j, n]
    theta_dstrb_js_ns = get_theta_dstrb_js_ns(k_eo_js=k_eo_js, theta_o_eqv_js_ns=theta_o_eqv_js_ns)

    # 係数 f_AX, -, [j, j]
    f_ax_js_js = get_f_ax_js_is(
        f_mrt_is_js=f_mrt_is_js,
        h_s_c_js=h_s_c_js,
        h_s_r_js=h_s_r_js,
        k_ei_js_js=k_ei_js_js,
        p_js_is=p_js_is,
        phi_a0_js=phi_a0_js,
        phi_t0_js=phi_t0_js
    )

    # 係数 f_FIA, -, [j, i]
    f_fia_js_is = get_f_fia_js_is(
        h_s_c_js=h_s_c_js,
        h_s_r_js=h_s_r_js,
        k_ei_js_js=k_ei_js_js,
        p_js_is=p_js_is,
        phi_a0_js=phi_a0_js,
        phi_t0_js=phi_t0_js
    )

    # 係数 f_CRX, degree C, [j, n]
    f_crx_js_ns = get_f_crx_js_ns(
        h_s_c_js=h_s_c_js,
        h_s_r_js=h_s_r_js,
        k_ei_js_js=k_ei_js_js,
        phi_a0_js=phi_a0_js,
        phi_t0_js=phi_t0_js,
        q_s_sol_js_ns=q_s_sol_js_ns,
        theta_dstrb_js_ns=theta_dstrb_js_ns
    )

    # 係数 f_WSR, -, [j, i]
    f_wsr_js_is = get_f_wsr_js_is(f_ax_js_js=f_ax_js_js, f_fia_js_is=f_fia_js_is)

    # 係数 f_{WSC, n}, degree C, [j, n]
    f_wsc_js_ns = get_f_wsc_js_ns(f_ax_js_js=f_ax_js_js, f_crx_js_ns=f_crx_js_ns)

    # region 読み込んだ値から新たに関数を作成する

    # 作用温度と人体周りの熱伝達率を計算する関数
    get_ot_target_and_h_hum = ot_target.make_get_ot_target_and_h_hum_function(
        is_radiative_heating_is=is_radiative_heating_is,
        is_radiative_cooling_is=is_radiative_cooling_is
    )

    # すきま風を計算する関数
    # 引数:
    #   theta_r_is_n: 時刻nの室温, degree C, [i,1]
    #   theta_o_n: 時刻n+1の外気温度, degree C
    # 戻り値:
    #   すきま風量, m3/s, [i,1]
    get_infiltration = infiltration.make_get_infiltration_function(
        infiltration=rd['building']['infiltration'],
        rms=rms
    )

    # 次のステップの室温と負荷を計算する関数
    calc_next_temp_and_load = next_condition.make_get_next_temp_and_load_function(
        is_radiative_heating_is=is_radiative_heating_is,
        is_radiative_cooling_is=is_radiative_cooling_is,
        lr_h_max_cap_is=q_rs_h_max_is,
        lr_cs_max_cap_is=q_rs_c_max_is
    )

    # endregion

    pre_calc_parameters = PreCalcParameters(
        n_rm=n_rm,
        id_rm_is=id_rm_is,
        name_rm_is=name_rm_is,
        v_rm_is=v_rm_is,
        c_sh_frt_is=c_sh_frt_is,
        c_lh_frt_is=c_lh_frt_is,
        g_sh_frt_is=g_sh_frt_is,
        g_lh_frt_is=g_lh_frt_is,
        v_vent_int_is_is=v_vent_int_is_is,
        name_bdry_js=name_bdry_js,
        sub_name_bdry_js=sub_name_bdry_js,
        a_s_js=a_s_js,
        v_vent_mec_is_ns=v_vent_mec_is_ns,
        q_gen_is_ns=q_gen_is_ns,
        n_hum_is_ns=n_hum_is_ns,
        x_gen_is_ns=x_gen_is_ns,
        f_mrt_hum_is_js=f_mrt_hum_is_js,
        theta_dstrb_js_ns=theta_dstrb_js_ns,
        n_bdry=n_b,
        r_js_ms=r_js_ms,
        phi_t0_js=phi_t0_js,
        phi_a0_js=phi_a0_js,
        phi_t1_js_ms=phi_t1_js_ms,
        phi_a1_js_ms=phi_a1_js_ms,
        q_trs_sol_is_ns=q_trs_sol_is_ns,
        v_vent_ntr_set_is=v_vent_ntr_set_is,
        ac_demand_is_ns=ac_demand_is_ns,
        f_flr_h_js_is=f_flr_h_js_is,
        f_flr_c_js_is=f_flr_c_js_is,
        h_s_r_js=h_s_r_js,
        h_s_c_js=h_s_c_js,
        f_mrt_is_js=f_mrt_is_js,
        q_s_sol_js_ns=q_s_sol_js_ns,
        q_sol_frt_is_ns=q_sol_frt_is_ns,
        beta_h_is=beta_h_is,
        beta_c_is=beta_c_is,
        f_wsr_js_is=f_wsr_js_is,
        f_ax_js_js=f_ax_js_js,
        p_is_js=p_is_js,
        p_js_is=p_js_is,
        is_ground_js=is_ground_js,
        f_wsc_js_ns=f_wsc_js_ns,
        k_ei_js_js=k_ei_js_js,
        theta_o_ns=theta_o_ns,
        x_o_ns=x_o_ns,
        get_ot_target_and_h_hum=get_ot_target_and_h_hum,
        get_infiltration=get_infiltration,
        calc_next_temp_and_load=calc_next_temp_and_load,
        get_f_l_cl=get_f_l_cl
    )

    # 地盤の数
    n_grounds = bs.get_n_ground()

    pre_calc_parameters_ground = PreCalcParametersGround(
        n_grounds=n_grounds,
        r_js_ms=r_js_ms[is_ground_js.flatten(), :],
        phi_a0_js=phi_a0_js[is_ground_js.flatten(), :],
        phi_t0_js=phi_t0_js[is_ground_js.flatten(), :],
        phi_a1_js_ms=phi_a1_js_ms[is_ground_js.flatten(), :],
        phi_t1_js_ms=phi_t1_js_ms[is_ground_js.flatten(), :],
        h_s_r_js=h_s_r_js[is_ground_js.flatten(), :],
        h_s_c_js=h_s_c_js[is_ground_js.flatten(), :],
        theta_o_ns=theta_o_ns,
        theta_dstrb_js_ns=theta_dstrb_js_ns[is_ground_js.flatten(), :],
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

    return np.dot(np.linalg.inv(f_ax_js_js), f_crx_js_ns)


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

    return np.dot(np.linalg.inv(f_ax_js_js), f_fia_js_is)


def get_f_crx_js_ns(h_s_c_js, h_s_r_js, k_ei_js_js, phi_a0_js, phi_t0_js, q_s_sol_js_ns, theta_dstrb_js_ns):
    """

    Args:
        h_s_c_js: 境界 j の室内側対流熱伝達率, W/(m2 K), [j, 1]
        h_s_r_js: 境界 j の室内側放射熱伝達率, W/(m2 K), [j, 1]
        k_ei_js_js: 境界 j の裏面温度に境界　j∗ の等価温度が与える影響, -, [j, j]
        phi_a0_js: 境界 j の吸熱応答係数の初項, m2 K/W, [j, 1]
        phi_t0_js: 境界 j の貫流応答係数の初項, -, [j, 1]
        q_s_sol_js_ns: ステップ n における境界 j の透過日射吸収熱量, W/m2, [j, n]
        theta_dstrb_js_ns: ステップ n の境界 j における外気側等価温度の外乱成分, degre C, [j, n]

    Returns:
        係数 f_CRX, degree C, [j, n]

    Notes:
        式(4.3)
    """

    return phi_a0_js * q_s_sol_js_ns\
        + phi_t0_js / (h_s_c_js + h_s_r_js) * np.dot(k_ei_js_js, q_s_sol_js_ns)\
        + phi_t0_js * theta_dstrb_js_ns


def get_f_fia_js_is(h_s_c_js, h_s_r_js, k_ei_js_js, p_js_is, phi_a0_js, phi_t0_js):
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

    return phi_a0_js * h_s_c_js * p_js_is + np.dot(k_ei_js_js, p_js_is) * phi_t0_js * h_s_c_js / (h_s_c_js + h_s_r_js)


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
        - np.dot(k_ei_js_js, np.dot(p_js_is, f_mrt_is_js)) * h_s_r_js * phi_t0_js / (h_s_c_js + h_s_r_js)


def get_theta_dstrb_js_ns(k_eo_js, theta_o_eqv_js_ns):
    """

    Args:
        k_eo_js: 境界 j の裏面温度に境界 j の相当外気温度が与える影響, -, [j, 1]
        theta_o_eqv_js_ns: ステップ n における境界 j の相当外気温度, degree C, [j, 1]

    Returns:
        ステップ n の境界 j における外気側等価温度の外乱成分, degre C, [j, n]

    Notes:
        式(4.6)
    """

    return theta_o_eqv_js_ns * k_eo_js


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


def _get_v_vent_int_is_is(next_vent_is_ks: List[List[dict]]) -> np.ndarray:
    """
    隣室iから室iへの機械換気量マトリクスを生成する。
    Args:
        next_vent_is_ks: 隣室からの機械換気
            2重のリスト構造を持つ。
            外側のリスト：室、（下流側の室を基準とする。）
            内側のリスト：換気経路（数は任意であり、換気経路が無い（0: 空のリスト）場合もある。）
                辞書型 （上流側の室ID: int, 換気量（m3/s): float)
    Returns:
        隣室iから室iへの機械換気量マトリクス, m3/s, [i, i]
            例えば、
                室0→室1:3.0
                室0→室2:4.0
                室1→室2:3.0
                室3→室1:1.5
                室3→室2:1.0
            の場合、
                [[0.0,  0.0,  0.0,  0.0],
                 [3.0, -4.5,  0.0,  1.5],
                 [4.0,  3.0, -8.0,  1.0],
                 [0.0,  0.0,  0.0,  0.0]]
    Note:
        2021/10/25 対角要素に流出側の流量をいれるように定義を変更した。
    """

    n_rooms = len(next_vent_is_ks)

    # 隣室iから室iへの換気量マトリックス（流入側のみ）, m3/s [i, i]
    v_int_vent_is_is = np.zeros((n_rooms, n_rooms), dtype=float)

    # 室iのループ（風下室ループ）
    for i, next_vent_i_ks in enumerate(next_vent_is_ks):

        # 室iにおける経路jのループ（風上室ループ）
        # 取得するのは、(ID: int, 換気量(m3/h): float) のタプル
        for next_vent_i_k in next_vent_i_ks:

            idx = next_vent_i_k['upstream_room_id']

            # 入力は m3/h なので、3600 で除して m3/s への変換を行っている。
            volume = next_vent_i_k['volume'] / 3600

            # 風上側の部屋IDが自分の部屋IDではないことのチェック
            if i != idx:
                # 流入側（プラス）
                v_int_vent_is_is[i, idx] += volume
                # 流出側（マイナス）
                v_int_vent_is_is[i, i] -= volume
            else:
                raise Exception

    # 対角要素に流出する換気量を設定する。
#    v_vent_nxt_is_is = v_int_vent_is_is - np.diag(v_int_vent_is_is.sum(axis=1))

    return v_int_vent_is_is


def _read_weather_data(input_data_dir: str):
    """
    気象データを読み込む。
    Args:
        input_data_dir: 現在計算しているデータのパス
    Returns:
        外気温度, degree C
        外気絶対湿度, kg/kg(DA)
        法線面直達日射量, W/m2
        水平面天空日射量, W/m2
        夜間放射量, W/m2
        太陽高度, rad
        太陽方位角, rad
    """

    # 気象データ
    pp = pd.read_csv(input_data_dir + '/weather.csv', index_col=0)

    # 外気温度, degree C
    theta_o_ns = pp['temperature'].values
    # 外気絶対湿度, kg/kg(DA)
    x_o_ns = pp['absolute humidity'].values
    # 法線面直達日射量, W/m2
    i_dn_ns = pp['normal direct solar radiation'].values
    # 水平面天空日射量, W/m2
    i_sky_ns = pp['horizontal sky solar radiation'].values
    # 夜間放射量, W/m2
    r_n_ns = pp['outward radiation'].values
    # 太陽高度, rad
    h_sun_ns = pp['sun altitude'].values
    # 太陽方位角, rad
    a_sun_ns = pp['sun azimuth'].values

    return a_sun_ns, h_sun_ns, i_dn_ns, i_sky_ns, r_n_ns, theta_o_ns, x_o_ns
