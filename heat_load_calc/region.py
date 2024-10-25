from enum import IntEnum
import math
from typing import Tuple
import numpy as np

class Region(IntEnum):

    Region1 = '1'
    Region2 = '2'
    Region3 = '3'
    Region4 = '4'
    Region5 = '5'
    Region6 = '6'
    Region7 = '7'
    Region8 = '8'

    def get_phi_loc_and_lambda_loc(self) -> Tuple[float, float]:
        """Get the latitude and longitude of the region. / 地域の区分から緯度、経度を設定する。

        Returns:
            (1) latitude, 緯度, rad
            (2) longitude, 経度, rad
        """

        latitude, longitude = {
            Region.Region1: (43.82, 143.91),    # 1地域（北見）
            Region.Region2: (43.21, 141.79),    # 2地域（岩見沢）
            Region.Region3: (39.70, 141.17),    # 3地域（盛岡）
            Region.Region4: (36.66, 138.20),    # 4地域（長野）
            Region.Region5: (36.55, 139.87),    # 5地域（宇都宮）
            Region.Region6: (34.66, 133.92),    # 6地域（岡山）
            Region.Region7: (31.94, 131.42),    # 7地域（宮崎）
            Region.Region8: (26.21, 127.685),   # 8地域（那覇）
        }[self]

        phi_loc, lambda_loc = math.radians(latitude), math.radians(longitude)

        return phi_loc, lambda_loc
    
    def get_season_status(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Get the summer season, winter season, and middle season in each region.

        Return:
            the summer season, winter season, and middle season.
            the season is represented by the ndarry list of bool which length is 365.
        """

        winter_start, winter_end, summer_start, summer_end, is_winter_period_set, is_summer_period_set = {
            Region.Region1: ("9/24", "6/7", "7/10", "8/30", True, True),
            Region.Region2: ("9/26", "6/4", "7/15", "8/31", True, True),
            Region.Region3: ("9/30", "5/31", "7/10", "8/31", True, True),
            Region.Region4: ("10/1", "5/30", "7/10", "8/31", True, True),
            Region.Region5: ("10/10", "5/15", "7/6", "8/31", True, True),
            Region.Region6: ("11/4", "4/21", "5/30", "9/23", True, True),
            Region.Region7: ("11/26", "3/27", "5/15", "10/13", True, True),
            Region.Region8: (None, None, "3/25", "12/14", False, True)
        }[self]

        return summer_start, summer_end, winter_start, winter_end, is_summer_period_set, is_winter_period_set

