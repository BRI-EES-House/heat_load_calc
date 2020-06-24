import json
import numpy as np
import csv

from heat_load_calc.external.global_number import get_c_air, get_rho_air
from heat_load_calc.core import shape_factor
import heat_load_calc.a16_blowing_condition_rac as a16


class PreCalcParameters:

    def __init__(
            self,
            number_of_spaces,
            number_of_bdries,
            space_name_is,
            v_room_is,
            c_cap_w_frt_is,
            c_w_frt_is,
            c_room_is,
            c_cap_h_frt_is,
            c_h_frt_is,
            v_int_vent_is_is,
            name_bdry_js,
            sub_name_bdry_js,
            a_srf_js,
            v_mec_vent_is_ns,
            q_gen_is_ns,
            n_hum_is_ns,
            x_gen_is_ns,
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
            brm_non_vent_is_is,
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
        self.v_room_is = v_room_is

        # 室iの熱容量, J/K, [i, 1]
        self.c_room_is = c_room_is

        # 室iの家具等の熱容量, J/K, [i, 1]
        self.c_cap_h_frt_is = c_cap_h_frt_is

        # 室iの家具等の湿気容量, kg/m3 (kg/kgDA), [i, 1]
        self.c_cap_w_frt_is = c_cap_w_frt_is

        # 室iの家具等と空気間の熱コンダクタンス, W/K, [i, 1]
        self.c_h_frt_is = c_h_frt_is

        # 室iの家具等と空気間の湿気コンダクタンス, kg/s (kg/kgDA), [i, 1]
        self.c_w_frt_is = c_w_frt_is

        # ステップnにおける室iの空調需要, [i, 8760*4]
        self.ac_demand_is_ns = ac_demand_is_ns

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
        self.v_int_vent_is_is = v_int_vent_is_is

        # 統合された境界j*の名前, [j*]
        self.name_bdry_js = name_bdry_js

        # 統合された境界j*の名前2, [j*]
        self.sub_name_bdry_js = sub_name_bdry_js

        # 境界jが地盤かどうか, [j]
        self.is_ground_js = is_ground_js

        # 統合された境界j*の面積, m2, [j, 1]
        self.a_srf_js = a_srf_js

        # ステップnの集約境界j*における外気側等価温度の外乱成分, degree C, [j*, 8760*4]
        self.theta_dstrb_js_ns = theta_dstrb_js_ns

        # BRM(換気なし), W/K, [i, i]
        self.brm_non_vent_is_is = brm_non_vent_is_is

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

        self.total_number_of_bdry = number_of_bdries
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
        self.wsb_js_is = wsb_js_is

        # 床暖房の発熱部位？
        self.flr_js_is = flr_js_is

        # WSC, W, [j, n]
        self.wsc_js_ns = wsc_js_ns

        # 境界jの裏面温度に他の境界の等価温度が与える影響, [j, j]
        self.k_ei_js_js = k_ei_js_js


def make_pre_calc_parameters():

    with open('mid_data_house.json') as f:
        rd = json.load(f)

    # region spaces の読み込み

    # spaces の取り出し
    ss = rd['spaces']

    # id, [i]
    spaces_id_is = [s['id'] for s in ss]

    # 空間iの名前, [i]
    space_name_is = [s['name'] for s in ss]

    # 空間iの気積, m3, [i, 1]
    v_room_is = np.array([s['volume'] for s in ss]).reshape(-1, 1)

    # 空間iのC値, [i]
    c_value_is = np.array([s['c_value'] for s in ss])

    # 室iに設置された放射暖房の対流成分比率, [i, 1]
    beta_is = np.array([s['beta'] for s in ss]).reshape(-1, 1)

    # 室iの機械換気量（局所換気を除く）, m3/h, [i]
    v_vent_ex_is = np.array([s['ventilation']['mechanical'] for s in ss])

    # 室iの隣室iからの機械換気量, m3/s, [i, i]
    v_int_vent_is_is = np.array([s['ventilation']['next_spaces'] for s in ss])

    # 室iの自然風利用時の換気量, m3/s, [i, 1]
    v_ntrl_vent_is = np.array([s['ventilation']['natural'] for s in ss]).reshape(-1, 1)

    # 室iの家具等の熱容量, J/K, [i, 1]
    c_cap_h_frt_is = np.array([s['furniture']['heat_capacity'] for s in ss]).reshape(-1, 1)

    # 室iの家具等と空気間の熱コンダクタンス, W/K, [i, 1]
    c_h_frt_is = np.array([s['furniture']['heat_cond'] for s in ss]).reshape(-1, 1)

    # 室iの家具等の湿気容量, kg/m3 kg/kgDA, [i, 1]
    c_cap_w_frt_is = np.array([s['furniture']['moisture_capacity'] for s in ss]).reshape(-1, 1)

    # 室iの家具等と空気間の湿気コンダクタンス, kg/s (kg/kgDA), [i, 1]
    c_w_frt_is = np.array([s['furniture']['moisture_cond'] for s in ss]).reshape(-1, 1)

    # 室iの暖房方式として放射空調が設置されているかどうか。  bool値, [i, 1]
    # 室iの暖房方式として放射空調が設置されている場合の、放射暖房最大能力, W, [i, 1]
    is_radiative_heating_is_list = []
    lrcap_is_list = []
    for i, s in enumerate(ss):
        if s['equipment']['heating']['radiative']['installed']:
            is_radiative_heating_is_list.append(True)
            lrcap_is_list.append(s['equipment']['heating']['radiative']['max_capacity'])
        else:
            is_radiative_heating_is_list.append(False)
            lrcap_is_list.append(0.0)
    is_radiative_heating_is = np.array(is_radiative_heating_is_list)
    lrcap_is = np.array(lrcap_is_list)

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
    is_radiative_cooling_is = np.array(is_radiative_cooling_is_list)
    radiative_cooling_max_capacity_is = np.array(radiative_cooling_max_capacity_is_list)

    qmin_c_is = np.array([s['equipment']['cooling']['convective']['q_min'] for s in ss])
    qmax_c_is = np.array([s['equipment']['cooling']['convective']['q_max'] for s in ss])
    Vmin_is = np.array([s['equipment']['cooling']['convective']['v_min'] for s in ss])
    Vmax_is = np.array([s['equipment']['cooling']['convective']['v_max'] for s in ss])

    # endregion

    # region boundaries の読み込み

    # boundaries の取り出し
    bs = rd['boundaries']

    # id, [j]
    bdry_id_js = [b['id'] for b in bs]

    # 名前, [j]
    name_bdry_js = np.array([b['name'] for b in bs])

    # 名前2, [j]
    sub_name_bdry_js= [b['sub_name'] for b in bs]

    # 地盤かどうか, [j]
    is_ground_js = [{'true': True, 'false': False}[b['is_ground']] for b in bs]

    # 隣接する空間のID, [j]
    connected_space_id_js = np.array([b['connected_space_id'] for b in bs])

    # 境界jの面積, m2, [j, 1]
    a_srf_js = np.array([b['area'] for b in bs]).reshape(-1, 1)

    # 境界jの吸熱応答係数の初項, m2K/W, [j, 1]
    phi_a0_js = np.array([b['phi_a0'] for b in bs]).reshape(-1, 1)

    # 境界jの項別公比法における項mの吸熱応答係数の第一項 , m2K/W, [j, 12]
    phi_a1_js_ms = np.array([b['phi_a1'] for b in bs])

    # 境界jの貫流応答係数の初項, [j, 1]
    phi_t0_js = np.array([b['phi_t0'] for b in bs]).reshape(-1, 1)

    # 境界jの項別公比法における項mの貫流応答係数の第一項, [j, 12]
    phi_t1_js_ms = np.array([b['phi_t1'] for b in bs])

    # 境界jの項別公比法における項mの公比, [j, 12]
    r_js_ms = np.array([b['r'] for b in bs])

    # 境界jの室内側表面総合熱伝達率, W/m2K, [j, 1]
    h_i_js = np.array([b['h_i'] for b in bs]).reshape(-1, 1)

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

    # ステップnの室iにおける局所換気量, m3/s, [i, 8760*4]
    with open('mid_data_local_vent.csv', 'r') as f:
        r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        v_mec_vent_local_is_ns = np.array([row for row in r]).T

    # ステップnの室iにおける内部発熱, W, [8760*4]
    with open('mid_data_heat_generation.csv', 'r') as f:
        r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        q_gen_is_ns = np.array([row for row in r]).T

    # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [8760*4]
    with open('mid_data_moisture_generation.csv', 'r') as f:
        r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        x_gen_is_ns = np.array([row for row in r]).T

    # ステップnの室iにおける在室人数, [8760*4]
    with open('mid_data_occupants.csv', 'r') as f:
        r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        n_hum_is_ns = np.array([row for row in r]).T

    # ステップnの室iにおける空調需要, [8760*4]
    with open('mid_data_ac_demand.csv', 'r') as f:
        r = csv.reader(f)
        ac_demand_is_ns2 = np.array([row for row in r]).T
    # ｓｔｒ型からbool型に変更
    ac_demand_is_ns = np.vectorize(lambda x: {'True': True, 'False': False}[x])(ac_demand_is_ns2)

    # ステップnの室iにおける窓の透過日射熱取得, W, [8760*4]
    with open('mid_data_q_trs_sol.csv', 'r') as f:
        r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        q_trs_sol_is_ns = np.array([row for row in r]).T

    # ステップnの境界jにおける裏面等価温度, ℃, [j, 8760*4]
    with open('mid_data_theta_o_sol.csv', 'r') as f:
        r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        theta_o_sol_js_ns = np.array([row for row in r]).T

    # endregion

    # region 読み込んだ変数をベクトル表記に変換する
    # ただし、1次元配列を縦ベクトルに変換する処理等は読み込み時に np.reshape を適用して変換している。

    # Spaceの数
    number_of_spaces = len(ss)

    # 境界の数
    number_of_bdries = len(bs)

    # 室iと境界jの関係を表す係数（境界jから室iへの変換）
    # [[p_0_0 ... ... p_0_j]
    #  [ ...  ... ...  ... ]
    #  [p_i_0 ... ... p_i_j]]
    p_is_js = np.zeros((number_of_spaces, number_of_bdries), dtype=int)
    for i in range(number_of_spaces):
        p_is_js[i, connected_space_id_js == i] = 1

    # 室iと境界jの関係を表す係数（室iから境界jへの変換）
    # [[p_0_0 ... p_i_0]
    #  [ ...  ...  ... ]
    #  [ ...  ...  ... ]
    #  [p_0_j ... p_i_j]]
    p_js_is = p_is_js.T

    # 境界jの裏面温度に他の境界の等価温度が与える影響, [j, j]
    k_ei_js_js = []
    for k_ei_id_j, k_ei_coef_j in zip(k_ei_id_js, k_ei_coef_js):
        k_ei_js = [0.0] * number_of_bdries
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
    c_room_is = v_room_is * get_rho_air() * get_c_air()

    # 境界jの室内側表面放射熱伝達率, W/m2K, [j, 1]
    h_r_js = shape_factor.get_h_r_js(a_srf_js=a_srf_js, p_js_is=p_js_is)

    # 平均放射温度計算時の各部位表面温度の重み, [i, j]
    f_mrt_is_js = shape_factor.get_f_mrt_is_js(a_srf_js=a_srf_js, h_r_js=h_r_js, p_is_js=p_is_js)

    # 境界jの室内側表面対流熱伝達率, W/m2K, [j, 1]
    h_c_js = np.clip(h_i_js - h_r_js, 0.0, None)

    # ステップnの室iにおける機械換気量（全般換気量+局所換気量）, m3/s, [i, n]
    v_mec_vent_is_ns = v_vent_ex_is[:, np.newaxis] + v_mec_vent_local_is_ns

    # 室内侵入日射のうち家具に吸収される割合
    r_sol_fnt = 0.5

    # ステップnの室iにおける家具の吸収日射量, W, [i, n]
    q_sol_frnt_is_ns = q_trs_sol_is_ns * r_sol_fnt

    # 室iにおける日射が吸収される境界の面積の合計, m2, [i, 1]
    a_srf_abs_is = np.dot(p_is_js, a_srf_js * is_solar_abs_js)

    # ステップnの境界jにおける透過日射吸収熱量, W/m2, [j, n]
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
    brm_non_vent_is_is = np.diag(c_room_is.flatten() / 900.0)\
        + np.dot(p_is_js, (p_js_is - wsr_js_is) * a_srf_js * h_c_js)\
        + np.diag((c_cap_h_frt_is * c_h_frt_is / (c_cap_h_frt_is + c_h_frt_is * 900.0)).flatten())

    # endregion

    def get_vac_xeout_is(lcs_is_n, theta_r_is_npls, operation_mode_is_n):

        vac_is_n = []
        xeout_is_n = []

        for lcs_i_n, theta_r_i_npls, operation_mode_i_n, Vmin_i, Vmax_i, qmin_c_i, qmax_c_i \
            in zip(lcs_is_n, theta_r_is_npls, operation_mode_is_n, Vmin_is, Vmax_is, qmin_c_is, qmax_c_is):
            Vac_n_i, xeout_i_n = a16.calcVac_xeout(Lcs=lcs_i_n, Vmin=Vmin_i, Vmax=Vmax_i, qmin_c=qmin_c_i, qmax_c=qmax_c_i, Tr=theta_r_i_npls, operation_mode=operation_mode_i_n)
            vac_is_n.append(Vac_n_i)
            xeout_is_n.append(xeout_i_n)

        return np.array(vac_is_n), np.array(xeout_is_n)

    pre_calc_parameters = PreCalcParameters(
        number_of_spaces=number_of_spaces,
        number_of_bdries=number_of_bdries,
        space_name_is=space_name_is,
        v_room_is=v_room_is,
        c_cap_w_frt_is=c_cap_w_frt_is,
        c_w_frt_is=c_w_frt_is,
        c_room_is=c_room_is,
        c_cap_h_frt_is=c_cap_h_frt_is,
        c_h_frt_is=c_h_frt_is,
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
        r_js_ms=r_js_ms,
        phi_t0_js=phi_t0_js,
        phi_a0_js=phi_a0_js,
        phi_t1_js_ms=phi_t1_js_ms,
        phi_a1_js_ms=phi_a1_js_ms,
        q_trs_sol_is_ns=q_trs_sol_is_ns,
        v_ntrl_vent_is=v_ntrl_vent_is,
        ac_demand_is_ns=ac_demand_is_ns,
        is_radiative_heating_is=np.array(is_radiative_heating_is).reshape(-1, 1),
        is_radiative_cooling_is=np.array(is_radiative_cooling_is).reshape(-1, 1),
        lrcap_is=lrcap_is,
        radiative_cooling_max_capacity_is=radiative_cooling_max_capacity_is,
        flr_js_is=flr_js_is,
        h_r_js=h_r_js,
        h_c_js=h_c_js,
        f_mrt_is_js=f_mrt_is_js,
        q_sol_js_ns=q_sol_js_ns,
        q_sol_frnt_is_ns=q_sol_frnt_is_ns,
        beta_is=beta_is,
        wsr_js_is=wsr_js_is,
        wsb_js_is=wsb_js_is,
        brm_non_vent_is_is=brm_non_vent_is_is,
        ivs_ax_js_js=ivs_ax_js_js,
        brl_is_is=brl_is_is,
        p_is_js=p_is_js,
        p_js_is=p_js_is,
        get_vac_xeout_is=get_vac_xeout_is,
        is_ground_js=is_ground_js,
        wsc_js_ns=wsc_js_ns,
        k_ei_js_js=k_ei_js_js
    )

    return pre_calc_parameters

