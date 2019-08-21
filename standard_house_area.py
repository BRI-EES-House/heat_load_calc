import copy
import math
import numpy

from common import get_a_f_nr


# 開口部比率, -
def get_ratio_window(house_type):

    ratio_window = {
        'detached': {
            'total': 0.11,
            'direction': {'top': 0.000, 'n': 0.110, 's': 0.686, 'e': 0.132, 'w': 0.072}
        },
        'condominium': {
            'total': 0.07,
            'direction': {'top': 0.000, 'n': 0.215, 's': 0.633, 'e': 0.000, 'w': 0.152}
        }
    }

    total_ratio = {
        'detached': 0.11,
        'condominium': 0.07,
    }[house_type]

    return ratio_window[house_type], total_ratio


def get_area_windows(house_type, area_total_skin):

    # 開口部比率, -
    ratio_window, total_ratio = get_ratio_window(house_type)

    # 開口部面積, m
    area_window = total_ratio * area_total_skin

    area_windows = {
        'top': area_window * ratio_window['direction']['top'],
        'n': area_window * ratio_window['direction']['n'],
        's': area_window * ratio_window['direction']['s'],
        'e': area_window * ratio_window['direction']['e'],
        'w': area_window * ratio_window['direction']['w'],
    }

    return area_windows


def get_list_general_parts(area_general_parts):
    correspondence = {
        'type': {'ceiling': 'ceiling', 'floor': 'floor', 'wall_n': 'wall', 'wall_s': 'wall', 'wall_e': 'Wall',
                 'wall_w': 'wall'},
        'direction': {'ceiling': 'top', 'floor': 'bottom', 'wall_n': 'n', 'wall_s': 's', 'wall_e': 'e', 'wall_w': 'w'}
    }

    d = []
    for x in area_general_parts.keys():
        for y in area_general_parts[x].keys():
            if area_general_parts[x][y] > 0:
                d.append({
                    'name': x + '_' + y,
                    'general_part_type': correspondence['type'][x],
                    'next_space': 'outdoor',
                    'external_surface_type': 'outdoor',
                    'direction': correspondence['direction'][x],
                    'area': area_general_parts[x][y],
                    'space_type': y
                })

    return d


def get_list_windows(area_windows):
    d = []
    for x in area_windows.keys():
        for y in area_windows[x].keys():
            if area_windows[x][y] > 0:
                d.append({
                    'name': x + '_' + y,
                    'next_space': 'outdoor',
                    'direction': x,
                    'area': area_windows[x][y],
                    'space_type': y
                })
    return d


def get_list_inner_walls(area_inner_walls):
    d = []
    for x in area_inner_walls.keys():
        if area_inner_walls[x] > 0:
            d.append({
                'name': 'inner_wall_' + x,
                'area': area_inner_walls[x],
                'space_type': x,
                'type': 'inner_wall'})

    return d


def get_geometry(a_evlp_total, a_f, h_total):

    # 周長の算出
    l_total = max(4 * a_f ** 0.5, (a_evlp_total - 2 * a_f) / h_total)

    # アスペクト比の上限値の設定
    r_aspect_max = 2

    # 短辺・長辺長さの算出
    l_short = max(l_total / ((1 + r_aspect_max) * 2),
                        (l_total - (l_total ** 2 - 16 * a_f) ** 0.5) / 4)
    l_long = (l_total - l_short * 2) / 2

    return l_short, l_long, l_total


def get_a_d_wind(area, area_max):
    adjusted = min(area, area_max)
    over = area - adjusted
    return adjusted, over


