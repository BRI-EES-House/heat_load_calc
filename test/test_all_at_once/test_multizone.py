import unittest
import json
import os
import time

from heat_load_calc import core, schedule, weather, furniture, interval


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

        rd = json.load(js)

        js.close()

        oc = weather.Weather.make_weather(rd=rd, itv=interval.Interval.M15)

        dd_i, dd_a, bs, scd = core.calc(rd=rd, w=oc, itv=interval.Interval.M15, entry_point_dir=os.path.dirname(__file__))

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

    # 室空気の熱収支のテスト（主たる居室）
    def test_air_heat_balance_mor(self):

        date_now = '1989-01-01 00:30:00'
        date_old = '1989-01-01 00:15:00'
        date_ave = '1989-01-01 00:15:00'
        date_ave1 = '1989-01-01 00:15:00'
        date_ave2 = '1989-01-01 00:30:00'
        t_r_old = self._dd_i['rm0_t_r'][date_old]
        t_r_new = self._dd_i['rm0_t_r'][date_now]

        volume = self._mdh['rooms'][0]['volume']  # m3
        c_air = 1005  # J/kg K
        rho_air = 1.2  # kg/m3

        heat_storage = (t_r_new - t_r_old) * volume * c_air * rho_air / 900.0   # W

        # 部位からの対流熱取得, [W]
        surf_conv_heat = 0.0
        for i in range(0, 12):
            surf_conv_heat -= self._dd_i['b' + str(i) + '_qic_s'][date_now]

        # 家具からの対流熱取得, [W]
        t_fun = self._dd_i['rm0_t_fun'][date_now]
        c_fun = furniture._get_g_sh_frt_i(furniture._get_c_sh_frt_i(v_rm_i=volume))
        q_fun = c_fun * (t_fun - t_r_new)

        self.assertAlmostEqual(q_fun, - self._dd_a['rm0_q_s_fun'][date_ave1, date_ave2])

        # すきま風による熱取得, [W]
        v_reak = self._dd_a['rm0_v_reak'][date_ave1, date_ave2]  # m3/s
        t_o = self._dd_i['out_temp'][date_now]  # C
        q_vent_reak = c_air * rho_air * v_reak * (t_o - t_r_new)

        # 計画換気による熱取得, [W]
        v_mechanical = self._mdh['mechanical_ventilations'][0]['volume'] / 3600  # m3/s
        q_vent_mecha = c_air * rho_air * v_mechanical * (t_o - t_r_new)

        # 自然換気による熱取得, [W]
        v_natural = self._dd_a['rm0_v_ntrl'][date_ave1, date_ave2]  # m3/s
        q_vent_natural = c_air * rho_air * v_natural * (t_o - t_r_new)

        # 隣室間換気による熱取得, [W]
        v_next_vent0 = 0.0                                                      # m3/s
        v_next_vent1 = 0.0                                                      # m3/s
        v_next_vent2 = 0.0                                                      # m3/s
        t_r_0_new = self._dd_i['rm0_t_r'][date_now]
        t_r_1_new = self._dd_i['rm1_t_r'][date_now]
        t_r_2_new = self._dd_i['rm2_t_r'][date_now]
        q_next_vent0 = c_air * rho_air * v_next_vent0 * (t_r_0_new - t_r_new)
        q_next_vent1 = c_air * rho_air * v_next_vent1 * (t_r_1_new - t_r_new)
        q_next_vent2 = c_air * rho_air * v_next_vent2 * (t_r_2_new - t_r_new)
        q_next_vent = q_next_vent0 + q_next_vent1 + q_next_vent2

        # 局所換気による熱取得, [W]
