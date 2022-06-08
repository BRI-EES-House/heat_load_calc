import unittest
import math

from heat_load_calc import region


class TestRegionLocation(unittest.TestCase):

    def test_region_location(self):

        # 1地域（北見）
        lat, lon = region.get_phi_loc_and_lambda_loc(rgn=region.Region.Region1)
        self.assertEqual(lat, math.radians(43.82))
        self.assertEqual(lon, math.radians(143.91))

        # 2地域（岩見沢）
        lat, lon = region.get_phi_loc_and_lambda_loc(rgn=region.Region.Region2)
        self.assertEqual(lat, math.radians(43.21))
        self.assertEqual(lon, math.radians(141.79))

        # 3地域（盛岡）
        lat, lon = region.get_phi_loc_and_lambda_loc(rgn=region.Region.Region3)
        self.assertEqual(lat, math.radians(39.70))
        self.assertEqual(lon, math.radians(141.17))

        # 4地域（長野）
        lat, lon = region.get_phi_loc_and_lambda_loc(rgn=region.Region.Region4)
        self.assertEqual(lat, math.radians(36.66))
        self.assertEqual(lon, math.radians(138.20))

        # 5地域（宇都宮）
        lat, lon = region.get_phi_loc_and_lambda_loc(rgn=region.Region.Region5)
        self.assertEqual(lat, math.radians(36.55))
        self.assertEqual(lon, math.radians(139.87))

        # 6地域（岡山）
        lat, lon = region.get_phi_loc_and_lambda_loc(rgn=region.Region.Region6)
        self.assertEqual(lat, math.radians(34.66))
        self.assertEqual(lon, math.radians(133.92))

        # 7地域（宮崎）
        lat, lon = region.get_phi_loc_and_lambda_loc(rgn=region.Region.Region7)
        self.assertEqual(lat, math.radians(31.94))
        self.assertEqual(lon, math.radians(131.42))

        # 8地域（那覇）
        lat, lon = region.get_phi_loc_and_lambda_loc(rgn=region.Region.Region8)
        self.assertEqual(lat, math.radians(26.21))
        self.assertEqual(lon, math.radians(127.685))


if __name__ == '__main__':
    unittest.main()
