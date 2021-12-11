import json
import os
import sys
import time
import argparse


def run(folder: str):

    data_dir = str(os.path.dirname(__file__)) + '/example/' + folder

    js = open(data_dir + '/mid_data_house.json', 'r', encoding='utf-8')

    d = json.load(js)

    weather.make_weather(region=d['common']['region'], output_data_dir=data_dir, csv_output=True)

    initializer.make_house(d=d, input_data_dir=data_dir, output_data_dir=data_dir)

    core.calc(input_data_dir=data_dir, output_data_dir=data_dir, show_detail_result=True)



if __name__ == '__main__':

    # 絶対パスでモジュールを探索できるようにする
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

    from heat_load_calc.initializer import initializer
    from heat_load_calc.weather import weather
    from heat_load_calc.core import core

    parser = argparse.ArgumentParser(description='住宅負荷計算プログラム例題実行')  # 2. パーサを作る

    # parser.add_argumentで受け取る引数を追加していく
    parser.add_argument('arg1', help='計算を実行するフォルダ名')  # 必須の引数を追加

    # 引数を受け取る
    args = parser.parse_args()

    start = time.time()
    run(args.arg1)
    elapsed_time = time.time() - start
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
