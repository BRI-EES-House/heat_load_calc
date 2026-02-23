import os
import unittest
import numpy as np
import json

from heat_load_calc import sequence, conditions, recorder
from heat_load_calc.sequence import Sequence
from heat_load_calc.operation_mode import OperationMode
from heat_load_calc.interval import Interval
from heat_load_calc.tenum import EInterval
from heat_load_calc.boundaries import Boundaries

from test.test_steady.test_steady import TestCase, initialize, get_steady_state_conditions


# 定常状態のテスト
class TestSteadyState(unittest.TestCase):
    """
    テストの目的
    定常状態を想定した壁体の貫流熱損失と透過日射熱取得が解析解と一致することを確認する。
    日射を考慮、夜間放射を無視。
    
    計算条件
    建物モデル  1m角立方体を上下に重ねた2室モデル
    部位構成    一般部位（8面）はせっこうボード12mm、南面窓は複層ガラスで構成される。
    　　　　　　内壁はボード壁
    """

    @classmethod
    def setUpClass(cls):

        print('\n testing 2 zone steady 01')

        # 計算用フォルダ
        s_folder = os.path.join(os.path.dirname(__file__), 'data')

        # 住宅計算条件JSONファイルの読み込み
        house_data_path = os.path.join(s_folder, "input.json")
        with open(house_data_path, 'r', encoding='utf-8') as js:
            d = json.load(js)

        sqc: Sequence = initialize(test_case=TestCase.MULTI_ZONE, d=d)

        bs: Boundaries = sqc.bs

        c_n = get_steady_state_conditions(test_case=TestCase.MULTI_ZONE, bs=bs)

        # 計算結果格納
        cls._c_n = c_n
        cls._c_n_pls = sqc.run_tick(n=0, c_n=c_n, recorder=None)
        cls._sqc = sqc

    # 室空気温[℃]のテスト
    def test_case_01_room_temp(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_r_is_n, self._c_n_pls.theta_r_is_n)

    # 室内側表面熱流[W/m2]のテスト
    def test_case_01_heat_flow(self):

        np.testing.assert_array_almost_equal(self._c_n.q_s_js_n, self._c_n_pls.q_s_js_n)

    # 人体のMRT[℃]のテスト
    def test_case_01_theta_mrt_hum(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_mrt_hum_is_n, self._c_n_pls.theta_mrt_hum_is_n)

    # 等価室温[℃]のテスト
    def test_case_01_theta_ei(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_ei_js_n, self._c_n_pls.theta_ei_js_n)

    # 内壁の熱流[W/m2]のテスト
    def test_case_01_heat_flow_inner_wall(self):

        self.assertAlmostEqual(self._c_n_pls.q_s_js_n[12][0], - self._c_n_pls.q_s_js_n[13][0])
        