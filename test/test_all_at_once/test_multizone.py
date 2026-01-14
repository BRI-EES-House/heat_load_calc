import unittest
import json
import os
import time

from heat_load_calc import core, schedule, weather, furniture, interval

#@unittest.skip("")
class TestAllAtOnce(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """

        Returns:

        """

        print('\n testing all at once')

        start = time.time()

        cls._data_dir = str(os.path.dirname(__file__)) + '/data_example1'

        js = open(cls._data_dir + '/mid_data_house.json', 'r', encoding='utf-8')

        d = json.load(js)

        js.close()

        dd_i, dd_a, bs, scd, _ = core.calc(d=d, entry_point_dir=os.path.dirname(__file__), exe_verify=True)

        cls._dd_i = dd_i
        cls._dd_a = dd_a
        cls._bs = bs

        elapsed_time = time.time() - start

        print("elapsed_time:{0}".format(elapsed_time) + "[sec]")

        with open(cls._data_dir + '/mid_data_house.json') as f:
            mdh = json.load(f)

        cls._mdh = mdh
        cls._v_mec_vent = scd.v_mec_vent_local_is_ns


    def test_weather(self):

        # 1/1 0:00の外気温度があっているかどうか？
        self.assertEqual(2.3, self._dd_i['out_temp']['1989-01-01 00:00:00'])

        # 1/1 0:15の外気温度があっているかどうか？
        self.assertEqual(2.375, self._dd_i['out_temp']['1989-01-01 00:15:00'])

        # 1/1 0:00の絶対湿度があっているかどうか？
        self.assertEqual(0.0032, self._dd_i['out_abs_humid']['1989-01-01 00:00:00'])

    def test_theta_r_and_humid(self):

        self.assertAlmostEqual(17.683850308594, self._dd_i['rm0_t_r']['1989-01-01  00:15:00'], delta=0.001)
        self.assertAlmostEqual(0.0128588987114641, self._dd_i['rm0_x_r']['1989/8/24  16:15:00'], delta=0.001)
        self.assertAlmostEqual(24.3932465822963, self._dd_i['rm1_t_r']['1989-01-01  00:15:00'], delta=0.001)
        self.assertAlmostEqual(0.00337886450310274, self._dd_i['rm1_x_r']['1989-01-01  00:15:00'], delta=0.001)
        self.assertAlmostEqual(16.4853237577382, self._dd_i['rm2_t_r']['1989-01-01  00:15:00'], delta=0.001)
        self.assertAlmostEqual(0.00327844979144449, self._dd_i['rm2_x_r']['1989-01-01  00:15:00'], delta=0.001)


    # 放射熱伝達率の計算結果のテスト
    def test_nagata_radiative_heat_transfer(self):

        h_i_r0 = self._dd_i['b0_hir_s']['1989-01-01 00:15:00']
        self.assertAlmostEqual(first=h_i_r0, second=5.3033300464)
        h_i_r1 = self._dd_i['b1_hir_s']['1989-01-01 00:15:00']
        self.assertAlmostEqual(first=h_i_r1, second=5.1924019186)
        h_i_r10 = self._dd_i['b10_hir_s']['1989-01-01 00:15:00']
        self.assertAlmostEqual(first=h_i_r10, second=5.5218668782)

    def test_solar_heat_gain_balance(self):

        '''
        透過日射熱取得が家具と部位の吸収日射熱取得と一致する
        '''

        date_now = '1989-08-08 12:00:00'
        date_now_plus = '1989-08-08 12:15:00'
        # 透過日射熱取得, W
        q_sol_trans = self._dd_i['rm0_q_sol_t'][date_now]

        # 家具の吸収日射, W
        q_sol_fun = self._dd_i['rm0_q_s_sol_fun'][date_now]
#        q_sol_fun = self._dd_i['rm0_q_s_sol_fun'][date_now_plus]

        # 部位の吸収日射, W
        surf_abs_sol = 0.0
        for i in range(11):
            surf_abs_sol += self._dd_i['b' + str(i) + '_qisol_s'][date_now]
#            surf_abs_sol += self._dd_i['b' + str(i) + '_qisol_s'][date_now_plus]

        self.assertAlmostEqual(q_sol_trans, q_sol_fun + surf_abs_sol)


    # 表面温度のテスト
    def test_theta_surface(self):

        # テスト時刻を指定
        date_now = '1989-08-08 12:00:00'

        n_bndrs = self._bs.n_b

        # 0番目の境界（外壁）
        for i in range(n_bndrs):
            bdr_name = 'b' + str(i) + '_'
            theta_s = self._dd_i[bdr_name + 't_s'][date_now]
            theta_rear = self._dd_i[bdr_name + 't_b'][date_now]
            f_cvl = self._dd_i[bdr_name + 'f_cvl'][date_now]
            q_all = self._dd_i[bdr_name + 'qiall_s'][date_now]
            phi_a_0 = self._bs.phi_a0_js[i][0]
            phi_t_0 = self._bs.phi_t0_js[i][0]
            self.assertAlmostEqual(theta_s, phi_a_0 * q_all + phi_t_0 * theta_rear + f_cvl)

if __name__ == '__main__':

    unittest.main()
