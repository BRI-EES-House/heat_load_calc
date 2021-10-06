import json
import numpy as np
from typing import Tuple
import csv
import pandas as pd
from dataclasses import dataclass
from typing import List, Callable

from heat_load_calc.external.global_number import get_c_air, get_rho_air
from heat_load_calc.core import infiltration, response_factor, indoor_radiative_heat_transfer, shape_factor, \
    occupants_form_factor, boundary_simple, furniture
from heat_load_calc.core import ot_target
from heat_load_calc.core import next_condition
from heat_load_calc.core import humidification

from heat_load_calc.initializer.boundary_type import BoundaryType


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

    dehumidification_funcs: [Callable]


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
    h_r_js: np.ndarray

    # 地盤jにおける室内側対流熱伝達率, W/m2K, [j, 1]
    h_c_js: np.ndarray

    # ステップnの外気温度, degree C, [n]
    theta_o_ns: np.ndarray

    # ステップnの境界jにおける外気側等価温度の外乱成分, degree C, [j, 8760*4]
    theta_dstrb_js_ns: np.ndarray

    # 年平均外気温度, degree C
    theta_o_ave: float


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
    a_sun_ns, h_sun_ns, i_dn_ns, i_sky_ns, r_n_ns, theta_o_ns = _read_weather_data(input_data_dir=data_directory)

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
    v_vent_ex_is = (np.array([rm['ventilation']['mechanical'] for rm in rms]) / 3600).reshape(-1, 1)

    # 室iの隣室iからの機械換気量, m3/s, [i, i]
    v_int_vent_is_is = _get_v_int_vent_is_is(
        next_vent_is_ks=[rm['ventilation']['next_spaces'] for rm in rms]
    )

    # 室iの自然風利用時の換気量, m3/s, [i, 1]
    # 入力は m3/h なので、3600 で除して m3/s への変換を行っている。
    v_ntrl_vent_is = np.array([s['ventilation']['natural'] / 3600 for s in rms]).reshape(-1, 1)

    # 家具に関する物性値を取得する。
    #   室iの家具等の熱容量, J/K, [i, 1]
    #   室iの家具等と空気間の熱コンダクタンス, W/K, [i, 1]
    #   室iの家具等の湿気容量, kg/m3 kg/kgDA, [i, 1]
    #   室iの家具等と空気間の湿気コンダクタンス, kg/s (kg/kgDA), [i, 1]
    c_lh_frt_is, c_sh_frt_is, g_lh_frt_is, g_sh_frt_is = furniture.get_furniture_specs(
        furnitures=[rm['furniture'] for rm in rms],
        v_rm_is=v_rm_is
    )

    # endregion

    # region boundaries の読み込み

    # boundaries の取り出し

    bss, h_r_js, rfs = boundary_simple.get_boundary_simples(
        a_sun_ns=a_sun_ns,
        h_sun_ns=h_sun_ns,
        i_dn_ns=i_dn_ns,
        i_sky_ns=i_sky_ns,
        n_rm=n_rm,
        r_n_ns=r_n_ns,
        theta_o_ns=theta_o_ns,
        bs=rd['boundaries']
    )

    h_r_js = np.array([bs.h_r for bs in bss]).reshape(-1, 1)

    # 名前, [j, 1]
    name_js = np.array([bs.name for bs in bss]).reshape(-1, 1)

    # 名前2, [j, 1]
    sub_name_js = np.array([bs.sub_name for bs in bss]).reshape(-1, 1)

    # endregion

    # region equipments の読み込み

    # 室iの暖房方式として放射空調が設置されているかどうか。  bool値, [i, 1]
    # 室iの暖房方式として放射空調が設置されている場合の、放射暖房最大能力, W, [i, 1]
    is_radiative_heating_is = np.full(shape=(n_rm, 1), fill_value=False)
    lr_h_max_cap_is = np.zeros(shape=(n_rm, 1), dtype=float)

    heating_equipments = rd['equipments']['heating_equipments']

    for e_h in heating_equipments:
        if e_h['equipment_type'] == 'floor_heating':
            is_radiative_heating_is[e_h['property']['space_id']] = True
            lr_h_max_cap_is[e_h['property']['space_id']] = lr_h_max_cap_is[e_h['property']['space_id']] + e_h['property']['max_capacity'] * e_h['property']['area']

    # 室iの冷房方式として放射空調が設置されているかどうか。  bool値, [i, 1]
    # 室iの冷房方式として放射空調が設置されている場合の、放射冷房最大能力, W, [i, 1]
    is_radiative_cooling_is = np.full(shape=(n_rm, 1), fill_value=False)
    lr_cs_max_cap_is = np.zeros(shape=(n_rm, 1), dtype=float)

    cooling_equipments = rd['equipments']['cooling_equipments']

    for e_c in cooling_equipments:
        if e_c['equipment_type'] == 'floor_cooling':
            is_radiative_cooling_is[e_c['property']['space_id']] = True
            lr_cs_max_cap_is[e_c['property']['space_id']] = lr_cs_max_cap_is[e_c['property']['space_id']] + e_c['property']['max_capacity'] * e_c['property']['area']

    # endregion


    # region スケジュール化されたデータの読み込み

    pp = pd.read_csv(data_directory + '/weather.csv', index_col=0, engine='python')

    theta_o_ns = pp['temperature'].values
    # ステップn+1に対応するために0番要素に最終要素を代入
    theta_o_ns = np.append(theta_o_ns, theta_o_ns[0])

    x_o_ns = pp['absolute humidity'].values
    # ステップn+1に対応するために0番要素に最終要素を代入
    x_o_ns = np.append(x_o_ns, x_o_ns[0])

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
    if q_trans_sol_calculate:
        q_trs_sol_is_ns = np.array([
            np.sum(np.array([bs.q_trs_sol for bs in bss if bs.connected_room_id == i]), axis=0)
            for i in range(n_rm)
        ])
    else:
        with open(data_directory + '/mid_data_q_trs_sol.csv', 'r') as f:
            r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            q_trs_sol_is_ns = np.array([row for row in r]).T

    # ステップn+1に対応するために0番要素に最終要素を代入
    q_trs_sol_is_ns = np.append(q_trs_sol_is_ns, q_trs_sol_is_ns[:, 0:1], axis=1)

    # ステップnの境界jにおける裏面等価温度, ℃, [j, 8760*4]
    if theta_o_sol_calculate:
        theta_o_sol_js_ns = np.array([bs.theta_o_sol for bs in bss])
    else:
        with open(data_directory + '/mid_data_theta_o_sol.csv', 'r') as f:
            r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            theta_o_sol_js_ns = np.array([row for row in r]).T

    # ステップn+1に対応するために0番要素に最終要素を代入
    theta_o_sol_js_ns = np.append(theta_o_sol_js_ns, theta_o_sol_js_ns[:, 0:1], axis=1)

    # endregion

    # region 読み込んだ変数をベクトル表記に変換する
    # ただし、1次元配列を縦ベクトルに変換する処理等は読み込み時に np.reshape を適用して変換している。

    # 地盤かどうか, [j, 1]
    is_ground_js = np.array([bs.boundary_type == BoundaryType.Ground for bs in bss]).reshape(-1, 1)

    # 室iと境界jの関係を表す係数（境界jから室iへの変換）
    # [[p_0_0 ... ... p_0_j]
    #  [ ...  ... ...  ... ]
    #  [p_i_0 ... ... p_i_j]]
    p_is_js = np.zeros((n_rm, len(bss)), dtype=int)
    for bs in bss:
        p_is_js[bs.connected_room_id, bs.id] = 1

    # 室iと境界jの関係を表す係数（室iから境界jへの変換）
    # [[p_0_0 ... p_0_i]
    #  [ ...  ...  ... ]
    #  [ ...  ...  ... ]
    #  [p_j_0 ... p_j_i]]
    p_js_is = p_is_js.T

    # 境界jの裏面温度に他の境界の等価温度が与える影響, [j, j]
    k_ei_js_js = np.array([get_k_ei_js_j(bs=bs, n_boundaries=len(bss)) for bs in bss])

    # endregion

    # region 読み込んだ値から新たに係数を作成する

    # TODO: is_radiative_is は flr の計算のみに使用されている。
    # flr の値は、暖房と冷房で違うのか？違う場合は、暖房用と冷房用で分ける必要があるのかどうかを精査しないといけない。
    is_radiative_is = np.array([s['is_radiative'] for s in rms])

    # 室iに設置された放射暖房の対流成分比率, [i, 1]
    # TODO: 入力ファイルから与えられるのではなく、設備の入力情報から計算するべき。
    beta_is = np.array([s['beta'] for s in rms]).reshape(-1, 1)

    # 境界jの面積, m2, [j, 1]
    a_srf_js = np.array([bs.area for bs in bss]).reshape(-1, 1)

    # 境界 j が床か否か, [j]
    is_floor_js = np.array([bs.is_floor for bs in bss])

    # 隣接する空間のID, [j]
    # 注意：　この変数は後の numpy の操作のみに使用されるため、[j, 1]の縦行列ではなく、[j] の1次元配列とした。
    connected_room_id_js = np.array([bs.connected_room_id for bs in bss])

    # 境界の数
    n_boundaries = len(bss)

    # 境界jの室に設置された放射暖房の放熱量のうち放射成分に対する境界jの室内側吸収比率
    f_mrt_hum_js = occupants_form_factor.get_f_mrt_hum_js(
        a_srf_js=a_srf_js.flatten(),
        connected_room_id_js=connected_room_id_js,
        is_floor_js=is_floor_js,
        n_boundaries=n_boundaries,
        n_spaces=n_rm
    )

    # 室iの在室者に対する境界j*の形態係数, [i, j]
    f_mrt_hum_is_js = p_is_js * f_mrt_hum_js[np.newaxis, :]

    # 境界jの吸熱応答係数の初項, m2K/W, [j, 1]
    phi_a0_js = np.array([rf.rfa0 for rf in rfs]).reshape(-1, 1)
    # 境界jの項別公比法における項mの吸熱応答係数の第一項 , m2K/W, [j, 12]
    phi_a1_js_ms = np.array([rf.rfa1 for rf in rfs])
    # 境界jの貫流応答係数の初項, [j, 1]
    phi_t0_js = np.array([rf.rft0 for rf in rfs]).reshape(-1, 1)
    # 境界jの項別公比法における項mの貫流応答係数の第一項, [j, 12]
    phi_t1_js_ms = np.array([rf.rft1 for rf in rfs])
    # 境界jの項別公比法における項mの公比, [j, 12]
    r_js_ms = np.array([rf.row for rf in rfs])

    # 境界jの室に設置された放射暖房の放熱量のうち放射成分に対する境界jの室内側吸収比率
    # 放射暖房の発熱部位の設定（とりあえず床発熱） 表7
    # TODO: 発熱部位を指定して、面積按分するように変更すべき。
    flr_js = indoor_radiative_heat_transfer.get_flr_js(
        a_srf_js=a_srf_js.flatten(),
        connected_room_id_js=connected_room_id_js,
        is_floor_js=is_floor_js,
        is_radiative_heating_is=is_radiative_is.flatten(),
        n_boundaries=n_boundaries,
        n_spaces=n_rm
    )

    # 室iに設置された放射暖房の放熱量のうち放射成分に対する境界jの室内側吸収比率, [j, i]
    flr_js_is = p_js_is * flr_js[:, np.newaxis]

    # 室iの空気の熱容量, J/K, [i, 1]
    c_rm_is = v_rm_is * get_rho_air() * get_c_air()

    # 平均放射温度計算時の各部位表面温度の重み, [i, j]
    f_mrt_is_js = shape_factor.get_f_mrt_is_js(a_srf_js=a_srf_js, h_r_js=h_r_js, p_is_js=p_is_js)

    # 境界jの室内側表面対流熱伝達率, W/m2K, [j, 1]
    h_c_js = np.array([bs.h_c for bs in bss]).reshape(-1, 1)

    # 境界jの室内側表面総合熱伝達率, W/m2K, [j, 1]
    h_i_js = h_c_js + h_r_js

    # ステップnの室iにおける機械換気量（全般換気量+局所換気量）, m3/s, [i, n]
    v_mec_vent_is_ns = v_vent_ex_is + v_mec_vent_local_is_ns

    # 室内侵入日射のうち家具に吸収される割合
    # TODO: これは入力値にした方がよいのではないか？
    r_sol_fnt = 0.5

    # ステップnの室iにおける家具の吸収日射量, W, [i, n]
    q_sol_frnt_is_ns = q_trs_sol_is_ns * r_sol_fnt

    # 境界jの日射吸収の有無, [j, 1]
    is_solar_abs_js = np.array([bs.is_solar_absorbed_inside for bs in bss]).reshape(-1, 1)

    # 室iにおける日射が吸収される境界の面積の合計, m2, [i, 1]
    a_srf_abs_is = np.dot(p_is_js, a_srf_js * is_solar_abs_js)

    # ステップnの境界jにおける透過日射吸収熱量, W/m2, [j, n]
    # TODO: 日射の吸収割合を入力値にした方がよいのではないか？
    q_sol_js_ns = np.dot(p_js_is, q_trs_sol_is_ns / a_srf_abs_is)\
        * is_solar_abs_js * (1.0 - r_sol_fnt)

    # 温度差係数
    k_eo_js = np.array([bs.h_td for bs in bss]).reshape(-1, 1)

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

    # CRX, degree C, [j, n]
    crx_js_ns = phi_a0_js * q_sol_js_ns\
        + phi_t0_js / h_i_js * np.dot(k_ei_js_js, q_sol_js_ns)\
        + phi_t0_js * theta_dstrb_js_ns

    # FLB, K/W, [j, i]
    flb_js_is = flr_js_is * (1.0 - beta_is.T) * phi_a0_js / a_srf_js\
        + np.dot(k_ei_js_js, flr_js_is * (1.0 - beta_is.T)) * phi_t0_js / h_i_js / a_srf_js

    # WSR, [j, i]
    wsr_js_is = np.dot(ivs_ax_js_js, fia_js_is)

    # WSC, degree C, [j, n]
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
        lr_h_max_cap_is=lr_h_max_cap_is,
        lr_cs_max_cap_is=lr_cs_max_cap_is
    )

    # endregion

    dehumidification_funcs = [
        humidification.make_dehumidification_function(
            n_room=n_rm, equipment_type=equipment['equipment_type'], prop=equipment['property']
        ) for equipment in cooling_equipments
    ]

    pre_calc_parameters = PreCalcParameters(
        n_spaces=n_rm,
        id_space_is=id_rm_is,
        name_space_is=name_rm_is,
        v_room_is=v_rm_is,
        c_room_is=c_rm_is,
        c_sh_frt_is=c_sh_frt_is,
        c_lh_frt_is=c_lh_frt_is,
        g_sh_frt_is=g_sh_frt_is,
        g_lh_frt_is=g_lh_frt_is,
        v_int_vent_is_is=v_int_vent_is_is,
        name_bdry_js=name_js,
        sub_name_bdry_js=sub_name_js,
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
        get_ot_target_and_h_hum=get_ot_target_and_h_hum,
        get_infiltration=get_infiltration,
        calc_next_temp_and_load=calc_next_temp_and_load,
        dehumidification_funcs=dehumidification_funcs
    )

    # 地盤の数
    n_grounds = sum(bs.boundary_type == BoundaryType.Ground for bs in bss)

    pre_calc_parameters_ground = PreCalcParametersGround(
        n_grounds=n_grounds,
        r_js_ms=r_js_ms[is_ground_js.flatten(), :],
        phi_a0_js=phi_a0_js[is_ground_js.flatten(), :],
        phi_t0_js=phi_t0_js[is_ground_js.flatten(), :],
        phi_a1_js_ms=phi_a1_js_ms[is_ground_js.flatten(), :],
        phi_t1_js_ms=phi_t1_js_ms[is_ground_js.flatten(), :],
        h_r_js=h_r_js[is_ground_js.flatten(), :],
        h_c_js=h_c_js[is_ground_js.flatten(), :],
        theta_o_ns=theta_o_ns,
        theta_dstrb_js_ns=theta_dstrb_js_ns[is_ground_js.flatten(), :],
        theta_o_ave=theta_o_ave,
    )

    return pre_calc_parameters, pre_calc_parameters_ground


