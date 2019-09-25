import factor_f
import model_house
import convert_model_house_to_house_dict
import get_u_psi_eta_from_u_a_and_eta_a as get_u_and_eta
from factor_h import get_factor_h
import factor_nu


def convert(common, envelope):

    region = common['region']
    house_type = common['house_type']
    a_f_total = common['total_floor_area']

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

    sunshade = factor_f.Sunshade(
        existence=True, input_method='simple',
        depth=0.3, d_h=1.0, d_e=0.0,
        x1=None, x2=None, x3=None,
        y1=None, y2=None, y3=None,
        z_x_pls=None, z_x_mns=None, z_y_pls=None, z_y_mns=None
    )

    u_psi, eta_d, eta_d_h, eta_d_c = get_u_and_eta.calc_parts_spec(
        region=region,
        house_no_spec=model_house_envelope_no_spec,
        u_a_target=u_a,
        eta_a_h_target=eta_a_h,
        eta_a_c_target=eta_a_c,
        sunshade=sunshade
    )

    print('U値: ' + str(u_psi))
    print('ηd値: ' + str(eta_d))
    print('UA設定値: ' + str(u_a) + ', ηAH設定値: ' + str(eta_a_h) + ', ηAC設定値: ' + str(eta_a_c))

    model_house_envelope = add_spec(model_house_envelope_no_spec, u_psi, eta_d, sunshade)

    checked_u_a, checked_eta_a_h, checked_eta_a_c = check_u_a_and_eta_a(region, model_house_envelope, eta_d_h, eta_d_c, sunshade)

    print('UA計算値: ' + str(checked_u_a) + ', ηAH計算値: ' + str(checked_eta_a_h) + ', ηAC計算値: ' + str(checked_eta_a_c))

    return model_house_envelope


def check_u_a_and_eta_a(region, model_house_envelope, eta_d_h, eta_d_c, sunshade):

    general_parts = model_house_envelope['general_parts']

    windows = model_house_envelope['windows']

    doors = model_house_envelope['doors']

    earthfloor_perimeters = model_house_envelope['earthfloor_perimeters']

    earthfloor_centers = model_house_envelope['earthfloor_centers']

    a_evp_total = get_total_area(general_parts, windows, doors, earthfloor_centers)

    q_general = sum(p['area'] * p['spec']['u_value_other'] * get_factor_h(region, p['next_space'])
                    for p in general_parts)

    q_window = sum(p['area'] * p['spec']['windows'][0]['u_value'] * get_factor_h(region, p['next_space'])
                   for p in windows)

    q_door = sum(p['area'] * p['spec']['u_value'] * get_factor_h(region, p['next_space']) for p in doors)

    q_earthfloor_perimeter = sum(p['length'] * p['spec']['psi_value'] * get_factor_h(region, p['next_space'])
                                 for p in earthfloor_perimeters)

    u_a = (q_general + q_window + q_door + q_earthfloor_perimeter) / a_evp_total

    if region != 8:

        m_h_general = sum(
            p['area'] * 0.034 * p['spec']['u_value_other']
            * factor_nu.get_nu(region=region, season='heating', direction=p['direction'])
            for p in general_parts if p['next_space'] == 'outdoor')

        m_h_door = sum(
            p['area'] * 0.034 * p['spec']['u_value']
            * factor_nu.get_nu(region=region, season='heating', direction=p['direction'])
            for p in doors if p['next_space'] == 'outdoor')

        m_h_window = sum(
            p['spec']['windows'][0]['eta_d_value'] * p['area']
            * factor_f.get_f(season='heating', region=region, direction=p['direction'], sunshade=sunshade)
            * factor_nu.get_nu(season='heating', region=region, direction=p['direction'])
            for p in windows)

        m_h_window = sum(
            eta_d_h * p['area']
            * factor_f.get_f(season='heating', region=region, direction=p['direction'], sunshade=sunshade)
            * factor_nu.get_nu(season='heating', region=region, direction=p['direction'])
            for p in windows)

        eta_a_h = (m_h_general + m_h_door + m_h_window) / a_evp_total * 100

    else:

        eta_a_h = None

    m_c_general = sum(
        p['area'] * 0.034 * p['spec']['u_value_other']
        * factor_nu.get_nu(region=region, season='cooling', direction=p['direction'])
        for p in general_parts if p['next_space'] == 'outdoor')

    m_c_door = sum(
        p['area'] * 0.034 * p['spec']['u_value']
        * factor_nu.get_nu(region=region, season='cooling', direction=p['direction'])
        for p in doors if p['next_space'] == 'outdoor')

    m_c_window = sum(
        p['spec']['windows'][0]['eta_d_value'] * p['area']
        * factor_f.get_f(season='cooling', region=region, direction=p['direction'], sunshade=sunshade)
        * factor_nu.get_nu(season='cooling', region=region,direction=p['direction'])
        for p in windows)

    m_c_window = sum(
        eta_d_c * p['area']
        * factor_f.get_f(season='cooling', region=region, direction=p['direction'], sunshade=sunshade)
        * factor_nu.get_nu(season='cooling', region=region, direction=p['direction'])
        for p in windows)

    eta_a_c = (m_c_general + m_c_door + m_c_window) / a_evp_total * 100

    return u_a, eta_a_h, eta_a_c


def get_total_area(general_parts, windows, doors, earthfloor_centers):

    d_area = []

    if general_parts is not None:
        d_area.extend(general_parts)

    if windows is not None:
        d_area.extend(windows)

    if doors is not None:
        d_area.extend(doors)

    if earthfloor_centers is not None:
        d_area.extend(earthfloor_centers)

    return sum(d['area'] for d in d_area)


def add_spec(model_house_envelope_no_spec, u, eta_d, sunshade):

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

    return {
        'input_method': model_house_envelope_no_spec['input_method'],
        'general_parts': general_parts,
        'windows': windows,
        'doors': doors,
        'earthfloor_perimeters': earthfloor_perimeters,
        'earthfloor_centers': earthfloor_centers
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

    result = convert(common=input_data_1['common'], envelope=input_data_1['envelope'])

    print(result)
