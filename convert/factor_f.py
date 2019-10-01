from collections import namedtuple
from typing import Optional, List, Dict, Union, Tuple

# ⽇射取得率補正係数
# ガラスの仕様の区分は、区分1（単板ガラス）を想定する。
# ⽅位が北・北東・東・南東・南・南⻄・⻄・北⻄の窓については、⽇除け下端から窓上端までの垂直⽅向の
# 距離︓窓の開口高さ寸法：壁面からの日よけの張り出し寸法＝3:0:1とする。
# 8地域の暖房期は、8地域の冷房期で代用。
# 平成28年省エネルギー基準に準拠したエネルギー消費性能の評価に関する技術情報（住宅）
# 2.エネルギー消費性能の算定⽅法
# 2.2 算定⽅法
# 第三章 暖冷房負荷と外皮性能
# 第四節 日射熱取得
# 付録 B 大部分がガラスで構成されている窓等の開口部における取得日射熱補正係数
# データ「取得日射熱補正係数」 表 1(a) 屋根又は屋根の直下の天井に設置されている開口部の暖房期の取得日
# 射熱補正係数 表 1(b) 屋根又は屋根の直下の天井に設置されている開口部の冷房期の取得日射熱補正係数

Sunshade = namedtuple('Sunshade', [
    'existence',
    'input_method',
    'depth',
    'd_h',
    'd_e',
    'x1',
    'x2',
    'x3',
    'y1',
    'y2',
    'y3',
    'z_x_pls',
    'z_x_mns',
    'z_y_pls',
    'z_y_mns',
])


def get_f_not_input(season: str, region: int) -> Optional[float]:
    """
    Args:
        season: 期間
        region: 地域の区分
    Returns:
        f値
    """

    if season == 'heating':
        if region == 8:
            return None
        else:
            return 0.51
    elif season == 'cooling':
        return 0.93
    else:
        raise ValueError()


def get_f(season: str, region: int, direction: str, sunshade: Optional[Sunshade]) -> Optional[float]:
    """
    Args:
        season: 期間
        region: 地域の区分
        direction: 方位
        sunshade: 日除けの形状
    Returns:
        f値
    """

    if sunshade is None:
        return get_f_not_input(season, region)
    elif sunshade.existence:
        return get_f_existence(season, region, direction, sunshade)
    elif not sunshade.existence:
        return get_f_not_existence(season, region, direction)
    else:
        raise ValueError()


def get_f_existence(season: str, region: int, direction: str, sunshade: Sunshade) -> Optional[float]:
    """
    Args:
        season: 期間
        region: 地域の区分
        direction: 方位
        sunshade: 日除けの形状
    Returns:
        f値
    """

    if sunshade.input_method == 'simple':
        if season == 'heating':
            if region == 8:
                return None
            else:
                if direction == 'sw' or direction == 's' or direction == 'se':
                    return min(0.01 * (5 + 20 * (3 * sunshade.d_e + sunshade.d_h)/sunshade.depth), 0.72)
                elif (direction == 'n' or direction == 'ne' or direction == 'e'
                      or direction == 'nw' or direction == 'w'):
                    return min(0.01 * (10 + 15 * (2 * sunshade.d_e + sunshade.d_h) / sunshade.depth), 0.72)
                elif direction == 'top':
                    return 1.0
                elif direction == 'bottom':
                    return 0.0
                else:
                    raise ValueError()
        elif season == 'cooling':
            if region == 8:
                if direction == 'sw' or direction == 's' or direction == 'se':
                    return min(0.01 * (16 + 19 * (2 * sunshade.d_e + sunshade.d_h)/sunshade.depth), 0.93)
                elif (direction == 'n' or direction == 'ne' or direction == 'e'
                      or direction == 'nw' or direction == 'w'):
                    return min(0.01 * (16 + 24 * (2 * sunshade.d_e + sunshade.d_h) / sunshade.depth), 0.93)
                elif direction == 'top':
                    return 1.0
                elif direction == 'bottom':
                    return 0.0
                else:
                    raise ValueError()
            else:
                if direction == 's':
                    return min(0.01 * (24 + 9 * (3 * sunshade.d_e + sunshade.d_h)/sunshade.depth), 0.93)
                elif (direction == 'n' or direction == 'ne' or direction == 'e' or direction == 'se'
                      or direction == 'nw' or direction == 'w' or direction == 'sw'):
                    return min(0.01 * (16 + 24 * (2 * sunshade.d_e + sunshade.d_h) / sunshade.depth), 0.93)
                elif direction == 'top':
                    return 1.0
                elif direction == 'bottom':
                    return 0.0
                else:
                    raise ValueError()
        else:
            raise ValueError()
    elif sunshade.input_method == 'detailed':
        raise NotImplementedError()
    else:
        raise ValueError()


