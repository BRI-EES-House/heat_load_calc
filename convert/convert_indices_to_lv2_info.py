import nbimporter
import copy
import numpy as np
import matplotlib.pyplot as plt

import factor_f
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


def get_general_parts(a_a):

    table = [
        ['simple_general_part1', 'ceiling', 'outdoor', 'outdoor','top', 50.85],
        ['simple_general_part2', 'wall', 'outdoor', 'outdoor','0', 30.47],
        ['simple_general_part3', 'wall', 'outdoor', 'outdoor','90', 22.37],
        ['simple_general_part4', 'wall', 'outdoor', 'outdoor','180', 47.92],
        ['simple_general_part5', 'wall', 'outdoor', 'outdoor','270', 22.28],
        ['simple_general_part6', 'floor', 'open_underfloor', 'not_outdoor', 'bottom', 45.05],
    ]

    return [
        {
            'name': row[0],
            'general_part_type': row[1],
            'next_space': row[2],
            'external_surface_type': row[3],
            'direction': get_direction(row[4]),
            'area': row[5] * get_r_size(a_a),
            'spec': None
        } for row in table]


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


def get_windows(a_a, region):

    is_f_value_input = False
    f_h, f_c = None, None

    table = [
        ['simple_window_part1', 'outdoor', '0', 22.69, None, 1.0, 1.0],
        ['simple_window_part2', 'outdoor', '90', 2.38, None, 1.0, 1.0],
        ['simple_window_part3', 'outdoor', '180', 3.63, None, 1.0, 1.0],
        ['simple_window_part4', 'outdoor', '270', 4.37, None, 1.0, 1.0],
    ]

    parts = []

    for row in table:
        direction = get_direction(row[2])
        y1, y2, z = get_y1_y2_z(is_f_value_input, region, direction, f_h, f_c)
        eta_d = get_eta_d(row[5], row[6])

        parts.append({
            'name': row[0],
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


def get_doors(a_a):

    table = [
        ['simple_door_part1', 'outdoor', '90', 1.89, None],
        ['simple_door_part2', 'outdoor', '180', 1.62, None],
    ]

    return [
        {
            'name': row[0],
            'next_space': row[1],
            'direction': get_direction(row[2]),
            'area': row[3] * get_r_size(a_a),
            'spec': {
                'u_value': row[4],
                'is_sunshade_input': False,
            }
        } for row in table
    ]


def get_earthfloor_perimeters(a_a):

    table = [
        ['simple_earthfloor_perimeter1', 'outdoor', '90', 1.82],
        ['simple_earthfloor_perimeter2', 'outdoor', '180', 1.37],
        ['simple_earthfloor_perimeter3', 'open_underfloor', 'other', 3.19],
        ['simple_earthfloor_perimeter4', 'outdoor', '90', 1.82],
        ['simple_earthfloor_perimeter5', 'outdoor', '180', 1.82],
        ['simple_earthfloor_perimeter6', 'open_underfloor', 'other', 3.64],
    ]

    return [
        {
            'name': row[0],
            'next_space': row[1],
            'direction': get_direction(row[2]),
            'length': row[3] * get_r_size(a_a),
            'spec': None
        } for row in table
    ]


def get_earthfloor_centers(a_a):

    table = [
        ['simple_earthfloor_center1', 2.48],
        ['simple_earthfloor_center2', 3.31],
    ]

    return [
        {
            'name': row[0],
            'area': row[1] * get_r_size(a_a),
        } for row in table
    ]


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


def convert(region, house_type, a_f_mr, a_f_or, a_f_total, envelope, indices):

    # 床断熱住戸、浴室は断熱区画内とする
    house_type = 'f_b'

    general_parts = get_general_parts(a_f_total)

    windows = get_windows(a_f_total, region)

    doors = get_doors(a_f_total)

    earthfloor_perimeters = get_earthfloor_perimeters(a_f_total)

    earthfloor_centers = get_earthfloor_centers(a_f_total)

    # U値、η値の取得
    l_direction_s = ['top', 'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw']

    f_heating = min(factor_f.get_f_without_eaves('heating', region, direction) for direction in l_direction_s)
    f_cooling = max(factor_f.get_f_without_eaves('cooling', region, direction) for direction in l_direction_s)

    u_a = indices['u_a']
    eta_a_h = indices['eta_a_h']
    eta_a_c = indices['eta_a_c']

    eta, eta_heating, eta_cooling, part_U = get_u_and_eta.calc_parts_spec(
        region=region,
        general_parts=general_parts, windows=windows, doors=doors,
        earthfloor_perimeters=earthfloor_perimeters, earthfloor_centers=earthfloor_centers,
        u_a=u_a, eta_a_h=eta_a_h, eta_a_c=eta_a_c
    )

    return {
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
    indices = envelope['indices']

    result = convert(
        region=region, house_type=house_type, a_f_mr=a_f_mr, a_f_or=a_f_or, a_f_total=a_f_total,
        envelope=envelope, indices=indices
    )

    print(result)
