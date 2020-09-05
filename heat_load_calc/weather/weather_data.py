# 附属書X4 気象データの取得と15分間隔のデータへの補間方法
# 地域の区分に応じて1時間ごとに定義される気象データ（8760データ）と、
# そのデータを15分間隔のデータに補間する方法について説明する。

import numpy as np
import os


def load(region: int) -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray):
    """
    地域の区分に応じて気象データを読み込む。

    Args:
        region: 地域の区分

    Returns:
        以下の5項目
            (1) ステップnにおける外気温度, ℃ [8760*4]
            (2) ステップnにおける法線面直達日射量, W/m2 [8760*4]
            (3) ステップnにおける水平面天空日射量, W/m2 [8760*4]
            (4) ステップnにおける夜間放射量, W/m2 [8760*4]
            (5) ステップnにおける外気絶対湿度, g/kgDA [8760*4]
    """

    # 地域の区分に応じたファイル名の取得
    weather_data_filename = get_filename(region)

    # ファイル読み込み
    path_and_filename = str(os.path.dirname(__file__)) + '/expanded_amedas/' + weather_data_filename

    data = np.loadtxt(path_and_filename, delimiter=",", skiprows=2, usecols=(2, 3, 4, 5, 6), encoding="utf-8")

    # 扱いにくいので転地（列：項目・行：時刻　→　列：時刻・行：項目
    # [5項目, 8760データ]
    # [8760, 5] -> [5, 8760]
    weather = data.T

    # ステップnにおける外気温度, ℃
    theta_o_ns = interpolate(weather[0])

    # ステップnにおける法線面直達日射量, W/m2
    i_dn_ns = interpolate(weather[1])

    # ステップnにおける水平面天空日射量, W/m2
    i_sky_ns = interpolate(weather[2])

    # ステップnにおける夜間放射量, W/m2
    r_n_ns = interpolate(weather[3])

    # ステップnにおける外気絶対湿度, kg/kgDA
    # g/kgDA から kg/kgDA へ単位変換を行う。
    x_o_ns = interpolate(weather[4]) / 1000.

    return theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns


def interpolate(weather_data: np.ndarray) -> np.ndarray:
    """
    1時間ごとの8760データを15分間隔の8760✕4のデータに補間する。

    Args:
        weather_data: 1時間ごとの気象データ [8760]

    Returns:
        15分間隔に補間された気象データ [8760*4]
    """

    # 補間比率の係数(1時間分4点)  式(56)
    alpha = np.array([1.0, 0.75, 0.5, 0.25])

    # 補間元データ1, 補間元データ2
    # 拡張アメダスのデータが1月1日の1時から始まっているため1時間ずらして0時始まりのデータに修正する。
    data1 = np.roll(weather_data, 1)     # 0時=24時のため、1回分前のデータを参照
    data2 = weather_data

    # 直線補完 8760×4 の2次元配列
    data_interp_2d = alpha[np.newaxis, :] * data1[:, np.newaxis] + (1.0 - alpha[np.newaxis, :]) * data2[:, np.newaxis]

    # 1次元配列へ変換
    data_interp_1d = data_interp_2d.flatten()

    return data_interp_1d


def get_filename(region: int) -> str:
    """
    地域の区分に応じたファイル名を取得する。

    Args:
        region: 地域の区分

    Returns:
        地域の区分に応じたファイル名（CSVファイル）（拡張子も含む）
    """

    weather_data_filename = {
        1: '01_kitami.csv',  # 1地域（北見）
        2: '02_iwamizawa.csv',  # 2地域（岩見沢）
        3: '03_morioka.csv',  # 3地域（盛岡）
        4: '04_nagano.csv',  # 4地域（長野）
        5: '05_utsunomiya.csv',  # 5地域（宇都宮）
        6: '06_okayama.csv',  # 6地域（岡山）
        7: '07_miyazaki.csv',  # 7地域（宮崎）
        8: '08_naha.csv'  # 8地域（那覇）
    }[region]

    return weather_data_filename
