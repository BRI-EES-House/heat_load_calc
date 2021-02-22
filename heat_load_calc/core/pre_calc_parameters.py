import json
import numpy as np
import csv
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Any, Callable

from heat_load_calc.external.global_number import get_c_air, get_rho_air
from heat_load_calc.initializer import response_factor, shape_factor
from heat_load_calc.core import infiltration
from heat_load_calc.core import ot_target
from heat_load_calc.core import next_condition


@dataclass
class PreCalcParameters:

    # region 建物全体に関すること

    # 該当なし

    # endregion

    # region 空間に関すること

    # 空間の数, [i]
    n_spaces: int

    # 空間のID
    id_space_is: List[int]

    # 空間の名前, [i]
    name_space_is: List[str]

    # 室iの容積, m3, [i, 1]
    v_room_is: np.ndarray

    # 室iの熱容量, J/K, [i, 1]
    c_room_is: np.ndarray

    # 室iの家具等の熱容量, J/K, [i, 1]
    c_sh_frt_is: np.ndarray

    # 室iの家具等の湿気容量, kg/m3 (kg/kgDA), [i, 1]
    c_lh_frt_is: np.ndarray

    # 室iの家具等と空気間の熱コンダクタンス, W/K, [i, 1]
    g_sh_frt_is: np.ndarray

    # 室iの家具等と空気間の湿気コンダクタンス, kg/s (kg/kgDA), [i, 1]
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
    v_mec_vent_is_ns: np.ndarray

    # 家具の吸収日射量, W, [i, 8760*4]
    q_sol_frt_is_ns: np.ndarray

    # 室iの自然風利用時の換気量, m3/s, [i, 1]
    v_ntrl_vent_is: np.ndarray

    # ステップnの室iにおける窓の透過日射熱取得, W, [8760*4]
    q_trs_sol_is_ns: np.ndarray

    # endregion

    # 室iの隣室からの機械換気量, m3/s, [i, i]
    v_int_vent_is_is: np.ndarray

    # 境界jの名前, [j]
    name_bdry_js: np.ndarray

    # 境界jの名前2, [j]
    sub_name_bdry_js: List[str]

    # 境界jが地盤かどうか, [j, 1]
    is_ground_js: np.ndarray

    # 境界jの面積, m2, [j, 1]
    a_srf_js: np.ndarray

    # ステップnの境界jにおける外気側等価温度の外乱成分, degree C, [j, 8760*4]
    theta_dstrb_js_ns: np.ndarray

    # BRM(換気なし), W/K, [i, i]
    brm_non_vent_is_is: np.ndarray

    # BRL, [i, i]
    brl_is_is: np.ndarray

    # 放射暖房対流比率, [i, 1]
    beta_is: np.ndarray

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
    q_sol_js_ns: np.ndarray

    n_bdries: int

    ivs_ax_js_js: np.ndarray

    p_is_js: np.ndarray
    p_js_is: np.ndarray

    # 室iの在室者に対する境界j*の形態係数
    f_mrt_hum_is_js: np.ndarray

    # 平均放射温度計算時の各部位表面温度の重み計算 式(101)
    f_mrt_is_js: np.ndarray

    # 境界jにおける室内側放射熱伝達率, W/m2K, [j, 1]
    h_r_js: np.ndarray

    # 境界jにおける室内側対流熱伝達率, W/m2K, [j, 1]
    h_c_js: np.ndarray

    # WSR, WSB の計算 式(24)
    wsr_js_is: np.ndarray
    wsb_js_is: np.ndarray

    # 床暖房の発熱部位？
    flr_js_is: np.ndarray

    # WSC, W, [j, n]
    wsc_js_ns: np.ndarray

    # 境界jの裏面温度に他の境界の等価温度が与える影響, [j, j]
    k_ei_js_js: np.ndarray

    # ステップnの外気温度, degree C, [n]
    theta_o_ns: np.ndarray

    # ステップnの外気絶対湿度, kg/kg(DA), [n]
    x_o_ns: np.ndarray

    # 年平均外気温度, degree C
    theta_o_ave: np.ndarray

    get_ot_target_and_h_hum: Callable[[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray], tuple]

    get_infiltration: Callable[[np.ndarray, float], np.ndarray]

    calc_next_temp_and_load: Callable

    rac_spec: Dict[str, Any]


