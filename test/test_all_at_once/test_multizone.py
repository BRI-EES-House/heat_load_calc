import unittest
import json
import time

from heat_load_calc.initializer import initializer
from heat_load_calc.weather import weather
from heat_load_calc.core import core


class TestAllAtOnce(unittest.TestCase):

    def test_all_at_once(self):

        print('\n testing all at once')

        js = open('data_example1/input_residential.json', 'r', encoding='utf-8')

        d = json.load(js)

        weather.make_weather(region=d['common']['region'], output_data_dir='data_example1', csv_output=True)

        initializer.make_house(d=d, input_data_dir='data_example1', output_data_dir='data_example1')

        ds, dd = core.calc(input_data_dir='data_example1', output_data_dir='data_example1')

        self.assertAlmostEqual(16.6934191745073, dd['rm0_t_r']['1989-12-31  23:45:00'])
        self.assertAlmostEqual(0.00391380896164113, dd['rm0_x_r']['1989-12-31  23:45:00'])


if __name__ == '__main__':

    start = time.time()
    unittest.main()
    elapsed_time = time.time() - start
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
