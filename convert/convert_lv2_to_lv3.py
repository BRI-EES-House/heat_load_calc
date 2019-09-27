import copy
from typing import Dict, Callable, List, Tuple


def get_separated_areas(
        a_evlp_i: float, a_f_mr: float, a_f_or: float, a_f_total: float) -> Tuple[float, float, float]:

    a_evlp_mr_i = a_f_mr / a_f_total * a_evlp_i
    a_evlp_or_i = a_f_or / a_f_total * a_evlp_i
    a_evlp_nr_i = (a_f_total - a_f_mr - a_f_or) / a_f_total * a_evlp_i

    return a_evlp_mr_i, a_evlp_or_i, a_evlp_nr_i


def get_separated_lengths(
        l_evlp_i: float, a_f_mr: float, a_f_or: float, a_f_total: float) -> Tuple[float, float, float]:

    l_evlp_mr_i = a_f_mr / a_f_total * l_evlp_i
    l_evlp_or_i = a_f_or / a_f_total * l_evlp_i
    l_evlp_nr_i = (a_f_total - a_f_mr - a_f_or) / a_f_total * l_evlp_i

    return l_evlp_mr_i, l_evlp_or_i, l_evlp_nr_i


def get_space_types():
    return 'main_occupant_room', 'other_occupant_room', 'non_occupant_room'


def get_evlps_lv3_area(
        common: Dict, envelope: List[Dict], make_evlp_lv3: Callable[[Dict, str, float], Dict]) -> List[Dict]:

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


def get_evlps_lv3_length(
        common: Dict, envelope: List[Dict], make_evlp_lv3: Callable[[Dict, str, float], Dict]) -> List[Dict]:

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


def get_general_parts(common: Dict, general_parts: List[Dict]) -> List[Dict]:

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

    return get_evlps_lv3_area(common, general_parts, make_general_part_lv3)


def get_windows(common: Dict, windows: List[Dict]) -> List[Dict]:

    def make_window_lv3(envelope, space_type, a_evlp):

        return {
            'name': envelope['name'] + '_' + space_type,
            'next_space': envelope['next_space'],
            'direction': envelope['direction'],
            'area': a_evlp,
            'space_type': space_type,
            'spec': copy.deepcopy(envelope['spec'])
        }

    return get_evlps_lv3_area(common, windows, make_window_lv3)


def get_doors(common: Dict, doors: List[Dict]) -> List[Dict]:

    def make_door_lv3(envelope, space_type, a_evlp):

        return {
            'name': envelope['name'] + '_' + space_type,
            'next_space': envelope['next_space'],
            'direction': envelope['direction'],
            'area': a_evlp,
            'space_type': space_type,
            'spec': copy.deepcopy(envelope['spec'])
        }

    return get_evlps_lv3_area(common, doors, make_door_lv3)


def get_heatbridges(common: Dict, heatbridges: List[Dict]) -> List[Dict]:

    def make_heatbridge_lv3(heatbridge_lv2, space_type, l_evlp):

        return {
            'name': heatbridge_lv2['name'] + '_' + space_type,
            'next_space': heatbridge_lv2['next_space'],
            'direction': heatbridge_lv2['direction'],
            'space_type': space_type,
            'length': l_evlp,
            'spec': copy.deepcopy(heatbridge_lv2['spec']),
        }

    return get_evlps_lv3_length(common, heatbridges, make_heatbridge_lv3)


def get_earthfloor_perimeters(earthfloor_perimeters: List[Dict]) -> List[Dict]:

    return [
        {
            'name': p['name'],
            'next_space': p['next_space'],
            'direction': p['direction'],
            'length': p['length'],
            'space_type': 'underfloor',
            'spec': copy.deepcopy(p['spec']),
        }
        for p in earthfloor_perimeters]


def get_earthfloor_centers(earthfloor_centers: List[Dict]) -> List[Dict]:

    return [
        {
            'name': p['name'],
            'area': p['area'],
            'space_type': 'underfloor'
        }
        for p in earthfloor_centers]


def convert(common, envelope):

    result = {
        'input_method': 'detail_with_room_usage'
    }

    if 'general_parts' in envelope:
        result['general_parts'] = get_general_parts(common, envelope['general_parts'])

    if 'windows' in envelope:
        result['windows'] = get_windows(common, envelope['windows'])

    if 'doors' in envelope:
        result['doors'] = get_doors(common, envelope['doors'])

    if 'heatbridges' in envelope:
        result['heatbridges'] = get_heatbridges(common, envelope['heatbridges'])

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
