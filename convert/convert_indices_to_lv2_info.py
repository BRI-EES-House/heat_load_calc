import factor_f
import model_house
import convert_model_house_to_house_dict
import get_u_psi_eta_from_u_a_and_eta_a as get_u_and_eta


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

    model_house_envelope_no_spec = convert_model_house_to_house_dict.convert(**model_house_shape)

    # U値、η値の取得
    l_direction_s = ['top', 'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw']

    f_heating = min(factor_f.get_f_without_eaves('heating', region, direction) for direction in l_direction_s)
    f_cooling = max(factor_f.get_f_without_eaves('cooling', region, direction) for direction in l_direction_s)

    u, eta_d = get_u_and_eta.calc_parts_spec(
        region=region,
        house_no_spec=model_house_envelope_no_spec,
        u_a_target=u_a,
        eta_a_h_target=eta_a_h,
        eta_a_c_target=eta_a_c
    )

    sunshade = factor_f.Sunshade(
        existence=True, input_method='simple', depth=0.3, d_h=1.0, d_e=0.0,
        x1=None, x2=None, x3=None, y1=None, y2=None, y3=None, z_x_pls=None, z_x_mns=None, z_y_pls=None, z_y_mns=None
    )

    general_parts = [
        {
            'name': p['name'],
            'general_part_type': p['general_part_type'],
            'next_space': p['next_space'],
            'direction': p['direction'],
            'area': p['area'],
            'space_type': p['space_type'],
            'spec': {
                'structure': 'other',
                'u_value_other': get_u_and_eta.get_u_psi(u, p['general_part_type'])
            },
            'is_sunshade_input': False
        } for p in model_house_envelope_no_spec['general_parts']
    ]

    windows = [
        {
            'name': p['name'],
            'next_space': p['next_space'],
            'direction': p['direction'],
            'area': p['area'],
            'space_type': p['space_type'],
            'spec': {
                'window_type': 'single',
                'windows': [
                    {
                        'u_value_input_method': 'u_value_directly',
                        'u_value': get_u_and_eta.get_u_psi(u, 'window'),
                        'eta_value_input_method': 'eta_value_directly',
                        'eta_d_value': eta_d,
                        'glass_type': 'single'
                    }
                ],
                'attachment_type': 'none',
                'is_windbreak_room_attached': 'none',
                'is_sunshade_input': True,
                'sunshade': {
                    'existance': sunshade.existence,
                    'input_method': sunshade.input_method,
                    'depth': sunshade.depth,
                    'd_h': sunshade.d_h,
                    'd_e': sunshade.d_e,
                    'x1': sunshade.x1,
                    'x2': sunshade.x2,
                    'x3': sunshade.x3,
                    'y1': sunshade.y1,
                    'y2': sunshade.y2,
                    'y3': sunshade.y3,
                    'z_x_pls': sunshade.z_x_pls,
                    'z_x_mns': sunshade.z_x_mns,
                    'z_y_pls': sunshade.z_y_pls,
                    'z_y_mns': sunshade.z_y_mns
                }
            },
            'is_sunshade_input': False
        } for p in model_house_envelope_no_spec['windows']
    ]

    doors = [
        {
            'name': p['name'],
            'next_space': p['next_space'],
            'direction': p['direction'],
            'area': p['area'],
            'space_type': p['space_type'],
            'spec': {
                'u_value': get_u_and_eta.get_u_psi(u, 'door'),
                'is_sunshade_input': False
            }
        } for p in model_house_envelope_no_spec['doors']
    ]

    earthfloor_perimeters = [
        {
            'name': p['name'],
            'next_space': p['next_space'],
            'length': p['length'],
            'space_type': p['space_type'],
            'spec': {
                'psi_value': get_u_and_eta.get_u_psi(u, 'earthfloor_perimeter'),
            }
        } for p in model_house_envelope_no_spec['earthfloor_perimeters']
    ]

    earthfloor_centers = [
        {
            'name': p['name'],
            'area': p['area'],
            'space_type': p['space_type'],
            'spec': {
                'is_layers_input': False
            }
        } for p in model_house_envelope_no_spec['earthfloor_centers']
    ]

    model_house_envelope = {
        'general_parts': general_parts,
        'windows': windows,
        'doors': doors,
        'earthfloor_perimeters': earthfloor_perimeters,
        'earthfloor_centers': earthfloor_centers
    }

    return model_house_envelope


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
