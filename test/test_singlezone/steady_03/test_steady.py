import json
import os
import shutil
import unittest

from heat_load_calc import s3_space_initializer
from heat_load_calc.weather import weather
from heat_load_calc.core import core


# 定常状態のテスト
class TestSteadyState(unittest.TestCase):
    """
    ここにテストの目的を記述すること。
    """

    @classmethod
    def setUpClass(cls):

        print('\n testing single zone steady 03')

        # 計算用フォルダ
        s_folder = str(os.path.dirname(__file__)) + '/data'

        # 計算条件読込
        js = open(s_folder + '/input_residential.json', 'r', encoding='utf-8')
        d = json.load(js)

        # 中間データ作成（建物のみ）
        s3_space_initializer.make_house_for_test(d=d, input_data_dir=s_folder, output_data_dir=s_folder)

        # 計算実行
        ds, dd = core.calc(input_data_dir=s_folder, output_data_dir=s_folder, show_detail_result=True)

        # 計算結果格納
        cls._ds = ds
        cls._dd = dd

    # 室空気温[℃]のテスト
    def test_case_01_room_temp(self):

        self.assertAlmostEqual(7.28499366028948, self._dd['rm0_t_r']['1989-12-31 00:00:00'])

    # 室内側表面熱流[W/m2]のテスト
    def test_case_01_heat_flow(self):

        self.assertAlmostEqual(16.9159256263269, self._dd['rm0_b0_qiall_s']['1989-12-31 00:00:00'])
        self.assertAlmostEqual(16.1681487468405, self._dd['rm0_b4_qiall_s']['1989-12-31 00:00:00'])

    # 表面温度[℃]のテスト
    def test_case_01_surface_temp(self):

        self.assertAlmostEqual(1.77708164899979, self._dd['rm0_b0_t_s']['1989-12-31 00:00:00'])
        self.assertAlmostEqual(1.85933710578008, self._dd['rm0_b4_t_s']['1989-12-31 00:00:00'])
