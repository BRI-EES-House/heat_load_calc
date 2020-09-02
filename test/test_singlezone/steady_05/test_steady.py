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

        # ファイル一時保管フォルダ
        s_folder_temporary = str(os.path.dirname(__file__)) + '/data_temporary'

        # ファイル一時保管フォルダ作成
        os.mkdir(s_folder_temporary)

        # 計算条件読込
        js = open(s_folder + '/input_residential.json', 'r', encoding='utf-8')
        d = json.load(js)

        # 気象データ作成
        weather.make_weather(region=d['common']['region'], output_data_dir=s_folder_temporary, csv_output=True)

        # 中間データ作成
        s3_space_initializer.make_house(d=d, input_data_dir=s_folder_temporary, output_data_dir=s_folder_temporary)

        # 使用するデータファイルの指定
        d_copy = {
            'weather.csv': False,
            'mid_data_house.json': True,
            'mid_data_theta_o_sol.csv': False,
            'mid_data_q_trs_sol.csv': False,
            'mid_data_local_vent.csv': False,
            'mid_data_occupants.csv': False,
            'mid_data_heat_generation.csv': False,
            'mid_data_moisture_generation.csv': False,
            'mid_data_ac_demand.csv': False
        }

        # 指定されたデータファイルのコピー
        for s_file in d_copy.keys():
            if d_copy[s_file]:
                shutil.copy(s_folder_temporary + '/' + s_file, s_folder + '/' + s_file)

        # ファイル一時保管フォルダ削除
        shutil.rmtree(s_folder_temporary)

        # 計算実行
        ds, dd = core.calc(input_data_dir=s_folder, output_data_dir=s_folder,
                           show_simple_result=True, show_detail_result=True)

        # 計算結果格納
        cls._ds = ds
        cls._dd = dd

    # 室空気温[℃]のテスト
    def test_room_temp(self):

        # 対流熱伝達率を放射熱伝達率のユニットテストより求め、室温を計算する必要がある
        # 対流熱伝達率の取得
        hc = self._dd['rm0_b0_hic_s']['1989-12-31 00:00:00']
        self.assertAlmostEqual(3.30840743877721, self._dd['rm0_t_r']['1989-12-31 00:00:00'])

    # 室内側表面熱流[W/m2]のテスト
    def test_heat_flow(self):

        self.assertAlmostEqual(15.3840945836677, self._dd['rm0_b1_qiall_s']['1989-12-31 00:00:00'])
        self.assertAlmostEqual(-31.1159054163324, self._dd['rm0_b2_qiall_s']['1989-12-31 00:00:00'])
        self.assertAlmostEqual(-29.7404113895651, self._dd['rm0_b4_qiall_s']['1989-12-31 00:00:00'])
        self.assertAlmostEqual(14.7040330548793, self._dd['rm0_b5_qiall_s']['1989-12-31 00:00:00'])

    # 表面温度[℃]のテスト
    def test_surface_temp(self):

        self.assertAlmostEqual(1.61615703314501, self._dd['rm0_b1_t_s']['1989-12-31 00:00:00'])
        self.assertAlmostEqual(6.73115703314502, self._dd['rm0_b2_t_s']['1989-12-31 00:00:00'])
        self.assertAlmostEqual(6.57985269020063, self._dd['rm0_b4_t_s']['1989-12-31 00:00:00'])
        self.assertAlmostEqual(1.69096380131174, self._dd['rm0_b5_t_s']['1989-12-31 00:00:00'])
