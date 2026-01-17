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

    def test_theta_r_and_humid(self):

        self.assertAlmostEqual(17.683850308594, self._dd_i['rm0_t_r']['1989-01-01  00:15:00'], delta=0.001)
        self.assertAlmostEqual(0.0128588987114641, self._dd_i['rm0_x_r']['1989/8/24  16:15:00'], delta=0.001)
        self.assertAlmostEqual(24.3932465822963, self._dd_i['rm1_t_r']['1989-01-01  00:15:00'], delta=0.001)
        self.assertAlmostEqual(0.00337886450310274, self._dd_i['rm1_x_r']['1989-01-01  00:15:00'], delta=0.001)
        self.assertAlmostEqual(16.4853237577382, self._dd_i['rm2_t_r']['1989-01-01  00:15:00'], delta=0.001)
        self.assertAlmostEqual(0.00327844979144449, self._dd_i['rm2_x_r']['1989-01-01  00:15:00'], delta=0.001)


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
