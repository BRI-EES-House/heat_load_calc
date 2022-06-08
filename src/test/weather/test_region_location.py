import unittest
import math

from heat_load_calc.region import Region


class TestRegionLocation(unittest.TestCase):

    def test_region_location(self):

        # 1地域（北見）
        lat, lon = Region.Region1.get_phi_loc_and_lambda_loc()
        self.assertEqual(lat, math.radians(43.82))
        self.assertEqual(lon, math.radians(143.91))

        # 2地域（岩見沢）
        lat, lon = Region.Region2.get_phi_loc_and_lambda_loc()
        self.assertEqual(lat, math.radians(43.21))
        self.assertEqual(lon, math.radians(141.79))

        # 3地域（盛岡）
        lat, lon = Region.Region3.get_phi_loc_and_lambda_loc()
        self.assertEqual(lat, math.radians(39.70))
        self.assertEqual(lon, math.radians(141.17))

        # 4地域（長野）
        lat, lon = Region.Region4.get_phi_loc_and_lambda_loc()
        self.assertEqual(lat, math.radians(36.66))
        self.assertEqual(lon, math.radians(138.20))

        # 5地域（宇都宮）
        lat, lon = Region.Region5.get_phi_loc_and_lambda_loc()
        self.assertEqual(lat, math.radians(36.55))
        self.assertEqual(lon, math.radians(139.87))

        # 6地域（岡山）
        lat, lon = Region.Region6.get_phi_loc_and_lambda_loc()
        self.assertEqual(lat, math.radians(34.66))
        self.assertEqual(lon, math.radians(133.92))

        # 7地域（宮崎）
        lat, lon = Region.Region7.get_phi_loc_and_lambda_loc()
        self.assertEqual(lat, math.radians(31.94))
        self.assertEqual(lon, math.radians(131.42))

        # 8地域（那覇）
        lat, lon = Region.Region8.get_phi_loc_and_lambda_loc()
        self.assertEqual(lat, math.radians(26.21))
        self.assertEqual(lon, math.radians(127.685))


if __name__ == '__main__':
    unittest.main()
