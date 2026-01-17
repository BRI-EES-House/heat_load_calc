import numpy as np
import pandas as pd
import os
import logging
from typing import Tuple, Dict
import math

from heat_load_calc import solar_position
from heat_load_calc.interval import Interval
from heat_load_calc.region import Region

logger = logging.getLogger(name='HeatLoadCalc').getChild('Weather')


class Weather:

    def __init__(
            self,
            a_sun_ns: np.ndarray,
            h_sun_ns: np.ndarray,
            i_dn_ns: np.ndarray,
            i_sky_ns: np.ndarray,
            r_n_ns: np.ndarray,
            theta_o_ns: np.ndarray,
            x_o_ns: np.ndarray,
            itv: Interval = Interval.M15
    ):
        """

        Args:
            a_sun_ns: solar direction at step n, ステップnにおける太陽方位角, rad, [N]
            h_sun_ns: solar altitude at step n, ステップnにおける太陽高度, rad, [N]
            i_dn_ns: normal surface direct solar radiation at step n, ステップnにおける法線面直達日射量, W/m2, [N]
            i_sky_ns: horizontal sky solar radiation at step n, ステップnにおける水平面天空日射量, W/m2, [N]
            r_n_ns: nighttime radiation at step n, ステップnにおける夜間放射量, W/m2, [N]
            theta_o_ns: outside temperature at step n, ステップnにおける外気温度, degree C, [N]
            x_o_ns: outside absolute humidity at step n, ステップnにおける外気絶対湿度, kg/kg(DA), [N]
            itv: interval class
        """

        if a_sun_ns.size != itv.get_n_step_annual():
            raise ValueError('The length of a_sun_ns array does not match the number of the annual steps.')
        if h_sun_ns.size != itv.get_n_step_annual():
            raise ValueError('The length of h_sun_ns array does not match the number of the annual steps.')
        if i_dn_ns.size != itv.get_n_step_annual():
            raise ValueError('The length of i_dn_ns array does not match the numeber of the annual steps.')
        if i_sky_ns.size != itv.get_n_step_annual():
            raise ValueError('The length of i_sky_ns array does not match the numeber of the annual steps.')
        if r_n_ns.size != itv.get_n_step_annual():
            raise ValueError('The length of r_n_ns array does not match the numeber of the annual steps.')
        if theta_o_ns.size != itv.get_n_step_annual():
            raise ValueError('The length of theta_o_ns array does not match the numeber of the annual steps.')
        if x_o_ns.size != itv.get_n_step_annual():
            raise ValueError('The length of x_o_ns array does not match the numeber of the annual steps.')

        self._a_sun_ns = a_sun_ns
        self._h_sun_ns = h_sun_ns
        self._i_dn_ns = i_dn_ns
        self._i_sky_ns = i_sky_ns
        self._r_n_ns = r_n_ns
        self._theta_o_ns = theta_o_ns
        self._x_o_ns = x_o_ns

        self._itv = itv

        # the number of data
        self._number_of_data = itv.get_n_step_annual()

    @classmethod
    def make_weather(cls, d_common: Dict, itv: Interval, entry_point_dir: str = ""):

        # Check the existance of the item "weather" in common item.
        if 'weather' not in d_common:
            raise KeyError('Key weather could not be found in common tag.')

        # item "weather"
        d_weather = d_common['weather']

        # Check the existance of the item "method" in weather item.
        if 'method' not in d_weather:
            raise KeyError('Key method could not be found in weather tag.')

        # item "method"
        d_method = d_weather['method']
        
        # The method "ees" is the method that the weather data is loaded from the pre set data based on the region of the Japanese Energy Efficiency Standard.
        if d_method == 'ees':

            # Chech the existance of the item "region" in weather item.
            if 'region' not in d_weather:
                raise KeyError('Key region should be specified if the ees method applied.')

            # item "region"
            region = Region(int(d_weather['region']))

            logger.info('make weather data based on the EES region')

            return _make_weather_ees(region=region, itv=itv)

        elif d_method == 'file':

            # Check the existance of the item "file_path" in weather item.
            if 'file_path' not in d_weather:
                raise KeyError('Key file_path should be specified if the file method applied.')
            
            # Check the existance of the item "latitude" and "longitude" in weather item.
            if 'latitude' not in d_weather:
                raise KeyError('Key latitude should be specified if the file method applied.')
            if 'longitude' not in d_weather:
                raise KeyError('Key longitude should be specified if the file method applied.')

            file_path = os.path.join(entry_point_dir, d_weather['file_path'])

            if not os.path.isfile(file_path):
                raise FileExistsError('The specified file does not exist when file method is applied.')
            
            latitude = float(d_weather['latitude'])
            longitude = float(d_weather['longitude'])

            logger.info('Load weather data from `{}`'.format(file_path))

            return _make_from_pd(file_path=file_path, itv=itv, latitude=latitude, longitude=longitude)

        else:

            raise ValueError('Invalid value is specified for the method.')

    def get_weather_as_pandas_data_frame(self):

        # インターバル指定文字をpandasのfreq引数に文字変換する。
        freq = self._itv.get_pandas_freq()

        # 時系列インデクスの作成
        dd = pd.DataFrame(index=pd.date_range(start='1/1/1989', periods=self._itv.get_n_step_annual(), freq=freq))

        dd['temperature'] = self._theta_o_ns.round(3)
        dd['absolute humidity'] = self._x_o_ns.round(6)
        dd['normal direct solar radiation'] = self._i_dn_ns
        dd['horizontal sky solar radiation'] = self._i_sky_ns
        dd['outward radiation'] = self._r_n_ns
        dd['sun altitude'] = self._h_sun_ns
        dd['sun azimuth'] = self._a_sun_ns

        return dd

    @property
    def a_sun_ns_plus(self) -> np.ndarray:
        """solar direction at step n / ステップnの太陽方位角, rad, [N+1]"""
        return _add_index_0_data_to_end(d=self._a_sun_ns)

    @property
    def h_sun_ns_plus(self) -> np.ndarray:
        """solar altitude at step n / ステップnの太陽高度, rad, [N+1]"""
        return _add_index_0_data_to_end(d=self._h_sun_ns)

    @property
    def i_dn_ns_plus(self) -> np.ndarray:
        """normal surface direct solar radiation at step n / ステップnの法線面直達日射量, W/m2, [N+1]"""
        return _add_index_0_data_to_end(d=self._i_dn_ns)

    @property
    def i_sky_ns_plus(self) -> np.ndarray:
        """horizontal sky solar radiation at step n / ステップnの水平面天空日射量, W/m2, [N+1]"""
        return _add_index_0_data_to_end(d=self._i_sky_ns)

    @property
    def r_n_ns_plus(self) -> np.ndarray:
        """nighttime solar radiation at step n / ステップnの夜間放射量, W/m2, [N+1]"""
        return _add_index_0_data_to_end(d=self._r_n_ns)

    @property
    def theta_o_ns_plus(self) -> np.ndarray:
        """outside temperature at step n / ステップnの外気温度, degree C, [N+1]"""
        return _add_index_0_data_to_end(d=self._theta_o_ns)

    @property
    def x_o_ns_plus(self) -> np.ndarray:
        """outside absolute humidity at step n / ステップnの外気絶対湿度, kg/kg(DA), [N+1]"""
        return _add_index_0_data_to_end(d=self._x_o_ns)

    @property
    def number_of_data(self) -> int:
        """Get the number of the data. / データの数を取得する。
        
        Returns:
            number of the data / データの数
        """

        return self._number_of_data
    
    @property
    def number_of_data_plus(self) -> int:
        """Get the number of the data added one. / データの数に1を足したものを取得する。
        例えば、1時間間隔の場合、データの数は8760なので、返す値は8761
        15分間隔の場合、データの数は35040なので、返す値は35041
        Returns:
            the number of the data added one / データの数に1を足したもの
        """

        return self.number_of_data + 1
    
    @property
    def theta_o_h(self) -> np.ndarray:
        """Outside hourly temperature, deg. C, [8760]"""
        
        n_hour = self._itv.get_n_hour()

        return self._theta_o_ns[::n_hour]

    @property
    def theta_o_h_plus(self) -> np.ndarray:
        """Outside hourly temperature, deg. C, [8761]"""
        
        return _add_index_0_data_to_end(d=self.theta_o_h)

    @property
    def theta_o_ave_d(self) -> np.ndarray:
        """Daily average outside temperature, deg. C, [365]"""
        return self.theta_o_h.reshape(365, 24).mean(axis=1)
    
    @property
    def theta_o_max_d(self) -> np.ndarray:
        """Daily maximum outside temperature, deg. C, [365]"""
        return self.theta_o_h.reshape(365, 24).max(axis=1)

    def get_theta_o_ave(self) -> float:
        """Get the annual average outside temperature. / 外気温度の年間平均値を取得する。

        Returns:
            annual average outside temperature / 外気温度の年間平均値, degree C
        """

        return np.average(self._theta_o_ns)


