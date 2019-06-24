import csv
import datetime
import json
import common
from Gdata import Gdata
from Weather import enmWeatherComponent, Weather
from Schedule import Schedule
# from Exsrf import create_exsurfaces
from Sunbrk import SunbrkType
from Space import create_spaces

# 熱負荷計算の実行
def calc_Hload(cdata, weather, schedule):
    """
    :param cdata: シミュレーション全体の設定条件
    :param weather: 気象データ
    :param schedule: スケジュール
    :param sunbrk_mng: 外部日除け
    """
    # 計算開始日の通日
    lngStNday = common.get_nday(cdata.ApDate.month, cdata.ApDate.day)
    # 計算終了日の通日
    lngEnNday = common.get_nday(cdata.EnDate.month, cdata.EnDate.day)
    if cdata.ApDate.year != cdata.EnDate.year:
        lngEnNday += 365
    if lngStNday > lngEnNday:
        lngEnNday += 365

    # １日の計算ステップ数
    lngNtime = int(24 * 3600 / cdata.DTime)

    # 計算完了日数
    lngNnow = 0

    print('計算開始：', cdata.ApDate)
    print('計算終了：', cdata.EnDate)
    print('１日の計算ステップ数：', lngNtime)

    # 助走計算開始日
    apDate = cdata.ApDate

    # 出力リスト
    OutList = []
    # 日ループの開始
    for lngNday in range(lngStNday, lngEnNday + 1):
        # 時刻ループの開始
        for lngTloop in range(0, lngNtime):
            dtime = datetime.timedelta(days=lngNnow + float(lngTloop) / float(lngNtime))
            dtmNow = apDate + dtime

            # 傾斜面日射量の計算
            # Solpos = weather.Solpos(dtmNow)
            # Idn = weather.WeaData(enmWeatherComponent.Idn, dtmNow)
            # Isky = weather.WeaData(enmWeatherComponent.Isky, dtmNow)
            # for exsrf in exsurfaces.values():
            #     exsrf.update_slop_sol(Solpos, Idn, Isky)
            rowlist = []
            # 室温・熱負荷の計算
            if cdata.FlgOrig(dtmNow):
                # 出力文字列
                rowlist.append(str(dtmNow))
                rowlist.append('{0:.1f}'.format(weather.WeaData(enmWeatherComponent.Ta, dtmNow)))
                rowlist.append('{0:.4f}'.format(weather.WeaData(enmWeatherComponent.x, dtmNow) / 1000.0))
                if lngTloop == 0:
                    print(dtmNow)
            for space in spaces.values():
                # 室温、熱負荷の計算
                space.calcHload(
                    Gdata=cdata,
                    spaces=spaces,
                    dtmNow=dtmNow,
                    defSolpos=weather.Solpos(dtmNow),
                    Schedule=schedule,
                    Weather=weather
                )
                
                if cdata.FlgOrig(dtmNow):
                    rowlist.append('{0:.0f}'.format(space.nowWin))
                    rowlist.append('{0:.0f}'.format(space.demAC))
                    rowlist.append('{0:.0f}'.format(space.finalAC))
                    rowlist.append('{0:.2f}'.format(space.Tr))
                    rowlist.append('{0:.0f}'.format(space.RH))
                    rowlist.append('{0:.4f}'.format(space.xr))
                    rowlist.append('{0:.2f}'.format(space.MRT))
                    rowlist.append('{0:.2f}'.format(space.OT))
                    rowlist.append('{0:.2f}'.format(space.Clo))
                    rowlist.append('{0:.2f}'.format(space.Vel))
                    rowlist.append('{0:.2f}'.format(space.PMV))
                    rowlist.append('{0:.0f}'.format(space.Lcs))
                    rowlist.append('{0:.0f}'.format(space.Lrs))
                    rowlist.append('{0:.0f}'.format(space.Lcl))
                    # print('{0:.0f}'.format(space.nowWin), '{0:.0f}'.format(space.nowAC), '{0:.2f}'.format(space.Tr), \
                    #         '{0:.0f}'.format(space.RH), '{0:.2f}'.format(space.MRT), '{0:.2f}'.format(space.PMV), \
                    #         '{0:.0f}'.format(space.Lcs), '{0:.0f}'.format(space.Lr), '{0:.0f}'.format(space.Ll), "", end="")
            
            if cdata.FlgOrig(dtmNow):
                OutList.append(rowlist)
                # print("")

            # 前時刻の室温を現在時刻の室温、湿度に置換
            for space in spaces.values():
                space.update_oldstate()

        lngNnow += 1

    # CSVファイルの出力
    f = open('simulatin_result.csv', 'w')
    dataWriter = csv.writer(f, lineterminator='\n')
    dataWriter.writerows(OutList)
    f.close()

if __name__ == '__main__':
    js = open('input20190528.json', 'r', encoding='utf-8')
    # js = open('input.json', 'r', encoding='utf-8')
    d = json.load(js)

    # シミュレーション全体の設定条件の読み込み
    cdata = Gdata(**d['common'])

    # 外表面の初期化
    # exsurfaces = create_exsurfaces(d['ExSurface'])

    # 外部日除けクラスの初期化
    # sunbrks = create_sunbrks(d['Sunbrk'])

    # スペースの読み取り
    spaces = create_spaces(cdata, d['rooms'])

    # 気象データの読み込み
    weather = Weather(cdata.Latitude, cdata.Longitude, cdata.StMeridian)

    # スケジュールの初期化
    schedule = Schedule()

    # 熱負荷計算の実行
    calc_Hload(cdata, weather, schedule)
