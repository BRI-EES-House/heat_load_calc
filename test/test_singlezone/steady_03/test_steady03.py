import os
import unittest
import numpy as np
import json

from heat_load_calc import sequence, weather, conditions, schedule, interval
from heat_load_calc.operation_mode import OperationMode


# 定常状態のテスト
class TestSteadyState(unittest.TestCase):
    """
    計算条件
    屋根と床が合板12mm、壁が複層ガラスの1m角の立方体の単室モデル。
    外気温度一定。日射、夜間放射は考慮なし。
    内部発熱一定。
    
    Weather: 0
    Heat Generation: 100 W
    Ventilation: 0 m3/s
    sun trans. 0W
    """

    @classmethod
    def setUpClass(cls):

        print('\n testing single zone steady 03')

        # 計算用フォルダ
        s_folder = os.path.join(os.path.dirname(__file__), 'data')

        # 住宅計算条件JSONファイルの読み込み
        house_data_path = os.path.join(s_folder, "mid_data_house.json")
        with open(house_data_path, 'r', encoding='utf-8') as js:
            rd = json.load(js)

        # 外界条件
        # 全ての値は0.0で一定とする。日射・夜間放射はなし。
        w = weather.Weather(
            a_sun_ns=np.zeros(8760*4, dtype=float),
            h_sun_ns=np.zeros(8760*4, dtype=float),
            i_dn_ns=np.zeros(8760*4, dtype=float),
            i_sky_ns=np.zeros(8760*4, dtype=float),
            r_n_ns=np.zeros(8760*4, dtype=float),
            theta_o_ns=np.zeros(8760*4, dtype=float),
            x_o_ns=np.zeros(8760*4, dtype=float),
            itv=interval.Interval.M15
        )

        # ステップ n の室 i における内部発熱, W, [i, n] ( = 100.0 )
        # ステップ n の室 i における人体発湿を除く内部発湿, kg/s, [i, n] ( = 0.0 )
        # ステップ n の室 i における局所換気量, m3/s, [i, n] ( = 0.0 )
        # ステップ n の室 i における在室人数, [i, n] ( = 0 )
        # ステップ n の室 i における空調需要, [i, n] ( = 0.0 )
        scd = schedule.Schedule(
            q_gen_is_ns=np.full((1, 8760*4), 100.0, dtype=float),
            x_gen_is_ns=np.zeros((1, 8760*4), dtype=float),
            v_mec_vent_local_is_ns=np.zeros((1, 8760*4), dtype=float),
            n_hum_is_ns=np.zeros((1, 8760*4), dtype=float),
            r_ac_demand_is_ns=np.zeros((1, 8760*4), dtype=float),
            t_ac_mode_is_ns=np.zeros((1, 8760 * 4), dtype=float)
        )

        # pre_calc_parametersの構築
        sqc = sequence.Sequence(itv=interval.Interval.M15, rd=rd, weather=w, scd=scd)

        q_srf_js_n = np.array([[16.915925628103, 16.915925628103, 16.915925628103, 16.915925628103, 16.168148743794,
                                16.168148743794]]).reshape(-1, 1)

        theta_ei_js_n = np.array(
            [[3.637833468, 3.637833468, 3.637833468, 3.637833468, 3.637833468, 3.637833468]]).reshape(-1, 1)
        
        theta_rear_js_n = np.zeros(shape=(6,1), dtype=float)

        theta_dsh_s_a_js_ms_n, theta_dsh_s_t_js_ms_n = sqc.bs.get_wall_steady_state_status(q_srf_js_n=q_srf_js_n, theta_rear_js_n=theta_rear_js_n)

        # 初期状態値の計算
        c_n = conditions.Conditions(
            operation_mode_is_n=np.array([[OperationMode.STOP_CLOSE]]),
            theta_r_is_n=np.array([[7.284839149577920]]),
            theta_mrt_hum_is_n=np.array([[1.823144704]]),
            x_r_is_n=np.array([[0.0]]),
            theta_dsh_s_a_js_ms_n=theta_dsh_s_a_js_ms_n,
            theta_dsh_s_t_js_ms_n=theta_dsh_s_t_js_ms_n,
            q_s_js_n=q_srf_js_n,
            theta_frt_is_n=np.array([[7.284839149577920]]),
            x_frt_is_n=np.array([[0.0]]),
            theta_ei_js_n=theta_ei_js_n
        )

        # 計算実行
        c_n_pls = sqc.run_tick(n=-2, c_n=c_n, recorder=None)

        # 計算結果格納
        cls._c_n = c_n
        cls._c_n_pls = c_n_pls

    # 室空気温[℃]のテスト
    def test_case_01_room_temp(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_r_is_n, self._c_n_pls.theta_r_is_n)

    # 室内側表面熱流[W/m2]のテスト
    def test_case_01_heat_flow(self):

        np.testing.assert_array_almost_equal(self._c_n.q_s_js_n, self._c_n_pls.q_s_js_n)

    # 表面温度[℃]のテスト
    def test_case_01_surface_temp(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_mrt_hum_is_n, self._c_n_pls.theta_mrt_hum_is_n)

    # 等価室温[℃]のテスト
    def test_case_01_theta_ei(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_ei_js_n, self._c_n_pls.theta_ei_js_n)
