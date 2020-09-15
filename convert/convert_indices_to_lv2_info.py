from typing import Dict

import factor_f
import model_house
import convert_model_house_to_house_dict
import get_u_psi_eta_from_u_a_and_eta_a as get_u_and_eta
import factor_nu

from heat_load_calc.external import factor_nu
from heat_load_calc.external import factor_h


def convert(common: Dict, envelope: Dict):

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

    model_house_envelope = add_spec(model_house_envelope_no_spec, u_psi, eta_d, eta_d_h, eta_d_c, sunshade)

    return model_house_envelope, sunshade


def check_u_a_and_eta_a(region, model_house_envelope, sunshade):

    general_parts = model_house_envelope['general_parts']

    windows = model_house_envelope['windows']

    doors = model_house_envelope['doors']

    earthfloor_perimeters = model_house_envelope['earthfloor_perimeters']

    earthfloor_centers = model_house_envelope['earthfloor_centers']

    a_evp_total = get_total_area(general_parts, windows, doors, earthfloor_centers)

    q_general = sum(p['area'] * p['spec']['u_value_other'] * factor_h.get_h(region, p['next_space'])
                    for p in general_parts)

    q_window = sum(p['area'] * p['spec']['windows'][0]['u_value'] * factor_h.get_h(region, p['next_space'])
                   for p in windows)

    q_door = sum(p['area'] * p['spec']['u_value'] * factor_h.get_h(region, p['next_space']) for p in doors)

    q_earthfloor_perimeter = sum(p['length'] * p['spec']['psi_value'] * factor_h.get_h(region, p['next_space'])
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
            p['spec']['windows'][0]['eta_d_h_value'] * p['area']
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
        p['spec']['windows'][0]['eta_d_c_value'] * p['area']
        * factor_f.get_f(season='cooling', region=region, direction=p['direction'], sunshade=sunshade)
        * factor_nu.get_nu(season='cooling', region=region,direction=p['direction'])
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


def add_spec(
        model_house_envelope_no_spec: Dict, u: Dict, eta_d: float, eta_d_h: float, eta_d_c: float, sunshade: Dict
) -> Dict:
    """
    Args:
        model_house_envelope_no_spec: U値やη値等の仕様が無い住宅形状等の辞書
        u: U値を格納した辞書
        eta_d: ηd値
        eta_d_h: ηdh値
        eta_d_c: ηdc値
        sunshade: ひさし形状の辞書
    Returns:
        U値やη値等の仕様を追加した住宅形状等の辞書
    """

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
                        'eta_d_h_value': eta_d_h,
                        'eta_d_c_value': eta_d_c,
                        'glass_type': 'single'
                    }
                ],
                'attachment_type': 'none',
                'is_windbreak_room_attached': 'none',
                'is_sunshade_input': True,
                'sunshade': {
                    'existence': sunshade.existence,
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


def print_target(indices: Dict):
    """
        ターゲットとなる指標をプリントする
    Args:
        indices: UA値・ηAH値・ηAC値の辞書
    """

    print('目標UA値：' + str(indices['u_a']))
    print('目標ηAH値：' + str(indices['eta_a_h']))
    print('目標ηAC値：' + str(indices['eta_a_c']))


def print_result(checked_u_a, checked_eta_a_h, checked_eta_a_c):

    print('計算UA値：' + str(checked_u_a))
    print('計算ηAH値：' + str(checked_eta_a_h))
    print('計算ηAC値：' + str(checked_eta_a_c))


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

    print_target(indices=input_data_1['envelope']['indices'])
    result1, sunshade1 = convert(common=input_data_1['common'], envelope=input_data_1['envelope'])

    checked_u_a1, checked_eta_a_h1, checked_eta_a_c1 = check_u_a_and_eta_a(
        region=input_data_1['common']['region'], model_house_envelope=result1, sunshade=sunshade1)

    print_result(checked_u_a=checked_u_a1, checked_eta_a_h=checked_eta_a_h1, checked_eta_a_c=checked_eta_a_c1)

    print(result1)
