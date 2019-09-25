

def get_inner_floor_spec():
    return {
        'layers': [
            {
                'name': 'plywood',
                'thermal_resistance_input_method': 'conductivity',
                'thermal_conductivity': 0.16,
                'volumetric_specific_heat': 720.0,
                'thickness': 0.024,
            }
        ]
    }


def get_downward_envelope_total_area(envelope):
    parts = []

    if 'general_parts' in envelope: parts.extend(envelope['general_parts'])

    if 'windows' in envelope: parts.extend(envelope['windows'])

    if 'doors' in envelope: parts.extend(envelope['doors'])

    def f(space_type):
        return sum(part['area'] for part in parts
                   if part['space_type'] == space_type and (
                               part['direction'] == 'bottom' or part['direction'] == 'downward'))

    return f('main_occupant_room'), f('other_occupant_room'), f('non_occupant_room')


def get_earthfloor_total_area(envelope):
    parts = []

    if 'earthfloor_centers' in envelope: parts.extend(envelope['earthfloor_centers'])

    def f(space_type):
        return sum(part['area'] for part in parts
                   if part['space_type'] == space_type)

    return f('main_occupant_room'), f('other_occupant_room'), f('non_occupant_room'), f('underfloor')


def get_inner_floor_total_area(a_a, a_mr, a_or,
                               a_evlp_down_mr, a_evlp_down_or, a_evlp_down_nr,
                               a_ef_mr, a_ef_or, a_ef_nr):
    a_if_mr = max(0.0, a_mr - a_evlp_down_mr - a_ef_mr)
    a_if_or = max(0.0, a_or - a_evlp_down_or - a_ef_or)
    a_if_nr = max(0.0, a_a - a_mr - a_or - a_evlp_down_nr - a_ef_nr)

    return a_if_mr, a_if_or, a_if_nr


def get_inner_floor_over_underfloor_total_area(a_if_mr, a_if_or, a_if_nr, a_ef_uf):
    if (a_if_mr + a_if_or + a_if_nr) > 0.0:
        a_if_mr_uf = a_ef_uf * a_if_mr / (a_if_mr + a_if_or + a_if_nr)
        a_if_or_uf = a_ef_uf * a_if_or / (a_if_mr + a_if_or + a_if_nr)
        a_if_nr_uf = a_ef_uf * a_if_nr / (a_if_mr + a_if_or + a_if_nr)
    else:
        a_if_mr_uf = 0.0
        a_if_or_uf = 0.0
        a_if_nr_uf = 0.0

    return a_if_mr_uf, a_if_or_uf, a_if_nr_uf


def get_inner_floor_between_rooms(a_mr, a_or, a_a, a_if_mr, a_if_or, a_if_nr, a_if_mr_uf, a_if_or_uf, a_if_nr_uf):
    a_nr = a_a - a_mr - a_or

    if a_mr <= 0.0:
        raise ValueError('主たる居室の面積に0又は負の値が指定されました。主たる居室は必ず0より大きい値を指定する必要があります。')

    a_if_mr_or_nr = max(0.0, a_if_mr - a_if_mr_uf)
    a_if_or_mr_nr = max(0.0, a_if_or - a_if_or_uf)
    a_if_nr_mr_or = max(0.0, a_if_nr - a_if_nr_uf)

    if a_or <= 0.0 and a_nr <= 0.0:
        a_if_mr_or = 0.0
        a_if_mr_nr = 0.0
        a_if_or_mr = 0.0
        a_if_or_nr = 0.0
        a_if_nr_mr = 0.0
        a_if_nr_or = 0.0
    elif a_or <= 0.0:
        a_if_mr_or = 0.0
        a_if_mr_nr = a_if_mr_or_nr
        a_if_or_mr = 0.0
        a_if_or_nr = 0.0
        a_if_nr_mr = a_if_nr_mr_or
        a_if_nr_or = 0.0
    elif a_nr <= 0.0:
        a_if_mr_or = a_if_mr_or_nr
        a_if_mr_nr = 0.0
        a_if_or_mr = a_if_or_mr_nr
        a_if_or_nr = 0.0
        a_if_nr_mr = 0.0
        a_if_nr_or = 0.0
    else:
        a_if_mr_or = a_if_mr_or_nr / 2
        a_if_mr_nr = a_if_mr_or_nr / 2
        a_if_or_mr = a_if_or_mr_nr / 2
        a_if_or_nr = a_if_or_mr_nr / 2
        a_if_nr_mr = a_if_nr_mr_or / 2
        a_if_nr_or = a_if_nr_mr_or / 2

    return a_if_mr_or, a_if_mr_nr, a_if_or_mr, a_if_or_nr, a_if_nr_mr, a_if_nr_or


