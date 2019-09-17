import csv
import datetime
import json
import common
from common import get_nday
from Gdata import Gdata, is_actual_calc
from a4_weather import enmWeatherComponent, Weather, WeaData
from Space import create_spaces
from heat_load import calcHload
import apdx5_solar_position as a5
import numpy as np
# from apdx6_direction_cos_incident_angle import calc_cos_incident_angle
# from rear_surface_equivalent_temperature import precalcTeo

# 熱負荷計算の実行
def calc_Hload(cdata, weather, solar_position):
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
    lngNtime = int(24 * 3600 / 900)

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
        rowlist.append(space.name + "_PMV[-]")
        rowlist.append(space.name + "_着衣量[clo]")
        rowlist.append(space.name + "_風速[m/s]")
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
            for g in range(space.surfG_i.NsurfG_i):
                rowlist.append(space.name + "_" + space.surfG_i.name[g] + "_表面温度[℃]")
        if 1:
            for g in range(space.surfG_i.NsurfG_i):
                rowlist.append(space.name + "_" + space.surfG_i.name[g] + "_等価室温[℃]")
        if 1:
            for g in range(space.surfG_i.NsurfG_i):
                rowlist.append(space.name + "_" + space.surfG_i.name[g] + "_境界温度[℃]")
        if 1:
            for g in range(space.surfG_i.NsurfG_i):
                rowlist.append(space.name + "_" + space.surfG_i.name[g] + "_表面放射熱流[W]")
        if 1:
            for g in range(space.surfG_i.NsurfG_i):
                rowlist.append(space.name + "_" + space.surfG_i.name[g] + "_表面対流熱流[W]")
    OutList.append(rowlist)
    rowlist = []

    #太陽位置を計算する
    solar_position = a5.calc_solar_position(region=region)

    outdoor_temp_list = np.zeros(8760*4)
    outdoor_humid_list = np.zeros(8760*4)

    # 予備計算（気象データの読み込み）
    for lngNday in range(common.get_nday(cdata.StDate.month, cdata.StDate.day), lngEnNday + 1):
        # 時刻ループ
        for lngTloop in range(lngNtime):
            dtime = datetime.timedelta(days=lngNnow + float(lngTloop) / float(lngNtime))
            dtmNow = apDate + dtime
            n = int((get_nday(dtmNow.month, dtmNow.day) - 1) * 24 * 4 + dtmNow.hour * 4 + float(dtmNow.minute) / 60.0 * 3600 / 900)

            # 太陽位置の計算
            # print(dtmNow)
            # 外気温度の補間、Listへの追加
            outdoor_temp_list[n] = WeaData(weather, enmWeatherComponent.To, dtmNow, solar_position, n)
            # 外気絶対湿度の補間、Listへの追加
            outdoor_humid_list[n] = WeaData(weather, enmWeatherComponent.x, dtmNow, solar_position, n) / 1000.

    # 日ループの開始
    for lngNday in range(lngStNday, lngEnNday + 1):
        # 時刻ループの開始
        for lngTloop in range(0, lngNtime):
            dtime = datetime.timedelta(days=lngNnow + float(lngTloop) / float(lngNtime))
            dtmNow = apDate + dtime
            n = int((get_nday(dtmNow.month, dtmNow.day) - 1) * 24 * 4 + dtmNow.hour * 4 + float(dtmNow.minute) / 60.0 * 3600 / 900)

            rowlist = []
            # 室温・熱負荷の計算
            if is_actual_calc(cdata, dtmNow):
                
                # print(str(dtmNow), end="\t")
                # 出力文字列
                rowlist.append(str(dtmNow))
                rowlist.append('{0:.1f}'.format(outdoor_temp_list[n]))
                rowlist.append('{0:.4f}'.format(outdoor_humid_list[n]))
                if lngTloop == 0:
                    print(dtmNow)
            # print(calc_solar_position.Sh, calc_solar_position.Sw, calc_solar_position.Ss)
            for space in spaces.values():
                # 室温、熱負荷の計算
                calcHload(
                    space=space,
                    is_actual_calc=is_actual_calc(cdata, dtmNow),
                    spaces=spaces,
                    dtmNow=dtmNow,
                    To_n=outdoor_temp_list[n],
                    xo=outdoor_humid_list[n],
                    n=n
                )
                
                if is_actual_calc(cdata, dtmNow):
                    rowlist.append(space.is_now_window_open)
                    rowlist.append(space.air_conditioning_demand)
                    rowlist.append('{0:.0f}'.format(space.now_air_conditioning_mode))
                    rowlist.append('{0:.2f}'.format(space.Tr_i_n[n]))
                    rowlist.append('{0:.0f}'.format(space.RH_i_n[n]))
                    rowlist.append('{0:.4f}'.format(space.xr_i_n[n]))
                    rowlist.append('{0:.2f}'.format(space.MRT_i_n[n]))
                    rowlist.append('{0:.2f}'.format(space.OT_i_n[n]))
                    rowlist.append('{0:.2f}'.format(space.PMV_i_n[n]))
                    rowlist.append('{0:.2f}'.format(space.Clo_i_n[n]))
                    rowlist.append('{0:.2f}'.format(space.Vel_i_n[n]))
                    rowlist.append('{0:.2f}'.format(space.QGT_i_n[n]))
                    rowlist.append('{0:.2f}'.format(space.heat_generation_appliances))
                    rowlist.append('{0:.2f}'.format(space.heat_generation_lighting))
                    rowlist.append('{0:.2f}'.format(space.Humans))
                    rowlist.append('{0:.2f}'.format(space.Humanl))
                    rowlist.append('{0:.1f}'.format(space.Lcs_i_n[n]))
                    rowlist.append('{0:.1f}'.format(space.Lrs_i_n[n]))
                    rowlist.append('{0:.1f}'.format(space.Lcl_i_n[n]))
                    rowlist.append('{0:.2f}'.format(space.Tfun_i_n[n]))
                    rowlist.append('{0:.1f}'.format(space.Qfuns_i_n[n]))
                    rowlist.append('{0:.1f}'.format(space.Qsolfun_i_n[n]))
                    rowlist.append('{0:.5f}'.format(space.xf_i_n[n]))
                    rowlist.append('{0:.5f}'.format(space.Qfunl_i_n[n]))
                    if 1:
                        for g in range(space.surfG_i.NsurfG_i):
                            rowlist.append('{0:.2f}'.format(space.Ts_i_k_n[g, n]))
                    if 1:
                        for g in range(space.surfG_i.NsurfG_i):
                            rowlist.append('{0:.2f}'.format(space.Tei_i_k_n[g, n]))
                    if 1:
                        for g in range(space.surfG_i.NsurfG_i):
                            rowlist.append('{0:.2f}'.format(space.Teo_i_k_n[g, n]))
                    if 1:
                        for g in range(space.surfG_i.NsurfG_i):
                            rowlist.append('{0:.2f}'.format(space.Qr[g]))
                    if 1:
                        for g in range(space.surfG_i.NsurfG_i):
                            rowlist.append('{0:.2f}'.format(space.Qc[g]))
                    # print('{0:.0f}'.format(space.is_now_window_open), '{0:.0f}'.format(space.nowAC), '{0:.2f}'.format(space.Tr), \
                    #         '{0:.0f}'.format(space.RH), '{0:.2f}'.format(space.MRT_i_n), '{0:.2f}'.format(space.PMV_i_n), \
                    #         '{0:.0f}'.format(space.Lcs), '{0:.0f}'.format(space.Lr), '{0:.0f}'.format(space.Ll), "", end="")
            
            if is_actual_calc(cdata, dtmNow):
                OutList.append(rowlist)
                # print("")

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

    # 地域の区分
    region = d['common']['region']

    # シミュレーション全体の設定条件の読み込み
    cdata = Gdata(**d['common'])

    # 気象データの読み込み
    weather = Weather()

    # 太陽位置は個別計算可能
    solar_position = a5.calc_solar_position(region=region)

    # スペースの読み取り
    spaces = create_spaces(d['rooms'], weather, solar_position)

    # 熱負荷計算の実行
    calc_Hload(cdata, weather, solar_position)
