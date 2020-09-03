import json
import os
import shutil
import unittest

from heat_load_calc import s3_space_initializer
from heat_load_calc.core import core


# 定常状態のテスト
# @unittest.skip('skip single zone steady 01')
class TestSteadyState(unittest.TestCase):
    """
    ここにテストの目的を記述すること。
    """

    @classmethod
    def setUpClass(cls):

        print('\n testing single zone steady 01')

        # 計算用フォルダ
        s_folder = str(os.path.dirname(__file__)) + '/data'

        # 計算条件読込
        js = open(s_folder + '/input_residential.json', 'r', encoding='utf-8')
        d = json.load(js)

        # 中間データ作成（建物のみ）
        s3_space_initializer.make_house_for_test(d=d, input_data_dir=s_folder, output_data_dir=s_folder)

        # 計算実行
        ds, dd = core.calc(input_data_dir=s_folder, output_data_dir=s_folder)

        # 計算結果格納
        cls._ds = ds
        cls._dd = dd

    def test_case_01_room_temp(self):
        """
        室空気温[℃]のテスト
        """

        # 対流熱伝達率を放射熱伝達率のユニットテストより求め、室温を計算する必要がある
        # 対流熱伝達率の取得
        hc = self._dd['rm0_b0_hic_s']['1989-12-31 00:00:00']
        self.assertAlmostEqual(0.0 + 100/(6/(1/hc + 0.075 + 0.04)), self._dd['rm0_t_r']['1989-12-31 00:00:00'])

    def test_case_01_heat_flow(self):
        """
        室内側表面熱流[W/m2]のテスト
        """

        self.assertAlmostEqual(100/6, self._dd['rm0_b0_qic_s']['1989-12-31 00:00:00'])

    def test_case_01_surface_temp(self):
        """
        表面温度[℃]のテスト
        """

        self.assertAlmostEqual(0.0 + 100/6*(0.075 + 0.04), self._dd['rm0_b0_t_s']['1989-12-31 00:00:00'])
