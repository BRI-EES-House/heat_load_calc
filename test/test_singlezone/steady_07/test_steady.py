import json
import numpy as np
import os
import shutil
import unittest

from heat_load_calc import initializer
from heat_load_calc.weather import weather
from heat_load_calc.core import core
from heat_load_calc.core import occupants
from heat_load_calc.external import psychrometrics


# 定常状態のテスト
@unittest.skip('TESTSKIP')
class TestSteadyState(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        print('\n testing single zone steady 07')

        # 計算用フォルダ
        s_folder = str(os.path.dirname(__file__)) + '/data'

        # 計算条件読込
        js = open(s_folder + '/input_residential.json', 'r', encoding='utf-8')
        d = json.load(js)

        # 中間データ作成（建物のみ）
        initializer.make_house_for_test(d=d, input_data_dir=s_folder, output_data_dir=s_folder)

        # 計算実行
        ds, dd = core.calc(input_data_dir=s_folder, output_data_dir=s_folder)

        # 計算結果格納
        cls._ds = ds
        cls._dd = dd

    # PMV[-]のテスト
    def test_pmv(self):

        theta_r = self._dd['rm0_t_r']['1989-12-31 00:00:00']
        theta_ot = self._dd['rm0_ot']['1989-12-31 00:00:00']
        clo = self._dd['rm0_clo']['1989-12-31 00:00:00']
        p_a = psychrometrics.get_p_v_r_is_n(np.array([self._dd['out_abs_humid']['1989-12-31 00:00:00']]))
        h_hum = self._dd['rm0_hc_hum']['1989-12-31 00:00:00'] + self._dd['rm0_hr_hum']['1989-12-31 00:00:00']

        # 確認用PMV
        # 室温の代わりに作用温度を使用
        pmv_confirm = occupants.get_pmv_is_n(
            np.array([theta_ot]),
            np.array([clo]),
            np.array([p_a]),
            np.array([h_hum]),
            np.array([theta_ot])
        )

        self.assertAlmostEqual(self._dd['rm0_pmv_target']['1989-12-31 00:00:00'], pmv_confirm[0][0])

        # 実現PMV
        pmv_practical = occupants.get_pmv_is_n(
            np.array([theta_r]),
            np.array([clo]),
            np.array([p_a]),
            np.array([h_hum]),
            np.array([theta_ot]))

        print(pmv_practical[0][0])
