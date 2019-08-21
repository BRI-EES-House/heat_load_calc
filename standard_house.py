import copy
import math
import nbimporter
import numpy

import standard_house_area
import get_u_and_eta_from_u_a_and_eta_a as get_u_and_eta


def get_std_UA(house_type, region):
    return {
        'detached'    : {1: 0.46, 2: 0.46, 3: 0.56, 4: 0.75, 5: 0.87, 6: 0.87, 7: 0.87, 8: 2.14 },
        'condominium' : {1: 0.41, 2: 0.41, 3: 0.44, 4: 0.69, 5: 0.75, 6: 0.75, 7: 0.75, 8: 1.67 }
    }[house_type][region]


def get_std_etaAH(house_type, region):
    return {
        'detached'    : {1: 2.5,  2: 2.3,  3: 2.7,  4: 3.7,  5: 4.5,  6: 4.3,  7: 4.6,  8: 3.2 },
        'condominium' : {1: 1.5,  2: 1.3,  3: 1.5,  4: 1.8,  5: 2.1,  6: 2.0,  7: 2.1,  8: 2.4 }
    }[house_type][region]


def get_std_etaAC(house_type, region):
    return {
        'detached'    : {1: 1.9,  2: 1.9,  3: 2.0,  4: 2.7,  5: 3.0,  6: 2.8,  7: 2.7,  8: 3.2 },
        'condominium' : {1: 1.1,  2: 1.1,  3: 1.1,  4: 1.4,  5: 1.5,  6: 1.4,  7: 1.3,  8: 2.4 }
    }[house_type][region]


def get_total_area(d):
    d_area = []
    for parts in ['general_parts', 'windows', 'doors', 'earthfloors']:
        if (parts in d['envelope']) == True:
            d_area.extend(d['envelope'][parts])

    return sum(part['area'] for part in d_area)


def convert_common(d, common):
    d['common']['total_outer_skin_area'] = get_total_area(d)

    return d['common']


