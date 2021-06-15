import unittest
import json
import os

from heat_load_calc.initializer import initializer
from heat_load_calc.weather import weather
from heat_load_calc.core import core


class TestAllAtOnce(unittest.TestCase):

    def test_all_at_once(self):

        """
        initializerとcoreを一気通貫で計算するテスト
        :return:
        """

        print('\n testing all at once')

        data_dir = str(os.path.dirname(__file__)) + '/data_example1'

        js = open(data_dir + '/input_residential.json', 'r', encoding='utf-8')

        d = json.load(js)

        js.close()

        weather.make_weather(region=d['common']['region'], output_data_dir=data_dir, csv_output=True)

        initializer.make_house(d=d, input_data_dir=data_dir, output_data_dir=data_dir)

        ds, dd = core.calc(input_data_dir=data_dir, output_data_dir=data_dir)

        self.assertAlmostEqual(18.630367276061, dd['rm0_t_r']['1989-12-31  23:45:00'])
        self.assertAlmostEqual(0.0132050530629374, dd['rm0_x_r']['1989/8/24  16:00:00'])
        self.assertAlmostEqual(24.0920859862135, dd['rm1_t_r']['1989-12-31  23:45:00'])
        self.assertAlmostEqual(0.00330535670575234, dd['rm1_x_r']['1989-12-31  23:45:00'])
        self.assertAlmostEqual(20.0248761260946, dd['rm2_t_r']['1989-12-31  23:45:00'])
        self.assertAlmostEqual(0.00327419283337522, dd['rm2_x_r']['1989-12-31  23:45:00'])


if __name__ == '__main__':

    unittest.main()
