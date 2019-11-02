# 附属書36 計算地点の緯度及び経度
# 本附属書は地域区分に応じた計算地点の緯度及び経度を定義する。

from typing import Tuple
import math


def get_phi_loc_and_lambda_loc(region: int) -> Tuple:
    """
    地域区分から緯度、経度を設定する

    Args:
        region: 地域区分

    Returns:
        以下のタプル
            (1) 緯度, rad
            (2) 経度, rad
    """

    latitude, longitude = {
        1: (43.82, 143.91),    # 1地域（北見）
        2: (43.21, 141.79),    # 2地域（岩見沢）
        3: (39.70, 141.17),    # 3地域（盛岡）
        4: (36.66, 138.20),    # 4地域（長野）
        5: (36.55, 139.87),    # 5地域（宇都宮）
        6: (34.66, 133.92),    # 6地域（岡山）
        7: (31.94, 131.42),    # 7地域（宮崎）
        8: (26.21, 127.685),    # 8地域（那覇）
    }[region]

    phi_loc, lambda_loc = math.radians(latitude), math.radians(longitude)

    return phi_loc, lambda_loc