# 戸建住宅の面積算出
def get_area_detached(h_f, area_windows, a_f_mr, a_f_or, a_f_nr, a_f, r_a_f_mr, r_a_f_or, r_a_f_nr, a_long, a_short):

    n = len(h_f)

    # 窓面積の調整 南、東、北、西、天井の順に割付
    a_d_wind_s, a_adj = get_a_d_wind(area_windows['s'], a_long)
    a_d_wind_e, a_adj = get_a_d_wind(area_windows['e'] + a_adj, a_short)
    a_d_wind_n, a_adj = get_a_d_wind(area_windows['n'] + a_adj, a_long)
    a_d_wind_w, _ = get_a_d_wind(area_windows['w'] + a_adj, a_short)

    return {
        'windows': {
            'n': {
                'main_occupant_room': 0.0,
                'other_occupant_room': 0.0,
                'non_occupant_room': a_d_wind_n,
            },
            's': {
                'main_occupant_room': a_d_wind_s * a_f_mr / (a_f_mr + a_f_or),
                'other_occupant_room': a_d_wind_s * a_f_or / (a_f_mr + a_f_or),
                'non_occupant_room': 0.0,
            },
            'e': {
                'main_occupant_room': a_d_wind_e * r_a_f_mr,
                'other_occupant_room': a_d_wind_e * r_a_f_or,
                'non_occupant_room': a_d_wind_e * r_a_f_nr,
            },
            'w': {
                'main_occupant_room': a_d_wind_w * r_a_f_mr,
                'other_occupant_room': a_d_wind_w * r_a_f_or,
                'non_occupant_room': a_d_wind_w * r_a_f_nr,
            },
            'top': {
                'main_occupant_room': 0.0,
                'other_occupant_room': 0.0,
                'non_occupant_room': 0.0,
            },
        },
        'general_parts': {
            'ceiling': {
                'main_occupant_room': max(0.0, a_f - a_f_nr / n - a_f_or),
                'other_occupant_room': min(a_f_or, a_f - a_f_nr / n),
                'non_occupant_room': a_f_nr / n,
            },
            'floor': {
                'main_occupant_room': min(a_f_mr, a_f - a_f_nr / n),
                'other_occupant_room': max(0.0, a_f - a_f_nr / n - a_f_mr),
                'non_occupant_room': a_f_nr / n,
            },
            'wall_n': {
                'main_occupant_room': 0.0,
                'other_occupant_room': 0.0,
                'non_occupant_room': a_long - a_d_wind_n,
            },
            'wall_s': {
                'main_occupant_room': (a_long - a_d_wind_s) * a_f_mr / (a_f_mr + a_f_or),
                'other_occupant_room': (a_long - a_d_wind_s) * a_f_or / (a_f_mr + a_f_or),
                'non_occupant_room': 0.0,
            },
            'wall_e': {
                'main_occupant_room': (a_short - a_d_wind_e) * r_a_f_mr,
                'other_occupant_room': (a_short - a_d_wind_e) * r_a_f_or,
                'non_occupant_room': (a_short - a_d_wind_e) * r_a_f_nr,
            },
            'wall_w': {
                'main_occupant_room': (a_short - a_d_wind_w) * r_a_f_mr,
                'other_occupant_room': (a_short - a_d_wind_w) * r_a_f_or,
                'non_occupant_room': (a_short - a_d_wind_w) * r_a_f_nr,
            }
        },
        'inner_walls': {
            'main to other': a_short / n * (r_a_f_mr + r_a_f_or) + min(a_f_mr, a_f_or),
            'main to nonliving': a_long * a_f_mr / (a_f_mr + a_f_or),
            'other to nonliving': a_long * a_f_or / (a_f_mr + a_f_or)
        },
    }


