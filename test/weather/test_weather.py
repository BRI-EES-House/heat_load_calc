import unittest

import heat_load_calc.weather.weather as t


class TestWeather(unittest.TestCase):

    def test_weather_values_solar_position(self):

        # データの取得
        d = t.make_weather(region=1)

        # 1/1 0:00
        self.assertAlmostEqual(d['sun altitude [rad]']['1989-01-01 00:00:00'], -1.18973183, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth [rad]']['1989-01-01 00:00:00'], -2.78729204, delta=0.00001)

        # 1/1 12:00
        self.assertAlmostEqual(d['sun altitude [rad]']['1989-01-01 12:00:00'], 0.39709158, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth [rad]']['1989-01-01 12:00:00'], 0.14037539, delta=0.00001)

        # 1/2 12:00
        self.assertAlmostEqual(d['sun altitude [rad]']['1989-01-02 12:00:00'], 0.39876328, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth [rad]']['1989-01-02 12:00:00'], 0.13851202, delta=0.00001)

    def test_weather_values(self):

        d = t.make_weather(region=1)

        # 外気温度
        self.assertEqual(d['temperature [degree C]']['1989-01-01 12:00:00'], -11.3)
        self.assertEqual(d['temperature [degree C]']['1989-01-01 13:00:00'], -9.4)
        self.assertAlmostEqual(
            d['temperature [degree C]']['1989-01-01 12:15:00'],
            -11.3 * 0.75 + -9.4 * 0.25, delta=0.00000001)

        # 法線面直達日射
        self.assertEqual(d['normal direct solar radiation [W/m2]']['1989-01-01 12:00:00'], 855.555555555556)
        self.assertEqual(d['normal direct solar radiation [W/m2]']['1989-01-01 13:00:00'], 791.666666666667)
        self.assertAlmostEqual(
            d['normal direct solar radiation [W/m2]']['1989-01-01 12:15:00'],
            855.555555555556 * 0.75 + 791.666666666667 * 0.25, delta=0.00000001)

        # 水平面天空日射
        self.assertEqual(d['horizontal sky solar radiation [W/m2]']['1989-01-01 12:00:00'], 55.5555555555556)
        self.assertEqual(d['horizontal sky solar radiation [W/m2]']['1989-01-01 13:00:00'], 58.3333333333333)
        self.assertAlmostEqual(
            d['horizontal sky solar radiation [W/m2]']['1989-01-01 12:15:00'],
            55.5555555555556 * 0.75 + 58.3333333333333 * 0.25, delta=0.00000001)

        # 夜間放射量
        self.assertEqual(d['outward radiation [W/m2]']['1989-01-01 12:00:00'], 88.8888888888889)
        self.assertEqual(d['outward radiation [W/m2]']['1989-01-01 13:00:00'], 91.6666666666667)
        self.assertAlmostEqual(
            d['outward radiation [W/m2]']['1989-01-01 12:15:00'],
            88.8888888888889 * 0.75 + 91.6666666666667 * 0.25, delta=0.00000001)

        # 絶対湿度
        self.assertEqual(d['absolute humidity [kg/kg(DA)]']['1989-01-01 12:00:00'], 0.0015)
        self.assertEqual(d['absolute humidity [kg/kg(DA)]']['1989-01-01 13:00:00'], 0.0017)
        self.assertAlmostEqual(
            d['absolute humidity [kg/kg(DA)]']['1989-01-01 12:15:00'],
            0.0015 * 0.75 + 0.0017 * 0.25, delta=0.00000001)


if __name__ == '__main__':
    unittest.main()
