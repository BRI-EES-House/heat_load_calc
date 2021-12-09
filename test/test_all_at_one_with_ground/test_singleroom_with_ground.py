import os
import unittest

from heat_load_calc.core import core


# 定常状態のテスト
class TestSigleRoomWithFround(unittest.TestCase):
    """
    計算条件
    土間床２面のみを有する単室。
    外気温度は10℃一定。日射、夜間放射は考慮なし。
    内部発熱なし。

    """

    @classmethod
    def setUpClass(cls):

        print('\n testing single room with ground')

        # 計算用フォルダ
        s_folder = str(os.path.dirname(__file__)) + '/data'

        # 計算実行
        dd_i, dd_a = core.calc(input_data_dir=s_folder, output_data_dir=s_folder,
                           show_detail_result=True, n_d_main=30, n_d_run_up=10, n_d_run_up_build=0)

        # 計算結果格納
        cls._dd_i = dd_i
        cls._dd_a = dd_a

    # 室空気温[℃]のテスト
    def test_case_01_room_temp(self):

        self.assertAlmostEqual(10.0057217473846, self._dd_i['rm0_t_r']['1989-1-31 0:00:00'])

    # 室内側表面熱流[W/m2]のテスト
    def test_case_01_heat_flow(self):

        self.assertAlmostEqual(-0.000471298032647407, self._dd_i['rm0_b0_qiall_s']['1989-1-31 0:00:00'])
        self.assertAlmostEqual(-0.000471298032647407, self._dd_i['rm0_b1_qiall_s']['1989-1-31 0:00:00'])

    # 表面温度[℃]のテスト
    def test_case_01_surface_temp(self):

        self.assertAlmostEqual(10.0058767197643, self._dd_i['rm0_b0_t_s']['1989-1-31 0:00:00'])
        self.assertAlmostEqual(10.0058767197643, self._dd_i['rm0_b1_t_s']['1989-1-31 0:00:00'])
