import unittest
import numpy as np
import math

import heat_load_calc.solar_position as t
from heat_load_calc.interval import Interval


class TestSolarPosition(unittest.TestCase):

    def test_solar_position_values(self):

        # region 正解値の計算

        # 1時間を4分割した場合の 1/1 0:00 と 1/1 12:00, 1/2 12:00 の値をテストする。
        # n = [0, 48, 144]

        # 1968年との年差
        # 1989年で計算するため、 1989-1968 = 21
        # 平均軌道上の近日点通過日 d_0 = 3.1616
        d_0 = 3.71 + 0.2596 * 21 - int((21 + 3.0)/4.0)

        # 平均近点離角 m_n = [-0.03718378 -0.03718378 -0.01998181]
        # np.array の中の数字は、1/1, 1/1, 1/2 を表す。
        m_n = 2 * np.pi * (np.array([1, 1, 2]) - d_0) / 365.2596

        # 近日点と冬至点の角度 [12.75029538 12.75029538 12.75076014]
        epsilone_n = np.radians(12.3901 + 0.0172 * (21 + m_n / 2 * np.pi))

        # 真近点離角 [-0.03845158 -0.03845158 -0.02066322]
        v_n = m_n + (1.914 * np.sin(m_n) + 0.02 * np.sin(2 * m_n)) * np.pi / 180

        # 均時差 [-0.01159637 -0.01159637 -0.01373477]
        e_t = (m_n - v_n) - np.arctan(0.043 * np.sin(2.0 * (v_n + epsilone_n)) / (1.0 - 0.043 * np.cos(2.0 * (v_n + epsilone_n))))

        # 赤緯 [-0.40451804 -0.40451804 -0.40330219]
        delta_n = np.arcsin(np.cos(v_n + epsilone_n) * np.sin(np.radians(-23.4393)))

        # 標準時
        t_m = np.array([0, 48, 144]) * 0.25

        # 時角 [-2.99768019  9.56869043 34.69929325]
        # 経度は北見の143.91°とする。
        omega = (t_m - 12.0) * 15.0 * np.pi / 180.0 + np.radians(143.91) - np.radians(135.0) + e_t

        # 太陽高度
        h_sun = np.arcsin(np.sin(np.radians(43.82)) * np.sin(delta_n) + np.cos(np.radians(43.82)) * np.cos(delta_n) * np.cos(omega))

        # 太陽方位角
        a_sun = np.arctan2(
            np.cos(delta_n) * np.sin(omega) / np.cos(h_sun),
            (np.sin(h_sun) * np.sin(np.radians(43.82)) - np.sin(delta_n)) / (np.cos(h_sun) * np.cos(np.radians(43.82)))
        )

        # endregion

        # プログラムで計算された値（1時間間隔）
        h_sun_ns_1h, a_sun_ns_1h = t.calc_solar_position(
            phi_loc=math.radians(43.82),
            lambda_loc=math.radians(143.91),
            interval=Interval.H1
        )

        # プログラムで計算された値（15分間隔）
        h_sun_ns_30m, a_sun_ns_30m = t.calc_solar_position(
            phi_loc=math.radians(43.82),
            lambda_loc=math.radians(143.91),
            interval=Interval.M30
        )

        # プログラムで計算された値（15分間隔）
        h_sun_ns_15m, a_sun_ns_15m = t.calc_solar_position(
            phi_loc=math.radians(43.82),
            lambda_loc=math.radians(143.91),
            interval=Interval.M15
        )

        # 1/1 0:00
        self.assertAlmostEqual(h_sun[0], h_sun_ns_1h[0], delta=0.00001)
        self.assertAlmostEqual(a_sun[0], a_sun_ns_1h[0], delta=0.00001)
        self.assertAlmostEqual(h_sun[0], h_sun_ns_30m[0], delta=0.00001)
        self.assertAlmostEqual(a_sun[0], a_sun_ns_30m[0], delta=0.00001)
        self.assertAlmostEqual(h_sun[0], h_sun_ns_15m[0], delta=0.00001)
        self.assertAlmostEqual(a_sun[0], a_sun_ns_15m[0], delta=0.00001)

        # 1/1 12:00
        self.assertAlmostEqual(h_sun[1], h_sun_ns_1h[12], delta=0.00001)
        self.assertAlmostEqual(a_sun[1], a_sun_ns_1h[12], delta=0.00001)
        self.assertAlmostEqual(h_sun[1], h_sun_ns_30m[24], delta=0.00001)
        self.assertAlmostEqual(a_sun[1], a_sun_ns_30m[24], delta=0.00001)
        self.assertAlmostEqual(h_sun[1], h_sun_ns_15m[48], delta=0.00001)
        self.assertAlmostEqual(a_sun[1], a_sun_ns_15m[48], delta=0.00001)

        # 1/2 12:00
        self.assertAlmostEqual(h_sun[2], h_sun_ns_1h[36], delta=0.00001)
        self.assertAlmostEqual(a_sun[2], a_sun_ns_1h[36], delta=0.00001)
        self.assertAlmostEqual(h_sun[2], h_sun_ns_30m[72], delta=0.00001)
        self.assertAlmostEqual(a_sun[2], a_sun_ns_30m[72], delta=0.00001)
        self.assertAlmostEqual(h_sun[2], h_sun_ns_15m[144], delta=0.00001)
        self.assertAlmostEqual(a_sun[2], a_sun_ns_15m[144], delta=0.00001)

    def test_solar_position_length(self):

        # プログラムで計算された値
        h_sun_ns_1h, a_sun_ns_1h = t.calc_solar_position(
            phi_loc=math.radians(43.82),
            lambda_loc=math.radians(143.91),
            interval=Interval.H1
        )
        h_sun_ns_30m, a_sun_ns_30m = t.calc_solar_position(
            phi_loc=math.radians(43.82),
            lambda_loc=math.radians(143.91),
            interval=Interval.M30
        )
        h_sun_ns_15m, a_sun_ns_15m = t.calc_solar_position(
            phi_loc=math.radians(43.82),
            lambda_loc=math.radians(143.91),
            interval=Interval.M15
        )

        # 配列長さが、1時間間隔、8760 であることの確認
        self.assertEqual(8760, len(h_sun_ns_1h))
        self.assertEqual(8760, len(a_sun_ns_1h))

        # 配列長さが、30分間隔、8760 * 2 であることの確認
        self.assertEqual(8760 * 2, len(h_sun_ns_30m))
        self.assertEqual(8760 * 2, len(a_sun_ns_30m))

        # 配列長さが、15分間隔、8760*4 であることの確認
        self.assertEqual(8760 * 4, len(h_sun_ns_15m))
        self.assertEqual(8760 * 4, len(a_sun_ns_15m))


if __name__ == '__main__':
    unittest.main()
