import nbimporter
import copy
import numpy as np
import matplotlib.pyplot as plt

import f
import get_u_and_eta_from_u_a_and_eta_a as get_u_and_eta


def get_r_size(a_a):
    a_s_a = 90.0

    return a_a / a_s_a


def get_direction(angle):
    if angle == '0':
        return 'sw'
    elif angle == '90':
        return 'nw'
    elif angle == '180':
        return 'ne'
    elif angle == '270':
        return 'se'
    else:
        return angle


def get_general_parts(a_a, house_type, u_roof, u_wall, u_floor_other=None, u_floor_bath=None):
    table = [
        [1, 'ceiling', 'outdoor', 'top', {'f_f': 50.85, 'f_b': 50.85, 'f_n': 50.85, 'b': 50.85}, u_roof],
        [2, 'wall', 'outdoor', '0', {'f_f': 30.47, 'f_b': 30.47, 'f_n': 30.47, 'b': 30.47}, u_wall],
        [3, 'wall', 'outdoor', '90', {'f_f': 22.37, 'f_b': 22.37, 'f_n': 22.37, 'b': 22.37}, u_wall],
        [4, 'wall', 'outdoor', '180', {'f_f': 47.92, 'f_b': 47.92, 'f_n': 47.92, 'b': 47.92}, u_wall],
        [5, 'wall', 'outdoor', '270', {'f_f': 22.28, 'f_b': 22.28, 'f_n': 22.28, 'b': 22.28}, u_wall],
        [6, 'floor', 'open_underfloor', 'bottom', {'f_f': 45.05, 'f_b': 45.05, 'f_n': 48.36, 'b': 0.00}, u_floor_other],
        [7, 'floor', 'open_underfloor', 'bottom', {'f_f': 3.31, 'f_b': 0.00, 'f_n': 0.00, 'b': 0.00}, u_floor_bath],
    ]

    parts = []

    for row in table:

        if row[4][house_type] > 0.0:
            parts.append({
                'name': 'simple_general_part' + str(row[0]),
                'general_part_type': row[1],
                'next_space': row[2],
                'external_surface_type': {
                    'outdoor': 'outdoor',
                    'open_underfloor': 'not_outdoor'
                }[row[2]],
                'direction': get_direction(row[3]),
                'area': row[4][house_type] * get_r_size(a_a),
                'spec': {
                    'structure': 'wood',
                    'u_value_input_method_wood': 'u_value_directly',
                    'u_value_wood': row[5],
                    'is_sunshade_input': False
                }
            })

    return parts


def get_heating_overhang_width(is_f_value_input, region, direction, y1, y2, f=None):
    if is_f_value_input:

        if region <= 7:
            a, b, c = {
                'se': (5, 20, 3),
                'sw': (5, 20, 3),
                'nw': (10, 15, 2),
                'ne': (10, 15, 2)
            }[direction]
        elif region == 8:
            raise ValueError('z_Hを取得する関数で地域が8地域を指定されました。')
        else:
            raise ValueError('z_Hを取得する関数でregionに不正な値が指定されました。')

        _f = min(f, 0.72)

        if ((_f / 0.01) - a) <= 0:
            return 5.0
        else:
            return min((b * (c * y1 + y2)) / ((_f / 0.01) - a), 5.0)

    else:

        l_h_2 = 1 / 0.3

        return (y1 + y2) / l_h_2


def get_cooling_overhang_width(is_f_value_input, region, direction, y1, y2, f=None):
    if is_f_value_input:

        if region <= 7:
            a, b, c = {
                'se': (16, 24, 2),
                'sw': (16, 24, 2),
                'nw': (16, 24, 2),
                'ne': (16, 24, 2)
            }[direction]
        elif region == 8:
            a, b, c = {
                'se': (16, 19, 2),
                'sw': (16, 19, 2),
                'nw': (16, 24, 2),
                'ne': (16, 24, 2)
            }[direction]
        else:
            raise ValueError('z_Cを取得する関数でregionに不正な値が指定されました。')

        _f = min(f, 0.93)

        if ((_f / 0.01) - a) <= 0:
            return 5.0
        else:
            return min((b * (c * y1 + y2)) / ((_f / 0.01) - a), 5.0)

    else:

        return 0.0


def get_y1_y2_z(is_f_value_input, region, direction, f_h=None, f_c=None):
    y1, y2 = 0.0, 1.1

    if region == 8:
        z_c = get_cooling_overhang_width(is_f_value_input, region, direction, y1, y2, f_c)
        z = z_c
    else:
        z_h = get_heating_overhang_width(is_f_value_input, region, direction, y1, y2, f_h)
        z_c = get_cooling_overhang_width(is_f_value_input, region, direction, y1, y2, f_c)
        z = (z_h + z_c) / 2

    return y1, y2, z