def _add_index_0_data_to_end(d: np.ndarray) -> np.ndarray:
    """ Add the first data to the end of the list. / リストの最後に一番最初のデータを追加する。

    Args:
        d: list / リスト

    Returns:
        added list / 追加されたリスト
    """

    return np.append(d, d[0])


def _make_from_pd(file_path, itv: Interval, latitude: float, longitude: float) -> Weather:
    """Read the weather data from the specified file. / 気象データを読み込む。

    Args:
        file_path: the file path of the weather data / 気象データのファイルのパス
        itv: interval, Interval 列挙体
        latitude: latitude / 緯度（北緯）, degree
        longitude: longitude / 経度（東経）, degree
    Returns:
        Weather class
    """

    if not os.path.isfile(file_path):
        raise FileNotFoundError("Error: File {} is not exist.".format(file_path))

    pp = pd.read_csv(file_path)

    if not len(pp) == 8760:
        raise Exception("Error: Row length of the file should be 8760.")

    phi_loc, lambda_loc = math.radians(latitude), math.radians(longitude)

    # solar position / 太陽位置
    #   (1) solar altitude at step n / 太陽高度, rad, [N]
    #   (2) solar direction at step n, rad / 太陽方位角, [N]
    h_sun_ns, a_sun_ns = solar_position.calc_solar_position(phi_loc=phi_loc, lambda_loc=lambda_loc, interval=itv)

    # outside temperature at step n / ステップnにおける外気温度, degree C, [N]
    theta_o_ns = _interpolate(weather_data=pp['temperature'].values, interval=itv, rolling=False)

    # outside absolute humidity at step n / ステップnにおける外気絶対湿度, kg / kg(DA), [N]
    # Convert to the unit kg / kg(DA) because the unit in file is g / kg(DA)
    # g/kgDA から kg/kgDA へ単位変換を行う。
    x_o_ns = _interpolate(weather_data=pp['absolute humidity'].values, interval=itv, rolling=False) / 1000.0

    # normal surface direct solar radiation at step n / ステップnにおける法線面直達日射量, W / m2, [N]
    i_dn_ns = _interpolate(weather_data=pp['normal direct solar radiation'].values, interval=itv, rolling=False)

    # horizontal sky solar radiation at step n / ステップnにおける水平面天空日射量, W / m2, [N]
    i_sky_ns = _interpolate(weather_data=pp['horizontal sky solar radiation'].values, interval=itv, rolling=False)

    # nighttime radiation at step n / ステップnにおける夜間放射量, W / m2, [N]
    r_n_ns = _interpolate(weather_data=pp['outward radiation'].values, interval=itv, rolling=False)

    return Weather(
        a_sun_ns=a_sun_ns,
        h_sun_ns=h_sun_ns,
        i_dn_ns=i_dn_ns,
        i_sky_ns=i_sky_ns,
        r_n_ns=r_n_ns,
        theta_o_ns=theta_o_ns,
        x_o_ns=x_o_ns,
        itv=itv
    )


