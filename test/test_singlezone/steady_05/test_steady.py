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

        self.assertAlmostEqual(3.30840743877721, self._dd['rm0_t_r']['1989-12-31 00:00:00'])

    # 室内側表面熱流[W/m2]のテスト
    def test_heat_flow(self):

        self.assertAlmostEqual(15.3840945836677, self._dd['rm0_b1_qiall_s']['1989-12-31 00:00:00'])
        self.assertAlmostEqual(-31.1159054163324, self._dd['rm0_b2_qiall_s']['1989-12-31 00:00:00'])
        self.assertAlmostEqual(14.7040330548793, self._dd['rm0_b4_qiall_s']['1989-12-31 00:00:00'])
        self.assertAlmostEqual(-29.7404113895651, self._dd['rm0_b5_qiall_s']['1989-12-31 00:00:00'])

    # 表面温度[℃]のテスト
    def test_surface_temp(self):

        self.assertAlmostEqual(1.61615703314501, self._dd['rm0_b1_t_s']['1989-12-31 00:00:00'])
        self.assertAlmostEqual(6.73115703314502, self._dd['rm0_b2_t_s']['1989-12-31 00:00:00'])
        self.assertAlmostEqual(1.69096380131174, self._dd['rm0_b4_t_s']['1989-12-31 00:00:00'])
        self.assertAlmostEqual(6.57985269020063, self._dd['rm0_b5_t_s']['1989-12-31 00:00:00'])