#        with open(self._data_dir + '/mid_data_local_vent.csv', 'r') as f:
#            r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
#            l = [row for row in r]
#        v_local = float(l[1][0])
        v_local = self._v_mec_vent[0][1]
        q_local_vent = c_air * rho_air * v_local * (t_o - t_r_new)

        # 内部発熱顕熱, [W]
        q_internal = self._dd_a['rm0_q_s_except_hum'][date_ave1, date_ave2]\
                     + self._dd_a['rm0_q_hum_s'][date_ave1, date_ave2]

        # 顕熱負荷, [W]
        L_s = self._dd_a['rm0_l_s_c'][date_ave1, date_ave2]

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
        date_ave = '1989-12-31 23:30:00'
        date_ave1 = '1989-12-31 23:30:00'
        date_ave2 = '1989-12-31 23:45:00'


        t_r_old = self._dd_i['rm2_t_r'][date_old]
        t_r_new = self._dd_i['rm2_t_r'][date_now]

        volume = self._mdh['rooms'][2]['volume']  # m3
        c_air = 1005  # J/kg K
        rho_air = 1.2  # kg/m3

        heat_storage = (t_r_new - t_r_old) * volume * c_air * rho_air / 900.0   # W

        # 部位からの対流熱取得, [W]
        surf_conv_heat = 0.0
        for i in [38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49]:
            surf_conv_heat -= self._dd_i['b' + str(i) + '_qic_s'][date_now]

        # 家具からの対流熱取得, [W]
        t_fun = self._dd_i['rm2_t_fun'][date_now]
        c_fun = furniture._get_g_sh_frt_i(furniture._get_c_sh_frt_i(v_rm_i=volume))
        q_fun = c_fun * (t_fun - t_r_new)
        self.assertAlmostEqual(q_fun, - self._dd_a['rm2_q_s_fun'][date_ave1, date_ave2])

        # すきま風による熱取得, [W]
        v_reak = self._dd_a['rm2_v_reak'][date_ave1, date_ave2]  # m3/s
        t_o = self._dd_i['out_temp'][date_now]  # C
        q_vent_reak = c_air * rho_air * v_reak * (t_o - t_r_new)

        # 計画換気による熱取得, [W]
        v_mechanical = 0.0  # m3/s
        q_vent_mecha = c_air * rho_air * v_mechanical * (t_o - t_r_new)

        # 自然換気による熱取得, [W]
        v_natural = self._dd_a['rm2_v_ntrl'][date_ave1, date_ave2]  # m3/s
        q_vent_natural = c_air * rho_air * v_natural * (t_o - t_r_new)

        # 隣室間換気による熱取得, [W]
        v_next_vent0 = self._mdh['mechanical_ventilations'][0]['volume'] / 3600  # m3/s
        v_next_vent1 = self._mdh['mechanical_ventilations'][1]['volume'] / 3600  # m3/s
        v_next_vent2 = 0.0                                                      # m3/s
        t_r_0_new = self._dd_i['rm0_t_r'][date_now]
        t_r_1_new = self._dd_i['rm1_t_r'][date_now]
        t_r_2_new = self._dd_i['rm2_t_r'][date_now]
        q_next_vent0 = c_air * rho_air * v_next_vent0 * (t_r_0_new - t_r_new)
        q_next_vent1 = c_air * rho_air * v_next_vent1 * (t_r_1_new - t_r_new)
        q_next_vent2 = c_air * rho_air * v_next_vent2 * (t_r_2_new - t_r_new)
        q_next_vent = q_next_vent0 + q_next_vent1 + q_next_vent2

        # 局所換気による熱取得, [W]
#        with open(self._data_dir + '/mid_data_local_vent.csv', 'r') as f:
#            r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
#            l = [row for row in r]
#        v_local = float(l[35039][2])
        v_local = self._v_mec_vent[2][35039]
        q_local_vent = c_air * rho_air * v_local * (t_o - t_r_new)

        # 内部発熱顕熱, [W]
        q_internal = self._dd_a['rm2_q_s_except_hum'][date_ave1, date_ave2]\
                     + self._dd_a['rm2_q_hum_s'][date_ave1, date_ave2]

        # 顕熱負荷, [W]
        L_s = self._dd_a['rm2_l_s_c'][date_ave1, date_ave2]

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
        n_part = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37],
            [38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49]
        ]

        for rm in range(3):
            # 部位の放射熱取得, [W]
            surf_radiative_heat = 0.0
            for i in n_part[rm]:
                surf_radiative_heat += self._dd_i['b' + str(i) + '_qir_s']['1989-01-01 12:15:00']

            self.assertAlmostEqual(surf_radiative_heat, 0.0)

    # 家具の熱収支のテスト
    def test_furniture_heat_balance(self):

        for rm in range(3):
            t_r_new = self._dd_i['rm' + str(rm) + '_t_r']['1989-01-01 12:15:00']
            t_fun_new = self._dd_i['rm' + str(rm) + '_t_fun']['1989-01-01 12:15:00']
            t_fun_old = self._dd_i['rm' + str(rm) + '_t_fun']['1989-01-01 12:00:00']

            # 家具と室の熱コンダクタンス
            # c_fun = self._mdh['spaces'][rm]['furniture']['heat_cond']  # W/K
            volume = self._mdh['rooms'][rm]['volume']  # m3
            c_fun = furniture._get_g_sh_frt_i(furniture._get_c_sh_frt_i(v_rm_i=volume))
