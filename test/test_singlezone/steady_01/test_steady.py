import json
import os
import time
import unittest

from heat_load_calc import s3_space_initializer
from heat_load_calc.weather import weather
from heat_load_calc.core import core


# 定常状態のテスト
class TestSteadyState(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

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

        cls._ds = ds
        cls._dd = dd

    def test_case_01_room_temp(self):

        # 対流熱伝達率を放射熱伝達率のユニットテストより求め、室温を計算する必要がある
        # 対流熱伝達率の取得
        hc = self._dd['rm0_b0_hic_s']['1989-12-31 00:00:00']
        self.assertAlmostEqual(0.0 + 100/(6/(1/hc + 0.075 + 0.04)), self._dd['rm0_t_r']['1989-12-31 00:00:00'])

    def test_case_01_heat_flow(self):

        # 室内側表面熱流, W/m2 のテスト
        self.assertAlmostEqual(100/6, self._dd['rm0_b0_qic_s']['1989-12-31 00:00:00'])

    def test_case_01_surface_temp(self):

        # 表面温度, C のテスト
        self.assertAlmostEqual(0.0 + 100/6*(0.075 + 0.04), self._dd['rm0_b0_t_s']['1989-12-31 00:00:00'])