def _make_weather_ees(region: Region, itv: Interval) -> Weather:
    """Make the climate data. / 気象データを作成する。

    Args:
        region: region of ees / 地域の区分
        itv: Interval 列挙体
    Returns:
        Weather Class
    """

    # Load the climate data.
    #   (1) outside temperature at step n / ステップnにおける外気温度, degree C, [N]
    #   (2) normal surface direct solar radiation at step n / ステップnにおける法線面直達日射量, W / m2, [N]
    #   (3) horizontal sky solar radiation at step n / ステップnにおける水平面天空日射量, W / m2, [N]
    #   (4) nighttime radiation at step n / ステップnにおける夜間放射量, W / m2, [N]
    #   (5) outside absolute humidity at step n / ステップnにおける外気絶対湿度, kg / kg(DA), [N]
    # The number of items. / 要素数について
    #   interval = '1h' -> n = 8760
    #   interval = '30m' -> n = 8760 * 2
    #   interval = '15m' -> n = 8760 * 4
    theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns = _load(region=region, itv=itv)

    # latitude / 緯度, rad
    # longitude / 経度, rad
    phi_loc, lambda_loc = region.get_phi_loc_and_lambda_loc()

    # solar position / 太陽位置
    #   solar altitude at step n / ステップnにおける太陽高度, rad, [N]
    #   solar azimuth at step n / ステップnにおける太陽方位角, rad, [N]
    h_sun_ns, a_sun_ns = solar_position.calc_solar_position(phi_loc=phi_loc, lambda_loc=lambda_loc, interval=itv)

    return Weather(
        a_sun_ns=a_sun_ns,
        h_sun_ns=h_sun_ns,
        i_dn_ns=i_dn_ns,
        i_sky_ns=i_sky_ns,
        r_n_ns=r_n_ns,
        theta_o_ns=theta_o_ns.round(3),
        x_o_ns=x_o_ns.round(6),
        itv=itv
    )


