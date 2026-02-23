import os
import unittest
import numpy as np
import json

from heat_load_calc import sequence, weather, conditions, schedule, interval, recorder
from heat_load_calc.operation_mode import OperationMode
from heat_load_calc.interval import Interval
from heat_load_calc.tenum import EInterval


# 定常状態のテスト
class TestSteadyState(unittest.TestCase):
    """
    テストの目的
    定常状態を想定した壁体の貫流熱損失と透過日射熱取得が解析解と一致することを確認する。
    日射を考慮、夜間放射を無視。
    
    計算条件
    建物モデル  1m角立方体を上下に重ねた2室モデル
    部位構成    一般部位（8面）はせっこうボード12mm、南面窓は複層ガラスで構成される。
    　　　　　　内壁はボード壁
    すきま風    なし
    換気        1m3/h（全ての部位の隙間風量を同じ値とする）
    相当外気温度    0℃
    日射、夜間放射  法線面直達日射量700W/m2、水平面天空日射量200W/m2、地表面反射率0.1
    太陽位置    太陽高度30度、太陽方位角-15度
    内部発熱    100W（1室目）、50W（2室目）
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
        w = weather.Weather.create_constant(a_sun=np.radians(-15.0), h_sun=np.radians(30.0), i_dn=700.0, i_sky=200.0, r_n=0.0, theta_o=0.0, x_o=0.0)

        # 内部発熱：100.0 W, 50.0 W
        # 人体発湿を除く内部発湿： 0.0 kg/s
        # 局所換気量： 1/3600 m3/s
        # 在室人数： 0 人
        # 空調需要： 0.0
        scd = schedule.Schedule.create_constant(n_rm=2, q_gen=[100.0, 50.0], x_gen=[0.0, 0.0], v_mec_vent_local=[1.0/3600.0, 1.0/3600.0], n_hum=[0.0, 0.0], r_ac_demanc=[0.0, 0.0], t_ac_mode=[0, 0])

        itv = Interval(eitv=EInterval.M15)

        # pre_calc_parametersの構築
        sqc = sequence.Sequence(itv=itv, d=d, weather=w, scd=scd)

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

        q_srf_js_n = np.array([[22.5640843447614, 28.7776071971038, 27.1092772092918, 28.7776071971038, 34.5498206239126, 18.4455892778106, 24.6659904777119, 22.9976604898999, 24.6659904777119, 20.1735351503884, 401.848561318479, 343.04893859407, -6.47651020672211, 6.47651020672555]]).reshape(-1, 1)

        theta_ei_js_n = np.array([[90.9040129182149, 90.6859250357919, 90.6859250357919, 90.6859250357919, 105.737344414368, 78.4766505951595, 78.3120550702779, 78.3120550702779, 78.3120550702779, 78.3120550702779, 91.791646652984, 79.1465664971971, 90.6859250357919, 93.3634744488544]]).reshape(-1, 1)

        # 初期状態値の計算
        theta_r_is_n = np.array([[98.4453457337847, 84.1682535365713]]).reshape(-1, 1)
        c_n = conditions.Conditions(
            operation_mode_is_n=np.array([[OperationMode.STOP_CLOSE, OperationMode.STOP_CLOSE]]).reshape(-1, 1),
            theta_r_is_n=theta_r_is_n,
            theta_mrt_hum_is_n=np.array([[92.1275839485637, 81.4104763944663]]).reshape(-1, 1),
            x_r_is_n=np.array([[0.0, 0.0]]).reshape(-1, 1),
            theta_dsh_s_a_js_ms_n=q_srf_js_n * sqc.bs.phi_a1_js_ms / (1.0 - sqc.bs.r_js_ms),
            theta_dsh_s_t_js_ms_n=(
                    np.dot(sqc.bs.k_ei_js_js, theta_ei_js_n)
                    + sqc.bs.k_eo_js * sqc.bs.theta_o_eqv_js_nspls[:, 1].reshape(-1, 1)
                    + np.dot(sqc.bs.k_s_r_js_is, theta_r_is_n)
                ) * sqc.bs.phi_t1_js_ms / (1.0 - sqc.bs.r_js_ms),
            q_s_js_n=q_srf_js_n,
            theta_frt_is_n=np.array([[144.968310321296, 130.691218124083]]).reshape(-1, 1),
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

    # 内壁の熱流[W/m2]のテスト
    def test_case_01_heat_flow_inner_wall(self):

        self.assertAlmostEqual(self._c_n_pls.q_s_js_n[12][0], - self._c_n_pls.q_s_js_n[13][0])
        