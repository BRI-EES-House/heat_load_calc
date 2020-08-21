import json
import os
import csv
import unittest

from heat_load_calc import s3_space_initializer
from heat_load_calc.weather import weather
from heat_load_calc.core import core


# クラスの名前は何でも良いので、　TestSurfaceHeatBalance のような形で名前を変更してください。
class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        s_folder = 'data'

        bln_make_weather = True

        bln_space_initialize = True

        js = open(str(os.path.dirname(__file__)) + '/' + s_folder + '/input_residential.json', 'r', encoding='utf-8')

        d = json.load(js)

        if bln_make_weather:
            weather.make_weather(region=d['common']['region'], output_data_dir=s_folder, csv_output=True)

        if bln_space_initialize:
            s3_space_initializer.make_house(d=d, input_data_dir=s_folder, output_data_dir=s_folder)

        cls._data_dir = str(os.path.dirname(__file__)) + '/data'

        ds, dd = core.calc(input_data_dir=cls._data_dir, output_data_dir=cls._data_dir,
                           show_simple_result=True, show_detail_result=True)

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

    def test_air_heat_balance(self):

        t_r_old = self._dd['rm0_t_r']['1989-01-01 00:00:00']
        t_r_new = self._dd['rm0_t_r']['1989-01-01 00:15:00']

        volume = self._mdh['spaces'][0]['volume']  # m3
        c_air = 1005  # J/kg K
        rho_air = 1.2  # kg/m3

        heat_storage = (t_r_new - t_r_old) * volume * c_air * rho_air / 900.0   # W

        # 部位からの対流熱取得, [W]
        surf_conv_heat = 0.0
        for i in range(0, 6):
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

        # 局所換気による熱取得, [W]
        with open(self._data_dir + '/mid_data_local_vent.csv', 'r') as f:
            r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            l = [row for row in r]
        v_local = l[1][0]
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
        print('q_local_vent=', q_local_vent)
        print('q_internal=', q_internal)
        print('L_s=', L_s)
        self.assertAlmostEqual(heat_storage, \
                               + surf_conv_heat \
                               + q_fun \
                               + q_vent_reak \
                               + q_vent_mecha \
                               + q_vent_natural \
                               + q_local_vent \
                               + q_internal \
                               + L_s)


if __name__ == '__main__':

    unittest.main()

