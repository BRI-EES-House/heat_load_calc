import json
import sys
import time
import logging
import argparse
import pandas as pd
from os import path, getcwd, mkdir
import csv
import numpy as np
import urllib.request, urllib.error

# 絶対パスでモジュールを探索できるようにする
sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '..')))

from heat_load_calc.weather import weather
from heat_load_calc import core2, schedule


def run(
        logger,
        house_data_path: str,
        output_data_dir: str,
        generate_schedule_only: bool = False,
        generate_weather_only: bool = False,
        load_schedule: str = False,
        load_weather: str = False,
        schedule_data_folder_path: str = None
):
    """負荷計算処理の実行

    Args:
        house_data_path (str): 住宅計算条件JSONファイルへのパス
        output_data_dir (str): 出力フォルダへのパス
        generate_schedule_only (bool, optional): スケジュール生成のみ実行の場合はTrue. Defaults to False.
        generate_weather_only (bool, optional): 気象データ生成のみ実行する場合はTrue. Defaults to False.
        load_schedule (str, optional): スケジュールを生成せずに読み込む場合はTrue. Defaults to False.
        load_weather (str, optional): 気象データを生成せずに読み込む場合はTrue. Defaults to False.
        schedule_data_folder_path: 独自のスケジュールを指定した場合にスケジュールファイルが置かれているフォルダパス（相対パス）
    """

    # ---- 事前準備 ----

    flag_run_calc = \
        generate_schedule_only is False and generate_weather_only is False
    flag_run_weather = generate_schedule_only is False and load_weather is False
    flag_run_schedule = generate_weather_only is False and load_schedule is False

    flag_save_house = True
    flag_save_calc = flag_run_calc
    flag_save_weather = generate_weather_only is True
    flag_save_schedule = generate_schedule_only is True

    # 出力ディレクトリの作成
    if path.exists(output_data_dir) is False:
        mkdir(output_data_dir)

    if path.isdir(output_data_dir) is False:
        logger.error('`{}` is not directory.'.format(output_data_dir), file=sys.stderr)

    # 住宅計算条件JSONファイルの読み込み
    logger.info('Load house data from `{}`'.format(house_data_path))
    if house_data_path.lower()[:4] == 'http':
        with urllib.request.urlopen(url=house_data_path) as response:
            json_text = response.read()
            rd = json.loads(json_text.decode())
    else:
        with open(house_data_path, 'r', encoding='utf-8') as js:
            rd = json.load(js)

    # 気象データの生成 => weather.csv
    if flag_run_weather:
        dd_weather = weather.make_weather(region=rd['common']['region'])
    elif load_weather is not False:
        import_weather_path = path.join(path.abspath(load_weather), 'weather.csv')
        logger.info('Load weather data from `{}`'.format(import_weather_path))
        dd_weather = pd.read_csv(import_weather_path)

    # 局所換気量,内部発熱,内部発湿,在室人数,空調需要の生成 => mid_data_*.csv
    # if flag_run_schedule:
    #
    #     scd = schedule.Schedule.make_schedule(rooms=rd['rooms'])
    #
    # elif load_schedule is not False:
    #
    #     scd = schedule.Schedule.read_schedule(folder_path=load_schedule, rooms=rd['rooms'])

    scd = schedule.Schedule.get_schedule(rooms=rd['rooms'], flag_run_schedule=flag_run_schedule, folder_path=load_schedule)

    # ---- 計算 ----

    # 計算
    if flag_run_calc:

        # scd = schedule.Schedule(q_gen_is_ns=q_gen_is_ns, x_gen_is_ns=x_gen_is_ns, v_mec_vent_local_is_ns=v_mec_vent_local_is_ns, n_hum_is_ns=n_hum_is_ns, ac_demand_is_ns=ac_demand_is_ns)

        dd_i, dd_a = core2.calc(
            rd=rd,
            weather_dataframe=dd_weather,
            scd=scd
        )

    # ---- 中間生成ファイルの保存 ----

    # 住宅計算条件JSONファイル
    if flag_save_house:
        mid_data_house_path = path.join(output_data_dir, 'mid_data_house.csv')
        logger.info('Save house data to `{}`'.format(mid_data_house_path))
        with open(mid_data_house_path, 'w') as f:
            json.dump(rd, f)

    # 気象データの生成 => weather.csv
    if flag_save_weather:
        weather_path = path.join(output_data_dir, 'weather.csv')
        logger.info('Save weather data to `{}`'.format(weather_path))
        dd_weather.to_csv(weather_path, encoding='utf-8')

    if flag_save_schedule:
        # ステップnの室iにおける局所換気量, m3/s, [i, 8760*4]
        mid_data_local_vent_path = path.join(output_data_dir, 'mid_data_local_vent.csv')
        logger.info('Save v_mec_vent_local_is_ns to `{}`'.format(mid_data_local_vent_path))
        with open(mid_data_local_vent_path, 'w') as f:
            w = csv.writer(f, lineterminator='\n')
            w.writerows(scd.v_mec_vent_local_is_ns.T.tolist())

        # ステップnの室iにおける内部発熱, W, [8760*4]
        mid_data_heat_generation_path = path.join(output_data_dir, 'mid_data_heat_generation.csv')
        logger.info('Save q_gen_is_ns to `{}`'.format(mid_data_heat_generation_path))
        with open(mid_data_heat_generation_path, 'w') as f:
            w = csv.writer(f, lineterminator='\n')
            w.writerows(scd.q_gen_is_ns.T.tolist())

        # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [8760*4]
        mid_data_moisture_generation_path = path.join(output_data_dir, 'mid_data_moisture_generation.csv')
        logger.info('Save x_gen_is_ns to `{}`'.format(mid_data_moisture_generation_path))
        with open(mid_data_moisture_generation_path, 'w') as f:
            w = csv.writer(f, lineterminator='\n')
            w.writerows(scd.x_gen_is_ns.T.tolist())

        # ステップnの室iにおける在室人数, [8760*4]
        mid_data_occupants_path = path.join(output_data_dir, 'mid_data_occupants.csv')
        logger.info('Save n_hum_is_ns to `{}`'.format(mid_data_occupants_path))
        with open(mid_data_occupants_path, 'w') as f:
            w = csv.writer(f, lineterminator='\n')
            w.writerows(scd.n_hum_is_ns.T.tolist())

        # ステップnの室iにおける空調需要, [8760*4]
        mid_data_ac_demand_path = path.join(output_data_dir, 'mid_data_ac_demand.csv')
        logger.info('Save ac_demand_is_ns to `{}`'.format(mid_data_ac_demand_path))
        with open(mid_data_ac_demand_path, 'w') as f:
            w = csv.writer(f, lineterminator='\n')
            w.writerows(scd.ac_demand_is_ns.T.tolist())

    # ---- 計算結果ファイルの保存 ----

    if flag_save_calc:
        # 計算結果（詳細版）をいれたDataFrame
        result_detail_i_path = path.join(output_data_dir, 'result_detail_i.csv')
        logger.info('Save calculation results data (detailed version) to `{}`'.format(result_detail_i_path))
        dd_i.to_csv(result_detail_i_path, encoding='cp932')

        # 計算結果（簡易版）をいれたDataFrame
        result_detail_a_path = path.join(output_data_dir, 'result_detail_a.csv')
        logger.info('Save calculation results data (simplified version) to `{}`'.format(result_detail_a_path))
        dd_a.to_csv(result_detail_a_path, encoding='cp932')