@dataclass
class PreCalcParametersGround:

    # 地盤の数
    n_grounds: int

    # 地盤jの項別公比法における項mの公比, [j, 12]
    r_js_ms: np.ndarray

    # 地盤jの吸熱応答係数の初項, m2K/W, [j, 1]
    phi_a0_js: np.ndarray

    # 地盤jの項別公比法における項mの吸熱応答係数の第一項 , m2K/W, [j, 12]
    phi_a1_js_ms: np.ndarray

    # 地盤jにおける室内側放射熱伝達率, W/m2K, [j, 1]
    h_r_js: np.ndarray

    # 地盤jにおける室内側対流熱伝達率, W/m2K, [j, 1]
    h_c_js: np.ndarray

    # ステップnの外気温度, degree C, [n]
    theta_o_ns: np.ndarray

    # 年平均外気温度, degree C
    theta_o_ave: float


def make_pre_calc_parameters(delta_t: float, data_directory: str) -> (PreCalcParameters, PreCalcParametersGround):

    with open(data_directory + '/mid_data_house.json') as f:
        rd = json.load(f)

    # region spaces の読み込み

    # spaces の取り出し
    ss = rd['spaces']

    # Spaceの数
    n_spaces = len(ss)

    # id, [i]
    id_space_is = [int(s['id']) for s in ss]

    # 空間iの名前, [i]
    name_space_is = [str(s['name']) for s in ss]

    # 空間iの気積, m3, [i, 1]
    v_room_is = np.array([float(s['volume']) for s in ss]).reshape(-1, 1)

    # 室iに設置された放射暖房の対流成分比率, [i, 1]
    beta_is = np.array([s['beta'] for s in ss]).reshape(-1, 1)

    # 室iの機械換気量（局所換気を除く）, m3/s, [i]
    v_vent_ex_is = np.array([s['ventilation']['mechanical'] for s in ss])

    # 室iの隣室iからの機械換気量, m3/s, [i, i]
    v_int_vent_is_is = np.array([s['ventilation']['next_spaces'] for s in ss])

    # 室iの自然風利用時の換気量, m3/s, [i, 1]
    v_ntrl_vent_is = np.array([s['ventilation']['natural'] for s in ss]).reshape(-1, 1)

    # 室iの家具等の熱容量, J/K, [i, 1]
    c_sh_frt_is = np.array([float(s['furniture']['heat_capacity']) for s in ss]).reshape(-1, 1)

    # 室iの家具等と空気間の熱コンダクタンス, W/K, [i, 1]
    g_sh_frt_is = np.array([float(s['furniture']['heat_cond']) for s in ss]).reshape(-1, 1)

    # 室iの家具等の湿気容量, kg/m3 kg/kgDA, [i, 1]
    c_lh_frt_is = np.array([float(s['furniture']['moisture_capacity']) for s in ss]).reshape(-1, 1)

    # 室iの家具等と空気間の湿気コンダクタンス, kg/s (kg/kgDA), [i, 1]
    g_lh_frt_is = np.array([float(s['furniture']['moisture_cond']) for s in ss]).reshape(-1, 1)

    # 室iの暖房方式として放射空調が設置されているかどうか。  bool値, [i, 1]
    # 室iの暖房方式として放射空調が設置されている場合の、放射暖房最大能力, W, [i, 1]
    is_radiative_heating_is_list = []
    radiative_heating_max_capacity_is_list = []
    for i, s in enumerate(ss):
        if s['equipment']['heating']['radiative']['installed']:
            is_radiative_heating_is_list.append(True)
            radiative_heating_max_capacity_is_list.append(s['equipment']['heating']['radiative']['max_capacity'])
        else:
            is_radiative_heating_is_list.append(False)
            radiative_heating_max_capacity_is_list.append(0.0)

    # 室iの冷房方式として放射空調が設置されているかどうか。  bool値, [i, 1]
    # 室iの冷房方式として放射空調が設置されている場合の、放射冷房最大能力, W, [i, 1]
    is_radiative_cooling_is_list = []
    radiative_cooling_max_capacity_is_list = []
    for i, s in enumerate(ss):
        if s['equipment']['cooling']['radiative']['installed']:
            is_radiative_cooling_is_list.append(True)
            radiative_cooling_max_capacity_is_list.append(s['equipment']['cooling']['max_capacity'])
        else:
            is_radiative_cooling_is_list.append(False)
            radiative_cooling_max_capacity_is_list.append(0.0)

    is_radiative_heating_is = np.array(is_radiative_heating_is_list).reshape(-1, 1)
    lr_h_max_cap_is = np.array(radiative_heating_max_capacity_is_list).reshape(-1, 1)
    is_radiative_cooling_is = np.array(is_radiative_cooling_is_list).reshape(-1, 1)
    lr_cs_max_cap_is = np.array(radiative_cooling_max_capacity_is_list).reshape(-1, 1)

    qmin_c_is = np.array([s['equipment']['cooling']['convective']['q_min'] for s in ss]).reshape(-1, 1)
    qmax_c_is = np.array([s['equipment']['cooling']['convective']['q_max'] for s in ss]).reshape(-1, 1)
    Vmin_is = np.array([s['equipment']['cooling']['convective']['v_min'] for s in ss]).reshape(-1, 1)
    Vmax_is = np.array([s['equipment']['cooling']['convective']['v_max'] for s in ss]).reshape(-1, 1)

    # endregion

    # region boundaries の読み込み

    # boundaries の取り出し
    bs = rd['boundaries']

    # id, [j]
    bdry_id_js = [b['id'] for b in bs]

    # 名前, [j]
    name_bdry_js = np.array([str(b['name']) for b in bs])

    # 名前2, [j]
    # TODO: なぜこちらは np.ndarray にしていない？
    sub_name_bdry_js = [b['sub_name'] for b in bs]

    # 地盤かどうか, [j, 1]
    is_ground_js = np.array([{'true': True, 'false': False}[b['is_ground']] for b in bs]).reshape(-1, 1)

    # 隣接する空間のID, [j]
    connected_space_id_js = np.array([b['connected_space_id'] for b in bs])

    # 境界jの面積, m2, [j, 1]
    a_srf_js = np.array([b['area'] for b in bs]).reshape(-1, 1)

    # 応答係数を取得する。
    phi_a0_js = np.array([b['phi_a0'] for b in bs]).reshape(-1, 1)
    phi_t0_js = np.array([b['phi_t0'] for b in bs]).reshape(-1, 1)
    phi_a1_js_ms_lst = []
    phi_t1_js_ms_lst = []
    r_js_ms_lst = []
    for b in bs:
        phi_a1_js_ms_lst.append(b['phi_a1'])
        phi_t1_js_ms_lst.append(b['phi_t1'])
        r_js_ms_lst.append(b['r'])

    phi_a1_js_ms = np.array(phi_a1_js_ms_lst)
    phi_t1_js_ms = np.array(phi_t1_js_ms_lst)
    r_js_ms = np.array(r_js_ms_lst)

    # 境界jの室内側表面対流熱伝達率, W/m2K, [j, 1]
    h_c_js = np.array([b['h_c'] for b in bs]).reshape(-1, 1)

    # 境界jの室内側表面放射熱伝達率, W/m2K, [j, 1]
    h_r_js = np.array([b['h_r'] for b in bs]).reshape(-1, 1)

    # 境界jの室内側表面総合熱伝達率, W/m2K, [j, 1]
    # h_i_js_temporary = np.array([b['h_i'] for b in bs]).reshape(-1, 1)

    # 境界jの室に設置された放射暖房の放熱量のうち放射成分に対する境界jの室内側吸収比率
    flr_js = np.array([b['flr'] for b in bs])

    # 境界jの日射吸収の有無, [j, 1]
    is_solar_abs_js = np.array(
        [
            {
                'True': True,
                'False': False
            }[b['is_solar_absorbed']]
            for b in bs
        ]
    ).reshape(-1, 1)

    # 境界jの室に設置された放射暖房の放熱量のうち放射成分に対する境界jの室内側吸収比率
    f_mrt_hum_is = np.array([b['f_mrt_hum'] for b in bs])

    # 境界の裏面温度に屋外側等価温度が与える影響, [j, 1]
    k_eo_js = np.array([b['k_outside'] for b in bs]).reshape(-1, 1)

    k_ei_id_js = []
    k_ei_coef_js = []
    for b in bs:
        if b['k_inside'] is None:
            k_ei_id_j = None
            k_ei_coef_j = None
        else:
            k_ei_id_j = b['k_inside']['id']
            k_ei_coef_j = b['k_inside']['coef']
        k_ei_id_js.append(k_ei_id_j)
        k_ei_coef_js.append(k_ei_coef_j)

    # 境界jの裏面に相当する境界のID