def get_inner_wall_spec():
    return {
        'layers' : [
            {
                'name'                            : 'gpb',
                'thermal_resistance_input_method' : 'conductivity',
                'thermal_conductivity'            : 0.22,
                'thickness'                       : 0.0125,
                'volumetric_specific_heat'        : 830.0,
            },
            {
                'name'                            : 'air_layer',
                'thermal_resistance_input_method' : 'resistance',
                'thermal_resistance'              : 0.09,
                'volumetric_specific_heat'        : 0.0,
            },
            {
                'name'                            : 'gpb',
                'thermal_resistance_input_method' : 'conductivity',
                'thermal_conductivity'            : 0.22,
                'thickness'                       : 0.0125,
                'volumetric_specific_heat'        : 830.0,
            },
        ]
    }


def get_horizontal_envelope_total_area(envelope):
    parts = []

    if 'general_parts' in envelope: parts.extend(envelope['general_parts'])

    if 'windows' in envelope: parts.extend(envelope['windows'])

    if 'doors' in envelope: parts.extend(envelope['doors'])

    def is_horizontal(part):
        d = part['direction']
        return d == 'n' or d == 'ne' or d == 'e' or d == 'se' or \
               d == 's' or d == 'sw' or d == 'w' or d == 'nw' or \
               d == 'horizontal'

    def f(space_type):
        return sum(part['area'] for part in parts \
                   if part['space_type'] == space_type and is_horizontal(part))

    return f('main_occupant_room'), f('other_occupant_room'), f('non_occupant_room')


def get_inner_wall_total_area(a_mr, a_or, a_a, a_evlp_hzt_mr, a_evlp_hzt_or, a_evlp_hzt_nr):
    r_iw_mr, r_iw_or, r_iw_nr = 1.2, 1.4, 1.4

    h_iw = 2.8

    a_iw_mr = max(0.0, 4 * r_iw_mr * h_iw * a_mr ** 0.5 - a_evlp_hzt_mr)
    a_iw_or = max(0.0, 4 * r_iw_or * h_iw * a_or ** 0.5 - a_evlp_hzt_or)
    a_iw_nr = max(0.0, 4 * r_iw_nr * h_iw * (a_a - a_mr - a_or) ** 0.5 - a_evlp_hzt_nr)

    return a_iw_mr, a_iw_or, a_iw_nr


def get_inner_wall_total_area_between_rooms(a_mr, a_or, a_a, a_iw_mr, a_iw_or, a_iw_nr):
    a_nr = a_a - a_mr - a_or

    if a_mr <= 0.0:
        raise ValueError('主たる居室の面積に0又は負の値が指定されました。主たる居室は必ず0より大きい値を指定する必要があります。')

    if a_or <= 0.0 and a_nr <= 0.0:
        a_iw_mr_or = 0.0
        a_iw_mr_nr = 0.0
        a_iw_or_nr = 0.0
    elif a_or <= 0.0:
        a_iw_mr_or = 0.0
        a_iw_mr_nr = (a_iw_mr + a_iw_nr) / 2
        a_iw_or_nr = 0.0
    elif a_nr <= 0.0:
        a_iw_mr_or = (a_iw_mr + a_iw_or) / 2
        a_iw_mr_nr = 0.0
        a_iw_or_nr = 0.0
    else:
        a_iw_mr_or = max(0.0, (a_iw_mr + a_iw_or - a_iw_nr) / 2)
        a_iw_mr_nr = max(0.0, (a_iw_mr + a_iw_nr - a_iw_or) / 2)
        a_iw_or_nr = max(0.0, (a_iw_or + a_iw_nr - a_iw_mr) / 2)

    return a_iw_mr_or, a_iw_mr_nr, a_iw_or_nr


