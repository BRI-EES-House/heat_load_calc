import unittest
import os
import json
import csv

from heat_load_calc.core import core


# クラスの名前は何でも良いので、　TestSurfaceHeatBalance のような形で名前を変更してください。
class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls._data_dir = str(os.path.dirname(__file__)) + '/data'

        ds, dd = core.calc(input_data_dir=cls._data_dir, output_data_dir=cls._data_dir, show_detail_result=True)

        cls._ds = ds
        cls._dd = dd

        with open(cls._data_dir + '/mid_data_house.json') as f:
            mdh = json.load(f)

        cls._mdh = mdh

#    @unittest.skip('時間がかかるのでとりあえずskip')
    def test_weather(self):

        # 1/1 0:00の外気温度があっているかどうか？
        self.assertEqual(2.3, self._dd['out_temp']['1989-01-01 00:00:00'])

        # 1/1 0:15の外気温度があっているかどうか？
        self.assertEqual(2.375, self._dd['out_temp']['1989-01-01 00:15:00'])

        # 1/1 0:00の絶対湿度があっているかどうか？
        self.assertEqual(0.0032, self._dd['out_abs_humid']['1989-01-01 00:00:00'])

    # 室空気の熱収支のテスト
    def test_air_heat_balance(self):

        t_r_old = self._dd['rm0_t_r']['1989-01-01 00:00:00']
        t_r_new = self._dd['rm0_t_r']['1989-01-01 00:15:00']

        volume = self._mdh['spaces'][0]['volume']  # m3
        c_air = 1005  # J/kg K
        rho_air = 1.2  # kg/m3

        heat_storage = (t_r_new - t_r_old) * volume * c_air * rho_air / 900.0   # W

        # 部位からの対流熱取得, [W]
        surf_conv_heat = 0.0
        for i in range(0, 11):
            surf_conv_heat -= self._dd['rm0_b' + str(i) + '_qic_s']['1989-01-01 00:15:00']

        # 家具からの対流熱取得, [W]
        t_fun = self._dd['rm0_t_fun']['1989-01-01 00:15:00']
        c_fun = self._mdh['spaces'][0]['furniture']['heat_cond']  # W/K
        q_fun = c_fun * (t_fun - t_r_new)
        self.assertAlmostEqual(q_fun, - self._dd['rm0_q_s_fun']['1989-01-01 00:15:00'])

        # すきま風による熱取得, [W]
        v_reak = self._dd['rm0_v_reak']['1989-01-01 00:15:00']  # m3/s
        t_o = self._dd['out_temp']['1989-01-01 00:15:00']  # C
        q_vent_reak = c_air * rho_air * v_reak * (t_o - t_r_new)

        # 計画換気による熱取得, [W]
        v_mechanical = self._mdh['spaces'][0]['ventilation']['mechanical']  # m3/s
        q_vent_mecha = c_air * rho_air * v_mechanical * (t_o - t_r_new)

        # 自然換気による熱取得, [W]
        v_natural = self._dd['rm0_v_ntrl']['1989-01-01 00:15:00']  # m3/s
        q_vent_natural = c_air * rho_air * v_natural * (t_o - t_r_new)

        # 隣室間換気による熱取得, [W]
        v_next_vent0 = self._mdh['spaces'][0]['ventilation']['next_spaces'][0]  # m3/s
        v_next_vent1 = self._mdh['spaces'][0]['ventilation']['next_spaces'][1]  # m3/s
        v_next_vent2 = self._mdh['spaces'][0]['ventilation']['next_spaces'][2]  # m3/s
        t_r_0_new = self._dd['rm0_t_r']['1989-01-01 00:15:00']
        t_r_1_new = self._dd['rm1_t_r']['1989-01-01 00:15:00']
        t_r_2_new = self._dd['rm2_t_r']['1989-01-01 00:15:00']
        q_next_vent0 = c_air * rho_air * v_next_vent0 * (t_r_0_new - t_r_new)
        q_next_vent1 = c_air * rho_air * v_next_vent1 * (t_r_1_new - t_r_new)
        q_next_vent2 = c_air * rho_air * v_next_vent2 * (t_r_2_new - t_r_new)
        q_next_vent = q_next_vent0 + q_next_vent1 + q_next_vent2

        # 局所換気による熱取得, [W]
        with open(self._data_dir + '/mid_data_local_vent.csv', 'r') as f:
            r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            l = [row for row in r]
        v_local = float(l[1][0])
        q_local_vent = c_air * rho_air * v_local * (t_o - t_r_new)

        # 内部発熱顕熱, [W]
        q_internal = self._dd['rm0_q_s_except_hum']['1989-01-01 00:15:00']\
                     + self._dd['rm0_q_hum_s']['1989-01-01 00:15:00']

        # 顕熱負荷, [W]
        L_s = self._dd['rm0_l_s_c']['1989-01-01 00:15:00']

        # 熱収支のテスト
        print('heat_storage=', heat_storage)
        print('surf_conv_heat=', surf_conv_heat)
        print('q_fun=', q_fun)
        print('q_vent_reak=', q_vent_reak)
        print('q_vent_mecha=', q_vent_mecha)
        print('q_vent_natural=', q_vent_natural)
        print('q_next_vent=', q_next_vent)
        print('q_local_vent=', q_local_vent)
        print('q_internal=', q_internal)
        print('L_s=', L_s)
        self.assertAlmostEqual(heat_storage,
                               + surf_conv_heat \
                               + q_fun \
                               + q_vent_reak \
                               + q_vent_mecha \
                               + q_vent_natural \
                               + q_next_vent \
                               + q_local_vent \
                               + q_internal \
                               + L_s)

    # 室内放射熱量の熱収支の確認
    def test_radiative_heat_balance(self):

        # 部位の放射熱取得, [W]
        surf_radiative_heat = 0.0
        for i in range(0, 11):
            surf_radiative_heat += self._dd['rm0_b' + str(i) + '_qir_s']['1989-01-01 00:15:00']

        self.assertAlmostEqual(surf_radiative_heat, 0.0)

    # 家具の熱収支のテスト
    def test_furniture_heat_balance(self):

        t_r_new = self._dd['rm0_t_r']['1989-01-01 00:15:00']
        t_fun_new = self._dd['rm0_t_fun']['1989-01-01 00:15:00']
        t_fun_old = self._dd['rm0_t_fun']['1989-01-01 00:00:00']

        # 家具と室の熱コンダクタンス
        c_fun = self._mdh['spaces'][0]['furniture']['heat_cond']  # W/K
        cap_fun = self._mdh['spaces'][0]['furniture']['heat_capacity']  # J/K
        q_fun1 = c_fun * (t_r_new - t_fun_new)
        q_fun2 = cap_fun * (t_fun_new - t_fun_old) / 900.0
        self.assertAlmostEqual(q_fun1, q_fun2)


if __name__ == '__main__':

    unittest.main()
