import os
import unittest
import json
import numpy as np

from heat_load_calc import core2, schedule, weather, interval


# 定常状態のテスト
class TestSigleRoomWithGround(unittest.TestCase):
    """
    計算条件
    土間床２面のみを有する単室。
    外気温度は10℃一定。日射、夜間放射は考慮なし。
    内部発熱なし。

    """

    @classmethod
    def setUpClass(cls):

        print('\n testing single room with ground')

        # 計算用フォルダ
        s_folder = os.path.join(os.path.dirname(__file__), 'data')

        # 住宅計算条件JSONファイルの読み込み
        house_data_path = os.path.join(s_folder, "mid_data_house.json")
        with open(house_data_path, 'r', encoding='utf-8') as js:
            rd = json.load(js)

        file_path = os.path.abspath(os.path.join(s_folder, "weather.csv"))

        # 気象データ読み出し
        w = weather.Weather(
            a_sun_ns=np.zeros(8760*4, dtype=float),
            h_sun_ns=np.zeros(8760*4, dtype=float),
            i_dn_ns=np.zeros(8760*4, dtype=float),
            i_sky_ns=np.zeros(8760*4, dtype=float),
            r_n_ns=np.zeros(8760*4, dtype=float),
            theta_o_ns=np.full(8760*4, fill_value=10.0, dtype=float),
            x_o_ns=np.zeros(8760*4, dtype=float),
            itv=interval.Interval.M15
        )

        # スケジュールの設定
        scd = schedule.Schedule.get_schedule(rooms=rd['rooms'])

        # 計算実行
        dd_i, dd_a = core2.calc(rd=rd, oc=w, scd=scd, n_d_main=30, n_d_run_up=10, n_d_run_up_build=0)

        # 計算結果格納
        cls._dd_i = dd_i
        cls._dd_a = dd_a

    # 室空気温[℃]のテスト
    def test_case_01_room_temp(self):

        self.assertAlmostEqual(10.005290205703218, self._dd_i['rm0_t_r']['1989-1-31 0:00:00'])

    # 室内側表面熱流[W/m2]のテスト
    def test_case_01_heat_flow(self):

        self.assertAlmostEqual(-0.00043266833497230444, self._dd_i['rm0_b0_qiall_s']['1989-1-31 0:00:00'])
        self.assertAlmostEqual(-0.00043266833497230444, self._dd_i['rm0_b1_qiall_s']['1989-1-31 0:00:00'])

    # 表面温度[℃]のテスト
    def test_case_01_surface_temp(self):

        self.assertAlmostEqual(10.005432475852627, self._dd_i['rm0_b0_t_s']['1989-1-31 0:00:00'])
        self.assertAlmostEqual(10.005432475852627, self._dd_i['rm0_b1_t_s']['1989-1-31 0:00:00'])
