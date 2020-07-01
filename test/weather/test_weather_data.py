import unittest

import heat_load_calc.weather.weather_data as t


class TestWeatherData(unittest.TestCase):

    def test_read_row_1_1_12(self):

        theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns = t.load(region=1)

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

        theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns = t.load(region=1)

        # 時刻 12 時のデータ
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

        theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns = t.load(region=1)

        # 時刻 12 時のデータ
        time = 12 * 4 + 1

        # 外気温度
        self.assertAlmostEqual(theta_o_ns[time], -11.3 * 0.75 + -9.4 * 0.25, delta=0.00000001)

        # 法線面直達日射
        self.assertAlmostEqual(i_dn_ns[time], 855.555555555556 * 0.75 + 791.666666666667 * 0.25, delta=0.00000001)

        # 水平面天空日射
        self.assertAlmostEqual(i_sky_ns[time], 55.5555555555556 * 0.75 + 58.3333333333333 * 0.25, delta=0.00000001)

        # 夜間放射量
        self.assertAlmostEqual(r_n_ns[time], 88.8888888888889 * 0.75 + 91.6666666666667 * 0.25, delta=0.00000001)

        # 絶対湿度
        self.assertAlmostEqual(x_o_ns[time], 0.0015 * 0.75 + 0.0017 * 0.25, delta=0.00000001)


if __name__ == '__main__':
    unittest.main()
