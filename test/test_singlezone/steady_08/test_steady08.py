import os
import unittest
import numpy as np
import json

from heat_load_calc import sequence, weather, conditions, schedule
from heat_load_calc.operation_mode import OperationMode
from heat_load_calc.interval import Interval
from heat_load_calc.tenum import EInterval


# 定常状態のテスト
class TestSteadyState(unittest.TestCase):
    """
    テストの目的
    定常状態を想定した壁体の貫流熱損失が解析解と一致することを確認する。
    日射、夜間放射は無視。
    全ての部位の温度差係数は0.15とする。
    
    計算条件
    建物モデル  1m角の立方体単室モデル
    部位構成    全ての部位（6面）はせっこうボード12mmで構成される。
    すきま風    なし
    換気        なし
    外気温度    0℃（全ての部位の隣室温度差係数を0.15とする）
    日射、夜間放射  なし
    太陽位置    －
    内部発熱    100W
    """

    @classmethod
    def setUpClass(cls):

        print('\n testing single zone steady 08')

        # 計算用フォルダ
        s_folder = os.path.join(os.path.dirname(__file__), 'data')

        # 住宅計算条件JSONファイルの読み込み
        house_data_path = os.path.join(s_folder, "mid_data_house.json")
        with open(house_data_path, 'r', encoding='utf-8') as js:
            d = json.load(js)

        # 気象データ読み出し
        # 外界条件
        # 全ての値は0.0で一定とする。日射・夜間放射はなし。
        w = weather.Weather.create_constant(a_sun=0.0, h_sun=0.0, i_dn=0.0, i_sky=0.0, r_n=0.0, theta_o=0.0, x_o=0.0)

        # 内部発熱：100 W
        # 人体発湿を除く内部発湿： 0.0 kg/s
        # 局所換気量： 0.0 m3/s
        # 在室人数： 0 人
        # 空調需要： 0.0
        scd = schedule.Schedule.create_constant(n_rm=1, q_gen=100.0, x_gen=0.0, v_mec_vent_local=0.0, n_hum=0.0, r_ac_demanc=0.0, t_ac_mode=0)

        itv = Interval(eitv=EInterval.M15)

        # pre_calc_parametersの構築
        sqc = sequence.Sequence(itv=itv, d=d, weather=w, scd=scd)

        q_srf_js_n = np.array([[16.66666667, 16.66666667, 16.66666667, 16.66666667,
                                16.66666667, 16.66666667]]).reshape(-1, 1)

        theta_ei_js_n = np.array(
            [[33.17499851, 33.17499851, 33.17499851, 33.17499851, 33.17499851, 33.17499851]]).reshape(-1, 1)

        theta_r_is_n = np.array([[34.999999999999800]])

        # theta_rear_js = (np.dot(sqc.bs.k_ei_js_js, theta_ei_js_n) + sqc.bs.k_eo_js * sqc.bs.theta_o_eqv_js_nspls[:, 1].reshape(-1, 1)+ np.dot(sqc.bs.k_s_r_js_is, theta_r_is_n))
        theta_rear_js_n = np.full((6, 1), 35.0 * 0.85, dtype=float)

        theta_dsh_s_a_js_ms_n, theta_dsh_s_t_js_ms_n = sqc.bs.get_wall_steady_state_status(q_srf_js_n=q_srf_js_n, theta_rear_js_n=theta_rear_js_n)

        # 初期状態値の計算
        c_n = conditions.Conditions(
            operation_mode_is_n=np.array([[OperationMode.STOP_CLOSE]]),
            theta_r_is_n=theta_r_is_n,
            theta_mrt_hum_is_n=np.array([[31.66666667]]),
            x_r_is_n=np.array([[0.0]]),
            theta_dsh_s_a_js_ms_n=theta_dsh_s_a_js_ms_n,
            theta_dsh_s_t_js_ms_n=theta_dsh_s_t_js_ms_n,
            q_s_js_n=q_srf_js_n,
            theta_frt_is_n=np.array([[34.999999999999900]]),
            x_frt_is_n=np.array([[0.0]]),
            theta_ei_js_n=theta_ei_js_n
        )

        # 計算実行
        c_n_pls = sqc.run_tick(n=-2, c_n=c_n, recorder=None)

        # 計算結果格納
        cls._c_n = c_n
        cls._c_n_pls = c_n_pls

    # 室空気温[℃]のテスト
    def test_case_08_room_temp(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_r_is_n, self._c_n_pls.theta_r_is_n)

    # 室内側表面熱流[W/m2]のテスト
    def test_case_08_heat_flow(self):

        np.testing.assert_array_almost_equal(self._c_n.q_s_js_n, self._c_n_pls.q_s_js_n)

    # 表面温度[℃]のテスト
    def test_case_08_surface_temp(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_mrt_hum_is_n, self._c_n_pls.theta_mrt_hum_is_n)

    # 等価室温[℃]のテスト
    def test_case_08_theta_ei(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_ei_js_n, self._c_n_pls.theta_ei_js_n)

    # 表面温度絶対値テスト
    def test_case08_hum_mrt_abs(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_mrt_hum_is_n, self._c_n_pls.theta_mrt_hum_is_n)