def main():

    parser = argparse.ArgumentParser(description='建築物の負荷計算を行うプログラムです。')

    # parser.add_argumentで受け取る引数を追加していく
    parser.add_argument(
        'house_data',
        help='計算を実行するJSONファイル'
    )
    parser.add_argument(
        '-o', '--output_data_dir',
        dest="output_data_dir",
        default=getcwd(),
        help="出力フォルダ"
    )
    parser.add_argument(
        '--generate-schedule-only',
        action='store_true',
        help="指定された場合はスケジュールファイルの生成します。"
    )
    parser.add_argument(
        '--generate-weather-only',
        action='store_true',
        help="指定された場合は気象データファイルの生成します。"
    )
    parser.add_argument(
        '--load-schedule',
        default=False,
        help="独自のスケジュールを指定します。"
    )
    parser.add_argument(
        '-s', '--schedule_data_folder_path',
        default=None,
        help="独自のスケジュールを指定した場合にスケジュールファイルが置かれているフォルダパスを相対パスで指定します。"
    )
    parser.add_argument(
        '--load-weather',
        action='store_true',
        help="独自の気象データを指定します。"
    )
    parser.add_argument(
        "--log",
        choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'],
        default='ERROR',
        help="ログレベルを指定します. (Default=ERROR)"
    )

    # 引数を受け取る
    args = parser.parse_args()

    # ログレベル設定
#    log_level = getattr(logging, args.log.upper(), None)
#    logging.basicConfig(
#        level=log_level,
#        format='%(message)s'
#    )
    level = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARN': logging.WARN,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }[args.log]

    logger = logging.getLogger(name='HeatLoadCalc')
    handler = logging.StreamHandler()
    logger.setLevel(level=level)
    handler.setLevel(level=level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)



    start = time.time()
    run(
        logger=logger,
        house_data_path=args.house_data,
        output_data_dir=args.output_data_dir,
        generate_schedule_only=args.generate_schedule_only,
        generate_weather_only=args.generate_weather_only,
        load_schedule=args.load_schedule,
        load_weather=args.load_weather,
        schedule_data_folder_path=args.schedule_data_folder_path
    )
    elapsed_time = time.time() - start

    logging.info("elapsed_time:{0}".format(elapsed_time) + "[sec]")


if __name__ == '__main__':
    main()