#    k_ei_id_js = [b['k_inside']['id'] for b in bs]

    # 境界jの裏面に相当する境界が与える影響
#    k_ei_coef_js = [b['k_inside']['coef'] for b in bs]

    # endregion

    # region スケジュール化されたデータの読み込み

    pp = pd.read_csv(data_directory + '/weather.csv', index_col=0, engine='python')

    theta_o_ns = pp['temperature'].values
    x_o_ns = pp['absolute humidity'].values

    # ステップnの室iにおける局所換気量, m3/s, [i, 8760*4]
    with open(data_directory + '/mid_data_local_vent.csv', 'r') as f:
        r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        v_mec_vent_local_is_ns = np.array([row for row in r]).T

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

    # ステップnの室iにおける窓の透過日射熱取得, W, [8760*4]
    with open(data_directory + '/mid_data_q_trs_sol.csv', 'r') as f:
        r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        q_trs_sol_is_ns = np.array([row for row in r]).T

    # ステップnの境界jにおける裏面等価温度, ℃, [j, 8760*4]
    with open(data_directory + '/mid_data_theta_o_sol.csv', 'r') as f:
        r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        theta_o_sol_js_ns = np.array([row for row in r]).T

    # endregion

    # region 読み込んだ変数をベクトル表記に変換する
    # ただし、1次元配列を縦ベクトルに変換する処理等は読み込み時に np.reshape を適用して変換している。

    # 境界の数
    n_boundaries = len(bs)

    # 地盤の数
    n_grounds = np.count_nonzero(is_ground_js)

    # 室iと境界jの関係を表す係数（境界jから室iへの変換）
    # [[p_0_0 ... ... p_0_j]
    #  [ ...  ... ...  ... ]
    #  [p_i_0 ... ... p_i_j]]
    p_is_js = np.zeros((n_spaces, n_boundaries), dtype=int)
    for i in range(n_spaces):
        p_is_js[i, connected_space_id_js == i] = 1

    # 室iと境界jの関係を表す係数（室iから境界jへの変換）
    # [[p_0_0 ... p_0_i]
    #  [ ...  ...  ... ]
    #  [ ...  ...  ... ]
    #  [p_j_0 ... p_j_i]]
    p_js_is = p_is_js.T

    # 境界jの裏面温度に他の境界の等価温度が与える影響, [j, j]
    k_ei_js_js = []
    for k_ei_id_j, k_ei_coef_j in zip(k_ei_id_js, k_ei_coef_js):
        k_ei_js = [0.0] * n_boundaries
        if k_ei_id_j is None:
            pass
        else:
            k_ei_js[k_ei_id_j] = k_ei_coef_j
        k_ei_js_js.append(k_ei_js)
    k_ei_js_js = np.array(k_ei_js_js)

    # 室iに設置された放射暖房の放熱量のうち放射成分に対する境界jの室内側吸収比率, [j, i]
    flr_js_is = p_js_is * flr_js[:, np.newaxis]

    # 室iの在室者に対する境界j*の形態係数, [i, j]
    f_mrt_hum_is_js = p_is_js * f_mrt_hum_is[np.newaxis, :]

    # endregion

    # region 読み込んだ値から新たに係数を作成する

    # 室iの空気の熱容量, J/K, [i, 1]
    c_rm_is = v_room_is * get_rho_air() * get_c_air()

    # 平均放射温度計算時の各部位表面温度の重み, [i, j]
    f_mrt_is_js = shape_factor.get_f_mrt_is_js(a_srf_js=a_srf_js, h_r_js=h_r_js, p_is_js=p_is_js)

    # 境界jの室内側表面総合熱伝達率, W/m2K, [j, 1]
    h_i_js = h_c_js + h_r_js

    # ステップnの室iにおける機械換気量（全般換気量+局所換気量）, m3/s, [i, n]
    v_mec_vent_is_ns = v_vent_ex_is[:, np.newaxis] + v_mec_vent_local_is_ns

    # 室内侵入日射のうち家具に吸収される割合
    # TODO: これは入力値にした方がよいのではないか？
    r_sol_fnt = 0.5

    # ステップnの室iにおける家具の吸収日射量, W, [i, n]
    q_sol_frnt_is_ns = q_trs_sol_is_ns * r_sol_fnt

    # 室iにおける日射が吸収される境界の面積の合計, m2, [i, 1]
    a_srf_abs_is = np.dot(p_is_js, a_srf_js * is_solar_abs_js)

    # ステップnの境界jにおける透過日射吸収熱量, W/m2, [j, n]
    # TODO: 日射の吸収割合を入力値にした方がよいのではないか？
    q_sol_js_ns = np.dot(p_js_is, q_trs_sol_is_ns / a_srf_abs_is)\
        * is_solar_abs_js * (1.0 - r_sol_fnt)

    # ステップnの境界jにおける外気側等価温度の外乱成分, ℃, [j, n]
    theta_dstrb_js_ns = theta_o_sol_js_ns * k_eo_js

    # AX, [j, j]
    ax_js_js = np.diag(1.0 + (phi_a0_js * h_i_js).flatten())\
        - np.dot(p_js_is, f_mrt_is_js) * h_r_js * phi_a0_js\
        - np.dot(k_ei_js_js, np.dot(p_js_is, f_mrt_is_js)) * h_r_js * phi_t0_js / h_i_js

    # AX^-1, [j, j]
    ivs_ax_js_js = np.linalg.inv(ax_js_js)

    # FIA, [j, i]
    fia_js_is = phi_a0_js * h_c_js * p_js_is\
        + np.dot(k_ei_js_js, p_js_is) * phi_t0_js * h_c_js / h_i_js

    # CRX, W, [j, n]
    crx_js_ns = phi_a0_js * q_sol_js_ns\
        + phi_t0_js / h_i_js * np.dot(k_ei_js_js, q_sol_js_ns)\
        + phi_t0_js * theta_dstrb_js_ns

    # FLB, K/W, [j, i]
    flb_js_is = flr_js_is * (1.0 - beta_is.T) * phi_a0_js / a_srf_js\
        + np.dot(k_ei_js_js, flr_js_is * (1.0 - beta_is.T)) * phi_t0_js / h_i_js / a_srf_js

    # WSR, [j, i]
    wsr_js_is = np.dot(ivs_ax_js_js, fia_js_is)

    # WSC, W, [j, n]
    wsc_js_ns = np.dot(ivs_ax_js_js, crx_js_ns)

    # WSB, K/W, [j, i]
    wsb_js_is = np.dot(ivs_ax_js_js, flb_js_is)

    # BRL, [i, i]
    brl_is_is = np.dot(p_is_js, wsb_js_is * h_c_js * a_srf_js) + np.diag(beta_is.flatten())

    # BRM(換気なし), W/K, [i, i]
    brm_non_vent_is_is = np.diag(c_rm_is.flatten() / delta_t)\
        + np.dot(p_is_js, (p_js_is - wsr_js_is) * a_srf_js * h_c_js)\
        + np.diag((c_sh_frt_is * g_sh_frt_is / (c_sh_frt_is + g_sh_frt_is * delta_t)).flatten())

    # 年平均外気温度, degree C
    # 地盤計算の時の深部温度に用いる
    theta_o_ave = np.average(theta_o_ns)

    # endregion

    # region 読み込んだ値から新たに関数を作成する

    # 作用温度と人体周りの熱伝達率を計算する関数
    get_ot_target_and_h_hum = ot_target.make_get_ot_target_and_h_hum_function(
        is_radiative_heating_is=is_radiative_heating_is,
        is_radiative_cooling_is=is_radiative_cooling_is
    )

    # すきま風を計算する関数
    get_infiltration = infiltration.make_get_infiltration_function(rd=rd)

    # 次のステップの室温と負荷を計算する関数
    calc_next_temp_and_load = next_condition.make_get_next_temp_and_load_function(
        is_radiative_heating_is=is_radiative_heating_is,
        is_radiative_cooling_is=is_radiative_cooling_is,
        lr_h_max_cap_is=lr_h_max_cap_is,
        lr_cs_max_cap_is=lr_cs_max_cap_is
    )

    # endregion

    rac_spec = {
        'v_min': Vmin_is,
        'v_max': Vmax_is,
        'q_min': qmin_c_is,
        'q_max': qmax_c_is
    }

    pre_calc_parameters = PreCalcParameters(
        n_spaces=n_spaces,
        id_space_is=id_space_is,
        name_space_is=name_space_is,
        v_room_is=v_room_is,
        c_room_is=c_rm_is,
        c_sh_frt_is=c_sh_frt_is,
        c_lh_frt_is=c_lh_frt_is,
        g_sh_frt_is=g_sh_frt_is,
        g_lh_frt_is=g_lh_frt_is,
        v_int_vent_is_is=v_int_vent_is_is,
        name_bdry_js=name_bdry_js,
        sub_name_bdry_js=sub_name_bdry_js,
        a_srf_js=a_srf_js,
        v_mec_vent_is_ns=v_mec_vent_is_ns,
        q_gen_is_ns=q_gen_is_ns,
        n_hum_is_ns=n_hum_is_ns,
        x_gen_is_ns=x_gen_is_ns,
        f_mrt_hum_is_js=f_mrt_hum_is_js,
        theta_dstrb_js_ns=theta_dstrb_js_ns,
        n_bdries=n_boundaries,
        r_js_ms=r_js_ms,
        phi_t0_js=phi_t0_js,
        phi_a0_js=phi_a0_js,
        phi_t1_js_ms=phi_t1_js_ms,
        phi_a1_js_ms=phi_a1_js_ms,
        q_trs_sol_is_ns=q_trs_sol_is_ns,
        v_ntrl_vent_is=v_ntrl_vent_is,
        ac_demand_is_ns=ac_demand_is_ns,
        flr_js_is=flr_js_is,
        h_r_js=h_r_js,
        h_c_js=h_c_js,
        f_mrt_is_js=f_mrt_is_js,
        q_sol_js_ns=q_sol_js_ns,
        q_sol_frt_is_ns=q_sol_frnt_is_ns,
        beta_is=beta_is,
        wsr_js_is=wsr_js_is,
        wsb_js_is=wsb_js_is,
        brm_non_vent_is_is=brm_non_vent_is_is,
        ivs_ax_js_js=ivs_ax_js_js,
        brl_is_is=brl_is_is,
        p_is_js=p_is_js,
        p_js_is=p_js_is,
        is_ground_js=is_ground_js,
        wsc_js_ns=wsc_js_ns,
        k_ei_js_js=k_ei_js_js,
        theta_o_ns=theta_o_ns,
        x_o_ns=x_o_ns,
        theta_o_ave=theta_o_ave,
        rac_spec=rac_spec,
        get_ot_target_and_h_hum=get_ot_target_and_h_hum,
        get_infiltration=get_infiltration,
        calc_next_temp_and_load=calc_next_temp_and_load
    )

    pre_calc_parameters_ground = PreCalcParametersGround(
        n_grounds=n_grounds,
        r_js_ms=r_js_ms[is_ground_js.flatten(), :],
        phi_a0_js=phi_a0_js[is_ground_js.flatten(), :],
        phi_a1_js_ms=phi_a1_js_ms[is_ground_js.flatten(), :],
        h_r_js=h_r_js[is_ground_js.flatten(), :],
        h_c_js=h_c_js[is_ground_js.flatten(), :],
        theta_o_ns=theta_o_ns,
        theta_o_ave=theta_o_ave,
    )

    return pre_calc_parameters, pre_calc_parameters_ground