def _load(region: Region, itv: Interval) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Read the weather data depend on the region and interpolates at specified time intervals to create data. / 地域の区分に応じて気象データを読み込み、指定された時間間隔で補間を行いデータを作成する。

    Args:
        region: 地域の区分
        itv: Interval 列挙体

    Returns:
        (1) outside temperature at step n / ステップnにおける外気温度, degree C, [N]
        (2) normal surface direct solar radiation at step n / ステップnにおける法線面直達日射量, W / m2, [N]
        (3) horizontal sky solar radiation at step n / ステップnにおける水平面天空日射量, W / m2, [N]
        (4) nighttime radiation at step n / ステップnにおける夜間放射量, W / m2, [N]
        (5) outside absolute humidity at step n / ステップnにおける外気絶対湿度, g / kg(DA), [N]

    Notes:
        interval = '1h' -> n = 8760
        interval = '30m' -> n = 8760 * 2
        interval = '15m' -> n = 8760 * 4
    """

    # Get the file name corresponding to the region. / 地域の区分に応じたファイル名の取得する。
    weather_data_filename = _get_filename(region=region)

    # absolute file path
    path_and_filename = str(os.path.dirname(__file__)) + '/expanded_amedas/' + weather_data_filename

    # read the file
    if not os.path.isfile(path_and_filename):
        raise FileExistsError('The ees file does not exist.')
    data = np.loadtxt(path_and_filename, delimiter=",", skiprows=2, usecols=(2, 3, 4, 5, 6), encoding="utf-8")

    # 扱いにくいので転地（列：項目・行：時刻　→　列：時刻・行：項目）
    # [5項目, 8760データ]
    # Change of place.
    # [8760, 5] -> [5, 8760]
    weather = data.T

    # outside temperature at step n / ステップnにおける外気温度, degree C, [N]
    theta_o_ns = _interpolate(weather_data=weather[0], interval=itv, rolling=True)

    # normal surface direct solar radiation at step n / ステップnにおける法線面直達日射量, W / m2, [N]
    i_dn_ns = _interpolate(weather_data=weather[1], interval=itv, rolling=True)

    # horizontal sky solar radiation at step n / ステップnにおける水平面天空日射量, W / m2, [N]
    i_sky_ns = _interpolate(weather_data=weather[2], interval=itv, rolling=True)

    # nighttime radiation at step n / ステップnにおける夜間放射量, W / m2, [N]
    r_n_ns = _interpolate(weather_data=weather[3], interval=itv, rolling=True)

    # outside absolute humidity at step n / ステップnにおける外気絶対湿度, kg / kg(DA)
    # Convert to the unit kg / kg(DA) because the unit in file is g / kg(DA)
    # g/kgDA から kg/kgDA へ単位変換を行う。
    x_o_ns = _interpolate(weather_data=weather[4], interval=itv, rolling=True) / 1000.0

    return theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns


def _interpolate(weather_data: np.ndarray, interval: Interval, rolling: bool) -> np.ndarray:
    """Interpolate the hourly 8760 data to the specified interval. / 1時間ごとの8760データを指定された間隔のデータに補間する。
    '1h': 1時間間隔の場合、 n = 8760
    '30m': 30分間隔の場合、 n = 8760 * 2 = 17520
    '15m': 15分間隔の場合、 n = 8760 * 4 = 35040

    Args:
        weather_data: hourly weather data / 1時間ごとの気象データ, [8760]
        interval: interval / 時間間隔
        rolling: is rolling? / rolling するか否か。
            If the data starts at 1:00, this value should be TRUE in order to move the data at 24:00 in 12/31 to 1/1 0:00.
            データが1時始まりの場合は最終行の 12/31 24:00 のデータを 1/1 0:00 に持ってくるため、この値は True にすること。

    Returns:
        interpolated weather data of specified interval / 指定する時間間隔に補間された気象データ, [N]
    
    Notes:
        N is;
            8760 * 1 =  8760 in case of  '1h' / 1時間間隔の場合
            8760 * 2 = 17520 in case of '30m' / 30分間隔の場合 
            8760 * 4 = 35040 in case of '30m' / 15分間隔の場合 
    """

    if interval == Interval.H1:

        if rolling:
            # 拡張アメダスのデータが1月1日の1時から始まっているため1時間ずらして0時始まりのデータに修正する。
            return np.roll(weather_data, 1)
        else:
            return weather_data

    else:

        # 補間比率の係数
        alpha = {
            Interval.M30: np.array([1.0, 0.5]),
            Interval.M15: np.array([1.0, 0.75, 0.5, 0.25])
        }[interval]

        # 補間元データ1, 補間元データ2
        if rolling:
            # 拡張アメダスのデータが1月1日の1時から始まっているため1時間ずらして0時始まりのデータに修正する。
            data1 = np.roll(weather_data, 1)     # 0時=24時のため、1回分前のデータを参照
            data2 = weather_data
        else:
            data1 = weather_data
            data2 = np.roll(weather_data, -1)

        # Interporats. / 直線補完 2 dimentional array [2, 8760] or [4, 8760]
        data_interp_2d = alpha[np.newaxis, :] * data1[:, np.newaxis] + (1.0 - alpha[np.newaxis, :]) * data2[:, np.newaxis]

        # Convert 2 dim to 1 dim. / 2次元配列を1次元配列へ変換
        data_interp_1d = data_interp_2d.flatten()

        return data_interp_1d


def _get_filename(region: Region) -> str:
    """Get the file name depending on the region. / 地域の区分に応じたファイル名を取得する。

    Args:
        region: 地域の区分

    Returns:
        file name (csv, including the extention). / 地域の区分に応じたファイル名(CSVファイル)(拡張子も含む)
    """

    weather_data_filename = {
        Region.Region1: '01_kitami.csv',  # 1地域（北見）
        Region.Region2: '02_iwamizawa.csv',  # 2地域（岩見沢）
        Region.Region3: '03_morioka.csv',  # 3地域（盛岡）
        Region.Region4: '04_nagano.csv',  # 4地域（長野）
        Region.Region5: '05_utsunomiya.csv',  # 5地域（宇都宮）
        Region.Region6: '06_okayama.csv',  # 6地域（岡山）
        Region.Region7: '07_miyazaki.csv',  # 7地域（宮崎）
        Region.Region8: '08_naha.csv'  # 8地域（那覇）
    }[region]

    return weather_data_filename
