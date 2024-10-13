import unittest
import numpy as np
import pytest

from heat_load_calc import season


class TestInterval(unittest.TestCase):

    def assert_season(self, spring, summer, autumn, winter, i, s):
        if s == "spring":
            self.assertEqual(spring[i], True)
            self.assertEqual(summer[i], False)
            self.assertEqual(autumn[i], False)
            self.assertEqual(winter[i], False)
        elif s == "summer":
            self.assertEqual(spring[i], False)
            self.assertEqual(summer[i], True)
            self.assertEqual(autumn[i], False)
            self.assertEqual(winter[i], False)
        elif s == "autumn":
            self.assertEqual(spring[i], False)
            self.assertEqual(summer[i], False)
            self.assertEqual(autumn[i], True)
            self.assertEqual(winter[i], False)
        elif s == "winter":
            self.assertEqual(spring[i], False)
            self.assertEqual(summer[i], False)
            self.assertEqual(autumn[i], False)
            self.assertEqual(winter[i], True)
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

        spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(summer_start=100, summer_end=150, winter_start=200, winter_end=250)

        self.assertEqual(np.all(spring | summer | autumn | winter), True)
        assert_season(spring, summer, autumn, winter, 0, "spring")
        assert_season(spring, summer, autumn, winter, 98, "spring")
        assert_season(spring, summer, autumn, winter, 99, "summer")
        assert_season(spring, summer, autumn, winter, 100, "summer")
        assert_season(spring, summer, autumn, winter, 148, "summer")
        assert_season(spring, summer, autumn, winter, 149, "summer")
        assert_season(spring, summer, autumn, winter, 150, "autumn")
        assert_season(spring, summer, autumn, winter, 198, "autumn")
        assert_season(spring, summer, autumn, winter, 199, "winter")
        assert_season(spring, summer, autumn, winter, 200, "winter")
        assert_season(spring, summer, autumn, winter, 248, "winter")
        assert_season(spring, summer, autumn, winter, 249, "winter")
        assert_season(spring, summer, autumn, winter, 250, "spring")
        assert_season(spring, summer, autumn, winter, 364, "spring")
        
        with pytest.raises(ValueError):
            spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(summer_start=100, summer_end=150, winter_end=200, winter_start=250)

        with pytest.raises(ValueError):
            spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(summer_start=100, winter_start=150, summer_end=200, winter_end=250)
        
        with pytest.raises(ValueError):
            spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(summer_start=100, winter_start=150, winter_end=200, summer_end=250)
        
        with pytest.raises(ValueError):
            spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(summer_start=100, winter_end=150, summer_end=200, winter_start=250)

        with pytest.raises(ValueError):
            spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(summer_start=100, winter_end=150, winter_start=200, summer_end=250)


        with pytest.raises(ValueError):
            spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(summer_end=100, summer_start=150, winter_start=200, winter_end=250)

        with pytest.raises(ValueError):
            spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(summer_end=100, summer_start=150, winter_end=200, winter_start=250)

        with pytest.raises(ValueError):
            spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(summer_end=100, winter_start=150, summer_start=200, winter_end=250)

        spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(summer_end=100, winter_start=150, winter_end=200, summer_start=250)

        self.assertEqual(np.all(spring | summer | autumn | winter), True)
        assert_season(spring, summer, autumn, winter, 0, "summer")
        assert_season(spring, summer, autumn, winter, 98, "summer")
        assert_season(spring, summer, autumn, winter, 99, "summer")
        assert_season(spring, summer, autumn, winter, 100, "autumn")
        assert_season(spring, summer, autumn, winter, 148, "autumn")
        assert_season(spring, summer, autumn, winter, 149, "winter")
        assert_season(spring, summer, autumn, winter, 150, "winter")
        assert_season(spring, summer, autumn, winter, 198, "winter")
        assert_season(spring, summer, autumn, winter, 199, "winter")
        assert_season(spring, summer, autumn, winter, 200, "spring")
        assert_season(spring, summer, autumn, winter, 248, "spring")
        assert_season(spring, summer, autumn, winter, 249, "summer")
        assert_season(spring, summer, autumn, winter, 250, "summer")
        assert_season(spring, summer, autumn, winter, 364, "summer")

        with pytest.raises(ValueError):
            spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(summer_end=100, winter_end=150, summer_start=200, winter_start=250)

        with pytest.raises(ValueError):
            spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(summer_end=100, winter_end=150, winter_start=200, summer_start=250)


        with pytest.raises(ValueError):
            spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(winter_start=100, summer_start=150, summer_end=200, winter_end=250)

        with pytest.raises(ValueError):
            spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(winter_start=100, summer_start=150, winter_end=200, summer_end=250)

        with pytest.raises(ValueError):
            spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(winter_start=100, summer_end=150, summer_start=200, winter_end=250)

        with pytest.raises(ValueError):
            spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(winter_start=100, summer_end=150, winter_end=200, summer_start=250)

        spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(winter_start=100, winter_end=150, summer_start=200, summer_end=250)

        self.assertEqual(np.all(spring | summer | autumn | winter), True)
        assert_season(spring, summer, autumn, winter, 0, "autumn")
        assert_season(spring, summer, autumn, winter, 98, "autumn")
        assert_season(spring, summer, autumn, winter, 99, "winter")
        assert_season(spring, summer, autumn, winter, 100, "winter")
        assert_season(spring, summer, autumn, winter, 148, "winter")
        assert_season(spring, summer, autumn, winter, 149, "winter")
        assert_season(spring, summer, autumn, winter, 150, "spring")
        assert_season(spring, summer, autumn, winter, 198, "spring")
        assert_season(spring, summer, autumn, winter, 199, "summer")
        assert_season(spring, summer, autumn, winter, 200, "summer")
        assert_season(spring, summer, autumn, winter, 248, "summer")
        assert_season(spring, summer, autumn, winter, 249, "summer")
        assert_season(spring, summer, autumn, winter, 250, "autumn")
        assert_season(spring, summer, autumn, winter, 364, "autumn")

        with pytest.raises(ValueError):
            spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(winter_start=100, winter_end=150, summer_end=200, summer_start=250)


        spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(winter_end=100, summer_start=150, summer_end=200, winter_start=250)

        self.assertEqual(np.all(spring | summer | autumn | winter), True)
        assert_season(spring, summer, autumn, winter, 0, "winter")
        assert_season(spring, summer, autumn, winter, 98, "winter")
        assert_season(spring, summer, autumn, winter, 99, "winter")
        assert_season(spring, summer, autumn, winter, 100, "spring")
        assert_season(spring, summer, autumn, winter, 148, "spring")
        assert_season(spring, summer, autumn, winter, 149, "summer")
        assert_season(spring, summer, autumn, winter, 150, "summer")
        assert_season(spring, summer, autumn, winter, 198, "summer")
        assert_season(spring, summer, autumn, winter, 199, "summer")
        assert_season(spring, summer, autumn, winter, 200, "autumn")
        assert_season(spring, summer, autumn, winter, 248, "autumn")
        assert_season(spring, summer, autumn, winter, 249, "winter")
        assert_season(spring, summer, autumn, winter, 250, "winter")
        assert_season(spring, summer, autumn, winter, 364, "winter")

        with pytest.raises(ValueError):
            spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(winter_end=100, summer_start=150, winter_start=200, summer_end=250)

        with pytest.raises(ValueError):
            spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(winter_end=100, summer_end=150, summer_start=200, winter_start=250)

        with pytest.raises(ValueError):
            spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(winter_end=100, summer_end=150, winter_start=200, summer_start=250)

        with pytest.raises(ValueError):
            spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(winter_end=100, winter_start=150, summer_start=200, summer_end=250)

        with pytest.raises(ValueError):
            spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(winter_end=100, winter_start=150, summer_end=200, summer_start=250)


        spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(summer_start=1, summer_end=199, winter_start=200, winter_end=365)

        self.assertEqual(np.all(spring | summer | autumn | winter), True)
        assert_season(spring, summer, autumn, winter, 0, "summer")
        assert_season(spring, summer, autumn, winter, 197, "summer")
        assert_season(spring, summer, autumn, winter, 198, "summer")
        assert_season(spring, summer, autumn, winter, 199, "winter")
        assert_season(spring, summer, autumn, winter, 200, "winter")
        assert_season(spring, summer, autumn, winter, 364, "winter")

        spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(summer_end=149, winter_start=150, winter_end=249, summer_start=250)

        self.assertEqual(np.all(spring | summer | autumn | winter), True)
        assert_season(spring, summer, autumn, winter, 0, "summer")
        assert_season(spring, summer, autumn, winter, 147, "summer")
        assert_season(spring, summer, autumn, winter, 148, "summer")
        assert_season(spring, summer, autumn, winter, 149, "winter")
        assert_season(spring, summer, autumn, winter, 247, "winter")
        assert_season(spring, summer, autumn, winter, 248, "winter")
        assert_season(spring, summer, autumn, winter, 249, "summer")
        assert_season(spring, summer, autumn, winter, 364, "summer")

        spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(winter_start=1, winter_end=199, summer_start=200, summer_end=365)

        self.assertEqual(np.all(spring | summer | autumn | winter), True)
        assert_season(spring, summer, autumn, winter, 0, "winter")
        assert_season(spring, summer, autumn, winter, 198, "winter")
        assert_season(spring, summer, autumn, winter, 199, "summer")
        assert_season(spring, summer, autumn, winter, 200, "summer")
        assert_season(spring, summer, autumn, winter, 364, "summer")

        spring, summer, autumn, winter = season._get_bool_list_for_four_season_as_int(winter_end=149, summer_start=150, summer_end=249, winter_start=250)

        self.assertEqual(np.all(spring | summer | autumn | winter), True)
        assert_season(spring, summer, autumn, winter, 0, "winter")
        assert_season(spring, summer, autumn, winter, 147, "winter")
        assert_season(spring, summer, autumn, winter, 148, "winter")
        assert_season(spring, summer, autumn, winter, 149, "summer")
        assert_season(spring, summer, autumn, winter, 247, "summer")
        assert_season(spring, summer, autumn, winter, 248, "summer")
        assert_season(spring, summer, autumn, winter, 249, "winter")
        assert_season(spring, summer, autumn, winter, 364, "winter")


    def test_get_bool_list_for_four_season_as_str(self):

        assert_season = self.assert_season

        spring, summer, autumn, winter = season.get_bool_list_for_four_season_as_str(summer_start="4/10", summer_end="5/30", winter_start="7/19", winter_end="9/7")

        self.assertEqual(np.all(spring | summer | autumn | winter), True)
        self.assertEqual(np.all(spring & summer & autumn & winter), False)
        assert_season(spring, summer, autumn, winter, 0, "spring")
        assert_season(spring, summer, autumn, winter, 98, "spring")
        assert_season(spring, summer, autumn, winter, 99, "summer")
        assert_season(spring, summer, autumn, winter, 100, "summer")
        assert_season(spring, summer, autumn, winter, 148, "summer")
        assert_season(spring, summer, autumn, winter, 149, "summer")
        assert_season(spring, summer, autumn, winter, 150, "autumn")
        assert_season(spring, summer, autumn, winter, 198, "autumn")
        assert_season(spring, summer, autumn, winter, 199, "winter")
        assert_season(spring, summer, autumn, winter, 200, "winter")
        assert_season(spring, summer, autumn, winter, 248, "winter")
        assert_season(spring, summer, autumn, winter, 249, "winter")
        assert_season(spring, summer, autumn, winter, 250, "spring")
        assert_season(spring, summer, autumn, winter, 364, "spring")


        spring, summer, autumn, winter = season.get_bool_list_for_four_season_as_str(summer_end="4/10", winter_start="5/30", winter_end="7/19", summer_start="9/7")

        self.assertEqual(np.all(spring | summer | autumn | winter), True)
        assert_season(spring, summer, autumn, winter, 0, "summer")
        assert_season(spring, summer, autumn, winter, 98, "summer")
        assert_season(spring, summer, autumn, winter, 99, "summer")
        assert_season(spring, summer, autumn, winter, 100, "autumn")
        assert_season(spring, summer, autumn, winter, 148, "autumn")
        assert_season(spring, summer, autumn, winter, 149, "winter")
        assert_season(spring, summer, autumn, winter, 150, "winter")
        assert_season(spring, summer, autumn, winter, 198, "winter")
        assert_season(spring, summer, autumn, winter, 199, "winter")
        assert_season(spring, summer, autumn, winter, 200, "spring")
        assert_season(spring, summer, autumn, winter, 248, "spring")
        assert_season(spring, summer, autumn, winter, 249, "summer")
        assert_season(spring, summer, autumn, winter, 250, "summer")
        assert_season(spring, summer, autumn, winter, 364, "summer")


        spring, summer, autumn, winter = season.get_bool_list_for_four_season_as_str(winter_start="4/10", winter_end="5/30", summer_start="7/19", summer_end="9/7")

        self.assertEqual(np.all(spring | summer | autumn | winter), True)
        assert_season(spring, summer, autumn, winter, 0, "autumn")
        assert_season(spring, summer, autumn, winter, 98, "autumn")
        assert_season(spring, summer, autumn, winter, 99, "winter")
        assert_season(spring, summer, autumn, winter, 100, "winter")
        assert_season(spring, summer, autumn, winter, 148, "winter")
        assert_season(spring, summer, autumn, winter, 149, "winter")
        assert_season(spring, summer, autumn, winter, 150, "spring")
        assert_season(spring, summer, autumn, winter, 198, "spring")
        assert_season(spring, summer, autumn, winter, 199, "summer")
        assert_season(spring, summer, autumn, winter, 200, "summer")
        assert_season(spring, summer, autumn, winter, 248, "summer")
        assert_season(spring, summer, autumn, winter, 249, "summer")
        assert_season(spring, summer, autumn, winter, 250, "autumn")
        assert_season(spring, summer, autumn, winter, 364, "autumn")

        spring, summer, autumn, winter = season.get_bool_list_for_four_season_as_str(winter_end="4/10", summer_start="5/30", summer_end="7/19", winter_start="9/7")

        self.assertEqual(np.all(spring | summer | autumn | winter), True)
        assert_season(spring, summer, autumn, winter, 0, "winter")
        assert_season(spring, summer, autumn, winter, 98, "winter")
        assert_season(spring, summer, autumn, winter, 99, "winter")
        assert_season(spring, summer, autumn, winter, 100, "spring")
        assert_season(spring, summer, autumn, winter, 148, "spring")
        assert_season(spring, summer, autumn, winter, 149, "summer")
        assert_season(spring, summer, autumn, winter, 150, "summer")
        assert_season(spring, summer, autumn, winter, 198, "summer")
        assert_season(spring, summer, autumn, winter, 199, "summer")
        assert_season(spring, summer, autumn, winter, 200, "autumn")
        assert_season(spring, summer, autumn, winter, 248, "autumn")
        assert_season(spring, summer, autumn, winter, 249, "winter")
        assert_season(spring, summer, autumn, winter, 250, "winter")
        assert_season(spring, summer, autumn, winter, 364, "winter")

        spring, summer, autumn, winter = season.get_bool_list_for_four_season_as_str(summer_start="1/1", summer_end="7/18", winter_start="7/19", winter_end="12/31")

        self.assertEqual(np.all(spring | summer | autumn | winter), True)
        assert_season(spring, summer, autumn, winter, 0, "summer")
        assert_season(spring, summer, autumn, winter, 197, "summer")
        assert_season(spring, summer, autumn, winter, 198, "summer")
        assert_season(spring, summer, autumn, winter, 199, "winter")
        assert_season(spring, summer, autumn, winter, 200, "winter")
        assert_season(spring, summer, autumn, winter, 364, "winter")

        spring, summer, autumn, winter = season.get_bool_list_for_four_season_as_str(summer_end="5/29", winter_start="5/30", winter_end="9/6", summer_start="9/7")

        self.assertEqual(np.all(spring | summer | autumn | winter), True)
        assert_season(spring, summer, autumn, winter, 0, "summer")
        assert_season(spring, summer, autumn, winter, 147, "summer")
        assert_season(spring, summer, autumn, winter, 148, "summer")
        assert_season(spring, summer, autumn, winter, 149, "winter")
        assert_season(spring, summer, autumn, winter, 247, "winter")
        assert_season(spring, summer, autumn, winter, 248, "winter")
        assert_season(spring, summer, autumn, winter, 249, "summer")
        assert_season(spring, summer, autumn, winter, 364, "summer")

        spring, summer, autumn, winter = season.get_bool_list_for_four_season_as_str(winter_start="1/1", winter_end="7/18", summer_start="7/19", summer_end="12/31")

        self.assertEqual(np.all(spring | summer | autumn | winter), True)
        assert_season(spring, summer, autumn, winter, 0, "winter")
        assert_season(spring, summer, autumn, winter, 198, "winter")
        assert_season(spring, summer, autumn, winter, 199, "summer")
        assert_season(spring, summer, autumn, winter, 200, "summer")
        assert_season(spring, summer, autumn, winter, 364, "summer")

        spring, summer, autumn, winter = season.get_bool_list_for_four_season_as_str(winter_end="5/29", summer_start="5/30", summer_end="9/6", winter_start="9/7")

        self.assertEqual(np.all(spring | summer | autumn | winter), True)
        assert_season(spring, summer, autumn, winter, 0, "winter")
        assert_season(spring, summer, autumn, winter, 147, "winter")
        assert_season(spring, summer, autumn, winter, 148, "winter")
        assert_season(spring, summer, autumn, winter, 149, "summer")
        assert_season(spring, summer, autumn, winter, 247, "summer")
        assert_season(spring, summer, autumn, winter, 248, "summer")
        assert_season(spring, summer, autumn, winter, 249, "winter")
        assert_season(spring, summer, autumn, winter, 364, "winter")






