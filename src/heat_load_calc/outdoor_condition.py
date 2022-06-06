import numpy as np
import pandas as pd


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

    @staticmethod
    def make_from_pd(pp: pd.DataFrame):
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
