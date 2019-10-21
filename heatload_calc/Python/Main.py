import numpy as np
import csv, json, datetime
import a4_weather as a4
import apdx5_solar_position as a5

from Gdata import Gdata
from s3_space_initializer import init_spaces
from s3_space_loader import Space
import s3_simulator as simulator
import a33_results_exporting as exporter


# 熱負荷計算の実行
def calc_Hload(cdata, To_n, xo_n):
    """
    :param cdata: シミュレーション全体の設定条件
    """
    # 計算開始日の通日
    lngStNday = get_nday(cdata.ApDate.month, cdata.ApDate.day)
    # 計算終了日の通日
    lngEnNday = get_nday(cdata.EnDate.month, cdata.EnDate.day)
    if cdata.ApDate.year != cdata.EnDate.year:
        lngEnNday += 365
    if lngStNday > lngEnNday:
        lngEnNday += 365

    print('計算開始：', cdata.ApDate)
    print('計算終了：', cdata.EnDate)
    print('１日の計算ステップ数：', 96)

    # 助走計算開始日
    apDate = cdata.ApDate

    OutList = exporter.append_headers(spaces)

    # 助走計算1(土壌のみ)
    for n in range((lngStNday-366) * 96, (lngStNday-184) * 96):
        simulator.run_tick_groundonly(spaces, To_n[n], n)

    # 助走計算2(室温、熱負荷)
    for n in range((lngStNday-184) * 96, (lngStNday-1) * 96):
        simulator.run_tick(spaces, To_n[n], xo_n[n], n)

    # 本計算(室温、熱負荷)
    for n in range((lngStNday-1) * 96, lngEnNday * 96):
        simulator.run_tick(spaces, To_n[n], xo_n[n], n)

    # 年間熱負荷の積算
    _ = exporter.get_annual_loads(spaces)

    # 計算結果出力前処理
    dtlist = get_datetime_list()
    for n in range((lngStNday - 1) * 96, lngEnNday * 96):
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

    return (ndays.days + 1)


if __name__ == '__main__':
    # js = open('1RCase1_最初の外壁削除.json', 'r', encoding='utf-8')
    # js = open('input_non_residential.json', 'r', encoding='utf-8')
    js = open('input_residential.json', 'r', encoding='utf-8')
    # js = open('input_simple_residential.json', 'r', encoding='utf-8')
    # js = open('検証用.json', 'r', encoding='utf-8')
    d = json.load(js)

    # 地域の区分
    region = d['common']['region']

    # シミュレーション全体の設定条件の読み込み
    cdata = Gdata(**d['common'])

    # 気象データの読み込み
    To_n, I_DN_n, I_sky_n, RN_n, xo_n = a4.load_weatherdata()

    # 太陽位置は個別計算可能
    solar_position = a5.calc_solar_position(region=region)

    # スペースの読み取り
    spaces = {}
    for room in d['rooms']:
        space = Space(room)
        init_spaces(space, solar_position, I_DN_n, I_sky_n, RN_n, To_n)
        spaces[room['name']] = space

    # 熱負荷計算の実行
    calc_Hload(cdata, To_n, xo_n)
