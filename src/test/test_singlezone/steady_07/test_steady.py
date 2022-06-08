import os
import unittest
import numpy as np
import pandas as pd
import csv
import json

from heat_load_calc import core, pmv
from heat_load_calc.external import psychrometrics


# 定常状態のテスト
@unittest.skip('TESTSKIP')
class TestSteadyState(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        print('\n testing single zone steady 07')

        # 計算用フォルダ
        s_folder = os.path.join(os.path.dirname(__file__), 'data')

        # 住宅計算条件JSONファイルの読み込み
        house_data_path = os.path.join(s_folder, "mid_data_house.json")
        with open(house_data_path, 'r', encoding='utf-8') as js:
            rd = json.load(js)

        # 気象データ読み出し
        import_weather_path = os.path.join(s_folder, "weather.csv")
        dd_weather = pd.read_csv(import_weather_path)

        # ステップnの室iにおける局所換気量, m3/s, [i, 8760*4]
        mid_data_local_vent_path = os.path.join(s_folder, 'mid_data_local_vent.csv')
        with open(mid_data_local_vent_path, 'r') as f:
            r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            v_mec_vent_local_is_ns = np.array([row for row in r]).T

        # ステップnの室iにおける内部発熱, W, [8760*4]
        mid_data_heat_generation_path = os.path.join(s_folder, 'mid_data_heat_generation.csv')
        with open(mid_data_heat_generation_path, 'r') as f:
            r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            q_gen_is_ns = np.array([row for row in r]).T

        # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [8760*4]
        mid_data_moisture_generation_path = os.path.join(s_folder, 'mid_data_moisture_generation.csv')
        with open(mid_data_moisture_generation_path, 'r') as f:
            r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            x_gen_is_ns = np.array([row for row in r]).T

        # ステップnの室iにおける在室人数, [8760*4]
        mid_data_occupants_path = os.path.join(s_folder, 'mid_data_occupants.csv')
        with open(mid_data_occupants_path, 'r') as f:
            r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            n_hum_is_ns = np.array([row for row in r]).T

        # ステップnの室iにおける空調需要, [8760*4]
        mid_data_ac_demand_path = os.path.join(s_folder, 'mid_data_ac_demand.csv')
        with open(mid_data_ac_demand_path, 'r') as f:
            r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            ac_demand_is_ns = np.array([row for row in r]).T

        ac_operation = {
            'ac_demand_is_ns': ac_demand_is_ns
        }

        # 計算実行
        ds, dd = core.calc(
            rd=rd,
            q_gen_is_ns=q_gen_is_ns,
            x_gen_is_ns=x_gen_is_ns,
            v_mec_vent_local_is_ns=v_mec_vent_local_is_ns,
            n_hum_is_ns=n_hum_is_ns,
            ac_demand_is_ns=ac_demand_is_ns,
            ac_operation=ac_operation,
            weather_dataframe=dd_weather
        )

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

        clo_is_n = np.array([clo])

        i_cl_is_n = pmv._get_i_cl_is_n(clo_is_n=clo_is_n)
        # 室 i の在室者のMet値, [i, 1]
        met_is = np.full_like(clo_is_n, fill_value=1.0, dtype=float)

        # 室 i の在室者の代謝量（人体内部発熱量）, W/m2
        m_is = pmv._get_m_is(met_is=met_is)

        # ステップnにおける室iの在室者の着衣面積率, [i, 1]
        f_cl_is_n = pmv._get_f_cl_is_n(i_cl_is_n=i_cl_is_n)

        pmv_confirm = pmv._get_pmv(
            theta_r_is_n=np.array([theta_ot]),
            p_a_is_n=np.array([p_a]),
            h_hum_is_n=np.array([h_hum]),
            theta_ot_is_n=np.array([theta_ot]),
            i_cl_is_n=i_cl_is_n,
            f_cl_is_n=f_cl_is_n,
            met_is=met_is
        )

        self.assertAlmostEqual(self._dd['rm0_pmv_target']['1989-12-31 00:00:00'], pmv_confirm[0][0])

        # 実現PMV
        pmv_practical = pmv._get_pmv(
            theta_r_is_n=np.array([theta_r]),
            p_a_is_n=np.array([p_a]),
            h_hum_is_n=np.array([h_hum]),
            theta_ot_is_n=np.array([theta_ot]),
            i_cl_is_n=i_cl_is_n,
            f_cl_is_n=f_cl_is_n,
            met_is=met_is
        )

        print(pmv_practical[0][0])
