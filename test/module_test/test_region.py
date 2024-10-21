import unittest
import math

from heat_load_calc.region import Region


class TestRegionLocation(unittest.TestCase):

    def test_region_location(self):

        print('\n testing region module')

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

    def test_region_season_status(self):

        # region 1, Kitami
        winter_start, winter_end, summer_start, summer_end, is_summer_period_set, is_winter_period_set = Region.Region1.get_season_status() 
        self.assertEqual(winter_start, '9/24')
        self.assertEqual(winter_end, '6/7')
        self.assertEqual(summer_start, '7/10')
        self.assertEqual(summer_end, '8/30')
        self.assertEqual(is_summer_period_set, True)
        self.assertEqual(is_winter_period_set, True)

        # region 2, Iwamizawa
        winter_start, winter_end, summer_start, summer_end, is_summer_period_set, is_winter_period_set = Region.Region2.get_season_status() 
        self.assertEqual(winter_start, '9/26')
        self.assertEqual(winter_end, '6/4')
        self.assertEqual(summer_start, '7/15')
        self.assertEqual(summer_end, '8/31')
        self.assertEqual(is_summer_period_set, True)
        self.assertEqual(is_winter_period_set, True)

        # region 3, Morioka
        winter_start, winter_end, summer_start, summer_end, is_summer_period_set, is_winter_period_set = Region.Region3.get_season_status() 
        self.assertEqual(winter_start, '9/30')
        self.assertEqual(winter_end, '5/31')
        self.assertEqual(summer_start, '7/10')
        self.assertEqual(summer_end, '8/31')
        self.assertEqual(is_summer_period_set, True)
        self.assertEqual(is_winter_period_set, True)

        # region 4, Nagano
        winter_start, winter_end, summer_start, summer_end, is_summer_period_set, is_winter_period_set = Region.Region4.get_season_status() 
        self.assertEqual(winter_start, '10/1')
        self.assertEqual(winter_end, '5/30')
        self.assertEqual(summer_start, '7/10')
        self.assertEqual(summer_end, '8/31')
        self.assertEqual(is_summer_period_set, True)
        self.assertEqual(is_winter_period_set, True)

        # region 5, Utsunomiya
        winter_start, winter_end, summer_start, summer_end, is_summer_period_set, is_winter_period_set = Region.Region5.get_season_status() 
        self.assertEqual(winter_start, '10/10')
        self.assertEqual(winter_end, '5/15')
        self.assertEqual(summer_start, '7/6')
        self.assertEqual(summer_end, '8/31')
        self.assertEqual(is_summer_period_set, True)
        self.assertEqual(is_winter_period_set, True)

        # region 6, Okayama
        winter_start, winter_end, summer_start, summer_end, is_summer_period_set, is_winter_period_set = Region.Region6.get_season_status() 
        self.assertEqual(winter_start, '11/4')
        self.assertEqual(winter_end, '4/21')
        self.assertEqual(summer_start, '5/30')
        self.assertEqual(summer_end, '9/23')
        self.assertEqual(is_summer_period_set, True)
        self.assertEqual(is_winter_period_set, True)

        # region 7, Miyazaki
        winter_start, winter_end, summer_start, summer_end, is_summer_period_set, is_winter_period_set = Region.Region7.get_season_status() 
        self.assertEqual(winter_start, '11/26')
        self.assertEqual(winter_end, '3/27')
        self.assertEqual(summer_start, '5/15')
        self.assertEqual(summer_end, '10/13')
        self.assertEqual(is_summer_period_set, True)
        self.assertEqual(is_winter_period_set, True)

        # region 8, Naha
        winter_start, winter_end, summer_start, summer_end, is_summer_period_set, is_winter_period_set = Region.Region8.get_season_status() 
        self.assertEqual(winter_start, None)
        self.assertEqual(winter_end, None)
        self.assertEqual(summer_start, '3/25')
        self.assertEqual(summer_end, '12/14')
        self.assertEqual(is_summer_period_set, True)
        self.assertEqual(is_winter_period_set, False)


if __name__ == '__main__':
    unittest.main()
