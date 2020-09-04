import json
import os
import shutil
import unittest

from heat_load_calc import s3_space_initializer
from heat_load_calc.weather import weather
from heat_load_calc.core import core


# 定常状態のテスト
class TestSteadyState(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

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
    def test_room_temp(self):

        self.assertAlmostEqual(4.57216538442016, self._dd['rm0_t_r']['1989-12-31 00:00:00'])

    # 室内側表面熱流[W/m2]のテスト
    def test_heat_flow(self):

        self.assertAlmostEqual(12.780921581686, self._dd['rm0_b1_qiall_s']['1989-12-31 00:00:00'])
        self.assertAlmostEqual(36.6603790567287, self._dd['rm0_b4_qiall_s']['1989-12-31 00:00:00'])
        self.assertAlmostEqual(12.2159346059803, self._dd['rm0_b5_qiall_s']['1989-12-31 00:00:00'])

    # 表面温度[℃]のテスト
    def test_surface_temp(self):

        self.assertAlmostEqual(1.34268391303035, self._dd['rm0_b1_t_s']['1989-12-31 00:00:00'])
        self.assertAlmostEqual(4.2159435914795, self._dd['rm0_b4_t_s']['1989-12-31 00:00:00'])
        self.assertAlmostEqual(1.40483248036838, self._dd['rm0_b5_t_s']['1989-12-31 00:00:00'])
