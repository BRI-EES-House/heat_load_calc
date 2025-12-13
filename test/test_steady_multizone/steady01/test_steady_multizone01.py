import os
import unittest
import numpy as np
import json

from heat_load_calc import sequence, weather, conditions, schedule, interval, recorder
from heat_load_calc.operation_mode import OperationMode


# 定常状態のテスト
class TestSteadyState(unittest.TestCase):
    """
    テストの目的
    定常状態を想定した壁体の貫流熱損失と透過日射熱取得が解析解と一致することを確認する。
    日射、夜間放射を無視。
    
    計算条件
    建物モデル  1m角立方体を上下に重ねた2室モデル
    部位構成    一般部位（8面）はせっこうボード12mm、南面窓は複層ガラスで構成される。
    　　　　　　内壁はボード壁
    すきま風    なし
    換気        なし
    相当外気温度    0℃
    日射、夜間放射  なし
    太陽位置    なし
    内部発熱    1F:100W、2F:50W
    """

    @classmethod
    def setUpClass(cls):

        print('\n testing 2 zone steady 01')

        # 計算用フォルダ
        s_folder = os.path.join(os.path.dirname(__file__), 'data')

        # 住宅計算条件JSONファイルの読み込み
        house_data_path = os.path.join(s_folder, "input.json")
        with open(house_data_path, 'r', encoding='utf-8') as js:
            d = json.load(js)

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
                [np.full(8760 * 4, 100.0, dtype=float), np.full(8760 * 4, 50.0, dtype=float)]).flatten().reshape(2, -1),
            x_gen_is_ns=np.zeros((2, 8760 * 4), dtype=float),
            v_mec_vent_local_is_ns=np.zeros((2, 8760 * 4), dtype=float),
            n_hum_is_ns=np.zeros((2, 8760 * 4), dtype=float),
            r_ac_demand_is_ns=np.zeros((2, 8760 * 4), dtype=float),
            t_ac_mode_is_ns=np.zeros((2, 8760 * 4), dtype=float)
        )

        # pre_calc_parametersの構築
        sqc = sequence.Sequence(itv=interval.Interval.M15, d=d, weather=w, scd=scd)

        result = recorder.Recorder(
            n_step_main=8760 * 4,
            id_rm_is=list(sqc.rms.id_r_is.flatten()),
            id_bs_js=list(sqc.bs.id_js.flatten())
        )

        result.pre_recording(
            weather=sqc.weather,
            scd=sqc.scd,
            bs=sqc.bs,
            q_sol_frt_is_ns=sqc.q_sol_frt_is_ns,
            q_s_sol_js_ns=sqc.q_s_sol_js_ns,
            q_trs_sol_is_ns=sqc.q_trs_sol_is_ns
        )

        q_srf_js_n = np.array([[7.76358335006654, 7.74050433879964, 7.74050433879964, 7.74050433879964, 7.74050433879964, 5.80030516395384, 5.79401025839501, 5.79401025839501, 5.79401025839501, 5.79401025839501, 101.973705196886, 76.1862895226058, 14.1693383740909, -14.1693383740943

        ]]).reshape(-1, 1)

        theta_ei_js_n = np.array([[23.4262422676557, 23.2949714656255, 23.2949714656255, 23.2949714656255, 23.2949714656255, 17.5021440319776, 17.4370167282659, 17.4370167282659, 17.4370167282659, 17.4370167282659, 23.4262422676557, 17.5021440319776, 23.2949714656255, 17.4370167282659

        ]]).reshape(-1, 1)

        # 初期状態値の計算
        theta_r_is_n = np.array([[27.9654986265184, 19.7542025471838

]]).reshape(-1, 1)
        c_n = conditions.Conditions(
            operation_mode_is_n=np.array([[OperationMode.STOP_CLOSE, OperationMode.STOP_CLOSE]]).reshape(-1, 1),
            theta_r_is_n=theta_r_is_n,
            theta_mrt_hum_is_n=np.array([[21.6703591329716, 17.3286299196982

]]).reshape(-1, 1),
            x_r_is_n=np.array([[0.0, 0.0]]).reshape(-1, 1),
            theta_dsh_s_a_js_ms_n=q_srf_js_n * sqc.bs.phi_a1_js_ms / (1.0 - sqc.bs.r_js_ms),
            theta_dsh_s_t_js_ms_n=(
                    np.dot(sqc.bs.k_ei_js_js, theta_ei_js_n)
                    + sqc.bs.k_eo_js * sqc.bs.theta_o_eqv_js_nspls[:, 1].reshape(-1, 1)
                    + np.dot(sqc.bs.k_s_r_js_is, theta_r_is_n)
                ) * sqc.bs.phi_t1_js_ms / (1.0 - sqc.bs.r_js_ms),
            q_s_js_n=q_srf_js_n,
            theta_frt_is_n=theta_r_is_n,
            x_frt_is_n=np.array([[0.0, 0.0]]).reshape(-1, 1),
            theta_ei_js_n=theta_ei_js_n
        )

        c_n_init = c_n
        c_n = sqc.run_tick(n=0, c_n=c_n, recorder=result)

        result.post_recording(rms=sqc.rms, bs=sqc.bs, f_mrt_is_js=sqc.f_mrt_is_js, es=sqc.es)

        # 計算結果格納
        cls._c_n = c_n_init
        cls._c_n_pls = c_n
        cls._dd_i, cls._dd_a = result.export_pd()
        cls._sqc = sqc

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

        n_bndrs = self._sqc.bs.n_b

        # 0番目の境界（外壁）
        for i in range(n_bndrs):
            bdr_name = 'b' + str(i) + '_'
            theta_s = self._dd_i[bdr_name + 't_s'][date_now]
            theta_rear = self._dd_i[bdr_name + 't_b'][date_now]
            f_cvl = self._dd_i[bdr_name + 'f_cvl'][date_now]
            q_all = self._dd_i[bdr_name + 'qiall_s'][date_now]
            phi_a_0 = self._sqc.bs.phi_a0_js[i][0]
            phi_t_0 = self._sqc.bs.phi_t0_js[i][0]
            self.assertAlmostEqual(theta_s, phi_a_0 * q_all + phi_t_0 * theta_rear + f_cvl)