def convert(common, envelope):

    a_mr = common['main_occupant_room_floor_area']
    a_or = common['other_occupant_room_floor_area']
    a_a = common['total_floor_area']

    a_evlp_down_mr, a_evlp_down_or, a_evlp_down_nr = get_downward_envelope_total_area(envelope)

    a_ef_mr, a_ef_or, a_ef_nr, a_ef_uf = get_earthfloor_total_area(envelope)

    a_if_mr, a_if_or, a_if_nr = get_inner_floor_total_area(a_a, a_mr, a_or,
                                                           a_evlp_down_mr, a_evlp_down_or, a_evlp_down_nr,
                                                           a_ef_mr, a_ef_or, a_ef_nr)

    a_if_mr_uf, a_if_or_uf, a_if_nr_uf = get_inner_floor_over_underfloor_total_area(a_if_mr, a_if_or, a_if_nr, a_ef_uf)

    a_if_mr_or, a_if_mr_nr, a_if_or_mr, a_if_or_nr, a_if_nr_mr, a_if_nr_or \
        = get_inner_floor_between_rooms(a_mr, a_or, a_a, a_if_mr, a_if_or, a_if_nr, a_if_mr_uf, a_if_or_uf, a_if_nr_uf)

    ifs = []

    def append_inner_floor(ifs, name, area, upper_space_type, lower_space_type):
        if area > 0.0:
            ifs.append(
                {
                    'name': name,
                    'area': area,
                    'upper_space_type': upper_space_type,
                    'lower_space_type': lower_space_type,
                    'spec': get_inner_floor_spec()
                }
            )

    append_inner_floor(ifs, 'inner_floor_main_to_underfloor', a_if_mr_uf, 'main_occupant_room', 'underfloor')
    append_inner_floor(ifs, 'inner_floor_other_to_underfloor', a_if_or_uf, 'other_occupant_room', 'underfloor')
    append_inner_floor(ifs, 'inner_floor_non_to_underfloor', a_if_nr_uf, 'non_occupant_room', 'underfloor')
    append_inner_floor(ifs, 'inner_floor_main_to_other', a_if_mr_or, 'main_occupant_room', 'other_occupant_room')
    append_inner_floor(ifs, 'inner_floor_main_to_non', a_if_mr_nr, 'main_occupant_room', 'non_occupant_room')
    append_inner_floor(ifs, 'inner_floor_other_to_main', a_if_or_mr, 'other_occupant_room', 'main_occupant_room')
    append_inner_floor(ifs, 'inner_floor_other_to_non', a_if_or_nr, 'other_occupant_room', 'non_occupant_room')
    append_inner_floor(ifs, 'inner_floor_non_to_main', a_if_nr_mr, 'non_occupant_room', 'main_occupant_room')
    append_inner_floor(ifs, 'inner_floor_non_to_other', a_if_nr_or, 'non_occupant_room', 'other_occupant_room')

    return ifs


if __name__ == '__main__':

    input_data_1 = {
        'common': {
            'region': 6,
            'main_occupant_room_floor_area': 30.0,
            'other_occupant_room_floor_area': 60.0,
            'total_floor_area': 120.0
        },
        'envelope': {
            'general_parts': [
                {
                    'name': 'floor',
                    'evlp_type': 'floor',
                    'next_space': 'open_underfloor',
                    'direction': 'bottom',
                    'area': 60.0,
                    'space_type': 'main',
                    'spec': 'something'
                },
            ],
            'earthfloor_centers': [
                {'name': 'other', 'area': 5.0, 'space_type': 'underfloor'},
                {'name': 'entrance', 'area': 5.0, 'space_type': 'underfloor'}
            ]
        }
    }

    result1 = convert(input_data_1['common'], input_data_1['envelope'])

    print(result1)
