import numpy as np
import pandas as pd
import os
import logging

from heat_load_calc.weather import weather


logger = logging.getLogger(name='HeatLoadCalc').getChild('Weather')


class OutdoorCondition:

    def __init__(self, a_sun_ns, h_sun_ns, i_dn_ns, i_sky_ns, r_n_ns, theta_o_ns, x_o_ns):
        """

        Args:
            a_sun_ns: 外気温度, degree C, [n]
            h_sun_ns: 外気絶対湿度, kg/kg(DA), [n]
            i_dn_ns: 法線面直達日射量, W/m2, [n]
            i_sky_ns: 水平面天空日射量, W/m2, [n]
            r_n_ns: 夜間放射量, W/m2, [n]
            theta_o_ns: 太陽高度, rad, [n]
            x_o_ns: 太陽方位角, rad, [n]
        """

        self._a_sun_ns = a_sun_ns
        self._h_sun_ns = h_sun_ns
        self._i_dn_ns = i_dn_ns
        self._i_sky_ns = i_sky_ns
        self._r_n_ns = r_n_ns
        self._theta_o_ns = theta_o_ns
        self._x_o_ns = x_o_ns

    @classmethod
    def make_weather(cls, method: str, file_path: str = "", region: int = None):

        if method == 'file':

            logger.info('Load weather data from `{}`'.format(file_path))

            if not os.path.isfile(file_path):

                raise FileNotFoundError("Error: File {} is not exist.".format(file_path))

            pp = pd.read_csv(file_path)

            return cls.make_from_pd(pp=pp)

        elif method == 'ees':

            logger.info('make weather data based on the EES region')

            pp = weather.make_weather(region=region)

            return cls.make_from_pd(pp=pp)

        else:

            raise Exception()

    def save_weather(self, output_data_dir: str):

        # TODO: とりあえずのコード。 pandas でデータを保持する方が素直か？

        weather_path = os.path.join(output_data_dir, 'weather.csv')
        logger.info('Save weather data to `{}`'.format(weather_path))

        # 時系列インデクスの作成
        dd = pd.DataFrame(index=pd.date_range(start='1/1/1989', periods=8760 * 4, freq='15min'))

        dd['temperature'] = self._theta_o_ns.round(3)
        dd['absolute humidity'] = self._x_o_ns.round(6)
        dd['normal direct solar radiation'] = self._i_dn_ns
        dd['horizontal sky solar radiation'] = self._i_sky_ns
        dd['outward radiation'] = self._r_n_ns
        dd['sun altitude'] = self._h_sun_ns
        dd['sun azimuth'] = self._a_sun_ns
        dd.to_csv(weather_path, encoding='utf-8')

    def get_a_sun_ns_plus(self):
        return self.add_index_0_data_to_end(d=self._a_sun_ns)

    def get_h_sun_ns_plus(self):
        return self.add_index_0_data_to_end(d=self._h_sun_ns)

    def get_i_dn_ns_plus(self):
        return self.add_index_0_data_to_end(d=self._i_dn_ns)

    def get_i_sky_ns_plus(self):
        return self.add_index_0_data_to_end(d=self._i_sky_ns)

    def get_r_n_ns_plus(self):
        return self.add_index_0_data_to_end(d=self._r_n_ns)

    def get_theta_o_ns_plus(self):
        return self.add_index_0_data_to_end(d=self._theta_o_ns)

    def get_x_o_ns_plus(self):
        return self.add_index_0_data_to_end(d=self._x_o_ns)

    @classmethod
    def make_from_pd(cls, pp: pd.DataFrame):
        """
        気象データを読み込む。

        Args:
            pp (pd.DataFrame): 気象データのDataFrame
        Returns:
            外気温度, degree C
            外気絶対湿度, kg/kg(DA)
            法線面直達日射量, W/m2
            水平面天空日射量, W/m2
            夜間放射量, W/m2
            太陽高度, rad
            太陽方位角, rad
        """

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
            x_o_ns=x_o_ns
        )

    @staticmethod
    def add_index_0_data_to_end(d: np.ndarray):
        """
        リストの最後に一番最初のデータを追加する。

        Args:
            d: リスト

        Returns:
            追加されたリスト
        """

        return np.append(d, d[0])
