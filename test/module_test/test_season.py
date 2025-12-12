import unittest
import numpy as np
import pytest

from heat_load_calc import season


class TestSeason(unittest.TestCase):

    def assert_season(self, summer, winter, middle, i, s):
        if s == "summer":
            self.assertEqual(summer[i], True)
            self.assertEqual(winter[i], False)
            self.assertEqual(middle[i], False)
        elif s == "winter":
            self.assertEqual(summer[i], False)
            self.assertEqual(winter[i], True)
            self.assertEqual(middle[i], False)
        elif s == "middle":
            self.assertEqual(summer[i], False)
            self.assertEqual(winter[i], False)
            self.assertEqual(middle[i], True)
        else:
            raise Exception()

    def test_get_total_day(self):

        self.assertEqual(1, season._get_total_day(date_str="1/1"))
        self.assertEqual(2, season._get_total_day(date_str="1/2"))
        
        self.assertEqual(364, season._get_total_day(date_str="12/30"))

    def test_get_bool_list_by_start_day(self):

        blist1: np.ndarray = season._get_bool_list_by_start_day(n=1)

        self.assertEqual(len(blist1), 365)
        self.assertEqual(blist1[0], True)
        self.assertEqual(blist1[1], True)
        self.assertEqual(blist1[2], True)
        self.assertEqual(blist1[3], True)

        blist3: np.ndarray = season._get_bool_list_by_start_day(n=3)

        self.assertEqual(blist3[0], False)
        self.assertEqual(blist3[1], False)
        self.assertEqual(blist3[2], True)
        self.assertEqual(blist3[3], True)

        blist365: np.ndarray = season._get_bool_list_by_start_day(n=365)

        self.assertEqual(blist365[363], False)
        self.assertEqual(blist365[364], True)

    def test_get_bool_list_by_end_day(self):

        blist1: np.ndarray = season._get_bool_list_by_end_day(n=1)

        self.assertEqual(len(blist1), 365)
        self.assertEqual(blist1[0], True)
        self.assertEqual(blist1[1], False)
        self.assertEqual(blist1[2], False)

        blist1: np.ndarray = season._get_bool_list_by_end_day(n=3)

        self.assertEqual(len(blist1), 365)
        self.assertEqual(blist1[0], True)
        self.assertEqual(blist1[1], True)
        self.assertEqual(blist1[2], True)
        self.assertEqual(blist1[3], False)

    def test_get_bool_list_by_start_day_index_error(self):

        # the value should be more than 0.
        with  pytest.raises(IndexError):
            blist: np.ndarray = season._get_bool_list_by_start_day(n=0)
        
        blist: np.ndarray = season._get_bool_list_by_start_day(n=1)
        
        blist: np.ndarray = season._get_bool_list_by_start_day(n=365)

        # the value should be less than 366.
        with  pytest.raises(IndexError):
            blist: np.ndarray = season._get_bool_list_by_start_day(n=366)

    def test_get_bool_list_by_start_day_and_end_day(self):

        blist1 = season._get_bool_list_by_start_day_and_end_day(nstart=100, nend=200)

        self.assertEqual(blist1[0], False)
        self.assertEqual(blist1[98], False)
        self.assertEqual(blist1[99], True)
        self.assertEqual(blist1[199], True)
        self.assertEqual(blist1[200], False)
        self.assertEqual(blist1[364], False)

        blist2 = season._get_bool_list_by_start_day_and_end_day(nstart=200, nend=100)

        self.assertEqual(blist2[0], True)
        self.assertEqual(blist2[99], True)
        self.assertEqual(blist2[100], False)
        self.assertEqual(blist2[198], False)
        self.assertEqual(blist2[199], True)
        self.assertEqual(blist2[364], True)

    def test_get_bool_list_for_four_season_as_int(self):

        assert_season = self.assert_season

        summer, winter, middle = season._get_bool_list_for_four_season_as_int(summer_start=100, summer_end=150, winter_start=200, winter_end=250)

        self.assertEqual(np.all(summer | winter | middle), True)

        assert_season(summer, winter, middle, 0, "middle")
        assert_season(summer, winter, middle, 98, "middle")
        assert_season(summer, winter, middle, 99, "summer")
        assert_season(summer, winter, middle, 100, "summer")
        assert_season(summer, winter, middle, 148, "summer")
        assert_season(summer, winter, middle, 149, "summer")
        assert_season(summer, winter, middle, 150, "middle")
        assert_season(summer, winter, middle, 198, "middle")
        assert_season(summer, winter, middle, 199, "winter")
        assert_season(summer, winter, middle, 200, "winter")
        assert_season(summer, winter, middle, 248, "winter")
        assert_season(summer, winter, middle, 249, "winter")
        assert_season(summer, winter, middle, 250, "middle")
        assert_season(summer, winter, middle, 364, "middle")
        
        with pytest.raises(ValueError):
            _ = season._get_bool_list_for_four_season_as_int(summer_start=100, summer_end=150, winter_end=200, winter_start=250)

        with pytest.raises(ValueError):
            _ = season._get_bool_list_for_four_season_as_int(summer_start=100, winter_start=150, summer_end=200, winter_end=250)
        
        with pytest.raises(ValueError):
            _ = season._get_bool_list_for_four_season_as_int(summer_start=100, winter_start=150, winter_end=200, summer_end=250)
        
        with pytest.raises(ValueError):
            _ = season._get_bool_list_for_four_season_as_int(summer_start=100, winter_end=150, summer_end=200, winter_start=250)

        with pytest.raises(ValueError):
            _ = season._get_bool_list_for_four_season_as_int(summer_start=100, winter_end=150, winter_start=200, summer_end=250)

        with pytest.raises(ValueError):
            _ = season._get_bool_list_for_four_season_as_int(summer_end=100, summer_start=150, winter_start=200, winter_end=250)

        with pytest.raises(ValueError):
            _ = season._get_bool_list_for_four_season_as_int(summer_end=100, summer_start=150, winter_end=200, winter_start=250)

        with pytest.raises(ValueError):
            _ = season._get_bool_list_for_four_season_as_int(summer_end=100, winter_start=150, summer_start=200, winter_end=250)

        summer, winter, middle = season._get_bool_list_for_four_season_as_int(summer_end=100, winter_start=150, winter_end=200, summer_start=250)

        self.assertEqual(np.all(summer | winter | middle), True)

        assert_season(summer, winter, middle, 0, "summer")
        assert_season(summer, winter, middle, 98, "summer")
        assert_season(summer, winter, middle, 99, "summer")
        assert_season(summer, winter, middle, 100, "middle")
        assert_season(summer, winter, middle, 148, "middle")
        assert_season(summer, winter, middle, 149, "winter")
        assert_season(summer, winter, middle, 150, "winter")
        assert_season(summer, winter, middle, 198, "winter")
        assert_season(summer, winter, middle, 199, "winter")
        assert_season(summer, winter, middle, 200, "middle")
        assert_season(summer, winter, middle, 248, "middle")
        assert_season(summer, winter, middle, 249, "summer")
        assert_season(summer, winter, middle, 250, "summer")
        assert_season(summer, winter, middle, 364, "summer")

        with pytest.raises(ValueError):
            _ = season._get_bool_list_for_four_season_as_int(summer_end=100, winter_end=150, summer_start=200, winter_start=250)

        with pytest.raises(ValueError):
            _ = season._get_bool_list_for_four_season_as_int(summer_end=100, winter_end=150, winter_start=200, summer_start=250)

        with pytest.raises(ValueError):
            _ = season._get_bool_list_for_four_season_as_int(winter_start=100, summer_start=150, summer_end=200, winter_end=250)

        with pytest.raises(ValueError):
            _ = season._get_bool_list_for_four_season_as_int(winter_start=100, summer_start=150, winter_end=200, summer_end=250)

        with pytest.raises(ValueError):
            _ = season._get_bool_list_for_four_season_as_int(winter_start=100, summer_end=150, summer_start=200, winter_end=250)

        with pytest.raises(ValueError):
            _ = season._get_bool_list_for_four_season_as_int(winter_start=100, summer_end=150, winter_end=200, summer_start=250)

        summer, winter, middle = season._get_bool_list_for_four_season_as_int(winter_start=100, winter_end=150, summer_start=200, summer_end=250)

        self.assertEqual(np.all(summer | winter | middle), True)

        assert_season(summer, winter, middle, 0, "middle")
        assert_season(summer, winter, middle, 98, "middle")
        assert_season(summer, winter, middle, 99, "winter")
        assert_season(summer, winter, middle, 100, "winter")
        assert_season(summer, winter, middle, 148, "winter")
        assert_season(summer, winter, middle, 149, "winter")
        assert_season(summer, winter, middle, 150, "middle")
        assert_season(summer, winter, middle, 198, "middle")
        assert_season(summer, winter, middle, 199, "summer")
        assert_season(summer, winter, middle, 200, "summer")
        assert_season(summer, winter, middle, 248, "summer")
        assert_season(summer, winter, middle, 249, "summer")
        assert_season(summer, winter, middle, 250, "middle")
        assert_season(summer, winter, middle, 364, "middle")

        with pytest.raises(ValueError):
            _ = season._get_bool_list_for_four_season_as_int(winter_start=100, winter_end=150, summer_end=200, summer_start=250)


        summer, winter, middle = season._get_bool_list_for_four_season_as_int(winter_end=100, summer_start=150, summer_end=200, winter_start=250)

        self.assertEqual(np.all(summer | winter | middle), True)

        assert_season(summer, winter, middle, 0, "winter")
        assert_season(summer, winter, middle, 98, "winter")
        assert_season(summer, winter, middle, 99, "winter")
        assert_season(summer, winter, middle, 100, "middle")
        assert_season(summer, winter, middle, 148, "middle")
        assert_season(summer, winter, middle, 149, "summer")
        assert_season(summer, winter, middle, 150, "summer")
        assert_season(summer, winter, middle, 198, "summer")
        assert_season(summer, winter, middle, 199, "summer")
        assert_season(summer, winter, middle, 200, "middle")
        assert_season(summer, winter, middle, 248, "middle")
        assert_season(summer, winter, middle, 249, "winter")
        assert_season(summer, winter, middle, 250, "winter")
        assert_season(summer, winter, middle, 364, "winter")

        with pytest.raises(ValueError):
            _ = season._get_bool_list_for_four_season_as_int(winter_end=100, summer_start=150, winter_start=200, summer_end=250)

        with pytest.raises(ValueError):
            _ = season._get_bool_list_for_four_season_as_int(winter_end=100, summer_end=150, summer_start=200, winter_start=250)

        with pytest.raises(ValueError):
            _ = season._get_bool_list_for_four_season_as_int(winter_end=100, summer_end=150, winter_start=200, summer_start=250)

        with pytest.raises(ValueError):
            _ = season._get_bool_list_for_four_season_as_int(winter_end=100, winter_start=150, summer_start=200, summer_end=250)

        with pytest.raises(ValueError):
            _ = season._get_bool_list_for_four_season_as_int(winter_end=100, winter_start=150, summer_end=200, summer_start=250)


        summer, winter, middle = season._get_bool_list_for_four_season_as_int(summer_start=1, summer_end=199, winter_start=200, winter_end=365)

        self.assertEqual(np.all(summer | winter | middle), True)

        assert_season(summer, winter, middle, 0, "summer")
        assert_season(summer, winter, middle, 197, "summer")
        assert_season(summer, winter, middle, 198, "summer")
        assert_season(summer, winter, middle, 199, "winter")
        assert_season(summer, winter, middle, 200, "winter")
        assert_season(summer, winter, middle, 364, "winter")

        summer, winter, middle = season._get_bool_list_for_four_season_as_int(summer_end=149, winter_start=150, winter_end=249, summer_start=250)

        self.assertEqual(np.all(summer | winter | middle), True)

        assert_season(summer, winter, middle, 0, "summer")
        assert_season(summer, winter, middle, 147, "summer")
        assert_season(summer, winter, middle, 148, "summer")
        assert_season(summer, winter, middle, 149, "winter")
        assert_season(summer, winter, middle, 247, "winter")
        assert_season(summer, winter, middle, 248, "winter")
        assert_season(summer, winter, middle, 249, "summer")
        assert_season(summer, winter, middle, 364, "summer")

        summer, winter, middle = season._get_bool_list_for_four_season_as_int(winter_start=1, winter_end=199, summer_start=200, summer_end=365)

        self.assertEqual(np.all(summer | winter | middle), True)

        assert_season(summer, winter, middle, 0, "winter")
        assert_season(summer, winter, middle, 198, "winter")
        assert_season(summer, winter, middle, 199, "summer")
        assert_season(summer, winter, middle, 200, "summer")
        assert_season(summer, winter, middle, 364, "summer")

        summer, winter, middle = season._get_bool_list_for_four_season_as_int(winter_end=149, summer_start=150, summer_end=249, winter_start=250)

        self.assertEqual(np.all(summer | winter | middle), True)

        assert_season(summer, winter, middle, 0, "winter")
        assert_season(summer, winter, middle, 147, "winter")
        assert_season(summer, winter, middle, 148, "winter")
        assert_season(summer, winter, middle, 149, "summer")
        assert_season(summer, winter, middle, 247, "summer")
        assert_season(summer, winter, middle, 248, "summer")
        assert_season(summer, winter, middle, 249, "winter")
        assert_season(summer, winter, middle, 364, "winter")

        summer, winter, middle = season._get_bool_list_for_four_season_as_int(summer_start=10, summer_end=80, is_winter_period_set=False)

        self.assertEqual(np.all(summer | winter | middle), True)

        assert_season(summer, winter, middle, 0, "middle")
        assert_season(summer, winter, middle, 7, "middle")
        assert_season(summer, winter, middle, 8, "middle")
        assert_season(summer, winter, middle, 9, "summer")
        assert_season(summer, winter, middle, 78, "summer")
        assert_season(summer, winter, middle, 79, "summer")
        assert_season(summer, winter, middle, 80, "middle")
        assert_season(summer, winter, middle, 364, "middle")

        summer, winter, middle = season._get_bool_list_for_four_season_as_int(winter_start=270, winter_end=300, is_summer_period_set=False)

        self.assertEqual(np.all(summer | winter | middle), True)

        assert_season(summer, winter, middle, 0, "middle")
        assert_season(summer, winter, middle, 267, "middle")
        assert_season(summer, winter, middle, 268, "middle")
        assert_season(summer, winter, middle, 269, "winter")
        assert_season(summer, winter, middle, 298, "winter")
        assert_season(summer, winter, middle, 299, "winter")
        assert_season(summer, winter, middle, 300, "middle")
        assert_season(summer, winter, middle, 364, "middle")


    def test_get_bool_list_for_four_season_as_str(self):

        assert_season = self.assert_season

        summer, winter, middle = season._get_bool_list_for_season_as_str(summer_start="4/10", summer_end="5/30", winter_start="7/19", winter_end="9/7")

        self.assertEqual(np.all(summer | winter | middle), True)
        self.assertEqual(np.all(summer & winter & middle), False)

        assert_season(summer, winter, middle, 0, "middle")
        assert_season(summer, winter, middle, 98, "middle")
        assert_season(summer, winter, middle, 99, "summer")
        assert_season(summer, winter, middle, 100, "summer")
        assert_season(summer, winter, middle, 148, "summer")
        assert_season(summer, winter, middle, 149, "summer")
        assert_season(summer, winter, middle, 150, "middle")
        assert_season(summer, winter, middle, 198, "middle")
        assert_season(summer, winter, middle, 199, "winter")
        assert_season(summer, winter, middle, 200, "winter")
        assert_season(summer, winter, middle, 248, "winter")
        assert_season(summer, winter, middle, 249, "winter")
        assert_season(summer, winter, middle, 250, "middle")
        assert_season(summer, winter, middle, 364, "middle")


        summer, winter, middle = season._get_bool_list_for_season_as_str(summer_end="4/10", winter_start="5/30", winter_end="7/19", summer_start="9/7")

        self.assertEqual(np.all(summer | winter | middle), True)
        self.assertEqual(np.all(summer & winter & middle), False)

        assert_season(summer, winter, middle, 0, "summer")
        assert_season(summer, winter, middle, 98, "summer")
        assert_season(summer, winter, middle, 99, "summer")
        assert_season(summer, winter, middle, 100, "middle")
        assert_season(summer, winter, middle, 148, "middle")
        assert_season(summer, winter, middle, 149, "winter")
        assert_season(summer, winter, middle, 150, "winter")
        assert_season(summer, winter, middle, 198, "winter")
        assert_season(summer, winter, middle, 199, "winter")
        assert_season(summer, winter, middle, 200, "middle")
        assert_season(summer, winter, middle, 248, "middle")
        assert_season(summer, winter, middle, 249, "summer")
        assert_season(summer, winter, middle, 250, "summer")
        assert_season(summer, winter, middle, 364, "summer")

        summer, winter, middle = season._get_bool_list_for_season_as_str(winter_start="4/10", winter_end="5/30", summer_start="7/19", summer_end="9/7")

        self.assertEqual(np.all(summer | winter | middle), True)
        self.assertEqual(np.all(summer & winter & middle), False)

        assert_season(summer, winter, middle, 0, "middle")
        assert_season(summer, winter, middle, 98, "middle")
        assert_season(summer, winter, middle, 99, "winter")
        assert_season(summer, winter, middle, 100, "winter")
        assert_season(summer, winter, middle, 148, "winter")
        assert_season(summer, winter, middle, 149, "winter")
        assert_season(summer, winter, middle, 150, "middle")
        assert_season(summer, winter, middle, 198, "middle")
        assert_season(summer, winter, middle, 199, "summer")
        assert_season(summer, winter, middle, 200, "summer")
        assert_season(summer, winter, middle, 248, "summer")
        assert_season(summer, winter, middle, 249, "summer")
        assert_season(summer, winter, middle, 250, "middle")
        assert_season(summer, winter, middle, 364, "middle")

        summer, winter, middle = season._get_bool_list_for_season_as_str(winter_end="4/10", summer_start="5/30", summer_end="7/19", winter_start="9/7")

        self.assertEqual(np.all(summer | winter | middle), True)
        self.assertEqual(np.all(summer & winter & middle), False)

        assert_season(summer, winter, middle, 0, "winter")
        assert_season(summer, winter, middle, 98, "winter")
        assert_season(summer, winter, middle, 99, "winter")
        assert_season(summer, winter, middle, 100, "middle")
        assert_season(summer, winter, middle, 148, "middle")
        assert_season(summer, winter, middle, 149, "summer")
        assert_season(summer, winter, middle, 150, "summer")
        assert_season(summer, winter, middle, 198, "summer")
        assert_season(summer, winter, middle, 199, "summer")
        assert_season(summer, winter, middle, 200, "middle")
        assert_season(summer, winter, middle, 248, "middle")
        assert_season(summer, winter, middle, 249, "winter")
        assert_season(summer, winter, middle, 250, "winter")
        assert_season(summer, winter, middle, 364, "winter")

        summer, winter, middle = season._get_bool_list_for_season_as_str(summer_start="1/1", summer_end="7/18", winter_start="7/19", winter_end="12/31")

        self.assertEqual(np.all(summer | winter | middle), True)
        self.assertEqual(np.all(summer & winter & middle), False)

        assert_season(summer, winter, middle, 0, "summer")
        assert_season(summer, winter, middle, 197, "summer")
        assert_season(summer, winter, middle, 198, "summer")
        assert_season(summer, winter, middle, 199, "winter")
        assert_season(summer, winter, middle, 200, "winter")
        assert_season(summer, winter, middle, 364, "winter")

        summer, winter, middle = season._get_bool_list_for_season_as_str(summer_end="5/29", winter_start="5/30", winter_end="9/6", summer_start="9/7")

        self.assertEqual(np.all(summer | winter | middle), True)
        self.assertEqual(np.all(summer & winter & middle), False)

        assert_season(summer, winter, middle, 0, "summer")
        assert_season(summer, winter, middle, 147, "summer")
        assert_season(summer, winter, middle, 148, "summer")
        assert_season(summer, winter, middle, 149, "winter")
        assert_season(summer, winter, middle, 247, "winter")
        assert_season(summer, winter, middle, 248, "winter")
        assert_season(summer, winter, middle, 249, "summer")
        assert_season(summer, winter, middle, 364, "summer")

        summer, winter, middle = season._get_bool_list_for_season_as_str(winter_start="1/1", winter_end="7/18", summer_start="7/19", summer_end="12/31")

        self.assertEqual(np.all(summer | winter | middle), True)
        self.assertEqual(np.all(summer & winter & middle), False)

        assert_season(summer, winter, middle, 0, "winter")
        assert_season(summer, winter, middle, 198, "winter")
        assert_season(summer, winter, middle, 199, "summer")
        assert_season(summer, winter, middle, 200, "summer")
        assert_season(summer, winter, middle, 364, "summer")

        summer, winter, middle = season._get_bool_list_for_season_as_str(winter_end="5/29", summer_start="5/30", summer_end="9/6", winter_start="9/7")

        self.assertEqual(np.all(summer | winter | middle), True)
        self.assertEqual(np.all(summer & winter & middle), False)

        assert_season(summer, winter, middle, 0, "winter")
        assert_season(summer, winter, middle, 147, "winter")
        assert_season(summer, winter, middle, 148, "winter")
        assert_season(summer, winter, middle, 149, "summer")
        assert_season(summer, winter, middle, 247, "summer")
        assert_season(summer, winter, middle, 248, "summer")
        assert_season(summer, winter, middle, 249, "winter")
        assert_season(summer, winter, middle, 364, "winter")

        summer, winter, middle = season._get_bool_list_for_season_as_str(summer_start="5/30", summer_end="9/6", is_winter_period_set=False)

        self.assertEqual(np.all(summer | winter | middle), True)
        self.assertEqual(np.all(summer & winter & middle), False)

        assert_season(summer, winter, middle, 0, "middle")
        assert_season(summer, winter, middle, 147, "middle")
        assert_season(summer, winter, middle, 148, "middle")
        assert_season(summer, winter, middle, 149, "summer")
        assert_season(summer, winter, middle, 247, "summer")
        assert_season(summer, winter, middle, 248, "summer")
        assert_season(summer, winter, middle, 249, "middle")
        assert_season(summer, winter, middle, 364, "middle")

        summer, winter, middle = season._get_bool_list_for_season_as_str(winter_end="5/29", winter_start="9/7", is_summer_period_set=False)

        self.assertEqual(np.all(summer | winter | middle), True)
        self.assertEqual(np.all(summer & winter & middle), False)

        assert_season(summer, winter, middle, 0, "winter")
        assert_season(summer, winter, middle, 147, "winter")
        assert_season(summer, winter, middle, 148, "winter")
        assert_season(summer, winter, middle, 149, "middle")
        assert_season(summer, winter, middle, 247, "middle")
        assert_season(summer, winter, middle, 248, "middle")
        assert_season(summer, winter, middle, 249, "winter")
        assert_season(summer, winter, middle, 364, "winter")

    def test_make_season_season_specified_error(self):

        d_common_1 = {
            'season': {}
        }

        with pytest.raises(KeyError):

            _ = season.make_season(d_common=d_common_1, w=None)

        d_common_2 = {
            'season': {
                'is_summer_period_set': False
            }
        }

        with pytest.raises(KeyError):

            _ = season.make_season(d_common=d_common_2, w=None)

        d_common_3 = {
            'season': {
                'is_winter_period_set': False
            }
        }

        with pytest.raises(KeyError):

            _ = season.make_season(d_common=d_common_3, w=None)

        d_common_4 = {
            'season': {
                'is_summer_period_set': False,
                'is_winter_period_set': False
            }
        }
        
        _ = season.make_season(d_common=d_common_4, w=None)

    def test_make_season_season_specified(self):

        d_common = {
            'season': {
                'is_summer_period_set': True,
                'is_winter_period_set': True,
                'summer_start': '1/31',
                'summer_end': '12/1',
                'winter_start': '12/10',
                'winter_end': '1/3'
            }
        }

        s = season.make_season(d_common=d_common, w=None)

        # 1/1
        self.assertEqual(s.summer[0], False)
        self.assertEqual(s.winter[0], True)
        self.assertEqual(s.middle[0], False)
        # 1/2
        self.assertEqual(s.summer[1], False)
        self.assertEqual(s.winter[1], True)
        self.assertEqual(s.middle[1], False)
        # 1/3
        self.assertEqual(s.summer[2], False)
        self.assertEqual(s.winter[2], True)
        self.assertEqual(s.middle[2], False)
        # 1/4
        self.assertEqual(s.summer[3], False)
        self.assertEqual(s.winter[3], False)
        self.assertEqual(s.middle[3], True)
        # 1/30
        self.assertEqual(s.summer[29], False)
        self.assertEqual(s.winter[29], False)
        self.assertEqual(s.middle[29], True)
        # 1/31
        self.assertEqual(s.summer[30], True)
        self.assertEqual(s.winter[30], False)
        self.assertEqual(s.middle[30], False)
        # 2/1
        self.assertEqual(s.summer[30], True)
        self.assertEqual(s.winter[30], False)
        self.assertEqual(s.middle[30], False)
        # 11/30
        self.assertEqual(s.summer[333], True)
        self.assertEqual(s.winter[333], False)
        self.assertEqual(s.middle[333], False)
        # 12/1
        self.assertEqual(s.summer[334], True)
        self.assertEqual(s.winter[334], False)
        self.assertEqual(s.middle[334], False)
        # 12/2
        self.assertEqual(s.summer[335], False)
        self.assertEqual(s.winter[335], False)
        self.assertEqual(s.middle[335], True)
        # 12/9
        self.assertEqual(s.summer[342], False)
        self.assertEqual(s.winter[342], False)
        self.assertEqual(s.middle[342], True)
        # 12/10
        self.assertEqual(s.summer[343], False)
        self.assertEqual(s.winter[343], True)
        self.assertEqual(s.middle[343], False)
        # 12/11
        self.assertEqual(s.summer[344], False)
        self.assertEqual(s.winter[344], True)
        self.assertEqual(s.middle[344], False)
        # 12/31
        self.assertEqual(s.summer[364], False)
        self.assertEqual(s.winter[364], True)
        self.assertEqual(s.middle[364], False)

    def test_make_season_season_specified_duplicated_error(self):

        d_common = {
            'season': {
                'is_summer_period_set': True,
                'is_winter_period_set': True,
                'summer_start': '1/1',
                'summer_end': '12/20',
                'winter_start': '12/10',
                'winter_end': '1/10'
            }
        }

        with pytest.raises(ValueError):
            s = season.make_season(d_common=d_common, w=None)
    
    def test_make_season_ees(self):

        d_common = {
            'weather': {
                'method': 'ees',
                'region': '1'
            }
        }

        s = season.make_season(d_common=d_common, w=None)
        st = season._get_season_status(d_common=d_common)

        # region 1(Kitami)
        # winter: 9/24 ~ 6/7
        # summer: 7/10 ~ 8/30

        # 1/1
        self.assertEqual(s.summer[0], False)
        self.assertEqual(s.winter[0], True)
        self.assertEqual(s.middle[0], False)

        # 6/6
        self.assertEqual(s.summer[156], False)
        self.assertEqual(s.winter[156], True)
        self.assertEqual(s.middle[156], False)

        # 6/7
        self.assertEqual(s.summer[157], False)
        self.assertEqual(s.winter[157], True)
        self.assertEqual(s.middle[157], False)

        # 6/8
        self.assertEqual(s.summer[158], False)
        self.assertEqual(s.winter[158], False)
        self.assertEqual(s.middle[158], True)

        # 7/9
        self.assertEqual(s.summer[189], False)
        self.assertEqual(s.winter[189], False)
        self.assertEqual(s.middle[189], True)

        # 7/10
        self.assertEqual(s.summer[190], True)
        self.assertEqual(s.winter[190], False)
        self.assertEqual(s.middle[190], False)

        # 7/11
        self.assertEqual(s.summer[191], True)
        self.assertEqual(s.winter[191], False)
        self.assertEqual(s.middle[191], False)

        # 8/29
        self.assertEqual(s.summer[240], True)
        self.assertEqual(s.winter[240], False)
        self.assertEqual(s.middle[240], False)

        # 8/30
        self.assertEqual(s.summer[241], True)
        self.assertEqual(s.winter[241], False)
        self.assertEqual(s.middle[241], False)

        # 8/31
        self.assertEqual(s.summer[242], False)
        self.assertEqual(s.winter[242], False)
        self.assertEqual(s.middle[242], True)

        # 9/23
        self.assertEqual(s.summer[265], False)
        self.assertEqual(s.winter[265], False)
        self.assertEqual(s.middle[265], True)

        # 9/24
        self.assertEqual(s.summer[266], False)
        self.assertEqual(s.winter[266], True)
        self.assertEqual(s.middle[266], False)

        # 9/25
        self.assertEqual(s.summer[267], False)
        self.assertEqual(s.winter[267], True)
        self.assertEqual(s.middle[267], False)


        # 1/31 30
        # 2/1 31
        # 2/28 58
        # 3/1 59
        # 3/31 89
        # 4/1 90
        # 4/30 119
        # 5/1 120
        # 5/31 150
        # 6/1 151
        # 6/6 156
        # 6/7 157
        # 6/8 158
        # 6/30 180
        # 7/1 181
        # 7/9 189
        # 7/10 190
        # 7/11 191
        # 7/31 211
        # 8/1 212
        # 8/29 240
        # 8/30 241
        # 8/31 242
        # 9/1 243
        # 9/23 265
        # 9/24 266
        # 9/25 267

