import os
import unittest
import numpy as np
import json

from heat_load_calc import sequence, conditions
from heat_load_calc.sequence import Sequence
from heat_load_calc.operation_mode import OperationMode
from heat_load_calc.interval import Interval
from heat_load_calc.tenum import EInterval
from heat_load_calc.boundaries import Boundaries

from test.test_steady.test_steady import TestCase, initialize, get_steady_state_conditions


# 定常状態のテスト
class TestSteadyState(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        テストの目的
        定常状態を想定した壁体の貫流熱損失と透過日射熱取得が解析解と一致することを確認する。
        日射を考慮（太陽位置、法線面直達日射、水平面天空日射を与える）して透過日射熱取得、相当外気温度を計算する。
        窓は２面を考慮し、透過日射の重ね合わせを確認する。
        内部発熱、換気を考慮する。
        床の温度差係数を0.7とする。その他の部位の温度差係数は1.0とする。
        
        計算条件
        建物モデル  1m角の立方体単室モデル
        部位構成    南面、東面以外の部位（4面）は合板、南面、東面は複層ガラスで構成される。
        """

        print('\n testing single zone steady')

        # 計算用フォルダ
        s_folder = os.path.join(os.path.dirname(__file__), 'data')

        # 住宅計算条件JSONファイルの読み込み
        house_data_path = os.path.join(s_folder, "mid_data_house.json")
        with open(house_data_path, 'r', encoding='utf-8') as js:
            d = json.load(js)

        sqc: Sequence = initialize(test_case=TestCase.SINGLE_ZONE, d=d)

        bs: Boundaries = sqc.bs

        c_n = get_steady_state_conditions(test_case=TestCase.SINGLE_ZONE, bs=bs)

        # 初期状態値の計算

        # 計算結果格納
        cls._c_n = c_n

        cls._c_n_pls = sqc.run_tick(n=-2, c_n=c_n, recorder=None)

    # 室空気温[℃]のテスト
    def test_room_temp(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_r_is_n, self._c_n_pls.theta_r_is_n)

    # 室内側表面熱流[W/m2]のテスト
    def test_heat_flow(self):

        np.testing.assert_array_almost_equal(self._c_n.q_s_js_n, self._c_n_pls.q_s_js_n)

    # 表面温度[℃]のテスト
    def test_surface_temp(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_mrt_hum_is_n, self._c_n_pls.theta_mrt_hum_is_n)

    # 等価室温[℃]のテスト
    def test_case_01_theta_ei(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_ei_js_n, self._c_n_pls.theta_ei_js_n)
