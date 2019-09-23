import copy
import numpy as np

import factor_f

import model_house
import convert_model_house_to_house_dict

import get_u_and_eta_from_u_a_and_eta_a as get_u_and_eta


def convert(input_data):

    common = input_data['common']
    region = common['region']
    house_type = common['house_type']
    a_f_total = common['total_floor_area']

    envelope = input_data['envelope']
    indices = envelope['indices']
    u_a = indices['u_a']
    eta_a_h = indices['eta_a_h']
    eta_a_c = indices['eta_a_c']
    a_env_total = indices['total_envelope_area']

    # 窓の開口部比率は10.0%とする。
    r_open = 0.1

    # 戸建住戸の場合は床断熱で浴室は基礎断熱とする。
    floor_ins_type, bath_ins_type = {
        'detached': ('floor', 'base'),
        'attached': (None, None)
    }[house_type]

    model_house_shape = model_house.calc_area(
        house_type=house_type, a_f_total=a_f_total, r_open=r_open,
        floor_ins_type=floor_ins_type, bath_ins_type=bath_ins_type, a_env_input=a_env_total
    )

    model_house_no_spec = convert_model_house_to_house_dict.convert(**model_house_shape)

    # U値、η値の取得
    l_direction_s = ['top', 'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw']

    f_heating = min(factor_f.get_f_without_eaves('heating', region, direction) for direction in l_direction_s)
    f_cooling = max(factor_f.get_f_without_eaves('cooling', region, direction) for direction in l_direction_s)

    eta, eta_heating, eta_cooling, part_U = get_u_and_eta.calc_parts_spec(
        region=region,
        general_parts=model_house_no_spec['general_parts'],
        windows=model_house_no_spec['windows'],
        doors=model_house_no_spec['doors'],
        earthfloor_perimeters=model_house_no_spec['earthfloor_perimeters'],
        earthfloor_centers=model_house_no_spec['earthfloor_centers'],
        u_a=u_a,
        eta_a_h=eta_a_h,
        eta_a_c=eta_a_c
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

    input_data_1 = {
        'common': {
            'region': 6,
            'house_type': 'detached',
            'main_occupant_room_floor_area': 30.0,
            'other_occupant_room_floor_area': 30.0,
            'total_floor_area': 90.0,
        },
        'envelope': {
            'input_method': 'index',
            'indices': {
                'u_a': 0.87,
                'eta_a_h': 2.8,
                'eta_a_c': 1.4,
                'total_envelope_area': 266.0962919879752
            }
        }
    }

    result = convert(input_data=input_data_1)

    print(result)
