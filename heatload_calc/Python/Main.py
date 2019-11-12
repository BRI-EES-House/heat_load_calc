from typing import Dict
import csv
import json

import x_04_weather as x_04
import x_05_solar_position as x_05
import x_17_calculation_period as x_17

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
    spaces = []
    for room in d['rooms']:
        space = Space(room)
        init_spaces(space, i_dn_ns, i_sky_ns, r_n_ns, theta_o_ns, h_sun_ns, a_sun_ns)
        spaces.append(space)

    # 助走計算1(土壌のみ)
    for n in range(-n_step_run_up, -n_step_run_up_build):
        simulator.run_tick_groundonly(spaces=spaces, To_n=theta_o_ns[n], n=n)

    # 助走計算2(室温、熱負荷)
    for n in range(-n_step_run_up_build, 0):
        simulator.run_tick(spaces=spaces, To_n=theta_o_ns[n], xo_n=x_o_ns[n], n=n)

    # 本計算(室温、熱負荷)
    for n in range(0, n_step_main):
        simulator.run_tick(spaces=spaces, To_n=theta_o_ns[n], xo_n=x_o_ns[n], n=n)

    # log ヘッダーの作成
    log = exporter.append_headers(spaces=spaces)

    # log の記録
    for n in range(0, n_step_main):
        exporter.append_tick_log(spaces=spaces, log=log, To_n=theta_o_ns, n=n, xo_n=x_o_ns)

    # CSVファイルの出力
    f = open('simulatin_result.csv', 'w', encoding="utf_8_sig")
    dataWriter = csv.writer(f, lineterminator='\n')
    dataWriter.writerows(log)
    f.close()


if __name__ == '__main__':

    # js = open('1RCase1_最初の外壁削除.json', 'r', encoding='utf-8')
    # js = open('input_non_residential.json', 'r', encoding='utf-8')
    js = open('input_residential.json', 'r', encoding='utf-8')
    # js = open('input_residential_include_ground.json', 'r', encoding='utf-8')

    # js = open('input_simple_residential.json', 'r', encoding='utf-8')
    # js = open('検証用.json', 'r', encoding='utf-8')
    d_json = json.load(js)

    # 熱負荷計算の実行
    calc_heat_load(d=d_json)
