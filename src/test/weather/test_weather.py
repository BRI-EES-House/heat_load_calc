import unittest

from heat_load_calc.outdoor_condition import OutdoorCondition
from heat_load_calc.weather.interval import Interval


class TestWeather(unittest.TestCase):

    def test_weather_values_solar_position(self):

        # データの取得
        oc = OutdoorCondition.make_weather(method="ees", itv=Interval.M15, region=1)
        d = oc.get_weather_as_pandas_data_frame()

        # 1/1 0:00
        self.assertAlmostEqual(d['sun altitude']['1989-01-01 00:00:00'], -1.18973183, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth']['1989-01-01 00:00:00'], -2.78729204, delta=0.00001)

        # 1/1 12:00
        self.assertAlmostEqual(d['sun altitude']['1989-01-01 12:00:00'], 0.39709158, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth']['1989-01-01 12:00:00'], 0.14037539, delta=0.00001)

        # 1/2 12:00
        self.assertAlmostEqual(d['sun altitude']['1989-01-02 12:00:00'], 0.39876328, delta=0.00001)
        self.assertAlmostEqual(d['sun azimuth']['1989-01-02 12:00:00'], 0.13851202, delta=0.00001)

    def test_weather_values(self):

        # データの取得
        oc = OutdoorCondition.make_weather(method="ees", itv=Interval.M15, region=1)
        d = oc.get_weather_as_pandas_data_frame()

        # 外気温度
        self.assertEqual(d['temperature']['1989-01-01 12:00:00'], -11.3)
        self.assertEqual(d['temperature']['1989-01-01 13:00:00'], -9.4)
        self.assertAlmostEqual(
            d['temperature']['1989-01-01 12:15:00'],
            -11.3 * 0.75 + -9.4 * 0.25, delta=0.00000001)

        # 法線面直達日射
        self.assertEqual(d['normal direct solar radiation']['1989-01-01 12:00:00'], 855.555555555556)
        self.assertEqual(d['normal direct solar radiation']['1989-01-01 13:00:00'], 791.666666666667)
        self.assertAlmostEqual(
            d['normal direct solar radiation']['1989-01-01 12:15:00'],
            855.555555555556 * 0.75 + 791.666666666667 * 0.25, delta=0.00000001)

        # 水平面天空日射
        self.assertEqual(d['horizontal sky solar radiation']['1989-01-01 12:00:00'], 55.5555555555556)
        self.assertEqual(d['horizontal sky solar radiation']['1989-01-01 13:00:00'], 58.3333333333333)
        self.assertAlmostEqual(
            d['horizontal sky solar radiation']['1989-01-01 12:15:00'],
            55.5555555555556 * 0.75 + 58.3333333333333 * 0.25, delta=0.00000001)

        # 夜間放射量
        self.assertEqual(d['outward radiation']['1989-01-01 12:00:00'], 88.8888888888889)
        self.assertEqual(d['outward radiation']['1989-01-01 13:00:00'], 91.6666666666667)
        self.assertAlmostEqual(
            d['outward radiation']['1989-01-01 12:15:00'],
            88.8888888888889 * 0.75 + 91.6666666666667 * 0.25, delta=0.00000001)

        # 絶対湿度
        self.assertEqual(d['absolute humidity']['1989-01-01 12:00:00'], 0.0015)
        self.assertEqual(d['absolute humidity']['1989-01-01 13:00:00'], 0.0017)
        self.assertAlmostEqual(
            d['absolute humidity']['1989-01-01 12:15:00'],
            0.0015 * 0.75 + 0.0017 * 0.25, delta=0.00000001)


if __name__ == '__main__':
    unittest.main()
