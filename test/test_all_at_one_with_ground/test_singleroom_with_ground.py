import json
import os
import shutil
import unittest

from heat_load_calc.initializer import initializer
from heat_load_calc.weather import weather
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

        # 計算条件読込
        js = open(s_folder + '/input_residential.json', 'r', encoding='utf-8')
        d = json.load(js)

        # weather.make_weather(region=d['common']['region'], output_data_dir=s_folder, csv_output=True)

        # 中間データ作成（境界条件は再構築しない）
        initializer.make_mid_data_house(d=d, output_data_dir=s_folder)
        # initializer.make_house(d=d, input_data_dir=s_folder, output_data_dir=s_folder)

        # 計算実行
        dd = core.calc(input_data_dir=s_folder, output_data_dir=s_folder,
                           show_detail_result=False, n_d_main=30, n_d_run_up=10, n_d_run_up_build=0)

        # 計算結果格納
        cls._dd = dd

    # 室空気温[℃]のテスト
    def test_case_01_room_temp(self):

        self.assertAlmostEqual(10.0057217473846, self._dd['rm0_t_r']['1989-1-30 23:45:00'])

    # 室内側表面熱流[W/m2]のテスト
    def test_case_01_heat_flow(self):

        self.assertAlmostEqual(-0.000471298032647407, self._dd['rm0_b0_qiall_s']['1989-1-30 23:45:00'])
        self.assertAlmostEqual(-0.000471298032647407, self._dd['rm0_b1_qiall_s']['1989-1-30 23:45:00'])

    # 表面温度[℃]のテスト
    def test_case_01_surface_temp(self):

        self.assertAlmostEqual(10.0058767197643, self._dd['rm0_b0_t_s']['1989-1-30 23:45:00'])
        self.assertAlmostEqual(10.0058767197643, self._dd['rm0_b1_t_s']['1989-1-30 23:45:00'])
