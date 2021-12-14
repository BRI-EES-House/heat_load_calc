import unittest
import math

from heat_load_calc.weather import region_location as t


class TestRegionLocation(unittest.TestCase):

    def test_region_location(self):

        # 1地域（北見）
        lat, lon = t.get_phi_loc_and_lambda_loc(region=1)
        self.assertEqual(lat, math.radians(43.82))
        self.assertEqual(lon, math.radians(143.91))

        # 2地域（岩見沢）
        lat, lon = t.get_phi_loc_and_lambda_loc(region=2)
        self.assertEqual(lat, math.radians(43.21))
        self.assertEqual(lon, math.radians(141.79))

        # 3地域（盛岡）
        lat, lon = t.get_phi_loc_and_lambda_loc(region=3)
        self.assertEqual(lat, math.radians(39.70))
        self.assertEqual(lon, math.radians(141.17))

        # 4地域（長野）
        lat, lon = t.get_phi_loc_and_lambda_loc(region=4)
        self.assertEqual(lat, math.radians(36.66))
        self.assertEqual(lon, math.radians(138.20))

        # 5地域（宇都宮）
        lat, lon = t.get_phi_loc_and_lambda_loc(region=5)
        self.assertEqual(lat, math.radians(36.55))
        self.assertEqual(lon, math.radians(139.87))

        # 6地域（岡山）
        lat, lon = t.get_phi_loc_and_lambda_loc(region=6)
        self.assertEqual(lat, math.radians(34.66))
        self.assertEqual(lon, math.radians(133.92))

        # 7地域（宮崎）
        lat, lon = t.get_phi_loc_and_lambda_loc(region=7)
        self.assertEqual(lat, math.radians(31.94))
        self.assertEqual(lon, math.radians(131.42))

        # 8地域（那覇）
        lat, lon = t.get_phi_loc_and_lambda_loc(region=8)
        self.assertEqual(lat, math.radians(26.21))
        self.assertEqual(lon, math.radians(127.685))


if __name__ == '__main__':
    unittest.main()
