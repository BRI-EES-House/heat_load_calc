import os
import unittest
import numpy as np

from heat_load_calc.core import pre_calc_parameters
from heat_load_calc.core import conditions
from heat_load_calc.core import sequence
from heat_load_calc.core import operation_mode


# 定常状態のテスト
class TestSteadyState(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        屋根と床が合板12mm、壁が複層ガラスの1m角の立方体の単室モデル。
        相当外気温度が屋根と南壁10℃、他は0℃。
        内部発熱なし。
        """

        print('\n testing single zone steady 05')

        # 計算用フォルダ
        s_folder = str(os.path.dirname(__file__)) + '/data'

        # pre_calc_parametersの構築
        ss, ppg = pre_calc_parameters.make_pre_calc_parameters(delta_t=900.0, data_directory=s_folder, theta_o_sol_calculate=False)

        q_srf_js_n = np.array([[15.384094583670, 15.384094583670, -31.115905416330, 15.384094583670,
            14.704033054882, -29.740411389563]]).reshape(-1, 1)

        theta_ei_js_n = np.array(
            [[3.308407437, 3.308407437, 3.308407437, 3.308407437, 3.308407437, 3.308407437]]).reshape(-1, 1)

        # 初期状態値の計算
        c_n = conditions.Conditions(
            operation_mode_is_n=np.array([[operation_mode.OperationMode.STOP_CLOSE]]),
            theta_r_is_n=np.array([[3.3084074373484]]),
            theta_mrt_hum_is_n=np.array([[2.758476601]]),
            x_r_is_n=np.array([[0.0]]),
            theta_dsh_s_a_js_ms_n=q_srf_js_n * ss.phi_a1_js_ms / (1.0 - ss.r_js_ms),
            theta_dsh_s_t_js_ms_n=(np.dot(ss.k_ei_js_js, theta_ei_js_n) + ss.theta_dstrb_js_ns[:, 1].reshape(-1, 1)) * ss.phi_t1_js_ms / (1.0 - ss.r_js_ms),
            q_s_js_n=q_srf_js_n,
            theta_frt_is_n=np.array([[3.3084074373484]]),
            x_frt_is_n=np.array([[0.0]]),
            theta_ei_js_n=theta_ei_js_n
        )

        # 計算実行
        c_n_pls = sequence.run_tick(n=-1, delta_t=900.0, ss=ss, c_n=c_n, logger=None, run_up=True)

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
