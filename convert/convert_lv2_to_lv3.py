import copy


def get_separated_areas(a_evlp_i, a_f_mr, a_f_or, a_f_total):
    a_evlp_mr_i = a_f_mr / a_f_total * a_evlp_i
    a_evlp_or_i = a_f_or / a_f_total * a_evlp_i
    a_evlp_nr_i = (a_f_total - a_f_mr - a_f_or) / a_f_total * a_evlp_i

    return a_evlp_mr_i, a_evlp_or_i, a_evlp_nr_i


def get_separated_lengths(l_evlp_i, a_f_mr, a_f_or, a_f_total):
    l_evlp_mr_i = a_f_mr / a_f_total * l_evlp_i
    l_evlp_or_i = a_f_or / a_f_total * l_evlp_i
    l_evlp_nr_i = (a_f_total - a_f_mr - a_f_or) / a_f_total * l_evlp_i

    return l_evlp_mr_i, l_evlp_or_i, l_evlp_nr_i


def get_space_types():
    return 'main_occupant_room', 'other_occupant_room', 'non_occupant_room'


def get_evlps_lv3_area(envelope, common, make_evlp_lv3):

    result = []

    for evlp_lv2 in envelope:

        a_evlp_mr, a_evlp_or, a_evlp_nr = get_separated_areas(
            a_evlp_i=evlp_lv2['area'],
            a_f_mr=common['main_occupant_room_floor_area'],
            a_f_or=common['other_occupant_room_floor_area'],
            a_f_total=common['total_floor_area']
        )

        result.append(make_evlp_lv3(evlp_lv2, 'main_occupant_room', a_evlp_mr))
        result.append(make_evlp_lv3(evlp_lv2, 'other_occupant_room', a_evlp_or))
        result.append(make_evlp_lv3(evlp_lv2, 'non_occupant_room', a_evlp_nr))

    return result


def get_evlps_lv3_length(envelope, common, make_evlp_lv3):

    result = []

    for evlp_lv2 in envelope:

        l_evlp_mr, l_evlp_or, l_evlp_nr = get_separated_lengths(
            l_evlp_i=evlp_lv2['length'],
            a_f_mr=common['main_occupant_room_floor_area'],
            a_f_or=common['other_occupant_room_floor_area'],
            a_f_total=common['total_floor_area']
        )

        result.append(make_evlp_lv3(evlp_lv2, 'main_occupant_room', l_evlp_mr))
        result.append(make_evlp_lv3(evlp_lv2, 'other_occupant_room', l_evlp_or))
        result.append(make_evlp_lv3(evlp_lv2, 'non_occupant_room', l_evlp_nr))

    return result


def get_general_parts(general_parts, common):

    def make_general_part_lv3(envelope, space_type, a_evlp):

        return {
            'name': envelope['name'] + '_' + space_type,
            'general_part_type': envelope['general_part_type'],
            'next_space': envelope['next_space'],
            'direction': envelope['direction'],
            'area': a_evlp,
            'space_type': space_type,
            'spec': copy.deepcopy(envelope['spec'])
        }

    return get_evlps_lv3_area(general_parts, common, make_general_part_lv3)


def get_windows(windows, common):

    def make_window_lv3(envelope, space_type, a_evlp):

        return {
            'name': envelope['name'] + '_' + space_type,
            'next_space': envelope['next_space'],
            'direction': envelope['direction'],
            'area': a_evlp,
            'space_type': space_type,
            'spec': copy.deepcopy(envelope['spec'])
        }

    return get_evlps_lv3_area(windows, common, make_window_lv3)


def get_doors(doors, common):

    def make_door_lv3(envelope, space_type, a_evlp):

        return {
            'name': envelope['name'] + '_' + space_type,
            'next_space': envelope['next_space'],
            'direction': envelope['direction'],
            'area': a_evlp,
            'space_type': space_type,
            'spec': copy.deepcopy(envelope['spec'])
        }

    return get_evlps_lv3_area(doors, common, make_door_lv3)


def get_heatbridges(heatbridges, common):

    def make_heatbridge_lv3(heatbridge_lv2, space_type, l_evlp):

        return {
            'name'       : heatbridge_lv2['name'] + '_' + space_type,
            'next_space' : heatbridge_lv2['next_space'],
            'direction'  : heatbridge_lv2['direction'],
            'space_type' : space_type,
            'length'     : l_evlp,
            'spec'       : copy.deepcopy(heatbridge_lv2['spec']),
        }

    return get_evlps_lv3_length(heatbridges, common, make_heatbridge_lv3)


