import json
import os
import unittest

from heat_load_calc import s3_space_initializer
from heat_load_calc.weather import weather
from heat_load_calc.core import core


# 定常状態のテスト
class TestSteadyState(unittest.TestCase):

    # @unittest.skip('時間がかかるのでskip')
    def test_case_01(self):

        s_folder = 'data'

        bln_make_weather = False

        bln_space_initialize = False

        js = open(str(os.path.dirname(__file__)) + '/' + s_folder + '/input_residential.json', 'r', encoding='utf-8')

        d = json.load(js)

        if bln_make_weather:
            weather.make_weather(region=d['common']['region'], output_data_dir=s_folder, csv_output=True)

        if bln_space_initialize:
            s3_space_initializer.make_house(d=d, input_data_dir=s_folder, output_data_dir=s_folder)

        data_dir = str(os.path.dirname(__file__)) + '/' + s_folder

        ds, dd = core.calc(input_data_dir=data_dir, output_data_dir=data_dir,
                           show_simple_result=True, show_detail_result=True)

        # 対流熱伝達率の取得
        hc = dd['rm0_b0_hic_s']['1989-12-31 00:00:00']

        # 室温のテスト
        self.assertAlmostEqual(0.0 + 100/(6/(1/hc + 1/4.65 - 0.11)), dd['rm0_t_r']['1989-12-31 00:00:00'])

        # 表面温度のテスト
        self.assertAlmostEqual(0.0 + 100/6*(1/4.65 - 0.11), dd['rm0_b0_t_s']['1989-12-31 00:00:00'])

        # 熱流のテスト
        self.assertAlmostEqual(100/6, dd['rm0_b0_qic_s']['1989-12-31 00:00:00'])


