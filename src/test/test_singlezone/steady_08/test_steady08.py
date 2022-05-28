import os
import unittest
import numpy as np
import pandas as pd
import csv
import json

from heat_load_calc.core import pre_calc_parameters
from heat_load_calc.core import conditions
from heat_load_calc.core import sequence
from heat_load_calc.core import operation_mode
from heat_load_calc.core import outdoor_condition


# 定常状態のテスト
class TestSteadyState(unittest.TestCase):
    """
    計算条件
    屋根と床が合板12mm、壁が複層ガラスの1m角の立方体の単室モデル。
    外気温度一定。日射、夜間放射は考慮なし。
    内部発熱一定。

    """

    @classmethod
    def setUpClass(cls):

        print('\n testing single zone steady 08')

        # 計算用フォルダ
        s_folder = os.path.join(os.path.dirname(__file__), 'data')

        # 住宅計算条件JSONファイルの読み込み
        house_data_path = os.path.join(s_folder, "mid_data_house.json")
        with open(house_data_path, 'r', encoding='utf-8') as js:
            rd = json.load(js)

        # 気象データ読み出し
        # 外界条件
        # 全ての値は0.0で一定とする。日射・夜間放射はなし。
        oc = outdoor_condition.OutdoorCondition(
            a_sun_ns=np.zeros(8760*4, dtype=float),
            h_sun_ns=np.zeros(8760*4, dtype=float),
            i_dn_ns=np.zeros(8760*4, dtype=float),
            i_sky_ns=np.zeros(8760*4, dtype=float),
            r_n_ns=np.zeros(8760*4, dtype=float),
            theta_o_ns=np.zeros(8760*4, dtype=float),
            x_o_ns=np.zeros(8760*4, dtype=float)
        )

        # ステップnの室iにおける局所換気量, m3/s, [i, 8760*4]
        # 局所換気量は常に 0.0 m3/s とする。
        v_mec_vent_local_is_ns = np.zeros((1, 8760*4), dtype=float)

        # ステップnの室iにおける内部発熱, W, [8760*4]
        # 内部発熱は常に 100 W とする。
        q_gen_is_ns = np.full((1, 8760*4), 100.0, dtype=float)

        # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [8760*4]
        # 内部発湿は常に 0.0 kg/s とする。
        x_gen_is_ns = np.zeros((1, 8760*4), dtype=float)

        # ステップnの室iにおける在室人数, [8760*4]
        # 在室人数は常に 0 人とする。
        n_hum_is_ns = np.zeros((1, 8760*4), dtype=float)

        # ステップnの室iにおける空調需要, [8760*4]
        ac_demand_is_ns = np.zeros((1, 8760*4), dtype=float)

        ac_operation = {
            "ac_demand_is_ns": ac_demand_is_ns
        }

        # pre_calc_parametersの構築
        ss, ppg = pre_calc_parameters.make_pre_calc_parameters(
            delta_t=900.0,
            rd=rd,
            q_gen_is_ns=q_gen_is_ns,
            x_gen_is_ns=x_gen_is_ns,
            v_vent_mec_local_is_ns=v_mec_vent_local_is_ns,
            n_hum_is_ns=n_hum_is_ns,
            ac_operation=ac_operation,
            ac_demand_is_ns=ac_demand_is_ns,
            oc=oc
        )

        q_srf_js_n = np.array([[16.66666667, 16.66666667, 16.66666667, 16.66666667,
                                16.66666667, 16.66666667]]).reshape(-1, 1)

        theta_ei_js_n = np.array(
            [[22.83332338, 22.83332338, 22.83332338, 22.83332338, 22.83332338, 22.83332338]]).reshape(-1, 1)

        # 初期状態値の計算
        c_n = conditions.Conditions(
            operation_mode_is_n=np.array([[operation_mode.OperationMode.STOP_CLOSE]]),
            theta_r_is_n=np.array([[24.658324874564500]]),
            theta_mrt_hum_is_n=np.array([[21.32499154]]),
            x_r_is_n=np.array([[0.0]]),
            theta_dsh_s_a_js_ms_n=q_srf_js_n * ss.phi_a1_js_ms / (1.0 - ss.r_js_ms),
            theta_dsh_s_t_js_ms_n=(np.dot(ss.k_ei_js_js, theta_ei_js_n) + ss.theta_dstrb_js_ns[:, 1].reshape(-1, 1)) * ss.phi_t1_js_ms / (1.0 - ss.r_js_ms),
            q_s_js_n=q_srf_js_n,
            theta_frt_is_n=np.array([[24.658324874564500]]),
            x_frt_is_n=np.array([[0.0]]),
            theta_ei_js_n=theta_ei_js_n
        )

        # 計算実行
        c_n_pls = sequence.run_tick(n=-2, delta_t=900.0, ss=ss, c_n=c_n, logger=None, run_up=True)

        # 計算結果格納
        cls._c_n = c_n
        cls._c_n_pls = c_n_pls

    # 室空気温[℃]のテスト
    def test_case_01_room_temp(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_r_is_n, self._c_n_pls.theta_r_is_n)

    # 室内側表面熱流[W/m2]のテスト
    def test_case_01_heat_flow(self):

        np.testing.assert_array_almost_equal(self._c_n.q_s_js_n, self._c_n_pls.q_s_js_n)

    # 表面温度[℃]のテスト
    def test_case_01_surface_temp(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_mrt_hum_is_n, self._c_n_pls.theta_mrt_hum_is_n)

    # 等価室温[℃]のテスト
    def test_case_01_theta_ei(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_ei_js_n, self._c_n_pls.theta_ei_js_n)

    # 表面温度絶対値テスト
    def test_case01_hum_mrt_abs(self):

        c_n_hum_theta_mrt = np.full(1, 21.32499154).reshape(-1, 1)
        np.testing.assert_array_almost_equal(c_n_hum_theta_mrt, self._c_n_pls.theta_mrt_hum_is_n)
