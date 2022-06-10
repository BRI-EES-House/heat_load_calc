from enum import IntEnum
import math
from typing import Tuple


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
        """
        地域の区分から緯度、経度を設定する

        Returns:
            以下のタプル
                (1) 緯度, rad
                (2) 経度, rad
        """

        latitude, longitude = {
            Region.Region1: (43.82, 143.91),    # 1地域（北見）
            Region.Region2: (43.21, 141.79),    # 2地域（岩見沢）
            Region.Region3: (39.70, 141.17),    # 3地域（盛岡）
            Region.Region4: (36.66, 138.20),    # 4地域（長野）
            Region.Region5: (36.55, 139.87),    # 5地域（宇都宮）
            Region.Region6: (34.66, 133.92),    # 6地域（岡山）
            Region.Region7: (31.94, 131.42),    # 7地域（宮崎）
            Region.Region8: (26.21, 127.685),    # 8地域（那覇）
        }[self]

        phi_loc, lambda_loc = math.radians(latitude), math.radians(longitude)

        return phi_loc, lambda_loc
