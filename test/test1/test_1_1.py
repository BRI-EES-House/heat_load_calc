import unittest
import os
import json

from heat_load_calc.core import core


# クラスの名前は何でも良いので、　TestSurfaceHeatBalance のような形で名前を変更してください。
class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        data_dir = str(os.path.dirname(__file__)) + '/data'

        ds, dd = core.calc(input_data_dir=data_dir)

        cls._ds = ds
        cls._dd = dd

        with open(data_dir + '/mid_data_house.json') as f:
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

    def test_temp_change(self):

        t_r_old = self._dd['rm0_t_r']['1989-01-01 00:00:00']
        t_r_new = self._dd['rm0_t_r']['1989-01-01 00:15:00']

        volume = self._mdh['spaces'][0]['volume']  # m3
        c_air = 1005  # J/kg K
        rho_air = 1.2  # kg/m3

        heat = (t_r_new - t_r_old) * volume * c_air * rho_air

        self.assertAlmostEqual(-54808.782520573935, heat)



if __name__ == '__main__':

    unittest.main()