def get_f_not_existence(season: str, region: int, direction: str) -> Optional[float]:
    """
    Args:
        season: 期間
        region: 地域の区分
        direction: 方位
    Returns:
        f値
    Notes:
        第3章第4部「日射熱取得率」における表１・表２のうち、ガラスの仕様の区分1の値を採用した。
    """

    return {
        'heating': {
            'top': {1: 0.90, 2: 0.91, 3: 0.91, 4: 0.91, 5: 0.90, 6: 0.90, 7: 0.90, 8: None}[region],
            'n': {1: 0.862, 2: 0.860, 3: 0.862, 4: 0.861, 5: 0.867, 6: 0.870, 7: 0.873, 8: None}[region],
            'ne': {1: 0.848, 2: 0.851, 3: 0.850, 4: 0.846, 5: 0.838, 6: 0.839, 7: 0.833, 8: None}[region],
            'e': {1: 0.871, 2: 0.873, 3: 0.869, 4: 0.874, 5: 0.874, 6: 0.874, 7: 0.868, 8: None}[region],
            'se': {1: 0.892, 2: 0.888, 3: 0.885, 4: 0.883, 5: 0.894, 6: 0.896, 7: 0.892, 8: None}[region],
            's': {1: 0.892, 2: 0.880, 3: 0.884, 4: 0.874, 5: 0.894, 6: 0.889, 7: 0.896, 8: None}[region],
            'sw': {1: 0.888, 2: 0.885, 3: 0.885, 4: 0.882, 5: 0.891, 6: 0.885, 7: 0.894, 8: None}[region],
            'w': {1: 0.869, 2: 0.874, 3: 0.871, 4: 0.872, 5: 0.871, 6: 0.874, 7: 0.870, 8: None}[region],
            'nw': {1: 0.850, 2: 0.850, 3: 0.850, 4: 0.845, 5: 0.840, 6: 0.844, 7: 0.834, 8: None}[region],
            'bottom': {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: None}[region],
        }[direction],
        'cooling': {
            'top': {1: 0.93, 2: 0.93, 3: 0.93, 4: 0.94, 5: 0.93, 6: 0.94, 7: 0.94, 8: 0.93}[region],
            'n': {1: 0.853, 2: 0.857, 3: 0.853, 4: 0.852, 5: 0.860, 6: 0.847, 7: 0.838, 8: 0.848}[region],
            'ne': {1: 0.865, 2: 0.864, 3: 0.862, 4: 0.861, 5: 0.863, 6: 0.862, 7: 0.861, 8: 0.857}[region],
            'e': {1: 0.882, 2: 0.877, 3: 0.870, 4: 0.881, 5: 0.874, 6: 0.880, 7: 0.881, 8: 0.877}[region],
            'se': {1: 0.864, 2: 0.858, 3: 0.853, 4: 0.853, 5: 0.854, 6: 0.852, 7: 0.849, 8: 0.860}[region],
            's': {1: 0.807, 2: 0.812, 3: 0.799, 4: 0.784, 5: 0.807, 6: 0.795, 7: 0.788, 8: 0.824}[region],
            'sw': {1: 0.860, 2: 0.861, 3: 0.859, 4: 0.850, 5: 0.858, 6: 0.852, 7: 0.847, 8: 0.858}[region],
            'w': {1: 0.880, 2: 0.878, 3: 0.883, 4: 0.876, 5: 0.875, 6: 0.880, 7: 0.880, 8: 0.876}[region],
            'nw': {1: 0.866, 2: 0.864, 3: 0.865, 4: 0.861, 5: 0.862, 6: 0.864, 7: 0.862, 8: 0.859}[region],
            'bottom': 0.0,
        }[direction],
    }[season]

