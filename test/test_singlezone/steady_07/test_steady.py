import json
import numpy as np
import os
import shutil
import unittest

from heat_load_calc import s3_space_initializer
from heat_load_calc.weather import weather
from heat_load_calc.core import core
from heat_load_calc.core import occupants
from heat_load_calc.external import psychrometrics


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

    # PMV[-]のテスト
    def test_pmv(self):

        theta_r = self._dd['rm0_t_r']['1989-12-31 00:00:00']
        clo = self._dd['rm0_clo']['1989-12-31 00:00:00']
        p_a = psychrometrics.get_p_v_r_is_n(np.array([self._dd['out_abs_humid']['1989-12-31 00:00:00']]))
        h_hum = self._dd['rm0_hc_hum']['1989-12-31 00:00:00'] + self._dd['rm0_hr_hum']['1989-12-31 00:00:00']
        theta_ot = self._dd['rm0_ot']['1989-12-31 00:00:00']
        pmv = occupants.get_pmv_is_n(np.array([theta_r]), clo, p_a, np.array([h_hum]), np.array([theta_ot]))

        self.assertAlmostEqual(self._dd['rm0_pmv_target']['1989-12-31 00:00:00'], pmv[0])