def get_earthfloor_perimeters(earthfloor_perimeters):

    return [
        {
            'name': earthfloor_perimeter['name'],
            'next_space': earthfloor_perimeter['next_space'],
            'direction': earthfloor_perimeter['direction'],
            'length': earthfloor_perimeter['length'],
            'space_type': 'underfloor',
            'spec': copy.deepcopy(earthfloor_perimeter['spec']),
        }
        for earthfloor_perimeter in earthfloor_perimeters]


def get_earthfloor_centers(earthfloor_centers):

    return [
        {
            'name': earghfloor_center['name'],
            'area': earghfloor_center['area'],
            'space_type': 'underfloor'
        }
        for earghfloor_center in earthfloor_centers]


def convert(common, envelope):

    result = {
        'input_method': 'detail_with_room_usage'
    }

    if 'general_parts' in envelope:
        result['general_parts'] = get_general_parts(envelope['general_parts'], common)

    if 'windows' in envelope:
        result['windows'] = get_windows(envelope['windows'], common)

    if 'doors' in envelope:
        result['doors'] = get_doors(envelope['doors'], common)

    if 'heatbridges' in envelope:
        result['heatbridges'] = get_heatbridges(envelope['heatbridges'], common)

    if 'earthfloor_perimeters' in envelope:
        result['earthfloor_perimeters'] = get_earthfloor_perimeters(envelope['earthfloor_perimeters'])

    if 'earthfloor_centers' in envelope:
        result['earthfloor_centers'] = get_earthfloor_centers(envelope['earthfloor_centers'])

    return result


if __name__ == '__main__':

    input_data_1 = {
        'common': {
            'region': 6,
            'main_occupant_room_floor_area': 30.0,
            'other_occupant_room_floor_area': 60.0,
            'total_floor_area': 120.0
        },
        'envelope': {
            'input_method': 'detail_without_room_usage',
            'general_parts': [
                {
                    'name'       : 'ceiling',
                    'general_part_type'  : 'ceiling',
                    'next_space' : 'outdoor',
                    'external_surface_type' : 'outdoor',
                    'direction'  : 'top',
                    'area'       : 67.8,
                    'spec'       : 'something'
                },
                {
                    'name'       : 'floor',
                    'general_part_type'  : 'floor',
                    'next_space' : 'outdoor',
                    'external_surface_type' : 'outdoor',
                    'direction'  : 'bottom',
                    'area'       : 67.8,
                    'spec'       : 'something'
                },
                {
                    'name'       : 'wall',
                    'general_part_type'  : 'wall',
                    'next_space' : 'outdoor',
                    'external_surface_type' : 'outdoor',
                    'direction'  : 'n',
                    'area'       : 67.8,
                    'spec'       : 'something'
                },
                {
                    'name'       : 'boundary_ceiling',
                    'general_part_type'  : 'boundary_ceiling',
                    'next_space' : 'air_conditioned',
                    'external_surface_type' : 'outdoor',
                    'direction'  : 'upward',
                    'area'       : 67.8,
                    'spec'       : 'something'
                },
            ],
            'windows': [
                {
                    'name'       : 'window_sw',
                    'next_space' : 'outdoor',
                    'direction'  : 'sw',
                    'area'       : 30.25,
                    'spec'       : 'something'
                },
                {
                    'name'       : 'window_nw',
                    'next_space' : 'outdoor',
                    'direction'  : 'nw',
                    'area'       : 3.17,
                    'spec'       : 'something'
                },
            ],
            'doors': [
                {
                    'name'       : 'door_nw',
                    'next_space' : 'outdoor',
                    'direction'  : 'nw',
                    'area'       : 2.52,
                    'spec'       : 'something'
                },
            ],
            'heatbridges': [
                {
                    'name'       : 'heatbridge_ne',
                    'length'     : 1.00,
                    'next_space' : ['outdoor', 'outdoor'],
                    'direction'  : ['n', 'e'],
                    'spec'       : 'something'
                },
            ],
            'earthfloor_perimeters': [
                {
                    'name'       : 'earthfloor_perimeter_nw',
                    'next_space' : 'outdoor',
                    'direction'  : 'nw',
                    'length'     : 2.43,
                    'spec'       : 'something'
                },
            ],
            'earthfloor_centers': [
                { 'area': 5.0, 'name': 'other' },
                { 'area': 5.0, 'name': 'entrance' }
            ],
        }
    }

    result1 = convert(common=input_data_1['common'], envelope=input_data_1['envelope'])

    print(result1)
