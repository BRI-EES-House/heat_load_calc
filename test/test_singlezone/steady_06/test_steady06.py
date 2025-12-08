import os
import unittest
import numpy as np
import json

from heat_load_calc import sequence, weather, conditions, schedule, interval
from heat_load_calc.operation_mode import OperationMode


# 定常状態のテスト
class TestSteadyState(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        テストの目的
        定常状態を想定した壁体の貫流熱損失が解析解と一致することを確認する。
        日射を考慮（太陽位置、法線面直達日射、水平面天空日射を与える）して相当外気温度を計算する。
        
        計算条件
        建物モデル  1m角の立方体単室モデル
        部位構成    全ての部位（6面）はせっこうボード12mmで構成される。
        すきま風    なし
        換気        なし
        外気温度    それぞれの部位の入射日射量より計算
        日射、夜間放射  法線面直達日射量:700W/m2、水平面天空日射量:200W/m2、地面反射率は0.1
        太陽位置    太陽高度:30度、太陽方位角:0度
        内部発熱    なし
        """

        print('\n testing single zone steady 06')

        # 計算用フォルダ
        s_folder = os.path.join(os.path.dirname(__file__), 'data')

        # 住宅計算条件JSONファイルの読み込み
        house_data_path = os.path.join(s_folder, "mid_data_house.json")
        with open(house_data_path, 'r', encoding='utf-8') as js:
            rd = json.load(js)

        # 気象データ読み出し
        # 太陽高度は30度、太陽方位角は0度、それ以外は0とする。
        # 法線面直達日射量は700W/m2、水平面天空日射量は200W/m2、それ以外は0とする。
        w = weather.Weather(
            a_sun_ns=np.zeros(8760*4, dtype=float),
            h_sun_ns=np.full(8760*4, fill_value=np.radians(30.0), dtype=float),
            i_dn_ns=np.full(8760*4, fill_value=700.0, dtype=float),
            i_sky_ns=np.full(8760*4, fill_value=200.0, dtype=float),
            r_n_ns=np.zeros(8760*4, dtype=float),
            theta_o_ns=np.zeros(8760*4, dtype=float),
            x_o_ns=np.zeros(8760*4, dtype=float),
            itv=interval.Interval.M15
        )

        # ステップ n の室 i における内部発熱, W, [i, n] ( = 0.0 )
        # ステップ n の室 i における人体発湿を除く内部発湿, kg/s, [i, n] ( = 0.0 )
        # ステップ n の室 i における局所換気量, m3/s, [i, n] ( = 0.0 )
        # ステップ n の室 i における在室人数, [i, n] ( = 0 )
        # ステップ n の室 i における空調需要, [i, n] ( = 0.0 )
        scd = schedule.Schedule(
            q_gen_is_ns=np.zeros((1, 8760*4), dtype=float),
            x_gen_is_ns=np.zeros((1, 8760*4), dtype=float),
            v_mec_vent_local_is_ns=np.zeros((1, 8760*4), dtype=float),
            n_hum_is_ns=np.zeros((1, 8760*4), dtype=float),
            r_ac_demand_is_ns=np.zeros((1, 8760*4), dtype=float),
            t_ac_mode_is_ns=np.zeros((1, 8760*4), dtype=float)
        )

        # pre_calc_parametersの構築
        sqc = sequence.Sequence(
            itv=interval.Interval.M15, rd=rd, weather=w, scd=scd
        )

        # ステップnにおける表面熱流[W/m2]の設定
        q_srf_js_n = np.array([[-63.5517372028421, 22.6659029961419, 22.6659029961419, 22.6659029961419,
            32.9770141072531, -37.4229858927469]]).reshape(-1, 1)

        theta_ei_js_n = np.array(
        #    [[2.748585309, 2.748585309, 2.748585309, 2.748585309, 8.248585309, 2.748585309]]).reshape(-1, 1)
            [[9.179828174, 9.179828174, 9.179828174, 9.179828174, 9.179828174, 9.179828174]]).reshape(-1, 1)
        
        # theta_rear_js_n = np.zeros(shape=(6,1), dtype=float)

        # theta_dsh_s_a_js_ms_n, theta_dsh_s_t_js_ms_n = sqc.bs.get_wall_steady_state_status(q_srf_js_n=q_srf_js_n, theta_rear_js_n=theta_rear_js_n)

        # 初期状態値の計算
        c_n = conditions.Conditions(
            operation_mode_is_n=np.array([[OperationMode.STOP_CLOSE]]),
            theta_r_is_n=np.array([[9.17982817413]]),
            theta_mrt_hum_is_n=np.array([[7.946487847]]),
            x_r_is_n=np.array([[0.0]]),
            # theta_dsh_s_a_js_ms_n=theta_dsh_s_a_js_ms_n,
            # theta_dsh_s_t_js_ms_n=theta_dsh_s_t_js_ms_n,
            theta_dsh_s_a_js_ms_n=q_srf_js_n * sqc.bs.phi_a1_js_ms / (1.0 - sqc.bs.r_js_ms),
            theta_dsh_s_t_js_ms_n=(np.dot(sqc.bs.k_ei_js_js, theta_ei_js_n) + sqc.bs.k_eo_js * sqc.bs.theta_o_eqv_js_nspls[:, 1].reshape(-1, 1)) * sqc.bs.phi_t1_js_ms / (1.0 - sqc.bs.r_js_ms),
            q_s_js_n=q_srf_js_n,
            theta_frt_is_n=np.array([[9.17982817413]]),
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
