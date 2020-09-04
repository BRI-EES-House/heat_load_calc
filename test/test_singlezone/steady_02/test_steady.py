import json
import os
import shutil
import unittest

from heat_load_calc import s3_space_initializer
from heat_load_calc.weather import weather
from heat_load_calc.core import core


# @unittest.skip('skip single zone steady 02')
class TestSteadyState(unittest.TestCase):
    """
    ここにテストの目的を記述すること。
    """

    @classmethod
    def setUpClass(cls):

        print('\n testing single zone steady 02')

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

        # 対流熱伝達率の取得
        self.assertAlmostEqual(7.23138958337832, self._dd['rm0_t_r']['1989-12-31 00:00:00'])

    # 室内側表面熱流[W/m2]のテスト
    def test_case_01_heat_flow(self):

        self.assertAlmostEqual(16.6666666666667, self._dd['rm0_b0_qic_s']['1989-12-31 00:00:00'])

    # 表面温度[℃]のテスト
    def test_case_01_surface_temp(self):

        self.assertAlmostEqual(1.75089605734767, self._dd['rm0_b0_t_s']['1989-12-31 00:00:00'])


if __name__ == '__main__':

    unittest.main()

