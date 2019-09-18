import math

"""
付録36．計算地域の緯度、経度
"""


# 地域区分から緯度、経度を設定する
# 当面は6地域の緯度、経度を返す
def get_region_location(Region: int) -> tuple:
    Latitude = -999.0
    Longitude = -999.0

    if Region == 1:
        # 1地域（北見）
        Latitude = 43.82
        Longitude = 143.91
    elif Region == 2:
        # 2地域（岩見沢）
        Latitude = 43.21
        Longitude = 141.79
    elif Region == 3:
        # 3地域（盛岡）
        Latitude = 39.70
        Longitude = 141.17
    elif Region == 4:
        # 4地域（長野）
        Latitude = 36.66
        Longitude = 138.20
    elif Region == 5:
        # 5地域（宇都宮）
        Latitude = 36.55
        Longitude = 139.87
    elif Region == 6:
        # 6地域（岡山）
        Latitude = 34.66
        Longitude = 133.92
    elif Region == 7:
        # 7地域（宮崎）
        Latitude = 31.94
        Longitude = 131.42
    elif Region == 8:
        # 8地域（那覇）
        Latitude = 26.21
        Longitude = 127.685
    return math.radians(Latitude), math.radians(Longitude)