def _get_v_int_vent_is_is(next_vent_is_ks: List[List[dict]]) -> np.ndarray:
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
                [[0.0, 0.0, 0.0,  0.0],
                 [3.0, 0.0, 0.0,  1.5],
                 [4.0, 3.0, 0.0,  1.0],
                 [0.0, 0.0, 0.0,  0.0]]
    """

    n_rooms = len(next_vent_is_ks)

    # 隣室iから室iへの換気量マトリックス, m3/s [i, i]
    v_int_vent_is_is = np.zeros((n_rooms, n_rooms), dtype=float)

    # 室iのループ（風下室ループ）
    for i, next_vent_i_ks in enumerate(next_vent_is_ks):

        # 室iにおける経路jのループ（風上室ループ）
        # 取得するのは、(ID: int, 換気量(m3/h): float) のタプル
        for next_vent_i_k in next_vent_i_ks:

            idx = next_vent_i_k['upstream_room_id']

            # 入力は m3/h なので、3600 で除して m3/s への変換を行っている。
            volume = next_vent_i_k['volume'] / 3600

            # 風上側
            if i != idx:
                v_int_vent_is_is[i, idx] += volume

    return v_int_vent_is_is


def get_k_ei_js_j(bs, n_boundaries):

    k_ei_js_j = [0.0] * n_boundaries

    if bs.boundary_type in [
        BoundaryType.ExternalOpaquePart,
        BoundaryType.ExternalTransparentPart,
        BoundaryType.ExternalGeneralPart
    ]:

        h = bs.h_td

        # 温度差係数が1.0でない場合はk_ei_jsに値を代入する。
        # id は自分自身の境界IDとし、自分自身の表面の影響は1.0から温度差係数を減じた値になる。
        if h < 1.0:
            k_ei_js_j[bs.id] = round(1.0 - h, 1)
        else:
            # 温度差係数が1.0の場合は裏面の影響は何もないため k_ei_js に操作は行わない。
            pass

    elif bs.boundary_type == BoundaryType.Internal:

        # 室内壁の場合にk_ei_jsを登録する。
        k_ei_js_j[int(bs.rear_surface_boundary_id)] = 1.0

    else:

        # 外皮に面していない場合、室内壁ではない場合（地盤の場合が該当）は、k_ei_js に操作は行わない。
        pass

    return k_ei_js_j


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

    return a_sun_ns, h_sun_ns, i_dn_ns, i_sky_ns, r_n_ns, theta_o_ns
