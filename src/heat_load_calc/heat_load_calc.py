import json
import sys
import time
import logging
import argparse
from os import path, getcwd, mkdir
import urllib.request, urllib.error

# 絶対パスでモジュールを探索できるようにする
sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '..')))

from heat_load_calc import core2, schedule, weather, interval


def run(
        logger,
        house_data_path: str,
        output_data_dir: str,
        schedule_specify_method: str = 'calculate',
        schedule_data_folder_path: str = "",
        is_schedule_saved: bool = False,
        weather_specify_method: str = 'ees',
        weather_file_path: str = "",
        region: int = 0,
        is_weather_saved: bool = False
):
    """負荷計算処理の実行

    Args:
        logger
        house_data_path (str): 住宅計算条件JSONファイルへのパス
        output_data_dir (str): 出力フォルダへのパス
        schedule_specify_method: スケジュールデータの指定方法
        schedule_data_folder_path: 独自のスケジュールを指定した場合にスケジュールファイルが置かれているフォルダパス（相対パス）
        is_schedule_saved: スケジュールを出力するか否か
        weather_specify_method: 気象データの指定方法
        weather_file_path: 気象データのファイルパス
        region: 地域の区分
        is_weather_saved: 気象データを出力するか否か
    """

    # 時間間隔
    # TODO: 現在、時間間隔が15分間隔であることを前提として作成されているモジュールがいくつかあるため、当分の間15分間隔固定とする。
    itv = interval.Interval.M15

    # ---- 事前準備 ----

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

    # 気象データの生成 => weather_for_method_file.csv
    w = weather.Weather.make_weather(
        method=weather_specify_method,
        file_path=path.abspath(weather_file_path),
        region=region,
        itv=interval.Interval.M15
    )

    scd = schedule.Schedule.get_schedule(
        schedule_specify_method=schedule_specify_method,
        rooms=rd['rooms'],
        folder_path=schedule_data_folder_path
    )

    # ---- 計算 ----

    # 計算
    dd_i, dd_a = core2.calc(rd=rd, oc=w, scd=scd)

    # 気象データの保存
    if is_weather_saved:

        weather_path = path.join(output_data_dir, 'weather_for_method_file.csv')
        logger.info('Save weather data to `{}`'.format(weather_path))
        dd = w.get_weather_as_pandas_data_frame()
        dd.to_csv(weather_path, encoding='utf-8')

    # スケジュールファイルの保存
    if is_schedule_saved:

        scd.save_schedule(output_data_dir)

    # ---- 計算結果ファイルの保存 ----

    # 計算結果（瞬時値）
    result_detail_i_path = path.join(output_data_dir, 'result_detail_i.csv')
    logger.info('Save calculation results data (detailed version) to `{}`'.format(result_detail_i_path))
    dd_i.to_csv(result_detail_i_path, encoding='cp932')

    # 計算結果（平均・積算値）
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
        '--schedule',
        choices=['calculate', 'specify'],
        default='calculate',
        type=str,
        help="スケジュールの指定方法を選択します。"
    )
    parser.add_argument(
        '-s', '--schedule_data_folder_path',
        default="",
        type=str,
        help="独自のスケジュールを指定した場合にスケジュールファイルが置かれているフォルダパスを相対パスで指定します。"
    )
    parser.add_argument(
        '--schedule_saved',
        action='store_true',
        help="スケジュールを出力するか否かを指定します。"
    )

    parser.add_argument(
        '--weather',
        choices=['ees', 'file'],
        default='ees',
        help="気象データの作成方法を指定します。"
    )
    parser.add_argument(
        '--weather_path',
        default="",
        type=str,
        help="気象データの絶対パスを指定します。 weather オプションで file が指定された場合は必ず指定します。"
    )
    parser.add_argument(
        '--region',
        choices=[1, 2, 3, 4, 5, 6, 7, 8],
        default=0,
        type=int,
        help="地域の区分を指定します。気象データの作成方法として建築物省エネ法を指定した場合には必ず指定します。"
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

    # 引数を受け取る
    args = parser.parse_args()

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
        schedule_specify_method=args.schedule,
        schedule_data_folder_path=args.schedule_data_folder_path,
        is_schedule_saved=args.schedule_saved,
        weather_specify_method=args.weather,
        weather_file_path=args.weather_path,
        region=args.region,
        is_weather_saved=args.weather_saved
    )

    elapsed_time = time.time() - start

    logger.info("elapsed_time:{0}".format(elapsed_time) + "[sec]")


if __name__ == '__main__':
    main()
