import pandas as pd
import numpy as np


def hasp_read(file_name: str) -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray):
    '''
    HASP形式のテキストファイル（utf-8）から気温、絶対湿度、法線面直達日射量、水平面天空日射量、夜間放射量、風向、風速を読み込む
    Args:
        file_name: HASP形式のファイル名（3カラムのSI形式）

    Returns:
        気温, C
        絶対湿度, kg/kg(DA)
        法線面直達日射量, W/m2
        水平面天空日射量, W/m2
        夜間放射量, W/m2
        風向, -
        風速, m/s
    '''

    # 区切り文字数
    column_width = [3] * 24
    # 年、月、日、曜日、気象要素番号
    column_width += [2, 2, 2, 1, 1]

    # テキストファイルを読み込み
    weather_data_pd = pd.read_fwf(
        filepath_or_buffer=file_name,
        widths=column_width,
        header=None
    )

    # 外気温度
    ta_data = get_element(weather_data_pd, 0)
    # 換算し端数処理
    ta_data = np.round((ta_data - 500.0) * 0.1, decimals=1)

    # 絶対湿度
    xa_data = get_element(weather_data_pd, 1)
    xa_data = np.round(xa_data * 0.0001, decimals=4)

    # 法線面直達日射量
    idn_data = get_element(weather_data_pd, 2)
    idn_data = np.round(idn_data * (0.01 * 1.0e6 / 3600.0), decimals=0)

    # 水平面天空日射量
    isky_data = get_element(weather_data_pd, 3)
    isky_data = np.round(isky_data * (0.01 * 1.0e6 / 3600.0), decimals=0)

    # 夜間放射量
    rn_data = get_element(weather_data_pd, 4)
    rn_data = np.round(rn_data * (0.01 * 1.0e6 / 3600.0), decimals=0)

    # 風向
    wdre_data = get_element(weather_data_pd, 5)

    # 風速
    wv_data = get_element(weather_data_pd, 6)
    wv_data = np.round(wv_data * 0.1, decimals=1)

    return (ta_data, xa_data, idn_data, isky_data, rn_data, wdre_data, wv_data)


def get_element(weather_pd: pd, row_number: int) -> np.ndarray:
    '''
    7行置きにデータを抽出し、１行に連結させたのちにnumpy配列として返す
    Args:
        weather_pd: 気象データを読み込んだPandas
        row_number: シフト行　0:気温、1:絶対湿度、2:法線面直達日射量、3:水平面天空日射量、4:夜間放射量、5:風向、6:風速

    Returns:
        8760時間分の気象要素（ただし、換算はしていない）
    '''

    # row_numberだけシフトし7行置きにデータを抽出
    element_data = weather_pd[row_number::7]
    # 余計な列を削除（年、月、日、曜日、気象要素番号）
    # TODO: ワーニングが発生する（A value is trying to be set on a copy of a slice from a DataFrame）
    element_data.drop(element_data.columns[[24, 25, 26, 27, 28]], axis=1, inplace=True)
    # 1行のNumpyに変換する
    element_data_np = element_data.values.flatten()

    # 実数型に変換
    return element_data_np.astype('float')


if __name__ == '__main__':

    (ta, xa, idn, isky, rn, wdre, wv) = hasp_read('expanded_amedas/tokyo_3column_SI.has')

    print(ta[0])
