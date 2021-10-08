import unittest
import json
import os
import csv

from heat_load_calc.initializer import initializer
from heat_load_calc.weather import weather
from heat_load_calc.core import core, furniture


class TestAllAtOnce(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        """
        initializerとcoreを一気通貫で計算するテスト
        :return:
        """

        print('\n testing all at once')

        cls._data_dir = str(os.path.dirname(__file__)) + '/data_example1'

        js = open(cls._data_dir + '/input_residential.json', 'r', encoding='utf-8')

        d = json.load(js)

        js.close()

        weather.make_weather(region=d['common']['region'], output_data_dir=cls._data_dir, csv_output=True)

        initializer.make_house(d=d, input_data_dir=cls._data_dir, output_data_dir=cls._data_dir)

        ds, dd = core.calc(input_data_dir=cls._data_dir, output_data_dir=cls._data_dir)

        cls._ds = ds
        cls._dd = dd

        with open(cls._data_dir + '/mid_data_house.json') as f:
            mdh = json.load(f)

        cls._mdh = mdh

    def test_weather(self):

        # 1/1 0:00の外気温度があっているかどうか？
        self.assertEqual(2.3, self._dd['out_temp']['1989-01-01 00:00:00'])

        # 1/1 0:15の外気温度があっているかどうか？
        self.assertEqual(2.375, self._dd['out_temp']['1989-01-01 00:15:00'])

        # 1/1 0:00の絶対湿度があっているかどうか？
        self.assertEqual(0.0032, self._dd['out_abs_humid']['1989-01-01 00:00:00'])

    def test_theta_r_and_humid(self):

        self.assertAlmostEqual(18.6278215601, self._dd['rm0_t_r']['1989-12-31  23:45:00'])
        self.assertAlmostEqual(0.0132358784030425, self._dd['rm0_x_r']['1989/8/24  16:00:00'])
        self.assertAlmostEqual(24.093575236161, self._dd['rm1_t_r']['1989-12-31  23:45:00'])
        self.assertAlmostEqual(0.00330617389905671, self._dd['rm1_x_r']['1989-12-31  23:45:00'])
        self.assertAlmostEqual(20.0209225042952, self._dd['rm2_t_r']['1989-12-31  23:45:00'])
        self.assertAlmostEqual(0.00327723691814345, self._dd['rm2_x_r']['1989-12-31  23:45:00'])

    # 室空気の熱収支のテスト（主たる居室）
    def test_air_heat_balance_mor(self):

        t_r_old = self._dd['rm0_t_r']['1989-01-01 00:00:00']
        t_r_new = self._dd['rm0_t_r']['1989-01-01 00:15:00']

        volume = self._mdh['rooms'][0]['volume']  # m3
        c_air = 1005  # J/kg K
        rho_air = 1.2  # kg/m3

        heat_storage = (t_r_new - t_r_old) * volume * c_air * rho_air / 900.0   # W

        # 部位からの対流熱取得, [W]
        surf_conv_heat = 0.0
        for i in range(0, 12):
            surf_conv_heat -= self._dd['rm0_b' + str(i) + '_qic_s']['1989-01-01 00:15:00']

        # 家具からの対流熱取得, [W]
        t_fun = self._dd['rm0_t_fun']['1989-01-01 00:15:00']
        c_fun = furniture._get_g_sh_frt(furniture._get_c_sh_frt(v_rm=volume))
        q_fun = c_fun * (t_fun - t_r_new)
        self.assertAlmostEqual(q_fun, - self._dd['rm0_q_s_fun']['1989-01-01 00:15:00'])

        # すきま風による熱取得, [W]
        v_reak = self._dd['rm0_v_reak']['1989-01-01 00:15:00']  # m3/s
        t_o = self._dd['out_temp']['1989-01-01 00:30:00']  # C
        q_vent_reak = c_air * rho_air * v_reak * (t_o - t_r_new)

        # 計画換気による熱取得, [W]
        v_mechanical = self._mdh['rooms'][0]['ventilation']['mechanical'] / 3600  # m3/s
        q_vent_mecha = c_air * rho_air * v_mechanical * (t_o - t_r_new)

        # 自然換気による熱取得, [W]
        v_natural = self._dd['rm0_v_ntrl']['1989-01-01 00:15:00']  # m3/s
        q_vent_natural = c_air * rho_air * v_natural * (t_o - t_r_new)

        # 隣室間換気による熱取得, [W]
        v_next_vent0 = 0.0                                                      # m3/s
        v_next_vent1 = 0.0                                                      # m3/s
        v_next_vent2 = 0.0                                                      # m3/s
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

    # 室空気の熱収支のテスト（非居室：室間換気流入あり）
    def test_air_heat_balance_nor(self):

        date_now = '1989-12-31 23:45:00'
        date_old = '1989-12-31 23:30:00'

        t_r_old = self._dd['rm2_t_r'][date_old]
        t_r_new = self._dd['rm2_t_r'][date_now]

        volume = self._mdh['rooms'][2]['volume']  # m3
        c_air = 1005  # J/kg K
        rho_air = 1.2  # kg/m3

        heat_storage = (t_r_new - t_r_old) * volume * c_air * rho_air / 900.0   # W

        # 部位からの対流熱取得, [W]
        surf_conv_heat = 0.0
        for i in range(0, 12):
            surf_conv_heat -= self._dd['rm2_b' + str(i) + '_qic_s'][date_now]

        # 家具からの対流熱取得, [W]
        t_fun = self._dd['rm2_t_fun'][date_now]
        c_fun = furniture._get_g_sh_frt(furniture._get_c_sh_frt(v_rm=volume))
        q_fun = c_fun * (t_fun - t_r_new)
        self.assertAlmostEqual(q_fun, - self._dd['rm2_q_s_fun'][date_now])

        # すきま風による熱取得, [W]
        v_reak = self._dd['rm2_v_reak'][date_now]  # m3/s
        t_o = self._dd['out_temp']['1989/1/1  0:00:00']  # C
        q_vent_reak = c_air * rho_air * v_reak * (t_o - t_r_new)

        # 計画換気による熱取得, [W]
        v_mechanical = self._mdh['rooms'][2]['ventilation']['mechanical'] / 3600  # m3/s
        q_vent_mecha = c_air * rho_air * v_mechanical * (t_o - t_r_new)

        # 自然換気による熱取得, [W]
        v_natural = self._dd['rm2_v_ntrl'][date_now]  # m3/s
        q_vent_natural = c_air * rho_air * v_natural * (t_o - t_r_new)

        # 隣室間換気による熱取得, [W]
        v_next_vent0 = self._mdh['rooms'][2]['ventilation']['next_spaces'][0]['volume'] / 3600  # m3/s
        v_next_vent1 = self._mdh['rooms'][2]['ventilation']['next_spaces'][1]['volume'] / 3600  # m3/s
        v_next_vent2 = 0.0                                                      # m3/s
        t_r_0_new = self._dd['rm0_t_r'][date_now]
        t_r_1_new = self._dd['rm1_t_r'][date_now]
        t_r_2_new = self._dd['rm2_t_r'][date_now]
        q_next_vent0 = c_air * rho_air * v_next_vent0 * (t_r_0_new - t_r_new)
        q_next_vent1 = c_air * rho_air * v_next_vent1 * (t_r_1_new - t_r_new)
        q_next_vent2 = c_air * rho_air * v_next_vent2 * (t_r_2_new - t_r_new)
        q_next_vent = q_next_vent0 + q_next_vent1 + q_next_vent2

        # 局所換気による熱取得, [W]
        with open(self._data_dir + '/mid_data_local_vent.csv', 'r') as f:
            r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            l = [row for row in r]
        v_local = float(l[35039][2])
        q_local_vent = c_air * rho_air * v_local * (t_o - t_r_new)

        # 内部発熱顕熱, [W]
        q_internal = self._dd['rm2_q_s_except_hum'][date_now]\
                     + self._dd['rm2_q_hum_s'][date_now]

        # 顕熱負荷, [W]
        L_s = self._dd['rm2_l_s_c'][date_now]

        # 熱収支のテスト
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

        # 各室の部位の数
        n_part = [12, 26, 12]

        for rm in range(3):
            # 部位の放射熱取得, [W]
            surf_radiative_heat = 0.0
            for i in range(n_part[rm]):
                surf_radiative_heat += self._dd['rm' + str(rm) + '_b' + str(i) + '_qir_s']['1989-01-01 12:15:00']

            self.assertAlmostEqual(surf_radiative_heat, 0.0)

    # 家具の熱収支のテスト
    def test_furniture_heat_balance(self):

        for rm in range(3):
            t_r_new = self._dd['rm' + str(rm) + '_t_r']['1989-01-01 12:15:00']
            t_fun_new = self._dd['rm' + str(rm) + '_t_fun']['1989-01-01 12:15:00']
            t_fun_old = self._dd['rm' + str(rm) + '_t_fun']['1989-01-01 12:00:00']

            # 家具と室の熱コンダクタンス
            # c_fun = self._mdh['spaces'][rm]['furniture']['heat_cond']  # W/K
            volume = self._mdh['rooms'][rm]['volume']  # m3
            c_fun = furniture._get_g_sh_frt(furniture._get_c_sh_frt(v_rm=volume))
#            cap_fun = self._mdh['spaces'][rm]['furniture']['heat_capacity']  # J/K
            cap_fun = furniture._get_c_sh_frt(v_rm=volume)
            q_s_fun = self._dd['rm' + str(rm) + '_q_s_sol_fun']['1989-01-01 12:15:00']
            q_fun1 = c_fun * (t_r_new - t_fun_new) + q_s_fun
            q_fun2 = cap_fun * (t_fun_new - t_fun_old) / 900.0
            self.assertAlmostEqual(q_fun1, q_fun2)

    # 放射熱伝達率の計算結果のテスト
    def test_nagata_radiative_heat_transfer(self):

        h_i_r0 = self._dd['rm0_b0_hir_s']['1989-01-01 00:15:00']
        self.assertAlmostEqual(first=h_i_r0, second=5.3033300464)
        h_i_r1 = self._dd['rm0_b1_hir_s']['1989-01-01 00:15:00']
        self.assertAlmostEqual(first=h_i_r1, second=5.1924019186)
        h_i_r10 = self._dd['rm0_b10_hir_s']['1989-01-01 00:15:00']
        self.assertAlmostEqual(first=h_i_r10, second=5.5218668782)

    def test_solar_heat_gain_balance(self):

        '''
        透過日射熱取得が家具と部位の吸収日射熱取得と一致する
        '''

        date_now = '1989-08-08 12:00:00'
        # 透過日射熱取得, W
        q_sol_trans = self._dd['rm0_q_sol_t'][date_now]

        # 家具の吸収日射, W
        q_sol_fun = self._dd['rm0_q_s_sol_fun'][date_now]

        # 部位の吸収日射, W
        surf_abs_sol = 0.0
        for i in range(11):
            surf_abs_sol += self._dd['rm0_b' + str(i) + '_qisol_s'][date_now]

        self.assertAlmostEqual(q_sol_trans, q_sol_fun + surf_abs_sol)

    # 備品の水分収支のテスト
    def test_furniture_humid_balance(self):

        '''
        備品の水分収支のテスト
        '''

        date_now = '1989-08-01 00:15:00'
        date_old = '1989-08-01 00:00:00'

        # 備品からの湿気取得, [kg/s]
        x_fun_now = self._dd['rm0_x_fun'][date_now]
        x_fun_old = self._dd['rm0_x_fun'][date_old]
        x_r_new = self._dd['rm0_x_r'][date_now]
        volume = self._mdh['rooms'][0]['volume']  # m3
#        cx_fun = self._mdh['spaces'][0]['furniture']['moisture_cond']  # kg/(s kg/kg(DA))
#        gf_fun = self._mdh['spaces'][0]['furniture']['moisture_capacity']   # kg
        gf_fun = furniture._get_c_lh_frt(v_rm=volume)
        cx_fun = furniture._get_g_lh_frt(c_lh_frt=gf_fun)
        humid_fun = cx_fun * (x_r_new - x_fun_now)
        humid_fun_storage = gf_fun * (x_fun_now - x_fun_old) / 900.0

        self.assertAlmostEqual(humid_fun_storage, humid_fun)

    # 室空気の水分収支のテスト（主たる居室）
    def test_air_humid_balance_mor(self):

        '''
        室の空気の水分収支をテスト
        '''

        print('test air humid balance mor')

        # テスト時刻を指定
        date_now = '1989-08-08 12:00:00'
        date_old = '1989-08-08 11:45:00'
        schedule_row = 21072

        # 室空気の蓄湿, [kg/s]
        x_r_old = self._dd['rm0_x_r'][date_old]
        x_r_new = self._dd['rm0_x_r'][date_now]
        volume = self._mdh['rooms'][0]['volume']  # m3
        rho_air = 1.2  # kg/m3
        humid_storage = (x_r_new - x_r_old) * volume * rho_air / 900.0   # kg/s

        # 備品からの湿気取得, [kg/s]
        x_fun = self._dd['rm0_x_fun'][date_now]
#        cx_fun = self._mdh['spaces'][0]['furniture']['moisture_cond']  # kg/(s kg/kg(DA))
        cx_fun = furniture._get_g_lh_frt(c_lh_frt=furniture._get_c_lh_frt(v_rm=volume))
        humid_fun = cx_fun * (x_fun - x_r_new)

        # すきま風による湿気取得, [kg/s]
        v_reak = self._dd['rm0_v_reak'][date_now]  # m3/s
        x_o = self._dd['out_abs_humid']['1989-08-08 12:15:00']  # kg/kg(DA)
        humid_reak = rho_air * v_reak * (x_o - x_r_new)

        # 計画換気による湿気取得, [kg/s]
        v_mechanical = self._mdh['rooms'][0]['ventilation']['mechanical'] / 3600  # m3/s
        humid_mecha = rho_air * v_mechanical * (x_o - x_r_new)

        # 自然換気による熱取得, [kg/s]
        v_natural = self._dd['rm0_v_ntrl'][date_now]  # m3/s
        humid_natural = rho_air * v_natural * (x_o - x_r_new)

        # 隣室間換気による湿気取得, [kg/s]
        v_next_vent0 = 0.0  # m3/s
        v_next_vent1 = 0.0  # m3/s
        v_next_vent2 = 0.0  # m3/s
        x_r_0_new = self._dd['rm0_x_r'][date_now]
        x_r_1_new = self._dd['rm1_x_r'][date_now]
        x_r_2_new = self._dd['rm2_x_r'][date_now]
        humid_next_vent0 = rho_air * v_next_vent0 * (x_r_0_new - x_r_new)
        humid_next_vent1 = rho_air * v_next_vent1 * (x_r_1_new - x_r_new)
        humid_next_vent2 = rho_air * v_next_vent2 * (x_r_2_new - x_r_new)
        humid_next_vent = humid_next_vent0 + humid_next_vent1 + humid_next_vent2

        # 局所換気による湿気取得, [kg/s]
        with open(self._data_dir + '/mid_data_local_vent.csv', 'r') as f:
            r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            l = [row for row in r]
        v_local = float(l[schedule_row][0])
        humid_local = rho_air * v_local * (x_o - x_r_new)

        # 内部発湿, [kg/s]
        humid_internal = self._dd['rm0_q_l_except_hum'][date_now] \
                     + self._dd['rm0_q_hum_l'][date_now]

        # 潜熱負荷, [kg/s]
        L_l = self._dd['rm0_l_l_c'][date_now] / 2501000.0

        self.assertAlmostEqual(humid_storage,
                               humid_fun + humid_reak + humid_mecha
                               + humid_natural + humid_next_vent
                               + humid_local + humid_internal + L_l)

    # 室空気の水分収支のテスト（非居室）
    def test_air_humid_balance_nor(self):

        '''
        室の空気の水分収支をテスト
        '''

        print('test air humid balance nor')

        # テスト時刻を指定
        date_now = '1989-08-08 12:00:00'
        date_old = '1989-08-08 11:45:00'
        schedule_row = 21072

        # 室空気の蓄湿, [kg/s]
        x_r_old = self._dd['rm2_x_r'][date_old]
        x_r_new = self._dd['rm2_x_r'][date_now]
        volume = self._mdh['rooms'][2]['volume']  # m3
        rho_air = 1.2  # kg/m3
        humid_storage = (x_r_new - x_r_old) * volume * rho_air / 900.0   # kg/s

        # 備品からの湿気取得, [kg/s]
        x_fun = self._dd['rm2_x_fun'][date_now]
#        cx_fun = self._mdh['spaces'][2]['furniture']['moisture_cond']  # kg/(s kg/kg(DA))
        cx_fun = furniture._get_g_lh_frt(c_lh_frt=furniture._get_c_lh_frt(v_rm=volume))
        humid_fun = cx_fun * (x_fun - x_r_new)

        # すきま風による湿気取得, [kg/s]
        v_reak = self._dd['rm2_v_reak'][date_now]  # m3/s
        x_o = self._dd['out_abs_humid']['1989-08-08 12:15:00']  # kg/kg(DA)
        humid_reak = rho_air * v_reak * (x_o - x_r_new)

        # 計画換気による湿気取得, [kg/s]
        v_mechanical = self._mdh['rooms'][2]['ventilation']['mechanical'] / 3600  # m3/s
        humid_mecha = rho_air * v_mechanical * (x_o - x_r_new)

        # 自然換気による熱取得, [kg/s]
        v_natural = self._dd['rm2_v_ntrl'][date_now]  # m3/s
        humid_natural = rho_air * v_natural * (x_o - x_r_new)

        # 隣室間換気による湿気取得, [kg/s]
        v_next_vent0 = self._mdh['rooms'][2]['ventilation']['next_spaces'][0]['volume'] / 3600  # m3/s
        v_next_vent1 = self._mdh['rooms'][2]['ventilation']['next_spaces'][1]['volume'] / 3600  # m3/s
        v_next_vent2 = 0.0                                                      # m3/s
        x_r_0_new = self._dd['rm0_x_r'][date_now]
        x_r_1_new = self._dd['rm1_x_r'][date_now]
        x_r_2_new = self._dd['rm2_x_r'][date_now]
        humid_next_vent0 = rho_air * v_next_vent0 * (x_r_0_new - x_r_new)
        humid_next_vent1 = rho_air * v_next_vent1 * (x_r_1_new - x_r_new)
        humid_next_vent2 = rho_air * v_next_vent2 * (x_r_2_new - x_r_new)
        humid_next_vent = humid_next_vent0 + humid_next_vent1 + humid_next_vent2

        # 局所換気による湿気取得, [kg/s]
        with open(self._data_dir + '/mid_data_local_vent.csv', 'r') as f:
            r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            l = [row for row in r]
        v_local = float(l[schedule_row][2])
        humid_local = rho_air * v_local * (x_o - x_r_new)

        # 内部発湿, [kg/s]
        humid_internal = self._dd['rm2_q_l_except_hum'][date_now] \
                     + self._dd['rm2_q_hum_l'][date_now]

        # 潜熱負荷, [kg/s]
        L_l = self._dd['rm2_l_l_c'][date_now] / 2501000.0

        self.assertAlmostEqual(humid_storage,
                               humid_fun + humid_reak + humid_mecha
                               + humid_natural + humid_next_vent
                               + humid_local + humid_internal + L_l)


if __name__ == '__main__':

    unittest.main()
