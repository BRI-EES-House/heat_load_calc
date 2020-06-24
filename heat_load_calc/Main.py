from typing import Dict
import json
import time

import x_04_weather as x_04
import x_05_solar_position as x_05

from s3_space_initializer import make_house

from heat_load_calc.core import core

# 熱負荷計算の実行
def calc_heat_load(d: Dict):
    """

    Args:
        d: 入力情報（辞書形式）

    Returns:

    """

    # 地域の区分
    region = d['common']['region']

    # 気象データの読み込み
    #   (1)ステップnにおける外気温度, ℃, [8760 * 4]
    #   (2)ステップnにおける法線面直達日射量, W/m2, [8760 * 4]
    #   (3)ステップnにおける水平面天空日射量, W/m2, [8760 * 4]
    #   (4)ステップnにおける夜間放射量, W/m2, [8760 * 4]
    #   (5)ステップnにおける外気絶対湿度, kg/kgDA, [8760 * 4]
    theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns = x_04.load_weather_data(region=region)

    # 太陽位置
    #   (1) ステップnにおける太陽高度, rad, [8760 * 96]
    #   (2) ステップnにおける太陽方位角, rad, [8760 * 96]
    h_sun_ns, a_sun_ns = x_05.calc_solar_position(region=region)

    # スペースの読み取り
    make_house(d=d, i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, r_n_ns=r_n_ns, theta_o_ns=theta_o_ns, h_sun_ns=h_sun_ns, a_sun_ns=a_sun_ns, x_o_ns=x_o_ns)

    core.calc()


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
