import json
import sys
import time
import logging
import argparse
from os import path, getcwd, mkdir
import urllib.request, urllib.error

# 絶対パスでモジュールを探索できるようにする
sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '..')))

from heat_load_calc import core, weather, interval


def run(
        logger,
        house_data_path: str,
        output_data_dir: str,
        is_schedule_saved: bool = False,
        is_weather_saved: bool = False
):
    """run the heat load calculation

    Args:
        logger: logger
        house_data_path: path of the input file (json)
        output_data_dir:path of the directory for output files
        is_schedule_saved: is the schedule written out ?
        is_weather_saved: is the climate data written out ?
    """

    # ---- preparations for this calculation ----

    # create the output directory
    # if the output directory does not exist, create a new directory
    if path.exists(output_data_dir) is False:
        mkdir(output_data_dir)

    # if the specified directory was not created for some reason, an error message is displayed
    if path.isdir(output_data_dir) is False:
        logger.error('`{}` is not directory.'.format(output_data_dir), file=sys.stderr)

    # read the input data(json) of the building setting for calculation
    logger.info('Load house data from `{}`'.format(house_data_path))
    if house_data_path.lower()[:4] == 'http':
        with urllib.request.urlopen(url=house_data_path) as response:
            json_text = response.read()
            d = json.loads(json_text.decode())
    else:
        with open(house_data_path, 'r', encoding='utf-8') as js:
            d = json.load(js)

    # obtain the entry point to load an external files
    entry_point_dir=path.dirname(__file__)

    # ---- calculation !!! ----

    # calculation
    # obtain the datas bellow
    # - data file containing the instantaneous values of the calculation results (pandas data format)
    # - data file containing the integrated values and average values of the calculation results (pandas data format)
    # - boundaries class (which is only used for debugging)
    # - Schedule class
    # - Weather class
    dd_i, dd_a, _, scd, w = core.calc(d=d, entry_point_dir=entry_point_dir)

    # write out the climate data
    if is_weather_saved:
        weather_path = path.join(output_data_dir, 'weather_for_method_file.csv')
        logger.info('Save weather data to `{}`'.format(weather_path))
        dd = w.get_weather_as_pandas_data_frame()
        dd.to_csv(weather_path, encoding='utf-8')

    # write out schedule file
    if is_schedule_saved:
        scd.save_schedule(output_data_dir)

    # ---- save the calculated results ----

    # instantaneous values
    result_detail_i_path = path.join(output_data_dir, 'result_detail_i.csv')
    logger.info('Save calculation results data (detailed version) to `{}`'.format(result_detail_i_path))
    dd_i.to_csv(result_detail_i_path, encoding='cp932')

    # integrated values and average values
    result_detail_a_path = path.join(output_data_dir, 'result_detail_a.csv')
    logger.info('Save calculation results data (simplified version) to `{}`'.format(result_detail_a_path))
    dd_a.to_csv(result_detail_a_path, encoding='cp932')


def main():

    parser = argparse.ArgumentParser(description='建築物の負荷計算を行うプログラムです。')

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
        '--schedule_saved',
        action='store_true',
        help="スケジュールを出力するか否かを指定します。"
    )

    parser.add_argument(
        '--weather_saved',
        action='store_true',
        help="気象データを出力するか否かを指定します。"
    )

    parser.add_argument(
        "--log",
        choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'],
        default='ERROR',
        help="ログレベルを指定します. (Default=ERROR)"
    )

    # make args
    args = parser.parse_args()

    # make logger
    logger = _make_logger(log=args.log)

    # record start time
    start = time.time()

    run(
        logger=logger,
        house_data_path=args.house_data,
        output_data_dir=args.output_data_dir,
        is_schedule_saved=args.schedule_saved,
        is_weather_saved=args.weather_saved
    )

    # take the difference between the start time and the end time
    elapsed_time = time.time() - start

    # output the time taken for the calculation
    logger.info("elapsed_time:{0}".format(elapsed_time) + "[sec]")


def _make_logger(
        log: str
    ) -> logging.Logger:
    """make logger

    Args:
        log: logging level
    Returns:
        logging.Logger: logger
    """

    # set logging level
    level = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARN': logging.WARN,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }[log]

    # set logger
    logger = logging.getLogger(name='HeatLoadCalc')
    logger.setLevel(level=level)

    # set handler
    handler = logging.StreamHandler()
    handler.setLevel(level=level)

    # set log output format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # set handler to logger
    logger.addHandler(handler)

    return logger



if __name__ == '__main__':
    main()
