import json
import os
import time

from heat_load_calc.initializer import initializer
from heat_load_calc.weather import weather
from heat_load_calc.core import core


def run():

    data_dir = str(os.path.dirname(__file__)) + '/data_example1'

    js = open(data_dir + '/input_residential.json', 'r', encoding='utf-8')

    d = json.load(js)

    weather.make_weather(region=d['common']['region'], output_data_dir=data_dir, csv_output=True)

    initializer.make_house(d=d, input_data_dir=data_dir, output_data_dir=data_dir)

    core.calc(input_data_dir=data_dir, output_data_dir=data_dir, show_detail_result=True)


if __name__ == '__main__':

    start = time.time()
    run()
    elapsed_time = time.time() - start
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
