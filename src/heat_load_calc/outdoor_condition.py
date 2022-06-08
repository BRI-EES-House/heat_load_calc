import numpy as np
import pandas as pd
import os
import logging

from heat_load_calc.weather import interval
from heat_load_calc.weather import weather_data
from heat_load_calc.weather import region_location
from heat_load_calc import solar_position

logger = logging.getLogger(name='HeatLoadCalc').getChild('Weather')


class OutdoorCondition:

    def __init__(
            self,
            a_sun_ns: np.ndarray,
            h_sun_ns: np.ndarray,
            i_dn_ns: np.ndarray,
            i_sky_ns: np.ndarray,
            r_n_ns: np.ndarray,
            theta_o_ns: np.ndarray,
            x_o_ns: np.ndarray,
            itv: interval = interval.Interval.M15
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
    def make_weather(cls, method: str, itv: interval.Interval, file_path: str = "", region: int = None):

        if method == 'file':

            logger.info('Load weather data from `{}`'.format(file_path))

            return cls.make_from_pd(file_path=file_path, itv=itv)

        elif method == 'ees':

            logger.info('make weather data based on the EES region')

            return cls._make_weather_ees(region=region, itv=interval.Interval.M15)

        else:

            raise Exception()

    def get_weather_as_pandas_data_frame(self):

        # インターバル指定文字をpandasのfreq引数に文字変換する。
        freq = {
            interval.Interval.M15: '15min',
            interval.Interval.M30: '30min',
            interval.Interval.H1: 'H'
        }[self._itv]

        # 時系列インデクスの作成
        dd = pd.DataFrame(index=pd.date_range(start='1/1/1989', periods=8760 * 4, freq=freq))

        dd['temperature'] = self._theta_o_ns.round(3)
        dd['absolute humidity'] = self._x_o_ns.round(6)
        dd['normal direct solar radiation'] = self._i_dn_ns
        dd['horizontal sky solar radiation'] = self._i_sky_ns
        dd['outward radiation'] = self._r_n_ns
        dd['sun altitude'] = self._h_sun_ns
        dd['sun azimuth'] = self._a_sun_ns

        return dd

    def get_a_sun_ns_plus(self):
        return self._add_index_0_data_to_end(d=self._a_sun_ns)

    def get_h_sun_ns_plus(self):
        return self._add_index_0_data_to_end(d=self._h_sun_ns)

    def get_i_dn_ns_plus(self):
        return self._add_index_0_data_to_end(d=self._i_dn_ns)

    def get_i_sky_ns_plus(self):
        return self._add_index_0_data_to_end(d=self._i_sky_ns)

    def get_r_n_ns_plus(self):
        return self._add_index_0_data_to_end(d=self._r_n_ns)

    def get_theta_o_ns_plus(self):
        return self._add_index_0_data_to_end(d=self._theta_o_ns)

    def get_x_o_ns_plus(self):
        return self._add_index_0_data_to_end(d=self._x_o_ns)

    @classmethod
    def make_from_pd(cls, file_path, itv: interval.Interval):
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

        # 外気温度, degree C
        theta_o_ns = pp['temperature'].values

        # 外気絶対湿度, kg/kg(DA)
        x_o_ns = pp['absolute humidity'].values

        # 法線面直達日射量, W/m2
        i_dn_ns = pp['normal direct solar radiation'].values

        # 水平面天空日射量, W/m2
        i_sky_ns = pp['horizontal sky solar radiation'].values

        # 夜間放射量, W/m2
        r_n_ns = pp['outward radiation'].values

        # 太陽高度, rad
        h_sun_ns = pp['sun altitude'].values

        # 太陽方位角, rad
        a_sun_ns = pp['sun azimuth'].values

        return OutdoorCondition(
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
    def _make_weather_ees(cls, region: int, itv: interval.Interval = interval.Interval.M15):
        """気象データを作成する。
        Args:
            region: 地域の区分
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
        theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns = weather_data.load(region=region, interval=itv)

        # 緯度, rad & 経度, rad
        phi_loc, lambda_loc = region_location.get_phi_loc_and_lambda_loc(region=region)

        # 太陽位置
        #   (1) ステップ n における太陽高度, rad, [n]
        #   (2) ステップ n における太陽方位角, rad, [n]
        h_sun_ns, a_sun_ns = solar_position.calc_solar_position(phi_loc=phi_loc, lambda_loc=lambda_loc, interval=itv)

        return OutdoorCondition(
            a_sun_ns=a_sun_ns,
            h_sun_ns=h_sun_ns,
            i_dn_ns=i_dn_ns,
            i_sky_ns=i_sky_ns,
            r_n_ns=r_n_ns,
            theta_o_ns=theta_o_ns.round(3),
            x_o_ns=x_o_ns.round(6),
            itv=itv
        )
