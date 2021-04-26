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
    屋根と床が合板12mm、壁が複層ガラスの1m角の立方体の単室モデル。
    外気温度一定。日射、夜間放射は考慮なし。
    内部発熱一定。

    """

    @classmethod
    def setUpClass(cls):

        print('\n testing single room with ground')

        # 計算用フォルダ
        s_folder = str(os.path.dirname(__file__)) + '/data'

        # 計算条件読込
        js = open(s_folder + '/input_residential.json', 'r', encoding='utf-8')
        d = json.load(js)

        # 中間データ作成（境界条件は再構築しない）
        initializer.make_house_for_test(d=d, input_data_dir=s_folder, output_data_dir=s_folder)
        # initializer.make_house(d=d, input_data_dir=s_folder, output_data_dir=s_folder)

        # 計算実行
        ds, dd = core.calc(input_data_dir=s_folder, output_data_dir=s_folder, show_detail_result=True)

        # 計算結果格納
        cls._ds = ds
        cls._dd = dd

    # 室空気温[℃]のテスト
    def test_case_01_room_temp(self):

        # self.assertAlmostEqual(7.28483914957795, self._dd['rm0_t_r']['1989-1-1 12:00:00'])
        pass

    # 室内側表面熱流[W/m2]のテスト
    def test_case_01_heat_flow(self):

        # self.assertAlmostEqual(16.9159256281029, self._dd['rm0_b0_qiall_s']['1989-1-1 12:00:00'])
        # self.assertAlmostEqual(16.1681487437944, self._dd['rm0_b4_qiall_s']['1989-1-1 12:00:00'])
        pass

    # 表面温度[℃]のテスト
    def test_case_01_surface_temp(self):

        # self.assertAlmostEqual(1.77708164821362, self._dd['rm0_b0_t_s']['1989-1-1 12:00:00'])
        # self.assertAlmostEqual(1.85933710553636, self._dd['rm0_b4_t_s']['1989-1-1 12:00:00'])
        pass
