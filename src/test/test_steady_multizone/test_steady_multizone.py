import os
import unittest
import numpy as np
import json

from heat_load_calc import sequence, pre_calc_parameters, weather, conditions, operation_mode, schedule, \
    interval, recorder


# 定常状態のテスト
class TestSteadyState(unittest.TestCase):
    """
    計算条件
    屋根と床が合板12mm、壁が複層ガラスの1m角の立方体の単室モデル。
    外気温度一定。日射、夜間放射は考慮なし。
    内部発熱一定。

    """

    @classmethod
    def setUpClass(cls):

        print('\n testing 2 zone steady 01')

        # 計算用フォルダ
        s_folder = os.path.join(os.path.dirname(__file__), 'data')

        # 住宅計算条件JSONファイルの読み込み
        house_data_path = os.path.join(s_folder, "input.json")
        with open(house_data_path, 'r', encoding='utf-8') as js:
            rd = json.load(js)

        # 外界条件
        # 全ての値は0.0で一定とする。日射・夜間放射はなし。
        w = weather.Weather(
            a_sun_ns=np.zeros(8760 * 4, dtype=float),
            h_sun_ns=np.zeros(8760 * 4, dtype=float),
            i_dn_ns=np.zeros(8760 * 4, dtype=float),
            i_sky_ns=np.zeros(8760 * 4, dtype=float),
            r_n_ns=np.zeros(8760 * 4, dtype=float),
            theta_o_ns=np.zeros(8760 * 4, dtype=float),
            x_o_ns=np.zeros(8760 * 4, dtype=float),
            itv=interval.Interval.M15
        )

        # ステップ n の室 i における内部発熱, W, [i, n] ( = 100.0 )
        # ステップ n の室 i における人体発湿を除く内部発湿, kg/s, [i, n] ( = 0.0 )
        # ステップ n の室 i における局所換気量, m3/s, [i, n] ( = 0.0 )
        # ステップ n の室 i における在室人数, [i, n] ( = 0 )
        # ステップ n の室 i における空調需要, [i, n] ( = 0.0 )
        scd = schedule.Schedule(
            q_gen_is_ns=np.concatenate(
                [np.full(8760 * 4, 1000.0, dtype=float), np.full(8760 * 4, 100.0, dtype=float)]).flatten().reshape(2, -1),
            x_gen_is_ns=np.zeros((2, 8760 * 4), dtype=float),
            v_mec_vent_local_is_ns=np.zeros((2, 8760 * 4), dtype=float),
            n_hum_is_ns=np.zeros((2, 8760 * 4), dtype=float),
            ac_demand_is_ns=np.zeros((2, 8760 * 4), dtype=float),
            ac_setting_is_ns=np.zeros((2, 8760 * 4), dtype=float)
        )

        # pre_calc_parametersの構築
        ss, ppg = pre_calc_parameters.make_pre_calc_parameters(itv=interval.Interval.M15, rd=rd, weather=w, scd=scd)

        result = recorder.Recorder(
            n_step_main=8760 * 4,
            id_rm_is=list(ss.rms.id_rm_is.flatten()),
            id_bdry_js=list(ss.bs.id_js.flatten())
        )

        result.pre_recording(ss=ss, weather=ss.weather, scd=ss.scd)

        q_srf_js_n = np.array([[
            3.615155079132,
            3.601529520124,
            3.601529520124,
            3.218198428266,
            3.738979305479,
            1.509356057488,
            1.510822067846,
            1.510822067846,
            1.426055294333,
            1.518645098305,
            47.479197099042,
            19.866797252780,
            15.010461644437,
            - 15.010461644437
        ]]).reshape(-1, 1)

        theta_ei_js_n = np.array([[
            10.9196525,
            10.8516512,
            10.8516512,
            10.1033362,
            11.3248286,
            4.5590419,
            4.5522087,
            4.5522087,
            4.4770130,
            4.5997568,
            10.8879303,
            4.5558543,
            10.8516512,
            4.5522087
        ]]).reshape(-1, 1)

        # 初期状態値の計算
        theta_r_is_n = np.array([[13.403464558874200, 4.808632169196720]]).reshape(-1, 1)
        c_n = conditions.Conditions(
            operation_mode_is_n=np.array(
                [[operation_mode.OperationMode.STOP_CLOSE, operation_mode.OperationMode.STOP_CLOSE]]).reshape(-1, 1),
            theta_r_is_n=theta_r_is_n,
            theta_mrt_hum_is_n=np.array([[9.689970497, 4.391663789]]).reshape(-1, 1),
            x_r_is_n=np.array([[0.0, 0.0]]).reshape(-1, 1),
            theta_dsh_s_a_js_ms_n=q_srf_js_n * ss.bs.phi_a1_js_ms / (1.0 - ss.bs.r_js_ms),
            theta_dsh_s_t_js_ms_n=(
                    np.dot(ss.bs.k_ei_js_js, theta_ei_js_n)
                    + ss.bs.k_eo_js * ss.theta_o_eqv_js_ns[:, 1].reshape(-1, 1)
                    + np.dot(ss.bs.k_s_r_js_is, theta_r_is_n)
                ) * ss.bs.phi_t1_js_ms / (1.0 - ss.bs.r_js_ms),
            q_s_js_n=q_srf_js_n,
            theta_frt_is_n=theta_r_is_n,
            x_frt_is_n=np.array([[0.0, 0.0]]).reshape(-1, 1),
            theta_ei_js_n=theta_ei_js_n
        )

        c_n_init = c_n
        c_n = sequence.run_tick(n=0, delta_t=900.0, ss=ss, c_n=c_n, recorder=result)

        result.post_recording(ss=ss, rms=ss.rms)

        # 計算結果格納
        cls._c_n = c_n_init
        cls._c_n_pls = c_n
        cls._pp = ss
        cls._dd_i, cls._dd_a = result.export_pd()

    # 室空気温[℃]のテスト
    def test_case_01_room_temp(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_r_is_n, self._c_n_pls.theta_r_is_n)

    # 室内側表面熱流[W/m2]のテスト
    def test_case_01_heat_flow(self):

        np.testing.assert_array_almost_equal(self._c_n.q_s_js_n, self._c_n_pls.q_s_js_n)

    # 人体のMRT[℃]のテスト
    def test_case_01_theta_mrt_hum(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_mrt_hum_is_n, self._c_n_pls.theta_mrt_hum_is_n)

    # 等価室温[℃]のテスト
    def test_case_01_theta_ei(self):

        np.testing.assert_array_almost_equal(self._c_n.theta_ei_js_n, self._c_n_pls.theta_ei_js_n)

    # 表面温度[℃]のテスト
    def test_case_01_theta_s(self):

        # テスト時刻を指定
        date_now = '1990-01-01 0:00:00'

        n_bndrs = self._pp.bs.n_b

        # 0番目の境界（外壁）
        for i in range(n_bndrs):
            bdr_name = 'b' + str(i) + '_'
            theta_s = self._dd_i[bdr_name + 't_s'][date_now]
            theta_rear = self._dd_i[bdr_name + 't_b'][date_now]
            f_cvl = self._dd_i[bdr_name + 'f_cvl'][date_now]
            q_all = self._dd_i[bdr_name + 'qiall_s'][date_now]
            phi_a_0 = self._pp.bs.phi_a0_js[i][0]
            phi_t_0 = self._pp.bs.phi_t0_js[i][0]
            self.assertAlmostEqual(theta_s, phi_a_0 * q_all + phi_t_0 * theta_rear + f_cvl)