def get_eta_d(eta_d_h, eta_d_c):
    return (eta_d_h + eta_d_c) / 2


def get_windows(a_a, region, u_window, eta_d_h, eta_d_c, is_f_value_input, f_h, f_c):
    table = [
        [1, 'outdoor', '0', 22.69, u_window, eta_d_h, eta_d_c],
        [2, 'outdoor', '90', 2.38, u_window, eta_d_h, eta_d_c],
        [3, 'outdoor', '180', 3.63, u_window, eta_d_h, eta_d_c],
        [4, 'outdoor', '270', 4.37, u_window, eta_d_h, eta_d_c],
    ]

    parts = []

    for row in table:
        direction = get_direction(row[2])
        y1, y2, z = get_y1_y2_z(is_f_value_input, region, direction, f_h, f_c)
        eta_d = get_eta_d(row[5], row[6])

        parts.append({
            'name': 'simple_window_part' + str(row[0]),
            'next_space': row[1],
            'direction': direction,
            'area': row[3] * get_r_size(a_a),
            'spec': {
                'window_type': 'single',
                'windows': [
                    {
                        'u_value_input_method': 'u_value_directly',
                        'u_value': row[4],
                        'eta_d_value_input_method': 'eta_d_value_directly',
                        'eta_d_value': eta_d,
                        'glass_type': 'single',
                    }
                ],
                'attachment_type': 'none',
                'is_windbreak_room_attached': False,
                'sunshade': {
                    'y1': y1,
                    'y2': y2,
                    'z': z,
                }
            }
        })

    return parts


def get_doors(a_a, u_door):
    table = [
        [1, 'outdoor', '90', 1.89, u_door],
        [2, 'outdoor', '180', 1.62, u_door],
    ]

    parts = []

    for row in table:
        direction = get_direction(row[2])

        parts.append({
            'name': 'simple_door_part' + str(row[0]),
            'next_space': row[1],
            'direction': direction,
            'area': row[3] * get_r_size(a_a),
            'spec': {
                'u_value': row[4],
                'is_sunshade_input': False,
            }
        })

    return parts


def get_earthfloor_perimeters(a_a, house_type, psi_prm_etrc, psi_prm_bath=None, psi_prm_other=None):
    table = [
        [1, 'outdoor', '90', {'f_f': 1.82, 'f_b': 1.82, 'f_n': 1.82, 'b': 1.82}, psi_prm_etrc],
        [2, 'outdoor', '180', {'f_f': 1.37, 'f_b': 1.37, 'f_n': 1.37, 'b': 1.37}, psi_prm_etrc],
        [3, 'open_underfloor', 'other', {'f_f': 3.19, 'f_b': 3.19, 'f_n': 3.19, 'b': 0.00}, psi_prm_etrc],
        [4, 'outdoor', '90', {'f_f': 0.00, 'f_b': 1.82, 'f_n': 0.00, 'b': 1.82}, psi_prm_bath],
        [5, 'outdoor', '180', {'f_f': 0.00, 'f_b': 1.82, 'f_n': 0.00, 'b': 1.82}, psi_prm_bath],
        [6, 'open_underfloor', 'other', {'f_f': 0.00, 'f_b': 3.64, 'f_n': 0.00, 'b': 0.00}, psi_prm_bath],
        [7, 'outdoor', '0', {'f_f': 0.00, 'f_b': 0.00, 'f_n': 0.00, 'b': 10.61}, psi_prm_other],
        [8, 'outdoor', '90', {'f_f': 0.00, 'f_b': 0.00, 'f_n': 0.00, 'b': 1.15}, psi_prm_other],
        [9, 'outdoor', '180', {'f_f': 0.00, 'f_b': 0.00, 'f_n': 0.00, 'b': 7.42}, psi_prm_other],
        [10, 'outdoor', '270', {'f_f': 0.00, 'f_b': 0.00, 'f_n': 0.00, 'b': 4.79}, psi_prm_other],
    ]

    parts = []

    num = 0

    for row in table:

        if row[3][house_type] > 0.0:
            parts.append({
                'name': 'simple_earthfloor_perimeter' + str(row[0]),
                'next_space': row[1],
                'direction': get_direction(row[2]),
                'length': row[3][house_type] * get_r_size(a_a),
                'spec': {
                    'psi_value': row[4],
                }
            })

    return parts


