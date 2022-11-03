import numpy as np
import pandas as pd
import os
import logging
from typing import Tuple
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
            a_sun_ns: 外気温度, degree C, [n]
            h_sun_ns: 外気絶対湿度, kg/kg(DA), [n]
            i_dn_ns: 法線面直達日射量, W/m2, [n]
            i_sky_ns: 水平面天空日射量, W/m2, [n]
            r_n_ns: 夜間放射量, W/m2, [n]
            theta_o_ns: 太陽高度, rad, [n]
            x_o_ns: 太陽方位角, rad, [n]
            itv: 時間間隔
        """

        self._a_sun_ns = a_sun_ns
        self._h_sun_ns = h_sun_ns
        self._i_dn_ns = i_dn_ns
        self._i_sky_ns = i_sky_ns
        self._r_n_ns = r_n_ns
        self._theta_o_ns = theta_o_ns
        self._x_o_ns = x_o_ns

        self._itv = itv

    @classmethod
    def make_weather(cls, method: str, itv: Interval = Interval.M15, file_path: str = "", region: int = None):

        if method == 'file':

            logger.info('Load weather data from `{}`'.format(file_path))

            return cls.make_from_pd(file_path=file_path, itv=itv)

        elif method == 'ees':

            logger.info('make weather data based on the EES region')

            return cls._make_weather_ees(rgn=Region(region), itv=itv)

        else:

            raise Exception()

    def get_weather_as_pandas_data_frame(self):

        # インターバル指定文字をpandasのfreq引数に文字変換する。
        freq = self._itv.get_pandas_freq()

        # 時系列インデクスの作成
        dd = pd.DataFrame(index=pd.date_range(start='1/1/1989', periods=self._itv.get_annual_number(), freq=freq))

        dd['temperature'] = self._theta_o_ns.round(3)
        dd['absolute humidity'] = self._x_o_ns.round(6)
        dd['normal direct solar radiation'] = self._i_dn_ns
        dd['horizontal sky solar radiation'] = self._i_sky_ns
        dd['outward radiation'] = self._r_n_ns
        dd['sun altitude'] = self._h_sun_ns
        dd['sun azimuth'] = self._a_sun_ns

        return dd

    @property
    def a_sun_ns_plus(self):
        return self._add_index_0_data_to_end(d=self._a_sun_ns)

    @property
    def h_sun_ns_plus(self):
        return self._add_index_0_data_to_end(d=self._h_sun_ns)

    @property
    def i_dn_ns_plus(self):
        return self._add_index_0_data_to_end(d=self._i_dn_ns)

    @property
    def i_sky_ns_plus(self):
        return self._add_index_0_data_to_end(d=self._i_sky_ns)

    @property
    def r_n_ns_plus(self):
        return self._add_index_0_data_to_end(d=self._r_n_ns)

    @property
    def theta_o_ns_plus(self):
        return self._add_index_0_data_to_end(d=self._theta_o_ns)

    @property
    def x_o_ns_plus(self):
        return self._add_index_0_data_to_end(d=self._x_o_ns)

    @property
    def number_of_data(self) -> int:
        """データの数を取得する。
        Returns:
            データの数
        """

        return self._itv.get_n_hour() * 8760

    @property
    def number_of_data_plus(self) -> int:
        """データの数に1を足したものを取得する。
        例えば、1時間間隔の場合、データの数は8760なので、返す値は8761
        15分間隔の場合、データの数は35040なので、返す値は35041
        Returns:
            データの数に1を足したもの
        """

        return self.number_of_data + 1

    def get_theta_o_ns_average(self) -> float:
        """外気温度の年間平均値を取得する。

        Returns:
            外気温度の年間平均値, degree C
        """

        return np.average(self._theta_o_ns)

    @classmethod
    def make_from_pd(cls, file_path, itv: Interval):
        """
        気象データを読み込む。

        Args:
            file_path: 気象データのファイルのパス
            itv: Interval 列挙体
        Returns:
            OutdoorCondition クラス
        """

        if not os.path.isfile(file_path):
            raise FileNotFoundError("Error: File {} is not exist.".format(file_path))

        pp = pd.read_csv(file_path)

        if not len(pp) == 8760:
            raise Exception("Error: Row length of the file should be 8760.")

        latitude = pp['longitude'][0]
        longitude = pp['latitude'][0]

        phi_loc, lambda_loc = math.radians(latitude), math.radians(longitude)

        # 太陽位置
        #   (1) ステップ n における太陽高度, rad, [n]
        #   (2) ステップ n における太陽方位角, rad, [n]
        h_sun_ns, a_sun_ns = solar_position.calc_solar_position(phi_loc=phi_loc, lambda_loc=lambda_loc, interval=itv)

        # 外気温度, degree C
        theta_o_ns = cls._interpolate(weather_data=pp['temperature'].values, interval=itv, rolling=False)

        # 外気絶対湿度, kg/kg(DA)
        # g/kgDA から kg/kgDA へ単位変換を行う。
        x_o_ns = cls._interpolate(weather_data=pp['absolute humidity'].values, interval=itv, rolling=False) / 1000.0

        # 法線面直達日射量, W/m2
        i_dn_ns = cls._interpolate(weather_data=pp['normal direct solar radiation'].values, interval=itv, rolling=False)

        # 水平面天空日射量, W/m2
        i_sky_ns = cls._interpolate(weather_data=pp['horizontal sky solar radiation'].values, interval=itv, rolling=False)

        # 夜間放射量, W/m2
        r_n_ns = cls._interpolate(weather_data=pp['outward radiation'].values, interval=itv, rolling=False)

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

    @classmethod
    def _add_index_0_data_to_end(cls, d: np.ndarray):
        """
        リストの最後に一番最初のデータを追加する。

        Args:
            d: リスト

        Returns:
            追加されたリスト
        """

        return np.append(d, d[0])

    @classmethod
    def _make_weather_ees(cls, rgn: Region, itv: Interval):
        """気象データを作成する。
        Args:
            rgn: 地域の区分
            itv: Interval 列挙体
        Returns:
            OutdoorCondition クラス
        """

        # 気象データの読み込み
        #   (1)ステップnにおける外気温度, degree C, [n]
        #   (2)ステップnにおける法線面直達日射量, W/m2, [n]
        #   (3)ステップnにおける水平面天空日射量, W/m2, [n]
        #   (4)ステップnにおける夜間放射量, W/m2, [n]
        #   (5)ステップnにおける外気絶対湿度, kg/kgDA, [n]
        # インターバルごとの要素数について
        #   interval = '1h' -> n = 8760
        #   interval = '30m' -> n = 8760 * 2
        #   interval = '15m' -> n = 8760 * 4
        theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns = cls._load(rgn=rgn, itv=itv)

        # 緯度, rad & 経度, rad
        phi_loc, lambda_loc = rgn.get_phi_loc_and_lambda_loc()

        # 太陽位置
        #   (1) ステップ n における太陽高度, rad, [n]
        #   (2) ステップ n における太陽方位角, rad, [n]
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

    @classmethod
    def _load(cls, rgn: Region, itv: Interval) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        地域の区分に応じて気象データを読み込み、指定された時間間隔で必要に応じて補間を行いデータを作成する。

        Args:
            rgn: 地域の区分
            itv: Interval 列挙体

        Returns:
            以下の5項目
                (1) ステップnにおける外気温度, degree C [n]
                (2) ステップnにおける法線面直達日射量, W/m2 [n]
                (3) ステップnにおける水平面天空日射量, W/m2 [n]
                (4) ステップnにおける夜間放射量, W/m2 [n]
                (5) ステップnにおける外気絶対湿度, g/kgDA [n]

        Notes:
            interval = '1h' -> n = 8760
            interval = '30m' -> n = 8760 * 2
            interval = '15m' -> n = 8760 * 4
        """

        # 地域の区分に応じたファイル名の取得
        weather_data_filename = cls._get_filename(rgn=rgn)

        # ファイル読み込み
        path_and_filename = str(os.path.dirname(__file__)) + '/expanded_amedas/' + weather_data_filename

        data = np.loadtxt(path_and_filename, delimiter=",", skiprows=2, usecols=(2, 3, 4, 5, 6), encoding="utf-8")

        # 扱いにくいので転地（列：項目・行：時刻　→　列：時刻・行：項目
        # [5項目, 8760データ]
        # [8760, 5] -> [5, 8760]
        weather = data.T

        # ステップnにおける外気温度, degree C
        theta_o_ns = cls._interpolate(weather_data=weather[0], interval=itv, rolling=True)

        # ステップnにおける法線面直達日射量, W/m2
        i_dn_ns = cls._interpolate(weather_data=weather[1], interval=itv, rolling=True)

        # ステップnにおける水平面天空日射量, W/m2
        i_sky_ns = cls._interpolate(weather_data=weather[2], interval=itv, rolling=True)

        # ステップnにおける夜間放射量, W/m2
        r_n_ns = cls._interpolate(weather_data=weather[3], interval=itv, rolling=True)

        # ステップnにおける外気絶対湿度, kg/kgDA
        # g/kgDA から kg/kgDA へ単位変換を行う。
        x_o_ns = cls._interpolate(weather_data=weather[4], interval=itv, rolling=True) / 1000.0

        return theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns

    @classmethod
    def _interpolate(cls, weather_data: np.ndarray, interval: Interval, rolling: bool) -> np.ndarray:
        """
        1時間ごとの8760データを指定された間隔のデータに補間する。
        '1h': 1時間間隔の場合、 n = 8760
        '30m': 30分間隔の場合、 n = 8760 * 2 = 17520
        '15m': 15分間隔の場合、 n = 8760 * 4 = 35040

        Args:
            weather_data: 1時間ごとの気象データ [8760]
            interval: 生成するデータの時間間隔
            rolling: rolling するか否か。データが1時始まりの場合は最終行の 12/31 24:00 のデータを 1/1 0:00 に持ってくるため、この値は True にすること。

        Returns:
            指定する時間間隔に補間された気象データ [n]
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

            # 直線補完 8760×4 の2次元配列
            data_interp_2d = alpha[np.newaxis, :] * data1[:, np.newaxis] + (1.0 - alpha[np.newaxis, :]) * data2[:, np.newaxis]

            # 1次元配列へ変換
            data_interp_1d = data_interp_2d.flatten()

            return data_interp_1d

    @classmethod
    def _get_filename(cls, rgn: Region) -> str:
        """
        地域の区分に応じたファイル名を取得する。

        Args:
            rgn: 地域の区分

        Returns:
            地域の区分に応じたファイル名（CSVファイル）（拡張子も含む）
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
        }[rgn]

        return weather_data_filename
