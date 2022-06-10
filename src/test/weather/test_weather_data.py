import unittest

from heat_load_calc.interval import Interval
from heat_load_calc.outdoor_condition import OutdoorCondition
from heat_load_calc.region import Region


class TestWeatherData15m(unittest.TestCase):

    def test_read_row_1_1_12(self):

        theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns = OutdoorCondition._load(rgn=Region.Region1, itv=Interval.M15)

        # 時刻 12 時のデータ
        time = 12 * 4

        # 外気温度
        self.assertEqual(theta_o_ns[time], -11.3)

        # 法線面直達日射
        self.assertEqual(i_dn_ns[time], 855.555555555556)

        # 水平面天空日射
        self.assertEqual(i_sky_ns[time], 55.5555555555556)

        # 夜間放射量
        self.assertEqual(r_n_ns[time], 88.8888888888889)

        # 絶対湿度
        self.assertEqual(x_o_ns[time], 0.0015)

    def test_read_row_1_1_13(self):

        theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns = OutdoorCondition._load(rgn=Region.Region1, itv=Interval.M15)

        # 時刻 13 時のデータ
        time = 13 * 4

        # 外気温度
        self.assertEqual(theta_o_ns[time], -9.4)

        # 法線面直達日射
        self.assertEqual(i_dn_ns[time], 791.666666666667)

        # 水平面天空日射
        self.assertEqual(i_sky_ns[time], 58.3333333333333)

        # 夜間放射量
        self.assertEqual(r_n_ns[time], 91.6666666666667)

        # 絶対湿度
        self.assertEqual(x_o_ns[time], 0.0017)

    def test_read_row_1_1_12_13(self):
        """
        按分のテスト
        """

        theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns = OutdoorCondition._load(rgn=Region.Region1, itv=Interval.M15)

        # 時刻 12 時 15 分のデータ
        time = 12 * 4 + 1

        # 外気温度
        self.assertAlmostEqual(theta_o_ns[time], -11.3 * 0.75 + -9.4 * 0.25)

        # 法線面直達日射
        self.assertAlmostEqual(i_dn_ns[time], 855.555555555556 * 0.75 + 791.666666666667 * 0.25)

        # 水平面天空日射
        self.assertAlmostEqual(i_sky_ns[time], 55.5555555555556 * 0.75 + 58.3333333333333 * 0.25)

        # 夜間放射量
        self.assertAlmostEqual(r_n_ns[time], 88.8888888888889 * 0.75 + 91.6666666666667 * 0.25)

        # 絶対湿度
        self.assertAlmostEqual(x_o_ns[time], 0.0015 * 0.75 + 0.0017 * 0.25)


class TestWeatherData30m(unittest.TestCase):

    def test_read_row_1_1_12(self):

        theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns = OutdoorCondition._load(rgn=Region.Region1, itv=Interval.M30)

        # 時刻 12 時のデータ
        time = 12 * 2

        # 外気温度
        self.assertEqual(theta_o_ns[time], -11.3)

        # 法線面直達日射
        self.assertEqual(i_dn_ns[time], 855.555555555556)

        # 水平面天空日射
        self.assertEqual(i_sky_ns[time], 55.5555555555556)

        # 夜間放射量
        self.assertEqual(r_n_ns[time], 88.8888888888889)

        # 絶対湿度
        self.assertEqual(x_o_ns[time], 0.0015)

    def test_read_row_1_1_13(self):

        theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns = OutdoorCondition._load(rgn=Region.Region1, itv=Interval.M30)

        # 時刻 13 時のデータ
        time = 13 * 2

        # 外気温度
        self.assertEqual(theta_o_ns[time], -9.4)

        # 法線面直達日射
        self.assertEqual(i_dn_ns[time], 791.666666666667)

        # 水平面天空日射
        self.assertEqual(i_sky_ns[time], 58.3333333333333)

        # 夜間放射量
        self.assertEqual(r_n_ns[time], 91.6666666666667)

        # 絶対湿度
        self.assertEqual(x_o_ns[time], 0.0017)

    def test_read_row_1_1_12_13(self):
        """
        按分のテスト
        """

        theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns = OutdoorCondition._load(rgn=Region.Region1, itv=Interval.M30)

        # 時刻 12 時 30 分のデータ
        time = 12 * 2 + 1

        # 外気温度
        self.assertAlmostEqual(theta_o_ns[time], -11.3 * 0.5 + -9.4 * 0.5)

        # 法線面直達日射
        self.assertAlmostEqual(i_dn_ns[time], 855.555555555556 * 0.5 + 791.666666666667 * 0.5)

        # 水平面天空日射
        self.assertAlmostEqual(i_sky_ns[time], 55.5555555555556 * 0.5 + 58.3333333333333 * 0.5)

        # 夜間放射量
        self.assertAlmostEqual(r_n_ns[time], 88.8888888888889 * 0.5 + 91.6666666666667 * 0.5)

        # 絶対湿度
        self.assertAlmostEqual(x_o_ns[time], 0.0015 * 0.5 + 0.0017 * 0.5)


class TestWeatherData1h(unittest.TestCase):

    def test_read_row_1_1_12(self):

        theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns = OutdoorCondition._load(rgn=Region.Region1, itv=Interval.H1)

        # 時刻 12 時のデータ
        time = 12

        # 外気温度
        self.assertEqual(theta_o_ns[time], -11.3)

        # 法線面直達日射
        self.assertEqual(i_dn_ns[time], 855.555555555556)

        # 水平面天空日射
        self.assertEqual(i_sky_ns[time], 55.5555555555556)

        # 夜間放射量
        self.assertEqual(r_n_ns[time], 88.8888888888889)

        # 絶対湿度
        self.assertEqual(x_o_ns[time], 0.0015)

    def test_read_row_1_1_13(self):

        theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns = OutdoorCondition._load(rgn=Region.Region1, itv=Interval.H1)

        # 時刻 13 時のデータ
        time = 13

        # 外気温度
        self.assertEqual(theta_o_ns[time], -9.4)

        # 法線面直達日射
        self.assertEqual(i_dn_ns[time], 791.666666666667)

        # 水平面天空日射
        self.assertEqual(i_sky_ns[time], 58.3333333333333)

        # 夜間放射量
        self.assertEqual(r_n_ns[time], 91.6666666666667)

        # 絶対湿度
        self.assertEqual(x_o_ns[time], 0.0017)


if __name__ == '__main__':
    unittest.main()
