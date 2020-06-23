from typing import Dict
import csv
import json
import time
import numpy as np
import pandas as pd

import x_04_weather as x_04
import x_05_solar_position as x_05
import x_17_calculation_period as x_17

from s3_space_initializer import make_house
import s3_simulator as simulator
import a33_results_exporting as exporter
import a37_groundonly_runup_calculation as a37
from s3_space_loader import initialize_conditions, Conditions
import s3_space_loader as space_loader
from a33_results_exporting import Logger
import heat_load_calc.s3_space_initializer as s3
from heat_load_calc.core.pre_calc_parameters import PreCalcParameters


# 熱負荷計算の実行
def calc_heat_load(d: Dict):
    """

    Args:
        d: 入力情報（辞書形式）

    Returns:

    """

    # 本計算のステップ数
    n_step_main = x_17.get_n_step_main()

    # 助走計算のステップ数
    n_step_run_up = x_17.get_n_step_run_up()

    # 助走計算の日数のうち建物全体を解く日数, d
    n_step_run_up_build = x_17.get_n_step_run_up_build()

    # 地域の区分
    region = d['common']['region']

    # 気象データの読み込み
    #   (1)ステップnにおける外気温度, ℃, [8760 * 4]
    #   (2)ステップnにおける法線面直達日射量, W/m2, [8760 * 4]
    #   (3)ステップnにおける水平面天空日射量, W/m2, [8760 * 4]
    #   (4)ステップnにおける夜間放射量, W/m2, [8760 * 4]
    #   (5)ステップnにおける外気絶対湿度, g/kgDA, [8760 * 4]
    theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns = x_04.load_weather_data(region=region)

    # 太陽位置
    #   (1) ステップnにおける太陽高度, rad, [8760 * 96]
    #   (2) ステップnにおける太陽方位角, rad, [8760 * 96]
    h_sun_ns, a_sun_ns = x_05.calc_solar_position(region=region)

    # スペースの読み取り
    make_house(d=d, i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, r_n_ns=r_n_ns, theta_o_ns=theta_o_ns, h_sun_ns=h_sun_ns, a_sun_ns=a_sun_ns)

    spaces2 = s3.make_pre_calc_parameters()

    conditions_n = initialize_conditions(ss=spaces2)

    logger = Logger(n_spaces=spaces2.number_of_spaces, n_bdrys=spaces2.total_number_of_bdry)
    logger.pre_logging(spaces2)

    # 助走計算1(土壌のみ)
    print('助走計算1（土壌のみ）')
    Tave = a37.get_a0(theta_o_ns)

    for n in range(-n_step_run_up, -n_step_run_up_build):
        conditions_n = simulator.run_tick_groundonly(
            To_n=theta_o_ns[n],
            Tave=Tave,
            c_n=conditions_n,
            ss=spaces2
        )

    # 助走計算2(室温、熱負荷)
    print('助走計算1（建物全体）')
    for n in range(-n_step_run_up_build, 0):
        conditions_n = simulator.run_tick(
            theta_o_n=theta_o_ns[n],
            x_o_n=x_o_ns[n],
            n=n,
            ss=spaces2,
            c_n=conditions_n,
            logger=logger
        )

    # 本計算(室温、熱負荷)
    print('本計算')
    for n in range(0, n_step_main):
        conditions_n = simulator.run_tick(
            theta_o_n=theta_o_ns[n],
            x_o_n=x_o_ns[n],
            n=n,
            ss=spaces2,
            c_n=conditions_n,
            logger=logger
        )

    logger.post_logging(spaces2)

    print('ログ作成')

    exporter.record(theta_o_ns=theta_o_ns, x_o_ns=x_o_ns, pps=spaces2, logger=logger)


def run():

    # js = open('1RCase1_最初の外壁削除.json', 'r', encoding='utf-8')
    # js = open('input_non_residential.json', 'r', encoding='utf-8')
    js = open('input_residential.json', 'r', encoding='utf-8')
    # js = open('input_residential_include_ground.json', 'r', encoding='utf-8')

    # js = open('input_simple_residential.json', 'r', encoding='utf-8')
    # js = open('検証用.json', 'r', encoding='utf-8')
    d_json = json.load(js)

    # 熱負荷計算の実行
    calc_heat_load(d=d_json)


if __name__ == '__main__':

    start = time.time()
    run()
    elapsed_time = time.time() - start
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
