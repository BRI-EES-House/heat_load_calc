import unittest
import os

from heat_load_calc.weather import Weather
from heat_load_calc.interval import Interval


class TestWeather(unittest.TestCase):

    file_path = os.path.join(os.path.dirname(__file__), 'weather_for_method_file.csv')

    def test_weather_values_solar_position_ees_m15(self):

        # データの取得
        w = Weather.make_weather(method="ees", itv=Interval.M15, region=1)
        d = w.get_weather_as_pandas_data_frame()

        # 確認する時刻のタイムスタンプとインデックス
        t0, i0 = '1989-01-01 00:00:00', 0
        t1, i1 = '1989-01-01 12:00:00', 48
        t2, i2 = '1989-01-02 12:00:00', 144

        # 1/1 0:00
        self.assertAlmostEqual(d['sun altitude'][t0], -1.18973183, delta=0.00001)
        self.assertAlmostEqual(w.h_sun_ns_plus[i0], -1.18973183, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth'][t0], -2.78729204, delta=0.00001)
        self.assertAlmostEqual(w.a_sun_ns_plus[i0], -2.78729204, delta=0.00001)

        # 1/1 12:00
        self.assertAlmostEqual(d['sun altitude'][t1], 0.39709158, delta=0.00001)
        self.assertAlmostEqual(w.h_sun_ns_plus[i1], 0.39709158, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth'][t1], 0.14037539, delta=0.00001)
        self.assertAlmostEqual(w.a_sun_ns_plus[i1], 0.14037539, delta=0.00001)

        # 1/2 12:00
        self.assertAlmostEqual(d['sun altitude'][t2], 0.39876328, delta=0.00001)
        self.assertAlmostEqual(w.h_sun_ns_plus[i2], 0.39876328, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth'][t2], 0.13851202, delta=0.00001)
        self.assertAlmostEqual(w.a_sun_ns_plus[i2], 0.13851202, delta=0.00001)

    def test_weather_values_solar_position_ees_m30(self):

        # データの取得
        w = Weather.make_weather(method="ees", itv=Interval.M30, region=1)
        d = w.get_weather_as_pandas_data_frame()

        # 確認する時刻のタイムスタンプとインデックス
        t0, i0 = '1989-01-01 00:00:00', 0
        t1, i1 = '1989-01-01 12:00:00', 24
        t2, i2 = '1989-01-02 12:00:00', 72

        # 1/1 0:00
        self.assertAlmostEqual(d['sun altitude'][t0], -1.18973183, delta=0.00001)
        self.assertAlmostEqual(w.h_sun_ns_plus[i0], -1.18973183, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth'][t0], -2.78729204, delta=0.00001)
        self.assertAlmostEqual(w.a_sun_ns_plus[i0], -2.78729204, delta=0.00001)

        # 1/1 12:00
        self.assertAlmostEqual(d['sun altitude'][t1], 0.39709158, delta=0.00001)
        self.assertAlmostEqual(w.h_sun_ns_plus[i1], 0.39709158, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth'][t1], 0.14037539, delta=0.00001)
        self.assertAlmostEqual(w.a_sun_ns_plus[i1], 0.14037539, delta=0.00001)

        # 1/2 12:00
        self.assertAlmostEqual(d['sun altitude'][t2], 0.39876328, delta=0.00001)
        self.assertAlmostEqual(w.h_sun_ns_plus[i2], 0.39876328, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth'][t2], 0.13851202, delta=0.00001)
        self.assertAlmostEqual(w.a_sun_ns_plus[i2], 0.13851202, delta=0.00001)

    def test_weather_values_solar_position_ees_1h(self):

        # データの取得
        w = Weather.make_weather(method="ees", itv=Interval.H1, region=1)
        d = w.get_weather_as_pandas_data_frame()

        # 確認する時刻のタイムスタンプとインデックス
        t0, i0 = '1989-01-01 00:00:00', 0
        t1, i1 = '1989-01-01 12:00:00', 12
        t2, i2 = '1989-01-02 12:00:00', 36

        # 1/1 0:00
        self.assertAlmostEqual(d['sun altitude'][t0], -1.18973183, delta=0.00001)
        self.assertAlmostEqual(w.h_sun_ns_plus[i0], -1.18973183, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth'][t0], -2.78729204, delta=0.00001)
        self.assertAlmostEqual(w.a_sun_ns_plus[i0], -2.78729204, delta=0.00001)

        # 1/1 12:00
        self.assertAlmostEqual(d['sun altitude'][t1], 0.39709158, delta=0.00001)
        self.assertAlmostEqual(w.h_sun_ns_plus[i1], 0.39709158, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth'][t1], 0.14037539, delta=0.00001)
        self.assertAlmostEqual(w.a_sun_ns_plus[i1], 0.14037539, delta=0.00001)

        # 1/2 12:00
        self.assertAlmostEqual(d['sun altitude'][t2], 0.39876328, delta=0.00001)
        self.assertAlmostEqual(w.h_sun_ns_plus[i2], 0.39876328, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth'][t2], 0.13851202, delta=0.00001)
        self.assertAlmostEqual(w.a_sun_ns_plus[i2], 0.13851202, delta=0.00001)

    def test_weather_values_solar_position_file_m15(self):

        # データの取得
        w = Weather.make_weather(method="file", itv=Interval.M15, file_path=self.file_path)
        d = w.get_weather_as_pandas_data_frame()

        # 確認する時刻のタイムスタンプとインデックス
        t0, i0 = '1989-01-01 00:00:00', 0
        t1, i1 = '1989-01-01 12:00:00', 48
        t2, i2 = '1989-01-02 12:00:00', 144

        # 1/1 0:00
        self.assertAlmostEqual(d['sun altitude'][t0], -1.42981114, delta=0.00001)
        self.assertAlmostEqual(w.h_sun_ns_plus[i0], -1.42981114, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth'][t0], 1.94621037, delta=0.00001)
        self.assertAlmostEqual(w.a_sun_ns_plus[i0], 1.94621037, delta=0.00001)

        # 1/1 12:00
        self.assertAlmostEqual(d['sun altitude'][t1], 0.70056402, delta=0.00001)
        self.assertAlmostEqual(w.h_sun_ns_plus[i1], 0.70056402, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth'][t1], -0.17185307, delta=0.00001)
        self.assertAlmostEqual(w.a_sun_ns_plus[i1], -0.17185307, delta=0.00001)

        # 1/2 12:00
        self.assertAlmostEqual(d['sun altitude'][t2], 0.70169989, delta=0.00001)
        self.assertAlmostEqual(w.h_sun_ns_plus[i2], 0.70169989, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth'][t2], -0.17461426, delta=0.00001)
        self.assertAlmostEqual(w.a_sun_ns_plus[i2], -0.17461426, delta=0.00001)

    def test_weather_values_solar_position_file_m30(self):

        # データの取得
        w = Weather.make_weather(method="file", itv=Interval.M30, file_path=self.file_path)
        d = w.get_weather_as_pandas_data_frame()

        # 確認する時刻のタイムスタンプとインデックス
        t0, i0 = '1989-01-01 00:00:00', 0
        t1, i1 = '1989-01-01 12:00:00', 24
        t2, i2 = '1989-01-02 12:00:00', 72

        # 1/1 0:00
        self.assertAlmostEqual(d['sun altitude'][t0], -1.42981114, delta=0.00001)
        self.assertAlmostEqual(w.h_sun_ns_plus[i0], -1.42981114, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth'][t0], 1.94621037, delta=0.00001)
        self.assertAlmostEqual(w.a_sun_ns_plus[i0], 1.94621037, delta=0.00001)

        # 1/1 12:00
        self.assertAlmostEqual(d['sun altitude'][t1], 0.70056402, delta=0.00001)
        self.assertAlmostEqual(w.h_sun_ns_plus[i1], 0.70056402, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth'][t1], -0.17185307, delta=0.00001)
        self.assertAlmostEqual(w.a_sun_ns_plus[i1], -0.17185307, delta=0.00001)

        # 1/2 12:00
        self.assertAlmostEqual(d['sun altitude'][t2], 0.70169989, delta=0.00001)
        self.assertAlmostEqual(w.h_sun_ns_plus[i2], 0.70169989, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth'][t2], -0.17461426, delta=0.00001)
        self.assertAlmostEqual(w.a_sun_ns_plus[i2], -0.17461426, delta=0.00001)

    def test_weather_values_solar_position_file_h1(self):

        # データの取得
        w = Weather.make_weather(method="file", itv=Interval.H1, file_path=self.file_path)
        d = w.get_weather_as_pandas_data_frame()

        # 確認する時刻のタイムスタンプとインデックス
        t0, i0 = '1989-01-01 00:00:00', 0
        t1, i1 = '1989-01-01 12:00:00', 12
        t2, i2 = '1989-01-02 12:00:00', 36

        # 1/1 0:00
        self.assertAlmostEqual(d['sun altitude'][t0], -1.42981114, delta=0.00001)
        self.assertAlmostEqual(w.h_sun_ns_plus[i0], -1.42981114, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth'][t0], 1.94621037, delta=0.00001)
        self.assertAlmostEqual(w.a_sun_ns_plus[i0], 1.94621037, delta=0.00001)

        # 1/1 12:00
        self.assertAlmostEqual(d['sun altitude'][t1], 0.70056402, delta=0.00001)
        self.assertAlmostEqual(w.h_sun_ns_plus[i1], 0.70056402, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth'][t1], -0.17185307, delta=0.00001)
        self.assertAlmostEqual(w.a_sun_ns_plus[i1], -0.17185307, delta=0.00001)

        # 1/2 12:00
        self.assertAlmostEqual(d['sun altitude'][t2], 0.70169989, delta=0.00001)
        self.assertAlmostEqual(w.h_sun_ns_plus[i2], 0.70169989, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth'][t2], -0.17461426, delta=0.00001)
        self.assertAlmostEqual(w.a_sun_ns_plus[i2], -0.17461426, delta=0.00001)

    def test_weather_values_ees_m15(self):
        """太陽位置を除く値のテスト（15分インターバル）

        外気温度・法線面直達日射・水平面天空日射・夜間放射量・絶対湿度について1地域（北見）できちんと読み込めているのかをテストする。
        12:15 を指定することで、きちんと按分操作ができているかをテストする。
        pandas data frame と numpy のそれぞれで値を確認する。

        """

        # データの取得
        w = Weather.make_weather(method="ees", itv=Interval.M15, region=1)
        d = w.get_weather_as_pandas_data_frame()

        # 確認する時刻のタイムスタンプとインデックス
        t0, i0 = '1989-01-01 12:00:00', 48
        t1, i1 = '1989-01-01 13:00:00', 52
        t2, i2 = '1989-01-01 12:15:00', 49

        # 外気温度
        self.assertEqual(d['temperature'][t0], -11.3)
        self.assertEqual(w.theta_o_ns_plus[i0], -11.3)
        self.assertEqual(d['temperature'][t1], -9.4)
        self.assertEqual(w.theta_o_ns_plus[i1], -9.4)
        self.assertAlmostEqual(d['temperature'][t2], -11.3 * 0.75 + -9.4 * 0.25)
        self.assertAlmostEqual(w.theta_o_ns_plus[i2], -11.3 * 0.75 + -9.4 * 0.25)

        # 法線面直達日射
        self.assertEqual(d['normal direct solar radiation'][t0], 855.555555555556)
        self.assertEqual(w.i_dn_ns_plus[i0], 855.555555555556)
        self.assertEqual(d['normal direct solar radiation'][t1], 791.666666666667)
        self.assertEqual(w.i_dn_ns_plus[i1], 791.666666666667)
        self.assertAlmostEqual(d['normal direct solar radiation'][t2], 855.555555555556 * 0.75 + 791.666666666667 * 0.25)
        self.assertAlmostEqual(w.i_dn_ns_plus[i2], 855.555555555556 * 0.75 + 791.666666666667 * 0.25)

        # 水平面天空日射
        self.assertEqual(d['horizontal sky solar radiation'][t0], 55.5555555555556)
        self.assertEqual(w.i_sky_ns_plus[i0], 55.5555555555556)
        self.assertEqual(d['horizontal sky solar radiation'][t1], 58.3333333333333)
        self.assertEqual(w.i_sky_ns_plus[i1], 58.3333333333333)
        self.assertAlmostEqual(d['horizontal sky solar radiation'][t2], 55.5555555555556 * 0.75 + 58.3333333333333 * 0.25)
        self.assertAlmostEqual(w.i_sky_ns_plus[i2], 55.5555555555556 * 0.75 + 58.3333333333333 * 0.25)

        # 夜間放射量
        self.assertEqual(d['outward radiation'][t0], 88.8888888888889)
        self.assertEqual(w.r_n_ns_plus[i0], 88.8888888888889)
        self.assertEqual(d['outward radiation'][t1], 91.6666666666667)
        self.assertEqual(w.r_n_ns_plus[i1], 91.6666666666667)
        self.assertAlmostEqual(d['outward radiation'][t2], 88.8888888888889 * 0.75 + 91.6666666666667 * 0.25)
        self.assertAlmostEqual(w.r_n_ns_plus[i2], 88.8888888888889 * 0.75 + 91.6666666666667 * 0.25)

        # 絶対湿度
        self.assertEqual(d['absolute humidity'][t0], 0.0015)
        self.assertEqual(w.x_o_ns_plus[i0], 0.0015)
        self.assertEqual(d['absolute humidity'][t1], 0.0017)
        self.assertEqual(w.x_o_ns_plus[i1], 0.0017)
        self.assertAlmostEqual(d['absolute humidity'][t2], 0.0015 * 0.75 + 0.0017 * 0.25)
        self.assertAlmostEqual(w.x_o_ns_plus[i2], 0.0015 * 0.75 + 0.0017 * 0.25)

    def test_weather_values_ees_m30(self):
        """太陽位置を除く値のテスト（30分インターバル）

        外気温度・法線面直達日射・水平面天空日射・夜間放射量・絶対湿度について1地域（北見）できちんと読み込めているのかをテストする。
        12:30 を指定することで、きちんと按分操作ができているかをテストする。
        pandas data frame と numpy のそれぞれで値を確認する。

        """

        # データの取得
        w = Weather.make_weather(method="ees", itv=Interval.M30, region=1)
        d = w.get_weather_as_pandas_data_frame()

        # 確認する時刻のタイムスタンプとインデックス
        t0, i0 = '1989-01-01 12:00:00', 24
        t1, i1 = '1989-01-01 13:00:00', 26
        t2, i2 = '1989-01-01 12:30:00', 25

        # 外気温度
        self.assertEqual(d['temperature'][t0], -11.3)
        self.assertEqual(w.theta_o_ns_plus[i0], -11.3)
        self.assertEqual(d['temperature'][t1], -9.4)
        self.assertEqual(w.theta_o_ns_plus[i1], -9.4)
        self.assertAlmostEqual(d['temperature'][t2], -11.3 * 0.5 + -9.4 * 0.5)
        self.assertAlmostEqual(w.theta_o_ns_plus[i2], -11.3 * 0.5 + -9.4 * 0.5)

        # 法線面直達日射
        self.assertEqual(d['normal direct solar radiation'][t0], 855.555555555556)
        self.assertEqual(w.i_dn_ns_plus[i0], 855.555555555556)
        self.assertEqual(d['normal direct solar radiation'][t1], 791.666666666667)
        self.assertEqual(w.i_dn_ns_plus[i1], 791.666666666667)
        self.assertAlmostEqual(d['normal direct solar radiation'][t2], 855.555555555556 * 0.5 + 791.666666666667 * 0.5)
        self.assertAlmostEqual(w.i_dn_ns_plus[i2], 855.555555555556 * 0.5 + 791.666666666667 * 0.5)

        # 水平面天空日射
        self.assertEqual(d['horizontal sky solar radiation'][t0], 55.5555555555556)
        self.assertEqual(w.i_sky_ns_plus[i0], 55.5555555555556)
        self.assertEqual(d['horizontal sky solar radiation'][t1], 58.3333333333333)
        self.assertEqual(w.i_sky_ns_plus[i1], 58.3333333333333)
        self.assertAlmostEqual(d['horizontal sky solar radiation'][t2], 55.5555555555556 * 0.5 + 58.3333333333333 * 0.5)
        self.assertAlmostEqual(w.i_sky_ns_plus[i2], 55.5555555555556 * 0.5 + 58.3333333333333 * 0.5)

        # 夜間放射量
        self.assertEqual(d['outward radiation'][t0], 88.8888888888889)
        self.assertEqual(w.r_n_ns_plus[i0], 88.8888888888889)
        self.assertEqual(d['outward radiation'][t1], 91.6666666666667)
        self.assertEqual(w.r_n_ns_plus[i1], 91.6666666666667)
        self.assertAlmostEqual(d['outward radiation'][t2], 88.8888888888889 * 0.5 + 91.6666666666667 * 0.5)
        self.assertAlmostEqual(w.r_n_ns_plus[i2], 88.8888888888889 * 0.5 + 91.6666666666667 * 0.5)

        # 絶対湿度
        self.assertEqual(d['absolute humidity'][t0], 0.0015)
        self.assertEqual(w.x_o_ns_plus[i0], 0.0015)
        self.assertEqual(d['absolute humidity'][t1], 0.0017)
        self.assertEqual(w.x_o_ns_plus[i1], 0.0017)
        self.assertAlmostEqual(d['absolute humidity'][t2], 0.0015 * 0.5 + 0.0017 * 0.5)
        self.assertAlmostEqual(w.x_o_ns_plus[i2], 0.0015 * 0.5 + 0.0017 * 0.5)

    def test_weather_values_ees_1h(self):
        """太陽位置を除く値のテスト（1時間インターバル）

        外気温度・法線面直達日射・水平面天空日射・夜間放射量・絶対湿度について1地域（北見）できちんと読み込めているのかをテストする。
        1時間インターバルのため按分テストは発生しない。
        pandas data frame と numpy のそれぞれで値を確認する。

        """

        # データの取得
        w = Weather.make_weather(method="ees", itv=Interval.H1, region=1)
        d = w.get_weather_as_pandas_data_frame()

        # 確認する時刻のタイムスタンプとインデックス
        t0, i0 = '1989-01-01 12:00:00', 12
        t1, i1 = '1989-01-01 13:00:00', 13

        # 外気温度
        self.assertEqual(d['temperature'][t0], -11.3)
        self.assertEqual(w.theta_o_ns_plus[i0], -11.3)
        self.assertEqual(d['temperature'][t1], -9.4)
        self.assertEqual(w.theta_o_ns_plus[i1], -9.4)

        # 法線面直達日射
        self.assertEqual(d['normal direct solar radiation'][t0], 855.555555555556)
        self.assertEqual(w.i_dn_ns_plus[i0], 855.555555555556)
        self.assertEqual(d['normal direct solar radiation'][t1], 791.666666666667)
        self.assertEqual(w.i_dn_ns_plus[i1], 791.666666666667)

        # 水平面天空日射
        self.assertEqual(d['horizontal sky solar radiation'][t0], 55.5555555555556)
        self.assertEqual(w.i_sky_ns_plus[i0], 55.5555555555556)
        self.assertEqual(d['horizontal sky solar radiation'][t1], 58.3333333333333)
        self.assertEqual(w.i_sky_ns_plus[i1], 58.3333333333333)

        # 夜間放射量
        self.assertEqual(d['outward radiation'][t0], 88.8888888888889)
        self.assertEqual(w.r_n_ns_plus[i0], 88.8888888888889)
        self.assertEqual(d['outward radiation'][t1], 91.6666666666667)
        self.assertEqual(w.r_n_ns_plus[i1], 91.6666666666667)

        # 絶対湿度
        self.assertEqual(d['absolute humidity'][t0], 0.0015)
        self.assertEqual(w.x_o_ns_plus[i0], 0.0015)
        self.assertEqual(d['absolute humidity'][t1], 0.0017)
        self.assertEqual(w.x_o_ns_plus[i1], 0.0017)

    def test_weather_values_file_m15(self):
        """太陽位置を除く値のテスト（15分インターバル）

        外気温度・法線面直達日射・水平面天空日射・夜間放射量・絶対湿度について独自ファイルをきちんと読み込めているのかをテストする。
        12:15 を指定することで、きちんと按分操作ができているかをテストする。
        pandas data frame と numpy のそれぞれで値を確認する。

        """

        # データの取得
        w = Weather.make_weather(method="file", itv=Interval.M15, file_path=self.file_path)
        d = w.get_weather_as_pandas_data_frame()

        # 確認する時刻のタイムスタンプとインデックス
        t0, i0 = '1989-01-01 12:00:00', 48
        t1, i1 = '1989-01-01 13:00:00', 52
        t2, i2 = '1989-01-01 12:15:00', 49

        # 外気温度
        self.assertEqual(d['temperature'][t0], 20.6)
        self.assertEqual(w.theta_o_ns_plus[i0], 20.6)
        self.assertEqual(d['temperature'][t1], 18.8)
        self.assertEqual(w.theta_o_ns_plus[i1], 18.8)
        self.assertAlmostEqual(d['temperature'][t2], 20.6 * 0.75 + 18.8 * 0.25)
        self.assertAlmostEqual(w.theta_o_ns_plus[i2], 20.6 * 0.75 + 18.8 * 0.25)

        # 法線面直達日射
        self.assertEqual(d['normal direct solar radiation'][t0], 0.0)
        self.assertEqual(w.i_dn_ns_plus[i0], 0.0)
        self.assertEqual(d['normal direct solar radiation'][t1], 13.88888889)
        self.assertEqual(w.i_dn_ns_plus[i1], 13.88888889)
        self.assertAlmostEqual(d['normal direct solar radiation'][t2], 0.0 * 0.75 + 13.88888889 * 0.25)
        self.assertAlmostEqual(w.i_dn_ns_plus[i2], 0.0 * 0.75 + 13.88888889 * 0.25)

        # 水平面天空日射
        self.assertEqual(d['horizontal sky solar radiation'][t0], 119.4444444)
        self.assertEqual(w.i_sky_ns_plus[i0], 119.4444444)
        self.assertEqual(d['horizontal sky solar radiation'][t1], 111.1111111)
        self.assertEqual(w.i_sky_ns_plus[i1], 111.1111111)
        self.assertAlmostEqual(d['horizontal sky solar radiation'][t2], 119.4444444 * 0.75 + 111.1111111 * 0.25)
        self.assertAlmostEqual(w.i_sky_ns_plus[i2], 119.4444444 * 0.75 + 111.1111111 * 0.25)

        # 夜間放射量
        self.assertEqual(d['outward radiation'][t0], 11.11111111)
        self.assertEqual(w.r_n_ns_plus[i0], 11.11111111)
        self.assertEqual(d['outward radiation'][t1], 11.11111111)
        self.assertEqual(w.r_n_ns_plus[i1], 11.11111111)
        self.assertAlmostEqual(d['outward radiation'][t2], 11.11111111 * 0.75 + 11.11111111 * 0.25)
        self.assertAlmostEqual(w.r_n_ns_plus[i2], 11.11111111 * 0.75 + 11.11111111 * 0.25)

        # 絶対湿度
        self.assertAlmostEqual(d['absolute humidity'][t0], 0.0138)
        self.assertAlmostEqual(w.x_o_ns_plus[i0], 0.0138)
        self.assertAlmostEqual(d['absolute humidity'][t1], 0.0128)
        self.assertAlmostEqual(w.x_o_ns_plus[i1], 0.0128)
        self.assertAlmostEqual(d['absolute humidity'][t2], 0.0138 * 0.75 + 0.0128 * 0.25)
        self.assertAlmostEqual(w.x_o_ns_plus[i2], 0.0138 * 0.75 + 0.0128 * 0.25)

    def test_weather_values_file_m30(self):
        """太陽位置を除く値のテスト（30分インターバル）

        外気温度・法線面直達日射・水平面天空日射・夜間放射量・絶対湿度について独自ファイルをきちんと読み込めているのかをテストする。
        12:30 を指定することで、きちんと按分操作ができているかをテストする。
        pandas data frame と numpy のそれぞれで値を確認する。

        """

        # データの取得
        w = Weather.make_weather(method="file", itv=Interval.M30, file_path=self.file_path)
        d = w.get_weather_as_pandas_data_frame()

        # 確認する時刻のタイムスタンプとインデックス
        t0, i0 = '1989-01-01 12:00:00', 24
        t1, i1 = '1989-01-01 13:00:00', 26
        t2, i2 = '1989-01-01 12:30:00', 25

        # 外気温度
        self.assertEqual(d['temperature'][t0], 20.6)
        self.assertEqual(w.theta_o_ns_plus[i0], 20.6)
        self.assertEqual(d['temperature'][t1], 18.8)
        self.assertEqual(w.theta_o_ns_plus[i1], 18.8)
        self.assertAlmostEqual(d['temperature'][t2], 20.6 * 0.5 + 18.8 * 0.5)
        self.assertAlmostEqual(w.theta_o_ns_plus[i2], 20.6 * 0.5 + 18.8 * 0.5)

        # 法線面直達日射
        self.assertEqual(d['normal direct solar radiation'][t0], 0.0)
        self.assertEqual(w.i_dn_ns_plus[i0], 0.0)
        self.assertEqual(d['normal direct solar radiation'][t1], 13.88888889)
        self.assertEqual(w.i_dn_ns_plus[i1], 13.88888889)
        self.assertAlmostEqual(d['normal direct solar radiation'][t2], 0.0 * 0.5 + 13.88888889 * 0.5)
        self.assertAlmostEqual(w.i_dn_ns_plus[i2], 0.0 * 0.5 + 13.88888889 * 0.5)

        # 水平面天空日射
        self.assertEqual(d['horizontal sky solar radiation'][t0], 119.4444444)
        self.assertEqual(w.i_sky_ns_plus[i0], 119.4444444)
        self.assertEqual(d['horizontal sky solar radiation'][t1], 111.1111111)
        self.assertEqual(w.i_sky_ns_plus[i1], 111.1111111)
        self.assertAlmostEqual(d['horizontal sky solar radiation'][t2], 119.4444444 * 0.5 + 111.1111111 * 0.5)
        self.assertAlmostEqual(w.i_sky_ns_plus[i2], 119.4444444 * 0.5 + 111.1111111 * 0.5)

        # 夜間放射量
        self.assertEqual(d['outward radiation'][t0], 11.11111111)
        self.assertEqual(w.r_n_ns_plus[i0], 11.11111111)
        self.assertEqual(d['outward radiation'][t1], 11.11111111)
        self.assertEqual(w.r_n_ns_plus[i1], 11.11111111)
        self.assertAlmostEqual(d['outward radiation'][t2], 11.11111111 * 0.5 + 11.11111111 * 0.5)
        self.assertAlmostEqual(w.r_n_ns_plus[i2], 11.11111111 * 0.5 + 11.11111111 * 0.5)

        # 絶対湿度
        self.assertAlmostEqual(d['absolute humidity'][t0], 0.0138)
        self.assertAlmostEqual(w.x_o_ns_plus[i0], 0.0138)
        self.assertAlmostEqual(d['absolute humidity'][t1], 0.0128)
        self.assertAlmostEqual(w.x_o_ns_plus[i1], 0.0128)
        self.assertAlmostEqual(d['absolute humidity'][t2], 0.0138 * 0.5 + 0.0128 * 0.5)
        self.assertAlmostEqual(w.x_o_ns_plus[i2], 0.0138 * 0.5 + 0.0128 * 0.5)

    def test_weather_values_file_h1(self):
        """太陽位置を除く値のテスト（1時間インターバル）

        外気温度・法線面直達日射・水平面天空日射・夜間放射量・絶対湿度について独自ファイルをきちんと読み込めているのかをテストする。
        1時間インターバルのため按分テストは発生しない。
        pandas data frame と numpy のそれぞれで値を確認する。

        """

        # データの取得
        w = Weather.make_weather(method="file", itv=Interval.H1, file_path=self.file_path)
        d = w.get_weather_as_pandas_data_frame()

        # 確認する時刻のタイムスタンプとインデックス
        t0, i0 = '1989-01-01 12:00:00', 12
        t1, i1 = '1989-01-01 13:00:00', 13

        # 外気温度
        self.assertEqual(d['temperature'][t0], 20.6)
        self.assertEqual(w.theta_o_ns_plus[i0], 20.6)
        self.assertEqual(d['temperature'][t1], 18.8)
        self.assertEqual(w.theta_o_ns_plus[i1], 18.8)

        # 法線面直達日射
        self.assertEqual(d['normal direct solar radiation'][t0], 0.0)
        self.assertEqual(w.i_dn_ns_plus[i0], 0.0)
        self.assertEqual(d['normal direct solar radiation'][t1], 13.88888889)
        self.assertEqual(w.i_dn_ns_plus[i1], 13.88888889)

        # 水平面天空日射
        self.assertEqual(d['horizontal sky solar radiation'][t0], 119.4444444)
        self.assertEqual(w.i_sky_ns_plus[i0], 119.4444444)
        self.assertEqual(d['horizontal sky solar radiation'][t1], 111.1111111)
        self.assertEqual(w.i_sky_ns_plus[i1], 111.1111111)

        # 夜間放射量
        self.assertEqual(d['outward radiation'][t0], 11.11111111)
        self.assertEqual(w.r_n_ns_plus[i0], 11.11111111)
        self.assertEqual(d['outward radiation'][t1], 11.11111111)
        self.assertEqual(w.r_n_ns_plus[i1], 11.11111111)

        # 絶対湿度
        self.assertAlmostEqual(d['absolute humidity'][t0], 0.0138)
        self.assertAlmostEqual(w.x_o_ns_plus[i0], 0.0138)
        self.assertAlmostEqual(d['absolute humidity'][t1], 0.0128)
        self.assertAlmostEqual(w.x_o_ns_plus[i1], 0.0128)


if __name__ == '__main__':
    unittest.main()
