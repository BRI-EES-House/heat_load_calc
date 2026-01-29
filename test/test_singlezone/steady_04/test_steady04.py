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
    壁体からの合計熱損失と換気熱損失の和が内部発熱と一致することを確認する。
    
    計算条件
    建物モデル  1m角の立方体単室モデル
    部位構成    垂直外皮は熱貫流率4.65W/(m2・K)の窓、床・屋根はせっこうボード12mmで構成される。
    すきま風    なし
    換気        1m3/h=0.000278m3/s（換気スケジュールで与える）
    外気温度    0.0℃
    日射、夜間放射  なし
    内部発熱    100W（対流成分のみ）
    """

    @classmethod
    def setUpClass(cls):

        print('\n testing single zone steady 04')

        # 計算用フォルダ
        s_folder = os.path.join(os.path.dirname(__file__), 'data')

        # 住宅計算条件JSONファイルの読み込み
        house_data_path = os.path.join(s_folder, "mid_data_house.json")
        with open(house_data_path, 'r', encoding='utf-8') as js:
            d = json.load(js)

        # 外界条件
        # 全ての値は0.0で一定とする。日射・夜間放射はなし。
        w = weather.Weather.create_constant(a_sun=0.0, h_sun=0.0, i_dn=0.0, i_sky=0.0, r_n=0.0, theta_o=0.0, x_o=0.0)

        # 内部発熱：100 W
        # 人体発湿を除く内部発湿： 0.0 kg/s
        # 局所換気量： 0.000278 m3/s
        # 在室人数： 0 人
        # 空調需要： 0.0
        scd = schedule.Schedule.create_constant(n_rm=1, q_gen=100.0, x_gen=0.0, v_mec_vent_local=0.000278, n_hum=0.0, r_ac_demanc=0.0, t_ac_mode=0)

        itv = Interval(eitv=EInterval.M15)

        # pre_calc_parametersの構築
        sqc = sequence.Sequence(itv=itv, d=d, weather=w, scd=scd)

        # ステップnにおける表面熱流[W/m2]の設定
        q_srf_js_n = np.array([[16.51262564317, 16.51262564317, 16.51262564317, 16.51262564317,
            15.78267683477, 15.78267683477]]).reshape(-1, 1)

        # ステップnにおける等価室温[℃]の設定
        theta_ei_js_n = np.array(
            [[3.551102289, 3.551102289, 3.551102289, 3.551102289, 3.551102289, 3.551102289]]).reshape(-1, 1)
        
        theta_rear_js_n = np.zeros(shape=(6,1), dtype=float)

        theta_dsh_s_a_js_ms_n, theta_dsh_s_t_js_ms_n = sqc.bs.get_wall_steady_state_status(q_srf_js_n=q_srf_js_n, theta_rear_js_n=theta_rear_js_n)

        # 初期状態値の計算
        c_n = conditions.Conditions(
            operation_mode_is_n=np.array([[OperationMode.STOP_CLOSE]]),
            theta_r_is_n=np.array([[7.1111581117273]]),
            theta_mrt_hum_is_n=np.array([[1.779678314]]),
            x_r_is_n=np.array([[0.0]]),
            theta_dsh_s_a_js_ms_n=theta_dsh_s_a_js_ms_n,
            theta_dsh_s_t_js_ms_n=theta_dsh_s_t_js_ms_n,
            q_s_js_n=q_srf_js_n,
            theta_frt_is_n=np.array([[7.1111581117273]]),
            x_frt_is_n=np.array([[0.0]]),
            theta_ei_js_n=theta_ei_js_n
        )

        # 計算実行
        c_n_pls = sqc.run_tick(n=-2, c_n=c_n, recorder=None)

        # 計算結果格納
        cls._c_n = c_n
        cls._c_n_pls = c_n_pls

    # 室空気温[℃]のテスト
    def test_room_temp(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_r_is_n, self._c_n_pls.theta_r_is_n)

    # 室内側表面熱流[W/m2]のテスト
    def test_heat_flow(self):

        np.testing.assert_array_almost_equal(self._c_n.q_s_js_n, self._c_n_pls.q_s_js_n)

    # 表面温度[℃]のテスト
    def test_surface_temp(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_mrt_hum_is_n, self._c_n_pls.theta_mrt_hum_is_n)

    # 等価室温[℃]のテスト
    def test_case_01_theta_ei(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_ei_js_n, self._c_n_pls.theta_ei_js_n)
