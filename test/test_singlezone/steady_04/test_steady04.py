import json
import os
import shutil
import unittest

from heat_load_calc.initializer import initializer
from heat_load_calc.weather import weather
from heat_load_calc.core import core


# 定常状態のテスト
class TestSteadyState(unittest.TestCase):
    """
    屋根と床が合板12mm、壁が複層ガラスの1m角の立方体の単室モデル。
    外気温度一定。日射、夜間放射は考慮なし。
    内部発熱一定。
    換気あり
    """

    @classmethod
    def setUpClass(cls):

        print('\n testing single zone steady 04')

        # 計算用フォルダ
        s_folder = str(os.path.dirname(__file__)) + '/data'

        # 計算条件読込
        js = open(s_folder + '/input_residential.json', 'r', encoding='utf-8')
        d = json.load(js)

        # 中間データ作成（建物のみ）
        initializer.make_house_for_test(d=d, input_data_dir=s_folder, output_data_dir=s_folder)

        # 計算実行
        ds, dd = core.calc(input_data_dir=s_folder, output_data_dir=s_folder, show_detail_result=False, n_d_main=3)

        # 計算結果格納
        cls._ds = ds
        cls._dd = dd

    # 室空気温[℃]のテスト
    def test_room_temp(self):

        self.assertAlmostEqual(7.11115811172635, self._dd['rm0_t_r']['1989-1-1 12:00:00'])

    # 室内側表面熱流[W/m2]のテスト
    def test_heat_flow(self):

        self.assertAlmostEqual(16.5126256431597, self._dd['rm0_b0_qiall_s']['1989-1-1 12:00:00'])
        self.assertAlmostEqual(15.7826768347608, self._dd['rm0_b4_qiall_s']['1989-1-1 12:00:00'])

    # 表面温度[℃]のテスト
    def test_surface_temp(self):

        self.assertAlmostEqual(1.73471346702658, self._dd['rm0_b0_t_s']['1989-1-1 12:00:00'])
        self.assertAlmostEqual(1.8150078359981, self._dd['rm0_b4_t_s']['1989-1-1 12:00:00'])
