import csv
from enum import IntEnum
import datetime
import math

from functools import lru_cache
import numpy as np
import a36_region_location as a36

"""
付録4．気象データの補間方法
"""

class enmWeatherComponent(IntEnum):
    To = 2  # 外気温度[℃]
    x = 6  # 絶対湿度[g/kg']
    I_DN = 3  # 法線面直辰日射量[W/m2]
    I_sky = 4  # 水平面天空日射量[W/m2]
    RN = 5  # 夜間放射量[W/m2]
    Ihol = 7  # 水平面全天日射量[W/m2]
    h = 8  # 太陽高度[rad]
    A = 9  # 太陽方位角[rad]


# 毎時気象データの所得
class Weather:

    # 気象データの取得
    def __init__(self):
        """
        :param Lat: 緯度
        :param Lon: 軽度
        :param Ls: 標準子午線
        """

        # 年平均気温
        self.AnnualTave = 0.0

        # 気象データの読み込み　→　dblWdata
        with open('weatherdata.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            _ = next(reader)
            _ = next(reader)
            day = 1
            time = 1

            # -----------------------------------------------------------------------------
            # データの形がVBAと違うことに注意！
            # VBAでは、dbl[5][365][24]の3次元配列。(VBなので1始まりであることに注意。)
            # ここでは、列1にday,列2にtime、列3～列7に5データを持つ2次元配列であることに注意。
            # -----------------------------------------------------------------------------

            self.dblWdata = []
            for row in reader:
                # データ自身は全部で7項目(温度、法線面直達日射量、水平面全天日射量、夜間放射量、絶対湿度)
                # このうち、VBAでは、夜間放射量と絶対湿度は捨てているので、VBAどおり、5データのみデータ化する。
                # time は、1始まりであることに注意。
                Col = 2
                # 外気温度
                Ta = float(row[Col])
                # 年平均気温の計算
                self.AnnualTave += Ta / 8760.0

                Col += 1
                # 法線面直達日射量
                Idn = float(row[Col])
                Col += 1
                # 水平面天空日射量
                Isky = float(row[Col])
                Col += 1
                # 夜間放射量
                RN = float(row[Col])
                Col += 1
                # 絶対湿度
                x = float(row[Col])
                Col += 1
                self.dblWdata.append([day, time, Ta, Idn, Isky, RN, x])
                time += 1
                if time > 24:
                    time = 1
                    day += 1

            self.dblWdata = np.array(self.dblWdata)

# 気象データの取得
# 戻り値はdouble
def WeaData(weatherdata: Weather, Compnt: enmWeatherComponent, dtmDate: datetime, solar_position, item:int) -> float :
    # Compnt:取得する気象要素
    # dtmDate:取得する日時
    # blnLinear:線形補間するかどうか（Trueは線形補間する）
    # print('WeaData')
    # 通日、時、分、秒の取得
    lngAddress = Address(dtmDate)
    lngMinu = dtmDate.minute
    lngSec = dtmDate.second

    # 線形補間時の案分比
    dblR = lngMinu / 60. + lngSec / 3600.

    # 1時間後のアドレスを取得
    lngAddress2 = Address(dtmDate + datetime.timedelta(hours=1))

    # print('h=', sp.h, 'A=', sp.A)
    # print(self.dblWdata)
    # aa =  self.dblWdata[0]
    # print(aa)
    # 水平面全天日射量、地面反射日射量の場合
    if Compnt == enmWeatherComponent.Ihol:
        # 正時に切り捨てた時の気象データを取得
        wdata1 = weatherdata.dblWdata[lngAddress]
        dblIdn1 = wdata1[int(enmWeatherComponent.I_DN)]
        dblIsky1 = wdata1[int(enmWeatherComponent.I_sky)]
        # 1時間後の気象要素を取得
        wdata2 = weatherdata.dblWdata[lngAddress2]
        dblIdn2 = wdata2[int(enmWeatherComponent.I_DN)]
        dblIsky2 = wdata2[int(enmWeatherComponent.I_sky)]

        # 直線補間
        dblIdn = (1. - dblR) * dblIdn1 + dblR * dblIdn2
        dblIsky = (1. - dblR) * dblIsky1 + dblR * dblIsky2
        return solar_position.Sh[item] * dblIdn + dblIsky
    # 太陽高度の場合
    elif Compnt == enmWeatherComponent.h:
        return solar_position.h[item]
    # 太陽方位角の場合
    elif Compnt == enmWeatherComponent.A:
        return solar_position.A[item]
    # 上記以外の場合
    else:
        # 正時に切り捨てた時の気象データを取得
        wdata1 = weatherdata.dblWdata[lngAddress]
        dblTemp1 = wdata1[int(Compnt)]
        # 1時間後の気象要素を取得
        wdata2 = weatherdata.dblWdata[lngAddress2]
        dblTemp2 = wdata2[int(Compnt)]

        # print(a_i_g, dblTemp1, dblTemp2)
        # 直線補完
        return (1. - dblR) * dblTemp1 + dblR * dblTemp2


# 計算日時のリストを生成する（正確にはタプル)
@lru_cache(maxsize = None)
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


# Date型日時から取得する通日、時刻アドレスを計算する
# 0時を24時に変換するため
# 補間は行わない
def Address(dtmDate: datetime) -> int:
    # dtmDate は、datetime オブジェクトとする。
    lngHour = dtmDate.hour
    # 1月1日から数えて何日目にあたるのかを計算する。
    lngNday = (datetime.date(1989, dtmDate.month, dtmDate.day) - datetime.date(1989, 1, 1)).days + 1
    if lngHour == 0:
        lngNday = lngNday - 1
        lngHour = 24
    if lngNday == 0:
        lngNday = 365
    return (lngNday - 1) * 24 + lngHour - 1