def get_earthfloor_centers(a_a, house_type):
    table = [
        [1, {'f_f': 2.48, 'f_b': 2.48, 'f_n': 2.48, 'b': 2.48}],
        [2, {'f_f': 0.00, 'f_b': 3.31, 'f_n': 0.00, 'b': 3.31}],
        [3, {'f_f': 0.00, 'f_b': 0.00, 'f_n': 0.00, 'b': 45.05}],
    ]

    parts = []

    for row in table:

        if row[1][house_type] > 0.0:
            parts.append({
                'name': 'simple_earthfloor_center' + str(row[0]),
                'area': row[1][house_type] * get_r_size(a_a),
            })

    return parts


def get_house_type(insulation_type, insulation_type_bathroom):
    if insulation_type == 'floor':
        if insulation_type_bathroom == 'floor':
            return 'f_f'
        elif insulation_type_bathroom == 'base':
            return 'f_b'
        elif insulation_type_bathroom == 'inside':
            return 'f_n'
        else:
            raise Exception('床断熱住戸における浴室の断熱の種類を指定するkeyが間違っています。')
    elif insulation_type == 'base':
        return 'b'
    else:
        raise Exception('住戸の種類を指定するkeyが間違っています。')


def convert(d):
    common = d['common']
    total_floor_area = common['total_floor_area']
    a_a = common['total_floor_area']
    region = common['region']

    envelope = d['envelope']

    # 床断熱住戸、浴室は断熱区画内とする
    house_type = get_house_type('floor', 'inside')

    # 共通要素はそのまま保持する
    d_common = copy.deepcopy(d['common'])

    u_roof, u_wall, u_floor_other, u_floor_bath, u_window, u_door = None, None, None, None, None, None
    eta_d_h, eta_d_c = 1, 1
    is_f_value_input = False
    f_h, f_c = None, None
    psi_prm_etrc, psi_prm_other, psi_prm_bath = None, None, None

    general_parts = get_general_parts(a_a, house_type, u_roof, u_wall, u_floor_other, u_floor_bath)
    windows = get_windows(a_a, region, u_window, eta_d_h, eta_d_c, is_f_value_input, f_h, f_c)
    doors = get_doors(a_a, u_door)
    earthfloor_perimeters = get_earthfloor_perimeters(a_a, house_type, psi_prm_etrc, psi_prm_bath, psi_prm_other)
    earthfloor_centers = get_earthfloor_centers(a_a, house_type)

    # U値、η値の取得
    l_direction_s = ['top', 'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw']

    f_heating = min(f.get_f('heating', d['common']['region'], direction) for direction in l_direction_s)
    f_cooling = max(f.get_f('cooling', d['common']['region'], direction) for direction in l_direction_s)

    d_for_u_and_eta = {
        'common': d['common'],
        'envelope': {
            'index': d['envelope']['indices'],
            'general_parts': general_parts,
            'windows': windows,
            'doors': doors,
            'earthfloor_perimeters': earthfloor_perimeters,
            'earthfloor_centers': earthfloor_centers
        }
    }

    eta, eta_heating, eta_cooling, part_U = get_u_and_eta.calc_adjustment_factor(d_for_u_and_eta)

    return {
        'common': copy.deepcopy(d['common']),
        'envelope': {
            'simple_method': {
                'insulation_type': 'floor',
                'insulation_type_bathroom': 'inside',
                'u_value_roof': part_U['roof'],
                'u_value_wall': part_U['wall'],
                'u_value_floor_other': part_U['floor'],
                'u_value_door': part_U['window'],
                'u_value_window': part_U['window'],
                'eta_d_value_window_c': eta_cooling,
                'eta_d_value_window_h': eta_heating,
                'is_f_value_input': False,
                'f_value_c': f_cooling,
                'f_value_h': f_heating,
                'psi_value_earthfloor_perimeter_entrance': part_U['earthfloor_perimeter']
            }
        }
    }


if __name__ == '__main__':

    d = {
        'common': {
            'region': 6,
            'house_type': 'detached',
            'main_occupant_room_floor_area': 30.0,
            'other_occupant_room_floor_area': 30.0,
            'total_floor_area': 90.0
        },
        'envelope': {
            'input_method': 'index',
            'indices': {
                'u_a': 0.87,
                'eta_a_h': 2.8,
                'eta_a_c': 1.4
            }
        }
    }

    common = d['common']
    region = common['region']
    house_type = common['house_type']
    a_f_mr = common['main_occupant_room_floor_area']
    a_f_or = common['other_occupant_room_floor_area']
    a_f_total = common['total_floor_area']
    envelope = d['envelope']

    result = convert(d)

    print(result)