# 共同住宅の面積算出
def get_area_attached(h_f, area_windows, a_f_mr, a_f_or, a_f_nr, a_f, r_a_f_mr, r_a_f_or, r_a_f_nr, a_long, a_short):

    a_d_wind_s, a_adj = get_a_d_wind(area_windows['s'], a_short)
    a_d_wind_n, a_adj = get_a_d_wind(area_windows['n'] + a_adj, a_short)
    a_d_wind_w, a_adj = get_a_d_wind(area_windows['w'] + a_adj, a_long)
    a_d_wind_e, _ = get_a_d_wind(area_windows['e'] + a_adj, a_long)

    return {
        # 窓面積：北窓はその他の居室、南窓は主たる居室、東窓・西窓は各用途に床面積案分で割り付け
        'windows': {
            'n': {
                'main_occupant_room': 0.0,
                'other_occupant_room': a_d_wind_n,
                'non_occupant_room': 0.0,
            },
            's': {
                'main_occupant_room': a_d_wind_s,
                'other_occupant_room': 0.0,
                'non_occupant_room': 0.0,
            },
            'e': {
                'main_occupant_room': a_d_wind_e * r_a_f_mr,
                'other_occupant_room': a_d_wind_e * r_a_f_or,
                'non_occupant_room': a_d_wind_e * r_a_f_nr,
            },
            'w': {
                'main_occupant_room': a_d_wind_w * r_a_f_mr,
                'other_occupant_room': a_d_wind_w * r_a_f_or,
                'non_occupant_room': a_d_wind_w * r_a_f_nr,
            },
            'top': {
                'main_occupant_room': 0.0,
                'other_occupant_room': 0.0,
                'non_occupant_room': 0.0,
            }
        },
        # 壁面積：北壁はその他の居室、南壁は主たる居室、天井・床・東壁・西壁は各用途に床面積案分で割り付け
        'general_parts': {
            'ceiling': {
                'main_occupant_room': a_f * r_a_f_mr,
                'other_occupant_room': a_f * r_a_f_or,
                'non_occupant_room': a_f * r_a_f_nr,
            },
            'floor': {
                'main_occupant_room': a_f * r_a_f_mr,
                'other_occupant_room': a_f * r_a_f_or,
                'non_occupant_room': a_f * r_a_f_nr,
            },
            'wall_n': {
                'main_occupant_room': 0.0,
                'other_occupant_room': a_short - a_d_wind_n,
                'non_occupant_room': 0.0,
            },
            'wall_s': {
                'main_occupant_room': a_short - a_d_wind_s,
                'other_occupant_room': 0.0,
                'non_occupant_room': 0.0,
            },
            'wall_e': {
                'main_occupant_room': (a_long - a_d_wind_e) * r_a_f_mr,
                'other_occupant_room': (a_long - a_d_wind_e) * r_a_f_or,
                'non_occupant_room': (a_long - a_d_wind_e) * r_a_f_nr,
            },
            'wall_w': {
                'main_occupant_room': (a_long - a_d_wind_w) * r_a_f_mr,
                'other_occupant_room': (a_long - a_d_wind_w) * r_a_f_or,
                'non_occupant_room': (a_long - a_d_wind_w) * r_a_f_nr,
            }
        },
        # 内壁面積
        'inner_walls': {
            'main to other': a_short,
            'main to nonliving': a_short,
            'other to nonliving': a_short
        }
    }


def get_area(a_f_total, a_f_mr, a_f_or, a_evlp_total, house_type):

    a_f_nr = get_a_f_nr(a_f_total, a_f_mr, a_f_or)

    # 階高
    h_f = {
        'detached': [2.9, 2.7],
        'condominium': [2.8]
    }[house_type]

    # 階数
    n = len(h_f)

    # 1フロアあたりの床面積, m2
    a_f = a_f_total / n

    # 建物高の算出
    h_total = sum(h_f)

    # 水平方向の長さ
    #   短手方向, m
    #   長手方向, m
    #   周長の合計, m
    l_short, l_long, l_total = get_geometry(a_evlp_total, a_f, h_total)

    # 基準住戸の総外皮面積の算出
    area_total_skin = l_total * h_total + 2 * a_f

    # 開口部面積, m2
    area_windows = get_area_windows(house_type, area_total_skin)

    # 延床面積に対する用途別床面積の割合
    r_a_f_mr = a_f_mr / a_f_total
    r_a_f_or = a_f_or / a_f_total
    r_a_f_nr = a_f_nr / a_f_total

    a_long = l_long * sum(h_f)
    a_short = l_short * sum(h_f)


    # 部位面積, ㎡
    if house_type == 'detached':
        area = get_area_detached(h_f, area_windows, a_f_mr, a_f_or, a_f_nr, a_f, r_a_f_mr, r_a_f_or, r_a_f_nr, a_long, a_short)
    elif house_type == 'condominium':
        area = get_area_attached(h_f, area_windows, a_f_mr, a_f_or, a_f_nr, a_f, r_a_f_mr, r_a_f_or, r_a_f_nr, a_long, a_short)

#    d['general_parts'] = get_list_general_parts(area['general_parts'])
#    d['windows'] = get_list_windows(area['windows'])
#    d['inner_walls'] = get_list_inner_walls(area['inner_walls'])

#    return d['general_parts'], d['windows'], d['inner_walls']

    general_parts = get_list_general_parts(area['general_parts'])
    windows = get_list_windows(area['windows'])
    inner_walls = get_list_inner_walls(area['inner_walls'])

    return general_parts, windows, inner_walls


if __name__ == '__main__':

    result = get_area(a_f_total=120.0, a_f_mr=60.0, a_f_or=30.0, a_evlp_total=360.0, house_type='detached')

    print(result)