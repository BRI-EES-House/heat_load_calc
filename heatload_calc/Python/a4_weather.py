import csv
from enum import IntEnum
import datetime
import math
from functools import lru_cache
import numpy as np

"""
付録4．気象データの補間方法
"""


# 気象データの補間
def interpolate(weatherdata: np.ndarray) -> np.ndarray:

    # 補間比率の係数(1時間分4点)  式(56)
    alpha = np.array([1.0, 0.75, 0.5, 0.25])

    # 補間元データ1, 補間元データ2
    data1 = np.roll(weatherdata, 1)     #0時=24時のため、1回分前のデータを参照
    data2 = weatherdata

    # 直線補完 8760×4 の2次元配列 式(55)相当
    data_interp_2d = alpha[np.newaxis, :] * data1[:, np.newaxis] + (1.0 - alpha[np.newaxis, :]) * data2[:, np.newaxis]

    # 1次元配列へ変換
    data_interp_1d = np.reshape(data_interp_2d, (24 * 365 * 4))

    return data_interp_1d


# 気象データの読み込み
def load_weatherdata(region: int) -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray):
    if region == 1:
        # 1地域（北見）
        weatherdata_filename = '1_Kitami.csv'
    elif region == 2:
        # 2地域（岩見沢）
        weatherdata_filename = '2_Iwamizawa.csv'
    elif region == 3:
        # 3地域（盛岡）
        weatherdata_filename = '3_Morioka.csv'
    elif region == 4:
        # 4地域（長野）
        weatherdata_filename = '4_Nagano.csv'
    elif region == 5:
        # 5地域（宇都宮）
        weatherdata_filename = '5_Utsunomiya.csv'
    elif region == 6:
        # 6地域（岡山）
        weatherdata_filename = '6_Okayama.csv'
    elif region == 7:
        # 7地域（宮崎）
        weatherdata_filename = '7_Miyazaki.csv'
    elif region == 8:
        # 8地域（那覇）
        weatherdata_filename = '8_Naha.csv'
    else:
        raise ValueError(region)

    # ファイル読み込み
    path_and_filename = "weather_data\\" + weatherdata_filename
    data = np.loadtxt(path_and_filename, delimiter=",", skiprows=2, usecols=(2, 3, 4, 5, 6), encoding="utf-8")

    # 扱いにくいので転地
    weather = data.T

    # n時点における外気温度[℃]
    To_n = interpolate(weather[0])

    # n時点における法線面直達日射量[W/m2]
    I_DN_n = interpolate(weather[1])

    # n時点における水平面天空日射量[W/m2]
    I_sky_n = interpolate(weather[2])

    # n時点における夜間放射量[W/m2]
    RN_n = interpolate(weather[3])

    # n時点における外気絶対湿度[g/kg']
    xo_n = interpolate(weather[4]) / 1000.

    return To_n, I_DN_n, I_sky_n, RN_n, xo_n