#            cap_fun = self._mdh['spaces'][rm]['furniture']['heat_capacity']  # J/K
            cap_fun = furniture._get_c_sh_frt_i(v_rm_i=volume)
#            q_s_fun = self._dd_i['rm' + str(rm) + '_q_s_sol_fun']['1989-01-01 12:15:00']
            q_s_fun = self._dd_i['rm' + str(rm) + '_q_s_sol_fun']['1989-01-01 12:00:00']
            q_fun1 = c_fun * (t_r_new - t_fun_new) + q_s_fun
            q_fun2 = cap_fun * (t_fun_new - t_fun_old) / 900.0
            self.assertAlmostEqual(q_fun1, q_fun2)

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

    # 備品の水分収支のテスト
    def test_furniture_humid_balance(self):

        '''
        備品の水分収支のテスト
        '''

        date_now = '1989-08-01 00:15:00'
        date_old = '1989-08-01 00:00:00'

        # 備品からの湿気取得, [kg/s]
        x_fun_now = self._dd_i['rm0_x_fun'][date_now]
        x_fun_old = self._dd_i['rm0_x_fun'][date_old]
        x_r_new = self._dd_i['rm0_x_r'][date_now]
        volume = self._mdh['rooms'][0]['volume']  # m3
#        cx_fun = self._mdh['spaces'][0]['furniture']['moisture_cond']  # kg/(s kg/kg(DA))
#        gf_fun = self._mdh['spaces'][0]['furniture']['moisture_capacity']   # kg
        gf_fun = furniture._get_c_lh_frt_i(v_rm_i=volume)
        cx_fun = furniture._get_g_lh_frt_i(c_lh_frt_i=gf_fun)
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
        date_ave = '1989-08-08 11:45:00'
        date_ave1 = '1989-08-08 11:45:00'
        date_ave2 = '1989-08-08 12:00:00'
        schedule_row = 21071

        # 室空気の蓄湿, [kg/s]
        x_r_old = self._dd_i['rm0_x_r'][date_old]
        x_r_new = self._dd_i['rm0_x_r'][date_now]
        volume = self._mdh['rooms'][0]['volume']  # m3
        rho_air = 1.2  # kg/m3
        humid_storage = (x_r_new - x_r_old) * volume * rho_air / 900.0   # kg/s

        # 備品からの湿気取得, [kg/s]
        x_fun = self._dd_i['rm0_x_fun'][date_now]
        cx_fun = furniture._get_g_lh_frt_i(c_lh_frt_i=furniture._get_c_lh_frt_i(v_rm_i=volume))
        humid_fun = cx_fun * (x_fun - x_r_new)

        # すきま風による湿気取得, [kg/s]
        v_reak = self._dd_a['rm0_v_reak'][date_ave1, date_ave2]  # m3/s
        x_o = self._dd_i['out_abs_humid'][date_now]  # kg/kg(DA)
        humid_reak = rho_air * v_reak * (x_o - x_r_new)

        # 計画換気による湿気取得, [kg/s]
        v_mechanical = self._mdh['mechanical_ventilations'][0]['volume'] / 3600  # m3/s
        humid_mecha = rho_air * v_mechanical * (x_o - x_r_new)

        # 自然換気による熱取得, [kg/s]
        v_natural = self._dd_a['rm0_v_ntrl'][date_ave1, date_ave2]  # m3/s
        humid_natural = rho_air * v_natural * (x_o - x_r_new)

        # 隣室間換気による湿気取得, [kg/s]
        v_next_vent0 = 0.0  # m3/s
        v_next_vent1 = 0.0  # m3/s
        v_next_vent2 = 0.0  # m3/s
        x_r_0_new = self._dd_i['rm0_x_r'][date_now]
        x_r_1_new = self._dd_i['rm1_x_r'][date_now]
        x_r_2_new = self._dd_i['rm2_x_r'][date_now]
        humid_next_vent0 = rho_air * v_next_vent0 * (x_r_0_new - x_r_new)
        humid_next_vent1 = rho_air * v_next_vent1 * (x_r_1_new - x_r_new)
        humid_next_vent2 = rho_air * v_next_vent2 * (x_r_2_new - x_r_new)
        humid_next_vent = humid_next_vent0 + humid_next_vent1 + humid_next_vent2

        # 局所換気による湿気取得, [kg/s]
        v_local = self._v_mec_vent[0][schedule_row]

        humid_local = rho_air * v_local * (x_o - x_r_new)

        # 内部発湿, [kg/s]
        humid_internal = self._dd_a['rm0_q_l_except_hum'][date_ave1, date_ave2] \
                     + self._dd_a['rm0_q_hum_l'][date_ave1, date_ave2]

        # 潜熱負荷, [kg/s]
        L_l = self._dd_a['rm0_l_l_c'][date_ave1, date_ave2] / 2501000.0

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
        date_ave = '1989-08-08 11:45:00'
        date_ave1 = '1989-08-08 11:45:00'
        date_ave2 = '1989-08-08 12:00:00'
        schedule_row = 21071

        # 室空気の蓄湿, [kg/s]
        x_r_old = self._dd_i['rm2_x_r'][date_old]
        x_r_new = self._dd_i['rm2_x_r'][date_now]
        volume = self._mdh['rooms'][2]['volume']  # m3
        rho_air = 1.2  # kg/m3
        humid_storage = (x_r_new - x_r_old) * volume * rho_air / 900.0   # kg/s

        # 備品からの湿気取得, [kg/s]
        x_fun = self._dd_i['rm2_x_fun'][date_now]
        cx_fun = furniture._get_g_lh_frt_i(c_lh_frt_i=furniture._get_c_lh_frt_i(v_rm_i=volume))
        humid_fun = cx_fun * (x_fun - x_r_new)

        # すきま風による湿気取得, [kg/s]
        v_reak = self._dd_a['rm2_v_reak'][date_ave1, date_ave2]  # m3/s
        x_o = self._dd_i['out_abs_humid'][date_now]  # kg/kg(DA)
        humid_reak = rho_air * v_reak * (x_o - x_r_new)

        # 計画換気による湿気取得, [kg/s]
        v_mechanical = 0.0  # m3/s
        humid_mecha = rho_air * v_mechanical * (x_o - x_r_new)

        # 自然換気による熱取得, [kg/s]
        v_natural = self._dd_a['rm2_v_ntrl'][date_ave1, date_ave2]  # m3/s
        humid_natural = rho_air * v_natural * (x_o - x_r_new)

        # 隣室間換気による湿気取得, [kg/s]
        v_next_vent0 = self._mdh['mechanical_ventilations'][0]['volume'] / 3600  # m3/s
        v_next_vent1 = self._mdh['mechanical_ventilations'][1]['volume'] / 3600  # m3/s
        v_next_vent2 = 0.0                                                      # m3/s
        x_r_0_new = self._dd_i['rm0_x_r'][date_now]
        x_r_1_new = self._dd_i['rm1_x_r'][date_now]
        x_r_2_new = self._dd_i['rm2_x_r'][date_now]
        humid_next_vent0 = rho_air * v_next_vent0 * (x_r_0_new - x_r_new)
        humid_next_vent1 = rho_air * v_next_vent1 * (x_r_1_new - x_r_new)
        humid_next_vent2 = rho_air * v_next_vent2 * (x_r_2_new - x_r_new)
        humid_next_vent = humid_next_vent0 + humid_next_vent1 + humid_next_vent2

        # 局所換気による湿気取得, [kg/s]
#        with open(self._data_dir + '/mid_data_local_vent.csv', 'r') as f:
#            r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
#            l = [row for row in r]
#        v_local = float(l[schedule_row][2])
        v_local = self._v_mec_vent[2][schedule_row]

        humid_local = rho_air * v_local * (x_o - x_r_new)

        # 内部発湿, [kg/s]
        humid_internal = self._dd_a['rm2_q_l_except_hum'][date_ave1, date_ave2] \
                     + self._dd_a['rm2_q_hum_l'][date_ave1, date_ave2]

        # 潜熱負荷, [kg/s]
        L_l = self._dd_a['rm2_l_l_c'][date_ave1, date_ave2] / 2501000.0

        self.assertAlmostEqual(humid_storage,
                               humid_fun + humid_reak + humid_mecha
                               + humid_natural + humid_next_vent
                               + humid_local + humid_internal + L_l)

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
