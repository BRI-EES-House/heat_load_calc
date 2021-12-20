import pandas as pd

from heat_load_calc.weather import weather_data
from heat_load_calc.weather import region_location
from heat_load_calc.weather import solar_position
from heat_load_calc.weather.interval import Interval


def make_weather(region: int, interval: str = '15m'):
    """
    気象データを作成する。
    Args:
        region: 地域の区分
        output_data_dir: 気象データを出力するディレクトリ名
        csv_output: 気象データの出力の有無
        interval: 生成するデータの時間間隔であり、以下の文字列で指定する。（デフォルト値は'15m'）
            1h: 1時間間隔
            30m: 30分間隔
            15m: 15分間隔
    Returns:
        作成された気象データ（pandas DataFrame 形式）
    Notes:
        csv_output が True のときのみ、 output_data_dir を指定する。
        output_data_dir で指定したディレクトリは実行ファイルがあるフォルダ内に作成される。
    """

    # 時間間隔を列挙体に変換する
    _interval = Interval(interval)

    # 気象データの読み込み
    #   (1)ステップnにおける外気温度, degree C [n]
    #   (2)ステップnにおける法線面直達日射量, W/m2 [n]
    #   (3)ステップnにおける水平面天空日射量, W/m2 [n]
    #   (4)ステップnにおける夜間放射量, W/m2 [n]
    #   (5)ステップnにおける外気絶対湿度, kg/kgDA [n]
    # インターバルごとの要素数について
    #   interval = '1h' -> n = 8760
    #   interval = '30m' -> n = 8760 * 2
    #   interval = '15m' -> n = 8760 * 4
    theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns = weather_data.load(region=region, interval=_interval)

    # 緯度, rad & 経度, rad
    phi_loc, lambda_loc = region_location.get_phi_loc_and_lambda_loc(region=region)

    # 太陽位置
    #   (1) ステップnにおける太陽高度, rad [n]
    #   (2) ステップnにおける太陽方位角, rad [n]
    h_sun_ns, a_sun_ns = solar_position.calc_solar_position(phi_loc=phi_loc, lambda_loc=lambda_loc, interval=_interval)

    # インターバル指定文字をpandasのfreq引数に文字変換する。
    freq = {
        Interval.M15: '15min',
        Interval.M30: '30min',
        Interval.H1: 'H'
    }[_interval]

    # 1時間を何分割するのかを取得する。
    n_hour = _interval.get_n_hour()

    # 時系列インデクスの作成
    dd = pd.DataFrame(index=pd.date_range(start='1/1/1989', periods=8760*n_hour, freq=freq))

    dd['temperature'] = theta_o_ns.round(3)
    dd['absolute humidity'] = x_o_ns.round(6)
    dd['normal direct solar radiation'] = i_dn_ns
    dd['horizontal sky solar radiation'] = i_sky_ns
    dd['outward radiation'] = r_n_ns
    dd['sun altitude'] = h_sun_ns
    dd['sun azimuth'] = a_sun_ns

    return dd
