from typing import Dict
import csv
import json
import datetime

from x_05_solar_position import calc_solar_position as x05_calc_solar_position
from x_17_calculation_period import get_n_step_main as x_17_get_n_step_main
from x_17_calculation_period import get_n_step_run_up as x_17_get_n_step_run_up
from x_17_calculation_period import get_n_step_run_up_build as x_17_get_n_step_run_up_build

import a4_weather as a4
from s3_space_initializer import init_spaces
from s3_space_loader import Space
import s3_simulator as simulator
import a33_results_exporting as exporter


# 熱負荷計算の実行
def calc_heat_load(d: Dict):
    """

    Args:
        d: 入力情報（辞書形式）

    Returns:

    """

    # 本計算のステップ数
    n_step_main = x_17_get_n_step_main()

    # 助走計算のステップ数
    n_step_run_up = x_17_get_n_step_run_up()

    # 助走計算の日数のうち建物全体を解く日数, d
    n_step_run_up_build = x_17_get_n_step_run_up_build()

    # 地域の区分
    region = d['common']['region']

    # 気象データの読み込み
    To_n, I_DN_n, I_sky_n, RN_n, xo_n = a4.load_weatherdata()

    # 太陽位置は個別計算可能
    h_s_n, a_s_n = x05_calc_solar_position(region=region)

    # スペースの読み取り
    spaces = {}
    for room in d['rooms']:
        space = Space(room)
        init_spaces(space, I_DN_n, I_sky_n, RN_n, To_n, h_s_n, a_s_n)
        spaces[room['name']] = space

    OutList = exporter.append_headers(spaces)

    # 助走計算1(土壌のみ)
    for n in range(-n_step_run_up, -n_step_run_up_build):
        simulator.run_tick_groundonly(spaces, To_n[n], n)

    # 助走計算2(室温、熱負荷)
    for n in range(-n_step_run_up_build, 0):
        simulator.run_tick(spaces, To_n[n], xo_n[n], n)

    # 本計算(室温、熱負荷)
    for n in range(0, n_step_main):
        simulator.run_tick(spaces, To_n[n], xo_n[n], n)

    # 年間熱負荷の積算
    _ = exporter.get_annual_loads(spaces)

    # 計算結果出力前処理
    dtlist = get_datetime_list()
    for n in range(0, n_step_main):
        exporter.append_tick_log(spaces, OutList, To_n, dtlist, n, xo_n)

    # CSVファイルの出力
    f = open('simulatin_result.csv', 'w', encoding="utf_8_sig")
    dataWriter = csv.writer(f, lineterminator='\n')
    dataWriter.writerows(OutList)
    f.close()



# 計算日時のリストを生成する（正確にはタプル)
def get_datetime_list():
    ntime = int(24 * 4)
    nnow = 0
    start_date = datetime.datetime(1989, 1, 1)
    dtlist = []
    for nday in range(365):
        for tloop in range(ntime):
            dtime = datetime.timedelta(days=nnow + float(tloop) / float(ntime))
            dtmNow = dtime + start_date
            dtlist.append(dtmNow)
        nnow += 1
    return tuple(dtlist)


# 通日を計算
def get_nday(mo, day):
    """
    :param mo: 月
    :param day: 日
    :return: 1月1日からの通日
    """
    new_year = datetime.datetime(2017, 1, 1)
    that_day = datetime.datetime(2017, mo, day)
    ndays = that_day - new_year

    return ndays.days + 1


if __name__ == '__main__':

    # js = open('1RCase1_最初の外壁削除.json', 'r', encoding='utf-8')
    # js = open('input_non_residential.json', 'r', encoding='utf-8')
    # js = open('input_residential.json', 'r', encoding='utf-8')
    js = open('input_residential_include_ground.json', 'r', encoding='utf-8')

    # js = open('input_simple_residential.json', 'r', encoding='utf-8')
    # js = open('検証用.json', 'r', encoding='utf-8')
    d_json = json.load(js)

    # 熱負荷計算の実行
    calc_heat_load(d=d_json)
