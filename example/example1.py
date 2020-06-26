import json
import time

from heat_load_calc import s3_space_initializer
from heat_load_calc.weather import weather
from heat_load_calc.core import core


def run():

    js = open('data_example1/input_residential.json', 'r', encoding='utf-8')

    d = json.load(js)

    weather.make_weather(region=d['common']['region'], output_data_dir='data_example1')

    s3_space_initializer.make_house(d=d, input_data_dir='data_example1', output_data_dir='data_example1')

    core.calc(input_data_dir='data_example1', output_data_dir='data_example1')


if __name__ == '__main__':

    start = time.time()
    run()
    elapsed_time = time.time() - start
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")