def get_area(d_envelope, area_type):
    l_next_space = ['outdoor', 'open_space', 'closed_space', 'open_underfloor', 'air_conditioned', 'closed_underfloor']
    l_direction = ['top', 'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'bottom', 'upward', 'horizontal', 'downward']
    l_space_type = ['main_occupant_room', 'other_occupant_room', 'non_occupant_room', 'underfloor']
    l_general_part_type = ['roof', 'ceiling', 'wall', 'floor', 'boundary_wall', 'upward_boundary_flo',
                           'downward_boundary_floor']

    area = {}

    # 一般部位
    # 用途を考慮しない場合
    if area_type == 'design_house_without_room_usage':
        area['general_parts'] = {
            v: {
                w: {
                    x: sum(y['area'] for y in d_envelope['general_parts'] \
                           if (y['general_part_type'] == v and y['next_space'] == w and y['direction'] == x))
                    for x in l_direction
                } for w in l_next_space
            } for v in l_general_part_type
        }
    # 用途を考慮する場合
    else:
        area['general_parts'] = {
            v: {
                w: {
                    x: {
                        y: sum(z['area'] for z in d_envelope['general_parts'] \
                               if (z['general_part_type'] == v and z['next_space'] == w and z['direction'] == x and z[
                            'space_type'] == y))
                        for y in l_space_type
                    } for x in l_direction
                } for w in l_next_space
            } for v in l_general_part_type
        }

    # 窓
    # 用途を考慮しない場合
    if area_type == 'design_house_without_room_usage':
        area['windows'] = {
            w: {
                x: sum(y['area'] for y in d_envelope['windows'] \
                       if (y['next_space'] == w and y['direction'] == x)) for x in l_direction
            } for w in l_next_space
        }
    # 用途を考慮する場合
    else:
        area['windows'] = {
            w: {
                x: {
                    y: sum(z['area'] for z in d_envelope['windows'] \
                           if (z['next_space'] == w and z['direction'] == x and z['space_type'] == y)) for y in
                l_space_type
                } for x in l_direction
            } for w in l_next_space
        }

    # ドア
    # 用途を考慮しない場合
    if area_type == 'design_house_without_room_usage':
        area['doors'] = {
            w: {
                x: sum(y['area'] for y in d_envelope['doors'] \
                       if (y['next_space'] == w and y['direction'] == x)) for x in l_direction
            } for w in l_next_space
        }
    # 用途を考慮する場合
    else:
        area['doors'] = {
            w: {
                x: {
                    y: sum(z['area'] for z in d_envelope['doors'] \
                           if (z['next_space'] == w and z['direction'] == x and z['space_type'] == y)) for y in
                l_space_type
                } for x in l_direction
            } for w in l_next_space
        }

    # 土間床等の外周部
    # 用途を考慮しない場合
    if area_type == 'design_house_without_room_usage':
        area['earthfloor_perimeters'] = {
            w: {
                x: sum(y['length'] for y in d_envelope['earthfloor_perimeters'] \
                       if (y['next_space'] == w and y['direction'] == x)) \
                for x in l_direction
            } for w in l_next_space
        }
    # 用途を考慮する場合
    else:
        area['earthfloor_perimeters'] = {
            w: {
                x: {
                    y: sum(z['length'] for z in d_envelope['earthfloor_perimeters'] \
                           if (z['next_space'] == w and z['direction'] == x and z['space_type'] == y)) \
                    for y in l_space_type
                } for x in l_direction
            } for w in l_next_space
        }

    return area


def get_list_general_parts(area_general_parts, area_type):
    l = []

    # 用途を考慮しない場合
    if area_type == 'design_house_without_room_usage':
        for v in area_general_parts.keys():
            for w in area_general_parts[v].keys():
                for x in area_general_parts[v][w].keys():
                    if area_general_parts[v][w][x] > 0:
                        l.append({
                            'name': v + '_' + (x if w == 'outdoor' else w),
                            'general_part_type': v,
                            'next_space': w,
                            'external_surface_type': ('outdoor' if w == 'outdoor' else None),
                            'direction': x,
                            'area': area_general_parts[v][w][x],
                            'spec': {
                                'structure': 'wood',
                                'u_value_input_method_wood': 'u_value_directly',
                                'is_sunshade_input': False
                            }
                        })

    # 用途を考慮する場合
    else:
        for v in area_general_parts.keys():
            for w in area_general_parts[v].keys():
                for x in area_general_parts[v][w].keys():
                    for y in area_general_parts[v][w][x].keys():
                        if area_general_parts[v][w][x][y] > 0:
                            l.append({
                                'name': v + '_' + (x if w == 'outdoor' else w) + '_' + y,
                                'general_part_type': v,
                                'next_space': w,
                                'external_surface_type': ('outdoor' if w == 'outdoor' else None),
                                'direction': x,
                                'area': area_general_parts[v][w][x][y],
                                'space_type': y,
                                'spec': {
                                    'structure': 'wood',
                                    'u_value_input_method_wood': 'u_value_directly',
                                    'is_sunshade_input': False
                                }
                            })

    return l


def get_list_windows(area_windows, area_type):
    l = []

    # 用途を考慮しない場合
    if area_type == 'design_house_without_room_usage':
        for x in area_windows.keys():
            for y in area_windows[x].keys():
                if area_windows[x][y] > 0:
                    l.append({
                        'name': (y if x == 'outdoor' else x),
                        'next_space': x,
                        'direction': y,
                        'area': area_windows[x][y],
                        'spec': {
                            'window_type': 'single',
                            'windows': [{
                                'u_value_input_method': 'u_value_directly',
                                'eta_value_input_method': 'eta_d_value_directly',
                                'glass_type': 'single'
                            }],
                            'attachment_type': 'none',
                            'is_windbreak_room_attached': False,
                            'is_sunshade_input': True,
                            'sunshade': {
                                'existance': True,
                                'input_method': 'simple',
                                'd_h': 3 if y in ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'] else 0,
                                'd_e': 0,
                                'depth': 1 if y in ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'] else 0,
                            }
                        }
                    })

    # 用途を考慮する場合
    else:
        for x in area_windows.keys():
            for y in area_windows[x].keys():
                for z in area_windows[x][y].keys():
                    if area_windows[x][y][z] > 0:
                        l.append({
                            'name': (y if x == 'outdoor' else x) + '_' + z,
                            'next_space': x,
                            'direction': y,
                            'area': area_windows[x][y][z],
                            'space_type': z,
                            'spec': {
                                'window_type': 'single',
                                'windows': [{
                                    'u_value_input_method': 'u_value_directly',
                                    'eta_value_input_method': 'eta_d_value_directly',
                                    'glass_type': 'single'
                                }],
                                'attachment_type': 'none',
                                'is_windbreak_room_attached': False,
                                'is_sunshade_input': True,
                                'sunshade': {
                                    'existance': True,
                                    'input_method': 'simple',
                                    'd_h': 3 if y in ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'] else 0,
                                    'd_e': 0,
                                    'depth': 1 if y in ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'] else 0,
                                }
                            }
                        })

    return l


def get_list_doors(area_doors, area_type):
    l = []

    # 用途を考慮しない場合
    if area_type == 'design_house_without_room_usage':
        for x in area_doors.keys():
            for y in area_doors[x].keys():
                if area_doors[x][y] > 0:
                    l.append({
                        'name': (y if x == 'outdoor' else x),
                        'next_space': x,
                        'direction': y,
                        'area': area_doors[x][y],
                        'spec': {
                            'is_sunshade_input': False
                        }
                    })

    # 用途を考慮する場合
    else:
        for x in area_doors.keys():
            for y in area_doors[x].keys():
                for z in area_doors[x][y].keys():
                    if area_doors[x][y][z] > 0:
                        l.append({
                            'name': (y if x == 'outdoor' else x) + '_' + z,
                            'next_space': x,
                            'direction': y,
                            'area': area_doors[x][y][z],
                            'space_type': z,
                            'spec': {
                                'is_sunshade_input': False
                            }
                        })

    return l


def get_list_earthfloor_perimeters(area_earthfloor_perimeters, area_type):
    l = []

    # 用途を考慮しない場合
    if area_type == 'design_house_without_room_usage':
        for x in area_earthfloor_perimeters.keys():
            for y in area_earthfloor_perimeters[x].keys():
                if area_earthfloor_perimeters[x][y] > 0:
                    l.append({
                        'name': (y if x == 'outdoor' else x),
                        'length': area_earthfloor_perimeters[x][y],
                        'next_space': x,
                        'direction': y,
                        'spec': {}
                    })

    # 用途を考慮する場合
    else:
        for x in area_earthfloor_perimeters.keys():
            for y in area_earthfloor_perimeters[x].keys():
                for z in area_earthfloor_perimeters[x][y].keys():
                    if area_earthfloor_perimeters[x][y][z] > 0:
                        l.append({
                            'name': (y if x == 'outdoor' else x) + '_' + z,
                            'length': area_earthfloor_perimeters[x][y][z],
                            'space_type': z,
                            'next_space': x,
                            'direction': y,
                            'spec': {}
                        })

    return l


def get_list(area, area_type):
    d = {}
    d['general_parts'] = get_list_general_parts(area['general_parts'], area_type)
    d['windows'] = get_list_windows(area['windows'], area_type)
    d['doors'] = get_list_doors(area['doors'], area_type)
    d['earthfloor_perimeters'] = get_list_earthfloor_perimeters(area['earthfloor_perimeters'], area_type)

    return d['general_parts'], d['windows'], d['doors'], d['earthfloor_perimeters']


def convert_parts(d, area_type):
    standard_d = {}

    # 部位面積の取得
    # 基準値計算用住戸を想定する場合
    if area_type == 'standard_house':
        # 基準値計算用住戸の面積取得
        d_standard_area = {'envelope': {}}
        d_standard_area['envelope']['general_parts'], d_standard_area['envelope'][
            'windows'], inner_walls = standard_house_area.get_area(
            a_f_total=d['common']['total_floor_area'],
            a_f_mr=d['common']['main_occupant_room_floor_area'],
            a_f_or=d['common']['other_occupant_room_floor_area'],
            a_evlp_total=d['common']['total_outer_skin_area'],
            house_type=d['common']['house_type']
        )
        d_standard_area['envelope']['doors'], d_standard_area['envelope']['earthfloor_perimeters'] = [], []

        standard_d['general_parts'], standard_d['windows'], standard_d['doors'], standard_d['earthfloor_perimeters'] \
            = get_list(get_area(d_standard_area['envelope'], area_type), area_type)

    # 設計住戸の面積を使用する場合
    elif area_type == 'design_house_with_room_usage' or area_type == 'design_house_without_room_usage':
        standard_d['general_parts'], standard_d['windows'], standard_d['doors'], standard_d['earthfloor_perimeters'] \
            = get_list(get_area(d['envelope'], area_type), area_type)

    # U値、η値の取得
    Eta, Eta_heating, Eta_cooling, part_U = get_u_and_eta.calc_adjustment_factor(d)

    # U値、η値の設定
    for part in standard_d['general_parts']:
        part['spec']['u_value_wood'] = part_U[part['general_part_type']]
    for part in standard_d['windows']:
        part['spec']['windows'][0]['u_vaue'] = part_U['window']
        part['spec']['windows'][0]['eta_d_value'] = Eta
    for part in standard_d['doors']:
        part['spec']['u_vaue'] = part_U['door']
    for part in standard_d['earthfloor_perimeters']:
        part['spec']['psi_value'] = part_U['earthfloor_perimeter']

    return standard_d['general_parts'], standard_d['windows'], standard_d['doors'], standard_d['earthfloor_perimeters']


def convert_earthfloor(d_earthfloors):
    d = copy.deepcopy(d_earthfloors)

    return d


def convert(d, area_type):

    common = d['common']
    house_type = common['house_type']
    region = common['region']

    indices = {
        'u_a': get_std_UA(house_type, region),
        'eta_a_h': get_std_etaAH(house_type, region),
        'eta_a_c': get_std_etaAC(house_type, region),
    }

    d['envelope']['index'] = indices

    standard_d = {'envelope': {}}
    standard_d['common'] = convert_common(d, common)

    rtn_general_parts, rtn_windows, rtn_doors, rtn_earthfloor_perimeters = convert_parts(d, area_type)

    standard_d['envelope']['general_parts'] = rtn_general_parts
    standard_d['envelope']['windows'] = rtn_windows
    standard_d['envelope']['doors'] = rtn_doors
    standard_d['envelope']['earthfloor_perimeters'] = rtn_earthfloor_perimeters

    if ('earthfloors' in d['envelope']) == True:
        standard_d['envelope']['earthfloors'] = convert_earthfloor(d['envelope']['earthfloors'])

    return standard_d


if __name__ == '__main__':

    d = {
        'common': {
            'region': 6,
            'house_type': 'condominium',  # 'detached','condominium'
            'main_occupant_room_floor_area': 98.0,
            'other_occupant_room_floor_area': 0.0,
            'total_floor_area': 98.0
        },
        'envelope': {
            'general_parts': [
                {'general_part_type': 'ceiling', 'area': 49, 'next_space': 'outdoor', 'direction': 'top',
                 'space_type': 'main_occupant_room'},
                {'general_part_type': 'wall', 'area': 40, 'next_space': 'outdoor', 'direction': 'n',
                 'space_type': 'main_occupant_room'},
                {'general_part_type': 'wall', 'area': 42, 'next_space': 'outdoor', 'direction': 'e',
                 'space_type': 'main_occupant_room'},
                {'general_part_type': 'wall', 'area': 22, 'next_space': 'outdoor', 'direction': 's',
                 'space_type': 'main_occupant_room'},
                {'general_part_type': 'wall', 'area': 42, 'next_space': 'outdoor', 'direction': 'w',
                 'space_type': 'main_occupant_room'},
                {'general_part_type': 'floor', 'area': 45, 'next_space': 'open_underfloor', 'direction': 'bottom',
                 'space_type': 'main_occupant_room'}
            ],
            'windows': [
                {'area': 20, 'next_space': 'outdoor', 'direction': 's', 'space_type': 'main_occupant_room'}
            ],
            'doors': [
                {'area': 2, 'next_space': 'outdoor', 'direction': 'n', 'space_type': 'main_occupant_room'}
            ],
            'earthfloor_perimeters': [
                {'length': 4, 'next_space': 'outdoor', 'direction': 'n', 'space_type': 'main_occupant_room'}
            ],
            'earthfloor_centers': [
                {'area': 4}
            ]
        }
    }

    result1 = convert(d, area_type='standard_house')
    print(result1)

    result2 = convert(d, area_type='design_house_with_room_usage')
    print(result2)