def _get_responsfactors(bs):

    # 境界jの吸熱応答係数の初項, m2K/W, [j, 1]
    phi_a0_js = []
    # 境界jの項別公比法における項mの吸熱応答係数の第一項 , m2K/W, [j, 12]
    phi_a1_js_ms = []
    # 境界jの貫流応答係数の初項, [j, 1]
    phi_t0_js = []
    # 境界jの項別公比法における項mの貫流応答係数の第一項, [j, 12]
    phi_t1_js_ms = []
    # 境界jの項別公比法における項mの公比, [j, 12]
    r_js_ms = []

    for b in bs:
        rff = response_factor.ResponseFactorFactory.create(spec=b['spec'])
        rf = rff.get_response_factors()
        phi_a0_js.append(rf.rfa0)
        phi_a1_js_ms.append(rf.rfa1)
        phi_t0_js.append(rf.rft0)
        phi_t1_js_ms.append(rf.rft1)
        r_js_ms.append(rf.row)
        # if b['spec']['method'] == 'response_factor':
        #     phi_a0_js.append(b['spec']['phi_a0'])
        #     phi_a1_js_ms.append(b['spec']['phi_a1'])
        #     phi_t0_js.append(b['spec']['phi_t0'])
        #     phi_t1_js_ms.append(b['spec']['phi_t1'])
        #     r_js_ms.append(b['spec']['r'])
        # else:
        #     rff = response_factor.ResponseFactorFactory.create(spec=b['spec'])
        #     rf = rff.get_response_factors()
        #     phi_a0_js.append(rf.rfa0)
        #     phi_a1_js_ms.append(rf.rfa1)
        #     phi_t0_js.append(rf.rft0)
        #     phi_t1_js_ms.append(rf.rft1)
        #     r_js_ms.append(rf.row)

    phi_a0_js = np.array(phi_a0_js).reshape(-1, 1)
    phi_a1_js_ms = np.array(phi_a1_js_ms)
    phi_t0_js = np.array(phi_t0_js).reshape(-1, 1)
    phi_t1_js_ms = np.array(phi_t1_js_ms)
    r_js_ms = np.array(r_js_ms)

#    phi_a0_js = np.array([b['phi_a0'] for b in bs]).reshape(-1, 1)
#    phi_a1_js_ms = np.array([b['phi_a1'] for b in bs])
#    phi_t0_js = np.array([b['phi_t0'] for b in bs]).reshape(-1, 1)
#    phi_t1_js_ms = np.array([b['phi_t1'] for b in bs])
#    r_js_ms = np.array([b['r'] for b in bs])

    return phi_a0_js, phi_a1_js_ms, phi_t0_js, phi_t1_js_ms, r_js_ms

