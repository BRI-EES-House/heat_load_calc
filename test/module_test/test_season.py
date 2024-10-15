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


    def test_get_bool_list_for_four_season_as_str(self):

        assert_season = self.assert_season

        summer, winter, middle = season.get_bool_list_for_four_season_as_str(summer_start="4/10", summer_end="5/30", winter_start="7/19", winter_end="9/7")

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


        summer, winter, middle = season.get_bool_list_for_four_season_as_str(summer_end="4/10", winter_start="5/30", winter_end="7/19", summer_start="9/7")

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

        summer, winter, middle = season.get_bool_list_for_four_season_as_str(winter_start="4/10", winter_end="5/30", summer_start="7/19", summer_end="9/7")

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

        summer, winter, middle = season.get_bool_list_for_four_season_as_str(winter_end="4/10", summer_start="5/30", summer_end="7/19", winter_start="9/7")

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

        summer, winter, middle = season.get_bool_list_for_four_season_as_str(summer_start="1/1", summer_end="7/18", winter_start="7/19", winter_end="12/31")

        self.assertEqual(np.all(summer | winter | middle), True)
        self.assertEqual(np.all(summer & winter & middle), False)

        assert_season(summer, winter, middle, 0, "summer")
        assert_season(summer, winter, middle, 197, "summer")
        assert_season(summer, winter, middle, 198, "summer")
        assert_season(summer, winter, middle, 199, "winter")
        assert_season(summer, winter, middle, 200, "winter")
        assert_season(summer, winter, middle, 364, "winter")

        summer, winter, middle = season.get_bool_list_for_four_season_as_str(summer_end="5/29", winter_start="5/30", winter_end="9/6", summer_start="9/7")

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

        summer, winter, middle = season.get_bool_list_for_four_season_as_str(winter_start="1/1", winter_end="7/18", summer_start="7/19", summer_end="12/31")

        self.assertEqual(np.all(summer | winter | middle), True)
        self.assertEqual(np.all(summer & winter & middle), False)

        assert_season(summer, winter, middle, 0, "winter")
        assert_season(summer, winter, middle, 198, "winter")
        assert_season(summer, winter, middle, 199, "summer")
        assert_season(summer, winter, middle, 200, "summer")
        assert_season(summer, winter, middle, 364, "summer")

        summer, winter, middle = season.get_bool_list_for_four_season_as_str(winter_end="5/29", summer_start="5/30", summer_end="9/6", winter_start="9/7")

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






