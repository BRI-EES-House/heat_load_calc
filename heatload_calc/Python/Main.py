import csv
import datetime
import json
import common
from common import get_nday
from Gdata import Gdata, FlgOrig
from Weather import enmWeatherComponent, Weather, WeaData, Solpos
from Sunbrk import SunbrkType
from Space import create_spaces, update_space_oldstate
from heat_load import calcHload
from PMV import get_OT

# 熱負荷計算の実行
def calc_Hload(cdata, weather):
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
    rowlist = []
    # ヘッダの出力
    rowlist.append("日時")
    rowlist.append("外気温度[℃]")
    rowlist.append("外気絶対湿度[kg/kg(DA)]")

    for space in spaces.values():
        rowlist.append(space.name + "_窓開閉")
        rowlist.append(space.name + "_在室状況")
        rowlist.append(space.name + "_最終空調状態")
        rowlist.append(space.name + "_空気温度[℃]")
        rowlist.append(space.name + "_室相対湿度[%]")
        rowlist.append(space.name + "_室絶対湿度[kg/kg(DA)]")
        rowlist.append(space.name + "_室MRT[℃]")
        rowlist.append(space.name + "_室作用温度[℃]")
        rowlist.append(space.name + "_透過日射熱取得[W]")
        rowlist.append(space.name + "_機器顕熱発熱[W]")
        rowlist.append(space.name + "_照明発熱[W]")
        rowlist.append(space.name + "_人体顕熱発熱[W]")
        rowlist.append(space.name + "_人体潜熱発熱[W]")
        rowlist.append(space.name + "_対流空調顕熱負荷[W]")
        rowlist.append(space.name + "_放射空調顕熱負荷[W]")
        rowlist.append(space.name + "_対流空調潜熱負荷[W]")
        rowlist.append(space.name + "_家具温度[℃]")
        rowlist.append(space.name + "_家具取得熱量[W]")
        rowlist.append(space.name + "_家具吸収日射熱量[W]")
        rowlist.append(space.name + "_家具絶対湿度[kg/kg(DA)]")
        rowlist.append(space.name + "_家具取得水蒸気量[kg/s]")
        if 1:
            for surface in space.input_surfaces:
                rowlist.append(space.name + "_" + surface.name + "_表面温度[℃]")
        if 1:
            for surface in space.input_surfaces:
                rowlist.append(space.name + "_" + surface.name + "_等価室温[℃]")
        if 1:
            for surface in space.input_surfaces:
                rowlist.append(space.name + "_" + surface.name + "_境界温度[℃]")
        if 1:
            for surface in space.input_surfaces:
                rowlist.append(space.name + "_" + surface.name + "_表面放射熱流[W]")
        if 1:
            for surface in space.input_surfaces:
                rowlist.append(space.name + "_" + surface.name + "_表面対流熱流[W]")
    OutList.append(rowlist)
    rowlist = []

    # 日ループの開始
    for lngNday in range(lngStNday, lngEnNday + 1):
        # 時刻ループの開始
        for lngTloop in range(0, lngNtime):
            dtime = datetime.timedelta(days=lngNnow + float(lngTloop) / float(lngNtime))
            dtmNow = apDate + dtime
            sequence_number = int((get_nday(dtmNow.month, dtmNow.day) - 1) * 24 * 4 + dtmNow.hour * 4 + float(dtmNow.minute) / 60.0 * 3600 / cdata.DTime)

            # 太陽位置の計算
            # print(dtmNow)
            solar_position = Solpos(weather, dtmNow)

            # 気象データの読み込み
            # 法線面直達日射量
            Idn = WeaData(weather, enmWeatherComponent.Idn, dtmNow, solar_position)
            # 水平面天空日射量
            Isky = WeaData(weather, enmWeatherComponent.Isky, dtmNow, solar_position)
            # 外気温度
            Ta = WeaData(weather, enmWeatherComponent.Ta, dtmNow, solar_position)
            # 夜間放射量
            RN = WeaData(weather, enmWeatherComponent.RN, dtmNow, solar_position)
            # 絶対湿度[kg/kg(DA)]
            xo = WeaData(weather, enmWeatherComponent.x, dtmNow, solar_position) / 1000.
            rowlist = []
            # 室温・熱負荷の計算
            if FlgOrig(cdata, dtmNow):
                
                # print(str(dtmNow), end="\t")
                # 出力文字列
                rowlist.append(str(dtmNow))
                rowlist.append('{0:.1f}'.format(Ta))
                rowlist.append('{0:.4f}'.format(xo))
                if lngTloop == 0:
                    print(dtmNow)
            # print(Solpos.Sh, Solpos.Sw, Solpos.Ss)
            for space in spaces.values():
                # 室温、熱負荷の計算
                calcHload(
                    space=space,
                    Gdata=cdata,
                    spaces=spaces,
                    dtmNow=dtmNow,
                    defSolpos=solar_position,
                    Ta=Ta,
                    xo=xo,
                    Idn=Idn,
                    Isky=Isky,
                    RN=RN,
                    annual_average_temperature=weather.AnnualTave
                )
                
                if FlgOrig(cdata, dtmNow):
                    rowlist.append('{0:.0f}'.format(space.nowWin))
                    rowlist.append('{0:.0f}'.format(space.demAC))
                    rowlist.append('{0:.0f}'.format(space.finalAC))
                    rowlist.append('{0:.2f}'.format(space.Tr))
                    rowlist.append('{0:.0f}'.format(space.RH))
                    rowlist.append('{0:.4f}'.format(space.xr))
                    rowlist.append('{0:.2f}'.format(space.MRT))
                    rowlist.append('{0:.2f}'.format(space.OT))
                    rowlist.append('{0:.2f}'.format(space.Qgt[sequence_number]))
                    rowlist.append('{0:.2f}'.format(space.heat_generation_appliances))
                    rowlist.append('{0:.2f}'.format(space.heat_generation_lighting))
                    rowlist.append('{0:.2f}'.format(space.Humans))
                    rowlist.append('{0:.2f}'.format(space.Humanl))
                    # rowlist.append('{0:.2f}'.format(space.Clo))
                    # rowlist.append('{0:.2f}'.format(space.Vel))
                    # rowlist.append('{0:.2f}'.format(space.PMV))
                    rowlist.append('{0:.1f}'.format(space.Lcs))
                    rowlist.append('{0:.1f}'.format(space.Lrs))
                    rowlist.append('{0:.1f}'.format(space.Lcl))
                    rowlist.append('{0:.2f}'.format(space.Tfun))
                    rowlist.append('{0:.1f}'.format(space.Qfuns))
                    rowlist.append('{0:.1f}'.format(space.Qsolfun))
                    rowlist.append('{0:.5f}'.format(space.xf))
                    rowlist.append('{0:.5f}'.format(space.Qfunl))
                    if 1:
                        for surface in space.input_surfaces:
                            rowlist.append('{0:.2f}'.format(surface.Ts))
                    if 1:
                        for surface in space.input_surfaces:
                            rowlist.append('{0:.2f}'.format(surface.Tei))
                    if 1:
                        for surface in space.input_surfaces:
                            rowlist.append('{0:.2f}'.format(surface.Teo))
                    if 1:
                        for surface in space.input_surfaces:
                            rowlist.append('{0:.2f}'.format(surface.Qr))
                    if 1:
                        for surface in space.input_surfaces:
                            rowlist.append('{0:.2f}'.format(surface.Qc))
                    # print('{0:.0f}'.format(space.nowWin), '{0:.0f}'.format(space.nowAC), '{0:.2f}'.format(space.Tr), \
                    #         '{0:.0f}'.format(space.RH), '{0:.2f}'.format(space.MRT), '{0:.2f}'.format(space.PMV), \
                    #         '{0:.0f}'.format(space.Lcs), '{0:.0f}'.format(space.Lr), '{0:.0f}'.format(space.Ll), "", end="")
            
            if FlgOrig(cdata, dtmNow):
                OutList.append(rowlist)
                # print("")

            # 前時刻の室温を現在時刻の室温、湿度に置換
            for space in spaces.values():
                update_space_oldstate(space)

        lngNnow += 1

    # CSVファイルの出力
    f = open('simulatin_result.csv', 'w', encoding="utf_8_sig")
    dataWriter = csv.writer(f, lineterminator='\n')
    dataWriter.writerows(OutList)
    f.close()

if __name__ == '__main__':

    # OT = get_OT(1.0, 1.0, 0.15, 50.0, 0.0)
    # print(OT)

    # js = open('1RCase1_最初の外壁削除.json', 'r', encoding='utf-8')
    # js = open('input_non_residential.json', 'r', encoding='utf-8')
    js = open('input_residential.json', 'r', encoding='utf-8')
    # js = open('input_simple_residential.json', 'r', encoding='utf-8')
    # js = open('検証用.json', 'r', encoding='utf-8')
    d = json.load(js)

    # シミュレーション全体の設定条件の読み込み
    cdata = Gdata(**d['common'])

    # 気象データの読み込み
    weather = Weather(cdata.Latitude, cdata.Longitude, cdata.StMeridian)

    # 外表面の初期化
    # exsurfaces = create_exsurfaces(d['ExSurface'])

    # 外部日除けクラスの初期化
    # sunbrks = create_sunbrks(d['Sunbrk'])

    # スペースの読み取り
    spaces = create_spaces(cdata, d['rooms'], weather)

    # スケジュールの初期化
    # schedule = Schedule()

    # 熱負荷計算の実行
    calc_Hload(cdata, weather)
